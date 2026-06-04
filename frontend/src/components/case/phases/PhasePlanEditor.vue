<template>
  <div class="phase-plan-editor">
    <el-form label-position="top">
      <!-- 平面规划图 -->
      <el-form-item label="平面规划图">
        <div class="plan-image-area">
          <div v-if="planImage" class="preview-area">
            <img :src="planImage" alt="平面规划图" />
            <div v-if="isUploading" class="uploading-mask">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>上传中...</span>
            </div>
            <div v-else class="img-overlay">
              <el-button type="primary" size="small" @click="triggerUpload">
                替换图片
              </el-button>
              <el-button type="danger" size="small" @click="removeImage">
                删除
              </el-button>
            </div>
          </div>
          <div v-else class="upload-area" @click="triggerUpload">
            <el-icon><Plus /></el-icon>
            <span>上传平面规划图</span>
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
        <div class="upload-tip">右边图片，左边规划文案（家居杂志风格）</div>
      </el-form-item>
      
      <!-- 规划文案 -->
      <el-form-item label="规划文案">
        <RichTextEditor 
          v-model="planText" 
          placeholder="请输入规划文案..."
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading } from '@element-plus/icons-vue'
import RichTextEditor from '@/components/RichTextEditor.vue'

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
const planImage = ref('')
const planText = ref('')
const isUploading = ref(false)

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    planImage.value = newVal.plan_image || ''
    planText.value = newVal.plan_text || ''
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
  // 立即显示本地预览
  const localUrl = URL.createObjectURL(file)
  planImage.value = localUrl
  isUploading.value = true
  return true
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    // 释放本地预览URL
    if (planImage.value && planImage.value.startsWith('blob:')) {
      URL.revokeObjectURL(planImage.value)
    }
    planImage.value = url
    isUploading.value = false
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  if (planImage.value && planImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(planImage.value)
    planImage.value = ''
  }
  isUploading.value = false
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

const removeImage = () => {
  if (planImage.value && planImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(planImage.value)
  }
  planImage.value = ''
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    plan_image: planImage.value,
    plan_text: planText.value
  })
}

watch(planText, () => {
  emitUpdate()
})
</script>

<style scoped>
.phase-plan-editor {
  width: 100%;
}

.plan-image-area {
  width: 100%;
}

.preview-area {
  position: relative;
  width: 400px;
  height: 300px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.preview-area img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f5f7fa;
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
  gap: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-area:hover .img-overlay {
  opacity: 1;
}

.upload-area {
  width: 400px;
  height: 300px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
}

.upload-area:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
