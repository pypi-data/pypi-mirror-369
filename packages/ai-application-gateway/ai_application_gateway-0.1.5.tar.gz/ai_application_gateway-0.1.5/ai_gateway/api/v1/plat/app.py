"""
应用管理接口
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.core.middleware import trace_request
from ai_gateway.curd.plat.app import crud_app
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail, RspList, RspBase
from ai_gateway.schemas.api.plat.app import AppCreate, AppOut
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode
from ai_gateway.schemas.table.plat.interface_auth import InterfaceAuth

app_router = APIRouter(prefix="/plat/app")


@app_router.post("/create_app", summary="创建新应用", response_description="返回创建的新应用", response_model=RspDetail[AppOut])
@trace_request
async def create_app(
    request: Request,
    app_data: AppCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新应用接口"""
    try:
        # 创建新应用
        new_app = await crud_app.create_app(
            app_name=app_data.app_name,
            app_url=app_data.app_url,
            company=app_data.company,
            department=app_data.department,
            status=app_data.status,
            remark=app_data.remark,
            db=db
        )

        return RspDetail(content="应用创建成功", items=new_app.dict())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建应用失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@app_router.get("/get_app", summary="获取应用信息", response_description="返回应用信息", response_model=RspDetail[AppOut])
@trace_request
async def get_app(
    request: Request,
    app_id: str = Query(description="应用ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定应用的详细信息"""
    try:
        app_info = await crud_app.get_by_id(app_id, db)

        if not app_info:
            return RspDetail.fail(content="应用不存在",
                                code=ErrorCode.PLAT_APP_1001)
        return RspDetail(items=app_info)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取应用信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@app_router.get("/get_apps", summary="获取所有应用列表", response_description="返回应用列表", response_model=RspList[AppOut])
@trace_request
async def get_apps(
    request: Request,
    skip: int = Query(default=0, description="跳过记录数"),
    limit: int = Query(default=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """获取所有应用列表"""
    try:
        apps = await crud_app.get_apps(db, skip=skip, limit=limit)
        return RspList(items=[app.dict() for app in apps])
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取应用列表失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@app_router.put("/update_app", summary="更新应用信息", response_description="返回更新后的应用信息", response_model=RspDetail[AppOut])
@trace_request
async def update_app(
    request: Request,
    app_data: AppCreate,
    app_id: str = Query(description="应用ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新应用信息"""
    try:
        update_data = app_data.dict(exclude_unset=True)
        updated_app = await crud_app.update_app(
            app_id=app_id,
            update_data=update_data,
            db=db
        )
        
        return RspDetail(content="应用信息更新成功", items=updated_app.dict())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"更新应用信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@app_router.delete("/fake_delete_app", summary="假删除应用", response_description="返回删除结果", response_model=RspBase)
@trace_request
async def fake_delete_app(
    request: Request,
    app_id: str = Query(description="应用ID"),
    db: AsyncSession = Depends(get_db)
):
    """假删除应用"""
    try:
        await crud_app.fake_delete_app(app_id, db)
        return RspBase(content="应用假删除成功")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"假删除应用失败！ status_code：{e.status_code} ｜ detail：{e.detail}")