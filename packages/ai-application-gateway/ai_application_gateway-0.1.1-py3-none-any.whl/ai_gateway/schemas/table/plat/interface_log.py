from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Float
from sqlmodel import Field, Relationship
from sqlalchemy.dialects.mysql import DATETIME, TIMESTAMP, DECIMAL, TEXT, LONGTEXT

from ai_gateway.schemas.table.base import AAGBaseModel


class Interface_log(AAGBaseModel, table=True):
    """接口表"""
    _id_prefix = "log"
    __table_args__ = {'extend_existing': True}  # 允许扩展已有表

    id: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
        sa_column=Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False,
                         comment="有序自增id，可用于游标分页")
    )

    user_id: str = Field(sa_column=Column(String(50), nullable=False, comment="用户ID"))
    request_id: str = Field(sa_column=Column(String(255), nullable=False, comment="请求ID"))
    code: str = Field(sa_column=Column(String(500), nullable=False, comment="密钥字符串"))
    url: str = Field(sa_column=Column(TEXT, nullable=False, comment="请求地址"))
    base_url: str = Field(sa_column=Column(String(255), nullable=False, comment="应用站点地址"))
    path: str = Field(sa_column=Column(String(255), nullable=False, comment="请求路径"))
    method: str = Field(sa_column=Column(String(10), nullable=False, comment="请求方式"))
    request_params: str = Field(sa_column=Column(Text, nullable=True, comment="请求参数格式"))
    ip: str = Field(sa_column=Column(String(50), nullable=False, comment="IP地址"))
    port: int = Field(sa_column=Column(Integer, nullable=False, comment="端口"))
    request_at: Optional[datetime] = Field(
        sa_column=Column(
            DATETIME(fsp=6),  # 精确到毫秒
            nullable=False,
            comment="请求时间(带时区，支持毫秒精度)"
        )
    )
    response_json: str = Field(sa_column=Column(LONGTEXT, nullable=False, comment="响应格式"))
    response_time: float = Field(sa_column=Column(Float, nullable=False, comment="响应时间"))
    status_code: int = Field(sa_column=Column(Integer, nullable=False, comment="响应状态码"))
    created: Optional[datetime] = Field(
        sa_column=Column(
            DATETIME(fsp=6),  # 精确到毫秒
            nullable=False,
            comment="日志创建时间(带时区，支持毫秒精度)"
        )
    )
    updated: Optional[datetime] = Field(
        sa_column=Column(
            DATETIME(fsp=6),  # 精确到毫秒
            nullable=False,
            comment="日志更新时间(带时区，支持毫秒精度)"
        )
    )
    timestamp: float = Field(sa_column=Column(DECIMAL(16, 6), nullable=False, comment="时间戳"))
    is_deleted: int = Field(sa_column=Column(Integer, default=0, nullable=False, comment="删除标示，0:未删除，1:已删除"))