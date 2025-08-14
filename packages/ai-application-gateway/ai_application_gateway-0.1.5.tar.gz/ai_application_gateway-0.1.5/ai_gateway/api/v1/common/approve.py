from fastapi import APIRouter, Request, Body
from ai_gateway.service.common.approve import _batch_approve, _get_approve_list, _get_approve
from ai_gateway.schemas.api.common.approve import InApprove, InGetApproves, InGetApprove
from ai_gateway.schemas.api.base import RspBase, RspListPage, RspList
from ai_gateway.core.middleware import trace_request

approve_router = APIRouter(prefix="/common/approve")


@approve_router.post("/batch_approve", summary="批量审批", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def batch_approve(request: Request,
        approve: InApprove = Body(...)
):      
    """
    批量审批API接口
    Args:
        request: 包含审批信息的请求体
        approve: 审批信息
    Returns:
        dict: 包含审批状态和消息的字典
    """
    rsp = await _batch_approve(approve)

    return rsp


@approve_router.post("/get_approve_list", summary="获取审批列表数据", response_description="返回成功",
                         response_model=RspListPage[dict])
@trace_request
async def get_approves_list(request: Request,
        approve: InGetApproves = Body(...)
):      
    """
    获取审批列表数据API接口
    Args:
        request: 包含审批信息的请求体
        approve: 审批信息
    Returns:
        dict: 包含审批状态和消息的字典
    """
    rsp = await _get_approve_list(approve)

    return rsp


@approve_router.post("/get_approve", summary="获取单条审批记录", response_description="返回成功",
                         response_model=RspList[dict])
@trace_request
async def get_approve(request: Request,
        approve: InGetApprove = Body(...)
):      
    """
    获取单条审批记录API接口
    Args:
        request: 包含审批信息的请求体
        approve: 审批信息
    Returns:
        dict: 包含审批状态和消息的字典
    """
    rsp = await _get_approve(approve)

    return rsp