from datetime import timedelta, datetime, date
from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel, conint


# 排序类型
class YearOrder(Enum):
    DESC = 1
    ASC = 2

# 获取A股分红指标数据
class DvdIndListed(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["600862.SH"]])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 获取A股历年分红明细数据
class DvdHis(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["600862.SH"]])
    start_year: Optional[int] | None = Field(default=None, description="开始年度", examples=["2015"])
    end_year: Optional[int] | None = Field(default=None, description="截止年度", examples=["2024"])
    order: YearOrder = Field(default=YearOrder.DESC, description="年度排序，1-倒序、2-正序", examples=["1"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 获取A股行业分类数据
class IndustriesClass(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["600862.SH"]])
    indu_class_type: Optional[int] | None = Field(default=0, description="行业分类类型，0:中信行业分类，1:申万行业分类", examples=["0"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])