// 关于我们
const app = getApp()

Page({
  data: { latestVersion: '已是最新' },

  onLoad() {
    this.checkUpdate(true)
  },

  goWebsite() {
    wx.setClipboardData({ data: 'https://www.designary.com' })
  },
  goWechat() {
    wx.setClipboardData({ data: '帝标设记家' })
  },
  contactService() {
    wx.makePhoneCall({ phoneNumber: '400-888-8888' })
  },
  checkUpdate(silent) {
    if (wx.getUpdateManager) {
      const updateManager = wx.getUpdateManager()
      updateManager.onCheckForUpdate((res) => {
        if (!res.hasUpdate && !silent) {
          this.setData({ latestVersion: '已是最新' })
        } else if (res.hasUpdate) {
          this.setData({ latestVersion: '有新版本' })
        }
      })
      updateManager.onUpdateReady(() => {
        wx.showModal({ title: '更新提示', content: '新版本已准备好，是否重启应用？', success: (r) => { if (r.confirm) updateManager.applyUpdate() } })
      })
    }
  },
  userAgreement() {
    wx.showToast({ title: '页面开发中', icon: 'none' })
  },
  privacyPolicy() {
    wx.showToast({ title: '页面开发中', icon: 'none' })
  }
})