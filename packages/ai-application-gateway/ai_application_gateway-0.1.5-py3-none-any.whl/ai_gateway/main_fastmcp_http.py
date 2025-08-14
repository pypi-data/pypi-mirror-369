# FastMCP 测试 -----------------------------------------------------
import argparse
import os

import uvicorn
from fastmcp import FastMCP

from ai_gateway.config import config
from ai_gateway.core.init_app import app, lifespan
from fastapi import Request

# 关键集成步骤，自动转换路由
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


# 关键集成步骤，自动转换路由
fastmcp_http_app = FastMCP.from_fastapi(
    app=app,
    lifespan=lifespan,  # 关键：传递同一生命周期
    include_tags=include_tags,
    httpx_client_kwargs={
        "headers": {"Authorization": f"Bearer {token}"} if token else {}
    }
)

# 以下是FastMCP初始化参数的详细解释：
# 1. `name="ConfiguredServer"` - 设置服务器名称，用于标识该FastMCP实例
# 2. `dependencies=["requests", "pandas>=2.0.0"]` - 指定服务器依赖的Python包及其版本要求
# 3. `include_tags={"public", "api"}` - 只暴露带有这些标签的组件
# 4. `exclude_tags={"internal", "deprecated"}` - 隐藏带有这些标签的组件
# 5. `on_duplicate_tools="error"` - 当注册重复工具时的处理方式(报错)
# 6. `on_duplicate_resources="warn"` - 当注册重复资源时的处理方式(警告)
# 7. `on_duplicate_prompts="replace"` - 当注册重复提示时的处理方式(替换)
# 8. `include_fastmcp_meta=False` - 禁用FastMCP元数据，使集成更简洁

# 给 mcp_app 增加，有效
@fastmcp_http_app.tool
async def hello_fastmcp():
    return "hello_fastmcp"

# if __name__ == "__main__":
#     print("FastMCP 测试")
#     print("Main Token:", os.getenv('TOKEN'))
#     # fastmcp_http_app.run(transport="stdio")
#     fastmcp_http_app.run(transport="streamable-http", host="127.0.0.1", port=8089, path="/mcp")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=config.listen_host, help="Host to listen on")
    parser.add_argument(
        "--port", type=int, default=config.listen_port_fastmcp, help="Port to listen on"
    )
    parser.add_argument(
        "--debug", type=bool, default=config.debug, help="Enable or disable debug mode"
    )
    parser.add_argument(
        "--is_reload", type=bool, default=config.is_reload, help="Enable or disable reload mode"
    )
    args = parser.parse_args()

    # 获取FastMCP的ASGI应用，确保生命周期正确传递
    mcp_asgi_app = fastmcp_http_app.http_app()
    
    uvicorn.run(
        mcp_asgi_app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        reload=False,
        lifespan="on",
        loop="asyncio",
        workers=1,
    )

if __name__ == "__main__":
    main()