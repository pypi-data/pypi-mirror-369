"""
通用审批
"""

from ast import Dict
import pymysql
import json
from loguru import logger
from datetime import datetime

from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.common_pymysql_tool import get_pool
from fastapi import HTTPException
from ai_gateway.schemas.api.base import RspBase, RspListPage, RspList
from ai_gateway.schemas.api.common.approve import AddDelApprove, InGetApproves, InApprove, ApproveOrderField, \
    ApproveTypeCode, InGetApprove, ApproveStateProcess
from ai_gateway.service.common.subscription_approve import update_subscription_approve_state, send_subscription_approve_email

# 插入审批数据
async def _insert_approve(
        approve: AddDelApprove,
) -> RspBase:
    try:
        connection_pool = get_pool(approve.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            # 检查是否已存在待审批的记录
            base_query = "SELECT id, object_ids, approve_description FROM approves where is_deleted = 0 and object_user_id = %s and approve_type_code = %s and approve_state = 0"
            cursor.execute(base_query, (
                approve.object_user_id,
                approve.approve_type_code
            ))
            obj = cursor.fetchone()
            if obj:
                # 去重合并object_ids
                object_ids = set(json.loads(obj["object_ids"]))  # 转换为集合
                id = obj["id"]
                is_update_object_ids =False   # 是否要更新审批对象ids
                # 检查approve.object_ids中的每个元素是否已存在,如果不存在则添加
                for item in approve.object_ids:
                    if item not in object_ids:
                        object_ids.add(item)
                        is_update_object_ids = True

                update_sql = "UPDATE approves SET updated_at = %(updated_at)s"
                params = {}
                params["updated_at"] = datetime.now()
                is_update = False   # 是否需要更新
                if approve.approve_description != obj["approve_description"]: # 更新审批描述信息
                    update_sql += ", approve_description = %(approve_description)s"
                    params["approve_description"] = approve.approve_description
                    is_update = True
                if is_update_object_ids:
                    update_sql += ", object_ids = %(object_ids)s"
                    params["object_ids"] = json.dumps(list(object_ids)),  # 将集合转为列表再序列化
                    is_update = True
                if is_update:
                    # 更新审批对象ids
                    update_sql += " WHERE id = %(id)s"
                    params["id"] = id
                    cursor.execute(update_sql, params)
                    connection.commit()
                    logger.info(f"更新审批成功，审批ID: {id}")
                    return RspBase(content=f"更新审批成功，审批ID: {id}")
                else:
                    logger.info("已存在待审批的记录，无需更新，审批ID: {id}")
            else:
                insert_sql = """
                INSERT INTO approves (
                    app_code,
                    object_user_id,
                    object_ids,
                    approve_type_code,
                    approve_type_name,
                    approve_user_id,
                    approve_description,
                    created_at
                ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)
                """
                approve_type_name = ""
                if approve.approve_type_code == ApproveTypeCode.Opportunity_Subscribable_Email:
                    approve_type_name = config.opportunity.opportunity_subscribable_email_approve_subject
                elif approve.approve_type_code == ApproveTypeCode.AshareCompany_Subscribable:
                    approve_type_name = "个股商机订阅"
                created_at = datetime.now()
                app_code = ""
                if approve.business_type=="opportunity":# 商机挖掘
                    app_code = "app-link-532bc071ddf640ee93e6ee0a7acb3fdb" # 商机挖掘CAP平台编码
                cursor.execute(insert_sql, (
                    app_code, 
                    approve.object_user_id,
                    json.dumps(approve.object_ids) if approve.object_ids else None,
                    approve.approve_type_code,
                    approve_type_name,
                    approve.approve_user_id,
                    approve.approve_description,
                    created_at
                ))
                connection.commit()

                # 调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知
                if approve.business_type=="opportunity" and approve.approve_type_code == ApproveTypeCode.Opportunity_Subscribable_Email and config.opportunity.opportunity_subscribable_email_approve_send:
                    await send_subscription_approve_email(
                        cursor,
                        app_code,
                        approve,
                        approve_type_name,
                        created_at
                    )

                logger.info(f"添加审批成功")
                return RspBase(content=f"添加审批成功")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"添加审批失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()

# 删除审批数据
async def _delete_approve(
        approve: AddDelApprove,
) -> RspBase:
    try:
        connection_pool = get_pool(approve.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            # 检查是否已存在待审批的记录
            base_query = "SELECT id, object_ids FROM approves where is_deleted = 0 and object_user_id = %s and approve_type_code = %s and approve_state = 0"
            cursor.execute(base_query, (
                approve.object_user_id,
                approve.approve_type_code
            ))
            obj = cursor.fetchone()
            if obj:
                # 去重合并object_ids
                object_ids = set(json.loads(obj["object_ids"]))  # 转换为集合
                id = obj["id"]

                # 如果要删除的审批对象ids与数据库中的object_ids完全相等，则删除这条审批记录
                if set(approve.object_ids) == object_ids:
                    update_sql = "UPDATE approves SET is_deleted = 1, updated_at = %s WHERE id = %s"
                    cursor.execute(update_sql, (
                        datetime.now(),
                        id
                    ))
                    connection.commit()
                    logger.info(f"删除审批成功，审批ID: {id}")
                    return RspBase(content=f"删除审批成功，审批ID: {id}")

                is_remove =False
                # 检查approve.object_ids中的每个元素是否已存在,如果存在则删除
                for item in approve.object_ids:
                    if item in object_ids:
                        object_ids.remove(item)
                        is_remove = True
                if is_remove:
                    # 更新审批对象ids
                    update_sql = "UPDATE approves SET object_ids= %s, updated_at = %s WHERE id = %s"
                    cursor.execute(update_sql, (
                        json.dumps(list(object_ids)),  # 将集合转为列表再序列化
                        datetime.now(),
                        id
                    ))
                    connection.commit()
                    logger.info(f"更新审批对象ids成功，审批ID: {id}")
                    return RspBase(content=f"更新审批对象ids成功，审批ID: {id}")

            return RspBase(content="不存在待审批的记录，无需删除")

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"删除审批失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()


# 批量审批
async def _batch_approve(
        approve: InApprove,
) -> RspBase:
    try:
        connection_pool = get_pool(approve.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            # 查询审批数据
            query_sql = "SELECT id, object_ids FROM approves where id in %s and is_deleted = 0 and approve_state = 0"
            cursor.execute(query_sql, (
                tuple(approve.id),
            ))
            obj_list = cursor.fetchall()
            if not obj_list:
                return RspBase(content="不存在待审批的记录，无需审批")
            
            updated_ids = [row["id"] for row in obj_list]

            # # 合并审批对象ids
            # object_ids = []
            # for obj in obj_list:
            #     # 去重合并  审批对象ids
            #     object_ids += json.loads(obj["object_ids"])
            # object_ids = tuple(set(object_ids))

            # 更新审批数据
            update_sql = """
            UPDATE approves SET approve_state = %s, approve_at = %s, approve_user_id = %s, approve_user_name = %s
            , approve_user_email = %s, cc_users = %s, object_user_name = %s WHERE id in %s and is_deleted = 0
            """
            cursor.execute(update_sql, (
                approve.approve_state.value,
                datetime.now(),
                approve.approve_user_id,
                approve.approve_user_name,
                approve.approve_user_email,
                json.dumps(approve.cc_users) if approve.cc_users else None,  # 将字典列表序列化为JSON字符串
                approve.object_user_name,
                tuple(updated_ids),
            ))
            # 返回更新记录数
            updated_rows = cursor.rowcount
            connection.commit()

            # # 更新个股订阅表数据，审批状态为：已通过或已驳回
            # if approve.approve_type_code == ApproveTypeCode.AshareCompany_Subscribable and len(object_ids) > 0:
            #     await update_subscription_approve_state("opportunity", object_ids, approve.approve_state)

            msg = f"审批成功！更新记录数：{updated_rows}, 更新审批ids：{updated_ids}"
            logger.info(msg)
            return RspBase(content=msg)

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"审批失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()


# 获取审批列表数据
async def _get_approve_list(
    approve: InGetApproves
) -> RspListPage[dict]:
    try:
        connection_pool = get_pool(approve.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            result_list: list = []
            total = 0
            conditions = []
            params = {}

            # 构建查询条件
            if approve.approve_type_code:
                conditions.append("approve_type_code = %(approve_type_code)s ")
                params['approve_type_code'] = approve.approve_type_code.value
            if approve.approve_state:
                conditions.append("approve_state IN %(approve_state)s ")
                params['approve_state'] = tuple(state.value for state in approve.approve_state)
            if approve.approve_user_id:
                conditions.append("approve_user_id = %(approve_user_id)s ")
                params['approve_user_id'] = approve.approve_user_id
            
            # 查询待审批数据总数
            count_query = "SELECT COUNT(*) as total FROM approves WHERE is_deleted = 0"
            # 查询待审批数据列表
            base_query = "SELECT * FROM approves WHERE is_deleted = 0"
            if conditions:
                count_query += " AND "+" AND ".join(conditions)
                base_query += " AND "+" AND ".join(conditions)

            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            if total > 0:
                # 添加排序
                if approve.order:
                    order_clauses = []
                    for field, direction in approve.order.items():
                        if direction not in (1, 2):
                            continue
                        for f in ApproveOrderField:
                            if field == f.name:
                                order_clauses.append(f"{f.value} {'DESC' if direction == 1 else 'ASC'}")
                                break
                    if order_clauses:
                        base_query += " ORDER BY " + ", ".join(order_clauses)
                    

                 # 添加分页
                if approve.page is not None and approve.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': approve.size,
                        'offset': (approve.page - 1) * approve.size
                    })

                cursor.execute(base_query, params)
                
                # 构建返回结果
                result_list = cursor.fetchall()

            content_res = "审批记录数量：" + str(total)
            return RspListPage(
                content=content_res,
                items=result_list,
                total=total,
                page=approve.page,
                size=approve.size,
            )

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"获取审批列表数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()


# 获取单条审批记录（前端打开审批页面后，点击审批按钮时调用，判断是否已经审批了，或要审批的对象是否有变化，给出提示）
async def _get_approve(
    approve: InGetApprove
) -> RspList[dict]:
    """
    获取单条审批记录
    
    参数:
        approve: InGetApprove - 包含查询条件的审批请求对象
        
    返回:
        RspBase - 包含审批记录的响应对象
    """
    try:
        connection_pool = get_pool(approve.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            conditions = []
            params = {}

            base_query = "SELECT * FROM approves WHERE id = %(id)s and is_deleted = 0"
            params['id'] = approve.id

            # 构建查询条件
            if approve.approve_type_code:
                conditions.append("approve_type_code = %(approve_type_code)s ")
                params['approve_type_code'] = approve.approve_type_code.value
            if approve.approve_state:
                conditions.append("approve_state IN %(approve_state)s ")
                params['approve_state'] = tuple(state.value for state in approve.approve_state)

            if conditions:
                base_query += " AND "+" AND ".join(conditions)

            cursor.execute(base_query, params)
            result_list = cursor.fetchall()
            content_res = "审批记录ID：" + str(approve.id)
            if len(result_list) == 0:
                content_res = "审批记录ID：" + str(approve.id) + "，不存在"
            return RspList(
                content=content_res,
                items=result_list
            )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"获取单条审批记录失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()
