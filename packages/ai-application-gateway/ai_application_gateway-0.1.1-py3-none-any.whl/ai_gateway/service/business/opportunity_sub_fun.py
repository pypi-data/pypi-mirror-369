"""
商机子函数
"""
from datetime import datetime
from decimal import Decimal

import pymysql
from fastapi import HTTPException
from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import opp_es_tool
from ai_gateway.schemas.api.business.opportunity import AnnouncementType, StockFilterType, AShare, AShareQueryType, \
    CompAnnQueryType, AShareDelistType, AnnouncementOrder
from ai_gateway.schemas.api.common.collection import CollectionType
from ai_gateway.schemas.api.common.subscription import SubscriptionType
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.service.business.opp_es_query_stock_body import get_query_stock_body
from ai_gateway.service.common.common_pymysql_tool import get_pool
from ai_gateway.utils.format_type import format_decimal_fields

# 构建商机查询条件
async def build_ann_query_conditions(ann_type, stock_code, stock_filter_type, start_time, end_time, list_board, region, is_delist):
    conditions = []
    params = {}

    # 商机类型：0-所有、1-委托理财、2-股东减持
    if ann_type == AnnouncementType.FINANCE:  # 理财
        conditions.append("ann_type=1")
    elif ann_type == AnnouncementType.REDUCTION:  # 减持
        conditions.append("ann_type=2")

    # 上市公司条件
    if stock_code:
        if stock_filter_type == StockFilterType.INCLUDE:  # 包含
            conditions.append("s_info_windcode IN %(stock_codes)s")
        else:  # 不包含
            conditions.append("s_info_windcode NOT IN %(stock_codes)s")
        params['stock_codes'] = stock_code

    # 时间范围条件
    if start_time and end_time:
        # 转义 % 符号
        conditions.append("ann_dt BETWEEN %(start_time)s AND %(end_time)s")
        params.update({
            'start_time': start_time,
            'end_time': end_time
        })

    # 上市板块条件
    if list_board:
        conditions.append("S_INFO_LISTBOARDNAME IN %(list_boards)s")
        params['list_boards'] = list_board

    # 地区条件
    if region:
        # 统一使用LIKE条件，内部用OR连接
        region_conditions = []
        if isinstance(region, list):
            region_conditions = [f"region LIKE %(region_{i})s" for i in range(len(region))]
            for i, _region in enumerate(region):
                params[f'region_{i}'] = f"%{_region}%"
        else:
            region_conditions.append("region LIKE %(region)s")
            params['region'] = f"%{region}%"

        # 将region条件用OR连接后作为一个整体条件添加到conditions列表中
        conditions.append(f"({' OR '.join(region_conditions)})")

    # 是否退市条件：0-否、1-是、2-全部
    if is_delist == AShareDelistType.NOT_DELIST:  # 否
        conditions.append("is_delist=0")
    elif is_delist == AShareDelistType.DELIST:  # 是
        conditions.append("is_delist=1")

    return conditions, params

