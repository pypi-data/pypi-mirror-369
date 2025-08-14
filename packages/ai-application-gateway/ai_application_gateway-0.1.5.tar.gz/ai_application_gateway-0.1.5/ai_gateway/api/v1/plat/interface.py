"""
接口管理接口
"""
import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.core.middleware import trace_request
from ai_gateway.curd.plat.interface import crud_interface
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail, RspList, RspBase
from ai_gateway.schemas.api.plat.interface import InterfaceCreate, InterfaceOut
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode

interface_router = APIRouter(prefix="/plat/interface")


@interface_router.post("/create_interface", summary="创建新接口", response_description="返回创建的新接口", response_model=RspDetail[InterfaceOut])
@trace_request
async def create_interface(
    request: Request,
    interface_data: InterfaceCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新接口"""
    try:
        # 转换字典为JSON字符串
        request_params_str = json.dumps(interface_data.request_params, ensure_ascii=False)
        response_json_str = json.dumps(interface_data.response_json, ensure_ascii=False)
        
        new_interface = await crud_interface.create_interface(
            interface_name=interface_data.interface_name,
            path=interface_data.path,
            method=interface_data.method,
            request_params=request_params_str,  # 传入字符串
            response_json=response_json_str,    # 传入字符串
            version=interface_data.version,
            app_id=interface_data.app_id,
            status=interface_data.status,
            remark=interface_data.remark,
            db=db
        )

        # 将数据库返回的字符串转换回字典
        interface_dict = new_interface.model_dump()
        interface_dict.update({
            "request_params": interface_data.request_params,
            "response_json": interface_data.response_json
        })
        return RspDetail(content="接口创建成功", items=InterfaceOut.model_validate(interface_dict).model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建接口失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_router.get("/get_interface", summary="获取接口信息", response_description="返回接口信息", response_model=RspDetail[InterfaceOut])
@trace_request
async def get_interface(
    request: Request,
    interface_id: str = Query(description="接口ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取指定接口的详细信息"""
    try:
        interface_info = await crud_interface.get_by_id(interface_id, db)
        if not interface_info:
            return RspDetail.fail(content="接口不存在",
                                code=ErrorCode.PLAT_INTERFACE_1101)

        # # # 将 Interface 模型实例转换为字典，因为重写了 model_dump() 会包含关联对象app
        # interface_dict = interface_info.model_dump()
        # # 不过，转换为字典SQLModel不会自动包含关联对象app，需要显示手动自己添加
        # if interface_info.app:
        #     interface_dict['app'] = interface_info.app.model_dump()
        # # 将 Interface 模型实例转换为 InterfaceOut，将字典转换为Pydantic模型
        # interface_out = InterfaceOut.model_validate(interface_dict)
        # app_name = interface_out.app_name
        # # 转换为字典Pydantic的BaseModel会自动包含关联对象app和属性 app_name
        # data = interface_out.model_dump()


        # app_name = interface_info.app.app_name
 
        # 将数据库返回的字符串转换回字典
        interface_dict = interface_info.model_dump()
        interface_dict.update({
            "request_params": json.loads(interface_info.request_params),
            "response_json": json.loads(interface_info.response_json)
        })
        return RspDetail(content="接口创建成功", items=InterfaceOut.model_validate(interface_dict).model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取接口信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_router.get("/get_interfaces", summary="获取所有接口列表", response_description="返回接口列表", response_model=RspList[InterfaceOut])
@trace_request
async def get_interfaces(
    request: Request,
    skip: int = Query(default=0, description="跳过记录数"),
    limit: int = Query(default=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """获取所有接口列表"""
    try:
        interfaces = await crud_interface.get_interfaces(db, skip=skip, limit=limit)
        return RspList(items=[
            InterfaceOut.model_validate({
                **interface.model_dump(),
                "request_params": json.loads(interface.request_params),
                "response_json": json.loads(interface.response_json)
            }).model_dump()
            for interface in interfaces
        ])
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取接口列表失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_router.put("/update_interface", summary="更新接口信息", response_description="返回更新后的接口信息", response_model=RspDetail[InterfaceOut])
@trace_request
async def update_interface(
    request: Request,
    interface_data: InterfaceCreate,
    interface_id: str = Query(description="接口ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新接口信息"""
    try:
        # 在update_data中添加格式转换
        update_data = interface_data.dict(exclude_unset=True)
        if 'request_params' in update_data:
            update_data['request_params'] = json.dumps(update_data['request_params'], ensure_ascii=False)
        if 'response_json' in update_data:
            update_data['response_json'] = json.dumps(update_data['response_json'], ensure_ascii=False)
        
        updated_interface = await crud_interface.update_interface(
            interface_id=interface_id,
            update_data=update_data,
            db=db
        )
        
        # 转换返回结果
        updated_dict = updated_interface.model_dump()
        if updated_interface.app:  # 添加关联对象处理
            updated_dict['app'] = updated_interface.app.model_dump()
        updated_dict.update({
            "request_params": interface_data.request_params,
            "response_json": interface_data.response_json
        })
        return RspDetail(content="接口信息更新成功", items=InterfaceOut.model_validate(updated_dict).model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"更新接口信息失败！ status_code：{e.status_code} ｜ detail：{e.detail}")


@interface_router.delete("/fake_delete_interface", summary="假删除接口", response_description="返回删除结果", response_model=RspBase)
@trace_request
async def fake_delete_interface(
    request: Request,
    interface_id: str = Query(description="接口ID"),
    db: AsyncSession = Depends(get_db)
):
    """假删除接口"""
    try:
        await crud_interface.fake_delete_interface(interface_id, db)
        return RspBase(content="接口假删除成功")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"假删除接口失败！ status_code：{e.status_code} ｜ detail：{e.detail}")