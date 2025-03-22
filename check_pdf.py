import os
import json

PDF_DIR = "Papers"
JSON_PATH = "Papers_Usage/papers_usage.json"

def load_json():
    """
    载入 Papers_Usage JSON 文件
    :return: papers_usage.json 文件数据
    """
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)  # 读取 JSON 文件
            except json.JSONDecodeError:
                print(f"Warning: {JSON_PATH} is corrupted. Reinitializing!")
                data = {"papers": []}
        # 保证 JSON 有 "papers" 键
        if "papers" not in data:
            data["papers"] = []
    else:
        data = {"papers": []}
    return data

def pdf_file_exists(data, pdf_filename):
    """
    判断 JSON 数据中是否存在给定的 pdf 文件名
    :param data: papers_usage.json 文件数据
    :param pdf_filename: 要检查的 pdf 文件名
    :return: True/False
    """
    for entry in data.get("papers", []):
        if entry.get("file_name") == pdf_filename:
            return True
    return False

def check_pdf():
    """
    检查 PDF 是否已经被解析过，为未被解析过的 PDF 添加使用信息
    :return: None
    """
    data = load_json()

    # 获取目标目录下的 pdf 文件名列表
    try:
        files = os.listdir(PDF_DIR)
    except Exception as e:
        print(f"Unable to access directory {PDF_DIR}: {e}")
        return

    pdf_files = [f for f in files if f.lower().endswith('.pdf')]

    added_count = 0  # 计数未处理过的 pdf 文件
    for pdf in pdf_files:
        file_name = pdf
        if not pdf_file_exists(data, file_name):  # 检查 pdf 文件是否存在
            data["papers"].append({
                "file_name": file_name,
                "is_used": False
            })
            added_count += 1

    # 更新 papers_usage.json
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Processed {len(pdf_files)} PDF files, added {added_count} new records.")

if __name__ == "__main__":
    check_pdf()
