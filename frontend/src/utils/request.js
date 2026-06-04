/**
 * API 请求封装
 * 基于 axios 的 HTTP 客户端
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
// baseURL 用相对路径，通过 Vite 代理统一转发到后端 8080
// 开发环境：/api/v3 → Vite proxy → http://localhost:8080/api/v3
// 生产环境：/api/v3 → Nginx 反向代理 → 后端
const request = axios.create({
  baseURL: '/api/v3',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 所有请求默认都带 token（后台接口需要认证）
    // 公开接口列表（不需要 token 的）
    const publicPaths = [
      '/cases/featured',
      '/public/cases',
      '/leads/public',
      '/auth/login',
      '/auth/register'
    ]
    const isPublicPath = publicPaths.some(p => config.url.includes(p))
    
    const token = localStorage.getItem('token')
    if (token && !isPublicPath) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // FormData 自动带上正确的 Content-Type（multipart/form-data + boundary）
    // 不要显式设置 Content-Type，否则 Flask 无法解析 request.files
    // 必须直接操作 axios headers 对象，清除实例级默认 Content-Type
    if (config.data instanceof FormData) {
      config.headers.delete('Content-Type')
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 如果响应格式是 { code, message, data }
    if (res.code !== undefined) {
      // 接受所有 2xx 状态码（200-299）为成功
      if (res.code < 200 || res.code >= 300) {
        ElMessage.error(res.message || '请求失败')
        return Promise.reject(new Error(res.message || '请求失败'))
      }
      // 解包到 data 层，业务代码直接用 res.items / res.data 访问
      return res.data
    }
    
    return res
  },
  (error) => {
    const { response } = error
    
    if (response) {
      // 401 统一处理：清除 token 并跳转登录页
      if (response.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      } else if (response.status === 403) {
        ElMessage.error('没有权限执行此操作')
      } else if (response.status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (response.status === 500) {
        ElMessage.error('服务器错误')
      } else {
        ElMessage.error(response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default request
