from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime
from sqlmodel import Field, Relationship

from ai_gateway.schemas.table.base import AAGBaseModel


class App(AAGBaseModel, table=True):
    """应用表"""
    _id_prefix = "app"
    __table_args__ = {'extend_existing': True}  # 允许扩展已有表

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )
    
    aid: int = Field(
            sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False, comment="有序自增id，可用于游标分页")
        )

    # 基础信息
    app_name: str = Field(sa_column=Column(String(255), nullable=False, comment="应用名称"))
    app_url: str = Field(sa_column=Column(String(255), nullable=False, comment="应用站点地址"))
    company: str = Field(sa_column=Column(String(100), nullable=False, comment="所属公司"))
    department: str = Field(sa_column=Column(String(100), nullable=False, comment="所属部门"))
    status: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="应用状态，0:运行中，1:维护中，2:已停止"))
    remark: Optional[str] = Field(sa_column=Column(String(500), comment="备注"))
    created: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="创建时间"))
    updated: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="更新时间"))
    is_deleted: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="删除标示，0:未删除，1:已删除"))

    # 添加反向关系
    interfaces: List["Interface"] = Relationship(
        back_populates="app"
    )
    interface_auths: List["InterfaceAuth"] = Relationship(
        back_populates="app"
    )
