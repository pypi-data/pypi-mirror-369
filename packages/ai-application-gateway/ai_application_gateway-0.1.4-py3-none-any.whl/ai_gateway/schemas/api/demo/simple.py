from pydantic import BaseModel, Field, ConfigDict


class SimpleIn(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["1"])
    name: str = Field(min_length=1, max_length=50, description="名称", examples=["名称"])
    description: str = Field(max_length=200,  description="说明", examples=["说明"])

class SimplePatchIn(BaseModel):
    description: str = Field(max_length=200,  description="说明", examples=["更新说明"])

class SimpleOut(BaseModel):
    item_id: str = Field(description="ID", examples=["唯一ID"])
    name: str = Field(min_length=1, max_length=50, description="名称", examples=["名称"])
    query: str = Field(max_length=200,  description="查询参数", examples=["查询参数"])
    description: str = Field(max_length=200,  description="说明", examples=["说明"])
    status: str = Field(max_length=200,  description="状态", examples=["状态"])
    message: str = Field(max_length=200,  description="消息", examples=["消息"])
