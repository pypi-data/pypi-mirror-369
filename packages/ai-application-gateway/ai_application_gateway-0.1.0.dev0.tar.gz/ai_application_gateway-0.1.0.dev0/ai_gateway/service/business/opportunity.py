"""
商机挖掘
"""
from datetime import datetime
from enum import Enum

import pymysql
from loguru import logger
from fastapi import HTTPException, Request

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import opp_es_tool
from ai_gateway.schemas.api.base import RspListPage, RspList, RspBase
from ai_gateway.schemas.api.business.opportunity import AnnouncementType, Announcement, StockSearch, StockSearchEx, \
    CompAnn, AnnouncementOrder, AShare, AShareOrderField, CompAnnQueryType, AShareExistAnns, StockSearchExQueryType
from ai_gateway.schemas.api.common.collection import CollectionType, Collection
from ai_gateway.schemas.api.common.subscription import Subscription, SubscriptionType

from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.business.opp_pymysql_tool import connection_pool
from ai_gateway.service.business.opp_es_query_stock_body import get_query_stock_body, get_query_stock_body2
from ai_gateway.service.business.opportunity_sub_fun import build_ann_result_list, \
    get_view_field_comments, build_ann_query_conditions, build_ashare_query_conditions, ashare_query_builders, \
    get_ashare_is_collect_ids, format_decimal_fields, get_ashare_is_subscribe_ids
from ai_gateway.service.common.collection import insert_collections, delete_collections
from ai_gateway.service.common.subscription import insert_subscriptions, delete_subscriptions


