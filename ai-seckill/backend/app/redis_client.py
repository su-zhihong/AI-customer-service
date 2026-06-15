"""
文件路径: backend/app/redis_client.py
Redis 客户端模块：连接池管理、分布式锁、缓存工具函数。
包含缓存雪崩/击穿/穿透的预防策略实现。
"""

import asyncio
import json
import random
import time
import uuid
from typing import Optional, Any, Callable

import redis.asyncio as aioredis

from app.config import settings


class RedisClient:
    """
    Redis 客户端封装类。
    提供连接池管理、分布式锁、缓存操作等高级功能。
    """

    def __init__(self):
        """初始化 Redis 连接池"""
        self.pool: Optional[aioredis.Redis] = None

    async def init_pool(self):
        """
        创建 Redis 连接池。
        使用连接池而非单连接，支持高并发场景下的连接复用。
        """
        self.pool = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,  # 自动将字节解码为字符串
            max_connections=50,     # 最大连接数，根据并发量调整
        )
        # 测试连接是否正常
        await self.pool.ping()

    async def close(self):
        """关闭 Redis 连接池"""
        if self.pool:
            await self.pool.close()

    def get_client(self) -> aioredis.Redis:
        """获取 Redis 客户端实例"""
        return self.pool

    # ==================== 缓存雪崩预防 ====================
    """
    【缓存雪崩】
    概念：大量缓存数据在同一时间过期失效，导致所有请求直接打到数据库，
    可能造成数据库瞬间压力过大甚至崩溃。

    预防策略：对缓存 TTL 添加随机值，避免大量 key 同时过期。
    实现：在基础 TTL 上增加 0~600 秒的随机偏移。
    """

    async def set_cache_with_random_ttl(
        self, key: str, value: Any, base_ttl: int = 3600, extra_ttl_range: int = 600
    ):
        """
        设置缓存，TTL 添加随机值以预防缓存雪崩。
        
        Args:
            key: 缓存键
            value: 缓存值（会自动 JSON 序列化）
            base_ttl: 基础过期时间（秒）
            extra_ttl_range: 随机额外时间范围（秒）
        """
        ttl = base_ttl + random.randint(0, extra_ttl_range)
        serialized = json.dumps(value, ensure_ascii=False, default=str)
        await self.pool.setex(key, ttl, serialized)

    # ==================== 缓存击穿预防 ====================
    """
    【缓存击穿】
    概念：某个热点 key 在缓存过期的瞬间，大量并发请求同时访问该 key，
    导致所有请求都穿透到数据库。

    预防策略：使用互斥锁（SETNX），只允许一个请求去加载数据，
    其他请求等待后读取新缓存。
    """

    async def get_or_refresh_cache(
        self,
        key: str,
        fetch_func: Callable,
        base_ttl: int = 3600,
        extra_ttl_range: int = 600,
        lock_timeout: int = 5,
    ) -> Any:
        """
        获取缓存，如果缓存不存在则使用互斥锁防止缓存击穿。
        
        Args:
            key: 缓存键
            fetch_func: 从数据库加载数据的异步函数
            base_ttl: 基础过期时间
            extra_ttl_range: 随机额外时间范围
            lock_timeout: 锁超时时间（秒）
        
        Returns:
            缓存数据
        """
        # 1. 尝试从缓存读取
        cached = await self.pool.get(key)
        if cached is not None:
            return json.loads(cached)

        # 2. 缓存未命中，尝试获取互斥锁
        lock_key = f"lock:{key}"
        lock_value = str(uuid.uuid4())

        # 使用 SET NX 尝试获取锁，防止缓存击穿
        # 只有第一个到达的请求能成功设置锁
        locked = await self.pool.set(
            lock_key, lock_value,
            nx=True,          # 只有 key 不存在时才设置
            px=lock_timeout * 1000  # 锁的过期时间（毫秒）
        )

        if locked:
            try:
                # 3. 获取到锁的请求负责加载数据
                # 再次检查缓存（双重检查锁定模式）
                cached = await self.pool.get(key)
                if cached is not None:
                    return json.loads(cached)

                # 从数据库加载数据
                data = await fetch_func()
                if data is not None:
                    # 写入缓存，带随机 TTL 预防雪崩
                    await self.set_cache_with_random_ttl(key, data, base_ttl, extra_ttl_range)
                else:
                    # ==================== 缓存穿透预防 ====================
                    """
                    【缓存穿透】
                    概念：查询一个不存在的数据，缓存和数据库都没有，
                    导致每次请求都穿透到数据库。

                    预防策略：将空值也写入缓存，设置较短的过期时间。
                    """
                    await self.pool.setex(key, 60, json.dumps(None))
                return data
            finally:
                # 4. 安全释放锁（使用 Lua 脚本确保原子性）
                await self._safe_release_lock(lock_key, lock_value)
        else:
            # 5. 未获取到锁的请求等待后重试
            await asyncio.sleep(0.1)
            return await self.get_or_refresh_cache(
                key, fetch_func, base_ttl, extra_ttl_range, lock_timeout
            )

    # ==================== 分布式锁 ====================
    """
    【分布式锁】
    原理：在分布式系统中，多个服务实例需要互斥访问共享资源时，
    使用 Redis 的 SET NX 命令实现分布式锁。
    
    关键设计：
    1. 使用唯一值（UUID）标识锁的持有者，防止误释放其他实例的锁
    2. 设置锁的过期时间，防止死锁
    3. 使用 Lua 脚本原子性地释放锁，确保校验和删除的原子性
    """

    async def acquire_lock(self, lock_key: str, lock_value: str, timeout_ms: int = 5000) -> bool:
        """
        获取分布式锁。
        
        Args:
            lock_key: 锁的键
            lock_value: 锁的唯一标识值（用于安全释放）
            timeout_ms: 锁的超时时间（毫秒）
        
        Returns:
            是否成功获取锁
        """
        result = await self.pool.set(
            lock_key, lock_value,
            nx=True,
            px=timeout_ms,
        )
        return result is not None

    async def _safe_release_lock(self, lock_key: str, lock_value: str):
        """
        安全释放分布式锁。
        使用 Lua 脚本确保比较和删除的原子性，防止误删其他实例的锁。
        
        Lua 脚本原理：
        - 在 Redis 服务端执行，保证原子性
        - 先比较 value 是否匹配，匹配才删除
        - 避免因操作超时导致锁被其他实例获取后误删
        """
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.pool.eval(lua_script, 1, lock_key, lock_value)

    # ==================== 分布式锁上下文管理器 ====================
    """
    分布式锁上下文管理器。
    使用 async with 语法简化锁的获取和释放。
    
    使用示例：
        async with redis_client.distributed_lock("my_lock"):
            # 执行需要互斥访问的代码
            pass
    """

    def distributed_lock(self, lock_key: str, timeout_ms: int = 5000):
        """返回分布式锁上下文管理器"""
        return _DistributedLock(self, lock_key, timeout_ms)


