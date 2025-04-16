import json
import os

from call_deepseek_api import call_deepseek_api
from extract_json_objects import extract_json_objects
from load_prompt import load_prompts
from save_to_json import save_to_json

# 提示词存放路径
SYSTEM_PROMPT_PATH = "Prompt/fuse_knowledge/system.txt"
USER_PROMPT_PATH = "Prompt/fuse_knowledge/user.txt"

FUSED_KG_DIR = "4_fuse_knowledge"
FUSED_KG_PATH = "4_fuse_knowledge/KG_fused.json"  # 融合后的 KG 存放路径
KGs_DIR = "3_extract_knowledge/KGs"  # 融合前 KGs 存放的文件夹

MAX_FILES = 5  # 每次融合 KG 数量的最大值


def select_KGs(kg_dir, max_files=10):
    """
    从指定目录中筛选 "has_been_merged" 为 False 的 JSON 文件, 最多返回 max_files 个。
    :param kg_dir: 未被融合的 KGs 文件所在目录
    :param max_files: 最多返回文件数量
    :return: selected_KGs_path 被选中的 KGs 文件路径名列表
    """
    selected_KGs_path = []  # 保存 KGs 文件路径的列表

    all_files = os.listdir(kg_dir)  # 获取指定目录下的所有文件名

    # 遍历所有文件
    for filename in all_files:
        filepath = os.path.join(kg_dir, filename)  # 拼接文件路径
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data.get("has_been_merged", False):  # 选择未被融合的 KGs 文件
            selected_KGs_path.append(filepath)  # 将文件路径添加到列表中
            if len(selected_KGs_path) >= max_files:  # 获取到足够数量的文件后退出
                break

    return selected_KGs_path

