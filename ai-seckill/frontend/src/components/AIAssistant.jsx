/**
 * 文件路径: frontend/src/components/AIAssistant.jsx
 * AI 智能客服对话组件。
 * 嵌入在商品详情页，用户可与 AI 助手对话，询问商品信息和秒杀状态。
 */

import React, { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, Typography, Space, Spin, Tag, Empty, Avatar, Divider } from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  BulbOutlined,
} from '@ant-design/icons'
import { agentApi } from '../api'

const { Text, Paragraph } = Typography

/**
 * AI 助手对话组件
 * @param {number} productId - 关联的商品 ID（可选）
 */
export default function AIAssistant({ productId }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '你好！我是智能助手小秒 🤖，有什么关于商品或秒杀的问题可以问我哦！',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  /** 自动滚动到最新消息 */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  /** 发送消息 */
  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')

    // 添加用户消息
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      // 调用后端 Agent 接口
      const res = await agentApi.chat({
        message: userMessage,
        product_id: productId || undefined,
      })

      // 添加 AI 回复
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          sources: res.sources || [],
        },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '抱歉，我暂时无法回答这个问题，请稍后重试。',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  /** 按回车发送 */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Card
      title={
        <Space>
          <RobotOutlined style={{ color: '#ff4d4f', fontSize: 20 }} />
          <Text strong>AI 智能助手</Text>
          <Tag color="red" style={{ fontSize: 11 }}>
            小秒
          </Tag>
        </Space>
      }
      className="w-full shadow-md"
      styles={{
        body: { padding: 0 },
      }}
    >
      {/* 消息列表 */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in-up`}
          >
            <div
              className={`flex gap-2 max-w-[85%] ${
                msg.role === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              {/* 头像 */}
              <Avatar
                icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{
                  backgroundColor: msg.role === 'user' ? '#ff4d4f' : '#1677ff',
                  flexShrink: 0,
                }}
              />

              {/* 消息内容 */}
              <div>
                <div
                  className={`rounded-2xl px-4 py-2.5 ${
                    msg.role === 'user'
                      ? 'bg-red-500 text-white rounded-tr-sm'
                      : 'bg-gray-100 dark:bg-gray-800 rounded-tl-sm'
                  }`}
                >
                  <Paragraph className="mb-0 whitespace-pre-wrap text-sm">
                    {msg.content}
                  </Paragraph>
                </div>

                {/* 信息来源 */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-1">
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      <BulbOutlined /> 信息来源：
                    </Text>
                    {msg.sources.map((source, i) => (
                      <Tag key={i} color="blue" style={{ fontSize: 10, marginTop: 2 }}>
                        {source}
                      </Tag>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* 加载中动画 */}
        {loading && (
          <div className="flex justify-start">
            <Space>
              <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#1677ff' }} />
              <Spin size="small" />
              <Text type="secondary" style={{ fontSize: 12 }}>
                思考中...
              </Text>
            </Space>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <Divider className="my-0" />

      {/* 输入区域 */}
      <div className="p-3 flex gap-2">
        <Input.TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入您的问题..."
          autoSize={{ minRows: 1, maxRows: 3 }}
          disabled={loading}
          className="flex-1"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          disabled={!input.trim()}
          className="self-end"
        />
      </div>
    </Card>
  )
}
