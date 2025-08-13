from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from typing import Optional

from ai_gateway.schemas.api.plat.api_key import APIKeyOut
from ai_gateway.schemas.api.plat.app import AppOut
from ai_gateway.schemas.api.plat.interface import InterfaceOut


class InterfaceAuthCreate(BaseModel):
    api_key_id: str = Field(..., max_length=50, description="密钥ID", examples=["apikey-LZfoEzoGbTEdHjL9G9EDYR"])
    app_id: str = Field(..., max_length=50, description="应用ID", examples=["app-k76ZbPra5uC6LNhfXG5goe"])
    interface_id: str = Field(..., max_length=50, description="接口ID", examples=["interface-VgdXFMkvWd5SHjAkE5hPJQ"])


class InterfaceAuthOut(BaseModel):
    id: str = Field(description="唯一id", examples=["auth-aWDuv3UwZmuxrJ4h24j8gd"])
    created: datetime = Field(description="创建时间", examples=["2025-02-12 14:48:07"])
    updated: datetime = Field(description="更新时间", examples=["2025-02-13 12:13:23"])
    api_key_id: str = Field(..., max_length=50, description="密钥ID", examples=["apikey-LZfoEzoGbTEdHjL9G9EDYR"])
    app_id: str = Field(..., max_length=50, description="应用ID", examples=["app-k76ZbPra5uC6LNhfXG5goe"])
    interface_id: str = Field(..., max_length=50, description="接口ID", examples=["interface-VgdXFMkvWd5SHjAkE5hPJQ"])

    api_key: APIKeyOut = Field(exclude=True) # 全局隐藏字段

    @computed_field(description="密钥字符串", examples=["xxx"])
    def code(self) -> str:
        return self.api_key.code if self.api_key else ""

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

    interface: InterfaceOut = Field(exclude=True) # 全局隐藏字段

    @computed_field(description="接口名称", examples=["创建ETF条目"])
    def interface_name(self) -> str:
        return self.interface.interface_name if self.interface else ""

    @computed_field(description="请求路径", examples=["/api/v1/business/etf/post_etf"])
    def path(self) -> str:
        return self.interface.path if self.interface else ""

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self.api_key:
            data["api_key"] = self.api_key.model_dump()
        if self.app:
            data["app"] = self.app.model_dump()
        if self.interface:
            data["interface"] = self.interface.model_dump()
        return data