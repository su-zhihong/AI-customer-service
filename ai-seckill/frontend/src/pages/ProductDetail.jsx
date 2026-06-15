/**
 * 文件路径: frontend/src/pages/ProductDetail.jsx
 * 商品详情页。
 * 展示商品详细信息，右侧嵌入 AI 客服对话组件。
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Row, Col, Card, Typography, Tag, Spin, Descriptions, Image,
  Button, Divider, Space, Empty,
} from 'antd'
import {
  ShoppingCartOutlined, ThunderboltOutlined, ArrowLeftOutlined,
  RobotOutlined, TagOutlined,
} from '@ant-design/icons'
import { productApi } from '../api'
import AIAssistant from '../components/AIAssistant'

const { Title, Text, Paragraph } = Typography

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)

  /** 加载商品详情 */
  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true)
      try {
        const res = await productApi.getDetail(id)
        setProduct(res)
      } catch (error) {
        console.error('加载商品详情失败:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchProduct()
  }, [id])

  /** 解析规格参数 JSON */
  const parseSpecs = (specsStr) => {
    try {
      return JSON.parse(specsStr)
    } catch {
      return null
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spin size="large" />
      </div>
    )
  }

  if (!product) {
    return (
      <Empty description="商品不存在" className="py-20">
        <Button type="primary" onClick={() => navigate('/')}>
          返回首页
        </Button>
      </Empty>
    )
  }

  const specs = parseSpecs(product.specs)

  return (
    <Row gutter={[32, 32]}>
      {/* 左侧：商品信息 */}
      <Col xs={24} lg={14}>
        <Card className="shadow-md">
          {/* 返回按钮 */}
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/')}
            className="mb-4"
          >
            返回
          </Button>

          <Row gutter={[24, 24]}>
            {/* 商品图片 */}
            <Col xs={24} md={10}>
              <Image
                src={product.image_url || 'https://picsum.photos/seed/default/400/400'}
                alt={product.name}
                className="w-full rounded-lg"
                fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
              />
            </Col>

            {/* 商品基本信息 */}
            <Col xs={24} md={14}>
              <Title level={4}>{product.name}</Title>

              <Space className="mb-3">
                {product.category && <Tag color="blue">{product.category}</Tag>}
                <Tag icon={<TagOutlined />} color="red">
                  ¥{product.original_price}
                </Tag>
              </Space>

              {product.material && (
                <Paragraph className="mb-2">
                  <Text strong>材质：</Text>
                  <Text>{product.material}</Text>
                </Paragraph>
              )}

              <Paragraph className="text-gray-500 dark:text-gray-400">
                {product.description || '暂无描述'}
              </Paragraph>

              <Divider />

              {/* 操作按钮 */}
              <Space>
                <Button
                  type="primary"
                  icon={<ThunderboltOutlined />}
                  size="large"
                  onClick={() => navigate('/seckill')}
                >
                  查看秒杀活动
                </Button>
                <Button
                  icon={<ShoppingCartOutlined />}
                  size="large"
                  onClick={() => navigate('/orders')}
                >
                  我的订单
                </Button>
              </Space>
            </Col>
          </Row>

          {/* 规格参数 */}
          {specs && (
            <>
              <Divider />
              <Title level={5}>规格参数</Title>
              <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
                {Object.entries(specs).map(([key, value]) => (
                  <Descriptions.Item key={key} label={key}>
                    {value}
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </>
          )}

          {/* AI 助手欢迎语 */}
          {product.ai_welcome && (
            <>
              <Divider />
              <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                <Space>
                  <RobotOutlined style={{ color: '#ff4d4f', fontSize: 20 }} />
                  <Text>{product.ai_welcome}</Text>
                </Space>
              </div>
            </>
          )}
        </Card>
      </Col>

      {/* 右侧：AI 智能助手 */}
      <Col xs={24} lg={10}>
        <AIAssistant productId={product.id} />
      </Col>
    </Row>
  )
}
