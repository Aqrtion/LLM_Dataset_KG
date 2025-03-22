def load_prompts(system_prompt_path, user_prompt_path):
    """
    读取系统提示词和用户提示词
    :param system_prompt_path: 系统提示词路径
    :param user_prompt_path: 用户提示词路径
    :return: system_prompt, user_prompt
    """
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    with open(user_prompt_path, "r", encoding="utf-8") as f:
        user_prompt = f.read()
    return system_prompt, user_prompt