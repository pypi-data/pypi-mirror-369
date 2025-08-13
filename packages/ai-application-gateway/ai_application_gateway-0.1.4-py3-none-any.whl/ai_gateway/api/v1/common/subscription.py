"""
订阅
"""

from fastapi import APIRouter, HTTPException, Request, Query, Path, Body
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspList, RspBase, RspListPage
from ai_gateway.schemas.api.common.subscription import Subscription
from ai_gateway.service.common.subscription import insert_subscriptions, delete_subscriptions

subscription_router = APIRouter(prefix="/common/subscription")

@subscription_router.post("/add_subscriptions", summary="批量添加订阅", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def add_subscriptions(
        request: Request,
        subscription: Subscription = Body(...)
):
    if subscription.subscribable_id is None or len(subscription.subscribable_id) == 0:
        raise HTTPException(status_code=400, detail="subscribable_id 不能为空")
    return await insert_subscriptions(request, subscription)


@subscription_router.post("/remove_subscriptions", summary="批量移除订阅", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def remove_subscriptions(
        request: Request,
        subscription: Subscription = Body(...)
):
    if subscription.subscribable_id is None or len(subscription.subscribable_id) == 0:
        raise HTTPException(status_code=400, detail="subscribable_id 不能为空")
    return await delete_subscriptions(request, subscription)