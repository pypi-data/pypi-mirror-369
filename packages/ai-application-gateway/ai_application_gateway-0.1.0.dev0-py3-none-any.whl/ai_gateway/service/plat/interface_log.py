import json
from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
import time
import uuid

from loguru import logger

from ai_gateway.config import config
from ai_gateway.curd.plat.interface_log import crud_interface_log
from ai_gateway.dbs.db import get_db
from ai_gateway.dbs.es_tool import es_tool
from ai_gateway.schemas.api.plat.interface_log import InterfaceLogOut, InterfaceLogCreate
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.scripts.es_migrations.create_api_logs_index import api_logs_index_mappings


async def interface_log_save(log_data:InterfaceLogCreate) -> InterfaceLogOut:  # 添加async
    """
    将日志数据写入 Database或Elasticsearch
    """
    try:
        if config.interface_log.database: # 日志写入数据库

            db_gen = None  # 提前初始化用于 finally 块
            try:
                db_gen = get_db()

                # 使用更规范的异步迭代语法
                async for db in db_gen:
                    # 转换字典为JSON字符串
                    request_params_str = json.dumps(log_data.request_params, ensure_ascii=False)
                    response_json_str = json.dumps(log_data.response_json, ensure_ascii=False)

                    new_interface_log = await crud_interface_log.create_log(
                        user_id=log_data.user_id,
                        request_id=log_data.request_id,
                        code=log_data.code,
                        url=log_data.url,
                        base_url=log_data.base_url,
                        path=log_data.path,
                        method=log_data.method,
                        request_params=request_params_str,  # 传入字符串
                        ip=log_data.ip,
                        port=log_data.port,
                        request_at=log_data.request_at,
                        response_json=response_json_str,  # 传入字符串
                        response_time=log_data.response_time,
                        status_code=log_data.status_code,
                        created=log_data.created,
                        updated=log_data.updated,
                        timestamp=log_data.timestamp,
                        db=db
                    )

            except StopAsyncIteration as e:
                logger.error(f"日志数据库连接异常: {str(e)}")
            except Exception as e:
                logger.opt(exception=True).error(f"写入日志错误信息: {str(e)}")
            finally:
                # 使用更健壮的资源清理方式
                if db_gen is not None:
                    try:
                        await db_gen.aclose()
                    except Exception as e:
                        logger.warning(f"关闭数据库连接异常: {str(e)}")



        if config.interface_log.elasticsearch: # 日志写入 ES
            # 添加索引检查逻辑
            index = config.es.ai_gateway_api_logs_index
            if not await es_tool.es.indices.exists(index=index):
                await es_tool.es.indices.create(index=index, body=api_logs_index_mappings)  # 如果没有创建索引，则索引字段类型按定义的严格映射

            res = await es_tool.index(
                index=config.es.ai_gateway_api_logs_index,
                body=log_data.model_dump()
            )
        return log_data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500, detail=f"日志写入Elasticsearch错误: {str(e)}")  # 修正异常参数
