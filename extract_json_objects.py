def extract_json_objects(str):
    """
    从字符串中提取出 json 数据
    :param str: 包含 json 数据的字符串
    :return: 字符串格式的 json 列表
    """
    json_strs = []
    start_idx = None
    stack = []
    for i, char in enumerate(str):
        if char == '{':
            if not stack:
                start_idx = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    json_str = str[start_idx:i + 1]
                    json_strs.append(json_str)
    return json_strs