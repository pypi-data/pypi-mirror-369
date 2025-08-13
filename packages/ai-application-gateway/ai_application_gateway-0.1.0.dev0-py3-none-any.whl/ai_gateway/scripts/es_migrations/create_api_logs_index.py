import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool

api_logs_index_mappings = {
    "mappings": {
        "properties": {
            "user_id": {"type": "keyword"},
            "request_id": {"type": "keyword"},
            "code": {"type": "keyword"},
            "url": {"type": "keyword"},
            "base_url": {"type": "keyword"},
            "path": {"type": "keyword"},
            "method": {"type": "keyword"},
            "request_params": {"type": "object"
               ,"dynamic": False     # 关闭自动映射。不会自动为文档中的新字段创建映射，但新字段的数据仍会被存储（只是不会被索引）
            },
            "ip": {"type": "ip"},
            "port": {"type": "integer"},
            "request_at": {"type": "date"},
            "response_json": {
                "type": "object"
                ,"dynamic": False     # 关闭自动映射。不会自动为文档中的新字段创建映射，但新字段的数据仍会被存储（只是不会被索引）
            },
            "response_time": {"type": "float"},
            "status_code": {"type": "integer"},
            "created": {"type": "date"},
            "updated": {"type": "date"},
            "is_deleted": {"type": "integer"},
            "timestamp": {"type": "float"}
        }
    }
}

async def create_api_logs_index_main(index):
    await es_tool.initialize()  # 初始化ES连接池
    await es_tool.create_index(  # 直接调用ES客户端创建索引
        index=index,
        body=api_logs_index_mappings
    )
    logger.info(f"索引 {index} 创建成功")
    await es_tool.close()  # 关闭ES连接池

if __name__ == "__main__":
    asyncio.run(create_api_logs_index_main(config.es.ai_gateway_api_logs_index))