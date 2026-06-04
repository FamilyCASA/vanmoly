Page({
  data: {
    hasDrawn: false,
    signatureImage: '',
    quoteId: null,
    signType: 'customer' // customer, planner, manager
  },
  
  ctx: null,
  isDrawing: false,
  lastX: 0,
  lastY: 0,

  onLoad(options) {
    // 获取传入的参数
    if (options.quote_id) {
      this.setData({
        quoteId: options.quote_id,
        signType: options.type || 'customer'
      })
    }
  },

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
        
        // 如果有 quoteId，则上传到服务器
        if (this.data.quoteId) {
          this.uploadSignature(res.tempFilePath)
        } else {
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          })
        }
      },
      fail: (err) => {
        console.error('保存失败:', err)
        wx.showToast({
          title: '保存失败',
          icon: 'none'
        })
      }
    }, this)
  },

  // 上传签名到服务器
  uploadSignature(filePath) {
    wx.showLoading({ title: '上传中...' })
    
    // 先上传图片
    wx.uploadFile({
      url: 'http://127.0.0.1:5000/api/v3/upload/image',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': 'Bearer ' + wx.getStorageSync('token')
      },
      success: (uploadRes) => {
        const data = JSON.parse(uploadRes.data)
        
        if (data.url) {
          // 更新报价签名
          this.updateQuoteSignature(data.url)
        } else {
          wx.hideLoading()
          wx.showToast({
            title: '上传失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
      }
    })
  },

  // 更新报价签名
  updateQuoteSignature(imageUrl) {
    const signField = {
      'customer': 'signature_customer',
      'planner': 'signature_planner',
      'manager': 'signature_manager'
    }[this.data.signType]

    wx.request({
      url: `http://127.0.0.1:5000/api/v3/quotes/${this.data.quoteId}/signature`,
      method: 'PUT',
      header: {
        'Authorization': 'Bearer ' + wx.getStorageSync('token'),
        'Content-Type': 'application/json'
      },
      data: {
        [signField]: imageUrl
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200) {
          wx.showToast({
            title: '签名成功',
            icon: 'success'
          })
          // 返回上一页
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        } else {
          wx.showToast({
            title: '签名失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '签名失败',
          icon: 'none'
        })
      }
    })
  }
})