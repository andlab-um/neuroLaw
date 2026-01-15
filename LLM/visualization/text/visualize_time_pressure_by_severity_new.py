#!/usr/bin/env python3
"""
研究时间压力对四个文本字段 emotion 密度的影响
【合并案件严重程度】

不再区分 Minor / Serious / Capital，
将所有案件合并后展示：

1 行 × 4 列子图（角色 × 延迟惩罚）

绘图逻辑：
- 四个文本字段
- 三种时间压力（no / short-term / long-term）
- 同色系箱线图 + 散点 + 中位数趋势线
"""

from __future__ import annotations

import json
import glob
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# 基础设置
# =========================
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

TEXT_FIELDS = [
    "emotional_description",
    "reasoning",
    "case_analysis",
    "punishment_justification",
]

OUTPUT_FIGURE = "time_pressure_merged_severity_12_20.png"
OUTPUT_LEGEND = "time_pressure_merged_severity_legend.png"

# =========================
# 工具函数
# =========================
def get_color_variations(base_color, n_variations=3):
    """生成同色系不同深浅的颜色"""
    from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
    rgb_array = np.array([[base_color[0], base_color[1], base_color[2]]])
    hsv = rgb_to_hsv(rgb_array)[0]
    variations = []
    for i in range(n_variations):
        brightness = 0.9 - i * 0.2
        new_rgb = hsv_to_rgb([[hsv[0], hsv[1], brightness]])[0]
        variations.append(tuple(new_rgb))
    return variations


def parse_delay_time(delay_time: str) -> str:
    if delay_time in ("当日", "当曰", None) or str(delay_time).upper() == "NAN":
        return "Immediate"
    return "Delayed"


def parse_time_condition_from_experiment_id(experiment_id: str) -> str:
    if "long-term" in experiment_id:
        return "long-term"
    if "short-term" in experiment_id:
        return "short-term"
    return "no"


def extract_emotion_scores(record: Dict[str, Any]) -> Dict[str, float]:
    scores = {}
    for field in TEXT_FIELDS:
        density = record.get(f"{field}_sentiment_density", {})
        if isinstance(density, dict):
            scores[field] = density.get("emotion", np.nan)
        else:
            scores[field] = np.nan
    return scores

