/**
 * 线索管理 API V2.0
 * 多分店客资线索管理系统
 */

import request from '@/utils/request'

const BASE_URL = '/leads'

// ========== 线索基础接口 ==========

/**
 * 获取线索列表
 * @param {Object} params 查询参数
 */
export function getLeads(params) {
  return request({
    url: BASE_URL,
    method: 'get',
    params
  })
}

/**
 * 获取线索详情
 * @param {number} id 线索ID
 * @param {Object} params 查询参数
 */
export function getLeadDetail(id, params = {}) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'get',
    params
  })
}

/**
 * 创建线索
 * @param {Object} data 线索数据
 */
export function createLead(data) {
  return request({
    url: BASE_URL,
    method: 'post',
    data
  })
}

/**
 * 更新线索
 * @param {number} id 线索ID
 * @param {Object} data 更新数据
 */
export function updateLead(id, data) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除线索
 * @param {number} id 线索ID
 */
export function deleteLead(id) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'delete'
  })
}

// ========== 跟进接口 ==========

/**
 * 添加跟进记录
 * @param {number} id 线索ID
 * @param {Object} data 跟进数据
 */
export function addFollow(id, data) {
  return request({
    url: `${BASE_URL}/${id}/follow`,
    method: 'post',
    data
  })
}

/**
 * 标记实际到店
 * @param {number} id 线索ID
 * @param {Object} data 到店数据
 */
export function markVisited(id, data) {
  return request({
    url: `${BASE_URL}/${id}/visit`,
    method: 'post',
    data
  })
}

/**
 * 标记交定金
 * @param {number} id 线索ID
 * @param {Object} data 定金数据
 */
export function markDeposit(id, data) {
  return request({
    url: `${BASE_URL}/${id}/deposit`,
    method: 'post',
    data
  })
}

/**
 * 标记签约
 * @param {number} id 线索ID
 * @param {Object} data 签约数据
 */
export function markContract(id, data) {
  return request({
    url: `${BASE_URL}/${id}/contract`,
    method: 'post',
    data
  })
}

// ========== 分配接口 ==========

/**
 * 分配线索
 * @param {number} id 线索ID
 * @param {Object} data 分配数据
 */
export function assignLead(id, data) {
  return request({
    url: `${BASE_URL}/${id}/assign`,
    method: 'post',
    data
  })
}

/**
 * 批量分配线索
 * @param {Object} data 批量分配数据 {lead_ids: [], employee_id: number}
 */
export function batchAssignLeads(data) {
  return request({
    url: `${BASE_URL}/batch/assign`,
    method: 'post',
    data
  })
}

/**
 * 标记无效
 * @param {number} id 线索ID
 * @param {Object} data 原因
 */
export function markInvalid(id, data) {
  return request({
    url: `${BASE_URL}/${id}/invalid`,
    method: 'post',
    data
  })
}

/**
 * 批量标记无效
 * @param {Object} data 批量数据
 */
export function batchMarkInvalid(data) {
  return request({
    url: `${BASE_URL}/batch/invalid`,
    method: 'post',
    data
  })
}

// ========== 公海接口 ==========

/**
 * 获取公海线索列表
 * @param {Object} params 查询参数
 */
export function getSeaLeads(params = {}) {
  return request({
    url: `${BASE_URL}/sea`,
    method: 'get',
    params
  })
}

/**
 * 从公海领取线索
 * @param {number} id 线索ID
 */
export function retrieveLeadFromSea(id) {
  return request({
    url: `${BASE_URL}/${id}/retrieve`,
    method: 'post'
  })
}

// ========== 积分接口 ==========

/**
 * 获取积分排行榜
 * @param {Object} params 查询参数 {period: 'today'|'week'|'month'|'all', limit: number}
 */
export function getPointsRanking(params = {}) {
  return request({
    url: '/points/ranking',
    method: 'get',
    params
  })
}

/**
 * 获取我的积分明细
 * @param {Object} params 查询参数
 */
export function getMyPoints(params = {}) {
  return request({
    url: '/points/my',
    method: 'get',
    params
  })
}

// ========== 统计接口 ==========

/**
 * 获取线索总览统计
 */
export function getLeadStats() {
  return request({
    url: `/stats/overview`,
    method: 'get'
  })
}

/**
 * 获取转化漏斗
 */
export function getConversionFunnel() {
  return request({
    url: `${BASE_URL}/stats/funnel`,
    method: 'get'
  })
}

/**
 * 获取渠道统计
 * @param {Object} params 查询参数 {start_date, end_date}
 */
export function getChannelStats(params = {}) {
  return request({
    url: `${BASE_URL}/stats/channels`,
    method: 'get',
    params
  })
}

// ========== 筛选选项 ==========

/**
 * 获取线索筛选选项
 */
export function getLeadFilters() {
  return request({
    url: `${BASE_URL}/filters`,
    method: 'get'
  })
}

// ========== 待办接口 ==========

/**
 * 获取待办事项
 */
export function getTodos() {
  return request({
    url: `${BASE_URL}/todos`,
    method: 'get'
  })
}

// ========== 升级接口 ==========

/**
 * 升级线索为客户
 * @param {number} id 线索ID
 */
export function upgradeToCustomer(id) {
  return request({
    url: `${BASE_URL}/${id}/upgrade`,
    method: 'post'
  })
}
