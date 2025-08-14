import asyncio
import argparse
from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import es_tool, ESTool, opp_es_tool
from ai_gateway.service.business.opp_es_query_stock_body import get_query_stock_body


async def search_stock_index(keyword):
    query_body = get_query_stock_body(keyword, 5)
    logger.info(f"query_body: {query_body}")

    cfg = config.opportunity.es
    await opp_es_tool.initialize()  # 初始化ES连接池
    result = await opp_es_tool.search(index=cfg.stock_index, body=query_body)

    for hit in result['hits']['hits']:
        logger.debug(hit)
        # logger.debug(f"文档ID: {hit['_id']} 内容: {hit['_source']}")
        # 新增高亮结果打印
        if 'highlight' in hit:
            logger.info(f"高亮结果: {hit['highlight']}")

    logger.info(f"共查询到 {result['hits']['total']['value']} 条，实际按时间降序展示 {len(result['hits']['hits'])} 条")

    await opp_es_tool.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='搜索股票索引')
    parser.add_argument('--keyword', type=str, required=True, help='搜索关键词')
    args = parser.parse_args()
    asyncio.run(search_stock_index(args.keyword))