<template>
  <div class="phase-space-renderings-editor">
    <!-- 报价表引用提示 -->
    <div v-if="!quoteId" class="quote-tip">
      <el-alert
        title="提示：关联报价表后，空间名称可从报价表引用"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 空间列表 -->
    <div class="spaces-list">
      <div
        v-for="(space, idx) in spaces"
        :key="space.id || idx"
        class="space-block"
      >
        <div class="space-header">
          <el-select
            v-model="space.space_name"
            placeholder="选择或输入空间名称（支持自定义）"
            filterable
            allow-create
            default-first-option
            style="width: 240px"
            @change="saveSpaceName(idx)"
          >
            <el-option
              v-for="name in availableSpaceNames"
              :key="name"
              :label="name"
              :value="name"
            />
          </el-select>
          <div class="space-actions">
            <!-- 批量上传按钮 -->
            <el-button type="success" size="small" @click="triggerBatchUpload(idx)">
              <el-icon><Upload /></el-icon> 批量上传图片
            </el-button>
            <el-button type="primary" size="small" @click="addRendering(idx)">
              + 添加效果图
            </el-button>
            <el-button type="danger" size="small" link @click="removeSpace(idx)">
              删除空间
            </el-button>
          </div>
        </div>

        <!-- 效果图列表 -->
        <div class="renderings-grid">
          <div
            v-for="(item, i) in space.renderings"
            :key="item.id || i"
            class="rendering-card"
          >
            <div class="rendering-image">
              <img v-if="item.image_url" :src="item.image_url" />
              <div v-else class="upload-placeholder" @click="triggerSingleUpload(idx, i)">
                <el-icon><Plus /></el-icon>
                <span>点击上传</span>
              </div>
              <div v-if="item.image_url" class="img-overlay">
                <el-button size="small" @click="triggerSingleUpload(idx, i)">替换</el-button>
                <el-button type="danger" size="small" @click="removeRendering(idx, i)">删除</el-button>
              </div>
              <div v-if="item.uploading" class="uploading-mask">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>上传中...</span>
              </div>
            </div>
            <div class="rendering-info">
              <div style="display: flex; gap: 6px; margin-bottom: 8px">
                <el-input
                  v-model="item.title"
                  placeholder="效果图标题"
                  size="small"
                  style="flex: 1"
                />
                <el-button
                  size="small"
                  type="primary"
                  :loading="item.saving"
                  @click="saveRendering(idx, i, item)"
                >保存</el-button>
              </div>
              <div class="rich-label">简介文案（富文本）</div>
              <RichTextEditor
                v-model="item.description"
                placeholder="请输入效果图的详细介绍..."
              />
              <el-button
                size="small"
                type="success"
                :loading="item.saving"
                :disabled="item.saving"
                @click="saveRendering(idx, i, item)"
                style="margin-top: 8px; width: 100%"
              >
                <span v-if="item.saving">保存中...</span>
                <span v-else>💾 保存简介文案</span>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加空间按钮 -->
    <el-button type="primary" @click="addSpace" style="margin-top: 16px">
      + 添加空间
    </el-button>

    <!-- 隐藏的上传组件 - 单张 -->
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :show-file-list="false"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :before-upload="beforeUpload"
      accept="image/*"
      style="display: none;"
    />

    <!-- 隐藏的上传组件 - 批量 -->
    <el-upload
      ref="batchUploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :show-file-list="false"
      :multiple="true"
      :on-success="handleBatchSuccess"
      :on-error="handleBatchError"
      :before-upload="beforeBatchUpload"
      accept="image/*"
      style="display: none;"
    />
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading, Upload } from '@element-plus/icons-vue'
import request from '@/utils/request'
import RichTextEditor from '@/components/RichTextEditor.vue'

const props = defineProps({
  caseId: {
    type: Number,
    required: true
  },
  quoteId: {
    type: Number,
    default: null
  }
})

const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const batchUploadRef = ref(null)
const spaces = ref([])

// 当前上传位置
const uploadPosition = ref({ spaceIdx: 0, renderingIdx: 0 })
// 当前批量上传的空间索引
const batchSpaceIdx = ref(0)

// 更丰富的空间名称列表
const availableSpaceNames = ref([
  '客厅', '餐厅', '主卧', '次卧', '客房', '儿童房', '老人房', '书房',
  '厨房', '主卫', '次卫', '公卫', '阳台', '生活阳台', '景观阳台',
  '玄关', '过道', '门厅', '楼梯间', '电梯厅',
  '储物间', '衣帽间', '杂物间', '设备间',
  '影音室', '健身房', '茶室', '棋牌室', '酒窖', '保姆间', '车库',
  '办公室', '会议室', '接待区', '展示区', '前台'
])

// ==================== 数据加载 ====================

const loadSpaces = async () => {
  try {
    const res = await request.get('/cases/' + props.caseId + '/spaces')
    if (res && Array.isArray(res)) {
      spaces.value = res.map(s => ({
        ...s,
        renderings: s.renderings || []
      }))
    }
  } catch (e) {
    console.error('Load spaces failed:', e)
  }
}

const loadQuoteSpaceNames = async () => {
  if (!props.quoteId) return
  try {
    const res = await request.get('/quotes/' + props.quoteId + '/space-names')
    if (res && Array.isArray(res)) {
      const merged = [...new Set([...res, ...availableSpaceNames.value])]
      availableSpaceNames.value = merged
    }
  } catch (e) {
    console.error('Load quote space names failed:', e)
  }
}

// ==================== 空间操作 ====================

