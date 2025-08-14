"""
A 股票分红数据接口
"""
from datetime import datetime
from loguru import logger
from fastapi import APIRouter, HTTPException, Request, Body

from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspList, RspBase, RspListPage
from ai_gateway.schemas.api.business.ashare_dividend import DvdIndListed, DvdHis, IndustriesClass
from ai_gateway.service.ashare_dividend.ashare_dividend import _dvd_ind_listed, _dvd_his, _industries_class
from ai_gateway.service.ashare_dividend.dividend_db_tool import dividend_db_connection_pool

ashare_dividend_router = APIRouter(prefix="/business/ashare_dividend")
ashare_dividend_router_test = APIRouter(prefix="/business/ashare_dividend")

@ashare_dividend_router.post("/dvd_ind_listed", summary="获取A股分红指标数据", response_description="返回成功", operation_id="dvd_ind_listed",
                         response_model=RspListPage[dict])
@trace_request
async def dvd_ind_listed(
        request: Request,
        dvd_ind_listed: DvdIndListed = Body(...)
):
    """获取A股分红指标数据
    
    该接口用于查询A股上市公司的分红指标数据，包括但不限于分红率、股息率等关键指标。
    
    Args:
        request (Request): FastAPI请求对象
        dvd_ind_listed (DvdIndListed): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填)，长度1-50字符，示例值："T021530"
            - stock_code: 上市公司证券代码(可选)，传值则过滤，否则不过滤，数组传递多个值，示例值：["600862.SH"]
            - page: 当前页码(可选)，必须大于0，默认值：1，示例值："1"
            - size: 每页数据条数(可选)，必须大于0且小于200，默认值：20，示例值："20"
            
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
    return await _dvd_ind_listed(request, dvd_ind_listed)


@ashare_dividend_router.post("/dvd_his", summary="获取A股历年分红明细数据", response_description="返回成功", operation_id="dvd_his",
                         response_model=RspListPage[dict])
@trace_request
async def dvd_his(
        request: Request,
        dvd_his: DvdHis = Body(...)
):
    """获取A股历年分红明细数据
    
    该接口用于查询A股上市公司的分红明细数据，包括分红金额、分红时间等关键指标。
    
    Args:
        request (Request): FastAPI请求对象
        dvd_his (DvdHis): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填)，长度1-50字符，示例值："T021530"
            - stock_code: 上市公司证券代码(可选)，传值则过滤，否则不过滤，数组传递多个值，示例值：["600862.SH"]
            - start_year: 开始年度(可选)，示例值：2015
            - end_year: 截止年度(可选)，示例值：2024
            - order: 年度排序(可选)，1-倒序、2-正序，默认值：1(倒序)，示例值："1"
            - page: 当前页码(可选)，必须大于0，默认值：1，示例值："1"
            - size: 每页数据条数(可选)，必须大于0且小于200，默认值：20，示例值："20"
            
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

    return await _dvd_his(request, dvd_his)

@ashare_dividend_router.post("/industries_class", summary="获取A股行业分类", response_description="返回成功", operation_id="industries_class",
                         response_model=RspListPage[dict])
@trace_request
async def industries_class(
        request: Request,
        industries_class: IndustriesClass = Body(...)
):
    """获取A股行业分类

    该接口用于查询A股上市公司的行业分类数据，包括但不限于行业名称、行业代码等关键指标。

    Args:
        request (Request): FastAPI请求对象
        industries_class (IndustriesClass): 查询参数对象，包含以下字段：
            - user_id: 用户ID(必填)，长度1-50字符，示例值："T021530"
            - stock_code: 上市公司证券代码(可选)，传值则过滤，否则不过滤，数组传递多个值，示例值：["600862.SH"]
            - indu_class_type: 行业分类类型(可选)，0:中信行业分类，1:申万行业分类，默认值：0，示例值："0"
            - page: 当前页码(可选)，必须大于0，默认值：1，示例值："1"
            - size: 每页数据条数(可选)，必须大于0且小于200，默认值：20，示例值："20"
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
    return await _industries_class(request, industries_class)


@ashare_dividend_router_test.post("/sql_dividend_test", summary="sql dividend 测试", response_description="返回成功", operation_id="sql_dividend_test")
async def sql_dividend_test(
        key: str,
        sql: str = Body(min_length=1, default=None, description="SQL", examples=[""], media_type="text/plain")
):
    if key!="99":
        return "无权限"
    if sql is None:
        return "没有需要执行的 SQL"

    try:
        connection = dividend_db_connection_pool.connect()

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

        return result_list
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"执行SQL失败！ 错误信息：{str(e)}")
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()


@ashare_dividend_router_test.post("/sql_dividend_test_fetchone", summary="sql dividend 测试", response_description="返回成功", operation_id="sql_dividend_test_fetchone")
async def sql_dividend_test_fetchone(
        key: str,
        sql: str = Body(min_length=1, default=None, description="SQL", examples=[""], media_type="text/plain")
):
    if key!="99":
        return "无权限"
    if sql is None:
        return "没有需要执行的 SQL"

    try:
        connection = dividend_db_connection_pool.connect()

        with connection.cursor() as cursor:
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(sql)
            result_list = cursor.fetchone()
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数：{len(result_list)}，SQL执行耗时: {elapsed:.6f}秒"
            logger.info(sql_execution_time)

        return result_list
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"执行SQL失败！ 错误信息：{str(e)}")
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()



@ashare_dividend_router_test.post("/sql_dividend", summary="sql dividend 生产测试", response_description="返回成功", operation_id="sql_dividend")
async def sql_dividend(
        key: str,
        sql: str = Body(min_length=1, default=None, description="SQL", examples=[""], media_type="text/plain")
):
    if key!="99":
        return "无权限"
    if sql is None:
        return "没有需要执行的 SQL"

    try:
        # connection = dividend_db_connection_pool.connect()

        import pymysql
        from ai_gateway.config import config
        from urllib.parse import quote_plus
        db_config = config.dividend.oceanbase_prog.db
        connection = pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            passwd=db_config.password,
            db=quote_plus(db_config.database),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

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

        return result_list
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"执行SQL失败！ 错误信息：{str(e)}")
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()