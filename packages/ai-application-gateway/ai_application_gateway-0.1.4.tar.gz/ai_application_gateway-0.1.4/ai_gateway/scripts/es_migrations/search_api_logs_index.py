import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool


async def search_api_logs_index(index):
    query_body = {
        "query": {
            "match_all": {}
        },
        "size": 100,  # 新增size参数控制返回数量
        "sort": [  # 新增排序参数
            {"timestamp": {"order": "desc"}}  # 按时间字段降序排列
        ]
    }

    await es_tool.initialize()
    result = await es_tool.search(index=index, body=query_body)

    for hit in result['hits']['hits']:
        logger.debug(f"文档ID: {hit['_id']} 内容: {hit['_source']}")

    logger.info(f"共查询到 {result['hits']['total']['value']} 条日志，实际按时间降序展示 {len(result['hits']['hits'])} 条")

    await es_tool.close()

if __name__ == "__main__":
    asyncio.run(search_api_logs_index(config.es.ai_gateway_api_logs_index))