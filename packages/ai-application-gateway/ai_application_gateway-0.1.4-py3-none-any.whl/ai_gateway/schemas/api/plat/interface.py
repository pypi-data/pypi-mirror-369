from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional

from ai_gateway.schemas.api.plat.app import AppOut


class InterfaceCreate(BaseModel):
    interface_name: str = Field(..., max_length=100, description="接口名称", examples=["创建ETF条目"])
    path: str = Field(..., max_length=255, description="请求路径", examples=["/api/v1/business/etf/post_etf"])
    method: str = Field(..., max_length=10, description="请求方式", examples=["POST"])
    request_params: dict = Field(..., description="请求参数格式", examples=[{
        "name": "名称",
        "description": "说明"
    }])
    response_json: dict = Field(..., description="响应格式", examples=[{
        "code": 200,
        "message": "success",
        "content": "",
        "items": {
            "item_id": "唯一ID",
            "name": "名称",
            "query": "查询参数",
            "description": "说明",
            "status": "状态",
            "message": "消息"
        }
    }])
    version: str = Field(..., max_length=20, description="版本号", examples=["0.1.0"])
    app_id: str = Field(..., max_length=50, description="应用ID", examples=["app-k76ZbPra5uC6LNhfXG5goe"])
    status: int = Field(..., description="状态", examples=["0"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])


class InterfaceOut(BaseModel):
    id: str = Field(description="唯一id", examples=["interface-VgdXFMkvWd5SHjAkE5hPJQ"])
    created: datetime = Field(description="创建时间", examples=["2025-02-12 14:48:07"])
    updated: datetime = Field(description="更新时间", examples=["2025-02-13 12:13:23"])
    interface_name: str = Field(..., max_length=100, description="接口名称", examples=["创建ETF条目"])
    path: str = Field(..., max_length=255, description="请求路径", examples=["/api/v1/business/etf/post_etf"])
    method: str = Field(..., max_length=10, description="请求方式", examples=["POST"])
    request_params: dict = Field(..., description="请求参数格式", examples=[{
        "name": "名称",
        "description": "说明"
    }])
    response_json: dict = Field(..., description="响应格式", examples=[{
        "code": 200,
        "message": "success",
        "content": "",
        "items": {
            "item_id": "唯一ID",
            "name": "名称",
            "query": "查询参数",
            "description": "说明",
            "status": "状态",
            "message": "消息"
        }
    }])
    version: str = Field(..., max_length=20, description="版本号", examples=["0.1.0"])
    app_id: str = Field(..., max_length=50, description="应用ID", examples=["app-k76ZbPra5uC6LNhfXG5goe"])
    status: int = Field(..., description="状态", examples=["0"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])

    app: AppOut = Field(exclude=True) # 全局隐藏字段

    @computed_field(description="应用名称", examples=["智能客服系统"])
    def app_name(self) -> str:
        return self.app.app_name if self.app else ""

    @computed_field(description="所属公司", examples=["中信证券"])
    def company(self) -> str:
        return self.app.company if self.app else ""

    @computed_field(description="所属部门", examples=["信息技术中心"])
    def department(self) -> str:
        return self.app.department if self.app else ""

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self.app:
            data["app"] = self.app.model_dump()
        return data