# =========================
# 数据读取
# =========================
def collect_data_from_json_files(root: Path) -> List[Dict[str, Any]]:
    json_files = [
        Path(p) for p in glob.glob(str(root / "*.json"))
        if not p.endswith(".backup")
        and "aggregated_sentiment_scores" not in p
    ]

    all_data = []
    for json_file in sorted(json_files):
        print(f"读取文件: {json_file.name}")
        try:
            with json_file.open("r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, dict):
                    continue
                emotion_scores = extract_emotion_scores(record)
                data_point = {
                    "role": record.get("role", "Unknown"),
                    "delay": parse_delay_time(record.get("delay_time", "NAN")),
                    "time_pressure": parse_time_condition_from_experiment_id(
                        record.get("experiment_id", "")
                    ),
                }
                for field in TEXT_FIELDS:
                    data_point[f"{field}_emotion"] = emotion_scores.get(field, np.nan)
                all_data.append(data_point)
        except Exception as exc:
            print(f"  ✗ 读取失败: {exc}")
    return all_data

# =========================
# 离群值处理
# =========================
def remove_outliers_iqr(df: pd.DataFrame, columns: List[str], multiplier: float = 1.5):
    print(f"\n开始 IQR 离群值检测（倍数={multiplier}）")
    for col in columns:
        valid = df[col].dropna()
        if valid.empty:
            continue
        q1, q3 = valid.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        outliers = (df[col] < lower) | (df[col] > upper)
        if outliers.any():
            print(f"  {col}: {outliers.sum()} 个离群值已置为 NaN")
            df.loc[outliers, col] = np.nan
    return df

# =========================
# 图例
# =========================
def create_legend_figure(metrics, time_order, metric_colors, output_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    handles = []
    for i, (_, name) in enumerate(metrics):
        for j, time_p in enumerate(time_order):
            label = f"{name}: {time_p}" if j == 0 else f"  {time_p}"
            handles.append(
                plt.Line2D([0], [0], lw=4, color=metric_colors[i][j], label=label)
            )
    handles.append(
        plt.Line2D([0], [0], color="#333333", lw=2, label="Trend line (median)")
    )
    ax.legend(handles=handles, loc="center", fontsize=10, frameon=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ 图例已保存: {output_path}")

# =========================
# 主绘图函数
# =========================
def create_time_pressure_plot(df: pd.DataFrame, output_path: str, legend_path: str):
    print("\n开始绘图（合并案件严重程度）")

    fig, axes = plt.subplots(1, 4, figsize=(24, 6))
    role_delay_combinations = [
        ("SPP", "Immediate", 0),
        ("SPP", "Delayed", 1),
        ("TPP", "Immediate", 2),
        ("TPP", "Delayed", 3),
    ]

    time_order = ["no", "short-term", "long-term"]
    metrics = [
        ("emotional_description_emotion", "Emotional Description"),
        ("reasoning_emotion", "Reasoning"),
        ("case_analysis_emotion", "Case Analysis"),
        ("punishment_justification_emotion", "Punishment Justification"),
    ]

    base_colors = sns.color_palette("husl", len(metrics))
    metric_colors = {i: get_color_variations(base_colors[i], 3) for i in range(len(metrics))}

    for role, delay, col_idx in role_delay_combinations:
        ax = axes[col_idx]
        subset = df[(df["role"] == role) & (df["delay"] == delay)]
        print(f"  ALL × {role} × {delay}: {len(subset)} 条")
        if subset.empty:
            continue

        width = 0.55
        within_spacing = 0.2
        group_spacing = 0.8
        x_positions = []

        for i, (metric_key, _) in enumerate(metrics):
            box_data = []
            time_indices = []
            scatter_data = []

            for j, time_p in enumerate(time_order):
                vals = subset[subset["time_pressure"] == time_p][metric_key].dropna()
                if not vals.empty:
                    box_data.append(vals.values)
                    time_indices.append(j)
                    x_jitter = np.random.normal(j * (1 + within_spacing), 0.02, len(vals))
                    for x, y in zip(x_jitter, vals.values):
                        scatter_data.append((i, x, y, j))

            if not box_data:
                continue

            x_start = i * (len(time_order) * (1 + within_spacing) + group_spacing)
            positions = [x_start + j * (1 + within_spacing) for j in range(len(box_data))]

            # 绘制散点
            scatter_by_time = {}
            for _, x_j, y, time_idx in scatter_data:
                if time_idx not in scatter_by_time:
                    scatter_by_time[time_idx] = {'x': [], 'y': []}
                scatter_by_time[time_idx]['x'].append(x_start + x_j)
                scatter_by_time[time_idx]['y'].append(y)
            for time_idx, data in scatter_by_time.items():
                color = metric_colors[i][time_idx]
                ax.scatter(data['x'], data['y'], color=color, alpha=0.3, s=12, edgecolors='none', zorder=1)

            # 绘制箱线图
            bp = ax.boxplot(
                box_data,
                positions=positions,
                widths=width,
                patch_artist=True,
                showfliers=False,
            )
            for idx, patch in enumerate(bp["boxes"]):
                color = metric_colors[i][time_indices[idx]]
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

            # 绘制中位数趋势线
            medians = [np.median(d) for d in box_data]
            if len(medians) > 1:
                ax.plot(
                    positions,
                    medians,
                    color="#333333",
                    marker="o",
                    lw=2,
                    zorder=3,
                )

            x_positions.extend(positions)

        if x_positions:
            ax.set_xlim(min(x_positions) - 0.5, max(x_positions) + 0.5)

        ax.set_xticks([])
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.set_ylim(-0.95, 0.35)

        ax.tick_params(axis="y", labelleft=False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ 主图已保存: {output_path}")

    create_legend_figure(metrics, time_order, metric_colors, legend_path)

# =========================
# main
# =========================
def main():
    root = Path(__file__).parent
    print("开始读取数据...")
    data = collect_data_from_json_files(root)
    if not data:
        print("未找到数据")
        return

    df = pd.DataFrame(data)
    emotion_cols = [f"{f}_emotion" for f in TEXT_FIELDS]
    df = remove_outliers_iqr(df, emotion_cols)

    create_time_pressure_plot(
        df,
        root / OUTPUT_FIGURE,
        root / OUTPUT_LEGEND,
    )
    print("\n完成")

if __name__ == "__main__":
    main()
