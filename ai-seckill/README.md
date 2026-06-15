# 🚀 AI 智能秒杀系统 (AI-Powered Seckill Agent System)

## 📖 项目简介

**AI 智能秒杀系统**是一个融合了 AI Agent、高并发秒杀和 Redis 深度应用的电商平台实战项目。系统模拟了电商平台的秒杀会场场景，集成了 AI 智能客服助手，用户在抢购前和抢购过程中可以随时向 AI 助手咨询商品细节和活动状态。

### 业务场景

在一个电商平台的秒杀会场中：
- **用户**可以在商品详情页浏览商品，并通过 AI 助手询问规格、材质、优惠规则等细节
- **AI 助手**通过 RAG（检索增强生成）技术从商品知识库中检索信息，并从 Redis 获取秒杀活动的实时数据（剩余库存、限购数量等）
- **秒杀功能**承载高并发压力，通过 Redis 的 Lua 脚本、分布式锁、消息队列等机制保证数据一致性和系统稳定性

### 项目定位

本项目适合计算机专业大三学生作为简历项目，能够展示以下能力：
- **AI Agent 构建**：使用 LangChain 构建智能 Agent，集成工具调用和 RAG
- **高并发秒杀**：Redis 深度应用，Lua 原子操作，分布式锁
- **全栈开发**：FastAPI + React 前后端分离架构
- **系统设计**：缓存策略、消息队列、异步处理

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (React + Vite)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │  登录注册  │ │ 商品浏览  │ │ 秒杀抢购  │ │ AI 智能对话   │  │
│  │  页面     │ │  页面    │ │  页面    │ │  组件        │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬────────┘  │
│       └────────────┴────────────┴──────────────┘           │
│                        │ Axios + JWT                        │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│              后端 (FastAPI)                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ 用户模块  │ │ 商品模块  │ │ 秒杀模块  │ │ AI Agent 模块 │  │
│  │ JWT 认证  │ │ CRUD     │ │ Lua 脚本 │ │ LangChain     │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬────────┘  │
│       └────────────┴────────────┴──────────────┘           │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌──────────┐     ┌──────────┐          ┌──────────┐
│  SQLite   │     │  Redis   │          │ ChromaDB │
│ (持久化)  │     │ (缓存/   │          │ (向量库) │
│          │     │  队列/锁)│          │          │
└──────────┘     └──────────┘          └──────────┘
```

### 数据流

1. **用户请求** → FastAPI 路由 → JWT 认证 → 业务逻辑处理
2. **商品查询** → Redis 缓存（防雪崩/击穿/穿透）→ SQLite 数据库
3. **秒杀流程** → 分布式锁（防重复下单）→ Lua 脚本（原子扣减）→ Redis 消息队列 → 异步写入 SQLite
4. **AI 问答** → LangChain Agent → 工具调用（RAG 检索 / Redis 查询）→ LLM 生成回答

---

## 🛠️ 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| Python 3.11+ | 编程语言 |
| FastAPI | 异步 Web 框架 |
| LangChain | AI Agent 框架，集成工具调用和 RAG |
| OpenAI API | LLM（gpt-4o-mini）和 Embedding（text-embedding-ada-002） |
| Redis | 缓存、秒杀库存、分布式锁、Lua 原子操作、消息队列 |
| SQLite + aiosqlite | 本地数据库，异步驱动 |
| SQLAlchemy 2.0 | ORM 框架，异步支持 |
| ChromaDB | 向量存储，用于 RAG 检索 |
| Pydantic | 数据校验 |
| python-jose | JWT 认证 |
| passlib | 密码哈希（bcrypt） |

### 前端
| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| Vite | 构建工具 |
| Ant Design 5 | 企业级 UI 组件库 |
| Tailwind CSS | 辅助样式 |
| Axios | HTTP 请求 |
| react-router-dom | 前端路由 |

---

## ✨ 功能列表

### 用户模块
- [x] 用户注册（密码 bcrypt 哈希存储）
- [x] 用户登录（返回 JWT token）
- [x] 获取当前用户信息

### 商品模块
- [x] 商品列表（支持搜索和分页）
- [x] 商品详情（含 AI 助手欢迎语）
- [x] 添加商品（管理员功能）
- [x] Redis 缓存（防雪崩/击穿/穿透）

### AI 智能问答模块
- [x] LangChain Agent（OpenAI Functions 模式）
- [x] RAG 商品知识检索（ChromaDB 向量库）
- [x] 秒杀状态实时查询（Redis）
- [x] 对话接口 `/api/agent/chat`

### 秒杀模块
- [x] 创建秒杀活动（预热到 Redis）
- [x] Lua 脚本原子扣减库存
- [x] 分布式锁防止重复下单
- [x] Redis 消息队列异步写库
- [x] 活动状态管理（未开始/进行中/已结束）

### 订单模块
- [x] 订单列表查询
- [x] 模拟支付
- [x] 取消订单

### 前端特性
- [x] 响应式设计（适配移动端和桌面端）
- [x] 暗色模式切换
- [x] 秒杀倒计时动画
- [x] 抢购按钮脉冲动画
- [x] 实时反馈抢购结果（成功/失败弹窗）
- [x] AI 对话组件（嵌入商品详情页）

---

## 🚀 快速开始

### 环境准备

确保已安装以下软件：

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Node.js 18+**
   ```bash
   node --version
   npm --version
   ```

3. **Redis**（必须安装并启动）
   - Windows: 下载 [Redis for Windows](https://github.com/microsoftarchive/redis/releases) 或使用 WSL
   - macOS: `brew install redis && brew services start redis`
   - Linux: `sudo apt install redis-server && sudo systemctl start redis`

4. **OpenAI API Key**
   - 注册 [OpenAI](https://platform.openai.com) 获取 API Key

### 安装步骤

#### 1. 克隆项目
```bash
cd ai-seckill
```

#### 2. 配置后端环境变量
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=your-secret-key-change-in-production
```