# 获取商机（一级是公司+二级是公告）数据
async def get_comp_ann(
        request: Request,
        comp_ann: CompAnn
) -> RspListPage[dict]:
    """获取商机"""
    try:
        # 动态构建查询条件
        conditions,params = await build_ann_query_conditions(comp_ann.ann_type,
                                                        comp_ann.stock_code,
                                                        comp_ann.stock_filter_type,
                                                        comp_ann.start_time,
                                                        comp_ann.end_time,
                                                        comp_ann.list_board,
                                                        comp_ann.region,
                                                        comp_ann.is_delist)
        # 数据库连接
        connection = connection_pool.connect()
        # 增加连接健康检查
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 如果查询类型是： 已收藏，并返回收藏状态字段is_collect
            inner_join_collect = ""
            is_collect_field = ""
            if comp_ann.query_type == CompAnnQueryType.COLLECT:
                # 是否收藏，固定返回 1
                is_collect_field = ", 1 as is_collect"
                # 内关联查询已收藏个股
                inner_join_collect = f" inner join user_collections u on a.ashare_company_id = u.collectable_id and u.user_id = %(user_id)s and u.collectable_type='{CollectionType.AshareCompany.value}'"
                params["user_id"] = comp_ann.user_id

            # 商机表
            comp_ann_tablename = config.opportunity.db.comp_ann_tablename
            # 获取满足条件公司的总数，只要有公告的公司就会筛选出来
            comp_total_query = f"SELECT COUNT(DISTINCT ashare_company_id) AS total FROM {comp_ann_tablename} a {inner_join_collect}"
            if conditions:
                comp_total_query += " WHERE " + " AND ".join(conditions)

            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(comp_total_query, params)
            total = cursor.fetchone()['total']
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            content_res = f"公司总数：{total} "
            logger.info(f"满足条件公司记录总数：{total}，SQL: {comp_total_query}, 参数: {params}")
            logger.info(sql_execution_time)

            result_list:list = []
            if total>0:
                # 查询公司：最近时间等条件下有公告的公司，并返回前几条公告 id
                # 组合WHERE条件
                if conditions:
                    where_str = " WHERE " + " AND ".join(conditions)
                # 添加排序
                if comp_ann.order == AnnouncementOrder.DESC:
                    order_str = " ORDER BY ann_dt DESC"  # 倒序
                elif comp_ann.order == AnnouncementOrder.ASC:
                    order_str = " ORDER BY ann_dt ASC"  # 正序
                # 添加分页
                if comp_ann.page is not None and comp_ann.size is not None:
                    limit_str = " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': comp_ann.size,
                        'offset': (comp_ann.page - 1) * comp_ann.size
                    })

                comp_query= f"""
                    WITH ashare AS (
                        SELECT 
                            id,
                            ashare_company_id,
                            ann_dt,
                            ROW_NUMBER() OVER (PARTITION BY ashare_company_id ORDER BY ann_dt DESC) AS row_num
                        FROM {comp_ann_tablename}
                        {where_str}
                    )
                    SELECT 
                        ashare_company_id,
                        MAX(ann_dt) AS ann_dt,
                        GROUP_CONCAT(a.id ORDER BY row_num SEPARATOR ', ') AS top_ids
                        {is_collect_field}
                    FROM ashare a {inner_join_collect}
                    WHERE row_num <= 3
                    GROUP BY ashare_company_id
                    {order_str}
                    {limit_str}
                """

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                cursor.execute(comp_query, params)
                comp_result_list = cursor.fetchall()
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取公司的分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取公司的分页数据SQL: {comp_query}, 参数: {params}")
                logger.info(sql_execution_time)

                if comp_result_list:
                    # 如果查询类型是：全部，并返回收藏状态字段is_collect
                    if comp_ann.query_type == CompAnnQueryType.ALL_COLLECT:
                        # 获取个股ids
                        ashare_company_ids = [item['ashare_company_id'] for item in comp_result_list]
                        # 获取已收藏的个股ids
                        is_collect_ashare_company_ids = await get_ashare_is_collect_ids(ashare_company_ids, comp_ann.user_id)
                        # 将个股收藏状态添加到comp_result_list
                        for item in comp_result_list:
                            item['is_collect'] = 1 if item['ashare_company_id'] in is_collect_ashare_company_ids else 0

                    # 通过查询表 view_field_comments，获取字段 field_name
                    field_list = await get_view_field_comments(cursor)
                    # 商机表 - 所有字段
                    all_field_str = ",".join([item["field_name"] for item in field_list])
                    # 商机表 - 公告相关字段： field_type = 1 理财字段， field_type = 2 减持字段， field_type = 3 基础商机字段
                    ann_field_list = [item["field_name"] for item in field_list if item.get("field_type") in (1, 2, 3)]
                    # 商机表 - field_type = 0 上市公司字段
                    comp_field_list = [item["field_name"] for item in field_list if item.get("field_type") == 0]

                    # 直接生成placeholders和id列表
                    all_top_ids = []
                    placeholders = []
                    for item in comp_result_list:
                        if 'top_ids' in item:
                            ids = [id.strip() for id in item['top_ids'].split(',')]
                            all_top_ids.extend(ids)
                            placeholders.extend(["%s"] * len(ids))
                    content_res += f"当前页商机公告数量: {len(all_top_ids)}"
                    logger.info(f"合并后的公告top_ids数量: {len(all_top_ids)}")

                    # 拼接公告查询SQL
                    ann_query = f"SELECT {all_field_str} FROM {comp_ann_tablename}"
                    if all_top_ids:
                        ann_query += f" WHERE id IN ({','.join(placeholders)})"
                        ann_params = tuple(all_top_ids)  # 改为直接使用元组作为参数

                        # 再获取分页数据
                        # 记录开始时间
                        start_time = datetime.now()
                        cursor.execute(ann_query, ann_params)
                        ann_result_list = cursor.fetchall()
                        # 计算耗时
                        elapsed = (datetime.now() - start_time).total_seconds()
                        sql_execution_time = f"获取公告数据SQL执行耗时: {elapsed:.6f}秒"
                        logger.info(f"获取公告数据SQL: {ann_query}, 参数: {params}")
                        logger.info(sql_execution_time)

                        # 构建结果列表
                        result_list = await build_ann_result_list(ann_result_list, 
                                                                    comp_result_list, 
                                                                    comp_field_list, 
                                                                    ann_field_list, 
                                                                    comp_ann.query_type,
                                                                    comp_ann.order)
            else:
                logger.info("未查询到符合条件的公司记录")

        logger.info(f"连接池状态: {connection_pool.status()}")
        logger.info("查询结果，"+content_res)
        return RspListPage(content=content_res,
                           items=result_list,
                           total=total,
                           page=comp_ann.page,
                           size=comp_ann.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取商机失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()


# 获取商机（公告）数据
async def get_announcements(
        request: Request,
        announcement: Announcement,
        is_collect: bool = True
)->RspListPage[dict]:
    """获取公告"""
    try:
        # 动态构建查询条件
        conditions, params = await build_ann_query_conditions(announcement.ann_type,
                                                        announcement.stock_code,
                                                        announcement.stock_filter_type,
                                                        announcement.start_time,
                                                        announcement.end_time,
                                                        announcement.list_board,
                                                        announcement.region,
                                                        announcement.is_delist)
        # 数据库连接
        connection = connection_pool.connect()
        # 增加连接健康检查
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 商机表
            comp_ann_tablename = config.opportunity.db.comp_ann_tablename
            # 先获取总数
            count_query = f"SELECT COUNT(*) as total FROM {comp_ann_tablename}"
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)

            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            result_list: list = []
            if total > 0:
                # 通过查询表 view_field_comments，获取字段 field_name
                field_list = await get_view_field_comments(cursor)
                """
                field_type = 0 上市公司字段
                field_type = 1 理财字段
                field_type = 2 减持字段
                field_type = 3 基础商机字段

                筛选逻辑：
                field_type 1: 筛选理财
                    field_type in (0,1,3)
                field_type 2: 筛选减持
                     field_type in (0,2,3)
                field_type 3: all
                      all
                """
                field_str = ",".join([item["field_name"] for item in field_list])
                if announcement.ann_type == AnnouncementType.FINANCE:  # 理财
                    field_str = ",".join(
                        [item["field_name"] for item in field_list if item.get("field_type") in (0, 1, 3)])
                elif announcement.ann_type == AnnouncementType.REDUCTION:  # 减持
                    field_str = ",".join(
                        [item["field_name"] for item in field_list if item.get("field_type") in (0, 2, 3)])

                # 拼接 公告查询 SQL
                base_query = f"SELECT {field_str} FROM {comp_ann_tablename}"

                # 组合WHERE条件
                if conditions:
                    base_query += " WHERE " + " AND ".join(conditions)

                # 添加排序
                if announcement.order == AnnouncementOrder.DESC:
                    base_query += " ORDER BY ann_dt DESC"  # 倒序
                elif announcement.order == AnnouncementOrder.ASC:
                    base_query += " ORDER BY ann_dt ASC"  # 正序

                # 添加分页
                if announcement.page is not None and announcement.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': announcement.size,
                        'offset': (announcement.page - 1) * announcement.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                cursor.execute(base_query, params)
                result_list = cursor.fetchall()
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)

                if is_collect:
                    # 获取个股ids
                    ashare_company_ids = [item['ashare_company_id'] for item in result_list]
                    # 获取已收藏的个股ids
                    is_collect_ashare_company_ids = await get_ashare_is_collect_ids(ashare_company_ids,
                                                                                    announcement.user_id)
                    # 将个股收藏状态添加到comp_result_list
                    for item in result_list:
                        item['is_collect'] = 1 if item['ashare_company_id'] in is_collect_ashare_company_ids else 0
                
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {connection_pool.status()}")
        content_res = "商机公告数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=announcement.page,
                        size=announcement.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取商机（公告）失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()