def update_selected_KGs(selected_KGs_path):
    """
    将选中的 KG 文件更新其 "has_been_merged" 字段为 True
    :param selected_KGs_path: 要更新的 KGs 文件路径列表
    """
    for kg_path in selected_KGs_path:
        with open(kg_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # 读入 JSON 文件
        data["has_been_merged"] = True  # 更新 "has_been_merged" 字段为 True
        with open(kg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)  # 重新写入 JSON 文件

def construct_intput_message(selected_KGs_path, entity_type):
    """
    抽取存放在 JSON 文件中的实体, 构造 input_message
    :param selected_KGs_path: 存放要融合的 KGs 对应的 JSON 文件路径列表
    :param entity_type: 要融合的实体类型
    :return: 构造出的 input_message
    """
    # 初始化 Integrated Entities 和 Non-integrated Entities 的列表
    integrated_entities = []
    non_integrated_entities = []

    # 抽取 Integrated Entities: 从 "4_fuse_knowledge/KG_fused.json" 中读取
    fused_file = os.path.join("4_fuse_knowledge", "KG_fused.json")
    if os.path.exists(fused_file):
        with open(fused_file, 'r', encoding='utf-8') as f:
            try:
                fused_data = json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Warning: {fused_file} is empty or contains invalid JSON. Using empty data.")
                fused_data = {}
        # 从 fused_data 中提取 entities 列表，若不存在则为空列表
        entities = fused_data.get("entities", [])
        # 筛选出 type 为 entity_type 的实体
        integrated_entities = [entity for entity in entities if entity.get("type") == entity_type]
    else:
        print(f"Warning: The file {fused_file} does not exist!")

    # 抽取 Non-integrated Entities: 遍历 selected_KGs_path 中的每个文件
    for json_path in selected_KGs_path:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    print(f"Warning: {json_path} is empty or contains invalid JSON. Skipping this file.")
                    continue
            # 从当前文件中提取 entities 列表
            entities = data.get("entities", [])
            # 筛选出 type 为 entity_type 的实体
            filtered = [entity for entity in entities if entity.get("type") == entity_type]
            non_integrated_entities.extend(filtered)
        else:
            print(f"Warning: The file {json_path} does not exist!")

    # 构造 input_message 格式
    input_message = {
        "Integrated Entities": {
            "entities": integrated_entities
        },
        "Non-integrated Entities": {
            "entities": non_integrated_entities
        }
    }

    return input_message

def fuse_knowledge(fused_KG_path, KGs_dir):
    """
    调用 DeepSeek API 执行知识融合过程
    :param fused_KG_path: KG_fused.json 的路径
    :param KGs_dir: 存放未被融合的 KGs 文件的目录
    """
    # 读取系统和用户提示词
    system_prompt, user_prompt = load_prompts(SYSTEM_PROMPT_PATH, USER_PROMPT_PATH)

    # 获取要融合的 KGs 的路径
    selected_KGs_path = select_KGs(KGs_dir)

    if os.path.exists(fused_KG_path):
        with open(fused_KG_path, 'r', encoding='utf-8') as f:
            try:
                original_data = json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Warning: {fused_KG_path} is empty or contains invalid JSON. Initializing empty fused KG.")
                original_data = {"entities": [], "relations": []}
    else:
        print(f"Warning: The file {fused_KG_path} does not exist! Initializing empty fused KG.")
        original_data = {"entities": [], "relations": []}

    # 初始化从 selected_KGs_path 中抽取的实体和关系列表
    aggregated_entities = []
    aggregated_relations = []

    # 遍历 selected_KGs_path 中的每个文件, 抽取 "entities" 和 "relations"
    for json_path in selected_KGs_path:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            entities = data.get("entities", [])
            relations = data.get("relations", [])
            aggregated_entities.extend(entities)
            aggregated_relations.extend(relations)
        else:
            print(f"Warning: The file {json_path} does not exist!")

    # 定义需要融合的实体类型列表
    entity_types = ["Paper", "Task", "Dataset", "Repository"]
    fused_relations = []  # 用于存放大模型返回的关系

    # 对每种实体依次进行知识融合, 提取大模型返回的 "relations"
    for entity_type in entity_types:
        print(f"Fusing knowledge for entity type: {entity_type}")

        # 构造 input_message
        input_message = construct_intput_message(selected_KGs_path, entity_type)
        # 将 input_message 转换为 JSON 字符串
        input_message_str = json.dumps(input_message)
        print(input_message_str)

        # 调用 DeepSeek API 进行知识融合
        fuse_result = call_deepseek_api(system_prompt, user_prompt, input_message_str)
        print("DeepSeek API Response:")
        print(fuse_result)

        # 提取返回内容中的 JSON 对象, 并获取其中的 "relations"
        json_strs = extract_json_objects(fuse_result)
        if json_strs:
            try:
                api_response = json.loads(json_strs[0])
                # 如果返回内容中包含 "relations", 则添加到 fused_relations
                relations_from_api = api_response.get("relations", [])
                fused_relations.extend(relations_from_api)
            except json.JSONDecodeError:
                print("Warning: Failed to decode JSON from API response.")
        else:
            print("Warning: No JSON object extracted from API response.")

    # 合并各部分数据: 原始数据, 选中文件中的数据, 大模型返回的关系
    updated_entities = original_data.get("entities", []) + aggregated_entities
    updated_relations = original_data.get("relations", []) + aggregated_relations + fused_relations

    # 构造最终更新的 KG 数据
    updated_KG = {
        "entities": updated_entities,
        "relations": updated_relations
    }

    # 保存更新后的 KG_fused.json
    save_to_json(updated_KG, FUSED_KG_DIR, "KG_fused.json")

    # 更新选中的文件状态
    update_selected_KGs(selected_KGs_path)

def check_and_fuse_knowledge(fused_KG_path, KGs_dir):
    """
    检测 KGs_dir 文件夹下是否有 'has_been_merged' 为 False 的 JSON 文件, 如果存在，则调用 fuse_knowledge 函数
    :param fused_KG_path: KG_fused.json 的路径
    :param KGs_dir: 存放未被融合的 KGs 文件的目录
    """
    should_fuse = False  # 标记是否需要调用 fuse_knowledge

    if not os.path.exists(KGs_dir):
        print(f"Warning: Directory '{KGs_dir}' does not exist!")
        return

    # 遍历目录中的所有文件
    for filename in os.listdir(KGs_dir):
        filepath = os.path.join(KGs_dir, filename)

        # 确保文件是 JSON 文件
        if os.path.isfile(filepath) and filename.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 检查 "has_been_merged" 是否为 False
                if not data.get("has_been_merged", True):
                    print(f"Warning: Directory '{KGs_dir}' does not exist!")
                    should_fuse = True
                    break  # 找到至少一个未融合的文件就可以停止检查

            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Directory '{KGs_dir}' does not exist!")

    if should_fuse:
        print("Calling fuse_knowledge function...")
        fuse_knowledge(fused_KG_path, KGs_dir)
    else:
        print("No unmerged files detected, fusion operation is not required.")

if __name__ == "__main__":
    import argparse

    check_and_fuse_knowledge(FUSED_KG_PATH, KGs_DIR)
