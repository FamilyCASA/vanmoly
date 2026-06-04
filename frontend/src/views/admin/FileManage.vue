<template>
  <div class="file-manage">
    <div class="page-header">
      <h2>文件管理</h2>
      <el-button type="primary" @click="uploadDialogVisible = true">
        <el-icon><Upload /></el-icon> 上传文件
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="(stat, key) in stats" :key="key">
        <el-card>
          <div class="stat-item">
            <div class="stat-icon" :class="key">
              <el-icon v-if="key === 'image'"><Picture /></el-icon>
              <el-icon v-else-if="key === 'office'"><Document /></el-icon>
              <el-icon v-else-if="key === 'audio'"><Microphone /></el-icon>
              <el-icon v-else-if="key === 'video'"><VideoCamera /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.count || 0 }}</div>
              <div class="stat-label">{{ categoryNames[key] }}</div>
              <div class="stat-size">{{ stat.size_human || '0 B' }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选工具栏 -->
    <el-card class="toolbar">
      <el-form :model="filters" inline>
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="全部分类" clearable style="width: 120px">
            <el-option label="图片" value="image" />
            <el-option label="文档" value="office" />
            <el-option label="音频" value="audio" />
            <el-option label="视频" value="video" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
        <el-form-item style="margin-left: auto">
          <el-button type="success" @click="handleSyncOSS" :loading="syncing">
            <el-icon><CloudUpload /></el-icon> 同步到阿里云
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文件列表 -->
    <el-card>
      <el-table :data="files" v-loading="loading" stripe>
        <el-table-column label="文件名" min-width="250">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon" :size="20" :class="row.category">
                <Picture v-if="row.category === 'image'" />
                <Document v-else-if="row.category === 'office'" />
                <Microphone v-else-if="row.category === 'audio'" />
                <VideoCamera v-else-if="row.category === 'video'" />
                <Document v-else />
              </el-icon>
              <span class="name-text" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getCategoryType(row.category)">
              {{ categoryNames[row.category] || row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="previewFile(row)">预览</el-button>
            <el-button type="danger" link @click="deleteFile(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="600px">
      <el-upload
        ref="uploadRef"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        multiple
        :file-list="fileList"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="upload-tip">
            <p>支持类型：</p>
            <ul>
              <li>图片：JPG、PNG、GIF、WebP（最大10MB）</li>
              <li>文档：Word、Excel、PPT、PDF（最大50MB）</li>
              <li>音频：MP3、WAV、AAC（最大100MB）</li>
              <li>视频：MP4、MOV、AVI（最大500MB）</li>
            </ul>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          开始上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="previewVisible"
      :url-list="[previewUrl]"
      @close="previewVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, Picture, Document, Microphone, VideoCamera
} from '@element-plus/icons-vue'
import { 
  getFiles, getUploadStats, uploadBatch, deleteFile as apiDeleteFile, syncToOSS 
} from '@/api/upload'

const loading = ref(false)
const uploading = ref(false)
const syncing = ref(false)
const uploadDialogVisible = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')
const fileList = ref([])

const stats = ref({})
const files = ref([])

const filters = reactive({
  category: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const categoryNames = {
  image: '图片',
  office: '文档',
  audio: '音频',
  video: '视频'
}

const fetchStats = async () => {
  try {
    const res = await getUploadStats()
    stats.value = res || {}
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const fetchFiles = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    const res = await getFiles(params)
    files.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取文件列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchFiles()
}

const resetFilters = () => {
  filters.category = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchFiles()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchFiles()
}

const getCategoryType = (category) => {
  const map = {
    image: 'success',
    office: 'primary',
    audio: 'warning',
    video: 'danger'
  }
  return map[category] || 'info'
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  uploading.value = true
  try {
    const files = fileList.value.map(f => f.raw)
    const res = await uploadBatch(files, filters.category)
    
    if (res.failed && res.failed.length > 0) {
      ElMessage.warning(`上传完成: ${res.success_count}个成功, ${res.failed_count}个失败`)
    } else {
      ElMessage.success(`成功上传 ${res.success_count} 个文件`)
    }
    
    uploadDialogVisible.value = false
    fileList.value = []
    fetchFiles()
    fetchStats()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const previewFile = (row) => {
  if (row.category === 'image') {
    previewUrl.value = row.url
    previewVisible.value = true
  } else {
    window.open(row.url, '_blank')
  }
}

const deleteFile = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await apiDeleteFile(row.path)
    ElMessage.success('删除成功')
    fetchFiles()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSyncOSS = async () => {
  try {
    await ElMessageBox.confirm('确定要同步所有文件到阿里云 OSS 吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    syncing.value = true
    const res = await syncToOSS(filters.category)
    
    if (res.failed > 0) {
      ElMessage.warning(`同步完成: ${res.success}个成功, ${res.failed}个失败`)
    } else {
      ElMessage.success(`成功同步 ${res.success} 个文件`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('同步失败:', error)
      ElMessage.error('同步失败: ' + (error.message || '未知错误'))
    }
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchFiles()
})
</script>

<style scoped>
.file-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.image { background: rgba(34,197,94,0.1); color: #22c55e; }
.stat-icon.office { background: rgba(59,130,246,0.1); color: #3b82f6; }
.stat-icon.audio { background: rgba(245,158,11,0.1); color: #f59e0b; }
.stat-icon.video { background: rgba(239,68,68,0.1); color: #ef4444; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.stat-size {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.toolbar {
  margin-bottom: 20px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  flex-shrink: 0;
}

.file-icon.image { color: #22c55e; }
.file-icon.office { color: #3b82f6; }
.file-icon.audio { color: #f59e0b; }
.file-icon.video { color: #ef4444; }

.name-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.upload-tip {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
}

.upload-tip p {
  margin: 0 0 8px;
  font-weight: 500;
}

.upload-tip ul {
  margin: 0;
  padding-left: 20px;
}

.upload-tip li {
  margin: 4px 0;
}
</style>