#### 3. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 4. 初始化商品数据和向量库
```bash
cd backend
python init_products.py
```

#### 5. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动，API 文档在 http://localhost:8000/docs

#### 6. 安装前端依赖
```bash
cd frontend
npm install
```

#### 7. 启动前端开发服务器
```bash
cd frontend
npm run dev
```

前端将在 http://localhost:5173 启动

#### 8. 访问系统
打开浏览器访问 http://localhost:5173

---

## 📋 API 接口文档

### 用户模块

#### 用户注册
- **路径**: `POST /api/users/register`
- **请求体**:
  ```json
  {
    "username": "testuser",
    "password": "123456",
    "nickname": "测试用户"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```

#### 用户登录
- **路径**: `POST /api/users/login`
- **请求体**:
  ```json
  {
    "username": "testuser",
    "password": "123456"
  }
  ```
- **响应**: 同上，返回 JWT token

#### 获取当前用户信息
- **路径**: `GET /api/users/me`
- **请求头**: `Authorization: Bearer <token>`
- **响应**:
  ```json
  {
    "id": 1,
    "username": "testuser",
    "nickname": "测试用户",
    "created_at": "2024-01-01T00:00:00"
  }
  ```

### 商品模块

#### 获取商品列表
- **路径**: `GET /api/products?search=&skip=0&limit=20`
- **响应**:
  ```json
  {
    "items": [
      {
        "id": 1,
        "name": "iPhone 16 Pro Max",
        "description": "Apple 最新旗舰手机...",
        "image_url": "https://...",
        "original_price": 9999.0,
        "category": "手机数码",
        "material": "钛金属边框",
        "specs": "{\"屏幕\":\"6.9英寸\"}",
        "created_at": "2024-01-01T00:00:00",
        "ai_welcome": ""
      }
    ],
    "total": 6
  }
  ```

#### 获取商品详情
- **路径**: `GET /api/products/{product_id}`
- **响应**: 包含 `ai_welcome` 字段（AI 助手欢迎语）

#### 添加商品
- **路径**: `POST /api/products`
- **请求头**: `Authorization: Bearer <token>`
- **请求体**:
  ```json
  {
    "name": "新商品",
    "description": "商品描述",
    "image_url": "https://...",
    "original_price": 1999.0,
    "category": "手机数码",
    "material": "材质信息",
    "specs": "{\"规格\":\"参数\"}"
  }
  ```

### AI 智能助手

#### 与 AI 助手对话
- **路径**: `POST /api/agent/chat`
- **请求体**:
  ```json
  {
    "message": "这个手机是什么材质的？",
    "product_id": 1
  }
  ```
