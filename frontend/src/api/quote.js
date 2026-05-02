/**
 * 报价管理 API
 */

import request from '@/utils/request'

// ========== 报价单 ==========

/**
 * 获取报价单列表
 * @param {Object} params 查询参数
 */
export function getQuotes(params = {}) {
  return request({
    url: '/quotes',
    method: 'get',
    params
  })
}

/**
 * 获取报价单详情
 * @param {number} id 报价单ID
 */
export function getQuote(id, params = {}) {
  return request({
    url: `/quotes/${id}`,
    method: 'get',
    params
  })
}

/**
 * 创建报价单
 * @param {Object} data 报价单数据
 */
export function createQuote(data) {
  return request({
    url: '/quotes',
    method: 'post',
    data
  })
}

/**
 * 更新报价单
 * @param {number} id 报价单ID
 * @param {Object} data 更新数据
 */
export function updateQuote(id, data) {
  return request({
    url: `/quotes/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除报价单
 * @param {number} id 报价单ID
 */
export function deleteQuote(id) {
  return request({
    url: `/quotes/${id}`,
    method: 'delete'
  })
}

// ========== 报价空间 ==========

/**
 * 获取报价空间列表
 * @param {number} quoteId 报价单ID
 */
export function getQuoteSpaces(quoteId) {
  return request({
    url: `/quotes/${quoteId}/spaces`,
    method: 'get'
  })
}

/**
 * 获取报价项目列表（用于引用添加到案例造价明细）
 * @param {number} quoteId 报价单ID
 */
export function getQuoteItems(quoteId) {
  return request({
    url: `/quotes/${quoteId}/items`,
    method: 'get'
  })
}

// ========== 客户 ==========

/**
 * 获取客户列表（下拉选择用）
 * @param {Object} params 查询参数
 */
export function getCustomers(params = {}) {
  return request({
    url: '/customers',
    method: 'get',
    params
  })
}

/**
 * 获取客户详情
 * @param {number} id 客户ID
 */
export function getCustomer(id) {
  return request({
    url: `/customers/${id}`,
    method: 'get'
  })
}