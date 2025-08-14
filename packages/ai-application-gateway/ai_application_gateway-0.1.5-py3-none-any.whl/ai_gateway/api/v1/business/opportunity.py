"""
商机挖掘
"""
from datetime import datetime
from loguru import logger
from fastapi import APIRouter, HTTPException, Request, Body
from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspList, RspBase, RspListPage
from ai_gateway.schemas.api.business.opportunity import Announcement, StockSearch, \
    CompAnn, AShare, StockSearchEx, CompAnnSub, AnnouncementSub, AnnouncementType
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.business.opp_pymysql_tool import connection_pool
from ai_gateway.service.business.opportunity import get_announcements, get_comp_ann, \
    get_search_stock, get_ashare_companies, get_search_stock_ex, get_search_stock_ex_test, \
    set_ashare_collections_subscriptions, AShareOptType

opportunity_router = APIRouter(prefix="/business/opportunity")
opportunity_router_test = APIRouter(prefix="/business/opportunity")


@opportunity_router.post("/comp_ann", summary="获取商机（一级是公司+二级是公告）数据", response_description="返回成功", operation_id="comp_ann",
                         response_model=RspListPage[dict])
@trace_request
async def comp_ann(
        request: Request,
        comp_ann: CompAnn = Body(...)
):
    """获取商机（一级是公司+二级是公告）数据
    Args:
        request (Request): FastAPI请求对象
        comp_ann (CompAnn): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认1-全部并返回收藏状态)：0-全部、1-全部并返回收藏状态、2-已收藏
            - ann_type: 商机类型(可选，默认0-全部)：0-全部、1-委托理财、2-股东减持
            - start_time: 开始时间(可选，默认7天前)
            - end_time: 结束时间(可选，默认今天)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    return await get_comp_ann(request, comp_ann)

@opportunity_router.post("/comp_ann_finance", summary="获取理财商机（一级是公司+二级是公告）数据", response_description="返回成功", operation_id="comp_ann_finance",
                         response_model=RspListPage[dict])
@trace_request
async def comp_ann_finance(
        request: Request,
        comp_ann_sub: CompAnnSub = Body(...)
):
    """获取理财商机（一级是公司+二级是公告）数据
    Args:
        request (Request): FastAPI请求对象
        comp_ann_sub (CompAnnSub): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认1-全部并返回收藏状态)：0-全部、1-全部并返回收藏状态、2-已收藏
            - start_time: 开始时间(可选，默认7天前)
            - end_time: 结束时间(可选，默认今天)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    comp_ann = CompAnn(**comp_ann_sub.dict(), ann_type=AnnouncementType.FINANCE.value)
    return await get_comp_ann(request, comp_ann)

@opportunity_router.post("/comp_ann_reduction", summary="获取减持商机（一级是公司+二级是公告）数据", response_description="返回成功", operation_id="comp_ann_reduction",
                         response_model=RspListPage[dict])
@trace_request
async def comp_ann_reduction(
        request: Request,
        comp_ann_sub: CompAnnSub = Body(...)
):
    """获取减持商机（一级是公司+二级是公告）数据
    Args:
        request (Request): FastAPI请求对象
        comp_ann_sub (CompAnnSub): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认1-全部并返回收藏状态)：0-全部、1-全部并返回收藏状态、2-已收藏
            - start_time: 开始时间(可选，默认7天前)
            - end_time: 结束时间(可选，默认今天)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    comp_ann = CompAnn(**comp_ann_sub.dict(), ann_type=AnnouncementType.REDUCTION.value)
    return await get_comp_ann(request, comp_ann)


@opportunity_router.post("/announcements", summary="获取商机（公告）数据", response_description="返回成功", operation_id="announcements",
                         response_model=RspListPage[dict])
@trace_request
async def announcements(
        request: Request,
        announcement: Announcement = Body(...)
):
    """获取商机（公告）数据
    Args:
        request (Request): FastAPI请求对象
        announcement (Announcement): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - ann_type: 商机类型(可选，默认0-全部)：0-全部、1-委托理财、2-股东减持
            - start_time: 开始时间(可选)
            - end_time: 结束时间(可选)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    return await get_announcements(request, announcement)

@opportunity_router.post("/announcements_finance", summary="获取理财商机（公告）数据", response_description="返回成功", operation_id="announcements_finance",
                         response_model=RspListPage[dict])
