#!/usr/bin/env python3
"""
脚本用于读取所有 JSON 文件中的四个文本字段，使用 cntext 计算情感分数，并保存回原始文件。
"""

import json
import os
import glob
from pathlib import Path
import cntext as ct
import pandas as pd

# 尝试导入 tqdm，如果没有则使用简单的进度显示
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc=""):
        return iterable

# 需要处理的字段
FIELDS_TO_PROCESS = [
    "reasoning",
    "emotional_description", 
    "case_analysis",
    "punishment_justification"
]

# 结果字段的命名（在原字段名后加上 _sentiment_score）
def get_sentiment_field_name(original_field):
    return f"{original_field}_sentiment_score"


def load_concreteness_dict(yaml_path):
    """加载情感词典"""
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"找不到 YAML 文件: {yaml_path}")
    
    concreteness_dict = ct.read_yaml_dict(yaml_path)['Dictionary']
    return concreteness_dict


def calculate_sentiment(text, concreteness_dict):
    """计算文本的情感分数"""
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return {}
    
    try:
        score = ct.sentiment_by_valence(
            text=text,
            diction=concreteness_dict,
            lang='chinese'
        )
        return score if score else {}
    except Exception as e:
        print(f"计算情感分数时出错: {e}")
        return {}


def process_json_file(json_path, concreteness_dict):
    """处理单个 JSON 文件"""
    print(f"\n处理文件: {os.path.basename(json_path)}")
    
    # 读取 JSON 文件
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
    if not isinstance(data, list):
        print(f"警告: 文件格式不是数组，跳过")
        return False
    
    # 处理每个记录
    updated_count = 0
    total_records = len(data)
    for idx, record in enumerate(tqdm(data, desc="处理记录")):
        if not isinstance(record, dict):
            continue
        
        # 处理每个字段
        for field in FIELDS_TO_PROCESS:
            if field in record:
                text = record[field]
                sentiment_score = calculate_sentiment(text, concreteness_dict)
                
                # 保存结果到新字段
                sentiment_field = get_sentiment_field_name(field)
                record[sentiment_field] = sentiment_score
                updated_count += 1
        
        # 每处理 100 条记录显示一次进度
        if (idx + 1) % 100 == 0:
            print(f"  已处理 {idx + 1}/{total_records} 条记录...")
    
    # 保存回文件
    try:
        # 创建备份
        backup_path = json_path + '.backup_sentiment'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 保存更新后的数据
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 成功处理 {updated_count} 个字段，已保存到文件")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    
    # 查找 YAML 文件（尝试多个可能的位置）
    yaml_paths = [
        script_dir / 'zh_valence_SixSemanticDimensionDatabase.yaml',
        script_dir.parent / 'zh_valence_SixSemanticDimensionDatabase.yaml',
        script_dir.parent.parent / 'zh_valence_SixSemanticDimensionDatabase.yaml',
    ]
    
    yaml_path = None
    for path in yaml_paths:
        if path.exists():
            yaml_path = str(path)
            break
    
    if not yaml_path:
        # 如果找不到，让用户输入
        print("未找到 zh_valence_SixSemanticDimensionDatabase.yaml 文件")
        yaml_path = input("请输入 YAML 文件的完整路径: ").strip()
        if not os.path.exists(yaml_path):
            print(f"错误: 文件不存在: {yaml_path}")
            return
    
    print(f"使用 YAML 文件: {yaml_path}")
    
    # 加载词典
    try:
        concreteness_dict = load_concreteness_dict(yaml_path)
        print("✓ 成功加载情感词典")
    except Exception as e:
        print(f"加载词典失败: {e}")
        return
    
    # 查找所有 JSON 文件（排除备份文件）
    json_files = [
        f for f in glob.glob(str(script_dir / '*.json'))
        if not f.endswith('.backup') and not f.endswith('.backup_sentiment')
    ]
    
    if not json_files:
        print("未找到 JSON 文件")
        return
    
    print(f"\n找到 {len(json_files)} 个 JSON 文件")
    
    # 处理每个文件
    success_count = 0
    for json_file in json_files:
        if process_json_file(json_file, concreteness_dict):
            success_count += 1
    
    print(f"\n完成! 成功处理 {success_count}/{len(json_files)} 个文件")


if __name__ == '__main__':
    main()

