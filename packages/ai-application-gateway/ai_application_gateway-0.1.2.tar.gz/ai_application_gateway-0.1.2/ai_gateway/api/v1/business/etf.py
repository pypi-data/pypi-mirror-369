"""
ETF 罗盘
"""
import json

from fastapi import APIRouter, HTTPException, Request, Query, Path
from starlette.responses import JSONResponse, Response

from ai_gateway.config import config
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspDetail, RspBase
from ai_gateway.schemas.api.business.etf import ETFIn, ETFOut, ETFPatchIn
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode
from ai_gateway.utils.forward import get_request_items, get_items

etf_router = APIRouter(prefix="/business/etf")


@etf_router.post("/post_etf", summary="POST 创建新的 etf 条目", response_description="返回新建的etf条目" , response_model=RspDetail[ETFOut])
@trace_request
async def post_etf(
    request: Request,
    item: ETFIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """POST示例"""

    items = await get_request_items(config.system.etf_url,
                                    path=f"/api/v1/etf/post_etf?item_id={item_id}&query={query}",
                                    request=request,
                                    data=item)

    return RspDetail(items=items)


@etf_router.put("/put_etf/{item_id}", summary="PUT 更新etf条目", response_description="返回更新的etf条目", response_model=RspDetail[ETFOut])
@trace_request
async def put_etf(
        request: Request,
        item: ETFIn,
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query("查询参数", description="查询参数")
):
    """PUT示例 - 完整替换资源"""

    items = await get_request_items(config.system.etf_url,
                                    path=f"/api/v1/etf/put_etf/{item_id}?query={query}",
                                    request=request,
                                    data=item)

    return RspDetail(items=items)

@etf_router.patch("/patch_etf/{item_id}", summary="PATCH 部分更新etf条目", response_description="返回部分更新的etf条目", response_model=RspDetail[ETFOut])
@trace_request
async def patch_etf(
        request: Request,
        updates: ETFPatchIn,
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query("查询参数", description="查询参数")
):
    """PATCH示例 - 部分更新资源"""

    items = await get_request_items(config.system.etf_url,
                                    path=f"/api/v1/etf/patch_etf/{item_id}?query={query}",
                                    request=request,
                                    data=updates)
    
    return RspDetail(items=items)


@etf_router.get("/get_etf/{item_id}", summary="GET 获取etf条目", response_description="返回etf条目" , response_model=RspDetail[ETFOut])
@trace_request
async def get_etf(
        request: Request,
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query(..., description="查询参数")    # 必填
):
    """GET示例"""

    items = await get_request_items(config.system.etf_url,
                                    path=f"/api/v1/etf/get_etf/{item_id}?query={query}",
                                    request=request
                                    )

    return RspDetail(items=items)



@etf_router.delete("/delete_etf/{item_id}", summary="DELETE 删除etf条目", response_description="返回删除的etf条目" , response_model=RspBase)
@trace_request
async def delete_etf(
        request: Request,
        item_id: str = Path(description="唯一ID", example="item-1"),
        query: str = Query("查询参数", description="查询参数")
):
    """DELETE示例"""

    items = await get_request_items(config.system.etf_url,
                                    path=f"/api/v1/etf/delete_etf/{item_id}?query={query}",
                                    request=request
                                    )

    return RspBase()