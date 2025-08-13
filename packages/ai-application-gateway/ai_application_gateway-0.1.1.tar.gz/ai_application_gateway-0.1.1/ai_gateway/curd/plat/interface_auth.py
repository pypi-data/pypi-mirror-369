from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.schemas.table.plat.interface_auth import InterfaceAuth


class CRUDInterfaceAuth(CRUDBase[InterfaceAuth]):
    model = InterfaceAuth

    async def create_interface_auth(
            self,
            *,
            api_key_id: str,
            app_id: str,
            interface_id: str,
            db: AsyncSession
    ) -> InterfaceAuth:
        try:
            auth_data = {
                "api_key_id": api_key_id,
                "app_id": app_id,
                "interface_id": interface_id
            }
            auth_obj = InterfaceAuth(**auth_data)
            db.add(auth_obj)
            await db.commit()
            await db.refresh(auth_obj)
            return auth_obj
        except SQLAlchemyError as e:
            await self._handle_db_error("创建接口授权", e)

    async def get_interface_auths(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[InterfaceAuth]:
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
            await self._handle_db_error("查询接口授权列表", e)

    async def get_by_id(self, auth_id: str, db: AsyncSession) -> Optional[InterfaceAuth]:
        try:
            stmt = (
                select(self.model)
                .options(selectinload(self.model.api_key),
                         selectinload(self.model.app),
                         selectinload(self.model.interface))  # 加载关联的 api_key 数据
                .where(
                    self.model.id == auth_id,
                    self.model.is_deleted == 0
                )
            )
            result = await db.execute(stmt)
            interface = result.scalar_one_or_none()
            
            return interface
        except SQLAlchemyError as e:
            await self._handle_db_error("查询接口授权", e)

    async def update_interface_auth(
            self,
            *,
            auth_id: str,
            update_data: Dict[str, Any],
            db: AsyncSession
    ) -> InterfaceAuth:
        try:
            auth = await self.get_by_id(auth_id, db)
            if not auth:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="接口授权不存在"
                )

            filtered_data = {k: v for k, v in update_data.items() if v is not None}

            query = (
                update(self.model)
                .where(self.model.id == auth_id, self.model.is_deleted == 0)
                .values(**filtered_data)
            )
            await db.execute(query)
            await db.commit()

            return await self.get_by_id(auth_id, db)
        except SQLAlchemyError as e:
            await self._handle_db_error("更新接口授权", e)

    async def fake_delete_interface_auth(self, auth_id: str, db: AsyncSession) -> None:
        """假删除接口授权"""
        try:
            auth = await self.get_by_id(auth_id, db)
            if not auth:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="接口授权不存在"
                )

            await db.execute(
                update(self.model)
                .where(self.model.id == auth_id)
                .values(is_deleted=1)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("假删除接口授权", e)


crud_interface_auth = CRUDInterfaceAuth(InterfaceAuth)