Page({
  data: {
    backendStatus: '检测中...'
  },

  onLoad() {
    this.checkBackend()
  },

  checkBackend() {
    wx.request({
      url: 'http://127.0.0.1:5000/api/v3/auth/login',
      method: 'POST',
      data: {
        username: 'admin',
        password: 'admin123'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ backendStatus: '✅ 已连接' })
        } else {
          this.setData({ backendStatus: '❌ 响应异常' })
        }
      },
      fail: () => {
        this.setData({ backendStatus: '❌ 无法连接' })
      }
    })
  },

  goToSignature() {
    wx.navigateTo({
      url: '/pages/signature/index'
    })
  }
})
