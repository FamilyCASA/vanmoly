Page({
  data: {
    stats: {
      customers: 0,
      quotes: 0,
      orders: 0,
      revenue: 0
    },
    backendStatus: '检测中...',
    dbStatus: '检测中...'
  },

  onLoad() {
    this.checkSystemStatus()
    this.loadStats()
  },

  onShow() {
    this.checkSystemStatus()
    this.loadStats()
  },

  // 检查系统状态
  checkSystemStatus() {
    wx.request({
      url: 'http://127.0.0.1:5000/',
      method: 'GET',
      timeout: 5000,
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            backendStatus: '正常',
            dbStatus: '正常'
          })
        } else {
          this.setData({
            backendStatus: '异常',
            dbStatus: '未知'
          })
        }
      },
      fail: () => {
        this.setData({
          backendStatus: '离线',
          dbStatus: '未知'
        })
      }
    })
  },

  // 加载统计数据
  loadStats() {
    // 模拟数据
    this.setData({
      stats: {
        customers: 128,
        quotes: 256,
        orders: 32,
        revenue: '128.5万'
      }
    })

    // 实际 API 调用：
    // wx.request({
    //   url: 'http://127.0.0.1:5000/api/v3/admin/dashboard',
    //   header: {
    //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
    //   },
    //   success: (res) => {
    //     if (res.statusCode === 200) {
    //       this.setData({ stats: res.data })
    //     }
    //   }
    // })
  },

  // 跳转到 Web 端页面
  goToWeb(e) {
    const path = e.currentTarget.dataset.path
    // 复制 Web 端链接到剪贴板，提示用户在浏览器中打开
    wx.setClipboardData({
      data: `http://localhost:3000/#${path}`,
      success: () => {
        wx.showModal({
          title: '提示',
          content: '链接已复制到剪贴板，请在浏览器中打开 Web 管理后台',
          showCancel: false
        })
      }
    })
  },

  // 打开 Web 管理后台
  openWebAdmin() {
    wx.setClipboardData({
      data: 'http://localhost:3000',
      success: () => {
        wx.showModal({
          title: '提示',
          content: 'Web 后台地址已复制到剪贴板，请在浏览器中打开',
          showCancel: false
        })
      }
    })
  }
})