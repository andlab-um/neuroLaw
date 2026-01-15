#!/usr/bin/env python3
"""
实验脚本 45: age:40 | long-term-reasoning | with_emotion | Qwen3-235B-A22B-Instruct-2507
"""

import os
import sys

# 添加项目根目录到路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from experiment_runner import run_experiment

if __name__ == "__main__":
    # 实验配置
    # 获取项目根目录（脚本在experiment_scripts子目录中，需要回到上一级）
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(root_dir, "final_crime_data.csv")
    model_name = "Qwen3-235B-A22B-Instruct-2507"
    samples_per_condition = 10  # 可根据需要调整
    include_emotional = True
    age = "age:40"
    experiment_prefix = "exp045_age40_long-term-reasoning_with_emotion_Qwen"
    
    # 模型名称简写（用于文件名）
    model_short = "Qwen"
    age_short = "age40"
    
    print("=" * 80)
    print(f"实验 45: age:40 | long-term-reasoning | with_emotion | Qwen3-235B-A22B-Instruct-2507")
    print("=" * 80)
    
    try:
        # 从experiment_prefix中提取reasoning_type
        reasoning_type = "NAN-reasoning"
        if "NAN-reasoning" in experiment_prefix:
            reasoning_type = "NAN-reasoning"
        elif "long-term-reasoning" in experiment_prefix:
            reasoning_type = "long-term-reasoning"
        elif "short-term-reasoning" in experiment_prefix:
            reasoning_type = "short-term-reasoning"
        
        run_experiment(
            csv_path=csv_path,
            model_name=model_name,
            samples=samples_per_condition,
            include_emotional=include_emotional,
            experiment_id_prefix=experiment_prefix,
            reasoning_type=reasoning_type,
            age=age
        )
        print(f"\n✅ 实验 45 完成")
    except Exception as e:
        print(f"\n❌ 实验 45 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
