"""
用户扩展
"""

from fastapi import APIRouter, HTTPException, Request, Query, Path, Body
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspList, RspBase, RspListPage
from ai_gateway.schemas.api.common.user_extend import UserExtend
from ai_gateway.service.common.user_extend import save_user_extend_info

user_extend_router = APIRouter(prefix="/common/user_extend")

# 保存用户扩展信息，如：订阅邮箱(支持多个)
@user_extend_router.post("/save_user_extend", summary="保存用户扩展信息", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def save_user(
        request: Request,
        user_extend: UserExtend
):
    return await save_user_extend_info(request, user_extend)
