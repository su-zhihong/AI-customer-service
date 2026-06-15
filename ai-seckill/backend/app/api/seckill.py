"""
文件路径: backend/app/api/seckill.py
秒杀模块 API 路由：秒杀活动管理、执行秒杀。
包含秒杀核心逻辑：Lua 原子扣减、分布式锁、消息队列。
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Product, SeckillActivity, User
from app.schemas import (
    SeckillActivityCreateRequest, SeckillActivityResponse,
    SeckillExecuteResponse,
)
from app.auth import get_current_user
from app.redis_client import redis_client, seckill_redis
from app.lua.seckill import get_seckill_lua_script

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/seckill", tags=["秒杀模块"])


@router.post("/activities", response_model=SeckillActivityResponse, summary="创建秒杀活动（管理员）")
async def create_activity(
    req: SeckillActivityCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建秒杀活动。
    1. 验证商品存在
    2. 创建活动记录到 SQLite
    3. 预热数据到 Redis（Hash + 库存计数器）
    """
    # 验证商品存在
    result = await db.execute(select(Product).where(Product.id == req.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 创建秒杀活动
    activity = SeckillActivity(
        product_id=req.product_id,
        seckill_price=req.seckill_price,
        total_stock=req.total_stock,
        limit_per_user=req.limit_per_user,
        start_time=req.start_time,
        end_time=req.end_time,
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)

    # 预热数据到 Redis
    await seckill_redis.warm_up_activity(
        activity_id=activity.id,
        stock=req.total_stock,
        limit_per_user=req.limit_per_user,
        seckill_price=req.seckill_price,
        start_time=req.start_time.isoformat(),
        end_time=req.end_time.isoformat(),
    )

    logger.info(f"秒杀活动已创建并预热: ID={activity.id}, 商品={product.name}, 库存={req.total_stock}")

    return SeckillActivityResponse(
        id=activity.id,
        product_id=activity.product_id,
        product_name=product.name,
        product_image=product.image_url,
        seckill_price=activity.seckill_price,
        original_price=product.original_price,
        total_stock=activity.total_stock,
        limit_per_user=activity.limit_per_user,
        start_time=activity.start_time,
        end_time=activity.end_time,
        is_active=activity.is_active,
        status="not_started",
        remaining_stock=req.total_stock,
        created_at=activity.created_at,
    )


@router.get("/activities", summary="获取秒杀活动列表")
async def get_activities(db: AsyncSession = Depends(get_db)):
    """
    获取所有秒杀活动列表。
    从数据库加载活动信息，并从 Redis 获取实时库存。
    """
    result = await db.execute(
        select(SeckillActivity).order_by(SeckillActivity.start_time.desc())
    )
    activities = result.scalars().all()

    response_list = []
    now = datetime.utcnow()

    for activity in activities:
        # 获取关联商品信息
        product_result = await db.execute(
            select(Product).where(Product.id == activity.product_id)
        )
        product = product_result.scalar_one_or_none()

        # 判断活动状态
        if now < activity.start_time:
            status_str = "not_started"
        elif now > activity.end_time:
            status_str = "ended"
        else:
            status_str = "in_progress"

        # 从 Redis 获取实时库存
        remaining = await seckill_redis.get_remaining_stock(activity.id)

        response_list.append(SeckillActivityResponse(
            id=activity.id,
            product_id=activity.product_id,
            product_name=product.name if product else "",
            product_image=product.image_url if product else "",
            seckill_price=activity.seckill_price,
            original_price=product.original_price if product else 0,
            total_stock=activity.total_stock,
            limit_per_user=activity.limit_per_user,
            start_time=activity.start_time,
            end_time=activity.end_time,
            is_active=activity.is_active,
            status=status_str,
            remaining_stock=remaining,
            created_at=activity.created_at,
        ))

    return {"items": response_list, "total": len(response_list)}


@router.get("/activities/{activity_id}", summary="获取秒杀活动详情")
async def get_activity_detail(activity_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个秒杀活动的详细信息"""
    result = await db.execute(
        select(SeckillActivity).where(SeckillActivity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="秒杀活动不存在")

    product_result = await db.execute(
        select(Product).where(Product.id == activity.product_id)
    )
    product = product_result.scalar_one_or_none()

    now = datetime.utcnow()
    if now < activity.start_time:
        status_str = "not_started"
    elif now > activity.end_time:
        status_str = "ended"
    else:
        status_str = "in_progress"

    remaining = await seckill_redis.get_remaining_stock(activity.id)

    return SeckillActivityResponse(
        id=activity.id,
        product_id=activity.product_id,
        product_name=product.name if product else "",
        product_image=product.image_url if product else "",
        seckill_price=activity.seckill_price,
        original_price=product.original_price if product else 0,
        total_stock=activity.total_stock,
        limit_per_user=activity.limit_per_user,
        start_time=activity.start_time,
        end_time=activity.end_time,
        is_active=activity.is_active,
        status=status_str,
        remaining_stock=remaining,
        created_at=activity.created_at,
    )


@router.post("/{activity_id}/execute", response_model=SeckillExecuteResponse, summary="执行秒杀")
async def execute_seckill(
    activity_id: int,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    执行秒杀核心逻辑。
    
    流程：
    1. 检查活动时间
    2. 使用分布式锁防止用户重复下单
    3. 使用 Lua 脚本原子扣减库存
    4. 成功后将订单推入 Redis 消息队列
    5. 后台任务异步持久化订单到 SQLite
    
    高并发设计要点：
    - Lua 脚本保证库存扣减原子性，防止超卖
    - 分布式锁防止同一用户并发重复下单
    - Redis 消息队列异步写库，降低响应延迟
    """
    # 1. 检查活动是否存在
    result = await db.execute(
        select(SeckillActivity).where(SeckillActivity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="秒杀活动不存在")

    # 2. 检查活动时间
    now = datetime.utcnow()
    if now < activity.start_time:
        return SeckillExecuteResponse(success=False, message="秒杀尚未开始")
    if now > activity.end_time:
        return SeckillExecuteResponse(success=False, message="秒杀已结束")

    # 3. 使用分布式锁防止同一用户重复下单
    user_lock_key = seckill_redis.USER_LOCK_KEY.format(
        activity_id=activity_id, user_id=current_user.id
    )

    try:
        async with redis_client.distributed_lock(user_lock_key, timeout_ms=5000):
            # 4. 执行 Lua 脚本原子扣减
            lua_script = get_seckill_lua_script()
            redis_conn = redis_client.get_client()

            # Lua 脚本参数
            stock_key = seckill_redis.STOCK_KEY.format(activity_id=activity_id)
            user_limit_key = seckill_redis.USER_LIMIT_KEY.format(
                activity_id=activity_id, user_id=current_user.id
            )

            try:
                # 执行 Lua 脚本
                result = await redis_conn.eval(
                    lua_script,
                    2,  # KEYS 数量
                    stock_key,
                    user_limit_key,
                    activity_id,
                    current_user.id,
                    quantity,
                    activity.limit_per_user,
                )
            except Exception as e:
                logger.error(f"Lua 脚本执行失败: {e}")
                return SeckillExecuteResponse(success=False, message="秒杀失败，请重试")

            # 解析 Lua 脚本返回结果
            # Redis 返回格式：{ok="秒杀成功", remaining=xx} 或 {err="错误信息"}
            if isinstance(result, dict):
                if "err" in result:
                    return SeckillExecuteResponse(
                        success=False,
                        message=result["err"],
                    )
                elif "ok" in result:
                    # 5. 秒杀成功，获取商品信息
                    product_result = await db.execute(
                        select(Product).where(Product.id == activity.product_id)
                    )
                    product = product_result.scalar_one_or_none()

                    # 6. 将订单信息推入 Redis 消息队列
                    order_data = {
                        "user_id": current_user.id,
                        "product_id": activity.product_id,
                        "seckill_activity_id": activity_id,
                        "quantity": quantity,
                        "total_price": activity.seckill_price * quantity,
                    }
                    await seckill_redis.push_order_to_queue(order_data)

                    logger.info(
                        f"秒杀成功: 用户={current_user.id}, "
                        f"活动={activity_id}, 剩余库存={result.get('remaining')}"
                    )

                    return SeckillExecuteResponse(
                        success=True,
                        message="🎉 抢购成功！订单正在处理中",
                    )

            return SeckillExecuteResponse(success=False, message="秒杀失败，请重试")

    except TimeoutError:
        # 分布式锁获取失败，说明用户正在并发操作
        return SeckillExecuteResponse(
            success=False,
            message="操作过于频繁，请稍后重试",
        )
