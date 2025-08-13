"""
标准示例：异常 API 路由
"""
from fastapi import APIRouter, HTTPException, Request, Query, Path
from loguru import logger
from starlette.responses import JSONResponse, Response

from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspDetail
from ai_gateway.schemas.api.demo.simple import SimpleIn, SimpleOut, SimplePatchIn
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode

exception_example_router = APIRouter(prefix="/demo/exception_example")


@exception_example_router.post("/fail", summary="API调用错误", response_description="返回API调用失败" , response_model=RspDetail[SimpleOut])
@trace_request
async def fail(
    request: Request,
    item: SimpleIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """API调用错误示例"""

    simple_data = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "created",
        "message": "simple successfully created"
    }

    return RspDetail.fail(content="Demo API调用失败", code=ErrorCode.DEMO_SIMPLE_10000)


@exception_example_router.post("/http_exception", summary="http异常", response_description="返回http异常" , response_model=RspDetail[SimpleOut])
@trace_request
async def http_exception(
    request: Request,
    item: SimpleIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """http异常"""

    simple_data = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "created",
        "message": "simple successfully created"
    }

    raise HTTPException(status_code=HttpStatusCode.BAD_REQUEST_400, detail=f"Demo API调用参数错误http异常")


@exception_example_router.post("/json_response_status_code", summary="额外的状态码_异常测试", response_description="返回额外的状态码_异常测试" , response_model=RspDetail[SimpleOut])
@trace_request
async def json_response_status_code(
    request: Request,
    item: SimpleIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """额外的状态码_异常测试"""

    simple_data = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "created",
        "message": "simple successfully created"
    }

    response = RspDetail.fail(content="Demo API额外的状态码_异常测试", code=ErrorCode.DEMO_SIMPLE_10000)
    return JSONResponse(content=response.model_dump(), status_code=HttpStatusCode.NO_API_PERMISSION_434)


@exception_example_router.post("/update_status_code", summary="更改状态代码_异常测试", response_description="返回更改状态代码_异常测试" , response_model=RspDetail[SimpleOut])
@trace_request
async def update_status_code(
    request: Request,
    response: Response,
    item: SimpleIn,
    item_id: str = Query(default="item-1", description="唯一ID"),
    query: str = Query("查询参数", description="查询参数")
):
    """更改状态代码_异常测试"""

    simple_data = {
        "item_id": item_id,
        "name": item.name,
        "query": query,
        "description": item.description,
        "status": "created",
        "message": "simple successfully created"
    }

    response.status_code = HttpStatusCode.NO_API_PERMISSION_434
    return RspDetail.fail(content="Demo API更改状态代码_异常测试", code=ErrorCode.DEMO_SIMPLE_10000)