# 搜索股票
async def get_search_stock(
        request: Request,
        stock_search: StockSearch
)->RspList[dict]:

    cfg = config.opportunity.es
    exist_anns = stock_search.exist_anns.value
    if stock_search.exist_anns == AShareExistAnns.ALL:
        exist_anns = None
    query_body = get_query_stock_body(stock_search.keyword, stock_search.size, exist_anns)  # 只查询有公告的股票
    result = await opp_es_tool.search(index=cfg.stock_index, body=query_body)

    res_info = f"从ES中共查询到 {result['hits']['total']['value']} 条，实际展示 {len(result['hits']['hits'])} 条"
    logger.info(res_info)

    res_list = [
        {
            **hit['_source'],
            'highlight': hit.get('highlight', None)
        }
        for hit in result['hits']['hits']
    ]
    return RspList(items=res_list, content=res_info)

    
# 搜索股票扩展（收藏或订阅条件）
async def get_search_stock_ex(
        request: Request,
        stock_search: StockSearchEx
)->RspList[dict]:

    cfg = config.opportunity.es
    exist_anns = stock_search.exist_anns.value
    if stock_search.exist_anns == AShareExistAnns.ALL:
        exist_anns = None
    query_body = get_query_stock_body(stock_search.keyword, stock_search.size, exist_anns)  # 只查询有公告的股票
    result = await opp_es_tool.search(index=cfg.stock_index, body=query_body)

    res_info = f"从ES中共查询到 {result['hits']['total']['value']} 条，实际展示 {len(result['hits']['hits'])} 条"
    logger.info(res_info)

    res_list = []
    if len(result['hits']['hits']) > 0:
        res_list = [
            {
                **hit['_source'],
                'highlight': hit.get('highlight', None)
            }
            for hit in result['hits']['hits']
        ]

        # 如果查询类型是：1-全部，并返回收藏状态字段is_collect
        if stock_search.query_type == StockSearchExQueryType.IS_COLLECT:
            # 获取个股ids
            ashare_company_ids = [item['id'] for item in res_list]
            # 获取已收藏的个股ids
            is_collect_ashare_company_ids = await get_ashare_is_collect_ids(ashare_company_ids, stock_search.user_id)
            # 将个股收藏状态添加到comp_result_list
            for item in res_list:
                item['is_collect'] = 1 if item['id'] in is_collect_ashare_company_ids else 0
        # 如果查询类型是：2-全部，并返回订阅状态字段is_subscribe
        elif stock_search.query_type == StockSearchExQueryType.IS_SUBSCRIBE:
            # 获取个股ids
            ashare_company_ids = [item['id'] for item in res_list]
            # 获取已订阅的个股ids
            is_subscribe_ashare_company_ids = await get_ashare_is_subscribe_ids(ashare_company_ids, stock_search.user_id)
            # 将个股收藏状态添加到comp_result_list
            for item in res_list:
                item['is_subscribe'] = 1 if item['id'] in is_subscribe_ashare_company_ids else 0

    return RspList(items=res_list, content=res_info)


