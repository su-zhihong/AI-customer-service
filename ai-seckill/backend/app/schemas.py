"""
文件路径: backend/app/schemas.py
Pydantic 模型模块：定义请求和响应的数据模型，用于 API 数据校验。
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 用户相关 ====================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field("", description="昵称")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """JWT Token 响应"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token 类型")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 商品相关 ====================

class ProductCreateRequest(BaseModel):
    """创建商品请求"""
    name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    description: str = Field("", description="商品描述")
    image_url: str = Field("", description="商品图片 URL")
    original_price: float = Field(..., gt=0, description="商品原价")
    category: str = Field("", description="商品分类")
    material: str = Field("", description="材质信息")
    specs: str = Field("", description="规格参数")


class ProductResponse(BaseModel):
    """商品信息响应"""
    id: int
    name: str
    description: str
    image_url: str
    original_price: float
    category: str
    material: str
    specs: str
    created_at: datetime
    ai_welcome: Optional[str] = Field("", description="AI 助手欢迎语")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """商品列表响应"""
    items: List[ProductResponse]
    total: int


# ==================== 秒杀活动相关 ====================

class SeckillActivityCreateRequest(BaseModel):
    """创建秒杀活动请求"""
    product_id: int = Field(..., description="商品 ID")
    seckill_price: float = Field(..., gt=0, description="秒杀价格")
    total_stock: int = Field(..., gt=0, description="秒杀总库存")
    limit_per_user: int = Field(1, ge=1, description="每人限购数量")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")


class SeckillActivityResponse(BaseModel):
    """秒杀活动信息响应"""
    id: int
    product_id: int
    product_name: Optional[str] = Field("", description="商品名称")
    product_image: Optional[str] = Field("", description="商品图片")
    seckill_price: float
    original_price: Optional[float] = Field(0, description="商品原价")
    total_stock: int
    limit_per_user: int
    start_time: datetime
    end_time: datetime
    is_active: bool
    status: Optional[str] = Field("", description="活动状态: not_started/in_progress/ended")
    remaining_stock: Optional[int] = Field(0, description="剩余库存（来自 Redis）")
    created_at: datetime

    class Config:
        from_attributes = True


class SeckillExecuteResponse(BaseModel):
    """秒杀执行结果响应"""
    success: bool
    message: str
    order_id: Optional[int] = None


# ==================== 订单相关 ====================

class OrderResponse(BaseModel):
    """订单信息响应"""
    id: int
    user_id: int
    product_id: int
    product_name: Optional[str] = ""
    product_image: Optional[str] = ""
    seckill_activity_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应"""
    items: List[OrderResponse]
    total: int


# ==================== AI Agent 相关 ====================

class AgentChatRequest(BaseModel):
    """AI 对话请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    product_id: Optional[int] = Field(None, description="关联商品 ID（可选）")


class AgentChatResponse(BaseModel):
    """AI 对话响应"""
    answer: str
    sources: Optional[List[str]] = Field([], description="信息来源")
