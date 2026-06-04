<template>
  <div class="cropper-upload-wrapper">
    <!-- 当前显示 + 点击触发 -->
    <div class="cropper-trigger" @click="showDialog = true">
      <video v-if="modelValue && isVideo(modelValue)" :src="modelValue" class="trigger-media" />
      <img v-else-if="modelValue" :src="modelValue" class="trigger-media" />
      <div v-else class="trigger-placeholder">
        <el-icon class="trigger-icon"><Plus /></el-icon>
        <span class="trigger-text">{{ placeholder }}</span>
      </div>
      <div class="trigger-overlay">
        <el-icon><EditPen /></el-icon>
      </div>
    </div>

    <!-- 换图/删除按钮 -->
    <div v-if="modelValue" class="trigger-actions">
      <el-button size="small" link type="primary" @click.stop="showDialog = true">换图</el-button>
      <el-button size="small" link type="danger" @click.stop="handleRemove">删除</el-button>
    </div>

    <!-- 上传/裁剪弹窗 -->
    <el-dialog
      v-model="showDialog"
      title="上传主图"
      width="760px"
      :close-on-click-modal="false"
      @opened="onDialogOpened"
      @closed="onDialogClosed"
    >
      <!-- 类型切换 -->
      <div class="mode-tabs">
        <el-radio-group v-model="mode" size="default">
          <el-radio-button value="upload">本地上传</el-radio-button>
          <el-radio-button value="url">链接地址</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 模式1：拖拽上传 -->
      <div v-if="mode === 'upload'" class="upload-area"
        :class="{ 'is-dragover': isDragover }"
        @dragover.prevent="isDragover = true"
        @dragleave="isDragover = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInputRef"
          type="file"
          :accept="accept"
          style="display:none"
          @change="handleFileChange"
        />
        <div v-if="!cropperOption.img" class="upload-placeholder">
          <el-icon class="upload-icon"><Upload /></el-icon>
          <p class="upload-hint">拖拽图片/视频到此处，或 <span class="link">点击选择</span></p>
          <p class="upload-formats">支持：JPG、PNG、WebP、GIF、MP4、WebM</p>
        </div>
        <div v-else class="upload-ready">
          <el-icon class="upload-ready-icon"><Picture /></el-icon>
          <p class="upload-ready-text">已选择图片，可拖入新文件替换</p>
          <el-button size="small" @click.stop="clearCrop">重新选择</el-button>
        </div>
      </div>

      <!-- 模式2：URL输入 -->
      <div v-if="mode === 'url'" class="url-area">
        <el-input
          v-model="urlInput"
          placeholder="请输入图片或视频链接，如 https://www.nio.cn/xxx.mp4"
          clearable
          @keyup.enter="handleUrlConfirm"
        >
          <template #prepend>链接</template>
        </el-input>
        <div v-if="urlInput" class="url-preview">
          <video v-if="isVideo(urlInput)" :src="urlInput" class="url-media" controls @error="urlError = true" @load="urlError = false" />
          <img v-else :src="urlInput" class="url-media" @error="urlError = true" @load="urlError = false" />
          <p v-if="urlError" class="url-error">链接无效或无法加载</p>
        </div>
      </div>

      <!-- 裁剪区：vue-cropper -->
      <div v-show="showCropper" class="cropper-section">
        <div class="cropper-toolbar">
          <span class="toolbar-label">裁剪比例：</span>
          <el-radio-group v-model="ratioLabel" size="small" @change="onRatioChange">
            <el-radio-button value="free">自由</el-radio-button>
            <el-radio-button value="1:1">1:1</el-radio-button>
            <el-radio-button value="16:9">16:9</el-radio-button>
            <el-radio-button value="4:3">4:3</el-radio-button>
          </el-radio-group>
          <div class="toolbar-right">
            <el-button size="small" @click="rotateLeft" title="向左旋转">
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
            <el-button size="small" @click="rotateRight" title="向右旋转">
              <el-icon><RefreshRight /></el-icon>
            </el-button>
            <el-button size="small" @click="resetCrop" title="重置">重置</el-button>
          </div>
        </div>
        <!-- vue-cropper 容器：必须设明确宽高 -->
        <div class="cropper-box">
          <VueCropper
            ref="vueCropperRef"
            :img="cropperOption.img"
            :outputSize="cropperOption.outputSize"
            :outputType="cropperOption.outputType"
            :info="false"
            :canScale="true"
            :autoCrop="true"
            :autoCropWidth="cropperOption.autoCropWidth"
            :autoCropHeight="cropperOption.autoCropHeight"
            :fixed="cropperOption.fixed"
            :fixedNumber="cropperOption.fixedNumber"
            :centerBox="true"
            :mode="cropperOption.mode"
            :full="false"
            :maxImgSize="2048"
            @realTime="onRealTime"
          />
        </div>
        <!-- 实时预览 -->
        <div v-if="previewResult.url" class="cropper-preview">
          <p class="preview-label">预览效果：</p>
          <div class="preview-box" :style="previewResult.box">
            <img :src="previewResult.url" :style="previewResult.img" />
          </div>
        </div>
      </div>

      <!-- 视频预览（URL模式选择了视频） -->
      <div v-if="mode === 'url' && urlInput && isVideo(urlInput) && !urlError" class="video-preview">
        <video :src="urlInput" class="url-media" controls />
      </div>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :disabled="!canSave" :loading="uploading" @click="handleConfirm">
          确认{{ mode === 'url' ? '链接' : (isVideoFile ? '视频' : '图片') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, Upload, EditPen, Picture, RefreshLeft, RefreshRight } from '@element-plus/icons-vue'
import 'vue-cropper/dist/index.css'
import { VueCropper } from 'vue-cropper'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '上传主图' },
  accept: { type: String, default: 'image/jpeg,image/png,image/webp,image/gif,video/mp4,video/webm' },
  aspectRatio: { type: Number, default: 0 }, // 0=自由
})

