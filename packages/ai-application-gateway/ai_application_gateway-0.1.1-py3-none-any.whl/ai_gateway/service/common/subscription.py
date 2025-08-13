"""
订阅
"""

from urllib.request import Request

from fastapi import HTTPException
from loguru import logger
import pymysql

from ai_gateway.schemas.api.base import RspBase
from ai_gateway.schemas.api.common.subscription import Subscription, SubscriptionType
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.common_pymysql_tool import get_pool
from ai_gateway.schemas.api.common.audit import Audit, AuditableType, ChangeType
from ai_gateway.service.common.audit import insert_audit_many
from datetime import datetime
import asyncio
from ai_gateway.schemas.api.common.approve import AddDelApprove, ApproveTypeCode, ApproveStateProcess
from ai_gateway.service.common.approve import _insert_approve, _delete_approve

# 添加订阅
async def insert_subscriptions(
        request: Request,
        subscription: Subscription
) -> RspBase:
    try:
        connection_pool = get_pool(subscription.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 批量检查是否已存在
            check_sql = """
            SELECT id, subscribable_id, is_deleted FROM user_subscriptions 
            WHERE user_id = %(user_id)s 
              AND subscribable_id IN %(subscribable_ids)s 
              AND subscribable_type = %(subscribable_type)s
            """
            params = {
                'user_id': subscription.user_id,
                'subscribable_ids': tuple(subscription.subscribable_id),
                'subscribable_type': subscription.subscribable_type
            }
            cursor.execute(check_sql, params)
            result = cursor.fetchall()
            # 已经存在的订阅记录subscribable_ids
            existing_subscribable_ids = [row["subscribable_id"] for row in result]
            # 已经存在但已删除的订阅记录
            existing_deleted_ids = [row["id"] for row in result if row["is_deleted"] == 1]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"获取已存在订阅SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"获取已存在订阅SQL: {check_sql}")
            logger.info(sql_execution_time)

            # 过滤掉已存在的ID
            new_subscribable_ids = [id for id in subscription.subscribable_id if id not in existing_subscribable_ids]
            if not new_subscribable_ids and not existing_deleted_ids:
                logger.info("所有订阅已存在")
                return RspBase(content="所有订阅已存在")

            start_time = datetime.now()
            inserted_ids = []
            if new_subscribable_ids:
                # 批量插入
                insert_sql = """
                INSERT INTO user_subscriptions (
                  `user_id`,
                  `subscribable_id`,
                  `subscribable_type`
                ) VALUES (%s, %s, %s)
                """

                params = [(subscription.user_id, subscribable_id, subscription.subscribable_type) for subscribable_id in new_subscribable_ids]
                cursor.executemany(insert_sql, params)
                connection.commit()

                # # 获取新增记录的主键ID
                # select_sql = """
                # SELECT id FROM user_subscriptions
                # WHERE user_id = %s
                # AND subscribable_id IN %s
                # AND subscribable_type = %s
                # ORDER BY id ASC
                # LIMIT %s
                # """
                # cursor.execute(select_sql, (
                #     subscription.user_id,
                #     tuple(new_subscribable_ids),
                #     subscription.subscribable_type,
                #     len(new_subscribable_ids)
                # ))
                # inserted_records = cursor.fetchall()
                # inserted_ids = [row['id'] for row in inserted_records]

            if existing_deleted_ids:
                # 批量更新
                update_sql = """
                UPDATE user_subscriptions SET is_deleted = 0, approve_state=0, updated_at = %s WHERE id = %s
                """
                cursor.executemany(update_sql, [(datetime.now(), id) for id in existing_deleted_ids])
                connection.commit()

            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"批量添加订阅SQL执行耗时: {elapsed:.6f}秒"
            logger.info(sql_execution_time)


            # # 要审批的主键 ID，合并去重新增和恢复
            # inserted_ids = list(set(inserted_ids + existing_deleted_ids))

            # # 添加审批记录
            # if subscription.subscribable_type == SubscriptionType.AshareCompany:
            #     await _insert_approve(AddDelApprove(
            #         business_type = subscription.business_type,
            #         user_id=subscription.user_id,
            #         object_user_id=subscription.user_id,
            #         object_ids=inserted_ids,
            #         approve_type_code=ApproveTypeCode.AshareCompany_Subscribable,
            #         approve_user_id=None,
            #     ))

            # start_time = datetime.now()
            # # 插入后查询新增ID
            # select_sql = """
            # SELECT id,subscribable_id FROM user_subscriptions
            # WHERE user_id = %s
            # AND subscribable_id IN %s
            # AND subscribable_type = %s
            # ORDER BY id ASC
            # LIMIT %s
            # """
            # cursor.execute(select_sql, (
            #     subscription.user_id,
            #     tuple(new_ids),
            #     subscription.subscribable_type,
            #     len(new_ids)
            # ))
            # result_list = cursor.fetchall()
            # # inserted_ids = [row['id'] for row in result_list]
            # # subscribable_ids =[row['subscribable_id'] for row in result_list]
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"插入后查询新增ID SQL执行耗时: {elapsed:.6f}秒"
            # logger.info(f"插入后查询新增ID SQL: {select_sql}")
            # logger.info(sql_execution_time)

            #
            # start_time = datetime.now()
            # # 批量添加审计日志
            # audit_params = [(
            #     subscription.user_id,
            #     inserted_id,
            #     AuditableType.USER_SUBSCRIPTION,
            #     None,
            #     ChangeType.CREATE
            # ) for inserted_id in inserted_ids]
            #
            # asyncio.create_task(insert_audit_many(subscription.business_type, audit_params))
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"批量添加审计日志执行耗时: {elapsed:.6f}秒"
            # logger.info(sql_execution_time)

            logger.info(f"批量添加订阅成功，新增{len(new_subscribable_ids)}条记录，恢复{len(existing_deleted_ids)}条记录")
            return RspBase(content=f"批量添加订阅成功，新增{len(new_subscribable_ids)}条记录，恢复{len(existing_deleted_ids)}条记录")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"批量添加订阅失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()

# 批量移除订阅
async def delete_subscriptions(
        request: Request,
        subscription: Subscription
) -> RspBase:
    try:
        connection_pool = get_pool(subscription.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 先查询要删除记录的ID
            select_sql = """
            SELECT id FROM user_subscriptions 
            WHERE user_id = %(user_id)s 
              AND subscribable_id IN %(subscribable_ids)s 
              AND subscribable_type = %(subscribable_type)s 
              AND is_deleted = 0
            """
            params = {
                'user_id': subscription.user_id,
                'subscribable_ids': tuple(subscription.subscribable_id),
                'subscribable_type': subscription.subscribable_type
            }
            cursor.execute(select_sql, params)
            result_list = cursor.fetchall()
            deleted_ids = [row['id'] for row in result_list]

            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"查询要删除记录ID SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"查询要删除记录ID SQL: {select_sql}")
            logger.info(sql_execution_time)

            if not deleted_ids:
                logger.info("没有找到要删除的订阅记录")
                return RspBase(content="没有找到要删除的订阅记录")

            start_time = datetime.now()
            # 执行假删除操作
            update_sql = """
            UPDATE user_subscriptions SET is_deleted = 1, updated_at = %s 
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

            # 删除审批记录
            # if subscription.subscribable_type == SubscriptionType.AshareCompany:
            #     await _delete_approve(AddDelApprove(
            #         business_type = subscription.business_type,
            #         user_id=subscription.user_id,
            #         object_user_id=subscription.user_id,
            #         object_ids=deleted_ids,
            #         approve_type_code=ApproveTypeCode.AshareCompany_Subscribable,
            #         approve_user_id=None,
            #     ))

            # start_time = datetime.now()
            # # 批量添加审计日志
            # audit_params = [(
            #     subscription.user_id,
            #     deleted_id,
            #     AuditableType.USER_SUBSCRIPTION,
            #     None,
            #     ChangeType.DELETE
            # ) for deleted_id in deleted_ids]
            #
            # asyncio.create_task(insert_audit_many(subscription.business_type, audit_params))
            # # 计算耗时
            # elapsed = (datetime.now() - start_time).total_seconds()
            # sql_execution_time = f"批量添加审计日志执行耗时: {elapsed:.6f}秒"
            # logger.info(sql_execution_time)

            logger.info(f"批量移除订阅成功，共删除{affected_rows}条记录")
            return RspBase(content=f"批量移除订阅成功，共删除{affected_rows}条记录")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"批量移除订阅失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()
