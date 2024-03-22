import os
import json
import shutil


def move_pdf_files(jsonl_path, pdf_folder_path, new_folder_name):
    # 创建新文件夹
    if not os.path.exists(new_folder_name):
        os.makedirs(new_folder_name)

    # 读取 JSONL 文件
    with open(jsonl_path, "r", encoding="utf-8") as jsonl_file:
        for line in jsonl_file:
            # 解析 JSON 行
            json_data = json.loads(line)
            pdf_name = json_data.get("pdf_name", None)

            # 如果存在 pdf_name 参数
            if pdf_name:
                # 构建 PDF 文件路径
                pdf_path = os.path.join(pdf_folder_path, pdf_name)
                # 检查文件是否存在
                if os.path.exists(pdf_path + ".pdf"):
                    # 移动文件到新文件夹
                    shutil.move(pdf_path + ".pdf", new_folder_name)
                    print(f"Moved {pdf_name} to {new_folder_name}")
                else:
                    print(f"File {pdf_name} not found in PDF folder.")
            else:
                print("pdf_name parameter not found in JSON record.")


jsonl_path = (
    "C:\\Users\\hayu\\appen\\scrapy_items\\pubmed\\pubmed\\1123.jsonl"  # JSONL 文件路径
)
pdf_folder_path = (
    "C:\\Users\\hayu\\appen\\scrapy_items\\pubmed\\pubmed\\pdf"  # PDF 文件夹路径
)
new_folder_name = (
    "C:\\Users\\hayu\\appen\\scrapy_items\\pubmed\\pubmed\\new_pdf"  # 新文件夹名称
)

# 调用函数进行文件移动
move_pdf_files(jsonl_path, pdf_folder_path, new_folder_name)