# 构建结果列表
async def build_ann_result_list(ann_result_list, comp_result_list, comp_field_list, ann_field_list, comp_ann_query_type:CompAnnQueryType, comp_ann_order:AnnouncementOrder):
    result_list:list = []
    if ann_result_list:
        for item in comp_result_list:
            # 查找匹配的公告
            top_ids = [id.strip() for id in item['top_ids'].split(',')]
            matched_anns = [ann for ann in ann_result_list if str(ann['id']).strip() in top_ids]
            if matched_anns:
                # 构建公司信息字典
                comp_dict = {
                    field: matched_anns[0].get(field, None)  # 从第一个匹配的公告中获取字段值
                    for field in comp_field_list
                }

                # 构建公告信息列表
                ann_list = []
                for ann in matched_anns:
                    ann_dict = {
                        field: ann.get(field, None)  # 添加默认值None
                        for field in ann_field_list
                    }
                    # 过滤掉完全为None的字典
                    if any(ann_dict.values()):
                        ann_list.append(ann_dict)

                # 只有当ann_list不为空时才添加到结果中
                if ann_list:
                    # 按公告日期排序
                    reverse = comp_ann_order == AnnouncementOrder.DESC
                    ann_list.sort(key=lambda x: x.get('ann_dt'), reverse=reverse)

                    # 计算理财和减持公告数量
                    finance_count = sum(1 for ann in matched_anns if ann.get('ann_type') == 1)
                    reduction_count = sum(1 for ann in matched_anns if ann.get('ann_type') == 2)

                    # 格式化公司信息中的Decimal字段
                    comp_dict = format_decimal_fields({
                        field: matched_anns[0].get(field, None)
                        for field in comp_field_list
                    })

                    # 格式化公告信息中的Decimal字段
                    formatted_ann_list = []
                    for ann in ann_list:
                        formatted_ann_list.append(format_decimal_fields(ann))

                    # 1-全部，并返回收藏状态字段is_collect、2-已收藏
                    if comp_ann_query_type == CompAnnQueryType.ALL_COLLECT or comp_ann_query_type == CompAnnQueryType.COLLECT:
                        result_dict = {
                            **comp_dict,
                            "is_collect": item["is_collect"],
                            "ann": formatted_ann_list,
                            "ann_total": len(formatted_ann_list),  # 当前公司商机公告总数
                            "ann_finance_total": finance_count,  # 当前公司理财商机公告总数
                            "ann_reduction_total": reduction_count  # 当前公司减持商机公告总数
                        }
                    else:
                        result_dict = {
                            **comp_dict,
                            "ann": formatted_ann_list,
                            "ann_total": len(formatted_ann_list),  # 当前公司商机公告总数
                            "ann_finance_total": finance_count,  # 当前公司理财商机公告总数
                            "ann_reduction_total": reduction_count  # 当前公司减持商机公告总数
                        }
                    result_list.append(result_dict)

    return result_list

# 通过查询表 view_field_comments，获取字段 field_name
async def get_view_field_comments(cursor):
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
    field_query = "SELECT field_name, field_type FROM view_field_comments WHERE view_name = %(view_name)s"

    # 记录开始时间
    start_time = datetime.now()
    # 执行SQL
    cursor.execute(field_query, {'view_name': config.opportunity.db.comp_ann_tablename})
    field_list = cursor.fetchall()
    # 计算耗时
    elapsed = (datetime.now() - start_time).total_seconds()
    sql_execution_time = f"查询表 view_field_comments 获取字段SQL执行耗时: {elapsed:.6f}秒"
    logger.info(f"字段总数：{len(field_list)}，SQL: {field_query}")
    logger.info(sql_execution_time)
    return field_list

