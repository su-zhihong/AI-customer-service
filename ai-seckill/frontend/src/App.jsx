/**
 * 文件路径: frontend/src/App.jsx
 * 应用主组件。
 * 定义路由结构，包含 Header 和页面路由。
 */

import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'

import Header from './components/Header'
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import ProductDetail from './pages/ProductDetail'
import SeckillList from './pages/SeckillList'
import SeckillDetail from './pages/SeckillDetail'
import Orders from './pages/Orders'

const { Content } = Layout

/**
 * 需要登录才能访问的路由包装组件
 */
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

/**
 * 应用主组件
 */
export default function App({ isDarkMode, setIsDarkMode }) {
  return (
    <Layout className="min-h-screen">
      <Header isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />
      <Content style={{ padding: '0 24px', marginTop: 64 }}>
        <div className="max-w-7xl mx-auto py-6">
          <Routes>
            {/* 公开路由 */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Home />} />
            <Route path="/products/:id" element={<ProductDetail />} />

            {/* 需要登录的路由 */}
            <Route
              path="/seckill"
              element={
                <ProtectedRoute>
                  <SeckillList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/seckill/:id"
              element={
                <ProtectedRoute>
                  <SeckillDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <Orders />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </Content>
    </Layout>
  )
}
