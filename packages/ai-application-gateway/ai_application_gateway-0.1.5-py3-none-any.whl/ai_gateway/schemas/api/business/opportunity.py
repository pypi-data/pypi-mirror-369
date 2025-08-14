from datetime import timedelta, datetime, date
from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel, conint


# 商机类型
class AnnouncementType(Enum):
    ALL = 0 # 全部
    FINANCE = 1 # 委托理财
    REDUCTION = 2 # 股东减持

# 上市公司筛选方式
class StockFilterType(Enum):
    INCLUDE = 0 # 包含
    NOT_INCLUDE = 1 # 不包含

# 排序类型
class AnnouncementOrder(Enum):
    DESC = 1
    ASC = 2

# 商机查询类型
class CompAnnQueryType(Enum):
    ALL = 0 #  全部
    ALL_COLLECT = 1 #  全部，并返回收藏状态字段is_collect，0-未收藏、1-已收藏
    COLLECT = 2  # 已收藏

# 上市公司是否退市
class AShareDelistType(Enum):
    NOT_DELIST = 0 #  否
    DELIST = 1 # 是
    ALL = 2 # 全部

# 商机（一级是公司+二级是公告）
class CompAnn(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    query_type: CompAnnQueryType = Field(default=CompAnnQueryType.ALL_COLLECT, description="查询类型：0-全部、1-全部，并返回收藏状态字段、2-已收藏", examples=["1"])
    ann_type: AnnouncementType = Field(default=AnnouncementType.ALL, description="商机类型：0-全部、1-委托理财、2-股东减持", examples=["0"])
    start_time: Optional[date] | None = Field(default=(datetime.now() - timedelta(days=7)).date(), description="开始时间", examples=["2025-04-01"])
    end_time: Optional[date] | None = Field(default=datetime.now().date(), description="结束时间", examples=["2025-04-30"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["002566.SZ", "002582.SZ"]])
    stock_filter_type: StockFilterType = Field(default=StockFilterType.INCLUDE, description="上市公司筛选方式：0-包含、1-不包括", examples=["0"])
    list_board: Optional[list] | None = Field(default=None, description="上市板块：主板、科创板、创业板、北交所，数组传递多个值", examples=[["主板", "创业板", "科创板", "北证"]])
    region: Optional[list] | None = Field(default=None, description="地区，如：华东、华南、华北、华中、西南、西北、东北、跨境，数组传递多个值", examples=[["跨境", "华北"]])
    is_delist: AShareDelistType = Field(default=AShareDelistType.NOT_DELIST, description="是否退市：0-否、1-是、2-全部", examples=["0"])
    order: AnnouncementOrder = Field(default=AnnouncementOrder.DESC, description="时间排序，1-倒序、2-正序", examples=["1"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 商机（一级是公司+二级是公告），固定传理财或减持
class CompAnnSub(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    query_type: CompAnnQueryType = Field(default=CompAnnQueryType.ALL_COLLECT, description="查询类型：0-全部、1-全部，并返回收藏状态字段、2-已收藏", examples=["1"])
    start_time: Optional[date] | None = Field(default=(datetime.now() - timedelta(days=7)).date(), description="开始时间", examples=["2025-04-01"])
    end_time: Optional[date] | None = Field(default=datetime.now().date(), description="结束时间", examples=["2025-04-30"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["002566.SZ", "002582.SZ"]])
    stock_filter_type: StockFilterType = Field(default=StockFilterType.INCLUDE, description="上市公司筛选方式：0-包含、1-不包括", examples=["0"])
    list_board: Optional[list] | None = Field(default=None, description="上市板块：主板、科创板、创业板、北交所，数组传递多个值", examples=[["主板", "创业板", "科创板", "北证"]])
    region: Optional[list] | None = Field(default=None, description="地区，如：华东、华南、华北、华中、西南、西北、东北、跨境，数组传递多个值", examples=[["跨境", "华北"]])
    is_delist: AShareDelistType = Field(default=AShareDelistType.NOT_DELIST, description="是否退市：0-否、1-是、2-全部", examples=["0"])
    order: AnnouncementOrder = Field(default=AnnouncementOrder.DESC, description="时间排序，1-倒序、2-正序", examples=["1"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 商机（公告）
class Announcement(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    ann_type: AnnouncementType = Field(default=AnnouncementType.ALL, description="商机类型：0-全部、1-委托理财、2-股东减持", examples=["0"])
    start_time: Optional[date] | None = Field(default=None, description="开始时间", examples=["2025-04-01"])
    end_time: Optional[date] | None = Field(default=None, description="结束时间", examples=["2025-04-30"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["002566.SZ", "002582.SZ"]])
    stock_filter_type: StockFilterType = Field(default=StockFilterType.INCLUDE, description="上市公司筛选方式：0-包含、1-不包括", examples=["0"])
    list_board: Optional[list] | None = Field(default=None, description="上市板块：主板、科创板、创业板、北交所，数组传递多个值", examples=[["主板", "创业板", "科创板", "北证"]])
    region: Optional[list] | None = Field(default=None, description="地区，如：华东、华南、华北、华中、西南、西北、东北、跨境，数组传递多个值", examples=[["跨境", "华北"]])
    is_delist: AShareDelistType = Field(default=AShareDelistType.NOT_DELIST, description="是否退市：0-否、1-是、2-全部", examples=["0"])
    order: AnnouncementOrder = Field(default=AnnouncementOrder.DESC, description="时间排序，1-倒序、2-正序", examples=["1"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 商机（公告），固定传理财或减持
class AnnouncementSub(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    start_time: Optional[date] | None = Field(default=None, description="开始时间", examples=["2025-04-01"])
    end_time: Optional[date] | None = Field(default=None, description="结束时间", examples=["2025-04-30"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["002566.SZ", "002582.SZ"]])
    stock_filter_type: StockFilterType = Field(default=StockFilterType.INCLUDE, description="上市公司筛选方式：0-包含、1-不包括", examples=["0"])
    list_board: Optional[list] | None = Field(default=None, description="上市板块：主板、科创板、创业板、北交所，数组传递多个值", examples=[["主板", "创业板", "科创板", "北证"]])
    region: Optional[list] | None = Field(default=None, description="地区，如：华东、华南、华北、华中、西南、西北、东北、跨境，数组传递多个值", examples=[["跨境", "华北"]])
    is_delist: AShareDelistType = Field(default=AShareDelistType.NOT_DELIST, description="是否退市：0-否、1-是、2-全部", examples=["0"])
    order: AnnouncementOrder = Field(default=AnnouncementOrder.DESC, description="时间排序，1-倒序、2-正序", examples=["1"])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 上市公司是否有公告
class AShareExistAnns(Enum):
    NOT_EXIST = 0 # 没有公告
    EXIST = 1 # 有公告
    ALL = 2 # 全部

# 搜索股票
class StockSearch(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    keyword: str = Field(..., description="股票名称、股票代码、简拼、全拼，支持模糊查询", examples=["芯海科技、688595、xhkj、xinhaikeji、xin hai ke ji"])
    exist_anns: AShareExistAnns = Field(default=AShareExistAnns.ALL, description="上市公司是否有公告：0-否、1-是、2-全部", examples=["2"])
    size: conint(gt=0) | None = Field(default=5, description="返回条数(必须大于0)", examples=["5"])

# 搜索股票扩展查询类型
class StockSearchExQueryType(Enum):
    NOT = 0 # 0-不返回任何扩展状态
    IS_COLLECT = 1 # 1-返回个股收藏状态字段is_collect、
    IS_SUBSCRIBE = 2  # 2-返回个股订阅状态字段is_subscribe

# 搜索股票扩展（收藏或订阅条件）
class StockSearchEx(StockSearch):
    query_type: StockSearchExQueryType = Field(default=StockSearchExQueryType.NOT, description="查询类型：0-不返回任何扩展状态、1-返回个股收藏状态字段is_collect、2-返回个股订阅状态字段is_subscribe", examples=["0"])

# 个股查询类型
class AShareQueryType(Enum):
    ALL = 0 #  全部
    ALL_COLLECT = 1 #  全部，并返回收藏状态字段is_collect，0-未收藏、1-已收藏
    COLLECT = 2  # 已收藏
    NOT_COLLECT = 3 # 未收藏
    ALL_SUBSCRIBE = 4 #  全部，并返回订阅状态字段is_subscribe，0-未订阅、1-已订阅
    SUBSCRIBE = 5  # 已订阅
    NOT_SUBSCRIBE = 6 # 未订阅

# 个股数据
class AShare(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, description="用户ID", examples=["T021530"])
    query_type: AShareQueryType = Field(default=AShareQueryType.ALL, description="查询类型：0-全部、1-全部，并返回收藏状态字段、2-已收藏、3-未收藏、4-全部，并返回订阅状态字段、5-已订阅、6-未订阅", examples=["0"])
    keyword: str = Field(default=None, description="股票名称、股票代码、简拼、全拼，支持模糊查询", examples=["益盛药业"])
    keyword_size: conint(gt=0, lt=201) | None = Field(default=20, description="返回条数(必须大于0)", examples=["20"])
    stock_code: Optional[list] | None = Field(default=None, description="上市公司证券代码，传值则过滤，否则不过滤，数组传递多个值", examples=[["600060.SH", "000639.SZ", "600941.SH"]])
    stock_filter_type: StockFilterType = Field(default=StockFilterType.INCLUDE, description="上市公司筛选方式：0-包含、1-不包括", examples=["0"])
    list_board: Optional[list] | None = Field(default=None, description="上市板块：主板、科创板、创业板，数组传递多个值", examples=[["主板", "创业板", "科创板", "北证"]])
    exchange: Optional[list] | None = Field(default=None, description="交易所：深交所、上交所、北交所，数组传递多个值", examples=[["深交所", "上交所", "北交所"]])
    company_type: Optional[list] | None = Field(default=None, description="公司类型：公众企业、民营企业，数组传递多个值", examples=[["公众企业", "民营企业", "外资企业", "中央国有企业", "地方国有企业", "其他企业", "集体企业"]])
    province: Optional[list] | None = Field(default=None, description="省份：广东省、山东省，数组传递多个值", examples=[["广东省", "山东省", "香港特别行政区"]])
    region: Optional[list] | None = Field(default=None, description="地区，如：华东、华南、华北、华中、西南、西北、东北、跨境，数组传递多个值", examples=[["跨境", "华北"]])
    is_delist: AShareDelistType = Field(default=AShareDelistType.NOT_DELIST, description="是否退市：0-否、1-是、2-全部", examples=["0"])
    order: Optional[dict] = Field(default=None, description="多字段排序，1-倒序、2-正序", examples=[{
        "exchange": 1,
        "stock_code": 1,
    }])
    page: conint(gt=0) | None = Field(default=1, description="当前页码(必须大于0)", examples=["1"])
    size: conint(gt=0, lt=201) | None = Field(default=20, description="每页数据条数(必须大于0且小于200)", examples=["20"])

# 个股排序字段（值为物理表字段，用于映射）
class AShareOrderField(Enum):
    stock_code = "s_info_windcode"  # 股票代码
    list_board = "S_INFO_LISTBOARDNAME"  # 上市板块
    exchange = "S_INFO_EXCHMARKET"  # 交易所
    company_type = "company_type"  # 公司类型
    province = "province"  # 省
    region = "region"  # 地区
    comp_name = "S_INFO_NAME"  # 简称
    comp_full_name = "S_INFO_COMPNAME"  # 公司名称
    citic_industry_l3 = "citic_industry_l3"  # 中信三级行业
    enterprise_circle_label = "enterprise_circle_label"  # 企业圈层标签
    honor_qualification_label = "honor_qualification_label"  # 荣誉资质标签