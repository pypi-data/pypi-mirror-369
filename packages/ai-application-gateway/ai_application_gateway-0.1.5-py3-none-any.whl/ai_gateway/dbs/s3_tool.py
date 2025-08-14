from functools import wraps
from contextlib import asynccontextmanager

import aiofiles
from fastapi import HTTPException
import aiobotocore.session
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError

from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode

def async_s3_wrapper_except(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == "NoSuchKey":
                raise HTTPException(HttpStatusCode.NOT_FOUND_404, "对象不存在")
            elif error_code in ("AccessDenied", "SignatureDoesNotMatch"):
                raise HTTPException(HttpStatusCode.FORBIDDEN_403, "权限校验失败")
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, f"存储服务错误: {str(e)}")
        except Exception as e:
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, f"服务器内部错误: {str(e)}")
    return wrapper

class S3Tool:
    _session = aiobotocore.session.get_session()
    _client = None
    bucket = config.minio.bucket

    @classmethod
    async def _get_client(cls):
        if not cls._client:
            cls._client = await cls._session.create_client(
                's3',
                endpoint_url=config.minio.endpoint,
                aws_access_key_id=config.minio.access_key,
                aws_secret_access_key=config.minio.secret_key,
                region_name=config.minio.region if config.minio.region else None,  # 区域名称
                config=AioConfig(
                    signature_version='s3v4',
                ),
                use_ssl=config.minio.secure                              # 是否使用SSL
            ).__aenter__()
            
            # 验证并创建存储桶
            try:
                await cls._client.head_bucket(Bucket=cls.bucket)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    await cls._client.create_bucket(Bucket=cls.bucket)
        return cls._client

    @async_s3_wrapper_except
    async def make_bucket(self, bucket_name: str = None):
        """创建存储桶（S3需要处理BucketAlreadyOwnedByYou异常）"""
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        try:
            await client.create_bucket(Bucket=bucket)
        except ClientError as e:
            if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                raise

    @async_s3_wrapper_except
    async def get_bucket_list(self):
        """获取所有存储桶列表"""
        client = await self._get_client()
        response = await client.list_buckets()
        return response['Buckets']

    @async_s3_wrapper_except
    async def get_object_list(self, bucket_name: str = None, prefix: str = ''):
        """获取对象列表（支持分页）"""
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        
        objects = []
        paginator = client.get_paginator('list_objects_v2')
        async for result in paginator.paginate(Bucket=bucket, Prefix=prefix):
            objects.extend(result.get('Contents', []))
        return objects

    @async_s3_wrapper_except
    async def get_object_info(self, object_name: str, bucket_name: str = None):
        """获取对象元数据"""
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        response = await client.head_object(Bucket=bucket, Key=object_name)
        return {
            'size': response['ContentLength'],
            'last_modified': response['LastModified'],
            'metadata': response['Metadata']
        }

    @async_s3_wrapper_except
    async def get_object(self, object_name: str, bucket_name: str = None):
        """获取对象数据流"""
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        response = await client.get_object(Bucket=bucket, Key=object_name)
        async with response['Body'] as stream:
            return await stream.read()

    @async_s3_wrapper_except
    async def get_file_size(self, object_name: str, bucket_name: str = None):
        """获取文件大小"""
        info = await self.get_object_info(object_name, bucket_name)
        return info['size']

    @async_s3_wrapper_except
    async def get_file_last_modified(self, object_name: str, bucket_name: str = None):
        """获取最后修改时间"""
        info = await self.get_object_info(object_name, bucket_name)
        return info['last_modified']

    @async_s3_wrapper_except
    async def upload_file(self, object_name: str, file, bucket_name: str = None):
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        
        if isinstance(file, str):
            async with aiofiles.open(file, 'rb') as f:
                content = await f.read()
        else:
            await file.seek(0)
            content = await file.read()
        
        await client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=content
        )

    @async_s3_wrapper_except
    async def download_file(self, object_name: str, file_path: str, bucket_name: str = None):
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        
        response = await client.get_object(Bucket=bucket, Key=object_name)
        async with aiofiles.open(file_path, 'wb') as f:
            async for chunk in response['Body']:
                await f.write(chunk)

    @async_s3_wrapper_except
    async def delete_file(self, object_name: str, bucket_name: str = None):
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        await client.delete_object(Bucket=bucket, Key=object_name)

    @async_s3_wrapper_except
    async def get_file_url(self, object_name: str, bucket_name: str = None, expires=3600):
        bucket = bucket_name or self.bucket
        client = await self._get_client()
        url = await client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': object_name},
            ExpiresIn=expires
        )
        return url


# 使用示例
# async def main():
#     s3 = S3Tool()
#     await s3.upload_file("test.txt", "/path/to/file.txt")