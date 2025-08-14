from datetime import datetime
from fastapi import HTTPException
from loguru import logger
import pymysql
import os
import asyncio
import ast

from ai_gateway.service.common.common_pymysql_tool import get_pool
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.common.email import _send_email

# 赂向所有订阅了商机的用户定时发送邮件
async def send_email_opportunity(
) :
    try:
        connection_pool = get_pool("opportunity")
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 先查询要删除记录的ID
            select_sql = "SELECT pid, id, sub_emails FROM users WHERE sub_emails IS NOT NULL"

            cursor.execute(select_sql)
            emails = [row['sub_emails'] for row in cursor.fetchall()]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"查询用户 SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"查询用户 SQL: {select_sql}")
            logger.info(sql_execution_time)
            
            if not emails:
                logger.info("没有找到用户")
                return False

            # 后续需要增加用户是否有订阅商机的记录，从表user_subscriptions查询
            # ------------------------------

            # 将emails，格式为["test1@example.com", "test2@example.com"]转为 to_list数组
            # 将emails字符串转换为邮箱列表
            # 使用set来存储所有邮箱地址以实现全局去重
            email_set = set()
            for email_str in emails:
                try:
                    # 安全解析字符串形式的数组
                    email_list = ast.literal_eval(email_str)
                    if isinstance(email_list, list):
                        email_set.update(email_list)
                    
                    # # 邮箱格式验证正则表达式
                    # email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    # # email_pattern = r'^(?!\.)(?!.*\.@)(?!.*@\.)([a-zA-Z0-9!#$%&\'*+\-/=?^_`{|}~]+(\.[a-zA-Z0-9!#$%&\'*+\-/=?^_`{|}~]+)*)@([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})$'
                    # # - 正则验证会增加处理时间，建议对数据库原始数据做预处理
                    # # - 对于国际化邮箱（包含unicode字符），需要更复杂的正则处理
                    
                    # for email in email_list:
                    #     if isinstance(email, str) and re.match(email_pattern, email):
                    #         email_set.update(email_list)
                    #     else:
                    #         logger.warning(f"无效邮箱格式: {email}")
                    
                except (SyntaxError, ValueError) as e:
                    logger.error(f"邮箱格式解析失败: {email_str}，错误: {e}")

            if not email_set:
                logger.error("没有找到有效的邮箱")
                return False

            # 将set转换为list用于发送邮件
            to_list = list(email_set)
            subject = '每日商机推送'
            text = get_email_text()
            # 项目目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            # 附件本地路径
            attachment_path = os.path.join(project_root, "data", "send_email", "daily_result.csv")
            # HTTP URL
            # attachment_path = "http://localhost:8008/data/send_email/daily_result.csv"
            await _send_email(to_list, subject, text, attachment_path)

            return True

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

# 邮件正文
def get_email_text():
    formatted_today = datetime.now().strftime("%Y-%m-%d")
    text = f"""<!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>每日商机推送 - 人工智能条线客户挖掘结果</title>
        </head>
        <body style="font-family: Arial, sans-serif;">
        <h2 style="color:#333;">每日商机推送</h2>
        <p><strong>主题：</strong>人工智能条线客户挖掘结果 – {formatted_today}</p>

        <p>尊敬的渠道营销部同事：</p>

        <p>您好！</p>

        <p>为支持贵部门精准拓展客户、把握市场机会，我们筛选出具有较高合作意向的商机信息。</p>

        <p>现将<strong>{formatted_today}</strong>的人工智能领域客户商机挖掘结果整理并附于邮件中，请参见附件《daily_result.csv》。</p>

        <p><strong>请注意查看附件，并根据需要采取相应行动。</strong></p>

        <p>如需进一步细化某类客户信息或调整挖掘维度，请随时告知，我们将持续优化模型策略，提升线索质量，助力业务增长。</p>

        <p>顺祝商祺！</p>

        <hr>

        <p><strong>中信证券股份有限公司</strong><br>
        信息技术中心<br>
        人工智能条线<br>
        {formatted_today}</p>

        <address>
            地址：北京市朝阳区亮马桥路48号中信证券大厦<br>
            邮编：100126<br>
            E-mail：<a href="mailto:data_mining@citics.com">data_mining@citics.com</a>
        </address>
        </body>
        </html>"""
    return text


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(send_email_opportunity())