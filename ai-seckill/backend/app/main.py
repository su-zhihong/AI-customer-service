"""
文件路径: backend/app/main.py
FastAPI 应用入口。
包含应用初始化、启动事件、路由注册、CORS 配置等。
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session_factory
from app.redis_client import redis_client
from app.agent.rag import build_product_knowledge_base
from app.tasks.order_consumer import start_order_consumer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。
    startup: 初始化数据库、Redis 连接池、向量库、启动后台任务
    shutdown: 清理资源
    """
    logger.info("🚀 AI 智能秒杀系统启动中...")

    # 1. 初始化数据库表
    await init_db()
    logger.info("✅ 数据库初始化完成")

    # 2. 初始化 Redis 连接池
    try:
        await redis_client.init_pool()
        logger.info("✅ Redis 连接池初始化完成")
    except Exception as e:
        logger.warning(f"⚠️ Redis 连接失败，部分功能不可用: {e}")

    # 3. 构建商品知识向量库（RAG）
    try:
        async with async_session_factory() as session:
            await build_product_knowledge_base(session)
        logger.info("✅ 商品知识向量库构建完成")
    except Exception as e:
        logger.warning(f"⚠️ 向量库构建失败，AI 问答功能可能受限: {e}")

    # 4. 启动订单消费后台任务
    consumer_task = asyncio.create_task(start_order_consumer())
    logger.info("✅ 订单消费后台任务已启动")

    yield

    # 关闭时清理资源
    consumer_task.cancel()
    await redis_client.close()
    logger.info("👋 应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI 智能秒杀系统",
    description="AI-Powered Seckill Agent System - 融合 AI Agent、高并发秒杀、Redis 深度应用的电商平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 注册路由 ====================

from app.api import users, products, seckill, orders, agent

app.include_router(users.router)
app.include_router(products.router)
app.include_router(seckill.router)
app.include_router(orders.router)
app.include_router(agent.router)


@app.get("/", tags=["健康检查"])
async def root():
    """根路径，返回服务状态"""
    return {
        "service": "AI 智能秒杀系统",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
