"""
文件路径: backend/app/lua/seckill.lua
秒杀原子操作 Lua 脚本。
该脚本在 Redis 服务端执行，保证整个扣减流程的原子性。

【Lua 原子性原理】
Redis 是单线程模型，Lua 脚本在执行期间不会被其他命令中断。
这意味着脚本内的所有操作要么全部成功，要么全部失败，
不存在并发竞态条件。

【与传统先查后改的对比】
传统方式：
1. GET stock -> 检查库存
2. DECR stock -> 扣减库存
问题：步骤1和2之间可能有其他请求修改了库存，导致超卖。

Lua 脚本方式：
1. 在脚本内一次性完成检查库存、检查限购、扣减库存
2. 所有操作在 Redis 服务端原子执行
3. 无需分布式锁即可保证数据一致性
"""

# Lua 脚本内容（作为字符串常量）
SECKILL_LUA_SCRIPT = """
-- KEYS[1]: 库存 key (seckill:stock:{activity_id})
-- KEYS[2]: 用户限购 key (seckill:user_limit:{activity_id}:{user_id})
-- ARGV[1]: 活动 ID
-- ARGV[2]: 用户 ID
-- ARGV[3]: 请求购买数量
-- ARGV[4]: 每人限购数量

-- 1. 检查库存是否充足
local stock = redis.call("GET", KEYS[1])
if not stock then
    return {err = "活动不存在或未预热"}
end
stock = tonumber(stock)
if stock < tonumber(ARGV[3]) then
    return {err = "库存不足"}
end

-- 2. 检查用户是否超过限购数量
local user_bought = redis.call("GET", KEYS[2])
if user_bought then
    user_bought = tonumber(user_bought)
    if user_bought + tonumber(ARGV[3]) > tonumber(ARGV[4]) then
        return {err = "超过限购数量"}
    end
end

-- 3. 扣减库存（原子操作）
redis.call("DECRBY", KEYS[1], tonumber(ARGV[3]))

-- 4. 记录用户已购数量
if user_bought then
    redis.call("INCRBY", KEYS[2], tonumber(ARGV[3]))
else
    redis.call("SET", KEYS[2], tonumber(ARGV[3]))
end

-- 5. 设置用户限购 key 的过期时间（与活动结束时间对齐，这里设为 2 小时）
redis.call("EXPIRE", KEYS[2], 7200)

-- 返回成功，包含扣减后的库存
local remaining = redis.call("GET", KEYS[1])
return {ok = "秒杀成功", remaining = tonumber(remaining)}
"""


def get_seckill_lua_script() -> str:
    """获取秒杀 Lua 脚本"""
    return SECKILL_LUA_SCRIPT
