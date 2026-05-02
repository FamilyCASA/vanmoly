Page({
  data: {
    userInfo: {},
    isLoggedIn: false,
    isStaff: false,
    stats: {
      quotes: 0,
      orders: 0,
      completed: 0
    }
  },

  onLoad() {
    this.checkLoginStatus()
  },

  onShow() {
    if (this.data.isLoggedIn) {
      this.loadUserStats()
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo,
        isStaff: userInfo.is_staff || false
      })
      this.loadUserStats()
    }
  },

  // 登录
  login() {
    wx.login({
      success: (res) => {
        if (res.code) {
          // 调用后端登录接口
          wx.request({
            url: 'http://127.0.0.1:5000/api/v3/auth/wechat-login',
            method: 'POST',
            data: {
              code: res.code
            },
            success: (loginRes) => {
              if (loginRes.statusCode === 200) {
                wx.setStorageSync('token', loginRes.data.token)
                wx.setStorageSync('userInfo', loginRes.data.user)
                this.setData({
                  isLoggedIn: true,
                  userInfo: loginRes.data.user,
                  isStaff: loginRes.data.user.is_staff || false
                })
                this.loadUserStats()
              } else {
                wx.showToast({
                  title: '登录失败',
                  icon: 'none'
                })
              }
            }
          })
        }
      }
    })
  },

  // 加载用户统计数据
  loadUserStats() {
    // 模拟数据
    this.setData({
      stats: {
        quotes: 3,
        orders: 1,
        completed: 2
      }
    })

    // 实际 API 调用：
    // wx.request({
    //   url: 'http://127.0.0.1:5000/api/v3/user/stats',
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

  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          this.setData({
            isLoggedIn: false,
            isStaff: false,
            userInfo: {},
            stats: { quotes: 0, orders: 0, completed: 0 }
          })
        }
      }
    })
  },

  // 跳转到我的报价
  goToQuotes() {
    if (!this.data.isLoggedIn) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    wx.navigateTo({ url: '/pages/quote/index' })
  },

  // 跳转到项目进度
  goToWorkflow() {
    if (!this.data.isLoggedIn) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    wx.showToast({ title: '功能开发中', icon: 'none' })
  },

  // 跳转到签名
  goToSignature() {
    wx.navigateTo({ url: '/pages/signature/index' })
  },

  // 跳转到后台管理
  goToAdmin() {
    wx.navigateTo({ url: '/pages/admin/index' })
  },

  // 跳转到客户管理
  goToCustomers() {
    wx.showToast({ title: '请在Web端使用', icon: 'none' })
  },

  // 跳转到选品清单
  goToSelection() {
    wx.navigateTo({ url: '/pages/selection/index' })
  },

  // 跳转到物料管理
  goToMaterials() {
    wx.showToast({ title: '请在Web端使用', icon: 'none' })
  },

  // 联系客服
  contactService() {
    wx.makePhoneCall({
      phoneNumber: '400-888-8888'
    })
  },

  // 关于我们
  aboutUs() {
    wx.showModal({
      title: '关于D&B 帝标|设记家',
      content: 'D&B 帝标|设记家·全安落地服务中心\n版本：v3.0.4\n致力于为您提供专业的软装设计与服务',
      showCancel: false
    })
  }
})