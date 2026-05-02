import request from './request'

// ========== 案例管理 ==========

// 获取案例列表
export function getCases(params) {
  return request.get('/cases', { params })
}

// 获取案例详情
export function getCase(id) {
  return request.get(`/cases/${id}`)
}

// 创建案例
export function createCase(data) {
  return request.post('/cases', data)
}

// 更新案例
export function updateCase(id, data) {
  return request.put(`/cases/${id}`, data)
}

// 删除案例
export function deleteCase(id) {
  return request.delete(`/cases/${id}`)
}

// 批量操作
export function batchOperation(data) {
  return request.post('/cases/batch', data)
}

// ========== 发布管理 ==========

// 立即发布
export function publishCase(id) {
  return request.post(`/cases/${id}/publish`)
}

// 定时发布
export function scheduleCase(id, data) {
  return request.post(`/cases/${id}/schedule`, data)
}

// 下架
export function unpublishCase(id) {
  return request.post(`/cases/${id}/unpublish`)
}

// 获取置顶列表
export function getPinnedCases() {
  return request.get('/cases/pinned')
}

// ========== 时间轴 ==========

// 获取时间轴
export function getTimeline(caseId) {
  return request.get(`/cases/${caseId}/timeline`)
}

// 添加时间节点
export function addTimeline(caseId, data) {
  return request.post(`/cases/${caseId}/timeline`, data)
}

// 更新时间节点
export function updateTimeline(nodeId, data) {
  return request.put(`/timeline/${nodeId}`, data)
}

// 删除时间节点
export function deleteTimeline(nodeId) {
  return request.delete(`/timeline/${nodeId}`)
}

// ========== 文件管理 ==========

// 获取文件列表
export function getFiles(caseId) {
  return request.get(`/cases/${caseId}/files`)
}

// 添加文件
export function addFile(caseId, data) {
  return request.post(`/cases/${caseId}/files`, data)
}

// 删除文件
export function deleteFile(fileId) {
  return request.delete(`/files/${fileId}`)
}

// 下载文件
export function downloadFile(fileId) {
  return request.get(`/files/${fileId}/download`)
}

// ========== 客资管理 ==========

// 获取案例留资
export function getCaseLeads(caseId, params) {
  return request.get(`/cases/${caseId}/leads`, { params })
}

// 获取全部留资
export function getAllLeads(params) {
  return request.get('/case-leads', { params })
}

// 标记已联系
export function markLeadContacted(leadId, data) {
  return request.post(`/case-leads/${leadId}/contact`, data)
}

// 标记已转化
export function markLeadConverted(leadId) {
  return request.post(`/case-leads/${leadId}/convert`)
}

// ========== 模板库 ==========

// 获取模板列表
export function getTemplates() {
  return request.get('/case-templates')
}

// 创建模板
export function createTemplate(data) {
  return request.post('/case-templates', data)
}

// 获取模板详情
export function getTemplate(id) {
  return request.get(`/case-templates/${id}`)
}

// 更新模板
export function updateTemplate(id, data) {
  return request.put(`/case-templates/${id}`, data)
}

// 删除模板
export function deleteTemplate(id) {
  return request.delete(`/case-templates/${id}`)
}

// 使用模板
export function useTemplate(id, data) {
  return request.post(`/case-templates/${id}/use`, data)
}

// ========== 数据统计 ==========

// 获取案例统计
export function getCaseStats(id) {
  return request.get(`/cases/${id}/stats`)
}

// 获取全局统计
export function getStatsOverview() {
  return request.get('/cases/stats/overview')
}

// ========== 前台公开 API ==========

// 获取公开案例列表
export function getPublicCases(params) {
  return request.get('/public/cases', { params })
}

// 获取公开案例详情
export function getPublicCase(id) {
  return request.get(`/public/cases/${id}`)
}

// 点赞案例
export function likeCase(id) {
  return request.post(`/public/cases/${id}/like`)
}

// 订阅案例
export function subscribeCase(id, data) {
  return request.post(`/public/cases/${id}/subscribe`, data)
}

// 提交留资
export function createCaseLead(id, data) {
  return request.post(`/public/cases/${id}/lead`, data)
}

// 获取筛选选项
export function getCaseFilters() {
  return request.get('/public/cases/filters')
}

// 获取精选案例
export function getFeaturedCases(limit = 6) {
  return request.get('/cases/featured', { params: { limit } })
}

// 上传案例媒体
export function uploadCaseMedia(id, formData) {
  return request.post(`/cases/${id}/media`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取案例详情（兼容旧方法）
export function getCaseDetail(id, params = {}) {
  return request.get(`/cases/${id}`, { params })
}

// 上传文件
export function uploadFile(formData) {
  return request.post('/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ========== 服务流程 Workflow ==========

// 初始化服务流程
export function initWorkflow(caseId) {
  return request.post(`/cases/${caseId}/workflow/init`)
}

// 获取服务流程时间轴
export function getWorkflowTimeline(caseId) {
  return request.get(`/cases/${caseId}/workflow/timeline`)
}

// 更新流程节点状态
export function updateWorkflowNode(caseId, data) {
  return request.post(`/cases/${caseId}/workflow/timeline`, data)
}

// 更新授权状态
export function authorizeWorkflow(caseId, data) {
  return request.post(`/cases/${caseId}/workflow/authorize`, data)
}

// 上传流程节点照片
export function uploadWorkflowPhoto(caseId, formData) {
  return request.post(`/cases/${caseId}/workflow/photos`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取流程节点模板列表（用于时间轴节点选择）
export function getWorkflowNodes() {
  return request.get('/workflow/nodes')
}
