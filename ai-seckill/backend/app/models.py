"""
文件路径: backend/app/models.py
ORM 模型模块：定义 User、Product、SeckillActivity、Order 四个数据表。
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    nickname = Column(String(50), default="", comment="昵称")
    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")

    # 关联关系
    orders = relationship("Order", back_populates="user")


class Product(Base):
    """商品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="商品名称")
    description = Column(Text, default="", comment="商品详细描述")
    image_url = Column(String(500), default="", comment="商品图片 URL")
    original_price = Column(Float, nullable=False, comment="商品原价")
    category = Column(String(100), default="", comment="商品分类")
    material = Column(String(200), default="", comment="材质信息")
    specs = Column(String(500), default="", comment="规格参数（JSON 字符串）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    seckill_activities = relationship("SeckillActivity", back_populates="product")


class SeckillActivity(Base):
    """秒杀活动模型"""
    __tablename__ = "seckill_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="关联商品 ID")
    seckill_price = Column(Float, nullable=False, comment="秒杀价格")
    total_stock = Column(Integer, nullable=False, comment="秒杀总库存")
    limit_per_user = Column(Integer, default=1, comment="每人限购数量")
    start_time = Column(DateTime, nullable=False, comment="秒杀开始时间")
    end_time = Column(DateTime, nullable=False, comment="秒杀结束时间")
    is_active = Column(Boolean, default=True, comment="活动是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    product = relationship("Product", back_populates="seckill_activities")
    orders = relationship("Order", back_populates="seckill_activity")


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付（秒杀成功自动生成）
    PAID = "paid"            # 已支付（模拟）
    CANCELLED = "cancelled"  # 已取消


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户 ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品 ID")
    seckill_activity_id = Column(Integer, ForeignKey("seckill_activities.id"), nullable=False, comment="秒杀活动 ID")
    quantity = Column(Integer, default=1, comment="购买数量")
    total_price = Column(Float, nullable=False, comment="订单总价")
    status = Column(String(20), default=OrderStatus.PENDING.value, comment="订单状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    paid_at = Column(DateTime, nullable=True, comment="支付时间")

    # 关联关系
    user = relationship("User", back_populates="orders")
    product = relationship("Product")
    seckill_activity = relationship("SeckillActivity", back_populates="orders")
