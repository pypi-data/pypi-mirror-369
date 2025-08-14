import asyncio
import os
from loguru import logger

from ai_gateway.service.business.opp_pymysql_tool import connection_pool
import json

async def business_opportunities_insert():
    connection = connection_pool.connect()
    cursor = connection.cursor()
    
    # 读取JSON文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'data_business_opportunities/business_opportunities5.json')

    if not os.path.exists(json_path):
        logger.error(f"商机数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
        raise FileNotFoundError(f"商机数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        stock_items = data['items']
    
    total_count = len(stock_items)
    success_count = 0
    logger.info(f"开始插入商机数据，共 {total_count} 条记录")
    
    # 插入商机数据
    for item in data['items']:
        try:
            insert_sql = """
            INSERT INTO business_opportunities (
                id, s_info_windcode, S_INFO_NAME, S_INFO_COMPNAME, province, city, region,
                S_INFO_EXCHMARKET, S_INFO_LISTBOARDNAME, company_type, citic_industry_l3,
                enterprise_circle_label, honor_qualification_label, insight_url, logo_url,
                ann_dt, ann_type, cross_border_opp, ann_original, business_opp_desc,
                ann_object_id, is_hot, total_fin_amt, idle_raised_funds, idle_own_funds,
                fin_term, fin_type, shareholder, shareholder_type, reduction_method,
                planned_reduction_quantity, planned_reduction_percentage, actual_reduction_quantity,
                actual_reduction_percentage, shareholding_percentage, share_source,
                exist_concerted_actor, combined_shareholding_percentage, ashare_company_id, 
                is_purchased, am_prod_intention, fin_prod_category,
                is_delist
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            cursor.execute(insert_sql, (
                item['id'], item['s_info_windcode'], item['S_INFO_NAME'], item['S_INFO_COMPNAME'],
                item['province'], item['city'], item['region'], item['S_INFO_EXCHMARKET'],
                item['S_INFO_LISTBOARDNAME'], item['company_type'], item['citic_industry_l3'],
                item['enterprise_circle_label'], item['honor_qualification_label'],
                item['insight_url'], item['logo_url'], item['ann_dt'], item['ann_type'],
                item['cross_border_opp'], item['ann_original'], item['business_opp_desc'],
                item['ann_object_id'], item['is_hot'], item['total_fin_amt'],
                item['idle_raised_funds'], item['idle_own_funds'], item['fin_term'],
                item['fin_type'], item['shareholder'], item['shareholder_type'],
                item['reduction_method'], item['planned_reduction_quantity'],
                item['planned_reduction_percentage'], item['actual_reduction_quantity'],
                item['actual_reduction_percentage'], item['shareholding_percentage'],
                item['share_source'], item['exist_concerted_actor'],
                item['combined_shareholding_percentage'],
                item['ashare_company_id'],
                item['is_purchased'], item['am_prod_intention'], item['fin_prod_category'],
                item['is_delist']
            ))
            success_count += 1
        except Exception as e:
            logger.error(f"插入记录失败: {item['id']} - {item['S_INFO_NAME']}, 错误: {str(e)}")
            return
    
    connection.commit()
    cursor.close()
    connection.close()
    
    logger.info(f"商机数据插入完成，共处理 {total_count} 条记录，成功 {success_count} 条")

if __name__ == "__main__":
    asyncio.run(business_opportunities_insert())