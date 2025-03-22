import json

# 读取 JSON 文件
with open("Papers_Usage/papers_usage.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 修改 is_used 为 False
for paper in data["papers"]:
    paper["is_used"] = False

# 写回 JSON 文件
with open("Papers_Usage/papers_usage.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print("所有 'is_used' 值已修改为 False 并保存成功！")
