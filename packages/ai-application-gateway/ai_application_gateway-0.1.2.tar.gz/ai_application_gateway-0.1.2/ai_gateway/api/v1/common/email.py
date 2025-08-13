from fastapi import APIRouter, Request, Body
from ai_gateway.service.common.email import _send_email
from ai_gateway.schemas.api.base import RspBase
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.common.email import Email

email_router = APIRouter(prefix="/common/email")


@email_router.post("/send_email", summary="发送邮件", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def send_email(request: Request,
        email: Email = Body(...)
):      
    """
    发送邮件API接口
    Args:
        request: 包含邮件信息的请求体
        email: 邮件信息
    Returns:
        dict: 包含发送状态和消息的字典
    """
    rsp = await _send_email(
        to_list=email.to_list,
        subject=email.subject,
        text=email.text,
        attachments=email.attachments
    )

    return rsp