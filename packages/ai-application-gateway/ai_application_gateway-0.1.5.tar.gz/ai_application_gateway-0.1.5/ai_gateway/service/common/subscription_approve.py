"""
订阅审批
"""
from fastapi import HTTPException
from loguru import logger
import pymysql
import json

from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.common_pymysql_tool import get_pool
from datetime import datetime
from ai_gateway.schemas.api.common.approve import ApproveStateProcess, AddDelApprove


# 调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知
async def send_subscription_approve_email(
    cursor,
    app_code: str,
    approve: AddDelApprove,
    approve_type_name: str,
    created_at: str
):
    base_query = "SELECT id FROM approves where is_deleted = 0 and object_user_id = %s and approve_type_code = %s and approve_state = 0"
    cursor.execute(base_query, (
        approve.object_user_id,
        approve.approve_type_code
    ))
    obj = cursor.fetchone()
    if obj:
        id = obj["id"]  # 查询新增的 ID
        # 审批人
        receiver_ids = ""

        send_cap_approve_email_info = {
            "app_code": app_code, # 商机挖掘
            "subject": approve_type_name,  # 主题
            "receiver_extended_info": { # 邮件接收方扩展信息
                "receiver_ids": receiver_ids, # 审批人
                "cc_receiver_ids": "", # 抄送人
            },
            "message_data": {   # 邮件数据（字典类型）
                "id": id,
                "object_user_id": approve.object_user_id,
                "approve_type_code": approve.approve_type_code.value,
                "approve_type_name": approve_type_name,
                "approve_user_id": approve.approve_user_id,
                "approve_description": approve.approve_description,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        # 测试邮箱
        if config.opportunity.opportunity_subscribable_email_approve_send_test_email:
            send_cap_approve_email_info["receiver"] = [config.opportunity.opportunity_subscribable_email_approve_send_test_email]
            logger.info(f"测试邮箱: {config.opportunity.opportunity_subscribable_email_approve_send_test_email}")

        # 审批人或测试发送邮箱不空
        if receiver_ids:
            logger.info(f"审批人: {receiver_ids}")
        if receiver_ids or config.opportunity.opportunity_subscribable_email_approve_send_test_email:
            try:
                import httpx
                from httpx import ConnectError, TimeoutException
                timeout = httpx.Timeout(10.0, connect=5.0)  # 设置连接和读取超时
                async with httpx.AsyncClient(timeout=timeout) as client:
                    headers = {
                        "Origin": config.cap.url,
                        "access-key-id": config.cap.niche_email_api_key,
                        "Content-Type": "application/json",
                        "User-Agent": "ai-gateway"
                    }

                    url = f"{config.cap.url}{config.cap.send_email_api}"
                    response = await client.request("POST", url,
                                                    headers=headers,
                                                    json=send_cap_approve_email_info)

                    response.raise_for_status()  # 自动处理HTTP错误状态码
                    json_text = response.json()  # 直接使用response.json()方法

                    if "code" in json_text and json_text["code"] != 1:
                        logger.error(f"调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知 | 失败，CAP平台返回错误码: {json_text} | 请求内容: {send_cap_approve_email_info}")
                    else:
                        logger.info(f"调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知 | 成功 | 请求内容: {send_cap_approve_email_info}")
            except TimeoutException as e:
                logger.error(f"调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知 | 超时 | 错误: {str(e)} | 请求内容: {send_cap_approve_email_info}")
            except ConnectError as e:
                logger.error(f"调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知 | 失败，连接CAP平台失败 | 错误: {str(e)} | 请求内容: {send_cap_approve_email_info}")
            except Exception as e:
                logger.error(f"调用CAP平台发送待审批邮件，商机挖掘：订阅审批通知 | 失败 | 错误: {str(e)} | 请求内容: {send_cap_approve_email_info}")


# 更新订阅表审批状态为：已通过或已驳回
async def update_subscription_approve_state(
        business_type: str,
        object_ids: tuple,
        approve_state: ApproveStateProcess
):
    try:
        connection_pool = get_pool(business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 执行假删除操作
            update_sql = """
            UPDATE user_subscriptions SET approve_state = %s 
            WHERE id IN %s
            """
            cursor.executemany(update_sql, [(approve_state.value, object_ids)])
            affected_rows = cursor.rowcount
            connection.commit()
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"更新订阅审批状态为：{approve_state.value}，SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"更新订阅审批状态SQL: {update_sql}")
            logger.info(sql_execution_time)
            return affected_rows
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"更新订阅审批状态为：{approve_state.value}失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()

