"""
标准示例：大模型请求 API 路由
"""
from typing import Dict

from fastapi import APIRouter, Request, Query

from ai_gateway.core.middleware import trace_request
from ai_gateway.schemas.api.base import RspDetail
from ai_gateway.utils.citics_gpt import citics_gpt
from enum import Enum

llm_router = APIRouter(prefix="/demo/llm")


class LLMModelName(str, Enum):
    QWEN_CHAT = "qwen-chat"
    QWEN25 = "qwen25"
    QWEN2 = "qwen2"
    QWEN_110 = "qwen-110"
    GPT4O = "gpt-4o"
    CITICS_LARGE = "citics-large"
    CITICS_MEDIUM = "citics-medium"

@llm_router.post("/citics_llm", summary="citics llm", response_description="返回 llm答案" , response_model=RspDetail[Dict])
@trace_request
async def citics_llm(
    request: Request,
    model: LLMModelName = Query(default=LLMModelName.QWEN25, description="模型", examples=["qwen-chat", "qwen25", "qwen2", "qwen-110", "gpt-4o", "citics-large", "citics-medium"]),
    messages: str = Query(default="你是谁？你是GPT吗？", description="问题"),
    temperature: float = Query(default=0.9, description="采样温度"),
):
    """citics llm"""
    res = citics_gpt(
        [{"role": "user", "content": messages}],
        model=model,
        temperature=temperature,
    )

    return RspDetail(items=res)
