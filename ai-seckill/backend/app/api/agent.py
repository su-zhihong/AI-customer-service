"""
文件路径: backend/app/api/agent.py
AI Agent 对话 API 路由。
提供与 AI 智能客服助手的对话接口。
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas import AgentChatRequest, AgentChatResponse
from app.agent.agent_setup import chat_with_agent as agent_chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["AI 智能助手"])


@router.post("/chat", response_model=AgentChatResponse, summary="与 AI 助手对话")
async def chat_with_agent(req: AgentChatRequest):
    """
    与 AI 智能客服助手对话。
    
    用户发送消息，Agent 根据问题内容自动选择工具：
    - 商品相关问题：调用 search_product_info 工具（RAG 检索）
    - 秒杀状态问题：调用 get_seckill_status 工具（Redis 实时数据）
    - 综合问题：可能同时调用多个工具
    
    返回 Agent 的最终回答和引用来源。
    """
    try:
        # 获取 Agent 执行器
        agent_executor = get_agent()

        # 构建用户输入，如果有关联商品 ID 则附带商品信息
        user_input = req.message
        if req.product_id:
            user_input = f"[商品ID: {req.product_id}] {req.message}"

        # 执行 Agent
        # 使用异步调用，Agent 会自动决定是否调用工具
        response = await agent_executor.ainvoke({
            "input": user_input,
        })

        answer = response.get("output", "抱歉，我暂时无法回答这个问题。")

        # 提取中间步骤中的工具调用结果作为来源
        sources = []
        intermediate_steps = response.get("intermediate_steps", [])
        for step in intermediate_steps:
            if hasattr(step[0], "tool"):
                tool_name = step[0].tool
                tool_input = str(step[0].tool_input)
                tool_output = str(step[1])[:200] if step[1] else ""
                sources.append(f"工具: {tool_name} | 输入: {tool_input}")

        return AgentChatResponse(
            answer=answer,
            sources=sources,
        )

    except Exception as e:
        logger.error(f"Agent 对话失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI 助手暂时无法响应，请稍后重试。错误: {str(e)}",
        )
