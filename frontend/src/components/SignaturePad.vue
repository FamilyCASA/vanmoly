<template>
  <div class="signature-pad">
    <div class="signature-header">
      <span class="title">{{ title }}</span>
      <div class="actions">
        <el-button size="small" @click="clear">清空</el-button>
        <el-button size="small" type="primary" @click="save">确认</el-button>
      </div>
    </div>

    <!-- PC端：Canvas手写签名 -->
    <div v-if="!isMiniProgram" class="canvas-wrapper">
      <canvas
        ref="canvasRef"
        class="signature-canvas"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="stopDrawing"
      />
    </div>

    <!-- 微信小程序端：调用原生手写签名 -->
    <div v-else class="miniprogram-wrapper">
      <div class="miniprogram-hint">
        <el-icon><Cellphone /></el-icon>
        <span>请在小程序中完成手写签名</span>
      </div>
      <div v-if="signatureImage" class="signature-preview">
        <img :src="signatureImage" alt="签名预览" />
      </div>
      <el-button type="primary" @click="openMiniProgramSignature">
        打开小程序签名
      </el-button>
    </div>

    <div class="signature-footer">
      <el-button v-if="signatureImage" type="danger" link @click="clear">
        重新签名
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Cellphone } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '手写签名'
  },
  width: {
    type: Number,
    default: 400
  },
  height: {
    type: Number,
    default: 200
  }
})

const emit = defineEmits(['save', 'cancel'])

const canvasRef = ref(null)
const isDrawing = ref(false)
const signatureImage = ref('')
const hasDrawing = ref(false)

// 判断是否在微信小程序环境
const isMiniProgram = computed(() => {
  return window.__wxjs_environment === 'miniprogram' || 
         /miniProgram/i.test(navigator.userAgent)
})

let ctx = null
let lastX = 0
let lastY = 0

onMounted(() => {
  if (!isMiniProgram.value && canvasRef.value) {
    initCanvas()
  }
})

// 初始化Canvas
const initCanvas = () => {
  const canvas = canvasRef.value
  canvas.width = props.width
  canvas.height = props.height

  ctx = canvas.getContext('2d')
  ctx.strokeStyle = '#000'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  // 设置背景为白色
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
}

// 开始绘制
const startDrawing = (e) => {
  isDrawing.value = true
  const { offsetX, offsetY } = getCoordinates(e)
  lastX = offsetX
  lastY = offsetY
}

// 绘制
const draw = (e) => {
  if (!isDrawing.value || !ctx) return

  const { offsetX, offsetY } = getCoordinates(e)

  ctx.beginPath()
  ctx.moveTo(lastX, lastY)
  ctx.lineTo(offsetX, offsetY)
  ctx.stroke()

  lastX = offsetX
  lastY = offsetY
  hasDrawing.value = true
}

// 停止绘制
const stopDrawing = () => {
  isDrawing.value = false
}

// 获取坐标
const getCoordinates = (e) => {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()

  if (e.touches && e.touches.length > 0) {
    return {
      offsetX: e.touches[0].clientX - rect.left,
      offsetY: e.touches[0].clientY - rect.top
    }
  }

  return {
    offsetX: e.offsetX,
    offsetY: e.offsetY
  }
}

// 触摸事件处理
const handleTouchStart = (e) => {
  e.preventDefault()
  startDrawing(e)
}

const handleTouchMove = (e) => {
  e.preventDefault()
  draw(e)
}

// 清空
const clear = () => {
  if (!ctx) return

  const canvas = canvasRef.value
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  hasDrawing.value = false
  signatureImage.value = ''
}

// 保存
const save = () => {
  if (!hasDrawing.value && !signatureImage.value) {
    ElMessage.warning('请先完成签名')
    return
  }

  if (!isMiniProgram.value && canvasRef.value) {
    signatureImage.value = canvasRef.value.toDataURL('image/png')
  }

  emit('save', signatureImage.value)
}

// 微信小程序：打开原生签名
const openMiniProgramSignature = () => {
  // 调用微信小程序JS-SDK
  if (window.wx && window.wx.miniProgram) {
    window.wx.miniProgram.navigateTo({
      url: `/pages/signature/index?type=${props.title}&callback=onSignatureComplete`
    })

    // 监听签名完成事件
    window.onSignatureComplete = (data) => {
      if (data && data.signature) {
        signatureImage.value = data.signature
        emit('save', signatureImage.value)
      }
    }
  } else {
    ElMessage.warning('请在微信小程序中使用此功能')
  }
}

// 外部设置签名图片
const setSignature = (imageUrl) => {
  signatureImage.value = imageUrl
}

// 暴露方法
defineExpose({
  clear,
  setSignature
})
</script>

<style scoped>
.signature-pad {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.signature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.signature-header .title {
  font-weight: 500;
  color: #262626;
}

.canvas-wrapper {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
}

.signature-canvas {
  display: block;
  cursor: crosshair;
  touch-action: none;
}

.miniprogram-wrapper {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
}

.miniprogram-hint {
  color: #8c8c8c;
  margin-bottom: 20px;
}

.miniprogram-hint .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.signature-preview {
  margin: 20px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.signature-preview img {
  max-width: 100%;
  max-height: 150px;
  border: 1px solid #d9d9d9;
  background: #fff;
}

.signature-footer {
  margin-top: 16px;
  text-align: center;
}
</style>
