import os
import time
import socket
import subprocess
from dotenv import load_dotenv
from neo4j import GraphDatabase

# **加载 .env 文件**
load_dotenv()

# **从 .env 读取 Neo4j 安装路径**
# 读取 Neo4j 配置
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_HOME = os.getenv("NEO4J_HOME")

def is_neo4j_running(host="localhost", port=7687):
    """ 检查 Neo4j 是否在运行 """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def start_neo4j():
    """ 如果 Neo4j 未运行，则启动 """
    if is_neo4j_running():
        print("Neo4j is already running.")
        return

    print("Starting Neo4j...")

    try:
        # **Windows 环境下使用 subprocess 启动 Neo4j**
        subprocess.Popen(
            [f"{NEO4J_HOME}\\bin\\neo4j.bat", "start"],  # Windows 使用 .bat 文件启动
            creationflags=subprocess.CREATE_NEW_CONSOLE,  # 以新窗口运行
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # **等待最多 30 秒，检查是否启动**
        for _ in range(30):
            if is_neo4j_running():
                print("Neo4j started successfully!")
                return
            time.sleep(1)

        print("Failed to start Neo4j within timeout.")
    except Exception as e:
        print(f"Error starting Neo4j: {e}")


# **自动检测并启动 Neo4j**
start_neo4j()

# **Neo4j 连接类**
class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_relationship(self, head, head_type, relation, tail, tail_type):
        query = (
            f"MERGE (h:{head_type} {{name: $head}}) "
            f"MERGE (t:{tail_type} {{name: $tail}}) "
            f"MERGE (h)-[:{relation.upper()}]->(t)"
        )
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(query, head=head, tail=tail))

    def load_json_and_create_graph(self, json_file):
        import json
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            self.create_relationship(
                entry["head"], entry["head_type"],
                entry["relation"], entry["tail"], entry["tail_type"]
            )
        print("Knowledge graph has been successfully imported into Neo4j!")

# **运行程序**
if __name__ == "__main__":
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    kg.load_json_and_create_graph("extracted_relations.json")  # 替换为你的 JSON 文件路径
    kg.close()