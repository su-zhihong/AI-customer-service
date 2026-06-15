/**
 * 文件路径: frontend/src/pages/SeckillDetail.jsx
 * 秒杀活动详情页。
 * 展示活动详细信息、倒计时、抢购按钮，实时反馈抢购结果。
 */

import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Row, Col, Card, Typography, Tag, Spin, Button, Empty, Space,
  Descriptions, Image, Divider, Progress, Modal, Result,
} from 'antd'
import {
  ThunderboltOutlined, ArrowLeftOutlined, ShoppingCartOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { seckillApi } from '../api'
import AIAssistant from '../components/AIAssistant'

const { Title, Text } = Typography

/**
 * 倒计时组件
 */
function Countdown({ targetTime, onEnd, label }) {
  const [remaining, setRemaining] = useState('')

  useEffect(() => {
    const target = new Date(targetTime).getTime()

    const timer = setInterval(() => {
      const now = Date.now()
      const diff = target - now

      if (diff <= 0) {
        clearInterval(timer)
        setRemaining('00:00:00')
        onEnd?.()
        return
      }

      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)

      setRemaining(
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      )
    }, 1000)

    return () => clearInterval(timer)
  }, [targetTime, onEnd])

  return (
    <div className="text-center">
      <Text type="secondary" className="text-sm">{label}</Text>
      <div
        className="text-3xl font-mono font-bold mt-1"
        style={{ color: remaining === '00:00:00' ? '#ff4d4f' : '#ff4d4f' }}
      >
        {remaining || '00:00:00'}
      </div>
    </div>
  )
}