const addSpace = async () => {
  try {
    const res = await request.post('/cases/' + props.caseId + '/spaces', {
      space_name: '新空间'
    })
    if (res) {
      spaces.value.push({
        ...res,
        renderings: []
      })
      ElMessage.success('空间已添加')
    }
  } catch (e) {
    console.error('Add space failed:', e)
    ElMessage.error('添加失败：' + (e.response?.data?.message || e.message))
  }
}

const removeSpace = async (idx) => {
  const space = spaces.value[idx]
  if (!space.id) {
    spaces.value.splice(idx, 1)
    return
  }
  try {
    // API路径修复: /spaces/{id}
    await request.delete('/spaces/' + space.id)
    spaces.value.splice(idx, 1)
    ElMessage.success('空间已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const saveSpaceName = async (idx) => {
  const space = spaces.value[idx]
  if (!space.id) return
  try {
    await request.put('/spaces/' + space.id, {
      space_name: space.space_name
    })
  } catch (e) {
    console.error('Save space name failed:', e)
  }
}

// ==================== 效果图操作 ====================

const addRendering = async (spaceIdx) => {
  const space = spaces.value[spaceIdx]
  if (!space.id) {
    ElMessage.warning('请先保存空间')
    return
  }

  try {
    // API路径修复: /spaces/{id}/renderings
    const res = await request.post('/spaces/' + space.id + '/renderings', {
      image_url: '',
      title: '',
      description: ''
    })
    if (res) {
      if (!space.renderings) {
        space.renderings = []
      }
      space.renderings.push(res)
      ElMessage.success('效果图已添加，可点击图片区域上传')
    }
  } catch (e) {
    console.error('Add rendering failed:', e)
    ElMessage.error('添加效果图失败：' + (e.response?.data?.message || e.message))
  }
}

const removeRendering = async (spaceIdx, renderingIdx) => {
  const space = spaces.value[spaceIdx]
  const item = space.renderings[renderingIdx]

  if (!item.id) {
    space.renderings.splice(renderingIdx, 1)
    return
  }

  try {
    // API路径修复: /renderings/{id}
    await request.delete('/renderings/' + item.id)
    space.renderings.splice(renderingIdx, 1)
    ElMessage.success('效果图已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const saveRendering = async (spaceIdx, renderingIdx, item) => {
  if (!item.id) return
  item.saving = true
  try {
    // API路径: /renderings/{id}
    const saved = await request.put('/renderings/' + item.id, {
      title: item.title,
      description: item.description
    })
    // 用后端返回数据更新本地，确保 description 正确回填
    if (saved) {
      Object.assign(item, saved)
    }
    ElMessage.success('保存成功')
  } catch (e) {
    console.error('Save rendering failed:', e)
    ElMessage.error('保存失败：' + (e.message || '网络错误'))
  } finally {
    item.saving = false
  }
}

// ==================== 单张上传 ====================

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }

  const sp = uploadPosition.value
  const item = spaces.value[sp.spaceIdx]?.renderings[sp.renderingIdx]
  if (item) {
    item.uploading = true
  }
  return true
}

const triggerSingleUpload = (spaceIdx, renderingIdx) => {
  uploadPosition.value = { spaceIdx, renderingIdx }
  uploadRef.value?.$el?.querySelector('input')?.click()
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const pos = uploadPosition.value
    const item = spaces.value[pos.spaceIdx]?.renderings[pos.renderingIdx]
    if (item) {
      item.image_url = url
      item.uploading = false
      if (item.id) {
        request.put('/renderings/' + item.id, { image_url: url }).catch(e => console.error(e))
      }
    }
    ElMessage.success('图片上传成功')
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const pos = uploadPosition.value
  const item = spaces.value[pos.spaceIdx]?.renderings[pos.renderingIdx]
  if (item) {
    item.uploading = false
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

// ==================== 批量上传 ====================

const triggerBatchUpload = (spaceIdx) => {
  batchSpaceIdx.value = spaceIdx
  batchUploadRef.value?.$el?.querySelector('input')?.click()
}

const beforeBatchUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error(file.name + ' 不是图片，已跳过')
    return false
  }
  return true
}

const handleBatchSuccess = (res, file) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (!url) return

  const space = spaces.value[batchSpaceIdx.value]
  if (!space || !space.id) return

  // 为每张上传的图片自动创建效果图记录
  request.post('/spaces/' + space.id + '/renderings', {
    image_url: url,
    title: file.name.replace(/\.[^/.]+$/, ''),
    description: ''
  }).then(response => {
    if (response) {
      if (!space.renderings) space.renderings = []
      space.renderings.push({
        ...response,
        uploading: false
      })
    }
  }).catch(e => {
    console.error('Create rendering for uploaded image failed:', e)
    ElMessage.error(file.name + ' 创建记录失败')
  })
}

const handleBatchError = (err) => {
  ElMessage.error('部分图片上传失败：' + (err?.message || '未知错误'))
}

onMounted(() => {
  loadSpaces()
  loadQuoteSpaceNames()
})

watch(() => props.quoteId, () => {
  loadQuoteSpaceNames()
})
</script>

<style scoped>
.phase-space-renderings-editor {
  width: 100%;
}

.quote-tip {
  margin-bottom: 16px;
}

.space-block {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fafafa;
}

.space-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.space-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.renderings-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.rendering-card {
  width: 420px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.rendering-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.rendering-image {
  width: 100%;
  height: 240px;
  position: relative;
  background: #f5f7fa;
}

.rendering-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
  gap: 8px;
  transition: background 0.2s;
}

.upload-placeholder:hover {
  background: #e6e8eb;
}

.img-overlay {
  position: absolute; inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.rendering-image:hover .img-overlay {
  opacity: 1;
}

.uploading-mask {
  position: absolute; inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 13px;
  gap: 6px;
}

.rendering-info {
  padding: 14px;
}

.rich-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}
</style>
