from typing import Generic, TypeVar, Type, Optional, List, Union, Dict, Any

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.schemas.errors import HttpStatusCode

ModelType = TypeVar("ModelType", bound=SQLModel)


# noinspection PyArgumentList
class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def _handle_db_error(self, operation: str, error: SQLAlchemyError) -> None:
        """统一处理数据库错误"""
        logger.error(f"数据库{operation}失败: {str(error)}")
        raise HTTPException(
            status_code=HttpStatusCode.SERVICE_UNAVAILABLE_503,
            detail=f"数据库{operation}失败: {str(error)}"
        )

    async def get(self, db: AsyncSession, record_id: Any) -> Optional[ModelType]:
        """
        通过ID获取记录

        Args:
            db: 数据库会话
            record_id: 记录ID

        Returns:
            Optional[ModelType]: 查询到的记录或None
        """
        try:
            stmt = select(self.model).where(self.model.id == record_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"获取记录失败: {str(e)}", exc_info=True)
            return None

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            query = select(self.model).offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"获取多条记录失败: {str(e)}", exc_info=True)
            return []

    async def create(self, db: AsyncSession, *, obj_in: ModelType) -> ModelType:
        try:
            db.add(obj_in)
            await db.commit()
            await db.refresh(obj_in)
            return obj_in
        except Exception as e:
            await db.rollback()
            logger.exception(f"创建记录失败: {str(e)}")
            raise

    async def update(
        self,
        db: AsyncSession,
        *,
        record_id: Any,
        obj_in: Union[ModelType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """
        更新记录

        Args:
            db: 数据库会话
            record_id: 记录ID
            obj_in: 更新数据

        Returns:
            Optional[ModelType]: 更新后的记录或None
        """
        try:
            db_obj = await self.get(db, record_id=record_id)
            if not db_obj:
                return None

            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"更新记录失败: {str(e)}", exc_info=True)
            raise

    async def delete(self, db: AsyncSession, *, _id: int) -> Optional[ModelType]:
        try:
            obj = await self.get(db=db, id=_id)
            if obj:
                stmt = delete(self.model).where(self.model.aid == _id)
                await db.execute(stmt)
                await db.commit()
            return obj
        except Exception as e:
            await db.rollback()
            logger.error(f"删除记录失败: {str(e)}", exc_info=True)
            raise
