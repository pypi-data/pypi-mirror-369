from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class APIKeyCreate(BaseModel):
    code: str = Field(..., max_length=255, description="密钥字符串", examples=["xxx"])
    company: str = Field(..., max_length=100, description="授权公司名称", examples=["中信证券"])
    department: str = Field(..., max_length=100, description="授权部门名称", examples=["协同部"])
    group: Optional[str] = Field(max_length=100, description="授权业务组名称", examples=["业务组"])
    business: str = Field(..., max_length=100, description="授权业务应用名称", examples=["业务应用"])
    expires_at: datetime = Field(..., description="过期时间", examples=["2025-02-12 14:48:07"])
    status: int = Field(..., description="状态", examples=["0"])
    ip_whitelist: Optional[str] = Field(description="IP白名单", examples=["192.168.1.1"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])

class APIKeyOut(BaseModel):
    id: str = Field(description="唯一id", examples=["apikey-LZfoEzoGbTEdHjL9G9EDYR"])
    created: datetime = Field(description="创建时间", examples=["2025-02-12 14:48:07"])
    updated: datetime = Field(description="更新时间", examples=["2025-02-13 12:13:23"])
    code: str = Field(..., max_length=255, description="密钥字符串", examples=["xxx"])
    company: str = Field(..., max_length=100, description="授权公司名称", examples=["中信证券"])
    department: str = Field(..., max_length=100, description="授权部门名称", examples=["协同部"])
    group: Optional[str] = Field(max_length=100, description="授权业务组名称", examples=["业务组"])
    business: str = Field(..., max_length=100, description="授权业务应用名称", examples=["业务应用"])
    expires_at: datetime = Field(..., description="过期时间", examples=["2025-02-12 14:48:07"])
    status: int = Field(..., description="状态", examples=["0"])
    ip_whitelist: Optional[str] = Field(description="IP白名单", examples=["192.168.1.1"])
    remark: Optional[str] = Field(max_length=500, description="备注", examples=[""])