"""
文件路径: backend/app/database.py
数据库模块：创建 SQLAlchemy 异步引擎和会话工厂。
使用 aiosqlite 驱动支持 SQLite 异步操作。
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步数据库引擎
# 对于 SQLite，需要设置 connect_args 中的 check_same_thread=False 以支持多线程访问
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # 生产环境建议设为 False
    connect_args={"check_same_thread": False},
)

# 创建异步会话工厂
# expire_on_commit=False 防止提交后对象过期导致无法访问属性
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类"""
    pass


async def get_db() -> AsyncSession:
    """
    数据库会话依赖注入函数。
    在 FastAPI 中作为 Depends 使用，自动管理会话的生命周期。
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库：创建所有表。
    在 FastAPI 启动事件中调用。
    """
    async with engine.begin() as conn:
        from app.models import User, Product, SeckillActivity, Order  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
