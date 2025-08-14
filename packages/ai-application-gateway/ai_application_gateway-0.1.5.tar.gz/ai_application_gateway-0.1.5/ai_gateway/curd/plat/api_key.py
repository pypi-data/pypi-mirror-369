from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.schemas.table.plat.api_key import API_KEY


class CRUDAPIKEY(CRUDBase[API_KEY]):
    model = API_KEY

    async def create_api_key(
            self,
            *,
            code: str,
            company: str,
            department: str,
            business: str,
            expires_at: datetime,
            status: int,
            group: Optional[str] = None,
            ip_whitelist: Optional[str] = None,
            remark: Optional[str] = None,
            db: AsyncSession
    ) -> API_KEY:
        try:
            api_key_data = {
                "code": code,
                "company": company,
                "department": department,
                "business": business,
                "expires_at": expires_at,
                "status": status,
                "group": group,
                "ip_whitelist": ip_whitelist,
                "remark": remark
            }
            api_key_obj = API_KEY(**{k: v for k, v in api_key_data.items() if v is not None})
            db.add(api_key_obj)
            await db.commit()
            await db.refresh(api_key_obj)
            return api_key_obj
        except SQLAlchemyError as e:
            await self._handle_db_error("创建API密钥", e)

    async def get_by_code(self, code: str, db: AsyncSession) -> Optional[API_KEY]:
        try:
            return await db.scalar(
                select(self.model)
                .where(self.model.code == code, self.model.is_deleted == 0)
            )
        except SQLAlchemyError as e:
            await self._handle_db_error("查询API密钥", e)

    async def get_api_keys(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[API_KEY]:
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
            await self._handle_db_error("查询API密钥列表", e)

    async def get_by_id(self, api_key_id: str, db: AsyncSession) -> Optional[API_KEY]:
        try:
            return await db.scalar(
                select(self.model).where(
                    self.model.id == api_key_id,
                    self.model.is_deleted == 0
                )
            )
        except SQLAlchemyError as e:
            await self._handle_db_error("查询API密钥", e)

    async def update_api_key(
            self,
            *,
            api_key_id: str,
            update_data: Dict[str, Any],
            db: AsyncSession
    ) -> API_KEY:
        try:
            api_key = await self.get_by_id(api_key_id, db)
            if not api_key:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="API密钥不存在"
                )

            # 如果要更新api_key，先检查新api_key是否已存在
            if "api_key" in update_data:
                existing_code = await self.get_by_code(update_data["code"], db)
                if existing_code and existing_code.id != api_key_id:
                    raise HTTPException(
                        status_code=HttpStatusCode.BAD_REQUEST_400,
                        detail="API密钥已存在"
                    )

            # 过滤掉None值，只更新非None的字段
            filtered_data = {k: v for k, v in update_data.items() if v is not None}

            query = (
                update(self.model)
                .where(self.model.id == api_key_id, self.model.is_deleted == 0)
                .values(**filtered_data)
            )
            await db.execute(query)
            await db.commit()

            return await self.get_by_id(api_key_id, db)
        except SQLAlchemyError as e:
            await self._handle_db_error("更新API密钥", e)

    async def delete_api_key(self, api_key_id: str, db: AsyncSession) -> None:
        try:
            api_key = await self.get_by_id(api_key_id, db)
            if not api_key:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="API密钥不存在"
                )

            await db.execute(
                delete(self.model).where(self.model.id == api_key_id)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("删除API密钥", e)

    async def fake_delete_api_key(self, api_key_id: str, db: AsyncSession) -> None:
        """假删除API密钥"""
        try:
            api_key = await self.get_by_id(api_key_id, db)
            if not api_key:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="API密钥不存在"
                )

            await db.execute(
                update(self.model)
                .where(self.model.id == api_key_id)
                .values(is_deleted=1)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("假删除API密钥", e)

    async def bulk_create_api_keys(
            self,
            api_keys_data: List[Dict[str, Any]],
            db: AsyncSession
    ) -> List[API_KEY]:
        try:
            api_keys = [API_KEY(**api_key_data) for api_key_data in api_keys_data]
            db.add_all(api_keys)
            await db.commit()
            for api_key in api_keys:
                await db.refresh(api_key)
            return api_keys
        except SQLAlchemyError as e:
            await self._handle_db_error("批量创建API密钥", e)


crud_api_key = CRUDAPIKEY(API_KEY)