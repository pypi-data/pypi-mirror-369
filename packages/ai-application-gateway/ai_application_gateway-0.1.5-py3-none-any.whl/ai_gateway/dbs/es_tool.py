from functools import wraps
from elasticsearch import AsyncElasticsearch, exceptions
from fastapi import HTTPException
from ai_gateway.config import config
from ai_gateway.schemas.errors import HttpStatusCode

def es_wrapper_except(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):  # 改为异步包装器
        try:
            return await func(*args, **kwargs)  # 添加 await
        except exceptions.ConnectionError as e:
            raise HTTPException(HttpStatusCode.SERVICE_UNAVAILABLE_503, f"ES连接失败: {str(e)}")
        except exceptions.AuthenticationException as e:
            raise HTTPException(HttpStatusCode.UNAUTHORIZED_401, f"ES认证失败: {str(e)}")
        except exceptions.NotFoundError as e:
            raise HTTPException(HttpStatusCode.NOT_FOUND_404, f"ES索引未找到: {str(e)}")
        except Exception as e:
            raise HTTPException(HttpStatusCode.INTERNAL_SERVER_ERROR_500, f"ES操作异常: {str(e)}")
    return async_wrapper

class ESTool:
    _pool = {}
    
    def __init__(self, hosts=None, auth=None):
        self.cfg = config.es
        self.hosts = hosts or [self.cfg.url]
        self.auth = auth or (self.cfg.user, self.cfg.password)
        self.es = None  # 延迟初始化

    async def initialize(self):  # 新增异步初始化方法
        """异步初始化连接池"""
        pool_key = hash((tuple(self.hosts), self.auth))
        
        if pool_key in self._pool:
            self.es = self._pool[pool_key]
            if not await self._check_connection():
                del self._pool[pool_key]
                await self._create_new_connection(pool_key)
        else:
            await self._create_new_connection(pool_key)

    async def _create_new_connection(self, pool_key): 
        self.es = AsyncElasticsearch(
            hosts=self.hosts,
            basic_auth=self.auth,  # 基本认证
            max_retries=3,    # 最大重试次数
            retry_on_timeout=True,  # 启用超时重试
            connections_per_node=10,   # 每个节点的最大连接数
            node_class="aiohttp",  # 使用支持的异步客户端类型
            http_compress=True  # 启用HTTP响应体的gzip压缩传输
        )
        if not await self._check_connection():
            raise ConnectionError("无法连接Elasticsearch")
        self._pool[pool_key] = self.es

    async def _check_connection(self):
        try:
            return await self.es.ping()
        except Exception:
            return False

    @es_wrapper_except
    async def bulk(self, actions):
        """批量操作文档"""
        return await self.es.bulk(operations=actions)

    @es_wrapper_except
    async def index_exists(self, index):
        """检查索引是否存在"""
        return await self.es.indices.exists(index=index)

    @es_wrapper_except
    async def close(self):
        """关闭所有ES连接"""
        for es_client in self._pool.values():
            await es_client.close()
        self._pool.clear()
        self.es = None

    @es_wrapper_except
    async def search(self, index, body):
        return await self.es.search(index=index, body=body)

    @es_wrapper_except
    async def index_stats(self, index):
        return await self.es.indices.stats(index=index)

    @es_wrapper_except
    async def create_index(self, index, body=None):
        if not await self.es.indices.exists(index=index):
            await self.es.indices.create(index=index, body=body)

    async def delete_index(self, index: str):
        """删除指定索引"""
        if await self.es.indices.exists(index=index):
            return await self.es.indices.delete(index=index)
        return {"acknowledged": False}

    @es_wrapper_except
    async def ping(self):
        return await self.es.ping()

    @es_wrapper_except
    async def info(self):
        return await self.es.info()
    
    @es_wrapper_except
    async def index(self, index: str, body: dict, id: str = None, **kwargs):
        return await self.es.index(index=index, body=body, id=id, **kwargs)



# 创建实例但不立即初始化
es_tool = ESTool()

# 商机 ES 创建实例
cfg = config.opportunity.es
opp_es_tool = ESTool(cfg.url, (cfg.user, cfg.password))