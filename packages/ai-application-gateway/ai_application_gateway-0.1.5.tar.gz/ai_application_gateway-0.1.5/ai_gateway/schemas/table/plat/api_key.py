from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlmodel import Field, Relationship

from ai_gateway.schemas.table.base import AAGBaseModel

from ai_gateway.utils import uuid


class API_KEY(AAGBaseModel, table=True):
    """API密钥表"""
    _id_prefix = "apikey"
    __table_args__ = {'extend_existing': True}  # 允许扩展已有表

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
            sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False, comment="有序自增id，可用于游标分页")
        )
    # 基础信息
    code: str = Field(sa_column=Column(String(255), nullable=False, comment="密钥字符串"))
    company: str = Field(sa_column=Column(String(100), nullable=False, comment="授权公司名称"))
    department: str = Field(sa_column=Column(String(100), nullable=True, comment="授权部门名称"))
    group: str = Field(sa_column=Column(String(100), nullable=True, comment="授权业务组名称"))
    business: str = Field(sa_column=Column(String(100), nullable=False, comment="授权业务应用名称"))
    expires_at: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="过期时间"))
    status: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="API 密钥状态，0:启用，1:禁用"))
    ip_whitelist: str = Field(sa_column=Column(Text, nullable=True, comment="IP白名单"))
    remark: Optional[str] = Field(sa_column=Column(String(500), comment="备注"))
    created: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="创建时间"))
    updated: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="更新时间"))
    is_deleted: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="删除标示，0:未删除，1:已删除"))

    # 添加反向关系
    interface_auths: List["InterfaceAuth"] = Relationship(
        back_populates="api_key"
    )
