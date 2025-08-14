from decimal import Decimal

import oracledb as cx_Oracle
from loguru import logger
from typing import List, Dict

from ai_gateway.config import config
from ai_gateway.service.ashare_dividend.dividend_db_tool import dividend_db_connection_pool


def execute_dividend_query_fetchone(sql: str, params=None, connection=None, cursor=None) -> List[Dict]:
    """执行SQL查询并返回结果"""
    try:
        if not connection:
            connection = dividend_db_connection_pool.connect()
            cursor = connection.cursor()

        cursor.execute(sql, params)
        # 获取查询结果的列名列表
        columns = [col[0] for col in cursor.description]
        # 设置行工厂函数，将每行数据与列名组合成字典
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        result = cursor.fetchone()

        return result
    except Exception as e:
        logger.error(f"dividend查询执行错误: {e}")
        raise

# 同样修改execute_dividend_query_fetchall函数
def execute_dividend_query_fetchall(sql: str, params=None, connection=None, cursor=None) -> List[Dict]:
    """执行SQL查询并返回结果"""
    try:
        if not connection:
            connection = dividend_db_connection_pool.connect()
            cursor = connection.cursor()

        cursor.execute(sql, params)
        # 获取查询结果的列名列表
        columns = [col[0] for col in cursor.description]
        # 设置行工厂函数，将每行数据与列名组合成字典
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        results = cursor.fetchall()

        return results
    except Exception as e:
        logger.error(f"dividend查询执行错误: {e}")
        raise