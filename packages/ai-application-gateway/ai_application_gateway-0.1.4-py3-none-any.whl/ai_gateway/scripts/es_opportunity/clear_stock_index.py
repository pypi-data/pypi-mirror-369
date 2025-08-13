import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import ESTool


async def clear_stock_index_main():
    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))
    await opp_es_tool.initialize()

    # 执行删除所有文档的操作（保留索引结构）
    await opp_es_tool.es.delete_by_query(
        index=cfg.stock_index,
        body={"query": {"match_all": {}}}
    )

    logger.info(f"索引 {cfg.stock_index} 数据已清空")

    await opp_es_tool.close()

if __name__ == "__main__":
    asyncio.run(clear_stock_index_main())