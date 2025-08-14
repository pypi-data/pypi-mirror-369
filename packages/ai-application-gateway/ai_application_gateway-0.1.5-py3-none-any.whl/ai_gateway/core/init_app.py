import os
from contextlib import asynccontextmanager
from typing import Union, List

from fastapi import FastAPI, HTTPException, Request, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.params import Query
from starlette.responses import JSONResponse, HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.staticfiles import StaticFiles

from ai_gateway.api import api_router
from ai_gateway.config import config
from ai_gateway.core import log
from ai_gateway.core.schedule import scheduler
from ai_gateway.schemas.api.base import RspDetail, RspBase
from ai_gateway.dbs.db import mysql_sessionmanager, ob_sessionmanager
from ai_gateway.dbs.es_tool import es_tool, opp_es_tool
from ai_gateway.dbs.redis_tool import RedisTool

openapi = {} if config.swagger.enable else {"docs_url": None, "redoc_url": None}


def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_favicon_url="/static/favicon.ico?v=1.0",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


# Actual monkey patch
applications.get_swagger_ui_html = swagger_monkey_patch


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化日志
    log.init()

    # 初始化数据库连接
    if config.database.db_type == "oceanbase":
        await ob_sessionmanager.init_db()
    elif config.database.db_type == "mysql":
        await mysql_sessionmanager.init_db()

    if config.es.enable:  # 启用 ES
        # 初始化ES连接池
        await es_tool.initialize()

    if config.opportunity.es.enable:  # 启用 商机ES
        # 初始化ES连接池
        await opp_es_tool.initialize()

    # 初始化调度器
    # scheduler = init_scheduler()
    scheduler.start()

    yield

    if config.database.db_type == "oceanbase":
        await ob_sessionmanager.close()
    elif config.database.db_type == "mysql":
        await mysql_sessionmanager.close()

    if config.es.enable:  # 关闭 ES
        # 关闭ES连接池
        await es_tool.close()

    if config.opportunity.es.enable:  # 关闭商机 ES
        # 关闭ES连接池
        await opp_es_tool.close()

    # 新增Redis连接关闭
    await RedisTool.close_all()

    # 关闭调度器
    scheduler.shutdown()


app = FastAPI(
    title="API 看板服务",
    description="API 看板服务接口说明及测试",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
    **openapi,
)

# 加载static静态文件路由
current_dir = os.path.dirname(__file__)
static_path = os.path.abspath(os.path.join(current_dir, "..", "static"))
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 添加data静态文件路由
data_path = os.path.abspath(os.path.join(current_dir, "../../", "data"))
# 检查data目录是否存在，不存在则创建
try:
    os.makedirs(data_path, exist_ok=True)
    print(f"Data directory created/verified at: {data_path}")
except OSError as e:
    print(f"Error creating data directory {data_path}: {e}")
    # 如果创建失败，使用临时目录作为后备
    import tempfile
    data_path = tempfile.mkdtemp(prefix="ai_gateway_data_")
    print(f"Using temporary data directory: {data_path}")
app.mount("/data", StaticFiles(directory=data_path), name="data")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    # 保存原有的 schemas
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
    else:
        schemas = {}

    # 更新 components
    openapi_schema["components"] = {
        "schemas": schemas,
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "请先调用 /api/v1/token/{api_key} 接口获取 access_token，然后在此输入（不需要输入 Bearer 前缀）"
            }
        }
    }

    # 设置全局安全配置
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

#   跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="")

