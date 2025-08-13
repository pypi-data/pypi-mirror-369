from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlmodel import Field, Relationship

from ai_gateway.schemas.table.base import AAGBaseModel
from ai_gateway.schemas.table.plat.app import App


class Interface(AAGBaseModel, table=True):
    """接口表"""
    _id_prefix = "interface"
    __table_args__ = {'extend_existing': True}  # 允许扩展已有表

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
        sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False,
                         comment="有序自增id，可用于游标分页")
    )

    # 基础信息
    interface_name: str = Field(sa_column=Column(String(100), nullable=False, comment="接口名称"))
    path: str = Field(sa_column=Column(String(255), nullable=False, comment="请求路径"))
    method: str = Field(sa_column=Column(String(10), nullable=False, comment="请求方式"))
    request_params: str = Field(sa_column=Column(Text, nullable=True, comment="请求参数格式"))
    response_json: str = Field(sa_column=Column(Text, nullable=False, comment="响应格式"))
    version: str = Field(sa_column=Column(String(20), nullable=False, comment="版本号"))
    
    app_id: str = Field(
        sa_column=Column(
            String(50), 
            ForeignKey("app.id", ondelete="CASCADE"), 
            nullable=False, 
            comment="应用ID"
        )
    )

    status: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="接口状态，0:运行中，1:维护中，2:已停止"))
    remark: Optional[str] = Field(sa_column=Column(String(500), comment="备注"))
    created: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="创建时间"))
    updated: datetime = Field(default_factory=datetime.now,
                              sa_column=Column(DateTime, nullable=False, comment="更新时间"))
    is_deleted: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="删除标示，0:未删除，1:已删除"))

    # 添加关系
    app: Optional[App] = Relationship(
        back_populates="interfaces",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self.app:
            data["app"] = self.app.model_dump()
        return data

    # 添加反向关系
    interface_auths: List["InterfaceAuth"] = Relationship(
        back_populates="interface"
    )
