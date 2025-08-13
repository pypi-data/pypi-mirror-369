import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from loguru import logger
import requests
import asyncio
from ai_gateway.schemas.api.base import RspBase

async def _send_email(to_list, subject, text, attachments:list[str]=None) -> RspBase:
    """
    发送带附件的邮件
    
    Args:
        to_list: 收件人邮箱列表
        subject: 邮件主题
        text: 邮件正文(HTML格式)
        attachments: 附件文件路径(可选), 可以是本地路径或HTTP URL
    
    Returns:
        int: 发送成功返回1，失败返回0
    """
    if not to_list:
        format_str = "收件人邮箱列表为空"
        logger.error(format_str)
        return RspBase().fail(format_str)
    if not subject:
        format_str = "邮件主题为空"
        logger.error(format_str)
        return RspBase().fail(format_str)
    if not text:
        format_str = "邮件正文为空"
        logger.error(format_str)
        return RspBase().fail(format_str)

    # 从配置中获取邮箱参数
    # Email地址和口令
    from_addr = os.getenv('EMAIL_FROM', 'data_mining@citics.com')
    password = os.getenv('EMAIL_PASSWORD')
    # 输入SMTP服务器地址
    smtp_server = os.getenv('SMTP_SERVER', 'newmail.citicsinfo.com')
    port = int(os.getenv('SMTP_PORT', '465'))

    if not password:
        format_str = "邮箱密码未配置"
        logger.error(format_str)
        return RspBase().fail(format_str)

    # 创建邮件对象
    message = MIMEMultipart()
    message['From'] = from_addr
    message['To'] = ";".join(to_list)
    message['Subject'] = Header(subject)
    message.attach(MIMEText(text, 'html'))

    # 添加附件(如果存在)
    if attachments:
            for attachment in attachments:
                try:
                    # 处理HTTP URL附件
                    if attachment.startswith(('http://', 'https://')):
                        mime_base, filename = _process_remote_attachment(attachment)
                    else:
                        # 处理本地文件附件
                        mime_base, filename = _process_local_attachment(attachment)

                    # 添加附件到邮件
                    _add_attachment_to_message(mime_base, filename, message)
                except Exception as e:
                    format_str = f"邮件添加附件失败，附件路径: {attachment}，错误详情: {str(e)}"
                    logger.error(format_str, exc_info=True)
                    return RspBase().fail(format_str)

    # 发送邮件
    try:
        with smtplib.SMTP_SSL(host=smtp_server, port=port) as smtpObj:
            smtpObj.login(from_addr, password)
            smtpObj.sendmail(from_addr, to_list, message.as_string())
        format_str = f"邮件发送成功： {to_list}"
        logger.info(format_str)
        return RspBase(content=format_str)
    except Exception as e:
        format_str = f"邮件发送失败： {e}"
        logger.error(format_str)
        return RspBase().fail(format_str)


def _process_remote_attachment(url: str) -> tuple:
    """
    处理远程URL附件
    :param url: 附件URL地址
    :return: (MIMEBase对象, 文件名)
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    mime_base = MIMEBase('application', 'octet-stream')
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            mime_base.set_payload(chunk)
    return mime_base, url.split('/')[-1]

def _process_local_attachment(filepath: str) -> tuple:
    """
    处理本地文件附件
    :param filepath: 本地文件路径
    :return: (MIMEBase对象, 文件名)
    """
    with open(filepath, 'rb') as f:
        mime_base = MIMEBase('application', 'octet-stream')
        mime_base.set_payload(f.read())
        return mime_base, os.path.basename(filepath)

def _add_attachment_to_message(mime_base: MIMEBase, filename: str, message: MIMEMultipart) -> None:
    """
    将附件添加到邮件消息中
    :param mime_base: MIMEBase对象
    :param filename: 附件文件名
    :param message: 邮件消息对象
    """
    encoders.encode_base64(mime_base)
    mime_base.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    message.attach(mime_base)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
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
    # 项目目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    # 附件本地路径
    attachment_path = os.path.join(project_root, "data", "send_email", "daily_result.csv")
    # HTTP URL
    attachment_url = "http://localhost:8008/data/send_email/daily_result.csv"
    attachments = [attachment_path, attachment_url]
    logger.info(f"attachments: {attachments}")
    to_list = ['royalseal11@126.com']
    subject = '每日商机推送'
    asyncio.run(_send_email(to_list, subject, text, attachments))