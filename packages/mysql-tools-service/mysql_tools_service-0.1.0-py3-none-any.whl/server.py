import pandas as pd
import pymysql
from mcp.server.fastmcp import FastMCP
from pymysql import MySQLError
from typing import Dict, List, Any
import os

app = FastMCP("MySQL & Excel Tools")


# 数据库连接配置（需替换为实际值）
DB_CONFIG = {
    "host": os.getenv("mysql_host", ""),
    "port": int(os.getenv("mysql_port", "")),
    "user": os.getenv("mysql_user", ""),
    "password": os.getenv("mysql_password", ""),
    "database": os.getenv("mysql_database", "")
}

print(DB_CONFIG)

def get_db_connection():
    """创建 MySQL 连接"""
    return pymysql.connect(**DB_CONFIG)

get_db_connection()

@app.tool(name="mysql_insert")
def mysql_insert(table_name: str, data: Dict[str, Any]) -> str:
    """
    向 MySQL 表插入一条数据
    :param table_name: 目标表名
    :param data: 数据字典（键为列名，值为数据）
    :return: 操作结果消息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(data.values()))
        conn.commit()
        return f"插入成功，影响行数: {cursor.rowcount}"
    except MySQLError as e:
        return f"数据库错误: {e}"
    finally:
        cursor.close()
        conn.close()

@app.tool(name="mysql_delete_table")
def mysql_delete_table(table_name: str) -> str:
    """
    删除 MySQL 数据表（慎用！）
    :param table_name: 目标表名
    :return: 操作结果消息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"DROP TABLE IF EXISTS {table_name}"
        cursor.execute(sql)
        conn.commit()
        return f"表 {table_name} 已删除"
    except MySQLError as e:
        return f"数据库错误: {e}"
    finally:
        cursor.close()
        conn.close()

@app.tool(name="execute_sql")
def execute_sql(sql: str) -> List[Dict[str, Any]]:
    """
    执行 SQL 查询语句
    :param sql: SQL 语句
    :return: 查询结果（字典列表）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except MySQLError as e:
        return [{"error": f"数据库错误: {e}"}]
    finally:
        cursor.close()
        conn.close()

@app.tool(name="excel_to_json")
def excel_to_json(file_path: str) -> List[Dict[str, Any]]:
    """
    将 Excel 文件转换为 JSON 格式（List[Dict]）
    :param file_path: Excel 文件路径
    :return: JSON 格式数据
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df.to_dict(orient='records')
    except Exception as e:
        return [{"error": f"文件处理失败: {e}"}]

if __name__ == "__main__":
    app.run(transport="stdio")