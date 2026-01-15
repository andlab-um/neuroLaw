def build_prompt(
    role: str,
    case_description: str,
    include_emotional: bool = True,
    reasoning_type: str = "NAN-reasoning",
    time_condition: str | None = None,
    age: str | None = None
) -> str:
    """
    构建用于惩罚决策实验的 Prompt

    Args:
        role: 视角角色, "SPP"(受害者) 或 "TPP"(法官)
        case_description: 案件文本描述
        include_emotional: 是否引入情感体验指令
        reasoning_type: 推理条件
            - "NAN-reasoning"
            - "long-term-reasoning"
            - "short-term-reasoning"
        time_condition: 时间条件
            - "即时"
            - "延迟"
            - None
        age: 年龄条件, 例如 "age:20", "age:40", 或 None

    Returns:
        完整 prompt 字符串
    """

    # ---------- 1. 角色设定 ----------
    role_instruction = (
        "你是一名受害者。" if role == "SPP"
        else "你是一名法官。"
    )

    # ---------- 2. 年龄条件 ----------
    age_instruction = ""
    if age and age != "age:NAN":
        age_num = age.replace("age:", "")
        age_instruction = f"你当前的年龄是{age_num}岁，请从这一年龄阶段的视角进行判断。"

    # ---------- 3. 时间条件 ----------
    time_instruction = ""
    if time_condition == "即时":
        time_instruction = "注意：这是一个即时发生的案件，你需要立刻做出判断。"
    elif time_condition == "延迟":
        time_instruction = "注意：这是一个延迟发生的案件，案件已经过去一段时间。"

    # ---------- 4. 推理条件 ----------
    reasoning_instruction_map = {
        "NAN-reasoning": "",
        "long-term-reasoning": "你有较为充足的时间进行思考和反应。",
        "short-term-reasoning": "你需要在时间紧迫的情况下迅速做出判断。"
    }
    reasoning_instruction = reasoning_instruction_map.get(reasoning_type, "")

    # ---------- 5. 情感体验指令 ----------
    emotional_instruction = (
        "请根据你个人的情感体验进行判断，充分感受案件带来的情绪影响。"
        if include_emotional else ""
    )

    # ---------- 6. 输出格式与任务说明 ----------
    task_instruction = """
请你判断犯罪者应当受到多严厉的惩罚。

评分标准：
0 分 —— 不给予任何刑罚
9 分 —— 死刑
分数越高，对应的惩罚越严厉

请严格按照以下 JSON 格式输出你的回答：
{
    "punishment_score": <0-9 的整数>,
    "reasoning": "<评分理由>",
    "emotional_arousal": <0-9 的整数>,
    "emotional_description": "<情绪状态描述>",
    "case_analysis": "<对案件的分析>",
    "punishment_justification": "<惩罚合理性的说明>"
}
""".strip()

    # ---------- 7. 拼接 Prompt ----------
    prompt_parts = [
        role_instruction,
        age_instruction,
        "",
        "案件描述：",
        case_description,
        "",
        time_instruction,
        reasoning_instruction,
        emotional_instruction,
        "",
        task_instruction
    ]

    # 过滤空字符串并拼接
    prompt = "\n".join(p for p in prompt_parts if p.strip())

    return prompt
