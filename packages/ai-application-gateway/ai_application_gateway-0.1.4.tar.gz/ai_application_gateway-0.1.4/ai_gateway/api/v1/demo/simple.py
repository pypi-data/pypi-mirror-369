"""
标准示例：简单请求 API 路由
"""
import json

from fastapi import APIRouter, HTTPException, Request, Query, Path

from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspDetail, RspBase
from ai_gateway.schemas.api.demo.simple import SimpleIn, SimpleOut, SimplePatchIn

simple_router = APIRouter(prefix="/demo/simple")


@simple_router.post("/post_simple", summary="POST 创建新的 simple 条目", response_description="返回新建的simple条目" , response_model=RspDetail[SimpleOut])
@trace_request
async def post_simple(
    request: Request,
    item: SimpleIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """POST示例"""

    # 获取请求体中的 JSON 数据
    # json_data = await request.json()
    # get_query = json_data.get("query")

    simple_data = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "created",
        "message": "simple successfully created"
    }

    return RspDetail(items=simple_data)


@simple_router.put("/put_simple/{item_id}", summary="PUT 更新simple条目", response_description="返回更新的simple条目", response_model=RspDetail[SimpleOut])
@trace_request
async def put_simple(
        request: Request,
        item: SimpleIn,
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query("查询参数", description="查询参数")
):
    """PUT示例 - 完整替换资源"""
    # PUT 需要提供资源的完整表示，缺少字段将被删除或设置为默认值
    updated_content = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "updated",
        "message": "resource completely replaced"
    }
    return RspDetail(items=updated_content)

@simple_router.patch("/patch_simple/{item_id}", summary="PATCH 部分更新simple条目", response_description="返回部分更新的simple条目", response_model=RspDetail[SimpleOut])
@trace_request
async def patch_simple(
        request: Request,
        updates: SimplePatchIn,
        user_id: str = Query(..., description="用户ID"),    # 必填
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query("查询参数", description="查询参数")
):
    """PATCH示例 - 部分更新资源"""
    # 模拟数据库中的现有资源
    existing_resource = {
        "item_id": item_id,
        "name": "名称",
        "query": query,
        "description": "原始描述",
        "status": "active",
    }
    
    # PATCH 只更新提供的字段，保留其他现有字段
    existing_resource.update(updates)  # 只更新传入的字段
    existing_resource["message"] = "resource partially updated"
    
    return RspDetail(items=existing_resource)


@simple_router.get("/get_simple/{item_id}", summary="GET 获取simple条目", response_description="返回simple条目" , response_model=RspDetail[SimpleOut])
@trace_request
async def get_simple(
        request: Request,
        item_id: str = Path(description="唯一ID", example="item-1"),
        user_id: str = Query(..., description="用户ID"),    # 必填
        query: str = Query(..., description="查询参数")    # 必填
):
    """GET示例"""
    retrieved_content = {
        "item_id": item_id,
        "name": "名称",
        "query": query,
        "description": "说明",
        "status": "retrieved",
        "message": "simple successfully retrieved",
    }
    return RspDetail(items=retrieved_content)



@simple_router.delete("/delete_simple/{item_id}/{user_id}", summary="DELETE 删除simple条目", response_description="返回删除的simple条目" , response_model=RspBase)
@trace_request
async def delete_simple(
        request: Request,
        item_id: str = Path(description="唯一ID", example="item-1"),
        user_id: str = Path(..., description="用户ID"),    # 必填
        query: str = Query("查询参数", description="查询参数")
):
    """DELETE示例"""
    deletion_status = {
        "item_id": item_id,
        "name": "名称",
        "query": query,
        "description": "说明",
        "status": "deleted",
        "message": "simple successfully deleted"
    }
    return RspBase()