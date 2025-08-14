from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.schemas.table.plat.app import App


class CRUDApp(CRUDBase[App]):
    model = App

    async def create_app(
            self,
            *,
            app_name: str,
            app_url: str,
            company: str,
            department: str,
            status: int,
            remark: Optional[str] = None,
            db: AsyncSession
    ) -> App:
        try:
            app_data = {
                "app_name": app_name,
                "app_url": app_url,
                "company": company,
                "department": department,
                "status": status,
                "remark": remark
            }
            app_obj = App(**{k: v for k, v in app_data.items() if v is not None})
            db.add(app_obj)
            await db.commit()
            await db.refresh(app_obj)
            return app_obj
        except SQLAlchemyError as e:
            await self._handle_db_error("创建应用", e)

    async def get_apps(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[App]:
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
            await self._handle_db_error("查询应用列表", e)

    async def get_by_id(self, app_id: str, db: AsyncSession) -> Optional[App]:
        try:
            return await db.scalar(
                select(self.model).where(
                    self.model.id == app_id,
                    self.model.is_deleted == 0
                )
            )
        except SQLAlchemyError as e:
            await self._handle_db_error("查询应用", e)

    async def update_app(
            self,
            *,
            app_id: str,
            update_data: Dict[str, Any],
            db: AsyncSession
    ) -> App:
        try:
            app = await self.get_by_id(app_id, db)
            if not app:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="应用不存在"
                )

            # 过滤掉None值，只更新非None的字段
            filtered_data = {k: v for k, v in update_data.items() if v is not None}

            query = (
                update(self.model)
                .where(self.model.id == app_id, self.model.is_deleted == 0)
                .values(**filtered_data)
            )
            await db.execute(query)
            await db.commit()

            return await self.get_by_id(app_id, db)
        except SQLAlchemyError as e:
            await self._handle_db_error("更新应用", e)

    async def fake_delete_app(self, app_id: str, db: AsyncSession) -> None:
        """假删除应用"""
        try:
            app = await self.get_by_id(app_id, db)
            if not app:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="应用不存在"
                )

            await db.execute(
                update(self.model)
                .where(self.model.id == app_id)
                .values(is_deleted=1)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("假删除应用", e)


crud_app = CRUDApp(App)