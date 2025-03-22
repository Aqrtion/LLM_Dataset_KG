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
    :return: (selected_KGs_path, selected_KGs) 被选中的 KGs 文件路径名列表和文件列表
    """
    selected_KGs_path = []  # 保存 KGs 文件路径的列表
    selected_KGs = []  # 保存 KGs 文件的列表

    all_files = os.listdir(kg_dir)  # 获取指定目录下的所有文件名

    # 遍历所有文件
    for filename in all_files:
        filepath = os.path.join(kg_dir, filename)  # 拼接文件路径
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data.get("has_been_merged", False):  # 选择未被融合的 KGs 文件
            # 再次读取未被融合的 KGs 文件 (以文本格式)
            with open(filepath, "r", encoding="utf-8") as f:
                file_text = f.read()
            selected_KGs_path.append(filepath)   # 将文件名添加到列表中
            selected_KGs.append(file_text)  # 将文件内容文本添加到列表中
            if len(selected_KGs_path) >= MAX_FILES:  # 获取到足够数量的文件后退出
                break

    return selected_KGs_path, selected_KGs

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

def fuse_knowledge(fused_KG_path, KGs_dir):
    """
    调用 DeepSeek API 执行知识融合过程
    :param fused_KG_path: KG_fused.json 的路径
    :param KGs_dir: 存放未被融合的 KGs 文件的目录
    """
    # 读取 fused_KG
    with open(fused_KG_path, 'r', encoding='utf-8') as f:
        fused_KG = f.read()

    # 获取要融合的 KGs 的路径和文本字符串
    selected_KGs_path, selected_KGs = select_KGs(KGs_dir)

    # 构造 input_message
    input_message = fused_KG + "\n" + "\n".join(selected_KGs)

    # 读取系统和用户提示词
    system_prompt, user_prompt = load_prompts(SYSTEM_PROMPT_PATH, USER_PROMPT_PATH)

    # 调用 DeepSeek API 进行知识融合
    fuse_result = call_deepseek_api(system_prompt, user_prompt, input_message)
    print("DeepSeek API Response:")
    print(fuse_result)

    # 提取返回内容中的 JSON 对象
    json_strs = extract_json_objects(fuse_result)
    fused_KG_update = json.loads(json_strs[0])

    # 用 fused_KG_update 更新 KG_fused.json
    save_to_json(fused_KG_update, FUSED_KG_DIR, "KG_fused.json")

    # 更新选中的文件状态
    update_selected_KGs(selected_KGs_path)

if __name__ == "__main__":
    import argparse

    fuse_knowledge(FUSED_KG_PATH, KGs_DIR)
