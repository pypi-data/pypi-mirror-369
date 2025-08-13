from fastapi import Request, HTTPException
from datetime import datetime, timedelta, timezone
from typing import Union

from jose import jwt,JWTError
from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode


# 创建token
async def create_jwt_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire}) # 仅在提供有效期时添加exp字段
    encoded_jwt = jwt.encode(claims=to_encode, key=config.auth.secret_key, algorithm=config.auth.algorithm)
    return encoded_jwt

# 验证Token
async def verify_jwt_token(access_token: str):
    is_valid = True
    api_key = ""
    error_str = ""
    try:
        payload = jwt.decode(access_token, config.auth.secret_key, algorithms=[config.auth.algorithm])
        api_key: str = payload.get("api_key")
        if api_key is None:
            is_valid = False
    except JWTError as error:
        error_str = str(error)
        is_valid = False
    return is_valid, api_key, error_str

async def get_api_key(access_token: str):
    api_key = ""
    if access_token:
        access_token = access_token.split(' ')[1]
        if access_token:
            is_valid_token, api_key, error_str = await verify_jwt_token(access_token)
    return api_key

# 验证请求Token认证
async def verify_token(request: Request):
    if config.auth.enable:  # 开启难验证
        # 从请求头中提取Bearer Token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise HTTPException(status_code=HttpStatusCode.UNAUTHORIZED_401, detail="身份验证失败：Header 中未收到 Authentication 参数，无法进行身份验证")

        if not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=HttpStatusCode.UNAUTHORIZED_401, detail="身份验证失败：Authentication Token 非法，请传入Bearer 认证")

        access_token = auth_header.split(' ')[1]

        #  判断 token 是否有效
        is_valid_token = False
        error_str = ""
        if access_token:
            is_valid_token, api_key, error_str = await verify_jwt_token(access_token)

        # TODO: 验证api_key是否有访问本接口的权限

        #   token 无效抛出异常
        if not is_valid_token:
            if error_str == "Signature has expired.":
                raise HTTPException(status_code=HttpStatusCode.UNAUTHORIZED_401, detail=f"身份验证失败：Authentication Token 已过期，请重新生成/获取")
            elif error_str == "Signature verification failed.":
                raise HTTPException(status_code=HttpStatusCode.UNAUTHORIZED_401, detail=f"身份验证失败：通过 Authentication Token 的验证失败")
            else:
                raise HTTPException(status_code=HttpStatusCode.UNAUTHORIZED_401, detail=f"身份验证失败：{error_str}")