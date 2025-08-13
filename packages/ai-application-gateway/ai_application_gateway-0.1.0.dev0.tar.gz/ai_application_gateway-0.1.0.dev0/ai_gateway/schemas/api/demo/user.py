from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名", examples=["gdx"])
    role: str = Field(..., min_length=1, max_length=50, description="角色", examples=["user"])
    avatar_url: Optional[str] = Field(max_length=255, description="头像URL", examples=["https://example.com/avatar.jpg"])
    age: Optional[int] = Field(description="年龄", examples=[25])
    gender: Optional[str] = Field(max_length=255, description="性别", examples=["男"])
    bio: Optional[str] = Field(description="描述", examples=["我是一名软件工程师"])

class UserOut(BaseModel):
    id: str = Field(description="唯一id", examples=["user-g77hcZVcCMSeK4DbvHHe3K"])
    created: datetime = Field(description="创建时间", examples=["2025-02-12 14:48:07"])
    updated: datetime = Field(description="更新时间", examples=["2025-02-13 12:13:23"])
    username: str = Field(..., min_length=1, max_length=50, description="用户名", examples=["gdx"])
    role: str = Field(..., min_length=1, max_length=50, description="角色", examples=["user"])
    avatar_url: Optional[str] = Field(max_length=255, description="头像URL", examples=["https://example.com/avatar.jpg"])
    age: Optional[int] = Field(description="年龄", examples=[25])
    gender: Optional[str] = Field(max_length=255, description="性别", examples=["男"])
    bio: Optional[str] = Field(description="描述", examples=["我是一名软件工程师"])
    last_login: Optional[datetime] = Field(description="最后登录时间", examples=["2025-02-13 14:48:07"])
    is_online: Optional[bool] = Field(description="在线状态", examples=["true"])
