"""
公告数据库连接池
"""
import pymysql
from sqlalchemy.pool import QueuePool
from ai_gateway.config import config

dbconfig = config.opportunity.db

# 在模块级别初始化连接池
connection_pool = QueuePool(
    lambda: pymysql.connect(
        host=dbconfig.host,
        port=dbconfig.port,
        user=dbconfig.user,
        passwd=dbconfig.password,
        db=dbconfig.database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    ),
    max_overflow=dbconfig.max_overflow,
    pool_size=dbconfig.pool_size,
    recycle=60,  # 连接回收时间1分钟
    reset_on_return='rollback'
)