- **响应**:
  ```json
  {
    "answer": "根据商品信息，iPhone 16 Pro Max 采用了钛金属边框和陶瓷盾玻璃面板...",
    "sources": [
      "工具: search_product_info | 输入: 这个手机是什么材质的？"
    ]
  }
  ```

### 秒杀模块

#### 创建秒杀活动
- **路径**: `POST /api/seckill/activities`
- **请求头**: `Authorization: Bearer <token>`
- **请求体**:
  ```json
  {
    "product_id": 1,
    "seckill_price": 6999.0,
    "total_stock": 100,
    "limit_per_user": 1,
    "start_time": "2024-12-01T10:00:00",
    "end_time": "2024-12-01T12:00:00"
  }
  ```

#### 获取秒杀活动列表
- **路径**: `GET /api/seckill/activities`
- **响应**: 包含活动状态、剩余库存（来自 Redis）

#### 获取秒杀活动详情
- **路径**: `GET /api/seckill/activities/{activity_id}`

#### 执行秒杀
- **路径**: `POST /api/seckill/{activity_id}/execute?quantity=1`
- **请求头**: `Authorization: Bearer <token>`
- **响应**:
  ```json
  {
    "success": true,
    "message": "🎉 抢购成功！订单正在处理中",
    "order_id": null
  }
  ```

### 订单模块

#### 获取订单列表
- **路径**: `GET /api/orders?skip=0&limit=20`
- **请求头**: `Authorization: Bearer <token>`

#### 模拟支付
- **路径**: `POST /api/orders/{order_id}/pay`
- **请求头**: `Authorization: Bearer <token>`

#### 取消订单
- **路径**: `POST /api/orders/{order_id}/cancel`
- **请求头**: `Authorization: Bearer <token>`

---

## 🔥 Redis 高并发设计专题

### 1. 缓存雪崩预防

**概念**：大量缓存数据在同一时间过期失效，导致所有请求直接打到数据库，可能造成数据库瞬间压力过大甚至崩溃。

**预防策略**：对缓存 TTL 添加随机值，避免大量 key 同时过期。

**代码位置**：`backend/app/redis_client.py` 中的 `set_cache_with_random_ttl` 方法

```python
async def set_cache_with_random_ttl(self, key, value, base_ttl=3600, extra_ttl_range=600):
    # 在基础 TTL 上增加 0~600 秒的随机偏移
    ttl = base_ttl + random.randint(0, extra_ttl_range)
    await self.pool.setex(key, ttl, serialized)
```

**设计意图**：假设有 1000 个商品缓存，基础 TTL 都是 3600 秒。如果不加随机值，它们会在同一时刻全部过期，导致数据库瞬间承受 1000 个并发查询。加上随机值后，过期时间分布在 3600~4200 秒之间，大大降低了同时过期的概率。

### 2. 缓存击穿预防

**概念**：某个热点 key 在缓存过期的瞬间，大量并发请求同时访问该 key，导致所有请求都穿透到数据库。

**预防策略**：使用互斥锁（SETNX），只允许一个请求去加载数据，其他请求等待后读取新缓存。

**代码位置**：`backend/app/redis_client.py` 中的 `get_or_refresh_cache` 方法

```python
# 使用 SET NX 尝试获取锁，防止缓存击穿
locked = await self.pool.set(lock_key, lock_value, nx=True, px=lock_timeout * 1000)
if locked:
    # 获取到锁的请求负责加载数据
    data = await fetch_func()
    await self.set_cache_with_random_ttl(key, data)
else:
    # 未获取到锁的请求等待后重试
    await asyncio.sleep(0.1)
    return await self.get_or_refresh_cache(key, fetch_func)
```

**设计意图**：当缓存过期时，第一个到达的请求通过 SETNX 获取互斥锁，然后去数据库加载数据并更新缓存。其他请求发现无法获取锁，就短暂等待（100ms）后重试，此时缓存已经被第一个请求更新，可以直接读取。这样保证了同一时刻只有一个请求访问数据库。

### 3. 缓存穿透预防

**概念**：查询一个不存在的数据，缓存和数据库都没有，导致每次请求都穿透到数据库。

**预防策略**：将空值也写入缓存，设置较短的过期时间（如 60 秒）。

**代码位置**：`backend/app/redis_client.py` 中的 `get_or_refresh_cache` 方法

```python
if data is not None:
    await self.set_cache_with_random_ttl(key, data)
else:
    # 将空值写入缓存，设置较短过期时间
    await self.pool.setex(key, 60, json.dumps(None))
```

