// 个人资料
const app = getApp()

Page({
  data: {
    userInfo: {},
    genderOptions: ['未设置', '男', '女'],
    genderIndex: 0
  },

  onLoad() {
    const userInfo = wx.getStorageSync('userInfo') || {}
    this.setData({
      userInfo,
      genderIndex: userInfo.gender !== undefined ? userInfo.gender : 0
    })
  },

  changeAvatar() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sizeType: ['compressed'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath
        wx.uploadFile({
          url: app.globalData.apiBaseUrl + '/user/avatar',
          filePath: tempFilePath,
          name: 'avatar',
          header: { 'Authorization': 'Bearer ' + wx.getStorageSync('token') },
          success: (uploadRes) => {
            try {
              const data = JSON.parse(uploadRes.data)
              if (data.code === 200) {
                this.setData({ 'userInfo.avatar': data.data.url })
                wx.showToast({ title: '头像已更新', icon: 'success' })
              }
            } catch(e) {}
          }
        })
      }
    })
  },

  bindPhone() {
    // 使用微信手机号快速验证
    wx.getPhoneNumber && wx.getPhoneNumber({
      success: (res) => {
        app.request({
          url: '/user/bind-phone',
          method: 'POST',
          data: { code: res.code },
          success: (r) => {
            if (r && r.phone) {
              this.setData({ 'userInfo.phone': r.phone })
              wx.showToast({ title: '绑定成功', icon: 'success' })
            }
          }
        })
      },
      fail: () => {
        wx.showToast({ title: '需要授权手机号', icon: 'none' })
      }
    })
  },

  onNickNameChange(e) { this.setData({ 'userInfo.nickName': e.detail.value }) },
  onRealNameChange(e) { this.setData({ 'userInfo.realName': e.detail.value }) },
  onGenderChange(e) { this.setData({ genderIndex: e.detail.value, 'userInfo.gender': parseInt(e.detail.value) }) },
  onBirthdayChange(e) { this.setData({ 'userInfo.birthday': e.detail.value }) },
  onCityChange(e) { this.setData({ 'userInfo.city': e.detail.value }) },

  saveProfile() {
    const { userInfo } = this.data
    app.request({
      url: '/user/profile',
      method: 'PUT',
      data: {
        nickName: userInfo.nickName,
        realName: userInfo.realName,
        gender: userInfo.gender,
        birthday: userInfo.birthday,
        city: userInfo.city
      },
      success: () => {
        wx.setStorageSync('userInfo', userInfo)
        wx.showToast({ title: '保存成功', icon: 'success' })
      },
      fail: () => {
        wx.setStorageSync('userInfo', userInfo)
        wx.showToast({ title: '已保存', icon: 'success' })
      }
    })
  }
})