const emit = defineEmits(['update:modelValue'])

// 状态
const showDialog = ref(false)
const mode = ref('upload')
const isDragover = ref(false)
const fileInputRef = ref(null)
const vueCropperRef = ref(null)
const urlInput = ref('')
const urlError = ref(false)
const uploading = ref(false)
const ratioLabel = ref('free')
const previewResult = ref({ url: '', box: {}, img: {} })

// 裁剪配置
const cropperOption = ref({
  img: '',
  outputSize: 0.92,
  outputType: 'jpeg',
  fixed: false,
  fixedNumber: [1, 1],
  autoCropWidth: 400,
  autoCropHeight: 400,
  mode: 'contain',
})

const isVideoFile = computed(() => {
  if (!cropperOption.value.img) return false
  return /\.(mp4|webm|mov|avi)$/i.test(cropperOption.value.img) || cropperOption.value.img.startsWith('data:video/')
})

const showCropper = computed(() => {
  return mode.value === 'upload' && cropperOption.value.img && !isVideoFile.value
})

const canSave = computed(() => {
  if (mode.value === 'url') return urlInput.value.trim() && !urlError.value
  return !!cropperOption.value.img
})

// 辅助
const isVideo = (src) => {
  if (!src) return false
  return /\.(mp4|webm|mov|avi)$/i.test(src)
}

// 裁剪比例切换
const ratioMap = {
  'free': { fixed: false, fixedNumber: [1, 1] },
  '1:1': { fixed: true, fixedNumber: [1, 1] },
  '16:9': { fixed: true, fixedNumber: [16, 9] },
  '4:3': { fixed: true, fixedNumber: [4, 3] },
}

const onRatioChange = (label) => {
  const cfg = ratioMap[label]
  if (!cfg) return
  cropperOption.value.fixed = cfg.fixed
  cropperOption.value.fixedNumber = cfg.fixedNumber
}

