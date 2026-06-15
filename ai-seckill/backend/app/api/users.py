"""
文件路径: backend/app/api/users.py
用户模块 API 路由：注册、登录、获取用户信息。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserInfoResponse,
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["用户模块"])


@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册接口。
    检查用户名唯一性，密码哈希存储，返回 JWT token。
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建新用户
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.username,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 生成 JWT token
    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录接口。
    验证用户名和密码，返回 JWT token。
    """
    # 查询用户
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 JWT token
    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return current_user
