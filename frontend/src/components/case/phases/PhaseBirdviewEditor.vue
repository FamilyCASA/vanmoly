<template>
  <div class="phase-birdview-editor">
    <el-form label-position="top">
      <!-- 鸟瞰图上传（最多4张） -->
      <el-form-item label="鸟瞰图（最多4张）">
        <div class="image-upload-grid">
          <div
            v-for="(img, idx) in birdviewImages"
            :key="idx"
            class="uploaded-image-card"
          >
            <img :src="img.url || img" alt="鸟瞰图" />
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
          <div 
            v-if="birdviewImages.length < 4" 
            class="upload-trigger" 
            @click="triggerUpload"
          >
            <el-icon><Plus /></el-icon>
            <span>上传鸟瞰图</span>
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
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Close, Loading } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const birdviewImages = ref([])

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    birdviewImages.value = newVal.birdview_images || []
  }
}, { immediate: true })

const triggerUpload = () => {
  uploadRef.value?.$el?.querySelector('input')?.click()
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (birdviewImages.value.length >= 4) {
    ElMessage.warning('最多上传4张鸟瞰图')
    return false
  }
  // 立即显示本地预览
  const localUrl = URL.createObjectURL(file)
  birdviewImages.value.push({ url: localUrl, uploading: true })
  emitUpdate()
  return true
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const uploadingIdx = birdviewImages.value.findIndex(img => img.uploading)
    if (uploadingIdx >= 0) {
      URL.revokeObjectURL(birdviewImages.value[uploadingIdx].url)
      birdviewImages.value[uploadingIdx] = { url, uploading: false }
    } else {
      birdviewImages.value.push({ url, uploading: false })
    }
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const uploadingIdx = birdviewImages.value.findIndex(img => img.uploading)
  if (uploadingIdx >= 0) {
    URL.revokeObjectURL(birdviewImages.value[uploadingIdx].url)
    birdviewImages.value.splice(uploadingIdx, 1)
    emitUpdate()
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

const removeImage = (idx) => {
  const img = birdviewImages.value[idx]
  if (img && img.url && img.url.startsWith('blob:')) {
    URL.revokeObjectURL(img.url)
  }
  birdviewImages.value.splice(idx, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    birdview_images: birdviewImages.value.filter(img => !img.uploading).map(img => ({ url: img.url }))
  })
}
</script>

<style scoped>
.phase-birdview-editor {
  width: 100%;
}

.image-upload-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.uploaded-image-card {
  width: 200px;
  height: 200px;
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
  width: 200px;
  height: 200px;
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
