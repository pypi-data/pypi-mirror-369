from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from typing import Optional



# InterfaceLogCreate 修改部分
class InterfaceLogCreate(BaseModel):
    user_id: str = Field(..., max_length=50, description="用户ID", examples=["1"])
    request_id: str = Field(..., max_length=50, description="请求ID", examples=["a720d3c0-ae74-4380-b512-247b42858cb6"])
    code: str = Field(..., max_length=500, description="密钥字符串", examples=["xxx"])
    url: str = Field(..., description="请求url", examples=["http://127.0.0.1:8008/api/v1/demo/simple/post_simple"])
    base_url: str = Field(..., max_length=255, description="站点地址", examples=["http://127.0.0.1:8008"])
    path: str = Field(..., max_length=255, description="请求path", examples=["/api/v1/demo/simple/post_simple"])
    method: str = Field(..., max_length=10, description="请求方式", examples=["POST"])
    request_params: dict = Field(..., description="请求参数", examples=[{
        "query": {
            "item_id": "item-1",
            "query": "查询参数"
        },
        "body": {
            "name": "名称",
            "description": "说明"
        }
    }])
    ip: str = Field(..., max_length=50, description="请求来源ip地址", examples=["127.0.0.1"])
    port: int = Field(..., description="请求来源端口", examples=["8008"])
    request_at: datetime = Field(..., description="请求时间", examples=["2025-03-05T12:41:06.638542"])

    response_json: dict = Field(..., description="响应结果", examples=[{
        "code": 200,
        "message": "success",
        "content": "",
        "items": {
            "item_id": "唯一ID",
            "name": "名称",
            "query": "查询参数",
            "description": "说明",
            "status": "状态",
            "message": "消息"
        }
    }])
    response_time: float = Field(..., description="响应时间", examples=["7922.83"])
    status_code: int = Field(..., description="响应状态码", examples=["200"])
    created: datetime = Field(..., description="日志创建时间", examples=["2025-03-05T12:41:06.638542"])
    updated: datetime = Field(..., description="日志更新时间", examples=["2025-03-05T12:41:06.638542"])
    timestamp: float = Field(..., description="时间戳", examples=["1741149666.123456"])

# InterfaceLogOut 修改部分
class InterfaceLogOut(BaseModel):
    user_id: str = Field(..., max_length=50, description="用户ID", examples=["1"])
    request_id: str = Field(..., max_length=50, description="请求ID", examples=["a720d3c0-ae74-4380-b512-247b42858cb6"])
    code: str = Field(..., max_length=500, description="密钥字符串", examples=["xxx"])
    url: str = Field(..., max_length=255, description="请求url",
                     examples=["http://127.0.0.1:8008/api/v1/demo/simple/post_simple"])
    base_url: str = Field(..., max_length=255, description="站点地址", examples=["http://127.0.0.1:8008"])
    path: str = Field(..., max_length=255, description="请求path", examples=["/api/v1/demo/simple/post_simple"])
    method: str = Field(..., max_length=10, description="请求方式", examples=["POST"])
    request_params: dict = Field(..., description="请求参数", examples=[{
        "query": {
            "item_id": "item-1",
            "query": "查询参数"
        },
        "body": {
            "name": "名称",
            "description": "说明"
        }
    }])
    ip: str = Field(..., max_length=50, description="请求来源ip地址", examples=["127.0.0.1"])
    port: int = Field(..., description="请求来源端口", examples=["8008"])
    request_at: datetime = Field(..., description="请求时间", examples=["2025-03-05T12:41:06.638542"])

    response_json: dict = Field(..., description="响应结果", examples=[{
        "code": 200,
        "message": "success",
        "content": "",
        "items": {
            "item_id": "唯一ID",
            "name": "名称",
            "query": "查询参数",
            "description": "说明",
            "status": "状态",
            "message": "消息"
        }
    }])
    response_time: float = Field(..., description="响应时间", examples=["7922.83"])
    status_code: int = Field(..., description="响应状态码", examples=["200"])

    created: datetime = Field(..., description="日志创建时间", examples=["2025-03-05T12:41:06.638542"])
    updated: datetime = Field(..., description="日志更新时间", examples=["2025-03-05T12:41:06.638542"])
    timestamp: float = Field(..., description="时间戳", examples=["1741149666.123456"])

