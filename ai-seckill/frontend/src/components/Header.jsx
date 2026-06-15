/**
 * 文件路径: frontend/src/components/Header.jsx
 * 顶部导航栏组件。
 * 包含 Logo、导航菜单、主题切换、用户信息。
 */

import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Space, Dropdown, Avatar, Switch, Typography } from 'antd'
import {
  HomeOutlined,
  ThunderboltOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
  SunOutlined,
  MoonOutlined,
  RobotOutlined,
} from '@ant-design/icons'

const { Text } = Typography

export default function Header({ isDarkMode, setIsDarkMode }) {
  const navigate = useNavigate()
  const location = useLocation()
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  /** 退出登录 */
  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  /** 导航菜单项 */
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/seckill',
      icon: <ThunderboltOutlined />,
      label: <Link to="/seckill">秒杀活动</Link>,
    },
    {
      key: '/orders',
      icon: <ShoppingCartOutlined />,
      label: <Link to="/orders">我的订单</Link>,
    },
  ]

  /** 用户下拉菜单 */
  const userMenuItems = [
    {
      key: 'user-info',
      label: (
        <div className="px-2 py-1">
          <Text strong>{user.nickname || user.username}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            @{user.username}
          </Text>
        </div>
      ),
      disabled: true,
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <Layout.Header
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6"
      style={{
        background: isDarkMode ? '#141414' : '#fff',
        borderBottom: `1px solid ${isDarkMode ? '#303030' : '#f0f0f0'}`,
        height: 64,
      }}
    >
      {/* Logo 和标题 */}
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2 no-underline">
          <RobotOutlined style={{ fontSize: 28, color: '#ff4d4f' }} />
          <span
            className="text-lg font-bold"
            style={{ color: isDarkMode ? '#fff' : '#000' }}
          >
            AI 智能秒杀
          </span>
        </Link>
      </div>

      {/* 导航菜单 */}
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{
          flex: 1,
          minWidth: 300,
          border: 'none',
          background: 'transparent',
          justifyContent: 'center',
        }}
      />

      {/* 右侧操作区 */}
      <Space size="middle">
        {/* 暗色模式切换 */}
        <Switch
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<SunOutlined />}
          checked={isDarkMode}
          onChange={setIsDarkMode}
        />

        {/* 用户相关 */}
        {token ? (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Avatar
              icon={<UserOutlined />}
              style={{ backgroundColor: '#ff4d4f', cursor: 'pointer' }}
            />
          </Dropdown>
        ) : (
          <Space>
            <Button type="primary" ghost onClick={() => navigate('/login')}>
              <LoginOutlined /> 登录
            </Button>
            <Button type="primary" onClick={() => navigate('/register')}>
              注册
            </Button>
          </Space>
        )}
      </Space>
    </Layout.Header>
  )
}
