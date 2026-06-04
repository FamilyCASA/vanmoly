/**
 * 员工管理 API
 */

import request from '@/utils/request'

const BASE_URL = '/employees'

/**
 * 获取员工列表
 * @param {Object} params 查询参数
 */
export function getEmployees(params = {}) {
  return request({
    url: BASE_URL,
    method: 'get',
    params
  })
}

/**
 * 获取员工详情
 * @param {number} id 员工ID
 */
export function getEmployee(id) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'get'
  })
}

/**
 * 创建员工
 * @param {Object} data 员工数据
 */
export function createEmployee(data) {
  return request({
    url: BASE_URL,
    method: 'post',
    data
  })
}

/**
 * 更新员工
 * @param {number} id 员工ID
 * @param {Object} data 更新数据
 */
export function updateEmployee(id, data) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除员工
 * @param {number} id 员工ID
 */
export function deleteEmployee(id) {
  return request({
    url: `${BASE_URL}/${id}`,
    method: 'delete'
  })
}

/**
 * 获取员工统计
 */
export function getEmployeeStats() {
  return request({
    url: `${BASE_URL}/stats`,
    method: 'get'
  })
}
