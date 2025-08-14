from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlmodel import Field, Relationship

from ai_gateway.schemas.table.base import AAGBaseModel
from ai_gateway.schemas.table.plat.app import App
from ai_gateway.schemas.table.plat.api_key import API_KEY
from ai_gateway.schemas.table.plat.interface import Interface


class InterfaceAuth(AAGBaseModel, table=True):
    """接口授权表"""
    _id_prefix = "auth"
    __table_args__ = {'extend_existing': True}  # 允许扩展已有表

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
        sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False,
                         comment="有序自增id，可用于游标分页")
    )

    # 基础信息
    api_key_id: str = Field(
        sa_column=Column(
            String(50), 
            ForeignKey("api_key.id", ondelete="CASCADE"),
            nullable=False, 
            comment="密钥ID"
        )
    )

    app_id: str = Field(
        sa_column=Column(
            String(50), 
            ForeignKey("app.id", ondelete="CASCADE"),
            nullable=False, 
            comment="应用ID"
        )
    )
    interface_id: str = Field(
        sa_column=Column(
            String(50), 
            ForeignKey("interface.id", ondelete="CASCADE"),
            nullable=False, 
            comment="接口ID"
        )
    )
    created: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="创建时间"))
    updated: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="更新时间"))
    is_deleted: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="删除标示，0:未删除，1:已删除"))

    # 添加关系
    api_key: Optional[API_KEY] = Relationship(
        back_populates="interface_auths",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    app: Optional[App] = Relationship(
        back_populates="interface_auths",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    interface: Optional[Interface] = Relationship(
        back_populates="interface_auths",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self.api_key:
            data["api_key"] = self.api_key.model_dump()
        if self.app:
            data["app"] = self.app.model_dump()
        if self.interface:
            data["interface"] = self.interface.model_dump()
        return data