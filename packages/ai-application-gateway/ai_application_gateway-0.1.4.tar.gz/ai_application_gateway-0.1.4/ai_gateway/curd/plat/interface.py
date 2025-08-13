from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.schemas.table.plat.interface import Interface


class CRUDInterface(CRUDBase[Interface]):
    model = Interface

    async def create_interface(
            self,
            *,
            interface_name: str,
            path: str,
            method: str,
            request_params: str,
            response_json: str,
            version: str,
            app_id: str,
            status: int,
            remark: Optional[str] = None,
            db: AsyncSession
    ) -> Interface:
        try:
            interface_data = {
                "interface_name": interface_name,
                "path": path,
                "method": method,
                "request_params": request_params,
                "response_json": response_json,
                "version": version,
                "app_id": app_id,
                "status": status,
                "remark": remark
            }
            interface_obj = Interface(**{k: v for k, v in interface_data.items() if v is not None})
            db.add(interface_obj)
            await db.commit()
            await db.refresh(interface_obj)
            return interface_obj
        except SQLAlchemyError as e:
            await self._handle_db_error("创建接口", e)

    async def get_interfaces(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[Interface]:
        try:
            query = (
                select(self.model)
                .where(self.model.is_deleted == 0)
                .offset(skip)
                .limit(limit)
            )
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            await self._handle_db_error("查询接口列表", e)

    async def get_by_id(self, interface_id: str, db: AsyncSession) -> Optional[Interface]:
        try:
            stmt = (
                select(self.model)
                .where(
                    self.model.id == interface_id,
                    self.model.is_deleted == 0
                )
            )
            result = await db.execute(stmt)
            interface = result.scalar_one_or_none()
            
            return interface
        except SQLAlchemyError as e:
            await self._handle_db_error("查询接口", e)

    async def update_interface(
            self,
            *,
            interface_id: str,
            update_data: Dict[str, Any],
            db: AsyncSession
    ) -> Interface:
        try:
            interface = await self.get_by_id(interface_id, db)
            if not interface:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="接口不存在"
                )

            filtered_data = {k: v for k, v in update_data.items() if v is not None}

            query = (
                update(self.model)
                .where(self.model.id == interface_id, self.model.is_deleted == 0)
                .values(**filtered_data)
            )
            await db.execute(query)
            await db.commit()

            return await self.get_by_id(interface_id, db)
        except SQLAlchemyError as e:
            await self._handle_db_error("更新接口", e)

    async def fake_delete_interface(self, interface_id: str, db: AsyncSession) -> None:
        """假删除接口"""
        try:
            interface = await self.get_by_id(interface_id, db)
            if not interface:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="接口不存在"
                )

            await db.execute(
                update(self.model)
                .where(self.model.id == interface_id)
                .values(is_deleted=1)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("假删除接口", e)


crud_interface = CRUDInterface(Interface)