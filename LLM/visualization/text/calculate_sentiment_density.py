#!/usr/bin/env python3
"""
脚本用于计算情感密度：将sentiment_score中的六个指标（vision, socialness, emotion, time, space, motor）
除以word_num，得到情感密度，并保存到对应的sentiment_density字段中。
"""

import json
import os
import glob
from pathlib import Path

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

# 需要计算密度的六个指标
DENSITY_METRICS = [
    "vision",
    "socialness",
    "emotion",
    "time",
    "space",
    "motor"
]

# 结果字段的命名
def get_sentiment_score_field_name(original_field):
    """获取sentiment_score字段名"""
    return f"{original_field}_sentiment_score"

def get_sentiment_density_field_name(original_field):
    """获取sentiment_density字段名"""
    return f"{original_field}_sentiment_density"


def calculate_density(sentiment_score):
    """
    计算情感密度：将六个指标除以word_num
    
    Args:
        sentiment_score: 包含情感分数的字典，包含vision, socialness, emotion, time, space, motor, word_num
    
    Returns:
        包含密度值的字典，如果word_num为0或不存在则返回None
    """
    if not sentiment_score or not isinstance(sentiment_score, dict):
        return None
    
    # 获取word_num
    word_num = sentiment_score.get('word_num')
    if word_num is None or word_num == 0:
        return None
    
    # 计算密度
    density = {}
    for metric in DENSITY_METRICS:
        if metric in sentiment_score:
            density[metric] = sentiment_score[metric] / word_num
        else:
            density[metric] = None
    
    # word_num保持不变（不除以自己）
    density['word_num'] = word_num
    
    return density


def process_json_file(json_path):
    """处理单个 JSON 文件，计算并添加情感密度"""
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
            sentiment_score_field = get_sentiment_score_field_name(field)
            sentiment_density_field = get_sentiment_density_field_name(field)
            
            # 检查是否存在sentiment_score字段
            if sentiment_score_field in record:
                sentiment_score = record[sentiment_score_field]
                density = calculate_density(sentiment_score)
                
                if density:
                    # 保存密度到新字段（覆盖已存在的）
                    record[sentiment_density_field] = density
                    updated_count += 1
                else:
                    print(f"  警告: 记录 {idx} 的 {sentiment_score_field} 无法计算密度（word_num为0或不存在）")
        
        # 处理combined_sentiment_score（如果存在）
        if "combined_sentiment_score" in record:
            combined_score = record["combined_sentiment_score"]
            density = calculate_density(combined_score)
            if density:
                record["combined_sentiment_density"] = density
                updated_count += 1
        
        # 每处理 100 条记录显示一次进度
        if (idx + 1) % 100 == 0:
            print(f"  已处理 {idx + 1}/{total_records} 条记录...")
    
    # 保存回文件
    try:
        # 创建备份
        backup_path = json_path + '.backup_density'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ 已创建备份文件: {os.path.basename(backup_path)}")
        
        # 保存更新后的数据
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 成功处理 {updated_count} 个密度字段，已保存到文件")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    
    # 查找所有 JSON 文件（排除备份文件）
    json_files = [
        f for f in glob.glob(str(script_dir / '*.json'))
        if not f.endswith('.backup') 
        and not f.endswith('.backup_sentiment')
        and not f.endswith('.backup_density')
    ]
    
    if not json_files:
        print("未找到 JSON 文件")
        return
    
    print(f"\n找到 {len(json_files)} 个 JSON 文件")
    
    # 处理每个文件
    success_count = 0
    for json_file in json_files:
        if process_json_file(json_file):
            success_count += 1
    
    print(f"\n完成! 成功处理 {success_count}/{len(json_files)} 个文件")


if __name__ == '__main__':
    main()
