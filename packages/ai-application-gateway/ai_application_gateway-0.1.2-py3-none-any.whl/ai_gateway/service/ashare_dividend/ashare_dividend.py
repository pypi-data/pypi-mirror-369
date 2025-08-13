"""
A股分红
"""
from datetime import datetime
from enum import Enum

import pymysql
from loguru import logger
from fastapi import HTTPException, Request

from ai_gateway.config import config
from ai_gateway.schemas.api.base import RspListPage
from ai_gateway.schemas.api.business.ashare_dividend import DvdIndListed, DvdHis, YearOrder, IndustriesClass
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.ashare_dividend.common_dividend_query import execute_dividend_query_fetchone, execute_dividend_query_fetchall
from ai_gateway.service.ashare_dividend.dividend_db_tool import dividend_db_connection_pool
from ai_gateway.utils.format_type import format_decimal_fields


# 获取A股分红指标数据
async def _dvd_ind_listed(
        request: Request,
        dvd_ind_listed: DvdIndListed
)->RspListPage[dict]:
    if config.dividend.database.db_type == "oracle":
        return await _dvd_ind_listed_oracle(request, dvd_ind_listed)
    else:
        return await _dvd_ind_listed_oceanbase(request, dvd_ind_listed)

# 获取A股分红指标数据
async def _dvd_ind_listed_oceanbase(
        request: Request,
        dvd_ind_listed: DvdIndListed
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()
        connection.ping(reconnect=True)
        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if dvd_ind_listed.stock_code:
                conditions.append("STK_CODE IN %(stock_codes)s")
                params['stock_codes'] = dvd_ind_listed.stock_code

            ashare_dvd_ind_listed_table = config.dividend.ashare_dvd_ind_listed_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + ashare_dvd_ind_listed_table
            base_query = "SELECT * FROM " + ashare_dvd_ind_listed_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                logger.info(f"查询结果：{result}")
                total = result["TOTAL"]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加分页
                if dvd_ind_listed.page is not None and dvd_ind_listed.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': dvd_ind_listed.size,
                        'offset': (dvd_ind_listed.page - 1) * dvd_ind_listed.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                # cursor.execute(base_query, params)
                # result_list = cursor.fetchall()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "个股数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=dvd_ind_listed.page,
                        size=dvd_ind_listed.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股分红指标数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

# 获取A股分红指标数据
async def _dvd_ind_listed_oracle(   
        request: Request,
        dvd_ind_listed: DvdIndListed
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()

        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if dvd_ind_listed.stock_code:
                stock_codes = ",".join(":stock_code"+str(i) for i in range(len(dvd_ind_listed.stock_code)))
                params.update({"stock_code"+str(i): dvd_ind_listed.stock_code[i] for i in range(len(dvd_ind_listed.stock_code))})
                conditions.append(f"STK_CODE IN ({stock_codes})")

            ashare_dvd_ind_listed_table = config.dividend.ashare_dvd_ind_listed_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + ashare_dvd_ind_listed_table
            base_query = "SELECT * FROM " + ashare_dvd_ind_listed_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            logger.info(f"SQL: {count_query}, 参数: {params}")
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                logger.info(f"查询结果：{result}")
                total = result["TOTAL"]
                logger.info(f"查询结果总数：{total}")
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加分页
                if dvd_ind_listed.page is not None and dvd_ind_listed.size is not None:
                    base_query = """
                    SELECT * FROM (
                        SELECT a.*, ROWNUM rn FROM (
                            """ + base_query + """
                        ) a WHERE ROWNUM <= :end_row
                    ) WHERE rn > :start_row
                    """
                    params.update({
                        'end_row': dvd_ind_listed.page * dvd_ind_listed.size,
                        'start_row': (dvd_ind_listed.page - 1) * dvd_ind_listed.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "个股数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=dvd_ind_listed.page,
                        size=dvd_ind_listed.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股分红指标数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()


# 获取A股历年分红明细数据
async def _dvd_his(
        request: Request,
        dvd_his: DvdHis
)->RspListPage[dict]:
    if config.dividend.database.db_type == "oracle":
        return await _dvd_his_oracle(request, dvd_his)
    else:
        return await _dvd_his_oceanbase(request, dvd_his)

# 获取A股历年分红明细数据
async def _dvd_his_oceanbase(
        request: Request,
        dvd_his: DvdHis
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()
        connection.ping(reconnect=True)
        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if dvd_his.stock_code:
                conditions.append("STK_CODE IN %(stock_codes)s")
                params['stock_codes'] = dvd_his.stock_code

            if dvd_his.start_year and dvd_his.end_year:
                conditions.append("REPORT_PERIOD BETWEEN %(start_date)s AND %(end_date)s")
                params.update({
                    'start_date': f"{dvd_his.start_year}-01-01",
                    'end_date': f"{dvd_his.end_year}-12-31"
                })
            ashare_dvd_his_table = config.dividend.ashare_dvd_his_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + ashare_dvd_his_table
            base_query = "SELECT * FROM " + ashare_dvd_his_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                total = result["TOTAL"]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加排序
                if dvd_his.order == YearOrder.DESC:
                    base_query += " ORDER BY REPORT_PERIOD DESC"  # 倒序
                elif dvd_his.order == YearOrder.ASC:
                    base_query += " ORDER BY REPORT_PERIOD ASC"  # 正序

                # 添加分页
                if dvd_his.page is not None and dvd_his.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': dvd_his.size,
                        'offset': (dvd_his.page - 1) * dvd_his.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                # cursor.execute(base_query, params)
                # result_list = cursor.fetchall()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "A股历年分红明细数据数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=dvd_his.page,
                        size=dvd_his.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股历年分红明细数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

# 获取A股历年分红明细数据
async def _dvd_his_oracle(
        request: Request,
        dvd_his: DvdHis
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()

        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if dvd_his.stock_code:
                stock_codes = ",".join(":stock_code"+str(i) for i in range(len(dvd_his.stock_code)))
                params.update({"stock_code"+str(i): dvd_his.stock_code[i] for i in range(len(dvd_his.stock_code))})
                conditions.append(f"STK_CODE IN ({stock_codes})")

            if dvd_his.start_year and dvd_his.end_year:
                conditions.append("REPORT_PERIOD BETWEEN :start_date AND :end_date")
                params.update({
                    'start_date': f"{dvd_his.start_year}-01-01",
                    'end_date': f"{dvd_his.end_year}-12-31"
                })
            ashare_dvd_his_table = config.dividend.ashare_dvd_his_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + ashare_dvd_his_table
            base_query = "SELECT * FROM " + ashare_dvd_his_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                total = result["TOTAL"]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加排序
                if dvd_his.order == YearOrder.DESC:
                    base_query += " ORDER BY REPORT_PERIOD DESC"  # 倒序
                elif dvd_his.order == YearOrder.ASC:
                    base_query += " ORDER BY REPORT_PERIOD ASC"  # 正序

                # 添加分页
                if dvd_his.page is not None and dvd_his.size is not None:
                    base_query = """
                    SELECT * FROM (
                        SELECT a.*, ROWNUM rn FROM (
                            """ + base_query + """
                        ) a WHERE ROWNUM <= :end_row
                    ) WHERE rn > :start_row
                    """
                    params.update({
                        'end_row': dvd_his.page * dvd_his.size,
                        'start_row': (dvd_his.page - 1) * dvd_his.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                # cursor.execute(base_query, params)
                # result_list = cursor.fetchall()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "A股历年分红明细数据数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=dvd_his.page,
                        size=dvd_his.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股历年分红明细数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()


# 获取A股行业分类
async def _industries_class(
        request: Request,
        industries_class: IndustriesClass
)->RspListPage[dict]:
    if config.dividend.database.db_type == "oracle":
        return await _industries_class_oracle(request, industries_class)
    else:
        return await _industries_class_oceanbase(request, industries_class)


# 获取A股行业分类
async def _industries_class_oceanbase(
        request: Request,
        industries_class: IndustriesClass
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()
        connection.ping(reconnect=True)
        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if industries_class.stock_code:
                conditions.append("STK_CODE IN %(stock_codes)s")
                params['stock_codes'] = industries_class.stock_code

            # 行业分类类型：0-中信行业
            if industries_class.indu_class_type:
                conditions.append("INDU_CLASS_TYPE = %(indu_class_type)s")
                params['indu_class_type'] = int(industries_class.indu_class_type)

            industries_class_table = config.dividend.industries_class_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + industries_class_table
            base_query = "SELECT * FROM " + industries_class_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                total = result["TOTAL"]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加分页
                if industries_class.page is not None and industries_class.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': industries_class.size,
                        'offset': (industries_class.page - 1) * industries_class.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                # cursor.execute(base_query, params)
                # result_list = cursor.fetchall()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "A股行业分类数据数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=industries_class.page,
                        size=industries_class.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股行业分类数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

async def _industries_class_oracle(#
        request: Request,
        industries_class: IndustriesClass
)->RspListPage[dict]:
    try:
        # 数据库连接
        connection = dividend_db_connection_pool.connect()

        result_list: list = []
        total = 0
        with connection.cursor() as cursor:
            conditions = []
            params = {}

            # 上市公司条件
            if industries_class.stock_code:
                stock_codes = ",".join(":stock_code"+str(i) for i in range(len(industries_class.stock_code)))
                params.update({"stock_code"+str(i): industries_class.stock_code[i] for i in range(len(industries_class.stock_code))})
                conditions.append(f"STK_CODE IN ({stock_codes})")

            # 行业分类类型：0-中信行业
            if industries_class.indu_class_type:
                conditions.append("INDU_CLASS_TYPE = :indu_class_type")
                params['indu_class_type'] = int(industries_class.indu_class_type)

            industries_class_table = config.dividend.industries_class_table
            count_query = "SELECT COUNT(*) as TOTAL FROM " + industries_class_table
            base_query = "SELECT * FROM " + industries_class_table
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
                base_query += " WHERE " + " AND ".join(conditions)
            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            result = execute_dividend_query_fetchone(count_query, params)
            if result is None:
                logger.error(f"查询执行失败: {count_query} with params {params}")
                total = 0
            else:
                total = result["TOTAL"]
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                # 添加分页
                if industries_class.page is not None and industries_class.size is not None:
                    base_query = """
                    SELECT * FROM (
                        SELECT a.*, ROWNUM rn FROM (
                            """ + base_query + """
                        ) a WHERE ROWNUM <= :end_row
                    ) WHERE rn > :start_row
                    """
                    params.update({
                        'end_row': industries_class.page * industries_class.size,
                        'start_row': (industries_class.page - 1) * industries_class.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                result_list = execute_dividend_query_fetchall(base_query, params, connection, cursor)
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {dividend_db_connection_pool.status()}")
        content_res = "A股行业分类数据数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=industries_class.page,
                        size=industries_class.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = dividend_db_connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取A股行业分类数据失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()