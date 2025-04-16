import json
import os

KGs_dir = "3_extract_knowledge/KGs"
FUSED_KG_DIR = "4_fuse_knowledge"

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

    # 从 "4_fuse_knowledge/KG_fused.json" 中抽取 Integrated Entities
    fused_file = os.path.join(FUSED_KG_DIR, "KG_fused.json")
    if os.path.exists(fused_file):
        with open(fused_file, 'r', encoding='utf-8') as f:
            fused_data = json.load(f)
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
                data = json.load(f)
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


if __name__ == '__main__':
    # 设置 JSON 文件路径和目标实体类型
    json_path = select_KGs(KGs_dir)
    # print(json_path)
    target_type = "Dataset"  # 可根据需要修改

    # 获取符合条件的实体
    entities = construct_intput_message(json_path, target_type)

    # 输出结果
    print(entities)
