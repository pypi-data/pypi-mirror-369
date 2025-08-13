from loguru import logger
from pydantic import BaseModel
from typing import Optional, Any, TypeVar, Generic, Sequence, Dict
from math import ceil

T = TypeVar('T')

class RspBase(BaseModel):
    code: int = 200
    message: str = "success"
    content: str = ""

    @classmethod
    def fail(cls, content: str, code: int = 400, message: str = "fail"):
        res=cls(code=code, message=message, content=content)
        logger.error(res.model_dump())
        return res

class RspList(RspBase, Generic[T]):
    items: Optional[Sequence[T]] = None


class RspDict(RspBase, Generic[T]):
    items: Optional[Dict[str, T]] = None

class RspDetail(RspBase, Generic[T]):
    items: Optional[T] = None

class RspListPage(RspBase, Generic[T]):
    code: int = 200
    message: str = "success"
    items: Optional[Sequence[T]] = None
    total: int
    page: int
    size: int
    pages: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pages = ceil(self.total / self.size)

    # @classmethod
    # def success(cls, items: Optional[T] = None, content: str = None, message: str = "success") -> "RspDetail[T]":
    #     return cls(code=200, message=message, content=content, items=items)


