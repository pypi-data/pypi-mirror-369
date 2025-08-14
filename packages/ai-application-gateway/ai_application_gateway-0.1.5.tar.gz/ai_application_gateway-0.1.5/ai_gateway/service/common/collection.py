"""
收藏
"""
import asyncio
from urllib.request import Request
from datetime import datetime

from fastapi import HTTPException
from loguru import logger
import pymysql

from ai_gateway.schemas.api.base import RspBase
from ai_gateway.schemas.api.common.audit import Audit, AuditableType, ChangeType
from ai_gateway.schemas.api.common.collection import Collection
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.audit import insert_audit_many
from ai_gateway.service.common.common_pymysql_tool import get_pool

# 添加收藏
async def insert_collections(
        request: Request,
        collection: Collection,
) -> RspBase:
    try:
        connection_pool = get_pool(collection.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 批量检查是否已存在
            check_sql = """
            SELECT id, collectable_id, is_deleted FROM user_collections 
            WHERE user_id = %(user_id)s 
              AND collectable_id IN %(collectable_ids)s 
              AND collectable_type = %(collectable_type)s
            """
            params = {
                'user_id': collection.user_id,
                'collectable_ids': tuple(collection.collectable_id),
                'collectable_type': collection.collectable_type
            }
            cursor.execute(check_sql, params)
            result = cursor.fetchall()
            # 已经存在的订阅记录collectable_ids
            existing_collectable_ids = [row["collectable_id"] for row in result]
            # 已经存在但已删除的收藏记录主键ID
            existing_deleted_ids = [row["id"] for row in result if row["is_deleted"] == 1]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"获取已存在收藏SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"获取已存在收藏SQL: {check_sql}, 参数: {params}")
            logger.info(sql_execution_time)
            
            # 过滤掉已存在的ID
            new_collectable_ids = [id for id in collection.collectable_id if id not in existing_collectable_ids]
            if not new_collectable_ids and not existing_deleted_ids:
                logger.info("所有收藏已存在")
                return RspBase(content="所有收藏已存在")

            start_time = datetime.now()
            if new_collectable_ids:
                # 批量插入
                insert_sql = """
                INSERT INTO user_collections (
                  `user_id`,
                  `collectable_id`,
                  `collectable_type`
                ) VALUES (%s, %s, %s)
                """

                params = [(collection.user_id, collectable_id, collection.collectable_type) for collectable_id in new_collectable_ids]
                cursor.executemany(insert_sql, params)
                connection.commit()

            if existing_deleted_ids:
                # 批量更新
                update_sql = """
                UPDATE user_collections SET is_deleted = 0, updated_at = %s WHERE id = %s
                """
                cursor.executemany(update_sql, [(datetime.now(), id) for id in existing_deleted_ids])
                connection.commit()

            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"批量添加收藏SQL执行耗时: {elapsed:.6f}秒"
            logger.info(sql_execution_time)

            # start_time = datetime.now()
            # # 插入后查询新增ID
            # select_sql = """
            # SELECT id FROM user_collections
            # WHERE user_id = %s
            # AND collectable_id IN %s
            # AND collectable_type = %s
            # ORDER BY id ASC
            # LIMIT %s
            # """
            # cursor.execute(select_sql, (
            #     collection.user_id,
            #     tuple(new_ids),
            #     collection.collectable_type,
            #     len(new_ids)
            # ))
            # inserted_ids = [row['id'] for row in cursor.fetchall()]
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"插入后查询新增ID SQL执行耗时: {elapsed:.6f}秒"
            # logger.info(f"插入后查询新增ID SQL: {select_sql}")
            # logger.info(sql_execution_time)
            #
            # start_time = datetime.now()
            # # 批量添加审计日志
            # audit_params = [(
            #     collection.user_id,
            #     inserted_id,
            #     AuditableType.USER_COLLECTION,
            #     None,
            #     ChangeType.CREATE
            # ) for inserted_id in inserted_ids]
            #
            # asyncio.create_task(insert_audit_many(collection.business_type, audit_params))
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"批量添加审计日志执行耗时: {elapsed:.6f}秒"
            # logger.info(sql_execution_time)
            
            logger.info(f"批量添加收藏成功，新增{len(new_collectable_ids)}条记录，恢复{len(existing_deleted_ids)}条记录")

            return RspBase(content=f"批量添加收藏成功，新增{len(new_collectable_ids)}条记录，恢复{len(existing_deleted_ids)}条记录")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"批量添加收藏失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()

# 批量移除收藏
async def delete_collections(
        request: Request,
        collection: Collection,
) -> RspBase:
    try:
        connection_pool = get_pool(collection.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 先查询要删除记录的ID
            select_sql = """
            SELECT id FROM user_collections 
            WHERE user_id = %(user_id)s 
              AND collectable_id IN %(collectable_ids)s 
              AND collectable_type = %(collectable_type)s 
              AND is_deleted = 0
            """
            params = {
                'user_id': collection.user_id,
                'collectable_ids': tuple(collection.collectable_id),
                'collectable_type': collection.collectable_type
            }
            cursor.execute(select_sql, params)
            result = cursor.fetchall()
            deleted_ids = [row['id'] for row in result]

            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"查询要删除记录ID SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"查询要删除记录ID SQL: {select_sql}")
            logger.info(sql_execution_time)

            if not deleted_ids:
                logger.info("没有找到要删除的收藏记录")
                return RspBase(content="没有找到要删除的收藏记录")
            
            start_time = datetime.now()
            # 执行假删除操作
            update_sql = """
            UPDATE user_collections SET is_deleted = 1, updated_at = %s 
            WHERE id IN %s
            """
            cursor.executemany(update_sql, [(datetime.now(), tuple(deleted_ids))])
            affected_rows = cursor.rowcount
            connection.commit()
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"删除操作SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"删除操作SQL: {update_sql}")
            logger.info(sql_execution_time)

            # start_time = datetime.now()
            # # 批量添加审计日志
            # audit_params = [(
            #     collection.user_id,
            #     deleted_id,
            #     AuditableType.USER_COLLECTION,
            #     None,
            #     ChangeType.DELETE
            # ) for deleted_id in deleted_ids]
            #
            # # 改为异步任务不等待执行完成
            # asyncio.create_task(insert_audit_many(collection.business_type, audit_params))
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"批量添加审计日志执行耗时: {elapsed:.6f}秒"
            # logger.info(sql_execution_time)
            
            logger.info(f"批量移除收藏成功，共删除{affected_rows}条记录")

            return RspBase(content=f"批量移除收藏成功，共删除{affected_rows}条记录")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"批量移除收藏失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()