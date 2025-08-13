import asyncio
import os
from loguru import logger

from ai_gateway.service.business.opp_pymysql_tool import connection_pool
import json

async def ashare_companies_insert():
    connection = connection_pool.connect()
    cursor = connection.cursor()
    
    # 读取JSON文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'data_ashare_companies/ashare_companies5.json')

    if not os.path.exists(json_path):
        logger.error(f"A股公司数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
        raise FileNotFoundError(f"A股公司数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        stock_items = data['items']
    
    total_count = len(stock_items)
    success_count = 0
    logger.info(f"开始插入A股公司数据，共 {total_count} 条记录")
    
    # 插入A股公司数据
    for item in data['items']:
        try:
            insert_sql = """
            INSERT INTO ashare_companies (
                id, s_info_windcode, S_INFO_NAME, S_INFO_COMPNAME, province, city, region,
                S_INFO_EXCHMARKET, S_INFO_LISTBOARDNAME, company_type, citic_industry_l3,
                enterprise_circle_label, honor_qualification_label, insight_url, logo_url,
                total_mv, statc_dt, created_at, updated_at, deleted_at, is_delist
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            cursor.execute(insert_sql, (
                item['id'], item['s_info_windcode'], item['S_INFO_NAME'], item['S_INFO_COMPNAME'],
                item['province'], item['city'], item['region'], item['S_INFO_EXCHMARKET'],
                item['S_INFO_LISTBOARDNAME'], item['company_type'], item['citic_industry_l3'],
                item['enterprise_circle_label'], item['honor_qualification_label'],
                item['insight_url'], item['logo_url'], item['total_mv'],
                item['statc_dt'], item['created_at'], item['updated_at'], item['deleted_at'], item['is_delist']
            ))
            success_count += 1
        except Exception as e:
            logger.error(f"插入记录失败: {item['id']} - {item['S_INFO_NAME']}, 错误: {str(e)}")
            return
    
    connection.commit()
    cursor.close()
    connection.close()
    
    logger.info(f"A股公司数据插入完成，共处理 {total_count} 条记录，成功 {success_count} 条")

if __name__ == "__main__":
    asyncio.run(ashare_companies_insert())