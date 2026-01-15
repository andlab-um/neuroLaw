#!/usr/bin/env python3
"""
实验运行器 - 干净的代码版本
用于大规模并行控制变量实验
支持通过环境变量和命令行参数配置实验参数
"""

import os
import json
import csv
import time
import re
import argparse
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
from openai import OpenAI


# ==================== LLM Client ====================
class LLMClient:
    """LLM API客户端封装"""
    
    def __init__(self, model_name: str, api_url: str = None, api_key: str = None):
        if not model_name:
            raise ValueError("model_name 必须提供")
        self.model_name = model_name
        self.api_url = api_url or os.getenv("LLM_API_URL", "your_default_api_url_here")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "your_default_api_key_here")
        
        if not self.api_key:
            raise ValueError("API密钥未提供，请设置环境变量 LLM_API_KEY 或通过参数传入")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )

    def generate_response(self, prompt: str) -> Tuple[str, float]:
        """生成响应并返回内容和响应时间"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            result = response.choices[0].message.content
            response_time = time.time() - start_time
            return result, response_time
                
        except Exception as e:
            error_msg = f"API调用出错: {str(e)}"
            return error_msg, time.time() - start_time


# ==================== Data Loading ====================
class CSVCases:
    """CSV案件数据加载器"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data = self._load()

    def _load(self) -> pd.DataFrame:
        """加载CSV数据"""
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            print(f"✓ 载入CSV: {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"⚠️ CSV载入失败: {e}")
            return pd.DataFrame(columns=["序号", "案件内容", "延迟时间", "Category"])

    def get_delay_values(self) -> List[str]:
        """获取所有延迟时间值"""
        if self.data.empty:
            return ["当日"]
        delays = list(self.data["延迟时间"].unique())
        has_immediate = any(("当" in str(d) and ("日" in str(d) or "曰" in str(d))) for d in delays)
        if not has_immediate:
            delays = ["当日"] + [d for d in delays if d != "当日"]
        return delays


# ==================== Prompt Building ====================
EMOTIONAL_INSTRUCTION = "根据个人的情感体验，"

# 推理条件指令
REASONING_INSTRUCTIONS = {
    "NAN-reasoning": "",  # 无特殊推理指令
    "long-term-reasoning": "你有较为充足的思考和反应时间。",
    "short-term-reasoning": "你需要立刻做出判断，时间紧迫。"
}


def build_prompt(role: str, 
                case_desc: str, 
                include_emotional: bool,
                reasoning_type: str = "NAN-reasoning",
                time_condition: str = None,
                age: str = None) -> str:
    """
    构建实验提示词
    
    Args:
        role: 角色 (SPP/TPP)
        case_desc: 案件描述
        include_emotional: 是否包含情感指令
        reasoning_type: 推理类型 (NAN-reasoning/long-term-reasoning/short-term-reasoning)
        time_condition: 时间条件 (即时/延迟)
        age: 年龄条件 (age:NAN/age:20/age:30/age:40/age:50/age:60)
    """
    # 角色设置
    role_prefix = "你是一名受害者" if role == "SPP" else "你是一名法官"
    
    # 情感指令
    emotional = EMOTIONAL_INSTRUCTION if include_emotional else ""
    
    # 推理指令
    reasoning_instruction = REASONING_INSTRUCTIONS.get(reasoning_type, "")
    
    # 时间条件说明
    time_instruction = ""
    if time_condition:
        if time_condition == "即时":
            time_instruction = "注意：这是一个即时发生的案件，你需要立即做出判断。"
        elif time_condition == "延迟":
            time_instruction = "注意：这是一个延迟发生的案件，案件已经过去一段时间。"
    
    # 年龄条件说明
    age_instruction = ""
    if age and age != "age:NAN":
        age_num = age.replace("age:", "")
        age_instruction = f"你当前的年龄是{age_num}岁，请从这个年龄段的视角进行判断。"
    
    # 构建完整的提示词
    parts = [role_prefix + "。"]
    
    if age_instruction:
        parts.append(age_instruction)
    
    parts.append("\n案件描述：" + case_desc)
    
    if time_instruction:
        parts.append("\n" + time_instruction)
    
    parts.append("\n")
    
    if reasoning_instruction:
        parts.append(reasoning_instruction + "\n")
    
    if emotional:
        parts.append(emotional)
    
    parts.append("请你判断犯罪者应当受到多严厉的惩罚。\n")
    parts.append("评分标准：\n")
    parts.append("0 分 —— 不给予任何刑罚\n")
    parts.append("9 分 —— 死刑\n")
    parts.append("分数越高，对应的惩罚越严厉\n\n")
    parts.append("请严格按照以下JSON格式输出你的回答：\n")
    parts.append("{\n")
    parts.append("    \"punishment_score\": <0-9的整数>,\n")
    parts.append("    \"reasoning\": \"<评分理由>\",\n")
    parts.append("    \"emotional_arousal\": <0-9的整数>,\n")
    parts.append("    \"emotional_description\": \"<情绪状态描述>\",\n")
    parts.append("    \"case_analysis\": \"<对案件的分析>\",\n")
    parts.append("    \"punishment_justification\": \"<惩罚合理性的说明>\"\n")
    parts.append("}\n")
    
    return "".join(parts)


# ==================== Response Parser ====================
def parse_response(resp: str) -> Tuple[int, str, int, str, str, str]:
    """解析LLM响应为结构化数据"""
    try:
        # 尝试从代码块中提取JSON
        m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", resp)
        if m:
            json_str = m.group(1)
        else:
            # 直接提取JSON对象
            json_match = re.search(r"\{[\s\S]*\}", resp)
            if not json_match:
                raise ValueError("未找到JSON格式")
            json_str = json_match.group(0)
        
        data = json.loads(json_str)
        return (
            int(data.get("punishment_score", 0)),
            str(data.get("reasoning", "")),
            int(data.get("emotional_arousal", 0)),
            str(data.get("emotional_description", "")),
            str(data.get("case_analysis", "")),
            str(data.get("punishment_justification", "")),
        )
    except Exception as e:
        print(f"⚠️ JSON解析失败: {e}")
        print(f"响应内容: {resp[:200]}...")
        return 0, resp.strip()[:200], 0, "", "", ""


# ==================== Result Structure ====================
@dataclass
class Result:
    """实验结果数据结构"""
    experiment_id: str
    case_id: str
    role: str
    time_condition: str
    delay_time: str
    model: str
    include_emotional: bool
    score: int
    reasoning: str
    emotional_arousal: int
    emotional_description: str
    case_analysis: str
    punishment_justification: str
    response_time: float
    timestamp: str


# ==================== Experiment Runner ====================
class SimpleExperiment:
    """简单实验运行器"""
    
    def __init__(self,
                 csv_path: str,
                 model_name: str,
                 samples_per_condition: int = 2,
                 include_emotional: bool = True,
                 experiment_id_prefix: str = "simp",
                 reasoning_type: str = "NAN-reasoning",
                 age: str = None,
                 api_url: str = None,
                 api_key: str = None):
        self.client = LLMClient(model_name, api_url, api_key)
        self.csv = CSVCases(csv_path)
        self.samples_per_condition = samples_per_condition
        self.include_emotional = include_emotional
        self.reasoning_type = reasoning_type
        self.age = age
        self.experiment_id = f"{experiment_id_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results: List[Result] = []

    def run(self) -> List[Result]:
        """运行实验"""
        roles = ["SPP", "TPP"]
        
        # 获取去重后的案件
        df_unique = self.csv.data.drop_duplicates(subset=["序号"])
        if df_unique.empty:
            print("⚠️ CSV 中没有有效案件")
            return []

        # 建立案件到时间条件的映射
        case_2_conditions: Dict[str, List[str]] = {}
        for _, row in self.csv.data.iterrows():
            cid = f"CSV_{row['序号']}"
            delay_str = str(row["延迟时间"])
            cond = ("即时" if ("当" in delay_str and ("日" in delay_str or "曰" in delay_str))
                    else "延迟")
            case_2_conditions.setdefault(cid, []).append(cond)

        # 计算总预期次数
        total_expected = 0
        for cid, conds in case_2_conditions.items():
            total_expected += len(roles) * len(conds) * self.samples_per_condition
        
        print(f"实验配置:")
        print(f"  模型: {self.client.model_name}")
        print(f"  推理类型: {self.reasoning_type}")
        print(f"  情感指令: {'包含' if self.include_emotional else '不包含'}")
        if self.age:
            print(f"  年龄条件: {self.age}")
        print(f"  每条件样本数: {self.samples_per_condition}")
        print(f"  总预期次数: {total_expected}")
        print(f"  实验ID: {self.experiment_id}")
        print("-" * 60)
        
        completed = 0

        # 开始采样
        for _, row in df_unique.iterrows():
            cid = f"CSV_{row['序号']}"
            case_dict = {
                "id": cid,
                "description": row["案件内容"],
                "delay_time": row["延迟时间"],
                "category": row.get("Category", "未知")
            }

            for cond in case_2_conditions[cid]:
                for role in roles:
                    for _ in range(self.samples_per_condition):
                        self._eval_case(role, cond, row["延迟时间"], case_dict)
                        completed += 1
                        if completed % 10 == 0:
                            print(f"进度: {completed}/{total_expected} "
                                  f"({completed/total_expected*100:.1f}%)")

        print(f"✓ 实验完成，共 {len(self.results)} 条结果")
        return self.results

    def _eval_case(self, role: str, time_cond: str, delay_time: str, case: Dict[str, Any]):
        """评估单个案件"""
        prompt = build_prompt(
            role=role,
            case_desc=case.get("description", ""),
            include_emotional=self.include_emotional,
            reasoning_type=self.reasoning_type,
            time_condition=time_cond,
            age=self.age
        )
        print(prompt)
        resp, rt = self.client.generate_response(prompt)
        
        # 检查API是否返回错误
        if "API调用失败" in resp or "API调用出错" in resp:
            print(f"⚠️ API调用失败: {resp[:100]}...")
            score, reasoning, arousal, emo_desc, analysis, just = 0, resp[:200], 0, "", "", ""
        else:
            score, reasoning, arousal, emo_desc, analysis, just = parse_response(resp)
        
        self.results.append(Result(
            experiment_id=self.experiment_id,
            case_id=case.get("id", ""),
            role=role,
            time_condition=time_cond,
            delay_time=str(delay_time),
            model=self.client.model_name,
            include_emotional=self.include_emotional,
            score=score,
            reasoning=reasoning,
            emotional_arousal=arousal,
            emotional_description=emo_desc,
            case_analysis=analysis,
            punishment_justification=just,
            response_time=rt,
            timestamp=datetime.now().isoformat()
        ))

    def export(self, base_name: str):
        """导出结果到JSON和CSV"""
        if not self.results:
            print("⚠️ 没有结果可导出")
            return
            
        records = [asdict(r) for r in self.results]
        json_path = f"{base_name}.json"
        csv_path = f"{base_name}.csv"
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        
        print(f"✓ 已导出: {json_path}, {csv_path}")


# ==================== Main Function ====================
def run_experiment(csv_path: str,
                   model_name: str,
                   samples: int = 5,
                   include_emotional: bool = True,
                   experiment_id_prefix: str = None,
                   reasoning_type: str = "NAN-reasoning",
                   age: str = None,
                   api_url: str = None,
                   api_key: str = None):
    """
    运行单次实验
    
    Args:
        csv_path: CSV数据文件路径
        model_name: 模型名称
        samples: 每个条件的样本数
        include_emotional: 是否包含情感指令
        experiment_id_prefix: 实验ID前缀
        reasoning_type: 推理类型 (NAN-reasoning/long-term-reasoning/short-term-reasoning)
        age: 年龄条件 (age:NAN/age:20/age:30/age:40/age:50/age:60)
        api_url: API URL
        api_key: API密钥
    """
    if experiment_id_prefix is None:
        experiment_id_prefix = "with_emotional" if include_emotional else "without_emotional"
    
    # 如果experiment_id_prefix中包含推理类型，尝试提取
    if reasoning_type == "NAN-reasoning":
        if "NAN-reasoning" in experiment_id_prefix:
            reasoning_type = "NAN-reasoning"
        elif "long-term-reasoning" in experiment_id_prefix:
            reasoning_type = "long-term-reasoning"
        elif "short-term-reasoning" in experiment_id_prefix:
            reasoning_type = "short-term-reasoning"
    
    # 如果experiment_id_prefix中包含年龄条件，尝试提取
    if age is None:
        if "ageNAN" in experiment_id_prefix or "age_NAN" in experiment_id_prefix:
            age = "age:NAN"
        elif "age20" in experiment_id_prefix or "age_20" in experiment_id_prefix:
            age = "age:20"
        elif "age30" in experiment_id_prefix or "age_30" in experiment_id_prefix:
            age = "age:30"
        elif "age40" in experiment_id_prefix or "age_40" in experiment_id_prefix:
            age = "age:40"
        elif "age50" in experiment_id_prefix or "age_50" in experiment_id_prefix:
            age = "age:50"
        elif "age60" in experiment_id_prefix or "age_60" in experiment_id_prefix:
            age = "age:60"
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"🧪 开始实验")
    print("=" * 60)
    
    exp = SimpleExperiment(
        csv_path=csv_path,
        model_name=model_name,
        samples_per_condition=samples,
        include_emotional=include_emotional,
        experiment_id_prefix=experiment_id_prefix,
        reasoning_type=reasoning_type,
        age=age,
        api_url=api_url,
        api_key=api_key
    )
    
    results = exp.run()
    output_name = f"{model_name}_{experiment_id_prefix}_{ts}"
    exp.export(output_name)
    
    if results:
        avg_score = sum(r.score for r in results) / len(results)
        avg_arousal = sum(r.emotional_arousal for r in results) / len(results)
        print(f"\n📊 结果统计:")
        print(f"  平均评分: {avg_score:.2f}")
        print(f"  平均情绪唤醒度: {avg_arousal:.2f}")
        print(f"  总样本数: {len(results)}")
    
    print("✅ 实验完成")
    return results


