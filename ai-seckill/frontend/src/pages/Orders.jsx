/**
 * 文件路径: frontend/src/pages/Orders.jsx
 * 我的订单页面。
 * 展示当前用户的订单列表，支持模拟支付和取消订单。
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table, Card, Typography, Tag, Button, Space, Empty, Spin,
  message, Modal, Image, Statistic, Row, Col,
} from 'antd'
import {
  ShoppingCartOutlined, PayCircleOutlined, CloseCircleOutlined,
  ThunderboltOutlined, CheckCircleOutlined,
} from '@ant-design/icons'
import { orderApi } from '../api'

const { Title, Text } = Typography

/** 订单状态映射 */
const statusMap = {
  pending: { color: 'processing', text: '待支付' },
  paid: { color: 'success', text: '已支付' },
  cancelled: { color: 'default', text: '已取消' },
}

export default function Orders() {
  const navigate = useNavigate()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)

  /** 加载订单列表 */
  const fetchOrders = async () => {
    setLoading(true)
    try {
      const res = await orderApi.getList({ limit: 50 })
      setOrders(res.items || [])
    } catch (error) {
      console.error('加载订单失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
  }, [])

  /** 模拟支付 */
  const handlePay = async (orderId) => {
    setActionLoading(orderId)
    try {
      await orderApi.pay(orderId)
      message.success('支付成功！')
      fetchOrders()
    } catch (error) {
      message.error(error.detail || '支付失败')
    } finally {
      setActionLoading(null)
    }
  }

  /** 取消订单 */
  const handleCancel = (orderId) => {
    Modal.confirm({
      title: '确认取消订单？',
      content: '取消后无法恢复',
      okText: '确认取消',
      cancelText: '再想想',
      okButtonProps: { danger: true },
      onOk: async () => {
        setActionLoading(orderId)
        try {
          await orderApi.cancel(orderId)
          message.success('订单已取消')
          fetchOrders()
        } catch (error) {
          message.error(error.detail || '取消失败')
        } finally {
          setActionLoading(null)
        }
      },
    })
  }

  /** 表格列定义 */
  const columns = [
    {
      title: '商品信息',
      dataIndex: 'product_name',
      key: 'product',
      render: (name, record) => (
        <div className="flex items-center gap-3">
          <Image
            src={record.product_image || 'https://picsum.photos/seed/default/80/80'}
            alt={name}
            width={60}
            height={60}
            className="rounded-lg object-cover"
            fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            preview={false}
          />
          <div>
            <Text strong>{name}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              x{record.quantity}
            </Text>
          </div>
        </div>
      ),
    },
    {
      title: '金额',
      dataIndex: 'total_price',
      key: 'price',
      width: 120,
      render: (price) => (
        <Text type="danger" strong>
          ¥{price.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const info = statusMap[status] || { color: 'default', text: status }
        return <Tag color={info.color}>{info.text}</Tag>
      },
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'time',
      width: 180,
      render: (time) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {new Date(time).toLocaleString('zh-CN')}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          {record.status === 'pending' && (
            <>
              <Button
                type="primary"
                size="small"
                icon={<PayCircleOutlined />}
                loading={actionLoading === record.id}
                onClick={() => handlePay(record.id)}
              >
                支付
              </Button>
              <Button
                size="small"
                icon={<CloseCircleOutlined />}
                loading={actionLoading === record.id}
                onClick={() => handleCancel(record.id)}
              >
                取消
              </Button>
            </>
          )}
          {record.status === 'paid' && (
            <Tag icon={<CheckCircleOutlined />} color="success">
              已支付
            </Tag>
          )}
          {record.status === 'cancelled' && (
            <Tag color="default">已取消</Tag>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div className="mb-6">
        <Title level={3}>
          <ShoppingCartOutlined style={{ color: '#ff4d4f' }} /> 我的订单
        </Title>
        <Text type="secondary">查看和管理您的秒杀订单</Text>
      </div>

      {/* 订单统计 */}
      {orders.length > 0 && (
        <Row gutter={16} className="mb-6">
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="总订单"
                value={orders.length}
                prefix={<ShoppingCartOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="待支付"
                value={orders.filter((o) => o.status === 'pending').length}
                valueStyle={{ color: '#faad14' }}
                prefix={<PayCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="已支付"
                value={orders.filter((o) => o.status === 'paid').length}
                valueStyle={{ color: '#52c41a' }}
                prefix={<CheckCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="已取消"
                value={orders.filter((o) => o.status === 'cancelled').length}
                valueStyle={{ color: '#999' }}
                prefix={<CloseCircleOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 订单列表 */}
      <Spin spinning={loading}>
        <Card className="shadow-md">
          {orders.length === 0 ? (
            <Empty
              description="暂无订单"
              className="py-16"
            >
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={() => navigate('/seckill')}
              >
                去秒杀
              </Button>
            </Empty>
          ) : (
            <Table
              dataSource={orders}
              columns={columns}
              rowKey="id"
              pagination={false}
              scroll={{ x: 700 }}
            />
          )}
        </Card>
      </Spin>
    </div>
  )
}
