<template>
  <div class="phase-layout-editor">
    <el-form label-position="top">
      <!-- 户型图上传 -->
      <el-form-item label="户型图">
        <div class="image-upload-grid">
          <div
            v-for="(img, idx) in layoutImages"
            :key="idx"
            class="uploaded-image-card"
          >
            <img :src="img.url || img" alt="户型图" />
            <div v-if="img.uploading" class="uploading-mask">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>上传中...</span>
            </div>
            <div class="img-overlay">
              <el-icon class="delete-btn" @click="removeImage(idx)">
                <Close />
              </el-icon>
            </div>
          </div>
          <div class="upload-trigger" @click="triggerUpload">
            <el-icon><Plus /></el-icon>
            <span>上传户型图</span>
          </div>
        </div>
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
      </el-form-item>
      
      <!-- 户型分析文案 -->
      <el-form-item label="户型分析文案（2000字以内）">
        <RichTextEditor 
          v-model="layoutAnalysis" 
          placeholder="请输入户型分析文案..."
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Close, Loading } from '@element-plus/icons-vue'
import RichTextEditor from '@/components/RichTextEditor.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

// 上传配置
const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const layoutImages = ref([])
const layoutAnalysis = ref('')

// 初始化数据
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    layoutImages.value = newVal.layout_images || []
    layoutAnalysis.value = newVal.layout_analysis || ''
  }
}, { immediate: true })

// 触发上传
const triggerUpload = () => {
  uploadRef.value?.$el?.querySelector('input')?.click()
}

// 上传前校验 + 本地预览
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  // 立即显示本地预览
  const localUrl = URL.createObjectURL(file)
  layoutImages.value.push({ url: localUrl, uploading: true })
  emitUpdate()
  return true
}

// 上传成功 - 替换本地预览为服务器URL
const handleUploadSuccess = (res) => {
  // 兼容多种返回格式
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    // 找到正在上传的项，替换为真实URL
    const uploadingIdx = layoutImages.value.findIndex(img => img.uploading)
    if (uploadingIdx >= 0) {
      URL.revokeObjectURL(layoutImages.value[uploadingIdx].url)
      layoutImages.value[uploadingIdx] = { url, uploading: false }
    } else {
      layoutImages.value.push({ url, uploading: false })
    }
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

// 上传失败 - 回滚预览
const handleUploadError = (err) => {
  const uploadingIdx = layoutImages.value.findIndex(img => img.uploading)
  if (uploadingIdx >= 0) {
    URL.revokeObjectURL(layoutImages.value[uploadingIdx].url)
    layoutImages.value.splice(uploadingIdx, 1)
    emitUpdate()
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

// 删除图片
const removeImage = (idx) => {
  const img = layoutImages.value[idx]
  if (img && img.url && img.url.startsWith('blob:')) {
    URL.revokeObjectURL(img.url)
  }
  layoutImages.value.splice(idx, 1)
  emitUpdate()
}

// 发射更新
const emitUpdate = () => {
  emit('update:modelValue', {
    layout_images: layoutImages.value.filter(img => !img.uploading).map(img => ({ url: img.url })),
    layout_analysis: layoutAnalysis.value
  })
}

// 监听文案变化
watch(layoutAnalysis, () => {
  emitUpdate()
})
</script>

<style scoped>
.phase-layout-editor {
  width: 100%;
}

.image-upload-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.uploaded-image-card {
  width: 150px;
  height: 150px;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  border: 1px solid #dcdfe6;
}

.uploaded-image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.uploading-mask {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 12px;
  gap: 4px;
}

.img-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.uploaded-image-card:hover .img-overlay {
  opacity: 1;
}

.delete-btn {
  font-size: 24px;
  color: white;
  cursor: pointer;
}

.upload-trigger {
  width: 150px;
  height: 150px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
}

.upload-trigger:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>
