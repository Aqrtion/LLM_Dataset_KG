import re
import os
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

# 设置输出文件存储目录
TXT_DIR = "0_parse_pdf/txt"
TXT_CLEANED_DIR = "0_parse_pdf/txt_cleaned"

def extract_paragraphs(pdf_path):
    """
    从 pdf 文件中提取段落文本
    :param pdf_path: 要解析的 pdf 文件的路径
    :return: 提取出的段落文本的列表
    """
    print(f"Starting to extract paragraphs from PDF.")

    la_params = LAParams(line_margin=0.5, word_margin=0.2, char_margin=2.0)  # 设置 PDF 解析参数
    text = extract_text(pdf_path, laparams=la_params)  # 提取 pdf 文本

    raws = text.split("\n")  # 按换行符拆分文本

    paragraphs = []  # 存储被提取出的段落
    current_paragraph = ""  # 暂存当前段落内容

    # 遍历所有行, 组合属于同一段落的行
    for raw in raws:
        raw = raw.strip()  # 去除首尾空格
        if raw:  # 非空行拼接成段落
            if re.match(r".*[a-zA-Z]-$", current_paragraph):
                current_paragraph = current_paragraph[:-1] + raw  # 当前段落以连字符结尾的换行, 拼接被分割的单词
            else:
                if current_paragraph:  # 当前段落非空
                    current_paragraph = current_paragraph + " " + raw  # 添加空格后拼接新行
                else:  # 当前段落为空
                    current_paragraph = current_paragraph + raw  # 不加空格
        else:  # 空行表示当前段落结束
            if current_paragraph:  # 当前段落非空, 存入列表
                paragraphs.append(current_paragraph)
                current_paragraph = ""  # 重置当前段落

    # 处理最后一个段落
    if current_paragraph:
        paragraphs.append(current_paragraph)

    print(f"Paragraphs extraction completed. {len(paragraphs)} paragraphs extracted.")
    return paragraphs

def save_paragraphs_to_txt(paragraphs, output_dir, output_name):
    """
    将提取出的段落文本保存为 TXT 文件
    :param paragraphs: 段落文本列表
    :param output_dir: 输出 TXT 文件所在目录
    :param output_name: 输出 TXT 文件名
    :return: None
    """
    output_path = os.path.join(output_dir, output_name)  # 拼接完整存储路径
    os.makedirs(output_dir, exist_ok=True)

    print(f"Saving extracted text to TXT file: {output_path}.")
    with open(output_path, "w", encoding="utf-8") as f:
        for para in paragraphs:
            f.write(para + "\n\n")
    print("TXT file saved successfully.")

    return output_path

def clean_txt(txt_path, txt_cleaned_output_name=None):
    """
    清理 TXT 文件, 去除多余的空行和大部分无意义的段落, 并输出清理结果到 0_0_paf_parse/txt_cleaned 目录
    :param txt_path: 待清理的 TXT 文件路径
    :param txt_cleaned_output_name: 清理后的 TXT 文件名
    :return: None
    """
    print(f"Starting to clean txt file: {txt_path}")

    # 读取整个文件内容
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    paragraphs = re.split(r'\n\s*\n', content)  # 根据空行拆分为段落

    processed_paragraphs = []  # 存储处理后的段落

    for paragraph in paragraphs:
        paragraph = paragraph.strip()  # 去除首尾空白
        if not paragraph:
            continue  # 跳过空段落

        non_whitespace_count = sum(1 for c in paragraph if not c.isspace())  # 统计段落中非空白字符的数量
        has_long_continuous_string = bool(re.search(r'\S{2,}', paragraph))  # 检测是否存在连续两个或以上的非空白字符
        contains_letter = bool(re.search(r'[a-zA-Z]', paragraph))  # 检测是否包含至少一个英文字母

        # 若段落内容符合要求，则保留
        if non_whitespace_count > 5 and has_long_continuous_string and contains_letter:
            processed_paragraphs.append(paragraph)

    # print(processed_paragraphs)

    base_name = os.path.splitext(os.path.basename(txt_path))[0]  # 解析 PDF 文件名

    # 生成默认输出文件名
    if txt_cleaned_output_name is None:
        txt_cleaned_output_name = f"{base_name}_cleaned.txt"

    # 保存输出文件
    txt_cleaned_path = save_paragraphs_to_txt(processed_paragraphs, TXT_CLEANED_DIR, txt_cleaned_output_name)

    print("Text cleaning completed successfully.")

    return txt_cleaned_path

def parse_pdf(pdf_path, txt_output_name=None):
    """
    pdf 文件解析函数, 将输入的 pdf 文件解析成 TXT 格式并保存
    :param pdf_path: 要解析的 pdf 文件的路径
    :param txt_output_name: TXT 文件名, 可指定, 如果为 None, 则使用 pdf 文件名替换后缀
    :return: None
    """
    print(f"Starting PDF parsing for: {pdf_path}")

    paragraphs = extract_paragraphs(pdf_path)  # 获取段落文本列表

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]  # 解析 PDF 文件名

    # 生成默认输出文件名
    if txt_output_name is None:
        txt_output_name = f"{base_name}.txt"

    # 保存输出文件
    txt_path = save_paragraphs_to_txt(paragraphs, TXT_DIR, txt_output_name)

    # 进行文件清理
    txt_cleaned_path  = clean_txt(txt_path)

    print("PDF parsing completed successfully.")

    return txt_cleaned_path

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="PDF Parser")
    parser.add_argument("--pdf_path", help="Input PDF file path")
    parser.add_argument("--txt", help="Output TXT file name", default=None)
    parser.add_argument("--txt_clean", help="Cleaned TXT output file name", default=None)
    parser.add_argument("--clean", action="store_true", help="Perform text cleaning on the generated TXT file", default=True)

    args = parser.parse_args()

    # 解析 PDF 并生成 TXT 文件
    txt_cleaned_path = parse_pdf(args.pdf_path, args.txt_clean)