# 搜索股票扩展（收藏或订阅条件），测试前缀匹配suggest，及与Query结果合并的情况（目前没用到Query查询）
async def get_search_stock_ex_test(
        request: Request,
        stock_search: StockSearchEx
)->RspList[dict]:

    cfg = config.opportunity.es
    exist_anns = stock_search.exist_anns.value
    if stock_search.exist_anns == AShareExistAnns.ALL:
        exist_anns = None
    query_body = get_query_stock_body2(stock_search.keyword, stock_search.size, exist_anns)  # 只查询有公告的股票
    result = await opp_es_tool.search(index=cfg.stock_index2, body=query_body)

    suggest_result = {}
    if 'suggest' in result:  # 修改为检查result中的suggest
        suggest_result = [
            {
                'text': option['text'],
                '_score': option['_score'],
                '_source': option['_source']  # 包含完整的文档数据
            }
            for option in result['suggest']['stock_suggest'][0]['options']
        ]
    
    # 合并suggest_result和result['hits']['hits']的结果
    res_list = [
        {
            **hit['_source'],
            'highlight': hit.get('highlight', None)
        }
        for hit in result['hits']['hits']
    ]
    
    for hit in suggest_result:
        if hit['_source']['id'] not in [item['id'] for item in res_list]:
            res_list.append({
                **hit['_source'],
                'highlight': hit.get('highlight', None)
            })
            
    res_info = f"从ES中共查询实际展示 {len(res_list)} 条"
    logger.info(res_info)
    if len(res_list) > 0:
        # 如果查询类型是：1-全部，并返回收藏状态字段is_collect
        if stock_search.query_type == StockSearchExQueryType.IS_COLLECT:
            # 获取个股ids
            ashare_company_ids = [item['id'] for item in res_list]
            # 获取已收藏的个股ids
            is_collect_ashare_company_ids = await get_ashare_is_collect_ids(ashare_company_ids, stock_search.user_id)
            # 将个股收藏状态添加到comp_result_list
            for item in res_list:
                item['is_collect'] = 1 if item['id'] in is_collect_ashare_company_ids else 0
        # 如果查询类型是：2-全部，并返回订阅状态字段is_subscribe
        elif stock_search.query_type == StockSearchExQueryType.IS_SUBSCRIBE:
            # 获取个股ids
            ashare_company_ids = [item['id'] for item in res_list]
            # 获取已订阅的个股ids
            is_subscribe_ashare_company_ids = await get_ashare_is_subscribe_ids(ashare_company_ids, stock_search.user_id)
            # 将个股收藏状态添加到comp_result_list
            for item in res_list:
                item['is_subscribe'] = 1 if item['id'] in is_subscribe_ashare_company_ids else 0

    return RspList(items=res_list, content=res_info)