# 构建个股查询条件，并基于 ES 搜索股票
async def build_ashare_query_conditions(ashare: AShare):
    conditions = []
    params = {}
    sorted_stock_codes = [] # 搜索的个股顺序

    # 搜索个股关键字，ES查询
    if ashare.keyword and ashare.keyword_size:
        cfg = config.opportunity.es
        query_body = get_query_stock_body(ashare.keyword, ashare.keyword_size)  # 查询全市场的股票
        result = await opp_es_tool.search(index=cfg.stock_index, body=query_body)

        res_info = f"从ES中共查询到 {result['hits']['total']['value']} 条，实际使用 {len(result['hits']['hits'])} 条"
        logger.info(res_info)
        res_list = [hit['_source'] for hit in result['hits']['hits']]
        # 搜索了，一个都没有，直接返回
        if not res_list:
            return conditions, params, sorted_stock_codes, True
        for item in res_list:
            sorted_stock_codes.append(item['stock_code'])
            if ashare.stock_code is None:
                ashare.stock_code = []
            if item['stock_code'] not in ashare.stock_code:
                ashare.stock_code.append(item['stock_code'])

    # 上市公司条件
    if ashare.stock_code:
        if ashare.stock_filter_type == StockFilterType.INCLUDE:  # 包含
            conditions.append("s_info_windcode IN %(stock_codes)s")
        else:  # 不包含
            conditions.append("s_info_windcode NOT IN %(stock_codes)s")
        params['stock_codes'] = ashare.stock_code

    # 上市板块条件
    if ashare.list_board:
        conditions.append("S_INFO_LISTBOARDNAME IN %(list_boards)s")
        params['list_boards'] = ashare.list_board

    # 交易所条件
    if ashare.exchange:
        conditions.append("S_INFO_EXCHMARKET IN %(exchange)s")
        params['exchange'] = ashare.exchange

    # 公司类型条件
    if ashare.company_type:
        conditions.append("company_type IN %(company_type)s")
        params['company_type'] = ashare.company_type

    # 省条件
    if ashare.province:
        conditions.append("province IN %(province)s")
        params['province'] = ashare.province

    # 地区条件
    if ashare.region:
        # 统一使用LIKE条件，内部用OR连接
        region_conditions = []
        if isinstance(ashare.region, list):
            region_conditions = [f"region LIKE %(region_{i})s" for i in range(len(ashare.region))]
            for i, _region in enumerate(ashare.region):
                params[f'region_{i}'] = f"%{_region}%"
        else:
            region_conditions.append("region LIKE %(region)s")
            params['region'] = f"%{ashare.region}%"

        # 将region条件用OR连接后作为一个整体条件添加到conditions列表中
        conditions.append(f"({' OR '.join(region_conditions)})")

    # 是否退市条件：0-否、1-是、2-全部
    if ashare.is_delist == AShareDelistType.NOT_DELIST:  # 否
        conditions.append("is_delist=0")
    elif ashare.is_delist == AShareDelistType.DELIST:  # 是
        conditions.append("is_delist=1")

    return conditions, params, sorted_stock_codes, False

# 构建基础查询SQL
def build_base_query(table_name, field, join_table=None, where_conditions=None):
    """
    构建基础查询SQL
    :param table_name: 主表名
    :param join_table: 关联表名
    :param where_conditions: WHERE条件列表
    :return: (count_query, base_query)
    """
    count_query = f"SELECT COUNT(*) as total FROM {table_name}"
    base_query = f"SELECT {field} FROM {table_name}"
    
    if join_table:
        count_query += f" {join_table}"
        base_query += f" {join_table}"
    
    if where_conditions:
        where_str = " WHERE " + " AND ".join(where_conditions)
        count_query += where_str
        base_query += where_str
    
    return count_query, base_query

