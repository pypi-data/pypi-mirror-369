"""
标准示例：数据表增删改查 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ai_gateway.core.middleware import trace_request
from ai_gateway.curd.demo.user import crud_user
from ai_gateway.dbs.db import get_db
from ai_gateway.schemas.api.base import RspDetail, RspList, RspBase
from ai_gateway.schemas.api.demo.user import UserCreate, UserOut
from ai_gateway.schemas.errors import ErrorCode, HttpStatusCode
from ai_gateway.schemas.table.demo.user import UserRole

db_curd_user_router = APIRouter(prefix="/demo/db_curd_user")


@db_curd_user_router.post("/create_user", summary="创建新用户", response_description="返回创建的新用户", response_model=RspDetail[UserOut])
@trace_request
async def create_user(
    request: Request,
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新用户接口"""

    try:
        role_enum = UserRole(user.role)  # 尝试将字符串转换为枚举
    except ValueError:
        raise HTTPException(status_code=HttpStatusCode.UNPROCESSABLE_ENTITY_422,
                        detail="无效的用户角色，请传入user或assistant")

    try:
        # 检查用户名是否已存在
        if await crud_user.get_by_username(user.username, db):
            return RspDetail.fail(content="用户名已存在", code=ErrorCode.DEMO_DB_CURD_11000)

        # 创建新用户
        new_user = await crud_user.create_user(
            username=user.username,
            role=user.role,
            avatar_url=user.avatar_url,
            age=user.age,
            gender=user.gender,
            bio=user.bio,
            db=db
        )

        return RspDetail(content="用户创建成功", items=new_user.dict())

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"创建用户失败！  status_code：{e.status_code} ｜ detail：{e.detail}")


@db_curd_user_router.get("/get_user", summary="获取用户信息", response_description="返回用户信息", response_model=RspDetail[UserOut])
@trace_request
async def get_user(
    request: Request,
    username: str = Query(description="用户名"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户的详细信息
    """
    try:
        user = await crud_user.get_by_username(username, db)
        if not user:
            return RspDetail.fail(content="用户不存在",
                                  code=ErrorCode.DEMO_DB_CURD_11000)
        return RspDetail(items=user)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取用户信息失败！  status_code：{e.status_code} ｜ detail：{e.detail}")


@db_curd_user_router.get("/get_users", summary="获取所有用户列表", response_description="返回用户列表", response_model=RspList[UserOut])
@trace_request
async def get_users(
        request: Request,
        skip: int = Query(default=0, description="跳过记录数"),
        limit: int = Query(default=100, description="返回记录数"),
        db: AsyncSession = Depends(get_db)
):
    """获取所有用户列表"""
    try:
        online_users = await crud_user.get_users(db, skip=skip, limit=limit)
        return RspList(items=[user.dict() for user in online_users])
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"获取用户列表失败！  status_code：{e.status_code} ｜ detail：{e.detail}")


@db_curd_user_router.put("/update_user", summary="更新用户信息", response_description="返回更新后的用户信息", response_model=RspDetail[UserOut])
@trace_request
async def update_user(
    request: Request,
    user: UserCreate,
    user_id: str = Query(description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    try:
        try:
            role_enum = UserRole(user.role)  # 验证角色是否有效
        except ValueError:
            raise HTTPException(status_code=HttpStatusCode.UNPROCESSABLE_ENTITY_422,
                            detail="无效的用户角色，请传入user或assistant")

        # 更新用户信息
        update_data = {
            "username": user.username,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "age": user.age,
            "gender": user.gender,
            "bio": user.bio
        }
        updated_user = await crud_user.update_user(
            user_id=user_id,
            update_data=update_data,
            db=db
        )
        
        return RspDetail(content="用户信息更新成功", items=updated_user.dict())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"更新用户信息失败！  status_code：{e.status_code} ｜ detail：{e.detail}")


@db_curd_user_router.delete("/fake_delete_user_by_username", summary="假删除用户", response_description="返回删除结果", response_model=RspBase)
@trace_request
async def fake_delete_user_by_username(
    request: Request,
    username: str = Query(description="用户名"),
    db: AsyncSession = Depends(get_db)
):
    """假删除用户"""
    try:
        # 检查用户是否存在
        user = await crud_user.get_by_username(username, db)
        if not user:
            return RspBase.fail(content="用户不存在", code=ErrorCode.DEMO_DB_CURD_11000)

        # 删除用户
        await crud_user.fake_delete_user_by_username(username, db)
        return RspBase(content="假用户删除成功")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"假删除用户失败！  status_code：{e.status_code} ｜ detail：{e.detail}")