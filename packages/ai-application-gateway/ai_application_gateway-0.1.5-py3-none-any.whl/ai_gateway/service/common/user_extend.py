"""
用户扩展
"""

from fastapi import HTTPException, Request
from ai_gateway.schemas.api.base import RspBase
import pymysql
import json
from loguru import logger
from datetime import datetime

from ai_gateway.schemas.api.common.audit import ChangeType, Audit, AuditableType
from ai_gateway.schemas.api.common.user_extend import UserExtend
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.audit import insert_audit
from ai_gateway.service.common.common_pymysql_tool import get_pool
from ai_gateway.service.common.approve import _insert_approve
from ai_gateway.schemas.api.common.approve import AddDelApprove, ApproveTypeCode
from ai_gateway.config import config

async def save_user_extend_info(
        request: Request,
        user_extend: UserExtend
) -> RspBase:
    try:
        connection_pool = get_pool(user_extend.business_type)
        connection = connection_pool.connect()
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            # 检查用户是否存在
            check_sql = """
            SELECT pid, sub_emails FROM users 
            WHERE id = %(user_id)s
            """
            cursor.execute(check_sql, {'user_id': user_extend.user_id})
            exists = cursor.fetchone()

            object_ids = []
            if exists:
                if exists["sub_emails"] == json.dumps(user_extend.sub_emails):
                    return RspBase(content="邮箱未修改，无需更新")
                else:
                    # 更新操作
                    update_sql = """
                    UPDATE users
                    SET sub_emails = %s,
                        updated_at = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_sql, (
                        json.dumps(user_extend.sub_emails) if user_extend.sub_emails else None,
                        datetime.now(),
                        user_extend.user_id
                    ))
                    connection.commit()

                    # 添加审计日志
                    await insert_audit(
                        Audit(
                            business_type=user_extend.business_type,
                            user_id=user_extend.user_id,
                            auditable_id=int(exists["pid"]),
                            auditable_type=AuditableType.USER,
                            changes={"sub_emails": [json.loads(exists["sub_emails"]) if exists["sub_emails"] else None,
                            user_extend.sub_emails if user_extend.sub_emails else None]},
                            change_type=ChangeType.UPDATE
                        )
                    )

                    object_ids.append(int(exists["pid"]))
                    msg = f"更新用户扩展信息成功，用户ID: {user_extend.user_id}"
                    logger.info(msg)
            else:
                # 插入操作
                insert_sql = """
                INSERT INTO users (
                    id, 
                    sub_emails
                ) VALUES (%s, %s)
                """
                cursor.execute(insert_sql, (
                    user_extend.user_id,
                    json.dumps(user_extend.sub_emails) if user_extend.sub_emails else None
                ))

                # 获取最后插入的ID
                last_id = cursor.lastrowid
                connection.commit()

                # 添加审计日志
                await insert_audit(
                    Audit(
                        business_type=user_extend.business_type,
                        user_id=user_extend.user_id,
                        auditable_id=last_id,
                        auditable_type=AuditableType.USER,
                        changes={"sub_emails": user_extend.sub_emails},
                        change_type=ChangeType.CREATE
                    )
                )

                object_ids.append(last_id)
                msg = f"新增用户扩展信息成功，用户ID: {user_extend.user_id}"
                logger.info(msg)

            # 添加商机订阅审批
            if config.opportunity.opportunity_subscribable_email_approve and user_extend.business_type == "opportunity":
                emails = user_extend.sub_emails
                if emails and len(emails) > 0:  # 有订阅邮箱时，再添加审批
                    await _insert_approve(AddDelApprove(
                        business_type = user_extend.business_type,
                        user_id=user_extend.user_id,
                        object_user_id=user_extend.user_id,
                        object_ids=object_ids,
                        approve_type_code=ApproveTypeCode.Opportunity_Subscribable_Email,
                        approve_user_id=None,
                        approve_description = f"商机订阅审批，收件人邮箱：{emails}"
                    ))

            return RspBase(content=msg)
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    except Exception as e:
        error_str = f"保存用户扩展信息失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                          detail=error_str)
    finally:
        if connection:
            connection.close()
