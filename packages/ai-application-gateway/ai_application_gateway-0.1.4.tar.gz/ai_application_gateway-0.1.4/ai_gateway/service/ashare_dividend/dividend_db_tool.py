"""
A股分红数据库连接池
支持Oracle、OceanBase和MySQL
"""
import pymysql
from sqlalchemy.pool import QueuePool
from ai_gateway.config import config
import oracledb as cx_Oracle
# import cx_Oracle
from urllib.parse import quote_plus

def create_connection():
    """创建数据库连接的工厂函数"""
    # Oracle测试环境 10.23.120.89 1521 cfgldb  account：ai_reader view_Ai#0603
    if config.dividend.database.db_type == "oracle":
        cx_Oracle.init_oracle_client()  # 启用thick模式
        db_config = config.dividend.oracle.db
        dsn = cx_Oracle.makedsn(
            host=db_config.host,
            port=db_config.port,
            service_name=quote_plus(db_config.database),
        )
        connection = cx_Oracle.connect(
            user=db_config.user,
            password=db_config.password,
            dsn=dsn,
            events=True,    # 启用事件通知（如语句缓存）
            expire_time=2  # 空闲2分钟后关闭连接
            )
        return connection
    elif config.dividend.database.db_type == "oceanbase_prog":
        db_config = config.dividend.oceanbase_prog.db
        return pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            passwd=db_config.password,
            db=quote_plus(db_config.database),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    elif config.dividend.database.db_type == "oceanbase":
        db_config = config.dividend.oceanbase.db
        return pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            passwd=db_config.password,
            db=quote_plus(db_config.database),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        db_config = config.dividend.mysql.db
        return pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            passwd=db_config.password,
            db=quote_plus(db_config.database),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )


# 在模块级别初始化连接池
dividend_db_connection_pool = QueuePool(
    create_connection,
    max_overflow=config.dividend.oracle.db.max_overflow if config.dividend.database.db_type == "oracle" else
                config.dividend.oceanbase_prog.db.max_overflow if config.dividend.database.db_type == "oceanbase_prog" else
                config.dividend.oceanbase.db.max_overflow if config.dividend.database.db_type == "oceanbase" else
                config.dividend.mysql.db.max_overflow,
    pool_size=config.dividend.oracle.db.pool_size if config.dividend.database.db_type == "oracle" else
            config.dividend.oceanbase_prog.db.pool_size if config.dividend.database.db_type == "oceanbase_prog" else
            config.dividend.oceanbase.db.pool_size if config.dividend.database.db_type == "oceanbase" else
            config.dividend.mysql.db.pool_size,
    recycle=60,  # 连接回收时间1分钟
    reset_on_return='rollback'
)