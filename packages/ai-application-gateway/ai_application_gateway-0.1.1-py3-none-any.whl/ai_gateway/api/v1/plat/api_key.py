"""
API Key 管理接口
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.core.middleware import trace_request
from ai_gateway.curd.plat.api_key import crud_api_key
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail, RspList, RspBase
from ai_gateway.schemas.api.plat.api_key import APIKeyCreate, APIKeyOut
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode

api_key_router = APIRouter(prefix="/plat/api_key")


@api_key_router.post("/create_api_key", summary="创建新API密钥", response_description="返回创建的新API密钥", response_model=RspDetail[APIKeyOut])
@trace_request
async def create_api_key(
    request: Request,
    api_key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新API密钥接口"""
    try:
        # 检查API密钥是否已存在
        if await crud_api_key.get_by_code(api_key_data.code, db):
            return RspDetail.fail(content="API密钥已存在", code=ErrorCode.PLAT_API_KEY_1200)

        # 创建新API密钥
        new_api_key = await crud_api_key.create_api_key(
            code=api_key_data.code,
            company=api_key_data.company,
            department=api_key_data.department,
            business=api_key_data.business,
            expires_at=api_key_data.expires_at,
            status=api_key_data.status,
            group=api_key_data.group,
            ip_whitelist=api_key_data.ip_whitelist,
            remark=api_key_data.remark,
            db=db
        )

        return RspDetail(content="API密钥创建成功", items=new_api_key.dict())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建API密钥失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@api_key_router.get("/get_api_key", summary="获取API密钥信息", response_description="返回API密钥信息", response_model=RspDetail[APIKeyOut])
@trace_request
async def get_api_key(
    request: Request,
    api_key_id: str = Query(description="密钥ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定API密钥的详细信息"""
    try:
        api_key_info = await crud_api_key.get_by_id(api_key_id, db)
        if not api_key_info:
            return RspDetail.fail(content="API密钥不存在",
                                code=ErrorCode.PLAT_API_KEY_1201)
        return RspDetail(items=api_key_info)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取API密钥信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@api_key_router.get("/get_api_keys", summary="获取所有API密钥列表", response_description="返回API密钥列表", response_model=RspList[APIKeyOut])
@trace_request
async def get_api_keys(
    request: Request,
    skip: int = Query(default=0, description="跳过记录数"),
    limit: int = Query(default=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """获取所有API密钥列表"""
    try:
        api_keys = await crud_api_key.get_api_keys(db, skip=skip, limit=limit)
        return RspList(items=[api_key.dict() for api_key in api_keys])
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取API密钥列表失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@api_key_router.put("/update_api_key", summary="更新API密钥信息", response_description="返回更新后的API密钥信息", response_model=RspDetail[APIKeyOut])
@trace_request
async def update_api_key(
    request: Request,
    api_key_data: APIKeyCreate,
    api_key_id: str = Query(description="API密钥ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新API密钥信息"""
    try:
        update_data = api_key_data.dict(exclude_unset=True)
        updated_api_key = await crud_api_key.update_api_key(
            api_key_id=api_key_id,
            update_data=update_data,
            db=db
        )
        
        return RspDetail(content="API密钥信息更新成功", items=updated_api_key.dict())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"更新API密钥信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@api_key_router.delete("/fake_delete_api_key", summary="假删除API密钥", response_description="返回删除结果", response_model=RspBase)
@trace_request
async def fake_delete_api_key(
    request: Request,
    api_key_id: str = Query(description="API密钥ID"),
    db: AsyncSession = Depends(get_db)
):
    """假删除API密钥"""
    try:
        await crud_api_key.fake_delete_api_key(api_key_id, db)
        return RspBase(content="API密钥假删除成功")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"假删除API密钥失败！ status_code：{e.status_code} ｜ detail：{e.detail}")