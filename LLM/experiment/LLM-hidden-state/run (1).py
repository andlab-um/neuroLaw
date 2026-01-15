
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态生成 Qwen3-8B：
- prompt 前向：仅保存最后一个 token 的每层 hidden
- 生成阶段：逐 token 生成，逐层保存 hidden
- 使用“括号配对”定位第一个完整 JSON
- JSON 一闭合立刻停止生成
- 每条样本落盘前强制自检，失败直接报错
"""

import json
import numpy as np
import torch
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple, List

from modelscope import snapshot_download
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoConfig,
)

from batch_csv_to_prompts import BatchCSVProcessor


# ================== 基础配置 ==================

MODEL_ID = "Qwen/Qwen3-8B"
CACHE_DIR = "./modelscope"
MAX_GENERATE_STEPS = 384   # 防死循环硬上限


# ================== JSON 精确定位 ==================

def find_first_complete_json(text: str):
    """
    定位文本中第一个完整 JSON 对象
    返回: (success, obj, json_str, end_pos)
    """
    start = text.find("{")
    if start == -1:
        return False, None, None, None

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                candidate = text[start : i + 1]
                try:
                    obj = json.loads(candidate)
                    return True, obj, candidate, i + 1
                except Exception:
                    return False, None, None, None

    return False, None, None, None


def extract_score_from_stream(
    text: str,
    prompt_type: str,
) -> Tuple[bool, Any, int]:
    """
    从生成流中提取评分
    返回: (success, score, json_end_pos)
    """
    ok, obj, _, end_pos = find_first_complete_json(text)
    if not ok:
        return False, None, None

    if prompt_type == "emotion" and "emotional_score" in obj:
        return True, obj["emotional_score"], end_pos

    if prompt_type == "punishment" and "punishment_score" in obj:
        return True, obj["punishment_score"], end_pos

    return False, None, None


# ================== 模型准备 ==================

def prepare_model() -> Dict[str, Any]:
    print(">>> 下载 / 同步模型")
    model_dir = snapshot_download(MODEL_ID, cache_dir=CACHE_DIR, revision="master")

    if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory < 20 * 1024**3:
        quant = BitsAndBytesConfig(load_in_8bit=True)
    else:
        quant = None

    tokenizer = AutoTokenizer.from_pretrained(
        model_dir, trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        quantization_config=quant,
        trust_remote_code=True,
        output_hidden_states=True,
    )

    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True)
    print("num_hidden_layers =", config.num_hidden_layers)

    return {
        "tokenizer": tokenizer,
        "model": model,
        "config": config,
    }


# ================== Prompt 构建 ==================

def build_prompts(csv_paths, column, delay_column):
    processor = BatchCSVProcessor(
        csv_paths=csv_paths,
        text_column=column,
        delay_column=delay_column,
        use_full_prompt=True,
        roles=["SPP", "TPP"],
    )
    return processor.process()


# ================== 核心采集逻辑 ==================

def collect_hidden_states_dynamic(
    prompt_text: str,
    prompt_type: str,
    tokenizer,
    model,
    config,
) -> Dict[str, Any]:

    device = next(model.parameters()).device

    enc = tokenizer(
        prompt_text,
        return_tensors="pt",
        add_special_tokens=True,
    ).to(device)

    # ---------- prompt 前向 ----------
    with torch.no_grad():
        out = model(**enc, output_hidden_states=True)

    past = out.past_key_values
    hidden_states = out.hidden_states[1:]
    num_layers = len(hidden_states)

    # prompt 最后一个 token 的每层 hidden
    input_last_hidden = np.stack(
        [h[0, -1].half().cpu().numpy() for h in hidden_states],
        axis=0,
    )

    # ---------- 生成阶段 ----------
    output_hidden_collector = [[] for _ in range(num_layers)]
    generated_ids: List[int] = []

    next_token_id = torch.argmax(out.logits[:, -1, :], dim=-1)

    success = False
    score_value = None

    for step in range(MAX_GENERATE_STEPS):
        with torch.no_grad():
            out_step = model(
                input_ids=next_token_id.unsqueeze(0),
                past_key_values=past,
                output_hidden_states=True,
            )

        next_token_id = torch.argmax(out_step.logits[:, -1, :], dim=-1)
        tid = int(next_token_id[0].item())
        generated_ids.append(tid)

        for li, layer_h in enumerate(out_step.hidden_states[1:]):
            output_hidden_collector[li].append(
                layer_h[0, 0].half().cpu().numpy()
            )

        past = out_step.past_key_values

        text = tokenizer.decode(
            generated_ids, skip_special_tokens=True
        )

        ok, score, _ = extract_score_from_stream(
            text, prompt_type
        )

        if ok:
            success = True
            score_value = score
            break

    if not success:
        raise RuntimeError(
            f"生成失败：{prompt_type} 在 {MAX_GENERATE_STEPS} 步内未解析出评分"
        )

    output_hidden = np.stack(
        [np.stack(v, axis=0) for v in output_hidden_collector],
        axis=0,
    )

    generated_texts = [
        tokenizer.decode([tid], skip_special_tokens=False)
        for tid in generated_ids
    ]

    return {
        "input_last_hidden": input_last_hidden,
        "output_hidden": output_hidden,
        "generated_ids": generated_ids,
        "generated_texts": generated_texts,
        "score": score_value,
    }


# ================== 保存 ==================

def save_npz_atomic(
    output_dir: Path,
    prompt_id: int,
    prompt_text: str,
    prompt_type: str,
    collected: Dict[str, Any],
):
    out_path = output_dir / f"prompt_{prompt_id:03d}_{prompt_type}.npz"
    tmp_path = str(out_path)

    meta = {
        "prompt_id": prompt_id,
        "prompt_type": prompt_type,
        "prompt": prompt_text,
        "generated_ids": collected["generated_ids"],
        "generated_texts": collected["generated_texts"],
        "score": collected["score"],
    }

    np.savez_compressed(
        tmp_path,
        input_last_hidden=collected["input_last_hidden"],
        output_hidden=collected["output_hidden"],
        meta=np.array(json.dumps(meta, ensure_ascii=False)),
    )

    shutil.move(tmp_path, out_path)
    print(f"✓ 保存成功: {out_path}")


# ================== main ==================

def main():
    class Args:
        csv = "final_crime_data.csv"
        column = "案件内容"
        delay_column = "延迟时间"
        output_dir = "../autodl-tmp/results_dynamic_clean"

    args = Args()

    prompts = build_prompts(
        [args.csv],
        args.column,
        args.delay_column,
    )

    print(f"共 {len(prompts)} 条 prompt")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    resources = prepare_model()
    tokenizer = resources["tokenizer"]
    model = resources["model"]
    config = resources["config"]

    for idx, prompt_text in enumerate(prompts, 1):
        prompt_type = (
            "punishment"
            if "\"punishment_score\"" in prompt_text
            else "emotion"
        )

        print(f"\n[{idx}/{len(prompts)}] 处理 {prompt_type}")

        collected = collect_hidden_states_dynamic(
            prompt_text,
            prompt_type,
            tokenizer,
            model,
            config,
        )

        save_npz_atomic(
            output_dir,
            idx,
            prompt_text,
            prompt_type,
            collected,
        )

    print("\n✅ 全部样本生成完成（JSON 精确定位，已干净截断）")


if __name__ == "__main__":
    main()
