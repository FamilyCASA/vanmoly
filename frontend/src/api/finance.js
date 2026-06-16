/**
 * 财务管理模块 API
 */
import request from '@/utils/request'

const financeAPI = {
  // ========== 组织架构与权限 ==========
  
  /** 获取财务角色列表 */
  getRoles() {
    return request({
      url: '/api/v3/finance/roles',
      method: 'get'
    })
  },
  
  /** 获取财务团队成员 */
  getMembers() {
    return request({
      url: '/api/v3/finance/members',
      method: 'get'
    })
  },
  
  /** 添加财务团队成员 */
  createMember(data) {
    return request({
      url: '/api/v3/finance/members',
      method: 'post',
      data
    })
  },
  
  /** 更新财务团队成员 */
  updateMember(id, data) {
    return request({
      url: `/api/v3/finance/members/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除财务团队成员 */
  deleteMember(id) {
    return request({
      url: `/api/v3/finance/members/${id}`,
      method: 'delete'
    })
  },
  
  /** 获取可添加的用户列表 */
  getAvailableUsers() {
    return request({
      url: '/api/v3/finance/members/available',
      method: 'get'
    })
  },
  
  /** 获取当前用户的财务权限 */
  getMyPermissions() {
    return request({
      url: '/api/v3/finance/my-permissions',
      method: 'get'
    })
  },
  
  // ========== 流水管理 ==========
  
  /** 获取财务总览 */
  getOverview() {
    return request({
      url: '/api/v3/finance/overview',
      method: 'get'
    })
  },
  
  /** 获取流水列表 */
  getTransactions(params) {
    return request({
      url: '/api/v3/finance/transactions',
      method: 'get',
      params
    })
  },
  
  /** 创建流水 */
  createTransaction(data) {
    return request({
      url: '/api/v3/finance/transactions',
      method: 'post',
      data
    })
  },
  
  /** 更新流水 */
  updateTransaction(id, data) {
    return request({
      url: `/api/v3/finance/transactions/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除流水 */
  deleteTransaction(id, reason) {
    return request({
      url: `/api/v3/finance/transactions/${id}`,
      method: 'delete',
      data: { reason }
    })
  },
  
  /** 审核流水 */
  reviewTransaction(id, status, note) {
    return request({
      url: `/api/v3/finance/transactions/${id}/review`,
      method: 'put',
      data: { status, note }
    })
  },
  
  // ========== 报销管理 ==========
  
  /** 获取报销列表 */
  getReimbursements(params) {
    return request({
      url: '/api/v3/finance/reimbursements',
      method: 'get',
      params
    })
  },
  
  /** 创建报销申请 */
  createReimbursement(data) {
    return request({
      url: '/api/v3/finance/reimbursements',
      method: 'post',
      data
    })
  },
  
  /** 审核报销 */
  reviewReimbursement(id, status, note) {
    return request({
      url: `/api/v3/finance/reimbursements/${id}/review`,
      method: 'put',
      data: { status, note }
    })
  },
  
  /** 确认付款 */
  payReimbursement(id, data) {
    return request({
      url: `/api/v3/finance/reimbursements/${id}/pay`,
      method: 'put',
      data
    })
  },
  
  /** 获取我的报销 */
  getMyReimbursements(params) {
    return request({
      url: '/api/v3/finance/my-reimbursements',
      method: 'get',
      params
    })
  },
  
  // ========== 分类管理 ==========
  
  /** 获取收支分类 */
  getCategories(params) {
    return request({
      url: '/api/v3/finance/categories',
      method: 'get',
      params
    })
  },
  
  // ========== 投资管理 ==========
  
  /** 获取股东列表 */
  getShareholders() {
    return request({
      url: '/api/v3/finance/shareholders',
      method: 'get'
    })
  },
  
  /** 创建股东 */
  createShareholder(data) {
    return request({
      url: '/api/v3/finance/shareholders',
      method: 'post',
      data
    })
  },
  
  /** 更新股东 */
  updateShareholder(id, data) {
    return request({
      url: `/api/v3/finance/shareholders/${id}`,
      method: 'put',
      data
    })
  },
  
  /** 删除股东 */
  deleteShareholder(id) {
    return request({
      url: `/api/v3/finance/shareholders/${id}`,
      method: 'delete'
    })
  },
  
  /** 获取企业章程 */
  getCharter() {
    return request({
      url: '/api/v3/finance/charter',
      method: 'get'
    })
  },
  
  /** 保存企业章程 */
  saveCharter(data) {
    return request({
      url: '/api/v3/finance/charter',
      method: 'post',
      data
    })
  },
  
  // ========== 操作日志 ==========
  
  /** 获取操作日志 */
  getAuditLogs(params) {
    return request({
      url: '/api/v3/finance/audit-logs',
      method: 'get',
      params
    })
  }
}

export default financeAPI
