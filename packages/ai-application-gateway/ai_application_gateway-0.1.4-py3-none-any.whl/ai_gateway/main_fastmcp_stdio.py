# FastMCP 测试 -----------------------------------------------------
import os

from fastmcp import FastMCP

from ai_gateway.core.init_app import app

print("Token:", os.getenv('TOKEN'))

# 关键集成步骤，自动转换路由
fastmcp_opp_app = FastMCP.from_fastapi(
    app=app,
    # include_tags=["业务服务：商机挖掘", "业务服务：A股分红"],
    include_tags=list(map(str.strip, os.getenv('TAGS').split(','))),
    # exclude_tags=["test"],
    httpx_client_kwargs={
        "headers": {"Authorization": f"Bearer {os.getenv('TOKEN')}"}
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
@fastmcp_opp_app.tool
async def hello_fastmcp():
    return "hello_fastmcp"

if __name__ == "__main__":
    print("FastMCP 测试")
    print("Main Token:", os.getenv('TOKEN'))
    fastmcp_opp_app.run(transport="stdio")
    # fastmcp_app.run(transport="streamable-http", host="127.0.0.1", port=8089, path="/mcp")