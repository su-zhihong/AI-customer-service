"""
文件路径: backend/app/tasks/order_consumer.py
订单消费后台任务模块。
从 Redis 消息队列中消费订单数据，异步写入 SQLite 数据库。
实现秒杀订单的最终持久化。
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models import Order, OrderStatus
from app.redis_client import seckill_redis

logger = logging.getLogger(__name__)


async def consume_order():
    """
    消费订单消息队列中的一条订单数据。
    从 Redis List 中取出订单信息，写入 SQLite 数据库。
    """
    # 从 Redis 队列取出订单数据
    order_data = await seckill_redis.pop_order_from_queue()
    if order_data is None:
        return False

    try:
        # 写入数据库
        async with async_session_factory() as session:
            async with session.begin():
                order = Order(
                    user_id=order_data["user_id"],
                    product_id=order_data["product_id"],
                    seckill_activity_id=order_data["seckill_activity_id"],
                    quantity=order_data["quantity"],
                    total_price=order_data["total_price"],
                    status=OrderStatus.PENDING.value,
                    created_at=datetime.utcnow(),
                )
                session.add(order)
            await session.commit()
            logger.info(
                f"订单已持久化: 用户={order_data['user_id']}, "
                f"活动={order_data['seckill_activity_id']}, "
                f"数量={order_data['quantity']}"
            )
        return True
    except Exception as e:
        logger.error(f"订单持久化失败: {e}, 数据: {order_data}")
        # 消费失败，将数据重新放回队列（可根据需要实现重试机制）
        await seckill_redis.push_order_to_queue(order_data)
        return False


async def start_order_consumer(interval: float = 0.1):
    """
    启动订单消费后台任务。
    持续轮询 Redis 消息队列，消费订单数据。
    
    Args:
        interval: 轮询间隔（秒），默认 0.1 秒
    """
    logger.info("订单消费后台任务已启动")
    while True:
        try:
            consumed = await consume_order()
            if not consumed:
                # 队列为空时，短暂休眠避免空轮询
                await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"订单消费任务异常: {e}")
            await asyncio.sleep(1)
