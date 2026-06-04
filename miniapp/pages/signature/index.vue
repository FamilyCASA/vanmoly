<template>
  <view class="signature-page">
    <view class="header">
      <text class="title">{{ title }}</text>
      <view class="actions">
        <button class="btn btn-default" @click="clear">清空</button>
        <button class="btn btn-primary" @click="save">确认</button>
      </view>
    </view>

    <view class="canvas-container">
      <canvas
        canvas-id="signatureCanvas"
        id="signatureCanvas"
        class="signature-canvas"
        @touchstart="startDrawing"
        @touchmove="draw"
        @touchend="stopDrawing"
        @touchcancel="stopDrawing"
      />
    </view>

    <view class="tips">
      <text>请在上方区域手写签名</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      title: '手写签名',
      ctx: null,
      isDrawing: false,
      lastX: 0,
      lastY: 0
    }
  },

  onLoad(options) {
    if (options.type) {
      this.title = options.type
    }

    // 获取回调函数名
    this.callback = options.callback || 'onSignatureComplete'

    // 初始化Canvas
    this.$nextTick(() => {
      this.initCanvas()
    })
  },

  methods: {
    // 初始化Canvas
    initCanvas() {
      const query = uni.createSelectorQuery().in(this)
      query.select('#signatureCanvas').fields({ node: true, size: true }).exec((res) => {
        const canvas = res[0].node
        const ctx = canvas.getContext('2d')

        // 设置Canvas尺寸
        const systemInfo = uni.getSystemInfoSync()
        canvas.width = systemInfo.windowWidth - 40
        canvas.height = 300

        // 设置画笔样式
        ctx.strokeStyle = '#000'
        ctx.lineWidth = 3
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'

        // 白色背景
        ctx.fillStyle = '#fff'
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        this.canvas = canvas
        this.ctx = ctx
      })
    },

    // 开始绘制
    startDrawing(e) {
      this.isDrawing = true
      const touch = e.touches[0]
      const { x, y } = this.getCoordinates(touch)
      this.lastX = x
      this.lastY = y
    },

    // 绘制
    draw(e) {
      if (!this.isDrawing || !this.ctx) return

      const touch = e.touches[0]
      const { x, y } = this.getCoordinates(touch)

      this.ctx.beginPath()
      this.ctx.moveTo(this.lastX, this.lastY)
      this.ctx.lineTo(x, y)
      this.ctx.stroke()

      this.lastX = x
      this.lastY = y
    },

    // 停止绘制
    stopDrawing() {
      this.isDrawing = false
    },

    // 获取坐标
    getCoordinates(touch) {
      return {
        x: touch.x,
        y: touch.y
      }
    },

    // 清空
    clear() {
      if (!this.ctx || !this.canvas) return

      this.ctx.fillStyle = '#fff'
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height)
    },

    // 保存
    save() {
      if (!this.canvas) return

      uni.canvasToTempFilePath({
        canvasId: 'signatureCanvas',
        success: (res) => {
          // 将签名图片转为base64
          uni.getFileSystemManager().readFile({
            filePath: res.tempFilePath,
            encoding: 'base64',
            success: (fileRes) => {
              const base64Image = `data:image/png;base64,${fileRes.data}`

              // 调用回调函数返回数据
              const pages = getCurrentPages()
              const prevPage = pages[pages.length - 2]

              if (prevPage && prevPage.$vm && prevPage.$vm[this.callback]) {
                prevPage.$vm[this.callback]({
                  signature: base64Image,
                  timestamp: Date.now()
                })
              }

              // 返回上一页
              uni.navigateBack()
            },
            fail: (err) => {
              uni.showToast({
                title: '保存失败',
                icon: 'none'
              })
            }
          })
        },
        fail: (err) => {
          uni.showToast({
            title: '保存失败',
            icon: 'none'
          })
        }
      }, this)
    }
  }
}
</script>

<style lang="scss" scoped>
.signature-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20rpx;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;

  .title {
    font-size: 32rpx;
    font-weight: 500;
    color: #262626;
  }

  .actions {
    display: flex;
    gap: 16rpx;
  }
}

.btn {
  padding: 16rpx 32rpx;
  font-size: 28rpx;
  border-radius: 8rpx;
  border: none;

  &-default {
    background: #f5f5f5;
    color: #595959;
  }

  &-primary {
    background: #8B4513;
    color: #fff;
  }
}

.canvas-container {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.signature-canvas {
  width: 100%;
  height: 600rpx;
  border: 2rpx dashed #d9d9d9;
  border-radius: 8rpx;
  background: #fff;
}

.tips {
  text-align: center;
  padding: 40rpx;

  text {
    font-size: 28rpx;
    color: #8c8c8c;
  }
}
</style>
