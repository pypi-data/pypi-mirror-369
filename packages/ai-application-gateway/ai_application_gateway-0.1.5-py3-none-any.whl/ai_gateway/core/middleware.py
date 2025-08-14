import time
import uuid
from functools import wraps
import json
from typing import Callable
from datetime import datetime

from loguru import logger
from prometheus_client import Counter, Histogram
from ai_gateway.core.token import get_api_key
from ai_gateway.schemas.api.plat.interface_log import InterfaceLogCreate
from ai_gateway.service.plat.interface_log import interface_log_save

# 定义 Prometheus 指标
# 请求计数器：记录HTTP请求的总次数，只增不减，用于统计请求量、错误率等累积值。
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests count',
    ['method', 'endpoint', 'status']
)
# 请求延迟直方图：统计HTTP请求耗时的分布情况（如P50/P90/P99分位数），适用于分析延迟、响应时间等。
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# 按照优先级顺序获取user_id：path > query > body
# 只有在高优先级未获取到user_id时，才会尝试从下一优先级获取
async def _extract_user_id(params: dict, source: str) -> str:
    """从指定参数源提取user_id"""
    return params.get(source, {}).get("user_id", "")

async def get_request_params(request) -> tuple[dict, str]:
    params = {}
    user_id = ""

    # 处理路径参数
    if request.path_params:
        params["path"] = dict(request.path_params)
        # 优先从path参数获取user_id
        user_id = await _extract_user_id(params, "path")
    
    # 处理查询参数
    if not user_id and request.query_params:
        params["query"] = dict(request.query_params)
        # 其次从query参数获取user_id
        user_id = await _extract_user_id(params, "query")
    
    # 处理请求体
    if not user_id and request.method in ["POST", "PUT", "PATCH"]:
        try:
            params["body"] = await request.json()
            # 最后从body参数获取user_id
            user_id = await _extract_user_id(params, "body")
        except json.JSONDecodeError:
            params["body"] = None
        except Exception:
            params["body"] = None
            
    return params, user_id

def trace_request(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从 kwargs 中获取 request
        request = kwargs.get('request')
        
        if not request:
            raise ValueError("Request object not found in function arguments")
        
        # 从请求头中提取Bearer Token
        auth_header = request.headers.get('Authorization')
        code = await get_api_key(auth_header)   #API_KEY
        # 生成请求追踪信息
        # 根据请求方法获取参数
        request_params, user_id = await get_request_params(request)

        # 使用构造参数规范初始化（代替逐个属性赋值）
        trace_info = InterfaceLogCreate(
            user_id=user_id,
            request_id=str(uuid.uuid4()),
            code=code,
            url=str(request.url),
            base_url=str(request.base_url),
            path=request.url.path,
            method=request.method,
            request_params=request_params,
            ip=request.client.host,
            port=request.client.port,
            request_at=datetime.now(),
            timestamp=float(time.time()),
            # 以下字段将在 finally 块中补充
            response_json={},
            response_time=0.0,
            status_code=200,
            created=datetime.now(),
            updated=datetime.now()
        )

        # 记录开始时间
        start_time = time.time()
        status = 200
        response_json:dict = {}
        try:
            response = await func(*args, **kwargs)
            # response_json:dict = json.loads(json.dumps(response.json(), ensure_ascii=False))
            response_json:dict = json.loads(response.json())
            status = getattr(response, 'status_code', 200)
        except Exception as e:
            status = 500
            raise e
        finally:
            # 记录 Prometheus 指标
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

            trace_info.response_json = response_json
            trace_info.response_time = round(duration * 1000, 2)
            trace_info.status_code = status
            trace_info.created = datetime.now()
            trace_info.updated = datetime.now()

            logger.info("接口调用日志："+trace_info.json())

            # log_to_es(trace_info)
            # interface_log = InterfaceLogCreate(**trace_info)
            await interface_log_save(trace_info)

        return response
    return wrapper