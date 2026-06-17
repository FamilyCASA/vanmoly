/**
 * 财务管理模块 API
 */
import request from '@/utils/request'

const financeAPI = {
  // ========== 组织架构与权限 ==========
  
  /** 获取财务角色列表 */
  getRoles() {
    return request({
      url: '/finance/roles',
      method: 'get'
    })
  },
  
  /** 获取财务团队成员 */
  getMembers() {
    return request({
      url: '/finance/members',
      method: 'get'
    })
  },
  
  /** 添加财务团队成员 */
  createMember(data) {
    return request({
      url: '/finance/members',
      method: 'post',
      data
    })
  },
  
  /** 更新财务团队成员 */
  updateMember(id, data) {
    return request({
      url: `/finance/members/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除财务团队成员 */
  deleteMember(id) {
    return request({
      url: `/finance/members/${id}`,
      method: 'delete'
    })
  },
  
  /** 获取可添加的用户列表 */
  getAvailableUsers() {
    return request({
      url: '/finance/members/available',
      method: 'get'
    })
  },
  
  /** 获取当前用户的财务权限 */
  getMyPermissions() {
    return request({
      url: '/finance/my-permissions',
      method: 'get'
    })
  },
  
  // ========== 流水管理 ==========
  
  /** 获取财务总览 */
  getOverview() {
    return request({
      url: '/finance/overview',
      method: 'get'
    })
  },
  
  /** 获取流水列表 */
  getTransactions(params) {
    return request({
      url: '/finance/transactions',
      method: 'get',
      params
    })
  },
  
  /** 创建流水 */
  createTransaction(data) {
    return request({
      url: '/finance/transactions',
      method: 'post',
      data
    })
  },
  
  /** 更新流水 */
  updateTransaction(id, data) {
    return request({
      url: `/finance/transactions/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除流水 */
  deleteTransaction(id, reason) {
    return request({
      url: `/finance/transactions/${id}`,
      method: 'delete',
      data: { reason }
    })
  },
  
  /** 审核流水 */
  reviewTransaction(id, status, note) {
    return request({
      url: `/finance/transactions/${id}/review`,
      method: 'put',
      data: { status, note }
    })
  },
  
  // ========== 报销管理 ==========
  
  /** 获取报销列表 */
  getReimbursements(params) {
    return request({
      url: '/finance/reimbursements',
      method: 'get',
      params
    })
  },
  
  /** 创建报销申请 */
  createReimbursement(data) {
    return request({
      url: '/finance/reimbursements',
      method: 'post',
      data
    })
  },
  
  /** 审核报销 */
  reviewReimbursement(id, status, note) {
    return request({
      url: `/finance/reimbursements/${id}/review`,
      method: 'put',
      data: { status, note }
    })
  },
  
  /** 确认付款 */
  payReimbursement(id, data) {
    return request({
      url: `/finance/reimbursements/${id}/pay`,
      method: 'put',
      data
    })
  },
  
  /** 获取我的报销 */
  getMyReimbursements(params) {
    return request({
      url: '/finance/my-reimbursements',
      method: 'get',
      params
    })
  },
  
  // ========== 分类管理 ==========
  
  /** 获取收支分类 */
  getCategories(params) {
    return request({
      url: '/finance/categories',
      method: 'get',
      params
    })
  },
  
  // ========== 投资管理 ==========
  
  /** 获取股东列表 */
  getShareholders() {
    return request({
      url: '/finance/shareholders',
      method: 'get'
    })
  },
  
  /** 创建股东 */
  createShareholder(data) {
    return request({
      url: '/finance/shareholders',
      method: 'post',
      data
    })
  },
  
  /** 更新股东 */
  updateShareholder(id, data) {
    return request({
      url: `/finance/shareholders/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除股东 */
  deleteShareholder(id) {
    return request({
      url: `/finance/shareholders/${id}`,
      method: 'delete'
    })
  },
  
  /** 获取企业章程 */
  getCharter() {
    return request({
      url: '/finance/charter',
      method: 'get'
    })
  },
  
  /** 保存企业章程 */
  saveCharter(data) {
    return request({
      url: '/finance/charter',
      method: 'post',
      data
    })
  },
  
  // ========== 操作日志 ==========
  
  /** 获取操作日志 */
  getAuditLogs(params) {
    return request({
      url: '/finance/audit-logs',
      method: 'get',
      params
    })
  },
  
  // ========== 财务分析 ==========
  
  /** 总览统计 */
  getAnalysisOverview() {
    return request({
      url: '/finance/analysis/overview',
      method: 'get'
    })
  },
  
  /** 月度收支趋势 */
  getMonthlyTrend() {
    return request({
      url: '/finance/analysis/monthly-trend',
      method: 'get'
    })
  },
  
  /** 分类统计 */
  getCategoryStats(params) {
    return request({
      url: '/finance/analysis/category-stats',
      method: 'get',
      params
    })
  },
  
  /** 最近交易 */
  getRecentTransactions(params) {
    return request({
      url: '/finance/analysis/recent-transactions',
      method: 'get',
      params
    })
  },

  // ========== 应收应付管理 ==========

  /** 获取应收款项列表 */
  getReceivables(params) {
    return request({ url: '/finance/receivables', method: 'get', params })
  },

  /** 创建应收款项 */
  createReceivable(data) {
    return request({ url: '/finance/receivables', method: 'post', data })
  },

  /** 更新应收款项 */
  updateReceivable(id, data) {
    return request({ url: `/finance/receivables/${id}`, method: 'put', data })
  },

  /** 删除应收款项 */
  deleteReceivable(id) {
    return request({ url: `/finance/receivables/${id}`, method: 'delete' })
  },

  /** 获取应付款项列表 */
  getPayables(params) {
    return request({ url: '/finance/payables', method: 'get', params })
  },

  /** 创建应付款项 */
  createPayable(data) {
    return request({ url: '/finance/payables', method: 'post', data })
  },

  /** 更新应付款项 */
  updatePayable(id, data) {
    return request({ url: `/finance/payables/${id}`, method: 'put', data })
  },

  /** 删除应付款项 */
  deletePayable(id) {
    return request({ url: `/finance/payables/${id}`, method: 'delete' })
  },

  // ========== 付款计划 ==========

  /** 获取付款计划 */
  getPaymentPlans(params) {
    return request({ url: '/finance/payment-plans', method: 'get', params })
  },

  /** 创建付款计划（支持批量分期） */
  createPaymentPlan(data) {
    return request({ url: '/finance/payment-plans', method: 'post', data })
  },

  /** 更新付款计划（确认收付款） */
  updatePaymentPlan(id, data) {
    return request({ url: `/finance/payment-plans/${id}`, method: 'put', data })
  },

  /** 删除付款计划 */
  deletePaymentPlan(id) {
    return request({ url: `/finance/payment-plans/${id}`, method: 'delete' })
  },

  // ========== 部门管理 ==========
  getDepartments(params) {
    return request({ url: '/finance/departments', params })
  },
  createDepartment(data) {
    return request({ url: '/finance/departments', method: 'post', data })
  },
  updateDepartment(id, data) {
    return request({ url: `/finance/departments/${id}`, method: 'put', data })
  },
  deleteDepartment(id) {
    return request({ url: `/finance/departments/${id}`, method: 'delete' })
  },
  // ========== 岗位管理 ==========
  getPositions(params) {
    return request({ url: '/finance/positions', params })
  },
  createPosition(data) {
    return request({ url: '/finance/positions', method: 'post', data })
  },
  updatePosition(id, data) {
    return request({ url: `/finance/positions/${id}`, method: 'put', data })
  },
  deletePosition(id) {
    return request({ url: `/finance/positions/${id}`, method: 'delete' })
  }
}

export default financeAPI