export default function SeckillDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [activity, setActivity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [resultModal, setResultModal] = useState({ open: false, success: false, message: '' })

  /** 加载活动详情 */
  const fetchActivity = useCallback(async () => {
    setLoading(true)
    try {
      const res = await seckillApi.getActivityDetail(id)
      setActivity(res)
    } catch (error) {
      console.error('加载活动详情失败:', error)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchActivity()
  }, [fetchActivity])

  /** 执行秒杀 */
  const handleSeckill = async () => {
    setExecuting(true)
    try {
      const res = await seckillApi.execute(id)
      setResultModal({
        open: true,
        success: res.success,
        message: res.message,
      })
      if (res.success) {
        // 刷新活动信息
        fetchActivity()
      }
    } catch (error) {
      setResultModal({
        open: true,
        success: false,
        message: error.detail || '秒杀失败，请重试',
      })
    } finally {
      setExecuting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spin size="large" />
      </div>
    )
  }

  if (!activity) {
    return (
      <Empty description="秒杀活动不存在" className="py-20">
        <Button type="primary" onClick={() => navigate('/seckill')}>
          返回列表
        </Button>
      </Empty>
    )
  }

  const stockPercent = activity.total_stock > 0
    ? Math.round((activity.remaining_stock / activity.total_stock) * 100)
    : 0

  return (
    <Row gutter={[32, 32]}>
      {/* 左侧：活动详情 */}
      <Col xs={24} lg={14}>
        <Card className="shadow-md">
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/seckill')}
            className="mb-4"
          >
            返回列表
          </Button>

          <Row gutter={[24, 24]}>
            {/* 商品图片 */}
            <Col xs={24} md={10}>
              <div className="relative">
                <Image
                  src={activity.product_image || 'https://picsum.photos/seed/default/400/400'}
                  alt={activity.product_name}
                  className="w-full rounded-lg"
                  fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
                />
                {/* 活动状态标签 */}
                <div className="absolute top-2 right-2">
                  {activity.status === 'in_progress' && (
                    <Tag color="red" className="text-base px-3 py-1 seckill-glow">
                      火热进行中
                    </Tag>
                  )}
                  {activity.status === 'not_started' && (
                    <Tag color="blue" className="text-base px-3 py-1">
                      即将开始
                    </Tag>
                  )}
                  {activity.status === 'ended' && (
                    <Tag className="text-base px-3 py-1">
                      已结束
                    </Tag>
                  )}
                </div>
              </div>
            </Col>

            {/* 活动信息 */}
            <Col xs={24} md={14}>
              <Title level={4}>{activity.product_name}</Title>

              <div className="flex items-baseline gap-3 mb-4">
                <Text type="danger" strong className="text-3xl">
                  ¥{activity.seckill_price}
                </Text>
                <Text delete type="secondary" className="text-lg">
                  ¥{activity.original_price}
                </Text>
                {activity.original_price > 0 && (
                  <Tag color="red">
                    省 ¥{(activity.original_price - activity.seckill_price).toFixed(2)}
                  </Tag>
                )}
              </div>

              <Divider />

              {/* 库存进度条 */}
              <div className="mb-4">
                <div className="flex justify-between mb-1">
                  <Text type="secondary">剩余库存</Text>
                  <Text strong>
                    {activity.remaining_stock} / {activity.total_stock}
                  </Text>
                </div>
                <Progress
                  percent={stockPercent}
                  status={stockPercent > 0 ? 'active' : 'exception'}
                  strokeColor={stockPercent > 20 ? '#ff4d4f' : '#faad14'}
                  size="small"
                />
              </div>

              {/* 限购信息 */}
              <Descriptions column={1} size="small" className="mb-4">
                <Descriptions.Item label="每人限购">
                  {activity.limit_per_user} 件
                </Descriptions.Item>
                <Descriptions.Item label="开始时间">
                  {new Date(activity.start_time).toLocaleString('zh-CN')}
                </Descriptions.Item>
                <Descriptions.Item label="结束时间">
                  {new Date(activity.end_time).toLocaleString('zh-CN')}
                </Descriptions.Item>
              </Descriptions>

              {/* 倒计时 */}
              {activity.status === 'not_started' && (
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4">
                  <Countdown
                    targetTime={activity.start_time}
                    label="距开始"
                    onEnd={fetchActivity}
                  />
                </div>
              )}

              {activity.status === 'in_progress' && (
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-4">
                  <Countdown
                    targetTime={activity.end_time}
                    label="距结束"
                    onEnd={fetchActivity}
                  />
                </div>
              )}

              {/* 抢购按钮 */}
              <Button
                type="primary"
                size="large"
                block
                className={activity.status === 'in_progress' ? 'seckill-btn-pulse' : ''}
                style={{ height: 52, fontSize: 18 }}
                icon={<ThunderboltOutlined />}
                disabled={activity.status !== 'in_progress'}
                loading={executing}
                onClick={handleSeckill}
              >
                {activity.status === 'not_started'
                  ? '即将开始'
                  : activity.status === 'in_progress'
                  ? '⚡ 立即抢购'
                  : '已结束'}
              </Button>
            </Col>
          </Row>
        </Card>
      </Col>

      {/* 右侧：AI 智能助手 */}
      <Col xs={24} lg={10}>
        <AIAssistant productId={activity.product_id} />
      </Col>

      {/* 秒杀结果弹窗 */}
      <Modal
        open={resultModal.open}
        footer={null}
        closable={false}
        centered
        width={400}
      >
        <Result
          status={resultModal.success ? 'success' : 'error'}
          title={resultModal.success ? '🎉 抢购成功！' : '😅 抢购失败'}
          subTitle={resultModal.message}
          extra={[
            <Button
              key="close"
              type={resultModal.success ? 'primary' : 'default'}
              onClick={() => setResultModal({ open: false, success: false, message: '' })}
            >
              {resultModal.success ? '查看订单' : '知道了'}
            </Button>,
            resultModal.success && (
              <Button key="orders" onClick={() => navigate('/orders')}>
                去订单页
              </Button>
            ),
          ]}
        />
      </Modal>
    </Row>
  )
}
