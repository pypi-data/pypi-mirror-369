import json

import httpx

from fastapi import Request, HTTPException
from httpx import ConnectError

from ai_gateway.schemas.errors import HttpStatusCode, ErrorCode


class HttpForwarder:
    def __init__(self, target_url):
        self.target_url = target_url
        self.headers = {"Content-Type": "application/json"}

    async def forward_data(self, method: str, path: str, headers=None, json_data=None, params=None, timeout=10):
        url = f"{self.target_url}{path}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, headers=headers, json=json_data, params=params)
            return response.status_code, response.headers, response.text

    @staticmethod
    async def extract_params(request: Request):
        return dict(request.query_params)

    async def get_data(self, path: str, request: Request, params=None, json_data=None, timeout=10, headers=None):
        if headers is None:
            headers = self.headers
            if authorization := request.headers.get("Authorization"):
                headers["authorization"] = authorization
        method = request.method
        return await self.forward_data(method, path, headers=headers, json_data=json_data, params=params, timeout=timeout)


async def get_request_items(target_url:str, path: str, request: Request, data=None, params=None, headers=None, timeout=10):
        if headers is None:
            headers = {"Content-Type": "application/json"}
            if authorization := request.headers.get("Authorization"):
                headers["authorization"] = authorization
        method = request.method
        return await get_items(method, target_url, path, headers, data, params, timeout)


async def get_items(method: str, target_url:str, path: str, headers=None, data=None, params=None, timeout=10):
    json_data = data if data is None else json.loads(data.model_dump_json())
    try:
        _status_code, _headers, _text = await HttpForwarder(target_url).forward_data(method, path, headers=headers, json_data=json_data, params=params, timeout=timeout)

        if _status_code != HttpStatusCode.SUCCESS_200:
            raise HTTPException(status_code=_status_code, detail=_text)

        json_text = json.loads(_text)
        if "code" in json_text and json_text["code"] != ErrorCode.SUCCESS_200:
            raise HTTPException(status_code=_status_code, detail=_text)

        items = None if "items" not in json_text else json_text["items"]
        return items
    except ConnectError as e:
        raise HTTPException(status_code=HttpStatusCode.INTERNAL_SERVER_ERROR_500, detail=f"{target_url} 连接错误，请稍后重试。")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