@trace_request
async def announcements_finance(
        request: Request,
        announcement_sub: AnnouncementSub = Body(...)
):
    """获取理财商机（公告）数据
    Args:
        request (Request): FastAPI请求对象
        announcement_sub (AnnouncementSub): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - start_time: 开始时间(可选)
            - end_time: 结束时间(可选)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    announcement = Announcement(**announcement_sub.dict(), ann_type=AnnouncementType.FINANCE.value)
    return await get_announcements(request, announcement)

@opportunity_router.post("/announcements_reduction", summary="获取减持商机（公告）数据", response_description="返回成功", operation_id="announcements_reduction",
                         response_model=RspListPage[dict])
@trace_request
async def announcements_reduction(
        request: Request,
        announcement_sub: AnnouncementSub = Body(...)
):
    """获取减持商机（公告）数据
    Args:
        request (Request): FastAPI请求对象
        announcement_sub (AnnouncementSub): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - start_time: 开始时间(可选)
            - end_time: 结束时间(可选)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    announcement = Announcement(**announcement_sub.dict(), ann_type=AnnouncementType.REDUCTION.value)
    return await get_announcements(request, announcement)

@opportunity_router.post("/opportunities_finance", summary="获取理财商机数据", response_description="返回成功", operation_id="opportunities_finance",
                         response_model=RspListPage[dict])
