import json
import os

def save_to_json(json_dict, output_dir, output_name):
    """
    将过滤后的内容保存为 JSON 文件
    :param json_dict: 要保存的 JSON 文件内容 (字典格式)
    :param output_dir: 输出文件目录
    :param output_name: JSON 文件名
    :return: None
    """
    # 确保解析后的数据是字典
    if not isinstance(json_dict, dict):
        raise ValueError(f"Error: Expected a dictionary, but got {type(json_dict)}. Response: {repr(json_dict)}")

    # 生成 JSON 文件路径
    json_path = os.path.join(output_dir, output_name)
    os.makedirs(output_dir, exist_ok=True)

    # 保存到 JSON 文件
    print(f"Saving extracted content to JSON: {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=4)
    print(f"Filtration results saved to {json_path}")

    return json_path