import request from './request'

// 提交预约（对外接口）
export function createAppointment(data) {
  return request.post('/appointments', data)
}

// 获取预约列表（管理端）
export function getAppointments(params) {
  return request.get('/appointments', { params })
}

// 获取预约详情
export function getAppointmentDetail(id) {
  return request.get(`/appointments/${id}`)
}

// 更新预约
export function updateAppointment(id, data) {
  return request.put(`/appointments/${id}`, data)
}

// 删除预约
export function deleteAppointment(id) {
  return request.delete(`/appointments/${id}`)
}

// 获取预约统计
export function getAppointmentStats() {
  return request.get('/appointments/stats')
}

// 获取日历数据
export function getAppointmentCalendar(params) {
  return request.get('/appointments/calendar', { params })
}
