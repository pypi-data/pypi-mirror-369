"""
接口授权管理接口
"""
import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.core.middleware import trace_request
from ai_gateway.curd.plat.interface_auth import crud_interface_auth
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail, RspList, RspBase
from ai_gateway.schemas.api.plat.interface_auth import InterfaceAuthCreate, InterfaceAuthOut
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode

interface_auth_router = APIRouter(prefix="/plat/interface_auth")


@interface_auth_router.post("/create_interface_auth", summary="创建新接口授权", response_description="返回创建的新接口授权", response_model=RspDetail[InterfaceAuthOut])
@trace_request
async def create_interface_auth(
    request: Request,
    auth_data: InterfaceAuthCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新接口授权"""
    try:
        new_auth = await crud_interface_auth.create_interface_auth(
            api_key_id=auth_data.api_key_id,
            app_id=auth_data.app_id,
            interface_id=auth_data.interface_id,
            db=db
        )

        # 转换返回结果
        auth_dict = new_auth.model_dump()
        if new_auth.interface:  # 处理关联的interface对象
            auth_dict['interface'] = {
                **new_auth.interface.model_dump(),
                "request_params": json.loads(new_auth.interface.request_params),
                "response_json": json.loads(new_auth.interface.response_json)
            }
            
        return RspDetail(
            content="接口授权创建成功",
            items=InterfaceAuthOut.model_validate(auth_dict).model_dump()
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建接口授权失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_auth_router.get("/get_interface_auth", summary="获取接口授权信息", response_description="返回接口授权信息", response_model=RspDetail[InterfaceAuthOut])
@trace_request
async def get_interface_auth(
    request: Request,
    auth_id: str = Query(description="授权ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定接口授权的详细信息"""
    try:
        auth_info = await crud_interface_auth.get_by_id(auth_id, db)
        if not auth_info:
            return RspDetail.fail(content="接口授权不存在",
                                code=ErrorCode.PLAT_INTERFACE_AUTH_1400)

        # # 将 Interface 模型实例转换为字典，包含关联对象
        # auth_dict = auth_info.model_dump()
        # # 转换为字典SQLModel不会自动包含关联对象app，需要显示手动自己添加
        # if auth_info.app:
        #     auth_dict['app'] = auth_info.app.model_dump()
        # # 将 Interface 模型实例转换为 InterfaceOut
        # auth_out = InterfaceAuthOut.model_validate(auth_dict)
        # app_name = auth_out.app_name
        # # 转换为字典Pydantic的BaseModel会自动包含关联对象app和属性 app_name
        # data = (auth_out.model_dump())

        # 字段转换处理
        auth_dict = auth_info.model_dump()
        if auth_info.interface:  # 处理关联的interface对象
            auth_dict['interface'] = {
                **auth_info.interface.model_dump(),
                "request_params": json.loads(auth_info.interface.request_params),
                "response_json": json.loads(auth_info.interface.response_json)
            }
            
        return RspDetail(items=InterfaceAuthOut.model_validate(auth_dict).model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取接口授权信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_auth_router.get("/get_interface_auths", summary="获取所有接口授权列表", response_description="返回接口授权列表", response_model=RspList[InterfaceAuthOut])
@trace_request
async def get_interface_auths(
    request: Request,
    skip: int = Query(default=0, description="跳过记录数"),
    limit: int = Query(default=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """获取所有接口授权列表"""
    try:
        auths = await crud_interface_auth.get_interface_auths(db, skip=skip, limit=limit)
        return RspList(items=[{
            **auth.model_dump(),
            "interface": {
                **auth.interface.model_dump(),
                "request_params": json.loads(auth.interface.request_params),
                "response_json": json.loads(auth.interface.response_json)
            } if auth.interface else None
        } for auth in auths])
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取接口授权列表失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_auth_router.put("/update_interface_auth", summary="更新接口授权信息", response_description="返回更新后的接口授权信息", response_model=RspDetail[InterfaceAuthOut])
@trace_request
async def update_interface_auth(
    request: Request,
    auth_data: InterfaceAuthCreate,
    auth_id: str = Query(description="授权ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新接口授权信息"""
    try:
        update_data = auth_data.dict(exclude_unset=True)
        updated_auth = await crud_interface_auth.update_interface_auth(
            auth_id=auth_id,
            update_data=update_data,
            db=db
        )
        
        # 字段转换处理
        updated_dict = updated_auth.model_dump()
        if updated_auth.interface:  # 处理关联的interface对象
            updated_dict['interface'] = {
                **updated_auth.interface.model_dump(),
                "request_params": json.loads(updated_auth.interface.request_params),
                "response_json": json.loads(updated_auth.interface.response_json)
            }
            
        return RspDetail(..., items=InterfaceAuthOut.model_validate(updated_dict).model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"更新接口授权信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_auth_router.delete("/fake_delete_interface_auth", summary="假删除接口授权", response_description="返回删除结果", response_model=RspBase)
@trace_request
async def fake_delete_interface_auth(
    request: Request,
    auth_id: str = Query(description="授权ID"),
    db: AsyncSession = Depends(get_db)
):
    """假删除接口授权"""
    try:
        await crud_interface_auth.fake_delete_interface_auth(auth_id, db)
        return RspBase(content="接口授权假删除成功")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"假删除接口授权失败！ status_code：{e.status_code} ｜ detail：{e.detail}")