# 自定义 OpenAPI 路由
@app.get("/custom-openapi.json")
async def filtered_openapi(request: Request, operation_id: str = Query(...)):
    # 获取完整 OpenAPI 文档
    full_spec = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    # 验证operation_id参数
    if not operation_id or not isinstance(operation_id, str):
        raise HTTPException(status_code=422, detail="Invalid operation_id")
        
    operation_ids = [id.strip() for id in operation_id.split(',') if id.strip()]

    filtered_paths = {}
    related_schemas = {}

    # 确保保留ValidationError schema
    if "ValidationError" in full_spec.get("components", {}).get("schemas", {}):
        related_schemas["ValidationError"] = full_spec["components"]["schemas"]["ValidationError"]

    
    for path, methods in full_spec["paths"].items():
        for method, spec in methods.items():
            if spec.get("operationId") in operation_ids:
                filtered_paths[path] = {method: spec}
                
                # # 收集请求体和响应体引用的schemas
                # if "requestBody" in spec:
                #     for content in spec["requestBody"].get("content", {}).values():
                #         if "schema" in content and "$ref" in content["schema"]:
                #             ref_parts = content["schema"]["$ref"].split("/")
                #             # 保留当前方法引用的schema
                #             schema_name = ref_parts[-1]
                #             if schema_name in full_spec.get("components", {}).get("schemas", {}):
                #                 related_schemas[schema_name] = full_spec["components"]["schemas"][schema_name]
                #             # 保留下一级引用的schema
                #             if len(ref_parts) > 2 and ref_parts[-2] not in ["", "#"]:
                #                 next_level_schema = f"{ref_parts[-2]}/{ref_parts[-1]}"
                #                 if next_level_schema in full_spec.get("components", {}).get("schemas", {}):
                #                     related_schemas[next_level_schema] = full_spec["components"]["schemas"][next_level_schema]
                
                # if "responses" in spec:
                #     for response in spec["responses"].values():
                #         for content in response.get("content", {}).values():
                #             if "schema" in content and "$ref" in content["schema"]:
                #                 ref_parts = content["schema"]["$ref"].split("/")
                #                 # 保留当前方法引用的schema
                #                 schema_name = ref_parts[-1]
                #                 if schema_name in full_spec.get("components", {}).get("schemas", {}):
                #                     related_schemas[schema_name] = full_spec["components"]["schemas"][schema_name]
                #                 # 保留下一级引用的schema
                #                 if len(ref_parts) > 2 and ref_parts[-2] not in ["", "#"]:
                #                     next_level_schema = f"{ref_parts[-2]}/{ref_parts[-1]}"
                #                     if next_level_schema in full_spec.get("components", {}).get("schemas", {}):
                #                         related_schemas[next_level_schema] = full_spec["components"]["schemas"][next_level_schema]

                # 收集请求体和响应体引用的schemas
                # if "requestBody" in spec:
                #     for content in spec["requestBody"].get("content", {}).values():
                #         if "schema" in content and "$ref" in content["schema"]:
                #             schema_name = content["schema"]["$ref"].split("/")[-1]
                #             if schema_name in full_spec.get("components", {}).get("schemas", {}):
                #                 related_schemas[schema_name] = full_spec["components"]["schemas"][schema_name]
                
                # if "responses" in spec:
                #     for response in spec["responses"].values():
                #         for content in response.get("content", {}).values():
                #             if "schema" in content and "$ref" in content["schema"]:
                #                 schema_name = content["schema"]["$ref"].split("/")[-1]
                #                 if schema_name in full_spec.get("components", {}).get("schemas", {}):
                #                     related_schemas[schema_name] = full_spec["components"]["schemas"][schema_name]

    # 更新安全认证securitySchemes
    full_spec["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "请先调用 /api/v1/token/{api_key} 接口获取 access_token，然后在此输入（不需要输入 Bearer 前缀）"
            }
        }

    # 返回过滤后的文档，包含相关schemas
    return {
        **full_spec,
        "paths": filtered_paths,
        # "components": {
        #     "schemas": related_schemas,
        #     "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {})
        # } if related_schemas else None,
        "security": full_spec.get("security", [])
    }


@app.get("/single-docs")
async def custom_docs(request: Request, operation_id: str = Query(...)):
    return get_swagger_ui_html(
        openapi_url=f"/custom-openapi.json?operation_id={operation_id}",
        title="Single API Docs"
    )

@app.get("/single-redoc")
async def custom_redoc(request: Request, operation_id: str = Query(...)):
    return get_redoc_html(
        openapi_url=f"/custom-openapi-redoc.json?operation_id={operation_id}",
        title="Single API Redoc"
    )

@app.get("/custom-openapi-redoc.json")
async def filtered_openapi_redoc(request: Request, operation_id: str = Query(...)):
    """
    返回过滤后的OpenAPI文档
    Args:
        operation_id: 要过滤的API操作ID，多个用逗号分隔
    Returns:
        包含指定operation_id的OpenAPI文档
    """
    try:
        # 获取完整OpenAPI文档
        full_spec = get_openapi(
            title=app.title,
            version="1.0.0",
            description=app.description,
            routes=app.routes,
        )

        # 验证operation_id参数
        if not operation_id or not isinstance(operation_id, str):
            raise HTTPException(status_code=422, detail="Invalid operation_id")
            
        operation_ids = [id.strip() for id in operation_id.split(',') if id.strip()]
        
        filtered_paths = {}
        
        for path, methods in full_spec["paths"].items():
            for method, spec in methods.items():
                if spec.get("operationId") in operation_ids:
                    filtered_paths[path] = {method: spec}

        # 返回完整的文档结构
        return {
            "openapi": "3.0.0",
            "info": full_spec["info"],
            "paths": filtered_paths,
            "components": full_spec.get("components", {}),
            "security": full_spec.get("security", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/", tags=["Root"])
async def root():
    return "ai-application-gateway"


@app.get("/version", tags=["Version"])
async def get_version():
    try:
        from ai_gateway.version import version
        return {"version": version}
    except ImportError:
        return {"version": "unknown"}


@app.get("/health", tags=["Health Check"])
async def health():
    return {"status": "ok"}


# 启动prometheus监控
Instrumentator().instrument(app).expose(app, tags=["Prometheus"])


#   全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    json_data = RspBase.fail(content=exc.detail, code=exc.status_code).model_dump()
    return JSONResponse(content=json_data, status_code=exc.status_code)
