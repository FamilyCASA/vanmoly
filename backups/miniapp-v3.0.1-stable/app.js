App({
  onLaunch() {
    console.log('D&B 帝标|设记家小程序启动')
    
    // 检查更新
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()
      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          updateManager.onUpdateReady(() => {
            wx.showModal({
              title: '更新提示',
              content: '新版本已准备好，是否重启应用？',
              success: (res) => {
                if (res.confirm) {
                  updateManager.applyUpdate()
                }
              }
            })
          })
        }
      })
    }
  },

  onShow() {
    console.log('小程序显示')
  },

  onHide() {
    console.log('小程序隐藏')
  },

  onError(msg) {
    console.error('小程序错误:', msg)
  },

  globalData: {
    userInfo: null,
    backendUrl: 'http://127.0.0.1:5000'
  }
})
