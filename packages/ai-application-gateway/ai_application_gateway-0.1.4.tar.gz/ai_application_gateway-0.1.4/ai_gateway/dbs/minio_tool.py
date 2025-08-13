from functools import wraps
from fastapi import HTTPException
from minio import Minio
from minio.error import S3Error

from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode


# 定义一个装饰器，用于捕获Minio操作的异常并转换为HTTPException
def minio_wrapper_except(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except S3Error as e:
            error_code = e.code
            # 根据错误类型设置不同的状态码
            if error_code == "NoSuchKey":
                raise HTTPException(HttpStatusCode.NOT_FOUND_404, "对象不存在")
            elif error_code in ("AccessDenied", "SignatureDoesNotMatch"):
                raise HTTPException(HttpStatusCode.FORBIDDEN_403, "权限校验失败")
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, f"存储服务错误: {str(e)}")
        except ConnectionError:
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, "无法连接存储服务")
        except Exception as e:
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, f"服务器内部错误: {str(e)}")

    return wrapper


class MinioTool:
    _pool = {}  # 新增类级别连接池
    bucket = config.minio.bucket

    def __init__(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket

        # 尝试从连接池获取已存在的客户端
        client = self._pool.get(bucket_name)
        try:
            if client is not None:
                # 验证连接有效性
                client.list_buckets()  # 简单验证命令
                self.client = client
                return
        except Exception:
            del self._pool[bucket_name]  # 移除无效连接

        # 创建新连接并加入连接池
        try:
            # 修改这里移除协议前缀
            clean_endpoint = config.minio.endpoint.replace("http://", "").replace("https://", "")
            self.client = Minio(
                endpoint=clean_endpoint,  # 修改这里移除协议前缀
                access_key=config.minio.access_key,
                secret_key=config.minio.secret_key,
                region=config.minio.region, # 区域名称
                secure=config.minio.secure  # 是否使用SSL
            )

            # 存储桶初始化验证
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)

            self._pool[bucket_name] = self.client
        except Exception as e:
            raise ConnectionError(f"minio 连接失败！错误：{str(e)}")

    @minio_wrapper_except
    def make_bucket(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    @minio_wrapper_except
    def get_bucket_list(self):
        buckets = self.client.list_buckets()
        return buckets

    @minio_wrapper_except
    def get_object_list(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        objects = self.client.list_objects(bucket_name, recursive=True)
        return objects

    @minio_wrapper_except
    def get_object_info(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        obj_info = self.client.stat_object(bucket_name, object_name)
        return obj_info

    @minio_wrapper_except
    def get_object(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        obj = self.client.get_object(bucket_name, object_name)
        return obj

    @minio_wrapper_except
    def upload_file(self, object_name, file, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        if isinstance(file, str):
            self.client.fput_object(bucket_name, object_name, file)
        else:
            file.file.seek(0)
            self.client.put_object(
                bucket_name,
                object_name,
                file.file,
                length=-1,
                part_size=10 * 1024 * 1024
            )

    @minio_wrapper_except
    def download_file(self, object_name, file_path, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        self.client.fget_object(bucket_name, object_name, file_path)

    @minio_wrapper_except
    def delete_file(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        self.client.remove_object(bucket_name, object_name)

    @minio_wrapper_except
    def get_file_url(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        url = self.client.presigned_get_object(bucket_name, object_name)
        return url

    @minio_wrapper_except
    def get_file_size(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        obj_info = self.client.stat_object(bucket_name, object_name)
        return obj_info.size

    @minio_wrapper_except
    def get_file_last_modified(self, object_name, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.bucket
        obj_info = self.client.stat_object(bucket_name, object_name)
        return obj_info.last_modified

# minio_tool = MinioTool()