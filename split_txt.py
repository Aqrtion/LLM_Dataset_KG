import json
import os

JSON_SPLIT_DIR = "1_split_txt"


def extract_key_information(text):
    """
    提取标题、作者、摘要、引言部分
    :param text: 输入文本内容
    :return: 一个元组 (提取的关键信息字符串, 剩余的段落列表)
    """
    print("Extracting key information...")

    paragraphs = text.split('\n')  # 按换行符分割文本为段落
    key_information = []  # 保存提取结果（完整段落）
    total_char_count = 0  # 非空字符累计数
    max_chars = 30000  # 非空字符上限
    found_introduction = False  # 标记是否找到 "introduction"

    for index, paragraph in enumerate(paragraphs):
        # 忽略大小写检测 "introduction"
        if 'introduction' in paragraph.lower():
            found_introduction = True

        # 在找到 "Introduction" 后，如果遇到以 "2" 开头的段落则停止提取
        if found_introduction and paragraph.strip().startswith('2'):
            break

        # 去除首尾空白
        paragraph_clean = paragraph.strip()
        # 如果段落为空则跳过
        if not paragraph_clean:
            continue

        # 计算当前段落的非空字符数（移除所有空白字符）
        non_space_count = len(''.join(paragraph_clean.split()))

        # 如果加上当前段落不会超过上限，则加入
        if total_char_count + non_space_count <= max_chars:
            key_information.append(paragraph)
            total_char_count += non_space_count
        else:
            break

    extracted_text = '\n'.join(key_information)
    remaining_paragraphs = paragraphs[index:] if index < len(paragraphs) else []
    print("Extraction completed.")
    return extracted_text, remaining_paragraphs

def extract_dataset_related_paragraphs(paragraphs, full_name=None, abbreviation=None):
    """
    从段落列表中提取包含字符串 "data" (忽略大小写), full_name 和 abbreviation 的段落
    :param paragraphs: 段落列表
    :param full_name: 数据集全名 (默认 None)
    :param abbreviation: 数据集名缩写 (默认 None)
    :return: 包含 "data" 的段落列表
    """
    print("Extracting data-related paragraphs...")

    data_related_paragraphs = []
    for paragraph in paragraphs:
        contains_data = 'data' in paragraph.lower()
        contains_full_name = full_name is not None and full_name in paragraph
        contains_abbr = abbreviation is not None and abbreviation in paragraph

        if contains_data or contains_full_name or contains_abbr:
            data_related_paragraphs.append(paragraph)

    print(f"Extracted {len(data_related_paragraphs)} data-related paragraphs.")

    return data_related_paragraphs


def read_txt_file(txt_path):
    """
    读取 TXT 文件
    :param txt_path: TXT 文件路径
    :return: 文件内容字符串
    """
    print(f"Reading text from file: {txt_path}")

    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    print("File read successfully.")
    return content


def save_to_json(key_information, data_related_paragraphs, json_output_name):
    """
    将提取的内容保存为 JSON 文件
    :param key_information: 提取的标题, 作者, 摘要, 引言
    :param data_related_paragraphs: 包含字符串 "data" 的段落的列表
    :param json_output_name: 输出 JSON 文件名
    :return: None
    """
    json_path = os.path.join(JSON_SPLIT_DIR, json_output_name)  # 拼接完整存储路径
    os.makedirs(JSON_SPLIT_DIR, exist_ok=True)  # 确保输出目录存在

    print(f"Saving extracted content to JSON: {json_path}")

    # 拼接输出
    output = {
        "title_author_abstract_introduction": key_information,
        "data_related_paragraphs": data_related_paragraphs,
    }

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

    print("JSON file saved successfully.")

    return json_path

def split_txt(txt_path, json_output_name=None):
    """
    处理文本文件：提取标题, 摘要, 引言部分及包含字符串 "data" 的段落, 将提取内容保存为 JSON 文件
    :param txt_path: 待处理的 TXT 文件路径
    :param json_output_name: 输出 JSON 文件名
    :return: None
    """
    print(f"Starting split txt file.")

    text = read_txt_file(txt_path)  # 读入 TXT 文件
    key_information, remaining_paragraphs = extract_key_information(text)  # 提取标题, 作者, 摘要, 引言
    data_related_paragraphs = extract_dataset_related_paragraphs(remaining_paragraphs)  # 提取包含字符串 "data" 的段落

    base_name = os.path.splitext(os.path.basename(txt_path))[0]  # 解析文件名
    # 将文件名中的 "cleaned" 替换为 "split"
    base_name = base_name.replace("cleaned", "split")

    # 生成默认输出文件名
    if json_output_name is None:
        json_output_name = f"{base_name}.json"

    # 保存输出文件
    json_path = save_to_json(key_information, data_related_paragraphs, json_output_name)  # 将提取内容保存为 JSON 文件

    print(f"Finished split txt file.")

    return json_path

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="TXT File Splitter")
    parser.add_argument("--txt_path", help="Input TXT file path", default=None)
    parser.add_argument("--json", help="Output JSON file name", default=None)

    args = parser.parse_args()

    split_txt(args.txt_path, args.json)
