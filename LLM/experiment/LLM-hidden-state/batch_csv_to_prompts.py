#!/usr/bin/env python3
"""
批量读取CSV文件中的文本并转换为prompt列表
参考 experiment_runner.py 的代码风格和结构
"""

import os
import argparse
import glob
from typing import List, Optional, Tuple
import pandas as pd


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
            return pd.DataFrame()

    def get_cases(self, 
                  text_column: str = "案件内容", 
                  delay_column: str = "延迟时间") -> List[Tuple[str, Optional[str]]]:
        """获取文本及延迟时间"""
        if self.data.empty:
            return []
        
        if text_column not in self.data.columns:
            print(f"⚠️ 列 '{text_column}' 不存在，可用列: {list(self.data.columns)}")
            return []
        if delay_column not in self.data.columns:
            print(f"⚠️ 列 '{delay_column}' 不存在，可用列: {list(self.data.columns)}")
            return []
        
        cases: List[Tuple[str, Optional[str]]] = []
        for _, row in self.data.iterrows():
            text = str(row[text_column]).strip()
            if not text:
                continue
            delay = row.get(delay_column)
            cases.append((text, None if pd.isna(delay) else str(delay).strip()))
        return cases


# ==================== Prompt Building ====================
PROMPT_TYPES = ("punishment", "emotion")


def build_prompt(role: str, 
                case_desc: str, 
                time_condition: Optional[str] = None,
                delay_label: Optional[str] = None,
                prompt_type: str = "punishment") -> str:
    """
    构建实验提示词
    
    Args:
        role: 角色 (SPP/TPP)
        case_desc: 案件描述
        time_condition: 时间条件 (即时/延迟)
        delay_label: 原始延迟字段内容，用于展示
        prompt_type: prompt类型（punishment 或 emotion）
    """
    if prompt_type not in PROMPT_TYPES:
        raise ValueError(f"prompt_type 必须为 {PROMPT_TYPES} 之一")
    
    # 角色设置
    role_prefix = "你是一名受害者" if role == "SPP" else "你是一名法官"
    
    # 时间条件说明
    time_instruction = ""
    if time_condition:
        if time_condition == "即时":
            if delay_label:
                time_instruction = f"注意：案件在{delay_label}发生，你需要立即做出判断。"
            else:
                time_instruction = "注意：这是一个即时发生的案件，你需要立即做出判断。"
        elif time_condition == "延迟":
            if delay_label:
                time_instruction = f"注意：这是一个延迟发生的案件（延迟时间：{delay_label}）。"
            else:
                time_instruction = "注意：这是一个延迟发生的案件，案件已经过去一段时间。"
    
    # 构建完整的提示词
    parts = [role_prefix + "。"]
    
    parts.append("\n案件描述：" + case_desc)
    
    if time_instruction:
        parts.append("\n" + time_instruction)
    
    parts.append("\n")
    
    if prompt_type == "punishment":
        parts.append("请你判断犯罪者应当受到多严厉的惩罚。\n")
        parts.append("评分标准：\n")
        parts.append("0 分 —— 不给予任何刑罚\n")
        parts.append("9 分 —— 死刑\n")
        parts.append("分数越高，对应的惩罚越严厉,所以谨慎确定你的打分\n")
        parts.append("坚决不要输出其他文本,仅输出这个json格式的内容;请严格按照以下JSON格式输出你的回答：\n")
        parts.append("{\n")
        parts.append("    \"punishment_score\": <0-9的整数>,\n")
        parts.append("}\n")
        parts.append("回答完请立刻输出[STOP], 必须在50词以内以[STOP]结尾，否则结果无效\n")
        parts.append("仅输出json格式的内容,必须在50词以内输出我们要的惩罚数字,否则结果无效")
    else:
        parts.append("请你判断当前的情绪激发情况。\n")
        parts.append("评分标准：\n")
        parts.append("0 分 —— 完全平静，无情绪波动\n")
        parts.append("9 分 —— 情绪高度激动或紧张\n")
        parts.append("分数越高，对应的情绪越浓烈,所以谨慎确定你的打分\n")
        parts.append("坚决不要输出其他文本,仅输出这个json格式的内容;请严格按照以下JSON格式输出你的回答：\n")
        parts.append("{\n")
        parts.append("    \"emotional_score\": <0-9的整数>,\n")
        parts.append("}\n")
        parts.append("回答完请立刻输出[STOP], 必须在50词以内以[STOP]结尾，否则结果无效\n")
        parts.append("仅输出json格式的内容,必须在50词以内输出我们要的情绪数字,否则结果无效")
    
    return "".join(parts)
 

def build_simple_prompt(text: str) -> str:
    """
    构建简单的prompt（仅包含文本内容）
    
    Args:
        text: 文本内容
    """
    return text


