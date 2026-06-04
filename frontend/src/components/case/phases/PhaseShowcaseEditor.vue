<template>
  <div class="phase-showcase-editor">
    <el-form label-position="top">
      <!-- 一级标题 -->
      <el-form-item label="一级标题（黑体大字）">
        <el-input 
          v-model="showcaseTitle1" 
          placeholder="如：现代简约"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 二级标题 -->
      <el-form-item label="二级标题">
        <el-input 
          v-model="showcaseTitle2" 
          placeholder="如：办公.手办.阅读.绘画.绿植"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 设计意向图（最多10张） -->
      <el-form-item label="设计意向图（最多10张）">
        <div class="image-upload-grid">
          <div
            v-for="(img, idx) in showcaseImages"
            :key="idx"
            class="uploaded-image-card"
          >
            <img :src="img.url || img" alt="意向图" />
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
            v-if="showcaseImages.length < 10" 
            class="upload-trigger" 
            @click="triggerUpload"
          >
            <el-icon><Plus /></el-icon>
            <span>上传意向图</span>
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
      
      <!-- 中文文案 -->
      <el-form-item label="中文文案">
        <el-input
          v-model="showcaseTextCn"
          type="textarea"
          :rows="4"
          placeholder="让空间留白，以光影塑形..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 英文文案 -->
      <el-form-item label="英文文案">
        <el-input
          v-model="showcaseTextEn"
          type="textarea"
          :rows="4"
          placeholder="Leave space in blankness, let light and shadow shape the form..."
          maxlength="800"
          show-word-limit
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
const showcaseTitle1 = ref('')
const showcaseTitle2 = ref('')
const showcaseImages = ref([])
const showcaseTextCn = ref('')
const showcaseTextEn = ref('')

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    showcaseTitle1.value = newVal.showcase_title1 || ''
    showcaseTitle2.value = newVal.showcase_title2 || ''
    showcaseImages.value = newVal.showcase_images || []
    showcaseTextCn.value = newVal.showcase_text_cn || ''
    showcaseTextEn.value = newVal.showcase_text_en || ''
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
  if (showcaseImages.value.length >= 10) {
    ElMessage.warning('最多上传10张意向图')
    return false
  }
  // 立即显示本地预览
  const localUrl = URL.createObjectURL(file)
  showcaseImages.value.push({ url: localUrl, uploading: true })
  emitUpdate()
  return true
}

const handleUploadSuccess = (res) => {
  // 兼容多种返回格式：后端api_response返回 { data: { file_url } }
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const uploadingIdx = showcaseImages.value.findIndex(img => img.uploading)
    if (uploadingIdx >= 0) {
      URL.revokeObjectURL(showcaseImages.value[uploadingIdx].url)
      showcaseImages.value[uploadingIdx] = { url, uploading: false }
    } else {
      showcaseImages.value.push({ url, uploading: false })
    }
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const uploadingIdx = showcaseImages.value.findIndex(img => img.uploading)
  if (uploadingIdx >= 0) {
    URL.revokeObjectURL(showcaseImages.value[uploadingIdx].url)
    showcaseImages.value.splice(uploadingIdx, 1)
    emitUpdate()
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

const removeImage = (idx) => {
  const img = showcaseImages.value[idx]
  if (img && img.url && img.url.startsWith('blob:')) {
    URL.revokeObjectURL(img.url)
  }
  showcaseImages.value.splice(idx, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    showcase_title1: showcaseTitle1.value,
    showcase_title2: showcaseTitle2.value,
    showcase_images: showcaseImages.value.filter(img => !img.uploading).map(img => ({ url: img.url })),
    showcase_text_cn: showcaseTextCn.value,
    showcase_text_en: showcaseTextEn.value
  })
}

// 监听所有字段变化
watch([showcaseTitle1, showcaseTitle2, showcaseTextCn, showcaseTextEn], () => {
  emitUpdate()
})
</script>

<style scoped>
.phase-showcase-editor {
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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
