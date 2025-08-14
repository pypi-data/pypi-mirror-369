"""
收藏
"""

from fastapi import APIRouter, HTTPException, Request, Query, Path, Body
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspList, RspBase, RspListPage
from ai_gateway.schemas.api.common.collection import Collection
from ai_gateway.service.common.collection import insert_collections, delete_collections

collection_router = APIRouter(prefix="/common/collection")

@collection_router.post("/add_collections", summary="批量添加收藏", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def add_collections(
        request: Request,
        collection: Collection = Body(...)
):
    if collection.collectable_id is None or len(collection.collectable_id) == 0:
        raise HTTPException(status_code=400, detail="collectable_id 不能为空")
    return await insert_collections(request, collection)


@collection_router.post("/remove_collections", summary="批量移除收藏", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def remove_collections(
        request: Request,
        collection: Collection = Body(...)
):
    if collection.collectable_id is None or len(collection.collectable_id) == 0:
        raise HTTPException(status_code=400, detail="collectable_id 不能为空")
    return await delete_collections(request, collection)
