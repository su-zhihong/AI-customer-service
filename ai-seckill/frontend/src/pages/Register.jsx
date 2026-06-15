/**
 * 文件路径: frontend/src/pages/Register.jsx
 * 注册页面。
 * 用户填写信息进行注册，成功后自动登录并跳转到首页。
 */

import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined, RobotOutlined, SmileOutlined } from '@ant-design/icons'
import { userApi } from '../api'

const { Title, Text } = Typography

export default function Register() {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = React.useState(false)

  /** 处理注册提交 */
  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      const res = await userApi.register(values)
      // 保存 token
      localStorage.setItem('token', res.access_token)

      // 获取用户信息
      const userRes = await userApi.getMe()
      localStorage.setItem('user', JSON.stringify(userRes))

      message.success('注册成功！欢迎加入！')
      navigate('/')
    } catch (error) {
      message.error(error.detail || '注册失败，请重试')
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
            创建账号
          </Title>
          <Text type="secondary">注册 AI 智能秒杀系统</Text>
        </div>

        {/* 注册表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="nickname"
            rules={[{ required: false }]}
          >
            <Input
              prefix={<SmileOutlined />}
              placeholder="昵称（选填）"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
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
              注册
            </Button>
          </Form.Item>

          <div className="text-center">
            <Space>
              <Text type="secondary">已有账号？</Text>
              <Link to="/login">立即登录</Link>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}
