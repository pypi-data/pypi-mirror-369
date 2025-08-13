from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Text, Integer
from sqlmodel import Field

from ai_gateway.schemas.table.base import AAGBaseModel

class UserRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class User(AAGBaseModel, table=True):
    """用户表 - 存储用户信息"""
    _id_prefix = "user"

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
        sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False,
                         comment="有序自增id，可用于游标分页")
    )

    # 基础信息
    username: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment="用户名"))
    role: str = Field(sa_column=Column(String(20), nullable=False, comment="用户角色"))

    # 用户详情
    avatar_url: Optional[str] = Field(sa_column=Column(String(255), comment="头像URL"))
    age: Optional[int] = Field(sa_column_kwargs={"comment": "年龄"})
    gender: Optional[str] = Field(sa_column=Column(String(10), comment="性别"))
    bio: Optional[str] = Field(sa_column=Column(Text, comment="描述"))
    last_login: Optional[datetime] = Field(sa_column_kwargs={"comment": "最后登录时间"})
    is_online: bool = Field(default=False, sa_column_kwargs={"comment": "在线状态"})

    def dict(self, *args, **kwargs):
        # 首先获取父类的 dict 结果
        base_dict = super().model_dump(*args, **kwargs)

        # 构建用户数据字典
        user_dict = {
            "id": self.id,
            "aid": self.aid,
            "username": self.username,
            "role": self.role,
            "avatar_url": self.avatar_url,
            "age": self.age,
            "gender": self.gender,
            "bio": self.bio,
            "is_online": self.is_online,
            "is_deleted": self.is_deleted,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        # 如果传入了 exclude 参数，排除指定字段
        if "exclude" in kwargs:
            for field in kwargs["exclude"]:
                user_dict.pop(field, None)

        # 如果传入了 include 参数，只保留指定字段
        if "include" in kwargs:
            user_dict = {k: v for k, v in user_dict.items() if k in kwargs["include"]}

        # 合并父类字典和用户字典
        base_dict.update(user_dict)
        return base_dict