# 获取个股数据
async def get_ashare_companies(
        request: Request,
        ashare: AShare
)->RspListPage[dict]:
    """获取公告"""
    try:
        # 数据库连接
        connection = connection_pool.connect()
        # 增加连接健康检查
        connection.ping(reconnect=True)

        result_list: list = []
        total = 0
        # 动态构建查询条件，并基于 ES 搜索股票
        conditions, params, sorted_stock_codes, search_not_exist_stock = await build_ashare_query_conditions(ashare)
        if search_not_exist_stock:     # 搜索了，没有查找到个股，直接返回
            content_res = "个股数量：" + str(total)
            logger.info("查询结果，" + content_res)
            return RspListPage(content=content_res,
                            items=result_list,
                            total=total,
                            page=ashare.page,
                            size=ashare.size,
                            )

        with connection.cursor() as cursor:
            # 个股表
            ashare_companies = config.opportunity.db.ashare_companies_tabename + " a"
            # 构建不同查询类型的个股查询语句
            count_query, base_query = ashare_query_builders[ashare.query_type](
                ashare_companies,
                conditions
            )
            params['user_id'] = ashare.user_id

            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"记录总数SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"记录总数：{total}，SQL: {count_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if total > 0:
                if sorted_stock_codes:  # 默认按通过 ES 查询股票的股票排序
                    base_query += " ORDER BY FIELD(a.s_info_windcode, '" + "','".join(sorted_stock_codes) + "')"
                # 添加排序，多字段排序，1-倒序、2-正序
                elif ashare.order:
                    order_clauses = []
                    for field, direction in ashare.order.items():
                        if direction not in (1, 2):
                            continue
                        for f in AShareOrderField:
                            if field == f.name:
                                order_clauses.append(f"{f.value} {'DESC' if direction == 1 else 'ASC'}")
                                break
                    if order_clauses:
                        base_query += " ORDER BY " + ", ".join(order_clauses)

                # 添加分页
                if ashare.page is not None and ashare.size is not None:
                    base_query += " LIMIT %(limit)s OFFSET %(offset)s"
                    params.update({
                        'limit': ashare.size,
                        'offset': (ashare.page - 1) * ashare.size
                    })

                # 再获取分页数据
                # 记录开始时间
                start_time = datetime.now()
                cursor.execute(base_query, params)
                result_list = cursor.fetchall()
                # 计算耗时
                elapsed = (datetime.now() - start_time).total_seconds()
                sql_execution_time = f"获取分页数据SQL执行耗时: {elapsed:.6f}秒"
                logger.info(f"获取分页数据SQL: {base_query}, 参数: {params}")
                logger.info(sql_execution_time)
                # 在返回结果前格式化decimal、float字段
                result_list = [format_decimal_fields(item) for item in result_list]

        logger.info(f"连接池状态: {connection_pool.status()}")
        content_res = "个股数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspListPage(content=content_res,
                        items=result_list,
                        total=total,
                        page=ashare.page,
                        size=ashare.size,
                           )
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取个股失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

