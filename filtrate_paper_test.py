import os
import json
from parse_pdf import parse_pdf
from split_txt import split_txt
from filtrate_paper import filtrate_paper
from extract_knowledge import extract_knowledge

PAPERS_DIR_1 = "Papers"  # 大模型相关, 有数据集
PAPERS_DIR_2 = "LLMs_Related_Papers" # 大模型相关, 无数据集
PAPERS_DIR_3 = "LLMs_No_Related_Papers" # 大模型无关, 无数据集

def main():
    """
    主函数：
    1. 载入 JSON 文件
    2. 遍历 JSON 文件中 "papers" 列表
    3. 对于每个 "is_used" 为 False 的对象，依次调用：
       - parse_pdf：将 PDF 文件转换为 TXT 文件
       - split_txt：对 TXT 文件进行分割处理，返回 JSON 文件路径
       - filtrate_paper：对上一步返回的 JSON 文件进行过滤处理
       - extract_knowledge：根据 TXT 文件和过滤后的 JSON 文件提取知识
    4. 每处理完一个 PDF 文件后，立即将其 "is_used" 标记为 True，并保存 JSON 文件
    """
    data = load_json()
    papers = data.get("papers", [])

    for paper in papers:
        # 只处理 is_used 为 False 的 PDF 文件
        if not paper.get("is_used", False):
            pdf_filename = paper.get("file_name")
            pdf_path = os.path.join(PDF_DIR, pdf_filename)
            print(f"Processing file: {pdf_filename}...")

            try:
                # 第一步：调用 parse_pdf，将 PDF 转换为 TXT 文件
                txt_path = parse_pdf(pdf_path)
                print(f"parse_pdf output: {txt_path}")

                # 第二步：调用 split_txt，对 TXT 文件进行分割处理，返回 JSON 文件路径
                split_json_path = split_txt(txt_path)
                print(f"split_txt output: {split_json_path}")

                # 第三步：调用 filtrate_paper，对上一步返回的 JSON 文件进行过滤处理
                filtrated_json_path = filtrate_paper(split_json_path)
                print(f"filtrate_paper output: {filtrated_json_path}")

                # 第四步：调用 extract_knowledge，根据 TXT 文件和过滤后的 JSON 文件提取知识
                extract_knowledge(txt_path, filtrated_json_path)
                print(f"extract_knowledge completed for {pdf_filename}")

                # 标记该 PDF 文件已处理, 并立即保存 JSON 进度
                paper["is_used"] = True
                save_json(data)
                print(f"Updated {pdf_filename} as processed.")

            except Exception as e:
                print(f"Error processing {pdf_filename}: {e}")

    print("All unprocessed papers have been processed.")


if __name__ == "__main__":
    main()