// 旋转
const rotateLeft = () => vueCropperRef.value?.rotateLeft()
const rotateRight = () => vueCropperRef.value?.rotateRight()
const resetCrop = () => vueCropperRef.value?.refresh()

// 实时预览
const onRealTime = (data) => {
  previewResult.value = {
    url: data.url,
    box: {
      width: data.w + 'px',
      height: data.h + 'px',
      overflow: 'hidden',
      margin: 0,
    },
    img: data.img,
  }
}

// 文件处理
const triggerFileInput = () => fileInputRef.value?.click()

const handleFileChange = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  loadFile(file)
  e.target.value = ''
}

const handleDrop = (e) => {
  isDragover.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  loadFile(file)
}

const loadFile = (file) => {
  // 视频直接上传
  if (file.type.startsWith('video/')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadBlob(e.target.result, file.name || 'video.mp4', file.type)
    }
    reader.readAsDataURL(file)
    return
  }
  // 图片转 base64 给 vue-cropper
  const reader = new FileReader()
  reader.onload = (e) => {
    cropperOption.value.img = e.target.result
  }
  reader.readAsDataURL(file)
}

const clearCrop = () => {
  cropperOption.value.img = ''
  previewResult.value = { url: '', box: {}, img: {} }
  if (fileInputRef.value) fileInputRef.value.value = ''
}

// URL 确认（直接赋值，无需上传）
const handleUrlConfirm = () => {
  if (!urlInput.value.trim() || urlError.value) return
  emit('update:modelValue', urlInput.value.trim())
  showDialog.value = false
}

// 上传 blob/dataURL
const uploadBlob = async (dataUrlOrBlob, name, mimeType) => {
  uploading.value = true
  try {
    let blob
    if (dataUrlOrBlob instanceof Blob) {
      blob = dataUrlOrBlob
    } else if (typeof dataUrlOrBlob === 'string') {
      if (dataUrlOrBlob.startsWith('data:')) {
        const b = dataURLToBlob(dataUrlOrBlob, mimeType)
        if (b) blob = b
      }
      if (!blob) {
        // Fallback: fetch as blob URL
        const resp = await fetch(dataUrlOrBlob)
        blob = await resp.blob()
      }
    }
    if (!blob) throw new Error('无法构建上传文件')
    const res = await fetch('/api/v3/upload', {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: createFormData(blob, name),
    })
    const json = await res.json()
    if (json.code === 200 || json.code === 0) {
      let url = json.data?.file_url || json.url || ''
      // 补全 /api/v3 前缀（后端 file_url 返回 /upload/...，实际路径是 /api/v3/upload/...）
      if (url && !url.startsWith('http') && !url.startsWith('/api')) {
        url = '/api/v3' + url
      }
      if (url) {
        emit('update:modelValue', url)
        showDialog.value = false
        resetAll()
      }
    }
  } catch (e) {
    console.error('上传失败', e)
  } finally {
    uploading.value = false
  }
}

const createFormData = (blob, name) => {
  const form = new FormData()
  form.append('file', blob, name)
  return form
}

const dataURLToBlob = (dataUrl, mimeType) => {
  try {
    const arr = dataUrl.split(',')
    const mime = mimeType || (arr[0].match(/:(.*?);/)?.[1] || 'image/jpeg')
    const bstr = atob(arr[1])
    let n = bstr.length
    const u8 = new Uint8Array(n)
    while (n--) u8[n] = bstr.charCodeAt(n)
    return new Blob([u8], { type: mime })
  } catch (e) {
    // Fallback: URL -> Blob
    return null
  }
}

