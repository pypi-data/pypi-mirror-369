from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.curd.base import CRUDBase
from ai_gateway.schemas.errors import HttpStatusCode
from ai_gateway.schemas.table.demo.user import User


class CRUDUser(CRUDBase[User]):
    model = User

    async def create_user(
            self,
            *,
            username: str,
            role: str,
            avatar_url: Optional[str] = None,
            age: Optional[int] = None,
            gender: Optional[str] = None,
            bio: Optional[str] = None,
            db: AsyncSession
    ) -> User:
        try:
            user_data = {
                "username": username,
                "role": role,
                "avatar_url": avatar_url,
                "age": age,
                "gender": gender,
                "bio": bio
            }
            user = User(**{k: v for k, v in user_data.items() if v is not None})
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self._handle_db_error("创建用户", e)

    async def get_by_username(self, username, db: AsyncSession) -> Optional[User]:
        try:
            return await db.scalar(
                select(self.model)
                .where(self.model.username == username, self.model.is_deleted == 0)
            )
        except SQLAlchemyError as e:
            await self._handle_db_error("查询用户", e)

    async def get_users(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[User]:
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
            await self._handle_db_error("查询用户列表", e)

    async def get_by_id(self, user_id, db: AsyncSession):
        try:
            return await db.scalar(
                select(self.model).where(
                    self.model.id == user_id,
                    self.model.is_deleted == 0,
                )
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
                detail=f"数据库查询用户失败: {str(e)}"
            )

    async def fake_delete_user_by_username(self, username, db: AsyncSession):
        """假删除用户"""
        try:
            user = await self.get_by_username(username, db)
            if not user:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="用户不存在"
                )

            await db.execute(
                update(self.model)
                .where(self.model.username == username)
                .values(is_deleted=1)
            )
            await db.commit()
        except SQLAlchemyError as e:
            await self._handle_db_error("假删除用户", e)


    async def bulk_create_users(
            self,
            users_data: List[Dict[str, Any]],
            db: AsyncSession
    ) -> List[User]:
        try:
            users = [User(**user_data) for user_data in users_data]
            db.add_all(users)
            await db.commit()
            for user in users:
                await db.refresh(user)
            return users
        except SQLAlchemyError as e:
            await self._handle_db_error("批量创建用户", e)


    async def delete_user_by_id(self, user_id: int, db: AsyncSession) -> None:
        """删除用户"""
        try:
            user_obj = await self.get_by_id(user_id, db)
            if user_obj is None:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail=f"用户不存在"
                )

            await db.execute(
                delete(self.model).where(
                    self.model.id == user_id
                )
            )
            await db.commit()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
                detail=f"数据库删除用户失败: {str(e)}"
            )


    async def update_user(
            self,
            *,
            user_id: int,
            update_data: Dict[str, Any],
            db: AsyncSession
    ) -> User:
        try:
            user = await self.get_by_id(user_id, db)
            if not user:
                raise HTTPException(
                    status_code=HttpStatusCode.BAD_REQUEST_400,
                    detail="用户不存在"
                )
            
            # 如果要更新用户名，先检查新用户名是否已存在
            if "username" in update_data:
                existing_user = await self.get_by_username(update_data["username"], db)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=HttpStatusCode.BAD_REQUEST_400,
                        detail="用户名已存在"
                    )
            
            # 过滤掉None值，只更新非None的字段
            filtered_data = {k: v for k, v in update_data.items() if v is not None}
            
            query = (
                update(self.model)
                .where(self.model.id == user_id, self.model.is_deleted == 0)
                .values(**filtered_data)
            )
            await db.execute(query)
            await db.commit()
            
            return await self.get_by_id(user_id, db)
        except SQLAlchemyError as e:
            await self._handle_db_error("更新用户", e)

crud_user = CRUDUser(User)