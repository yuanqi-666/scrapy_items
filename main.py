import json

# 读取JSONL文件，提取content字段，并保存到txt文件
def clean_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            content = data.get('content', '')  # 获取content字段，如果字段不存在，则返回空字符串
            # 写入到txt文件中，每个content字段一行
            outfile.write(content + '\n')

# 输入文件名和输出文件名
input_file = 'novelup.jsonl'
output_file = 'output.txt'

# 执行清洗操作
clean_jsonl(input_file, output_file)
