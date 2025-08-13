import json
from datetime import timedelta

from fastapi import APIRouter,Path

from ai_gateway.core.token import create_jwt_token
from ai_gateway.config import config
from loguru import logger

auth_router = APIRouter()


@auth_router.post("/token/{api_key}",summary="获取 access_token", response_description="返回 access_token 等信息")
async def create_access_token(api_key:str = Path(title="api_key", description="传入api_key")) -> dict:
    """
    通过 api_key 获取 access_token
    """
    api_key_json_str = json.dumps(config.auth.api_key)
    api_key_dict = json.loads(api_key_json_str)
    api_key_list = list(api_key_dict.values())

    if(api_key in api_key_list):
        access_token_expires = None
        if config.auth.expire_day > 0:
            access_token_expires = timedelta(days=config.auth.expire_day)
        access_token = await create_jwt_token(
            data={"api_key": api_key}, expires_delta=access_token_expires
        )

        logger.info(f"创建access_token成功: {access_token}")
        if config.auth.expire_day > 0:
            return {
                "access_token" : access_token,
                "expires_day" : config.auth.expire_day
            }
        else:
            return {
                "access_token" : access_token
            }
    else:
        logger.error(f"无效的 api_key: {api_key}")
        return {
            "error": "无效的 api_key ：" + api_key,
        }