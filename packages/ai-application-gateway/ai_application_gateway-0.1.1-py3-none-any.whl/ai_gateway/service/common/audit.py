"""
变更日志
"""

import pymysql
import json
from loguru import logger
from datetime import datetime
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.common_pymysql_tool import get_pool
from fastapi import HTTPException
from ai_gateway.schemas.api.base import RspBase
from ai_gateway.schemas.api.common.audit import Audit

# 插入变更日志数据
async def insert_audit(
        audit: Audit,
) -> RspBase:
    try:
        connection_pool = get_pool(audit.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        
        with connection.cursor() as cursor:
            insert_sql = """
            INSERT INTO audits (
                user_id,
                auditable_id,
                auditable_type,
                changes,
                change_type
            ) VALUES ( %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                audit.user_id,
                audit.auditable_id,
                audit.auditable_type,
                json.dumps(audit.changes) if audit.changes else None,
                audit.change_type.value
            ))
            
            connection.commit()
            logger.info(f"添加变更日志成功，用户ID: {audit.user_id}")
            return RspBase(content="添加变更日志成功")
            
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"添加变更日志失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()

# 批量插入变更日志数据
async def insert_audit_many(
        business_type: str,
        audit_params: list[tuple],
) -> RspBase:
    """
    批量插入变更日志
    :param audit_params: 参数列表，每个元素为元组(user_id, auditable_id, auditable_type, changes, change_type)
    """
    if not audit_params:
        return RspBase(content="无变更日志需要添加")
        
    try:
        connection_pool = get_pool(business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        
        with connection.cursor() as cursor:
            insert_sql = """
            INSERT INTO audits (
                user_id,
                auditable_id,
                auditable_type,
                changes,
                change_type
            ) VALUES (%s, %s, %s, %s, %s)
            """
            start_time = datetime.now()
            cursor.executemany(insert_sql, audit_params)
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"批量插入变更日志 SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"批量插入变更日志 SQL: {insert_sql}")
            logger.info(sql_execution_time)
            
            connection.commit()
            logger.info(f"批量添加变更日志成功，共{len(audit_params)}条记录")
            return RspBase(content=f"批量添加变更日志成功，共{len(audit_params)}条记录")
            
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"批量添加变更日志失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()