import json
import os
from datetime import datetime

from call_deepseek_api import call_deepseek_api, call_deepseek_api_with_time
from extract_json_objects import extract_json_objects
from load_prompt import load_prompts
from save_to_json import save_to_json
from split_txt import read_txt_file, extract_key_information, extract_dataset_related_paragraphs

# 输出文件保存路径
ENTITIES_DIR = "3_extract_knowledge/Entities"
RELATIONS_DIR = "3_extract_knowledge/Relations"
KG_DIR = "3_extract_knowledge/KGs"

# 提示词存放路径
SYSTEM_PROMPT_PATH = "Prompt/extract_knowledge/system.txt"
USER_PROMPT_PATH = "Prompt/extract_knowledge/user.txt"

def construct_input_message(txt_path, json_path):
    """
    根据论文过滤结果, 重新读取 TXT 文件,
    提取 "title_author_abstract_introduction" 和 "dataset_related_paragraphs" 然后将它们组合成 input_message
    :param txt_path: TXT 文件路径
    :param json_path: JSON 文件路径
    :return: input_message
    """
    text = read_txt_file(txt_path)  # 读入 TXT 文件
    title_author_abstract_introduction, remaining_paragraphs = extract_key_information(text)  # 提取标题, 作者, 摘要, 引言

    # 读取 JSON 配置文件
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 获取数据集的 full_name 和 abbreviation
    full_name = config.get("dataset_info", {}).get("full_name")
    abbreviation = config.get("dataset_info", {}).get("abbreviation")

    dataset_related_paragraphs = extract_dataset_related_paragraphs(remaining_paragraphs, full_name, abbreviation)  # 提取数据集相关段落

    all_paragraphs = [str(p) for p in dataset_related_paragraphs]  # 将所有段落转换为字符串

    # 构造 input_message
    input_message = (
            "Title, author, abstract and Introduction:\n" +
            title_author_abstract_introduction + "\n\n" +
            "Dataset Related Paragraphs:\n" +
            "\n\n".join(all_paragraphs)
    )

    return input_message

def extract_knowledge(txt_path, json_path):
    """
    调用 DeepSeek API 完成知识抽取
    :param txt_path: TXT 文件路径
    :param json_path: JSON 文件路径
    :return: None
    """
    input_message = construct_input_message(txt_path, json_path)
    system_prompt, user_prompt = load_prompts(SYSTEM_PROMPT_PATH, USER_PROMPT_PATH)

    # 获取当前时间用于区分实体
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # 调用 DeepSeek API 进行知识抽取
    extract_result = call_deepseek_api_with_time(system_prompt, user_prompt, input_message, formatted_time)

    json_strs = extract_json_objects(extract_result)

    # 返回结果第一个 JSON 是 Entities，第二个是 Relations
    entities_json_dict = json.loads(json_strs[0])
    relations_json_dict = json.loads(json_strs[1])

    # 合并 Entities 和 Relations 成 KG
    kg_json_dict = {**entities_json_dict, **relations_json_dict, "has_been_merged": False}

    # 生成文件名
    base_name = os.path.splitext(os.path.basename(json_path))[0].replace("cleaned", "")
    entities_output_name = f"{base_name}entities.json"
    relations_output_name = f"{base_name}relations.json"
    kg_output_name = f"{base_name}kg.json"

    # 保存输出 JSON 文件
    save_to_json(entities_json_dict, ENTITIES_DIR, entities_output_name)
    save_to_json(relations_json_dict, RELATIONS_DIR, relations_output_name)
    save_to_json(kg_json_dict, KG_DIR, kg_output_name)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Extraction")
    parser.add_argument("--txt_path", help="Input TXT file path", default=None)
    parser.add_argument("--json_path", help="Input JSON file name", default=None)
    args = parser.parse_args()

    extract_knowledge(args.txt_path, args.json_path)