class AShareOptType(Enum):
    ADD_COLLECT = 0 #  添加收藏
    REMOVE_COLLECT = 1 #  移除收藏
    ADD_SUBSCRIBE = 2  # 添加订阅
    REMOVE_SUBSCRIBE = 3 # 移除订阅

# 根据查询个股条件-批量添加、移除 收藏或订阅
async def set_ashare_collections_subscriptions(
        request: Request,
        ashare: AShare,
        ashare_opt_type: AShareOptType
)->RspBase:
    """获取公告"""
    try:
        # 数据库连接
        connection = connection_pool.connect()
        # 增加连接健康检查
        connection.ping(reconnect=True)

        result_list: list = []
        total = 0
        # 动态构建查询条件，并基于 ES 搜索股票
        conditions, params, sorted_stock_codes, search_not_exist_stock = await build_ashare_query_conditions(ashare)
        if search_not_exist_stock:     # 搜索了，没有查找到个股，直接返回
            content_res = "个股数量：" + str(total)
            logger.info("查询结果，" + content_res)
            return RspListPage(content=content_res,
                            items=result_list,
                            total=total,
                            page=ashare.page,
                            size=ashare.size,
                            )

        with connection.cursor() as cursor:
            # 个股表
            ashare_companies = config.opportunity.db.ashare_companies_tabename

            base_query = f"SELECT id FROM {ashare_companies}"

            if conditions:
                where_str = " WHERE " + " AND ".join(conditions)
                base_query += where_str


            # 记录开始时间
            start_time = datetime.now()
            # 执行SQL
            cursor.execute(base_query, params)
            result_list = cursor.fetchall()
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            sql_execution_time = f"获取符合条件的个股 ID，SQL执行耗时: {elapsed:.6f}秒"
            logger.info(f"获取符合条件的个股 ID: {base_query}, 参数: {params}")
            logger.info(sql_execution_time)

            if len(result_list) > 0:
                ids = [item['id'] for item in result_list]
                if ashare_opt_type == AShareOptType.ADD_COLLECT:
                    collection = Collection(
                        business_type="opportunity",
                        user_id=ashare.user_id,
                        collectable_type=CollectionType.AshareCompany.value,
                        collectable_id=[item['id'] for item in result_list]
                    )
                    return await insert_collections(request, collection)
                elif ashare_opt_type == AShareOptType.REMOVE_COLLECT:
                    collection = Collection(
                        business_type="opportunity",
                        user_id=ashare.user_id,
                        collectable_type=SubscriptionType.AshareCompany.value,
                        collectable_id=[item['id'] for item in result_list]
                    )
                    return await delete_collections(request, collection)
                elif ashare_opt_type == AShareOptType.ADD_SUBSCRIBE:
                    subscription = Subscription(
                        business_type="opportunity",
                        user_id=ashare.user_id,
                        subscribable_type=SubscriptionType.AshareCompany.value,
                        subscribable_id=[item['id'] for item in result_list]
                    )
                    return await insert_subscriptions(request, subscription)
                elif ashare_opt_type == AShareOptType.REMOVE_SUBSCRIBE:
                    subscription = Subscription(
                        business_type="opportunity",
                        user_id=ashare.user_id,
                        subscribable_type=SubscriptionType.AshareCompany.value,
                        subscribable_id=[item['id'] for item in result_list]
                    )
                    return await delete_subscriptions(request, subscription)

        logger.info(f"连接池状态: {connection_pool.status()}")
        content_res = "查询个股数量：" + str(total)
        logger.info("查询结果，" + content_res)
        return RspBase(content=content_res)
    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()  # 主动重连
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"失败！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        # 显式关闭连接（归还给连接池）
        if connection:
            connection.close()

