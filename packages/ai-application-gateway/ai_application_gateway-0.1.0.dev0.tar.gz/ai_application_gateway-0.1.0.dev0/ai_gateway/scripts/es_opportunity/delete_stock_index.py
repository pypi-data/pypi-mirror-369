import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import ESTool


async def delete_stock_index():
    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))
    await opp_es_tool.initialize()
    await opp_es_tool.delete_index(index=cfg.stock_index)
    logger.info(f"索引 {cfg.stock_index} 删除成功")
    await opp_es_tool.close()

if __name__ == "__main__":
    asyncio.run(delete_stock_index())