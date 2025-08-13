from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.table.plat.interface_log import Interface_log


class CRUDInterfaceLog(CRUDBase[Interface_log]):
    model = Interface_log

    async def create_log(
        self,
        *,
        user_id: str,
        request_id: str,
        code: str,
        url: str,
        base_url: str,
        path: str,
        method: str,
        request_params: str,
        ip: str,
        port: int,
        request_at: datetime,
        response_json: str,
        response_time: float,
        status_code: int,
        created: datetime,
        updated: datetime,
        timestamp: float,
        db: AsyncSession
    ) -> Interface_log:
        try:
            log_data = {
                "user_id": user_id,
                "request_id": request_id,
                "code": code,
                "url": url,
                "base_url": base_url,
                "path": path,
                "method": method,
                "request_params": request_params,
                "ip": ip,
                "port": port,
                "request_at": request_at,
                "response_json": response_json,
                "response_time": response_time,
                "status_code": status_code,
                "created": created,
                "updated": created,
                "timestamp": timestamp
            }
            log_obj = Interface_log(**log_data)
            db.add(log_obj)
            await db.commit()
            await db.refresh(log_obj)
            return log_obj
        except SQLAlchemyError as e:
            await self._handle_db_error("创建接口日志", e)

    async def get_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interface_log]:
        try:
            query = (
                select(self.model)
                .order_by(self.model.timestamp.desc())
                .offset(skip)
                .limit(limit)
            )
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            await self._handle_db_error("查询日志列表", e)

    async def get_log_by_id(self, log_id: str, db: AsyncSession) -> Optional[Interface_log]:
        try:
            stmt = select(self.model).where(self.model.id == log_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self._handle_db_error("查询日志详情", e)

    async def delete_log(self, log_id: str, db: AsyncSession) -> None:
        """物理删除日志（慎用）"""
        try:
            await db.execute(
                delete(self.model).where(self.model.id == log_id)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("删除日志", e)


crud_interface_log = CRUDInterfaceLog(Interface_log)