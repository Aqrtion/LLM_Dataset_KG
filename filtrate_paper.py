import json
import os
from call_deepseek_api import call_deepseek_api
from load_prompt import load_prompts
from save_to_json import save_to_json

SYSTEM_PROMPT_PATH = "Prompt/filtrate_paper/system.txt"
USER_PROMPT_PATH = "Prompt/filtrate_paper/user.txt"
OUTPUT_DIR = "2_filtrate_paper"

def construct_input_message(json_path):
    """
    读取 JSON 文件, 提取 "title_abstract_introduction" 和 "data_related_paragraphs" 然后将它们组合成 input_message
    :param json_path: 输入 JSON 文件路径
    :return: input_message
    """
    print("Start constructing input message...")

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    title_author_abstract_introduction = data.get("title_author_abstract_introduction", "")
    data_related_paragraphs = data.get("data_related_paragraphs", [])

    # 将所有段落转换为字符串
    all_paragraphs = [str(p) for p in data_related_paragraphs]

    # 构造 input_message
    input_message = (
            "Title, author, abstract and Introduction:\n" +
            title_author_abstract_introduction + "\n\n" +
            "Data Related Paragraphs:\n" +
            "\n\n".join(all_paragraphs)
    )

    print("Input message constructed successfully.")
    return input_message

def filtrate_paper(json_path, filtrate_output_name=None):
    """
    调用 DeepSeek API 获取过滤结果
    :param json_path: 输入 JSON 文件路径
    :param filtrate_output_name: 过滤结果 (JSON 格式) 文件名
    :return: None
    """
    print("Filtering the paper...")

    input_message = construct_input_message(json_path)
    system_prompt, user_prompt = load_prompts(SYSTEM_PROMPT_PATH, USER_PROMPT_PATH)

    filtrate_result = call_deepseek_api(system_prompt, user_prompt, input_message)

    print(filtrate_result)

    if filtrate_result is None:
        raise ValueError("Paper filtration failed due to invalid API response.")

    # 生成默认输出文件名
    base_name = os.path.splitext(os.path.basename(json_path))[0].replace("split", "filtrate")

    if filtrate_output_name is None:
        filtrate_output_name = f"{base_name}.json"

    # 保存输出文件
    json_dict = json.loads(filtrate_result)
    json_output_path = save_to_json(json_dict, OUTPUT_DIR, filtrate_output_name)  # 将提取内容保存为 JSON 文件

    print("Paper filtration completed successfully.")

    return json_output_path

# 当作为主程序运行时，提供命令行接口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Paper Filtrate")
    parser.add_argument("--input_json", help="Input JSON file path", default=None)
    parser.add_argument("--output_json", help="Output JSON file name", default=None)
    args = parser.parse_args()

    filtrate_paper(args.input_json, args.output_json)
