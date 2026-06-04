import request from './request'

// 单文件上传
export function uploadFile(file, category, name) {
  const formData = new FormData()
  formData.append('file', file)
  if (category) formData.append('category', category)
  if (name) formData.append('name', name)
  
  return request.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 批量文件上传
export function uploadBatch(files, category) {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  if (category) formData.append('category', category)
  
  return request.post('/upload/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取文件列表
export function getFiles(params) {
  return request.get('/upload/files', { params })
}

// 获取上传统计
export function getUploadStats() {
  return request.get('/upload/stats')
}

// 获取上传配置
export function getUploadConfig() {
  return request.get('/upload/config')
}

// 删除文件
export function deleteFile(filePath) {
  return request.post('/upload/delete', { file_path: filePath })
}

// 同步到阿里云 OSS
export function syncToOSS(category) {
  return request.post('/upload/sync/oss', { category })
}
