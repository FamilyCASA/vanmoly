Page({
  data: {
    hasDrawn: false,
    signatureImage: ''
  },
  
  ctx: null,
  isDrawing: false,
  lastX: 0,
  lastY: 0,

  onReady() {
    this.initCanvas()
  },

  initCanvas() {
    // 使用旧版 canvas API
    this.ctx = wx.createCanvasContext('signatureCanvas', this)
    
    // 设置画笔样式
    this.ctx.setStrokeStyle('#000000')
    this.ctx.setLineWidth(3)
    this.ctx.setLineCap('round')
    this.ctx.setLineJoin('round')
  },

  onTouchStart(e) {
    if (!this.ctx) return
    
    const touch = e.touches[0]
    this.lastX = touch.x
    this.lastY = touch.y
    
    this.ctx.beginPath()
    this.ctx.moveTo(this.lastX, this.lastY)
    this.isDrawing = true
  },

  onTouchMove(e) {
    if (!this.isDrawing || !this.ctx) return
    
    const touch = e.touches[0]
    const x = touch.x
    const y = touch.y
    
    this.ctx.lineTo(x, y)
    this.ctx.stroke()
    this.ctx.draw(true)
    
    this.lastX = x
    this.lastY = y
    
    if (!this.data.hasDrawn) {
      this.setData({ hasDrawn: true })
    }
  },

  onTouchEnd() {
    this.isDrawing = false
  },

  clearCanvas() {
    if (!this.ctx) return
    
    this.ctx.clearRect(0, 0, 1000, 1000)
    this.ctx.draw()
    
    this.setData({ 
      hasDrawn: false,
      signatureImage: ''
    })
  },

  saveSignature() {
    if (!this.data.hasDrawn) {
      wx.showToast({
        title: '请先签名',
        icon: 'none'
      })
      return
    }
    
    wx.canvasToTempFilePath({
      canvasId: 'signatureCanvas',
      success: (res) => {
        this.setData({
          signatureImage: res.tempFilePath
        })
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
      },
      fail: (err) => {
        console.error('保存失败:', err)
        wx.showToast({
          title: '保存失败',
          icon: 'none'
        })
      }
    }, this)
  }
})
