from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class AppCreate(BaseModel):
    app_name: str = Field(..., max_length=255, description="应用名称", examples=["智能客服系统"])
    app_url: str = Field(..., max_length=255, description="应用站点地址", examples=["http://www.citicsinfo.com"])
    company: str = Field(..., max_length=100, description="所属公司", examples=["中信证券"])
    department: str = Field(..., max_length=100, description="所属部门", examples=["信息技术中心"])
    status: int = Field(..., description="状态", examples=["0"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])


class AppOut(BaseModel):
    id: str = Field(description="唯一id", examples=["app-k76ZbPra5uC6LNhfXG5goe"])
    created: datetime = Field(description="创建时间", examples=["2025-02-12 14:48:07"])
    updated: datetime = Field(description="更新时间", examples=["2025-02-13 12:13:23"])
    app_name: str = Field(..., max_length=255, description="应用名称", examples=["智能客服系统"])
    app_url: str = Field(..., max_length=255, description="应用站点地址", examples=["http://www.citicsinfo.com"])
    company: str = Field(..., max_length=100, description="所属公司", examples=["中信证券"])
    department: str = Field(..., max_length=100, description="所属部门", examples=["信息技术中心"])
    status: int = Field(..., description="状态", examples=["0"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])