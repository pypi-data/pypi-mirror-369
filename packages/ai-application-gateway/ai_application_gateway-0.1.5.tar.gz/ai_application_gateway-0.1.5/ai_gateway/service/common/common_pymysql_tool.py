"""
通用类应用数据库连接池
"""
from urllib.parse import quote_plus
import pymysql
from sqlalchemy.pool import QueuePool
from ai_gateway.config import config

# 存储多个连接池的字典
connection_pools = {}

# 初始化所有配置的连接池
def init_connection_pools():
    for db_name in config.common.db:
        # 为每个配置创建独立连接池
        connection_pools[db_name] = QueuePool(
            lambda db=db_name: create_connection(db),
            max_overflow=getattr(config, db_name).max_overflow,
            pool_size=getattr(config, db_name).pool_size,
            recycle=60,  # 连接回收时间1分钟
            reset_on_return='rollback'
        )

# 初始化时自动创建连接池
init_connection_pools()

# 获取指定连接池
def get_pool(business_type):
    return connection_pools.get(business_type+".db")

def create_connection(db_name):
    # 根据配置名称加载对应的数据库配置
    db_config = getattr(config, db_name)
    return pymysql.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        passwd=db_config.password,
        db=quote_plus(db_config.database),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )