#!/usr/bin/env python3
"""
可视化情绪刺激下三种时间压力情况（no, short-term, long-term）
对三个文本长度指标的影响（1×3 横向排列，保留折线）

分析指标：
1. 词数
2. 去重后词数
3. 句数
"""

from __future__ import annotations

import json
import glob
import re
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

TEXT_FIELDS = [
    "emotional_description",
    "reasoning",
    "case_analysis",
    "punishment_justification",
]

FIELD_NAMES = {
    "emotional_description": "Emotional Description",
    "reasoning": "Reasoning",
    "case_analysis": "Case Analysis",
    "punishment_justification": "Punishment Justification",
}

OUTPUT_FIGURE = "text_length_by_time_pressure_.png"
OUTPUT_LEGEND = "text_length_by_time_pressure_legend.png"


def parse_time_condition_from_experiment_id(experiment_id: str) -> str:
    if "long-term" in experiment_id:
        return "long-term"
    elif "short-term" in experiment_id:
        return "short-term"
    else:
        return "no"


def count_words(text: str) -> int:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z0-9]+', text))
    return chinese_chars + english_words


def count_unique_words(text: str) -> int:
    chinese_chars = set(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', text))
    return len(chinese_chars) + len(english_words)


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'[。！？.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_text_metrics(text: str) -> Dict[str, Any]:
    wc = count_words(text)
    return {
        "word_count": wc,
        "unique_word_count": count_unique_words(text),
        "sentence_count": len(split_sentences(text)) or (1 if wc > 0 else 0),
    }


def collect_data_from_json_files(root: Path) -> List[Dict[str, Any]]:
    json_files = [Path(p) for p in glob.glob(str(root / "*.json"))]
    all_data = []

    for jf in json_files:
        with jf.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, list):
            continue

        for r in records:
            exp_id = r.get("experiment_id", "")
            if "with_emotion" not in exp_id:
                continue

            tp = parse_time_condition_from_experiment_id(exp_id)

            for field in TEXT_FIELDS:
                text = r.get(field, "")
                if not isinstance(text, str) or not text.strip():
                    continue

                metrics = calculate_text_metrics(text)
                if metrics["word_count"] == 0:
                    continue

                all_data.append({
                    "time_pressure": tp,
                    "field_name": FIELD_NAMES[field],
                    **metrics
                })

    return all_data


def create_text_length_visualization(df: pd.DataFrame, output_path: str, legend_path: str):
    time_order = ["no", "short-term", "long-term"]
    field_order = list(FIELD_NAMES.values())

    fig, axes = plt.subplots(1, 3, figsize=(24, 7))

    metrics_config = [
        {"key": "word_count", "ax": axes[0]},
        {"key": "unique_word_count", "ax": axes[1]},
        {"key": "sentence_count", "ax": axes[2]},
    ]

    time_colors = {
        "no": "#FFB6C1",
        "short-term": "#87CEEB",
        "long-term": "#98D8C8",
    }

    for cfg in metrics_config:
        metric = cfg["key"]
        ax = cfg["ax"]

        plot_df = df[[metric, "field_name", "time_pressure"]].dropna()

        bar_info = []
        x_start = 0
        width = 0.6
        spacing = 0.3
        group_spacing = 1.5

        for field in field_order:
            xs, ys, tps = [], [], []

            for tp in time_order:
                subset = plot_df[
                    (plot_df["field_name"] == field) &
                    (plot_df["time_pressure"] == tp)
                ][metric]

                if subset.empty:
                    continue

                mean = subset.mean()
                sem = subset.std() / np.sqrt(len(subset))

                bar_info.append((x_start, mean, sem, tp))
                xs.append(x_start)
                ys.append(mean)
                tps.append(tp)

                x_start += width + spacing

            # 折线（关键：保留）
            if len(xs) > 1:
                order = sorted(range(len(tps)), key=lambda i: time_order.index(tps[i]))
                ax.plot(
                    [xs[i] for i in order],
                    [ys[i] for i in order],
                    color="#333333",
                    marker="o",
                    linewidth=2,
                    zorder=3,
                )

            x_start += group_spacing

        # 柱子 + 误差线
        for x, h, sem, tp in bar_info:
            ax.bar(
                x, h, width=width,
                color=time_colors[tp],
                alpha=0.7,
                edgecolor="white",
                zorder=2,
            )
            ax.errorbar(
                x, h, yerr=sem,
                color="black",
                capsize=3,
                linewidth=1,
                zorder=4,
            )

        # ax.set_title(metric.replace("_", " ").title())
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        # 去掉上、右边框
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    root = Path(__file__).parent
    df = pd.DataFrame(collect_data_from_json_files(root))

    if df.empty:
        print("未找到数据")
        return

    create_text_length_visualization(
        df,
        root / OUTPUT_FIGURE,
        root / OUTPUT_LEGEND,
    )

    print("✓ 图表生成完成")


if __name__ == "__main__":
    main()
