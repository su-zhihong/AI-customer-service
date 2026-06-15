"""
文件路径: backend/app/api/products.py
商品模块 API 路由：商品列表、商品详情、添加商品（管理员）。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Product, User
from app.schemas import (
    ProductCreateRequest, ProductResponse, ProductListResponse,
)
from app.auth import get_current_user
from app.redis_client import redis_client

router = APIRouter(prefix="/api/products", tags=["商品模块"])


@router.get("", response_model=ProductListResponse, summary="获取商品列表")
async def get_products(
    search: str = "",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    获取商品列表，支持搜索和分页。
    使用 Redis 缓存商品列表数据，带随机 TTL 预防缓存雪崩。
    """
    cache_key = f"products:list:{search}:{skip}:{limit}"

    async def fetch_products():
        """从数据库加载商品列表"""
        query = select(Product)
        if search:
            query = query.where(Product.name.contains(search))
        query = query.offset(skip).limit(limit).order_by(Product.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()

        # 获取总数
        count_query = select(Product)
        if search:
            count_query = count_query.where(Product.name.contains(search))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "items": [ProductResponse.model_validate(p) for p in items],
            "total": total,
        }

    # 使用 Redis 缓存，带互斥锁防止缓存击穿
    data = await redis_client.get_or_refresh_cache(
        key=cache_key,
        fetch_func=fetch_products,
        base_ttl=3600,
        extra_ttl_range=600,
    )
    return data


@router.get("/{product_id}", response_model=ProductResponse, summary="获取商品详情")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取商品详情。
    包含 AI 助手的欢迎语。
    使用 Redis 缓存，带空值缓存预防缓存穿透。
    """
    cache_key = f"product:{product_id}"

    async def fetch_product():
        """从数据库加载商品"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product is None:
            return None
        response = ProductResponse.model_validate(product)
        # 添加 AI 助手欢迎语
        response.ai_welcome = (
            f"你好！我是智能助手小秒，很高兴为你服务！\n"
            f"关于「{product.name}」的任何问题，比如规格、材质、价格、优惠规则等，"
            f"或者想了解相关秒杀活动的实时状态，都可以问我哦！"
        )
        return response

    # 使用 Redis 缓存，如果商品不存在会缓存空值（60秒过期）预防穿透
    data = await redis_client.get_or_refresh_cache(
        key=cache_key,
        fetch_func=fetch_product,
        base_ttl=3600,
        extra_ttl_range=600,
    )

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )
    return data


@router.post("", response_model=ProductResponse, summary="添加商品（管理员）")
async def create_product(
    req: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    添加商品（需要登录）。
    商品数据存入 SQLite，后续可通过 init_products.py 或启动事件构建向量库。
    """
    product = Product(
        name=req.name,
        description=req.description,
        image_url=req.image_url,
        original_price=req.original_price,
        category=req.category,
        material=req.material,
        specs=req.specs,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    # 清除商品列表缓存，下次请求会重新加载
    await redis_client.get_client().flushall()

    return ProductResponse.model_validate(product)
