/**
 * 文件路径: frontend/src/api/index.js
 * API 请求封装模块。
 * 使用 Axios 与后端通信，自动处理 JWT token 注入。
 */

import axios from 'axios'

// 创建 Axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动注入 JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // token 过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

// ==================== 用户模块 API ====================

export const userApi = {
  /** 用户注册 */
  register: (data) => api.post('/users/register', data),
  /** 用户登录 */
  login: (data) => api.post('/users/login', data),
  /** 获取当前用户信息 */
  getMe: () => api.get('/users/me'),
}

// ==================== 商品模块 API ====================

export const productApi = {
  /** 获取商品列表 */
  getList: (params) => api.get('/products', { params }),
  /** 获取商品详情 */
  getDetail: (id) => api.get(`/products/${id}`),
  /** 添加商品 */
  create: (data) => api.post('/products', data),
}

// ==================== 秒杀模块 API ====================

export const seckillApi = {
  /** 获取秒杀活动列表 */
  getActivities: () => api.get('/seckill/activities'),
  /** 获取秒杀活动详情 */
  getActivityDetail: (id) => api.get(`/seckill/activities/${id}`),
  /** 创建秒杀活动 */
  createActivity: (data) => api.post('/seckill/activities', data),
  /** 执行秒杀 */
  execute: (activityId, quantity = 1) =>
    api.post(`/seckill/${activityId}/execute`, null, { params: { quantity } }),
}

// ==================== 订单模块 API ====================

export const orderApi = {
  /** 获取订单列表 */
  getList: (params) => api.get('/orders', { params }),
  /** 模拟支付 */
  pay: (orderId) => api.post(`/orders/${orderId}/pay`),
  /** 取消订单 */
  cancel: (orderId) => api.post(`/orders/${orderId}/cancel`),
}

// ==================== AI Agent API ====================

export const agentApi = {
  /** 与 AI 助手对话 */
  chat: (data) => api.post('/agent/chat', data),
}

export default api
