"""
插入股票测试数据到ES
"""
import asyncio
import json
import os

from loguru import logger

from ai_gateway.config import config
from ai_gateway.dbs.es_tool import ESTool
from ai_gateway.service.business.opp_es_stock_index_settings import stock_index_settings, stock_index_settings2
# 使用pypinyin库预处理数据
from pypinyin import pinyin, Style

async def insert_stock_data():
    # 从JSON文件加载股票数据
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'stock_index.json')
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"股票数据文件 {json_path} 未找到，请确保文件已放置于脚本目录")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        stock_items = data['items']
    
    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))
    await opp_es_tool.initialize()
    
    # 批量插入数据 - 修正格式
    bulk_actions = []
    for item in stock_items:
        # 增加是否有公告字段 1有 / 0 无
        # if item['stock_code'] == '002566.SZ': # 益盛药业
        #     item["exist_anns"] = 0
        # else:
        #     item["exist_anns"] = 1

        # 全拼转换
        full_pinyin = ''.join([item[0] for item in pinyin(item["comp_name"], style=Style.NORMAL)])
        # 首字母简拼
        abbrev = ''.join([item[0][0] for item in pinyin(item["comp_name"], style=Style.FIRST_LETTER)])

        item["stock_suggest"] = {
            "input": [item["stock_code"], item["comp_name"], full_pinyin, abbrev],
            "weight": 10
        }

        # 添加索引操作指令
        bulk_actions.append({"index": {"_index": cfg.stock_index2}})
        # 添加文档数据
        bulk_actions.append(item)
    
    # 执行批量插入
    if bulk_actions:
        try:
            result = await opp_es_tool.bulk(bulk_actions)
            logger.info(f"成功插入 {len(result['items'])} 条股票数据")
            logger.debug(f"插入结果: {result}")
        except Exception as e:
            logger.error(f"批量插入失败: {str(e)}")
            raise
    
    await opp_es_tool.close()

async def main():
    # 1. 创建索引
    cfg = config.opportunity.es
    opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))
    await opp_es_tool.initialize()
    
    # 检查索引是否存在，不存在则创建
    if not await opp_es_tool.index_exists(cfg.stock_index2):
        await opp_es_tool.create_index(
            index=cfg.stock_index2,
            body=stock_index_settings2
        )
        logger.info(f"索引 {cfg.stock_index2} 创建成功")
    else:
        logger.info(f"索引 {cfg.stock_index2} 已存在")
    
    await opp_es_tool.close()
    
    # 2. 插入数据
    await insert_stock_data()

if __name__ == "__main__":
    asyncio.run(main())