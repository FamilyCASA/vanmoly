import request from './request'

// 提交留资（对外接口）
export function createLead(data) {
  return request.post('/leads', data)
}

// 获取线索列表（管理端）
export function getLeads(params) {
  return request.get('/leads', { params })
}

// 获取线索详情
export function getLeadDetail(id, params = {}) {
  return request.get(`/leads/${id}`, { params })
}

// 分配线索
export function assignLead(id, data) {
  return request.put(`/leads/${id}/assign`, data)
}

// 更新线索状态
export function updateLeadStatus(id, data) {
  return request.put(`/leads/${id}/status`, data)
}

// 添加跟进记录
export function addLeadFollow(id, data) {
  return request.post(`/leads/${id}/follow`, data)
}

// 更新线索信息
export function updateLead(id, data) {
  return request.put(`/leads/${id}`, data)
}

// 删除线索
export function deleteLead(id) {
  return request.delete(`/leads/${id}`)
}

// 获取线索统计
export function getLeadStats() {
  return request.get('/leads/stats')
}

// 获取线索来源列表
export function getLeadSources() {
  return request.get('/leads/sources')
}
