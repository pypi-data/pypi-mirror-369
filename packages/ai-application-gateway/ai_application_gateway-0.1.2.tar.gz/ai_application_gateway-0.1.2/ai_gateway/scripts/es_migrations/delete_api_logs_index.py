import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool


async def delete_api_logs_index(index):
    
    await es_tool.initialize()
    await es_tool.delete_index(index=index)
    logger.info(f"索引 {index} 删除成功")
    await es_tool.close()

if __name__ == "__main__":
    asyncio.run(delete_api_logs_index(config.es.ai_gateway_api_logs_index))