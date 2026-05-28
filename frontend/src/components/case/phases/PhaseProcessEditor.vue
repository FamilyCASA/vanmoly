<template>
  <div class="phase-process-editor">
    <el-form label-position="top">
      <!-- 工法图上传（最多20张） -->
      <el-form-item label="工法展示图（最多20张）">
        <div class="image-upload-grid">
          <div
            v-for="(img, idx) in processGallery"
            :key="idx"
            class="uploaded-image-card"
          >
            <img :src="img.url || img" alt="工法图" />
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
            v-if="processGallery.length < 20"
            class="upload-trigger"
            @click="triggerUpload"
          >
            <el-icon><Plus /></el-icon>
            <span>上传工法图</span>
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
        <div class="upload-tip">展示水电改造、防水施工、墙面处理、吊顶工艺等施工细节</div>
      </el-form-item>

      <!-- 工艺说明 -->
      <el-form-item label="工艺说明">
        <RichTextEditor
          v-model="processDesc"
          placeholder="请输入工艺说明，如施工规范、验收标准、特殊工艺要求等..."
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

const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const processGallery = ref([])
const processDesc = ref('')

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    processGallery.value = newVal.process_gallery || []
    processDesc.value = newVal.process_desc || ''
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
  if (processGallery.value.length >= 20) {
    ElMessage.warning('最多上传20张工法图')
    return false
  }
  const localUrl = URL.createObjectURL(file)
  processGallery.value.push({ url: localUrl, uploading: true })
  emitUpdate()
  return true
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const uploadingIdx = processGallery.value.findIndex(img => img.uploading)
    if (uploadingIdx >= 0) {
      URL.revokeObjectURL(processGallery.value[uploadingIdx].url)
      processGallery.value[uploadingIdx] = { url, uploading: false }
    } else {
      processGallery.value.push({ url, uploading: false })
    }
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const uploadingIdx = processGallery.value.findIndex(img => img.uploading)
  if (uploadingIdx >= 0) {
    URL.revokeObjectURL(processGallery.value[uploadingIdx].url)
    processGallery.value.splice(uploadingIdx, 1)
    emitUpdate()
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

const removeImage = (idx) => {
  const img = processGallery.value[idx]
  if (img && img.url && img.url.startsWith('blob:')) {
    URL.revokeObjectURL(img.url)
  }
  processGallery.value.splice(idx, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    process_gallery: processGallery.value.filter(img => !img.uploading).map(img => ({ url: img.url })),
    process_desc: processDesc.value
  })
}

watch(processDesc, () => {
  emitUpdate()
})
</script>

<style scoped>
.phase-process-editor {
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

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
