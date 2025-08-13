from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, Integer, String
from ai_gateway.utils import uuid

class AAGBaseModel(SQLModel):
    """Base model（需作为抽象类继承）"""
    __abstract__ = True  # 关键！声明为抽象基类，避免自身映射为表
    _id_prefix = ""

    @property
    def generate_id(self) -> str:
        return uuid.generator(self._id_prefix)()

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = self.generate_id

    id: str = Field(
        sa_column=lambda: Column(String(50), unique=True, index=True, nullable=False, comment="随机生成唯一id")
    )

    aid: int = Field(
        sa_column=lambda: Column(Integer, primary_key=True, default=None, autoincrement=True, nullable=False, comment="有序自增id，可用于游标分页")
    )
    created: datetime = Field(
        default_factory=datetime.now,
        sa_column=lambda: Column(DateTime, nullable=False, comment="创建时间")
    )
    updated: datetime = Field(
        default_factory=datetime.now,
        sa_column=lambda: Column(DateTime, onupdate=datetime.now, nullable=False, comment="更新时间"),
    )
    is_deleted: int = Field(
        sa_column=lambda: Column(Integer, default=0,nullable=False, comment="删除标示，0:未删除，1:已删除")
    )

    def time_to_format(self, format_str: str = "%Y-%m-%d %H:%M"):
        if hasattr(self, "created"):
            self.created: str = self.created.strftime(format_str)
        if hasattr(self, "updated"):
            self.updated: str = self.updated.strftime(format_str)
        return self

    def format_dict(
        self,
        include: list = None,
        exclude: list = None,
    ):
        if not exclude:
            exclude = []
        exclude.append("_sa_instance_state")

        return {k: v for k, v in self if (include and k in include) or k not in exclude}
