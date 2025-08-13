import uvicorn
import argparse
import os
from fastapi import FastAPI, Request

from ai_gateway.core.init_app import app, lifespan, openapi
from config import config

from ai_gateway.core.init_app import app

# FastApiMCP 测试 -----------------------------------------------------
from fastapi_mcp import FastApiMCP

# 安全处理TAGS环境变量，支持多种来源
def get_tags_from_request(request: Request = None):
    """从请求中获取TAGS参数"""
    # 优先级：环境变量 > 请求头 > 查询参数 > 默认值
    tags = None
    
    # 1. 从环境变量获取
    tags = os.getenv('TAGS')
    
    # 2. 如果有request对象，尝试从请求中获取
    if request:
        # 从查询参数获取
        if not tags and hasattr(request, 'query_params'):
            tags = request.query_params.get('TAGS')
        
        # 从请求头获取
        if not tags and hasattr(request, 'headers'):
            tags = request.headers.get('X-Tags')
    
    # 处理tags
    if tags:
        return list(map(str.strip, tags.split(',')))
    else:
        # 默认标签
        return ["业务服务：商机挖掘", "业务服务：A股分红"]

# 安全处理TOKEN环境变量，支持多种来源
def get_token_from_request(request: Request = None):
    """从请求中获取TOKEN参数"""
    # 优先级：环境变量 > 请求头 > 查询参数
    token = None
    
    # 1. 从环境变量获取
    token = os.getenv('TOKEN')
    
    # 2. 如果有request对象，尝试从请求中获取
    if request:
        # 从查询参数获取
        if not token and hasattr(request, 'query_params'):
            token = request.query_params.get('TOKEN')
        
        # 从请求头获取（支持Bearer格式）
        if not token and hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]  # 去掉'Bearer '
            elif auth_header:
                token = auth_header
    
    return token

# 获取参数
include_tags = get_tags_from_request()
token = get_token_from_request()

@app.get("/")
async def hello_fastapi_mcp():
    return "hello_fastapi_mcp"

@app.get("/users/{user_id}", operation_id="get_user_info")
async def read_user(user_id: int):
    return {"user_id": user_id}

# 创建 MCP 服务器
fastapi_mcp = FastApiMCP(
    app,
    name="AI 应用网关 MCP",                        # MCP 名称
    describe_all_responses=True,          # 展示所有响应模型
    describe_full_response_schema=True,   # 展示完整 JSON 模式
    # include_tags=include_tags,           # 只暴露带有这些标签的组件
    include_operations=["ashare_companies"] # 只暴露带有这些 operation_id 的接口，fastmcp不支持此参数
)

# 挂载 MCP
# mcp.mount()


# 单独的 FastAPI 应用
# mcp_app = FastAPI()
# fastapi_mcp_app = FastAPI(
#     title="AI 应用网关",
#     description="AI 应用网关接口说明及测试",
#     openapi_url="/api/v1/openapi.json",
#     lifespan=lifespan,
#     **openapi,
# )

# # 给 mcp_app 增加，无效
# @fastapi_mcp_app.get("/hello_mcp")
# async def hello_mcp():
#     return "hello_mcp"
#
# # 在 FastApiMCP( 之后加载，无效
# @app.get("/users/{user_name}", operation_id="get_user_name")
# async def read_user_name(user_name: str):
#     return {"user_name": user_name}

# fastapi_mcp.mount(fastapi_mcp_app, mount_path="/mcp") # 将FastApiMCP挂载到mcp_app
fastapi_mcp.mount(app, mount_path="/mcp") # 将FastApiMCP挂载到mcp_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=config.listen_host, help="Host to listen on")
    parser.add_argument(
        "--port", type=int, default=config.listen_port_mcp, help="Port to listen on"
    )
    parser.add_argument(
        "--debug", type=bool, default=config.debug, help="Enable or disable debug mode"
    )
    parser.add_argument(
        "--is_reload", type=bool, default=config.is_reload, help="Enable or disable reload mode"
    )
    args = parser.parse_args()

    uvicorn.run(
        # "ai_gateway.main_fastapi_mcp:fastapi_mcp_app",
        "ai_gateway.core.init_app:app",
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        reload=args.is_reload,
        lifespan="on",
        loop="asyncio",
        workers=config.workers,
    )

if __name__ == "__main__":
    main()

