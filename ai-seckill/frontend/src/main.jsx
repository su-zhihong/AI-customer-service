/**
 * 文件路径: frontend/src/main.jsx
 * React 应用入口文件。
 * 配置 Ant Design 主题（支持暗色模式）、路由、全局样式。
 */

import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme, App as AntApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './styles/global.css'

/**
 * 根组件：管理全局主题状态（亮色/暗色模式）
 */
function Root() {
  // 从 localStorage 读取主题偏好，默认为亮色模式
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })

  // 切换主题时保存到 localStorage
  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')
    // 更新 body 的 class，用于 Tailwind CSS 暗色模式
    document.body.className = isDarkMode ? 'dark' : ''
  }, [isDarkMode])

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        // 根据暗色模式切换算法
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#ff4d4f', // 秒杀主题红色
          borderRadius: 8,
        },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <App isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
)
