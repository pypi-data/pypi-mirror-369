from asyncio import current_task
from typing import AsyncIterator, Literal
from typing import Optional
from urllib.parse import quote_plus

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)

from ai_gateway.config import config


def get_url(sync=False):
    if config.database.db_type == "oceanbase":
        # OceanBase 的连接参数需要通过 connect_args 传递，而不是通过 URL query 参数
        base_url = URL.create(
            drivername="mysql+pymysql" if sync else "mysql+aiomysql",
            host=config.oceanbase.host,
            port=config.oceanbase.port,
            username=config.oceanbase.user,
            password=config.oceanbase.password,
            database=quote_plus(config.oceanbase.database),
            query={"charset": "utf8mb4"},
        )
        return base_url
    # MySQL 连接
    elif config.database.db_type == "mysql":
        return URL.create(
            drivername="mysql+pymysql" if sync else "mysql+aiomysql",
            host=config.mysql.host,
            port=config.mysql.port,
            username=config.mysql.user,
            password=config.mysql.password,
            database=quote_plus(config.mysql.database),
            query={"charset": "utf8mb4"},
        )


class SessionInitializationError(Exception):
    """Raised when the database session manager is not properly initialized."""


async def get_db() -> AsyncIterator[AsyncSession]:
    session = mysql_sessionmanager.session if config.database.db_type == "mysql" else ob_sessionmanager.session
    if session is None:
        raise SessionInitializationError("DatabaseSessionManager is not initialized")
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


class DatabaseSessionManager:
    def __init__(self, db_type: Literal["mysql", "oceanbase"] = "mysql"):
        self.engine: Optional[AsyncEngine] = None
        self.session_maker = None
        self.session = None
        self.db_type = db_type

    async def init_db(self):

        connect_args = {}
        # if self.db_type == "oceanbase":
        #     connect_args.update({
        #         "tenant": config.oceanbase.tenant,
        #         "cluster": config.oceanbase.cluster,
        #     })

        self.engine = create_async_engine(
            get_url(),
            pool_size=config.mysql.pool_size if self.db_type == "mysql" else config.oceanbase.pool_size,
            max_overflow=config.mysql.max_overflow if self.db_type == "mysql" else config.oceanbase.max_overflow,
            pool_pre_ping=True,
            echo=config.debug,
            pool_recycle=60,
            connect_args=connect_args
        )

        self.session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self.session = async_scoped_session(self.session_maker, scopefunc=current_task)

    async def close(self):
        if self.engine is None:
            raise SessionInitializationError(
                "DatabaseSessionManager is not initialized"
            )
        await self.engine.dispose()
        self.engine = None

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


# 创建 MySQL 和 OceanBase 会话管理器实例
mysql_sessionmanager = DatabaseSessionManager("mysql")
ob_sessionmanager = DatabaseSessionManager("oceanbase")