**设计意图**：恶意攻击者可能不断请求不存在的商品 ID（如 -1、999999 等），如果没有空值缓存，每次请求都会查询数据库。通过缓存空值，后续相同请求直接返回缓存中的 null，保护数据库不被无效请求压垮。

### 4. 分布式锁

**场景一**：防止同一用户在同一秒杀活动中并发重复下单。

**场景二**：缓存击穿时的互斥锁，避免缓存重建并发。

**代码位置**：`backend/app/redis_client.py` 中的 `_DistributedLock` 类和 `acquire_lock`/`_safe_release_lock` 方法

```python
# 获取锁：SET lock_key unique_value NX PX 5000
async def acquire_lock(self, lock_key, lock_value, timeout_ms=5000):
    result = await self.pool.set(lock_key, lock_value, nx=True, px=timeout_ms)
    return result is not None

# 释放锁：使用 Lua 脚本确保原子性
async def _safe_release_lock(self, lock_key, lock_value):
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    await self.pool.eval(lua_script, 1, lock_key, lock_value)
```

**设计原理**：
1. **唯一值标识**：每个锁使用 UUID 作为唯一值，只有锁的持有者才能释放锁
2. **过期时间**：设置锁的过期时间（如 5 秒），防止因程序崩溃导致死锁
3. **原子释放**：使用 Lua 脚本先比较 value 再删除，避免因操作超时导致误删其他实例的锁

**使用示例**（秒杀模块）：
```python
async with redis_client.distributed_lock(user_lock_key, timeout_ms=5000):
    # 执行 Lua 脚本原子扣减
    result = await redis_conn.eval(lua_script, ...)
```

### 5. 秒杀 Lua 脚本原子性

**代码位置**：`backend/app/lua/seckill.lua`

```lua
-- 1. 检查库存是否充足
local stock = redis.call("GET", KEYS[1])
if stock < tonumber(ARGV[3]) then
    return {err = "库存不足"}
end

-- 2. 检查用户是否超过限购数量
local user_bought = redis.call("GET", KEYS[2])
if user_bought + tonumber(ARGV[3]) > tonumber(ARGV[4]) then
    return {err = "超过限购数量"}
end

-- 3. 扣减库存
redis.call("DECRBY", KEYS[1], tonumber(ARGV[3]))

-- 4. 记录用户已购数量
redis.call("INCRBY", KEYS[2], tonumber(ARGV[3]))
```

**原子性原理**：
- Redis 是单线程模型，Lua 脚本在执行期间不会被其他命令中断
- 脚本内的所有操作要么全部成功，要么全部失败，不存在并发竞态条件

**与传统方式的对比**：
| 方式 | 步骤 | 问题 |
|------|------|------|
| 传统先查后改 | 1. GET stock 2. 检查库存 3. DECR stock | 步骤 1 和 3 之间可能有其他请求修改了库存，导致超卖 |
| Lua 脚本 | 在脚本内一次性完成检查+扣减 | 所有操作在 Redis 服务端原子执行，无需分布式锁即可保证数据一致性 |

### 6. 消息队列异步订单处理

**流程**：
1. 秒杀成功 → 订单数据推入 Redis List（`lpush seckill:order_queue`）
2. 后台任务轮询 Redis List（`rpop seckill:order_queue`）
3. 消费订单数据，写入 SQLite 订单表
4. 消费失败时重新放回队列

**代码位置**：
- 生产者：`backend/app/api/seckill.py` 中的 `execute_seckill` 方法
- 消费者：`backend/app/tasks/order_consumer.py` 中的 `start_order_consumer` 函数

**设计意图**：
- 秒杀接口只需操作 Redis（内存操作），响应时间极短（毫秒级）
- 订单持久化由后台任务异步完成，不阻塞用户请求
- Redis List 作为缓冲队列，可以应对突发的高并发写入

---

## 🤖 LangChain Agent 与 RAG 设计

### Agent 架构

```
用户输入 → Agent Executor → LLM (GPT-4o-mini)
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
           search_product_info      get_seckill_status
           (RAG 检索工具)           (Redis 查询工具)
                    │                       │
                    ▼                       ▼
              ChromaDB 向量库           Redis 缓存
```

### 工具描述

1. **search_product_info**：根据用户问题从商品知识向量库中检索相关知识片段。使用 ChromaDB 进行语义相似度搜索，返回最相关的商品信息。