@trace_request
async def opportunities_finance(
        request: Request,
        announcement_sub: AnnouncementSub = Body(...)
):
    """获取理财商机数据
    Args:
        request (Request): FastAPI请求对象
        announcement_sub (AnnouncementSub): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - start_time: 开始时间(可选)
            - end_time: 结束时间(可选)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 时间排序(可选，默认1-倒序)：1-倒序、2-正序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    announcement = Announcement(**announcement_sub.dict(), ann_type=AnnouncementType.FINANCE.value)
    return await get_announcements(request, announcement, False)

@opportunity_router.post("/search_stocks", summary="搜索股票", response_description="返回成功", operation_id="search_stocks",
                         response_model=RspList[dict])
@trace_request
async def search_stocks(
        request: Request,
        stock_search: StockSearch
):
    """搜索股票
    Args:
        request (Request): FastAPI请求对象
        stock_search (StockSearch): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - keyword: 搜索关键词(必填)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - exist_anns: 上市公司是否有公告(可选，默认2-全部)：0-否、1-是、2-全部
            - size: 返回条数(可选，默认5，必须大于0)
    Returns:
        RspList[dict]: 返回列表结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
    """
    return await get_search_stock(request, stock_search)

@opportunity_router.post("/search_stocks_ex", summary="搜索股票扩展（收藏或订阅条件）", response_description="返回成功", operation_id="search_stocks_ex",
                         response_model=RspList[dict])
@trace_request
async def search_stocks_ex(
        request: Request,
        stock_search: StockSearchEx
):
    """搜索股票扩展（收藏或订阅条件）
    Args:
        request (Request): FastAPI请求对象
        stock_search (StockSearchEx): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - keyword: 搜索关键词(必填)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - exist_anns: 上市公司是否有公告(可选，默认2-全部)：0-否、1-是、2-全部
            - size: 返回条数(可选，默认5，必须大于0)
            - query_type: 查询类型(可选，默认0-不返回任何扩展状态)：0-不返回任何扩展状态、1-返回个股收藏状态字段、2-返回个股订阅状态字段
    Returns:
        RspList[dict]: 返回列表结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
    """
    return await get_search_stock_ex(request, stock_search)

@opportunity_router_test.post("/search_stocks_ex_test", summary="搜索股票扩展测试（收藏或订阅条件）", response_description="返回成功",
                         response_model=RspList[dict])
@trace_request
async def search_stocks_ex_test(
        request: Request,
        stock_search: StockSearchEx
):
    """搜索股票扩展测试（收藏或订阅条件）
    Args:
        request (Request): FastAPI请求对象
        stock_search (StockSearchEx): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - keyword: 搜索关键词(必填)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - exist_anns: 上市公司是否有公告(可选，默认2-全部)：0-否、1-是、2-全部
            - size: 返回条数(可选，默认5，必须大于0)
            - query_type: 查询类型(可选，默认0-不返回任何扩展状态)：0-不返回任何扩展状态、1-返回个股收藏状态字段、2-返回个股订阅状态字段
    Returns:
        RspList[dict]: 返回列表结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
    """
    return await get_search_stock_ex_test(request, stock_search)

@opportunity_router.post("/ashare_companies", summary="获取个股数据", response_description="返回成功", operation_id="ashare_companies",
                         response_model=RspListPage[dict])
@trace_request
async def ashare_companies(
        request: Request,
        ashare: AShare = Body(...)
):
    """获取个股数据
    Args:
        request (Request): FastAPI请求对象
        ashare (AShare): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认0-全部)：0-全部、1-全部并返回收藏状态、2-已收藏、3-未收藏、4-全部并返回订阅状态、5-已订阅、6-未订阅
            - keyword: 搜索关键词(可选)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - keyword_size: 关键词搜索返回条数(可选，默认20，必须大于0且小于200)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - exchange: 交易所(可选，数组传递多个值)：深交所、上交所、北交所
            - company_type: 公司类型(可选，数组传递多个值)：公众企业、民营企业、外资企业、中央国有企业、地方国有企业、其他企业、集体企业
            - province: 省份(可选，数组传递多个值)：广东省、山东省、香港特别行政区等
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 多字段排序(可选)：1-倒序、2-正序，支持多个字段排序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspListPage[dict]: 返回分页结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - items: 数据列表
            - total: 总记录数
            - page: 当前页码
            - size: 每页数量
            - pages: 总页数
    """
    return await get_ashare_companies(request, ashare)

@opportunity_router.post("/ashare_add_collections", summary="根据查询个股条件-批量添加收藏", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def ashare_add_collections(
        request: Request,
        ashare: AShare = Body(...)
):
    """根据查询个股条件-批量添加收藏
    Args:
        request (Request): FastAPI请求对象
        ashare (AShare): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认0-全部)：0-全部、1-全部并返回收藏状态、2-已收藏、3-未收藏、4-全部并返回订阅状态、5-已订阅、6-未订阅
            - keyword: 搜索关键词(可选)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - keyword_size: 关键词搜索返回条数(可选，默认20，必须大于0且小于200)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - exchange: 交易所(可选，数组传递多个值)：深交所、上交所、北交所
            - company_type: 公司类型(可选，数组传递多个值)：公众企业、民营企业、外资企业、中央国有企业、地方国有企业、其他企业、集体企业
            - province: 省份(可选，数组传递多个值)：广东省、山东省、香港特别行政区等
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 多字段排序(可选)：1-倒序、2-正序，支持多个字段排序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspBase: 返回操作结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - content: 返回内容
    """
    return await set_ashare_collections_subscriptions(request, ashare, AShareOptType.ADD_COLLECT)

@opportunity_router.post("/ashare_remove_collections", summary="根据查询个股条件-批量移除收藏", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def ashare_remove_collections(
        request: Request,
        ashare: AShare = Body(...)
):
    """根据查询个股条件-批量移除收藏
    Args:
        request (Request): FastAPI请求对象
        ashare (AShare): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认0-全部)：0-全部、1-全部并返回收藏状态、2-已收藏、3-未收藏、4-全部并返回订阅状态、5-已订阅、6-未订阅
            - keyword: 搜索关键词(可选)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - keyword_size: 关键词搜索返回条数(可选，默认20，必须大于0且小于200)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - exchange: 交易所(可选，数组传递多个值)：深交所、上交所、北交所
            - company_type: 公司类型(可选，数组传递多个值)：公众企业、民营企业、外资企业、中央国有企业、地方国有企业、其他企业、集体企业
            - province: 省份(可选，数组传递多个值)：广东省、山东省、香港特别行政区等
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 多字段排序(可选)：1-倒序、2-正序，支持多个字段排序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspBase: 返回操作结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - content: 返回内容
    """
    return await set_ashare_collections_subscriptions(request, ashare, AShareOptType.REMOVE_COLLECT)

@opportunity_router.post("/ashare_add_subscriptions", summary="根据查询个股条件-批量添加订阅", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def ashare_add_subscriptions(
        request: Request,
        ashare: AShare = Body(...)
):
    """根据查询个股条件-批量添加订阅
    Args:
        request (Request): FastAPI请求对象
        ashare (AShare): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认0-全部)：0-全部、1-全部并返回收藏状态、2-已收藏、3-未收藏、4-全部并返回订阅状态、5-已订阅、6-未订阅
            - keyword: 搜索关键词(可选)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - keyword_size: 关键词搜索返回条数(可选，默认20，必须大于0且小于200)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - exchange: 交易所(可选，数组传递多个值)：深交所、上交所、北交所
            - company_type: 公司类型(可选，数组传递多个值)：公众企业、民营企业、外资企业、中央国有企业、地方国有企业、其他企业、集体企业
            - province: 省份(可选，数组传递多个值)：广东省、山东省、香港特别行政区等
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 多字段排序(可选)：1-倒序、2-正序，支持多个字段排序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspBase: 返回操作结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - content: 返回内容
    """
    return await set_ashare_collections_subscriptions(request, ashare, AShareOptType.ADD_SUBSCRIBE)

@opportunity_router.post("/ashare_remove_subscriptions", summary="根据查询个股条件-批量移除订阅", response_description="返回成功",
                         response_model=RspBase)
@trace_request
async def ashare_remove_subscriptions(
        request: Request,
        ashare: AShare = Body(...)
):
    """根据查询个股条件-批量移除订阅
    Args:
        request (Request): FastAPI请求对象
        ashare (AShare): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填，长度1-50)
            - query_type: 查询类型(可选，默认0-全部)：0-全部、1-全部并返回收藏状态、2-已收藏、3-未收藏、4-全部并返回订阅状态、5-已订阅、6-未订阅
            - keyword: 搜索关键词(可选)：股票名称、股票代码、简拼、全拼，支持模糊查询
            - keyword_size: 关键词搜索返回条数(可选，默认20，必须大于0且小于200)
            - stock_code: 上市公司证券代码(可选，数组传递多个值)
            - stock_filter_type: 上市公司筛选方式(可选，默认0-包含)：0-包含、1-不包括
            - list_board: 上市板块(可选，数组传递多个值)：主板、科创板、创业板、北交所
            - exchange: 交易所(可选，数组传递多个值)：深交所、上交所、北交所
            - company_type: 公司类型(可选，数组传递多个值)：公众企业、民营企业、外资企业、中央国有企业、地方国有企业、其他企业、集体企业
            - province: 省份(可选，数组传递多个值)：广东省、山东省、香港特别行政区等
            - region: 地区(可选，数组传递多个值)：华东、华南、华北、华中、西南、西北、东北、跨境
            - is_delist: 是否退市(可选，默认0-否)：0-否、1-是、2-全部
            - order: 多字段排序(可选)：1-倒序、2-正序，支持多个字段排序
            - page: 当前页码(可选，默认1，必须大于0)
            - size: 每页数据条数(可选，默认20，必须大于0且小于200)
    Returns:
        RspBase: 返回操作结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - content: 返回内容
    """
    return await set_ashare_collections_subscriptions(request, ashare, AShareOptType.REMOVE_SUBSCRIBE)

@opportunity_router_test.post("/sql_test", summary="sql测试", response_description="返回成功",
                         response_model=RspList[dict])
@trace_request
async def sql_test(
        request: Request,
        key: str,
        sql: str = Body(min_length=1, default=None, description="SQL", examples=[""], media_type="text/plain")
):
    """SQL测试接口
    Args:
        request (Request): FastAPI请求对象
        key (str): 权限验证密钥
        sql (str): 需要执行的SQL语句(必填，最小长度1)
    Returns:
        RspList[dict]: 返回SQL执行结果，包含以下字段：
            - code: 返回码(200表示成功)
            - message: 返回信息("success"表示成功)
            - content: 执行信息（记录总数和执行耗时）
            - items: SQL查询结果数据列表
    """
    if key!="99":
        return RspBase().fail(content="无权限")
    if sql is None:
        return RspBase().fail(content="没有需要执行的 SQL")
    """获取公告"""
    try:
        connection = connection_pool.connect()

        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(sql)
            result_list = cursor.fetchall()
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数：{len(result_list)}，SQL执行耗时: {elapsed:.6f}秒"
            logger.info(sql_execution_time)

        return RspList(code=200, content=sql_execution_time, items=result_list )
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=f"执行SQL失败！ 错误信息：{str(e)}")
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