class _DistributedLock:
    """
    分布式锁上下文管理器实现。
    在 __aenter__ 中获取锁，在 __aexit__ 中释放锁。
    """

    def __init__(self, redis_client: RedisClient, lock_key: str, timeout_ms: int):
        self.redis = redis_client
        self.lock_key = f"distlock:{lock_key}"
        self.lock_value = str(uuid.uuid4())
        self.timeout_ms = timeout_ms

    async def __aenter__(self):
        """进入上下文时获取锁"""
        acquired = await self.redis.acquire_lock(self.lock_key, self.lock_value, self.timeout_ms)
        if not acquired:
            raise TimeoutError(f"获取分布式锁失败: {self.lock_key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时释放锁"""
        await self.redis._safe_release_lock(self.lock_key, self.lock_value)


# ==================== 秒杀相关 Redis 操作 ====================

class SeckillRedisHelper:
    """
    秒杀模块的 Redis 操作辅助类。
    管理秒杀活动的缓存预热、库存操作等。
    """

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client.get_client()

    # Redis Key 命名规范
    ACTIVITY_HASH_KEY = "seckill:activity:{activity_id}"       # 活动信息 Hash
    STOCK_KEY = "seckill:stock:{activity_id}"                   # 库存计数器
    USER_LIMIT_KEY = "seckill:user_limit:{activity_id}:{user_id}"  # 用户限购计数器
    ORDER_QUEUE_KEY = "seckill:order_queue"                     # 订单消息队列（List）
    USER_LOCK_KEY = "seckill:user_lock:{activity_id}:{user_id}" # 用户防重复下单锁

    async def warm_up_activity(self, activity_id: int, stock: int, limit_per_user: int,
                                seckill_price: float, start_time: str, end_time: str):
        """
        秒杀活动预热：将活动数据写入 Redis。
        在活动开始前调用，将数据从数据库加载到缓存。
        """
        # 使用 Hash 结构存储活动信息，方便读取单个字段
        hash_key = self.ACTIVITY_HASH_KEY.format(activity_id=activity_id)
        await self.redis.hset(hash_key, mapping={
            "stock": stock,
            "limit_per_user": limit_per_user,
            "seckill_price": seckill_price,
            "start_time": start_time,
            "end_time": end_time,
        })
        # 设置 Hash 的过期时间，与活动结束时间对齐
        # 这里使用基础 TTL + 随机值预防缓存雪崩
        base_ttl = 7200  # 2小时基础
        random_extra = random.randint(0, 600)
        await self.redis.expire(hash_key, base_ttl + random_extra)

        # 使用独立的 String key 存储库存，方便 Lua 脚本原子操作
        stock_key = self.STOCK_KEY.format(activity_id=activity_id)
        await self.redis.set(stock_key, stock)

    async def get_activity_info(self, activity_id: int) -> dict:
        """从 Redis 获取秒杀活动信息"""
        hash_key = self.ACTIVITY_HASH_KEY.format(activity_id=activity_id)
        data = await self.redis.hgetall(hash_key)
        return data

    async def get_remaining_stock(self, activity_id: int) -> int:
        """获取秒杀活动剩余库存"""
        stock_key = self.STOCK_KEY.format(activity_id=activity_id)
        stock = await self.redis.get(stock_key)
        return int(stock) if stock is not None else 0

    async def push_order_to_queue(self, order_data: dict):
        """
        将订单信息推入 Redis 消息队列。
        秒杀成功后，订单数据先进入 Redis List，
        由后台任务异步消费写入数据库。
        """
        serialized = json.dumps(order_data, ensure_ascii=False, default=str)
        await self.redis.lpush(self.ORDER_QUEUE_KEY, serialized)

    async def pop_order_from_queue(self) -> Optional[dict]:
        """从 Redis 消息队列取出订单数据（供后台任务消费）"""
        data = await self.redis.rpop(self.ORDER_QUEUE_KEY)
        if data:
            return json.loads(data)
        return None

    async def get_queue_length(self) -> int:
        """获取订单消息队列长度"""
        return await self.redis.llen(self.ORDER_QUEUE_KEY)


# 全局 Redis 客户端实例
redis_client = RedisClient()
seckill_redis = SeckillRedisHelper(redis_client)
