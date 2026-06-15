"""
文件路径: backend/app/api/orders.py
订单模块 API 路由：订单列表查询、模拟支付。
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Order, OrderStatus, Product, User
from app.schemas import OrderResponse, OrderListResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["订单模块"])


@router.get("", response_model=OrderListResponse, summary="获取用户订单列表")
async def get_orders(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的订单列表。
    按创建时间倒序排列。
    """
    query = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    # 获取总数
    count_query = select(Order).where(Order.user_id == current_user.id)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # 组装响应数据，包含商品名称和图片
    items = []
    for order in orders:
        product_result = await db.execute(
            select(Product).where(Product.id == order.product_id)
        )
        product = product_result.scalar_one_or_none()

        items.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            product_name=product.name if product else "",
            product_image=product.image_url if product else "",
            seckill_activity_id=order.seckill_activity_id,
            quantity=order.quantity,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
            paid_at=order.paid_at,
        ))

    return OrderListResponse(items=items, total=total)


@router.post("/{order_id}/pay", summary="模拟支付")
async def pay_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    模拟支付接口。
    将订单状态从"待支付"变更为"已支付"。
    实际项目中会对接真实的支付网关。
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单状态不允许支付（当前状态: {order.status}）",
        )

    # 更新订单状态
    order.status = OrderStatus.PAID.value
    order.paid_at = datetime.utcnow()
    await db.flush()

    return {"success": True, "message": "支付成功", "order_id": order.id}


@router.post("/{order_id}/cancel", summary="取消订单")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    取消订单。
    只有待支付的订单可以取消。
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单状态不允许取消（当前状态: {order.status}）",
        )

    order.status = OrderStatus.CANCELLED.value
    await db.flush()

    return {"success": True, "message": "订单已取消", "order_id": order.id}
