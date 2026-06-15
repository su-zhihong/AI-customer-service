/**
 * 文件路径: frontend/src/pages/Login.jsx
 * 登录页面。
 * 用户输入用户名和密码进行登录，成功后跳转到首页。
 */

import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined, RobotOutlined } from '@ant-design/icons'
import { userApi } from '../api'

const { Title, Text } = Typography

export default function Login() {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = React.useState(false)

  /** 处理登录提交 */
  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      const res = await userApi.login(values)
      // 保存 token 到 localStorage
      localStorage.setItem('token', res.access_token)

      // 获取用户信息
      const userRes = await userApi.getMe()
      localStorage.setItem('user', JSON.stringify(userRes))

      message.success('登录成功！')
      navigate('/')
    } catch (error) {
      message.error(error.detail || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card
        className="w-full max-w-md shadow-lg"
        styles={{
          body: { padding: '40px 32px' },
        }}
      >
        {/* 标题区域 */}
        <div className="text-center mb-8">
          <RobotOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />
          <Title level={3} className="mt-4 mb-1">
            欢迎回来
          </Title>
          <Text type="secondary">登录 AI 智能秒杀系统</Text>
        </div>

        {/* 登录表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item className="mb-4">
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{ height: 44 }}
            >
              登录
            </Button>
          </Form.Item>

          <div className="text-center">
            <Space>
              <Text type="secondary">还没有账号？</Text>
              <Link to="/register">立即注册</Link>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}
