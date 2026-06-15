"""
文件路径: backend/app/agent/agent_setup.py
AI Agent 初始化模块。
使用 OpenAI Function Calling 直接实现智能问答。
"""

import json
import logging
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.agent.tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

# 全局 OpenAI 客户端
_client: Optional[AsyncOpenAI] = None

# 系统提示词
SYSTEM_PROMPT = """
你是一个专业的电商智能客服助手，名叫"小秒"。你服务于一个电商秒杀平台。

## 你的能力
1. **商品知识问答**：你可以使用 search_product_info 工具检索商品知识库。
2. **秒杀状态查询**：你可以使用 get_seckill_status 工具查询秒杀活动的实时状态。

## 回答规范
1. 用中文简洁、准确回答。
2. 需要信息时调用对应工具，基于工具返回结果回答。
3. 如果信息不足，如实告知用户。
"""


def get_client() -> AsyncOpenAI:
    """获取 OpenAI 客户端实例"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
    return _client


async def chat_with_agent(user_message: str) -> str:
    """
    与 AI Agent 对话。
    使用 OpenAI Function Calling 实现工具调用。
    """
    client = get_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # 最多允许 5 轮工具调用
    for _ in range(5):
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            # 没有工具调用，直接返回
            return message.content or "抱歉，我暂时无法回答这个问题。"

        # 处理工具调用
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in message.tool_calls
            ]
        })

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
                result = await execute_tool(tool_name, tool_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
            except Exception as e:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"执行出错: {str(e)}",
                })

    # 最终回复
    final = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
    )
    return final.choices[0].message.content or "抱歉，处理超时。"