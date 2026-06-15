/**
 * 文件路径: frontend/src/pages/SeckillList.jsx
 * 秒杀活动列表页。
 * 展示所有秒杀活动，显示倒计时，根据状态控制抢购按钮。
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Row, Col, Card, Typography, Tag, Spin, Button, Empty, Space } from 'antd'
import { ThunderboltOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { seckillApi } from '../api'

const { Title, Text } = Typography

/**
 * 倒计时组件
 */
function Countdown({ targetTime, onEnd }) {
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
    <Text
      className="font-mono text-lg"
      style={{ color: remaining === '00:00:00' ? '#ff4d4f' : '#52c41a' }}
    >
      <ClockCircleOutlined className="mr-1" />
      {remaining || '00:00:00'}
    </Text>
  )
}

export default function SeckillList() {
  const navigate = useNavigate()
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  /** 加载秒杀活动列表 */
  const fetchActivities = async () => {
    setLoading(true)
    try {
      const res = await seckillApi.getActivities()
      setActivities(res.items || [])
    } catch (error) {
      console.error('加载秒杀活动失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActivities()
  }, [])

  /** 获取活动状态标签 */
  const getStatusTag = (status) => {
    const statusMap = {
      not_started: { color: 'blue', text: '未开始' },
      in_progress: { color: 'red', text: '进行中' },
      ended: { color: 'default', text: '已结束' },
    }
    const info = statusMap[status] || { color: 'default', text: '未知' }
    return <Tag color={info.color}>{info.text}</Tag>
  }

  return (
    <div>
      <div className="mb-6">
        <Title level={3}>
          <ThunderboltOutlined style={{ color: '#ff4d4f' }} /> 秒杀活动
        </Title>
        <Text type="secondary">限时抢购，手慢无！</Text>
      </div>

      <Spin spinning={loading}>
        {activities.length === 0 ? (
          <Empty description="暂无秒杀活动" className="py-20" />
        ) : (
          <Row gutter={[24, 24]}>
            {activities.map((activity) => (
              <Col xs={24} sm={12} lg={8} key={activity.id}>
                <Card
                  hoverable
                  className={`h-full transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                    activity.status === 'in_progress' ? 'seckill-glow' : ''
                  }`}
                  cover={
                    <div className="h-48 overflow-hidden bg-gray-100 dark:bg-gray-800 relative">
                      <img
                        alt={activity.product_name}
                        src={activity.product_image || 'https://picsum.photos/seed/default/400/400'}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.src = 'https://picsum.photos/seed/default/400/400'
                        }}
                      />
                      {/* 状态覆盖层 */}
                      <div className="absolute top-2 right-2">
                        {getStatusTag(activity.status)}
                      </div>
                      {/* 秒杀价格标签 */}
                      <div className="absolute bottom-2 left-2">
                        <Tag color="red" className="text-base font-bold px-3 py-1">
                          ¥{activity.seckill_price}
                        </Tag>
                      </div>
                    </div>
                  }
                  onClick={() => navigate(`/seckill/${activity.id}`)}
                >
                  <div className="space-y-3">
                    {/* 商品名称 */}
                    <Text strong ellipsis className="text-base block">
                      {activity.product_name}
                    </Text>

                    {/* 价格信息 */}
                    <div className="flex items-center gap-2">
                      <Text type="danger" strong className="text-xl">
                        ¥{activity.seckill_price}
                      </Text>
                      <Text delete type="secondary">
                        ¥{activity.original_price}
                      </Text>
                    </div>

                    {/* 库存信息 */}
                    <div className="flex justify-between text-sm">
                      <Text type="secondary">
                        剩余 <Text strong>{activity.remaining_stock}</Text> / {activity.total_stock}
                      </Text>
                      <Text type="secondary">
                        限购 {activity.limit_per_user} 件/人
                      </Text>
                    </div>

                    {/* 倒计时 */}
                    {activity.status === 'not_started' && (
                      <div className="text-center py-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <Text type="secondary" className="text-xs">距开始</Text>
                        <br />
                        <Countdown targetTime={activity.start_time} onEnd={fetchActivities} />
                      </div>
                    )}

                    {activity.status === 'in_progress' && (
                      <div className="text-center py-2 bg-red-50 dark:bg-red-900/20 rounded">
                        <Text type="secondary" className="text-xs">距结束</Text>
                        <br />
                        <Countdown targetTime={activity.end_time} onEnd={fetchActivities} />
                      </div>
                    )}

                    {/* 操作按钮 */}
                    <Button
                      type="primary"
                      block
                      size="large"
                      disabled={activity.status !== 'in_progress'}
                      className={
                        activity.status === 'in_progress' ? 'seckill-btn-pulse' : ''
                      }
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/seckill/${activity.id}`)
                      }}
                    >
                      {activity.status === 'not_started'
                        ? '即将开始'
                        : activity.status === 'in_progress'
                        ? '立即抢购'
                        : '已结束'}
                    </Button>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Spin>
    </div>
  )
}
