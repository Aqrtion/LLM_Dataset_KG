import json
import os
import re

from dotenv import load_dotenv
from neo4j import GraphDatabase

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中读取 Neo4j 的连接信息
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# 创建 Neo4j 驱动，建立与数据库的连接
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def safe_label(label_str):
    """
    将传入的字符串转换为合法的 Neo4j 标签:
      - 移除非字母数字字符 (用下划线替代)
      - 标签需以字母开头, 如果不是则加上前缀
    :param label_str: 要进行处理的 Neo4j 标签字符串
    :return: 合法的 Neo4j 标签
    """
    # 将非字母数字字符替换为下划线
    safe = re.sub(r'\W+', '_', label_str)
    # 如果标签不是以字母开头, 则添加前缀
    if not safe[0].isalpha():
        safe = "L_" + safe
    return safe


def create_entity(tx, entity):
    """
    根据传入的实体信息, 在 Neo4j 中创建或合并节点, 并设置节点的属性, 同时根据实体类型添加标签
    :param tx: Neo4j 的事务对象, 用于执行数据库操作
    :param entity: 字典, 包含实体的详细信息, 如 id, name, type 和 attributes
    :return: None
    """
    # 构造基础属性字典 (固定属性)
    properties = {
        "id": entity["id"],
        "name": entity["name"],
        "type": entity["type"]
    }
    # 如果存在额外的 attributes, 则展开添加
    attributes = entity.get("attributes", {})
    for key, value in attributes.items():
        properties[key] = value

    # 构造新的字典 safe_properties 用于存放转换后的参数, 避免参数名中包含非法字符
    safe_properties = {}
    set_clauses = []
    for key, value in properties.items():
        # 使用正则表达式将所有非字母数字和下划线的字符转换为下划线
        safe_key = re.sub(r'\W+', '_', key)
        safe_properties[safe_key] = value
        # 构造 SET 子句时, 节点属性名仍然保持原始格式, 用反引号包裹
        set_clauses.append(f"n.`{key}` = ${safe_key}")

    # 根据实体类型添加标签, 确保标签合法
    entity_label = safe_label(entity["type"])

    # 构造完整的 Cypher 查询语句, 动态添加标签
    # MERGE (n:Label {id: $id}) 能确保同一 id 的节点只创建一次且带有对应的标签
    query = f"MERGE (n:{entity_label} {{id: $id}}) SET " + ", ".join(set_clauses)
    tx.run(query, **safe_properties)


def create_relation(tx, relation):
    """
    根据传入的关系信息, 在 Neo4j 中创建节点间的关系
    :param tx: Neo4j 的事务对象, 用于执行数据库操作
    :param relation: 字典, 包含关系的详细信息
    :return: None
    """
    # 转换关系类型，确保符合 Neo4j 命名规范
    rel_type = relation["relation"].upper().replace(" ", "_")
    query = f"""
    MATCH (a {{id: $head_id}}), (b {{id: $tail_id}})
    MERGE (a)-[r:{rel_type}]->(b)
    RETURN type(r) AS relType
    """
    tx.run(query, head_id=relation["head_id"], tail_id=relation["tail_id"])


def import_graph(json_path):
    """
    从指定的 JSON 文件中读取知识图谱数据, 并将实体节点与关系导入到 Neo4j 数据库中
    :param json_path: 保存知识图谱数据的 JSON 文件的路径
    :return: None
    """
    # 打开并读取 JSON 文件，加载知识图谱数据
    with open(json_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    # print(graph_data)

    # 使用 Neo4j 驱动建立 session, 进行写入操作
    with driver.session() as session:
        # 导入实体节点
        for entity in graph_data.get("entities", []):
            session.execute_write(create_entity, entity)
        # 导入关系数据
        for relation in graph_data.get("relations", []):
            session.execute_write(create_relation, relation)


if __name__ == "__main__":
    try:
        # 调用导入函数, 将指定 JSON 文件中的数据导入到 Neo4j 中
        import_graph("4_fuse_knowledge/KG_fused.json")
        print("The knowledge graph data has been successfully imported into Neo4j!")
    finally:
        # 关闭 Neo4j 驱动连接
        driver.close()