// 确认（图片裁剪上传）
const handleConfirm = async () => {
  if (mode.value === 'url') {
    if (!urlInput.value.trim() || urlError.value) return
    emit('update:modelValue', urlInput.value.trim())
    showDialog.value = false
    return
  }
  if (isVideoFile.value) {
    // 视频从 dataURL 重新提取 blob 上传
    await uploadBlob(cropperOption.value.img, 'video.mp4', 'video/mp4')
    return
  }
  // 图片裁剪上传
  uploading.value = true
  vueCropperRef.value?.getCropBlob((blob) => {
    uploadBlob(URL.createObjectURL(blob), 'crop.jpg', 'image/jpeg')
  })
}

// 弹窗生命周期
const onDialogOpened = () => {
  // 已有图片时激活裁剪器
  if (cropperOption.value.img && !isVideoFile.value) {
    setTimeout(() => vueCropperRef.value?.refresh(), 100)
  }
}

const onDialogClosed = () => {
  resetAll()
}

const resetAll = () => {
  cropperOption.value.img = ''
  urlInput.value = ''
  urlError.value = false
  uploading.value = false
  previewResult.value = { url: '', box: {}, img: {} }
  if (fileInputRef.value) fileInputRef.value.value = ''
}

// 删除
const handleRemove = () => {
  emit('update:modelValue', '')
  resetAll()
}
</script>

<style scoped>
.cropper-upload-wrapper { display: inline-block; }

/* 触发区 */
.cropper-trigger {
  position: relative;
  width: 120px;
  height: 120px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  transition: border-color 0.2s;
}
.cropper-trigger:hover { border-color: #8B5A2B; }
.cropper-trigger:hover .trigger-overlay { opacity: 1; }

.trigger-media { width: 100%; height: 100%; object-fit: cover; }

.trigger-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #999;
}
.trigger-icon { font-size: 28px; color: #bfbfbf; }
.trigger-text { font-size: 12px; color: #999; text-align: center; }

.trigger-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  opacity: 0;
  transition: opacity 0.2s;
}

.trigger-actions { display: flex; gap: 8px; margin-top: 6px; }

/* 弹窗 */
.mode-tabs { margin-bottom: 14px; }

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}
.upload-area:hover,
.upload-area.is-dragover {
  border-color: #8B5A2B;
  background: #fdf5f0;
}

.upload-placeholder { text-align: center; padding: 20px; color: #999; }
.upload-icon { font-size: 36px; color: #bfbfbf; margin-bottom: 8px; }
.upload-hint { margin: 0 0 4px; font-size: 14px; }
.upload-hint .link { color: #8B5A2B; font-weight: 500; }
.upload-formats { margin: 0; font-size: 12px; color: #bbb; }

.upload-ready { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px; color: #67c23a; }
.upload-ready-icon { font-size: 32px; color: #67c23a; }
.upload-ready-text { margin: 0; font-size: 13px; color: #67c23a; }

/* URL 模式 */
.url-area { display: flex; flex-direction: column; gap: 12px; }
.url-preview { margin-top: 4px; }
.url-media { width: 100%; max-height: 240px; border-radius: 6px; object-fit: contain; background: #000; }
.url-error { color: #f56c6c; font-size: 12px; margin: 4px 0 0; }

/* 裁剪区 */
.cropper-section { margin-top: 14px; border-top: 1px solid #eee; padding-top: 14px; }
.cropper-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #666;
  flex-wrap: wrap;
}
.toolbar-label { white-space: nowrap; }
.toolbar-right { margin-left: auto; display: flex; gap: 6px; }

/* vue-cropper 容器：关键！必须明确宽高 */
.cropper-box {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

/* 实时预览 */
.cropper-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}
.preview-label { font-size: 12px; color: #999; white-space: nowrap; margin: 0; }
.preview-box {
  border: 1px solid #ddd;
  overflow: hidden;
  border-radius: 4px;
  background: #fff;
}
.preview-box img { display: block; }

/* 视频预览 */
.video-preview { margin-top: 12px; }
.url-media { width: 100%; max-height: 300px; border-radius: 6px; object-fit: contain; background: #000; }
</style>
