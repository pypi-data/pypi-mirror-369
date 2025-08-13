import asyncio

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import ESTool
from ai_gateway.service.business.opp_es_stock_index_settings import stock_index_settings, stock_index_settings2


async def create_stock_index_main():
    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url,(cfg.user, cfg.password))
    await opp_es_tool.initialize()  # 初始化ES连接池

    await opp_es_tool.create_index(  # 直接调用ES客户端创建索引
        index=cfg.stock_index,
        body=stock_index_settings2
    )
    logger.info(f"索引 {cfg.stock_index} 创建成功")
    await opp_es_tool.close()  # 关闭ES连接池

if __name__ == "__main__":
    asyncio.run(create_stock_index_main())