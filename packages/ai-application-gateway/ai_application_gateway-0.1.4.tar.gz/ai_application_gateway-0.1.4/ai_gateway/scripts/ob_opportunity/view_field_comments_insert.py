import asyncio
import os
from loguru import logger

from ai_gateway.service.business.opp_pymysql_tool import connection_pool
import json

async def view_field_comments_insert():
    connection = connection_pool.connect()
    cursor = connection.cursor()
    
    # 读取JSON文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'view_field_comments.json')
    
    if not os.path.exists(json_path):
        logger.error(f"字段注释数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
        raise FileNotFoundError(f"字段注释数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        field_items = data['items']
    
    total_count = len(field_items)
    success_count = 0
    logger.info(f"开始插入字段注释数据，共 {total_count} 条记录")
    
    # 插入字段注释数据
    for item in field_items:
        try:
            insert_sql = """
            INSERT INTO view_field_comments (
                id, view_name, field_name, comment, field_type
            ) VALUES (
                %s, %s, %s, %s, %s
            )
            """
            cursor.execute(insert_sql, (
                item['id'], item['view_name'], item['field_name'], 
                item['comment'], item['field_type']
            ))
            success_count += 1
        except Exception as e:
            logger.error(f"插入记录失败: {item['id']} - {item['field_name']}, 错误: {str(e)}")
            return
    
    connection.commit()
    cursor.close()
    connection.close()
    
    logger.info(f"字段注释数据插入完成，共处理 {total_count} 条记录，成功 {success_count} 条")

if __name__ == "__main__":
    asyncio.run(view_field_comments_insert())