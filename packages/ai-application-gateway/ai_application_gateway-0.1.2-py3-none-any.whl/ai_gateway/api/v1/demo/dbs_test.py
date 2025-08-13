"""
标准示例：数据存储连接测试
"""
import os
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, UploadFile, Depends
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.config import config
from ai_gateway.core.middleware import trace_request
from ai_gateway.core.schedule import scheduler, add_task
from ai_gateway.dbs.es_tool import es_tool
from ai_gateway.dbs.minio_tool import MinioTool
from ai_gateway.dbs.redis_tool import RedisTool
from ai_gateway.dbs.s3_tool import S3Tool
from ai_gateway.schemas.api.base import RspBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.dbs.db import get_db

dbs_test_router = APIRouter(prefix="/demo/dbs_test")


@dbs_test_router.post("/ob_connect", operation_id="OceanBase_数据库连接测试", summary="OceanBase 数据库连接测试", response_description="返回连接是否成功" , response_model=RspBase)
@trace_request
async def ob_connect(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """OceanBase 数据库连接测试"""
    try:
        # 执行数据库查询
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return RspBase(content="数据库连接成功！")
        else:
            return RspBase(content="数据库连接失败！")
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503, detail=f"数据库连接失败！  detail：{str(e)}")


@dbs_test_router.post("/redis_connect", summary="redis 连接测试", response_description="返回连接是否成功" , response_model=RspBase)
@trace_request
async def redis_connect(
    request: Request,
):
    """Redis 连接测试"""
    try:
        redis_tool = await RedisTool.get_pool()  # 集群模式下强制使用数据库 0
        await redis_tool.set("zx", "8888")
        data = await redis_tool.get("zx")
        return RspBase(content=f"redis 连接成功！获取键值：{data}")
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503, detail=f"redis 连接失败！  detail：{str(e)}")

@dbs_test_router.post("/elasticsearch_connect", summary="elasticsearch 连接测试", response_description="返回连接是否成功" , response_model=RspBase)
@trace_request
async def elasticsearch_connect(
    request: Request,
):
    """elasticsearch 连接测试"""
    try:
        # 先创建索引（如果不存在）
        ai_gateway_api_test_index = "ai_gateway_api_test_index"
        await es_tool.create_index(ai_gateway_api_test_index)
        
        # 新增测试文档索引
        test_doc = {
            "timestamp": datetime.now().isoformat(),
            "message": "网关连接测试",
            "status": "success"
        }
        index_result = await  es_tool.index(
            index=ai_gateway_api_test_index,
            body=test_doc,
            id="gateway_test_001"
        )
        
        # 查询新增的文档
        response = await es_tool.search(ai_gateway_api_test_index, {
            "query": {"ids": {"values": ["gateway_test_001"]}}
        })
        
        data = response['hits']['hits']
        if await es_tool.ping():
            return RspBase(content=f"ES连接成功！版本信息：{es_tool.info()}\n"
                                f"测试文档状态：{index_result['result']}\n"
                                f"查询结果：{len(data)}条记录")
        else:
            return RspBase(content="elasticsearch 连接失败！")
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
                            detail=f"{str(e)}")


@dbs_test_router.post("/s3_connect", summary="S3 连接测试（支持异步操作 minio）",
                      response_description="返回连接是否成功", response_model=RspBase)
@trace_request
async def s3_connect(
        request: Request,
        file: UploadFile,
):
    """S3 兼容存储连接测试"""
    try:
        s3 = S3Tool()
        buckets = await s3.get_bucket_list()

        # 上传测试文件
        await s3.upload_file("s3-object", file)

        # 获取对象信息
        object_info = await s3.get_object_info("s3-object")
        file_url = await s3.get_file_url("s3-object")

        # 下载文件到本地
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..",
            "data", "downloads",
            file.filename
        ))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await s3.download_file("s3-object", file_path)

        return RspBase(content=f"s3 连接成功！存储桶列表：{[b['Name'] for b in buckets]}\n"
                               f"文件大小：{object_info['size']} bytes\n"
                               f"临时URL：{file_url}")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
                            detail=f"S3连接异常：{str(e)}")


@dbs_test_router.post("/minio_connect", summary="minio 连接测试（minio对象只支持同步）",
                     response_description="返回连接是否成功", response_model=RspBase)
@trace_request
async def minio_connect(
        request: Request,
        file: UploadFile,
):
    """minio 连接测试"""
    try:
        minio_tool = MinioTool()
        buckets = minio_tool.get_bucket_list()
        minio_tool.upload_file("my-object", file)

        object_info = minio_tool.get_object_info("my-object")
        file_url = minio_tool.get_file_url("my-object")

        # 自动创建目录路径
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..",  # 上溯到 ai_gateway 的父目录
            "data", "downloads",
            file.filename
        ))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        minio_tool.download_file("my-object", file_path)
        return RspBase(content=f"minio 连接成功！存储桶列表：{', '.join([bucket.name for bucket in buckets])}\n"
                               f"文件大小：{object_info.size} bytes\n"
                               f"临时URL：{file_url}")

    except Exception as e:
        raise HTTPException(status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
                            detail=f"{str(e)}")
