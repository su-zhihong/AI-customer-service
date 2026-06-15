/**
 * 文件路径: frontend/src/pages/Home.jsx
 * 首页（商品列表页）。
 * 展示所有商品卡片，支持搜索，点击进入商品详情。
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Row, Col, Card, Input, Typography, Spin, Tag, Empty, Image } from 'antd'
import { SearchOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { productApi } from '../api'

const { Title, Text, Paragraph } = Typography
const { Meta } = Card

export default function Home() {
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  /** 加载商品列表 */
  const fetchProducts = async (keyword = '') => {
    setLoading(true)
    try {
      const params = { search: keyword, limit: 50 }
      const res = await productApi.getList(params)
      setProducts(res.items || [])
    } catch (error) {
      console.error('加载商品失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  /** 搜索防抖 */
  const handleSearch = (value) => {
    setSearch(value)
    fetchProducts(value)
  }

  return (
    <div>
      {/* 页面标题和搜索 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Title level={3} className="mb-1">
            <ThunderboltOutlined style={{ color: '#ff4d4f' }} /> 商品广场
          </Title>
          <Text type="secondary">浏览商品，了解详情，参与秒杀</Text>
        </div>
        <Input.Search
          placeholder="搜索商品..."
          allowClear
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
        />
      </div>

      {/* 商品列表 */}
      <Spin spinning={loading}>
        {products.length === 0 ? (
          <Empty description="暂无商品" className="py-20" />
        ) : (
          <Row gutter={[24, 24]}>
            {products.map((product) => (
              <Col xs={24} sm={12} md={8} lg={6} key={product.id}>
                <Card
                  hoverable
                  className="h-full transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
                  cover={
                    <div className="h-48 overflow-hidden bg-gray-100 dark:bg-gray-800">
                      <Image
                        alt={product.name}
                        src={product.image_url || 'https://picsum.photos/seed/default/400/400'}
                        className="w-full h-full object-cover"
                        preview={false}
                        fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
                      />
                    </div>
                  }
                  onClick={() => navigate(`/products/${product.id}`)}
                >
                  <Meta
                    title={
                      <div className="flex items-center justify-between">
                        <Text ellipsis className="text-base font-semibold">
                          {product.name}
                        </Text>
                        <Tag color="red">¥{product.original_price}</Tag>
                      </div>
                    }
                    description={
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        className="text-gray-500 dark:text-gray-400 mb-0"
                      >
                        {product.description || '暂无描述'}
                      </Paragraph>
                    }
                  />
                  {product.category && (
                    <Tag className="mt-2" color="blue">
                      {product.category}
                    </Tag>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Spin>
    </div>
  )
}
