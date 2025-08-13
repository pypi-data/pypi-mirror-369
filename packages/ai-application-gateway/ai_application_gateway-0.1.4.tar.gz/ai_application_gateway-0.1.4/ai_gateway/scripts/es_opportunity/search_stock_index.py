import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool, ESTool


async def search_stock_index():
    query_body = {
        "query": {
            "match_all": {}
        },
        "size": 100,  # 新增size参数控制返回数量
    }

    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))
    await opp_es_tool.initialize()  # 初始化ES连接池
    result = await opp_es_tool.search(index=cfg.stock_index, body=query_body)

    for hit in result['hits']['hits']:
        logger.debug(f"文档ID: {hit['_id']} 内容: {hit['_source']}")

    logger.info(f"共查询到 {result['hits']['total']['value']} 条，实际按时间降序展示 {len(result['hits']['hits'])} 条")

    await opp_es_tool.close()

if __name__ == "__main__":
    asyncio.run(search_stock_index())