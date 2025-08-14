"""
接口日志管理接口
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.config import config
from ai_gateway.curd.plat.interface_log import crud_interface_log
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail

from ai_gateway.schemas.api.plat.interface_log import InterfaceLogCreate, InterfaceLogOut
from ai_gateway.service.plat.interface_log import interface_log_save

interface_log_router = APIRouter(prefix="/plat/interface_log")


@interface_log_router.post("/create_interface_log", summary="创建新接口日志", response_description="返回创建的新接口日志", response_model=RspDetail[InterfaceLogOut])
# @trace_request
async def create_interface_log(
    request: Request,
    log_data: InterfaceLogCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新接口授权"""
    try:

        # 转换字典为JSON字符串
        request_params_str = json.dumps(log_data.request_params, ensure_ascii=False)
        response_json_str = json.dumps(log_data.response_json, ensure_ascii=False)

        new_interface_log = await crud_interface_log.create_log(
            user_id=log_data.user_id,
            request_id=log_data.request_id,
            code=log_data.code,
            url=log_data.url,
            base_url=log_data.base_url,
            path=log_data.path,
            method=log_data.method,
            request_params=request_params_str,  # 传入字符串
            ip=log_data.ip,
            port=log_data.port,
            request_at=log_data.request_at,
            response_json=response_json_str,    # 传入字符串
            response_time=log_data.response_time,
            status_code=log_data.status_code,
            created=log_data.created,
            updated=log_data.updated,
            timestamp=log_data.timestamp,
            db=db
        )

        # 将数据库返回的字符串转换回字典
        interface_log_dict = new_interface_log.model_dump()
        interface_log_dict.update({
            "request_params": log_data.request_params,
            "response_json": log_data.response_json
        })

        if config.interface_log.elasticsearch:  # 日志写入 ES
            interface_log_out = await interface_log_save(log_data)

        return RspDetail(content="接口日志创建成功", items=InterfaceLogOut.model_validate(interface_log_dict).model_dump())
        # return RspDetail(content="接口日志创建成功", items=interface_log_out)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建接口日志失败！ status_code：{e.status_code} ｜ detail：{e.detail}")
