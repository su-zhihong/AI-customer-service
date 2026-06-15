"""
文件路径: backend/app/agent/tools.py
工具定义模块。
定义 AI Agent 可以调用的工具函数，使用 OpenAI Function Calling 格式。
"""

import json
import logging
from typing import Any

from app.agent.rag import search_product_info, format_search_results
from app.redis_client import seckill_redis

logger = logging.getLogger(__name__)


# ==================== OpenAI Function Calling 工具定义 ====================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_product_info",
            "description": "根据用户的问题检索商品知识库中的相关信息。当用户询问商品详情、规格、材质、价格、优惠规则等问题时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户关于商品的问题，例如：'这个手机是什么材质的？'、'有什么优惠规则？'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_seckill_status",
            "description": "查询秒杀活动的当前状态，包括剩余库存、限购数量、活动时间等。当用户询问秒杀活动是否开始、库存情况时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "integer",
                        "description": "秒杀活动 ID"
                    }
                },
                "required": ["activity_id"]
            }
        }
    }
]


async def execute_tool(name: str, args: dict[str, Any]) -> str:
    """
    执行指定的工具函数。
    
    Args:
        name: 工具名称
        args: 工具参数
    
    Returns:
        工具执行结果的字符串表示
    """
    if name == "search_product_info":
        query = args.get("query", "")
        docs = await search_product_info(query)
        return format_search_results(docs)

    elif name == "get_seckill_status":
        activity_id = args.get("activity_id", 0)
        info = await seckill_redis.get_activity_info(activity_id)
        if not info:
            return f"未找到秒杀活动（ID: {activity_id}）的信息，活动可能不存在或已结束。"

        remaining = await seckill_redis.get_remaining_stock(activity_id)
        result = (
            f"秒杀活动 ID: {activity_id}\n"
            f"秒杀价格: {info.get('seckill_price', '未知')} 元\n"
            f"剩余库存: {remaining} 件\n"
            f"每人限购: {info.get('limit_per_user', '未知')} 件\n"
            f"开始时间: {info.get('start_time', '未知')}\n"
            f"结束时间: {info.get('end_time', '未知')}\n"
        )
        return result

    else:
        return f"未知工具: {name}"