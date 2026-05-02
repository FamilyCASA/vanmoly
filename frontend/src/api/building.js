import request from './request'

// 获取楼盘列表
export function getBuildings(params) {
  return request.get('/buildings', { params })
}

// 获取楼盘详情
export function getBuilding(id) {
  return request.get(`/buildings/${id}`)
}

// 创建楼盘
export function createBuilding(data) {
  return request.post('/buildings', data)
}

// 更新楼盘
export function updateBuilding(id, data) {
  return request.put(`/buildings/${id}`, data)
}

// 删除楼盘
export function deleteBuilding(id) {
  return request.delete(`/buildings/${id}`)
}

// 获取楼盘选项（下拉选择用）
export function getBuildingOptions() {
  return request.get('/buildings/options')
}