def main():

    
    """主函数 - 支持命令行参数"""
    parser = argparse.ArgumentParser(
        description='运行LLM惩罚决策实验',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本运行（使用环境变量）
  python experiment_runner.py --model DeepSeek-V3-Fast --samples 10

  # 指定API密钥
  python experiment_runner.py --model DeepSeek-V3-Fast --samples 10 --api-key YOUR_KEY

  # 运行不包含情感指令的实验
  python experiment_runner.py --model DeepSeek-V3-Fast --no-emotional --samples 10

  # 自定义实验ID前缀
  python experiment_runner.py --model DeepSeek-V3-Fast --prefix exp_001 --samples 10
  
  # 指定CSV文件路径
  python experiment_runner.py --model DeepSeek-V3-Fast --csv /path/to/data.csv --samples 10
        """
    )
    
    parser.add_argument('--csv', type=str, 
                       default=None,
                       help='CSV数据文件路径（默认: final_crime_data.csv）')
    parser.add_argument('--model', type=str, required=True,
                       help='模型名称（必需）')
    parser.add_argument('--samples', type=int, default=10,
                       help='每个条件的样本数（默认: 10）')
    parser.add_argument('--no-emotional', action='store_true',
                       help='不包含情感体验指令（默认: 包含）')
    parser.add_argument('--prefix', type=str, default=None,
                       help='实验ID前缀（默认: 根据情感指令自动生成）')
    parser.add_argument('--api-url', type=str, default=None,
                       help='API URL（默认: 从环境变量LLM_API_URL读取）')
    parser.add_argument('--api-key', type=str, default=None,
                       help='API密钥（默认: 从环境变量LLM_API_KEY读取）')
    
    args = parser.parse_args()
    
    # 确定CSV路径
    if args.csv:
        csv_path = args.csv
    else:
        root = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(root, "final_crime_data.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ 错误: CSV文件不存在: {csv_path}")
        return 1
    
    # 运行实验
    try:
        run_experiment(
            csv_path=csv_path,
            model_name=args.model,
            samples=args.samples,
            include_emotional=not args.no_emotional,
            experiment_id_prefix=args.prefix,
            api_url=args.api_url,
            api_key=args.api_key
        )
        return 0
    except Exception as e:
        print(f"❌ 实验运行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