# ==================== Batch Processor ====================
class BatchCSVProcessor:
    """批量CSV处理器"""
    
    def __init__(self, 
                 csv_paths: List[str],
                 text_column: str = "案件内容",
                 delay_column: str = "延迟时间",
                 use_full_prompt: bool = True,
                 roles: Optional[List[str]] = None,
                 ):
        """
        初始化批量处理器
        
        Args:
            csv_paths: CSV文件路径列表
            text_column: 文本列名
            delay_column: 延迟时间列名
            use_full_prompt: 是否使用完整的prompt（True）或简单文本（False）
            roles: 角色列表 (SPP/TPP)，仅在 use_full_prompt=True 时使用
        """
        self.csv_paths = csv_paths
        self.text_column = text_column
        self.delay_column = delay_column
        self.use_full_prompt = use_full_prompt
        self.roles = roles or ["SPP", "TPP"]
        self.prompts: List[str] = []
    
    def process(self) -> List[str]:
        """处理所有CSV文件并生成prompt列表"""
        self.prompts = []
        
        for csv_path in self.csv_paths:
            if not os.path.exists(csv_path):
                print(f"⚠️ 文件不存在: {csv_path}")
                continue
            
            print(f"\n处理文件: {csv_path}")
            csv_loader = CSVCases(csv_path)
            cases = csv_loader.get_cases(self.text_column, self.delay_column)
            
            if not cases:
                print(f"  ⚠️ 未找到有效文本")
                continue
            
            print(f"  ✓ 找到 {len(cases)} 条文本")
            
            for text, delay in cases:
                if self.use_full_prompt:
                    time_cond = self._infer_time_condition(delay)
                    
                    for role in self.roles:
                        for prompt_type in PROMPT_TYPES:
                            prompt = build_prompt(
                                role=role,
                                case_desc=text,
                                time_condition=time_cond,
                                delay_label=delay,
                                prompt_type=prompt_type
                            )
                            self.prompts.append(prompt)
                else:
                    prompt = build_simple_prompt(text)
                    self.prompts.append(prompt)
        
        print(f"\n✓ 总共生成 {len(self.prompts)} 个prompt")
        return self.prompts
    
    @staticmethod
    def _infer_time_condition(delay_value: Optional[str]) -> Optional[str]:
        """根据延迟字段推断时间条件"""
        if not delay_value:
            return None
        if any(token in delay_value for token in ("当日", "当曰", "即时")):
            return "即时"
        return "延迟"
    
    def print_all(self):
        """逐个打印所有prompt"""
        if not self.prompts:
            print("⚠️ 没有prompt可打印，请先调用 process() 方法")
            return
        
        print("\n" + "=" * 80)
        print("开始打印所有prompt")
        print("=" * 80)
        
        for i, prompt in enumerate(self.prompts, 1):
            print(f"\n{'='*80}")
            print(f"Prompt #{i}/{len(self.prompts)}")
            print(f"{'='*80}")
            print(prompt)
            print(f"{'='*80}")
        
        print(f"\n✓ 已打印所有 {len(self.prompts)} 个prompt")


# ==================== Main Function ====================
def main():
    """主函数 - 支持命令行参数"""
    parser = argparse.ArgumentParser(
        description='批量读取CSV文件中的文本并转换为prompt列表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个CSV文件
  python batch_csv_to_prompts.py --csv data.csv

  # 处理多个CSV文件（使用通配符）
  python batch_csv_to_prompts.py --csv "*.csv"

  # 处理多个CSV文件（指定多个文件）
  python batch_csv_to_prompts.py --csv file1.csv --csv file2.csv

  # 使用简单文本模式（不构建完整prompt）
  python batch_csv_to_prompts.py --csv data.csv --simple

  # 指定文本列名
  python batch_csv_to_prompts.py --csv data.csv --column "文本内容"

  # 指定角色和其他参数
  python batch_csv_to_prompts.py --csv data.csv --role TPP --no-emotional --reasoning long-term-reasoning
        """
    )
    
    parser.add_argument('--csv', type=str, action='append',
                       help='CSV文件路径（可指定多个，或使用通配符）')
    parser.add_argument('--column', type=str, default='案件内容',
                       help='文本列名（默认: 案件内容）')
    parser.add_argument('--simple', action='store_true',
                       help='使用简单文本模式（不构建完整prompt）')
    parser.add_argument('--roles', type=str, nargs='+', choices=['SPP', 'TPP'],
                       default=['SPP', 'TPP'],
                       help='角色列表（默认: SPP TPP）')
    parser.add_argument('--delay-column', type=str, default='延迟时间',
                       help='延迟时间列名（默认: 延迟时间）')
    
    args = parser.parse_args()
    
    # 确定CSV文件列表
    csv_paths = []
    if args.csv:
        for csv_pattern in args.csv:
            # 检查是否是通配符模式
            if '*' in csv_pattern or '?' in csv_pattern:
                matched = glob.glob(csv_pattern)
                if matched:
                    csv_paths.extend(matched)
                else:
                    print(f"⚠️ 未找到匹配的文件: {csv_pattern}")
            else:
                csv_paths.append(csv_pattern)
    else:
        # 默认查找当前目录下的CSV文件
        root = os.path.dirname(os.path.abspath(__file__))
        default_csv = os.path.join(root, "final_crime_data.csv")
        if os.path.exists(default_csv):
            csv_paths = [default_csv]
        else:
            print("❌ 错误: 未指定CSV文件，且未找到默认文件 final_crime_data.csv")
            return 1
    
    if not csv_paths:
        print("❌ 错误: 未找到任何CSV文件")
        return 1
    
    # 去重
    csv_paths = list(set(csv_paths))
    print(f"📁 找到 {len(csv_paths)} 个CSV文件")
    
    # 创建处理器并处理
    try:
        processor = BatchCSVProcessor(
            csv_paths=csv_paths,
            text_column=args.column,
            delay_column=args.delay_column,
            use_full_prompt=not args.simple,
            roles=args.roles
        )
        
        processor.process()
        processor.print_all()
        
        return 0
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

