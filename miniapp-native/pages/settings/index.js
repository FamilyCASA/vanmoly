// 设置
const app = getApp()

Page({
  data: { isLoggedIn: false, phoneBound: false, messageEnabled: true, cacheSize: '0KB' },
  onLoad() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo') || {}
    this.setData({ isLoggedIn: !!token, phoneBound: !!userInfo.phone })
    wx.getStorageInfo({
      success: (res) => {
        const kb = Math.round(res.currentSize)
        this.setData({ cacheSize: kb > 1024 ? (kb/1024).toFixed(1) + 'MB' : kb + 'KB' })
      }
    })
  },

  goProfileDetail() { wx.navigateTo({ url: '/pages/profile-detail/index' }) },
  goAbout() { wx.navigateTo({ url: '/pages/about/index' }) },
  goFeedback() { wx.navigateTo({ url: '/pages/feedback/index' }) },
  goHelp() { wx.navigateTo({ url: '/pages/help/index' }) },

  bindPhone() {
    wx.navigateTo({ url: '/pages/profile-detail/index' })
  },
  changePassword() {
    wx.showToast({ title: '功能开发中', icon: 'none' })
  },
  onMessageChange(e) {
    this.setData({ messageEnabled: e.detail.value })
  },
  clearCache() {
    wx.showModal({ title: '确认', content: '确定要清除缓存吗？', success: (r) => {
      if (r.confirm) {
        wx.clearStorageSync()
        this.setData({ cacheSize: '0KB', isLoggedIn: false, phoneBound: false })
        wx.showToast({ title: '已清除', icon: 'success' })
      }
    }})
  },
  logout() {
    wx.showModal({ title: '提示', content: '确定要退出登录吗？', success: (r) => {
      if (r.confirm) {
        wx.removeStorageSync('token')
        wx.removeStorageSync('userInfo')
        wx.reLaunch({ url: '/pages/profile/index' })
      }
    }})
  }
})