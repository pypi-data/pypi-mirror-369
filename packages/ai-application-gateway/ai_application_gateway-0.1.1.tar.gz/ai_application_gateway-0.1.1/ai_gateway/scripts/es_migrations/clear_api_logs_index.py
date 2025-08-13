import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool

async def clear_api_logs_index_main(index):
    await es_tool.initialize()  # 初始化ES连接池
    
    # 执行删除所有文档的操作（保留索引结构）
    await es_tool.es.delete_by_query(
        index=index,
        body={"query": {"match_all": {}}}
    )
    
    logger.info(f"索引 {index} 数据已清空")
    await es_tool.close()  # 关闭ES连接池

if __name__ == "__main__":
    asyncio.run(clear_api_logs_index_main(config.es.ai_gateway_api_logs_index))