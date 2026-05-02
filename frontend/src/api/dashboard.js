import request from './request'

// 获取看板核心统计数据
export function getDashboardStats() {
  return request.get('/dashboard/stats')
}

// 获取业务趋势数据
export function getTrends(period = 'week') {
  return request.get('/dashboard/trends', { params: { period } })
}

// 获取合同金额分布
export function getContractDistribution() {
  return request.get('/dashboard/contract-distribution')
}

// 获取最近动态
export function getRecentActivities(limit = 10) {
  return request.get('/dashboard/recent-activities', { params: { limit } })
}

// 获取获客漏斗数据
export function getFunnel() {
  return request.get('/dashboard/funnel')
}

// 获取案例统计数据
export function getCaseStats() {
  return request.get('/dashboard/case-stats')
}

// 获取获客数据
export function getLeadStats() {
  return request.get('/dashboard/lead-stats')
}
