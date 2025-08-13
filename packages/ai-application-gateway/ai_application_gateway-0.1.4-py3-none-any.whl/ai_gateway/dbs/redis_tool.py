from typing import Optional
import atexit  # 新增导入

from redis.asyncio import ConnectionPool, Redis

from ai_gateway.config import config


class RedisTool:
    _pool = {}

    @classmethod
    async def close_all(cls):
        """关闭所有Redis连接"""
        for db, redis_cli in cls._pool.items():
            await redis_cli.aclose()
        cls._pool.clear()

    @classmethod
    def _sync_close_all(cls):
        """同步关闭方法用于atexit注册"""
        import asyncio
        asyncio.run(cls.close_all())

    @classmethod
    async def get_pool(cls, database: Optional[int] = None):
        if database is None:
            database = config.redis.database

        redis_cli = cls._pool.get(database)
        try:
            if redis_cli is None:
                raise ConnectionError("Redis connection is closed or not initialized")
            await redis_cli.ping()
        except (ConnectionError, TimeoutError):
            if config.redis.cluster: # 集群模式
                # 集群模式使用异步客户端
                from redis.asyncio.cluster import RedisCluster
                redis = RedisCluster(
                    host=config.redis.host,
                    port=config.redis.port,
                    password=config.redis.password,
                    decode_responses=True,  # 自动解码为字符串
                    socket_connect_timeout=5,
                    cluster_error_retry_attempts=3,  # 添加集群错误重试
                    reinitialize_steps=5,  # 集群拓扑刷新
                    # 集群模式下强制使用数据库 0（需要与集群配置一致）
                    read_from_replicas=True  # 启用从节点读取
                )
            else:   # 非集群模式
                redis = Redis(connection_pool=ConnectionPool.from_url(
                    f"redis://{config.redis.host}:{config.redis.port}",
                    password=config.redis.password,
                    db=database,
                    decode_responses=True,  # 自动解码为字符串
                    socket_connect_timeout=5,  # 添加异步连接超时
                    health_check_interval=30    # 保持健康检查参数
                ))
            await redis.ping()
            cls._pool[database] = redis
            # 注册退出处理（只需要注册一次）
            if not hasattr(cls, "_atexit_registered"):
                atexit.register(cls._sync_close_all)
                cls._atexit_registered = True

        return cls._pool[database]