# 个股查询类型处理逻辑
ashare_query_builders = {
    AShareQueryType.ALL: lambda table_name, conditions:     # 0-全部
        build_base_query(table_name, "*", where_conditions=conditions),

    AShareQueryType.ALL_COLLECT: lambda table_name, conditions:   # 1-全部，并返回收藏状态字段is_collect，0-未收藏、1-已收藏
        build_base_query(
            table_name, 
            "a.*, CASE WHEN u.id IS NOT NULL THEN 1 ELSE 0 END as is_collect",  # 明确指定a.*避免字段冲突
            join_table=f"left join user_collections u on a.id = u.collectable_id and u.is_deleted = 0 and u.user_id = %(user_id)s and u.collectable_type='{CollectionType.AshareCompany.value}'",
            where_conditions=conditions
        ),
        
    AShareQueryType.COLLECT: lambda table_name, conditions:   # 2-已收藏
        build_base_query(
            table_name, 
            "a.*, 1 as is_collect", 
            join_table=f"inner join user_collections u on a.id = u.collectable_id and u.is_deleted = 0 and u.user_id = %(user_id)s and u.collectable_type='{CollectionType.AshareCompany.value}'",
            where_conditions=conditions
        ),
    
    AShareQueryType.NOT_COLLECT: lambda table_name, conditions:   # 3-未收藏
        build_base_query(
            table_name,
            "a.*, 0 as is_collect",
            where_conditions=[
                f"""
                NOT EXISTS (
                    SELECT 1 
                    FROM user_collections u 
                    WHERE u.is_deleted = 0 and u.user_id = %(user_id)s 
                    AND u.collectable_type = '{CollectionType.AshareCompany.value}'
                    AND u.collectable_id = a.id
                )
                """
            ] + (conditions if conditions else [])
        ),

    AShareQueryType.ALL_SUBSCRIBE: lambda table_name, conditions: # 4-全部，并返回订阅状态字段is_subscribe，0-未订阅、1-已订阅
        build_base_query(
            table_name, 
            "a.*, CASE WHEN u.id IS NOT NULL THEN 1 ELSE 0 END as is_subscribe",  # 明确指定a.*避免字段冲突
            join_table=f"left join user_subscriptions u on a.id = u.subscribable_id and u.is_deleted = 0 and u.user_id = %(user_id)s and u.subscribable_type='{SubscriptionType.AshareCompany.value}'",
            where_conditions=conditions
        ),

    AShareQueryType.SUBSCRIBE: lambda table_name, conditions:     # 5-已订阅
        build_base_query(
            table_name,
            "a.*, 1 as is_subscribe", 
            join_table=f"inner join user_subscriptions u on a.id = u.subscribable_id and u.is_deleted = 0 and u.user_id = %(user_id)s and u.subscribable_type='{SubscriptionType.AshareCompany.value}'",
            where_conditions=conditions
        ),
    
    AShareQueryType.NOT_SUBSCRIBE: lambda table_name, conditions: # 6-未订阅
        build_base_query(
            table_name,
            "a.*, 0 as is_subscribe",
            where_conditions=[
                f"""
                NOT EXISTS (
                    SELECT 1 
                    FROM user_subscriptions u 
                    WHERE u.is_deleted = 0 and u.user_id = %(user_id)s 
                    AND u.subscribable_type = '{SubscriptionType.AshareCompany.value}'
                    AND u.subscribable_id = a.id
                )
                """
            ] + (conditions if conditions else [])
        ),

}


# 获取已收藏的个股ID
async def get_ashare_is_collect_ids(
        ashare_company_ids: list,
        user_id: str
) -> list:
    try:
        connection_pool = get_pool("opportunity")
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 批量检查是否已存在
            sql = f"""
            SELECT collectable_id FROM user_collections 
            WHERE is_deleted = 0 and user_id = %(user_id)s 
              AND collectable_id IN %(collectable_ids)s 
              AND collectable_type = '{CollectionType.AshareCompany.value}'
            """
            cursor.execute(sql, {
                'user_id': user_id,
                'collectable_ids': tuple(ashare_company_ids)
            })
            logger.info(f"获取已收藏的个股ID，SQL: {sql}")
            existing_ids = [row["collectable_id"] for row in cursor.fetchall()]
            logger.info(f"获取已收藏的个股ID，结果：{existing_ids}")

            return existing_ids

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取收藏个股ids！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()

# 获取已订阅的个股ID
async def get_ashare_is_subscribe_ids(
        ashare_company_ids: list,
        user_id: str
) -> list:
    try:
        connection_pool = get_pool("opportunity")
        connection = connection_pool.connect()
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            # 批量检查是否已存在
            sql = f"""
            SELECT subscribable_id FROM user_subscriptions 
            WHERE is_deleted = 0 and user_id = %(user_id)s 
              AND subscribable_id IN %(subscribable_ids)s 
              AND subscribable_type = '{SubscriptionType.AshareCompany.value}'
            """
            cursor.execute(sql, {
                'user_id': user_id,
                'subscribable_ids': tuple(ashare_company_ids)
            })
            logger.info(f"获取已订阅的个股ID，SQL: {sql}")
            existing_ids = [row["subscribable_id"] for row in cursor.fetchall()]
            logger.info(f"获取已订阅的个股ID，结果：{existing_ids}")

            return existing_ids

    except pymysql.OperationalError as e:
        error_str = f"数据库连接异常，正在尝试重连... 错误信息：{str(e)}"
        logger.error(error_str)
        connection = connection_pool.connect()
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    except Exception as e:
        error_str = f"获取订阅个股ids！ 错误信息：{str(e)}"
        logger.error(error_str)
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500,
                            detail=error_str)
    finally:
        if connection:
            connection.close()