2. **get_seckill_status**：查询秒杀活动的实时状态，包括剩余库存、限购数量、活动时间等。数据直接来自 Redis 缓存，保证实时性。

### 向量库构建

**构建时机**：
- FastAPI 启动时自动构建（`main.py` 的 `lifespan` 事件）
- 手动运行 `python init_products.py`

**构建流程**：
1. 从 SQLite 读取所有商品
2. 为每个商品生成多个文档片段（基本信息、描述、材质、规格）
3. 使用 OpenAI Embedding 将文档转换为向量
4. 存入 ChromaDB 持久化存储

### 检索流程

1. 用户输入问题
2. Agent 决定调用 `search_product_info` 工具
3. 工具将用户问题转换为向量，在 ChromaDB 中进行相似度搜索
4. 返回最相关的 3 个文档片段
5. LLM 基于检索结果生成回答

---

## 💡 项目亮点总结

### 适合写入简历的描述

**项目名称**：AI 智能秒杀系统 (AI-Powered Seckill Agent System)

**技术栈**：Python, FastAPI, LangChain, Redis, React, Ant Design

**项目描述**：
- 设计并实现了一个融合 AI Agent 和高并发秒杀的电商平台，支持用户注册登录、商品浏览、秒杀抢购、订单管理等完整业务流程
- 基于 LangChain 构建 AI 智能客服 Agent，集成 RAG（检索增强生成）技术，通过 ChromaDB 向量库实现商品知识检索，结合 Redis 实时数据查询，为用户提供精准的商品咨询和秒杀状态查询服务
- 深度应用 Redis 解决高并发秒杀的核心挑战：使用 Lua 脚本保证库存扣减的原子性，防止超卖；实现分布式锁防止用户重复下单；采用缓存雪崩（随机 TTL）、击穿（互斥锁）、穿透（空值缓存）的完整预防策略；通过 Redis 消息队列异步持久化订单，提升系统吞吐量
- 前端使用 React 18 + Ant Design 5，支持暗色模式、秒杀倒计时动画、实时抢购反馈，提供现代流畅的用户体验

**技术亮点**：
- ✅ LangChain Agent + RAG 智能问答
- ✅ Redis Lua 脚本原子扣减库存
- ✅ 分布式锁 + 缓存三大策略
- ✅ 消息队列异步订单处理
- ✅ FastAPI + React 全栈架构
- ✅ JWT 认证 + 暗色模式

---

## 📁 项目目录结构

```
ai-seckill/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库引擎
│   │   ├── models.py            # ORM 模型
│   │   ├── schemas.py           # Pydantic 模型
│   │   ├── auth.py              # JWT 认证
│   │   ├── redis_client.py      # Redis 客户端
│   │   ├── api/
│   │   │   ├── users.py         # 用户接口
│   │   │   ├── products.py      # 商品接口
│   │   │   ├── seckill.py       # 秒杀接口
│   │   │   ├── orders.py        # 订单接口
│   │   │   └── agent.py         # AI 对话接口
│   │   ├── agent/
│   │   │   ├── agent_setup.py   # Agent 初始化
│   │   │   ├── tools.py         # 工具定义
│   │   │   └── rag.py           # RAG 检索
│   │   ├── tasks/
│   │   │   └── order_consumer.py # 订单消费任务
│   │   └── lua/
│   │       └── seckill.lua      # 秒杀 Lua 脚本
│   ├── .env.example
│   ├── requirements.txt
│   └── init_products.py
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # 入口文件
│   │   ├── App.jsx              # 主组件
│   │   ├── api/index.js         # API 封装
│   │   ├── pages/
│   │   │   ├── Login.jsx        # 登录页
│   │   │   ├── Register.jsx     # 注册页
│   │   │   ├── Home.jsx         # 首页
│   │   │   ├── ProductDetail.jsx # 商品详情
│   │   │   ├── SeckillList.jsx  # 秒杀列表
│   │   │   ├── SeckillDetail.jsx # 秒杀详情
│   │   │   └── Orders.jsx       # 订单页
│   │   ├── components/
│   │   │   ├── Header.jsx       # 导航栏
│   │   │   └── AIAssistant.jsx  # AI 对话组件
│   │   └── styles/global.css    # 全局样式
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 📝 许可证

本项目仅供学习和参考使用。
