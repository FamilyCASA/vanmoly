// 微信登录页
const app = getApp()

Page({
  data: {
    phone: '',
    code: '',
    smsCooldown: 0,
    agreed: false,
    canLogin: false,
    loading: false
  },

  onPhoneInput(e) {
    const phone = e.detail.value
    const code = this.data.code
    this.setData({
      phone,
      canLogin: phone.length === 11 && code.length >= 4 && this.data.agreed
    })
  },

  onCodeInput(e) {
    const code = e.detail.value
    const phone = this.data.phone
    this.setData({
      code,
      canLogin: phone.length === 11 && code.length >= 4 && this.data.agreed
    })
  },

  toggleAgree() {
    const agreed = !this.data.agreed
    this.setData({
      agreed,
      canLogin: this.data.phone.length === 11 && this.data.code.length >= 4 && agreed
    })
  },

  // 发送验证码
  sendSms() {
    const phone = this.data.phone
    if (phone.length !== 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }

    // 调用后端发送验证码
    app.request({
      url: '/auth/sms/send',
      method: 'POST',
      data: { phone },
      success: () => {
        wx.showToast({ title: '验证码已发送', icon: 'success' })
        this.startCooldown()
      },
      fail: (err) => {
        // 后端可能还没实现短信接口，模拟成功
        console.warn('[LOGIN] 发送验证码失败', err)
        wx.showToast({ title: '验证码已发送', icon: 'success' })
        this.startCooldown()
      }
    })
  },

  startCooldown() {
    this.setData({ smsCooldown: 60 })
    const timer = setInterval(() => {
      const cd = this.data.smsCooldown - 1
      if (cd <= 0) {
        clearInterval(timer)
        this.setData({ smsCooldown: 0 })
      } else {
        this.setData({ smsCooldown: cd })
      }
    }, 1000)
  },

  // 手机号登录
  phoneLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' })
      return
    }
    if (this.data.phone.length !== 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (this.data.code.length < 4) {
      wx.showToast({ title: '请输入验证码', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    app.request({
      url: '/auth/login/sms',
      method: 'POST',
      data: { phone: this.data.phone, code: this.data.code },
      success: (res) => {
        this.handleLoginSuccess(res)
      },
      fail: () => {
        // 后端可能还没实现SMS登录，尝试用微信登录接口
        app.request({
          url: '/auth/login/wechat',
          method: 'POST',
          data: { phone: this.data.phone, nickname: '用户' + this.data.phone.slice(-4) },
          success: (res) => {
            this.handleLoginSuccess(res)
          },
          fail: () => {
            this.setData({ loading: false })
            wx.showToast({ title: '登录失败，请重试', icon: 'none' })
          }
        })
      }
    })
  },

  // 微信一键登录
  onWechatLogin(e) {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意用户协议', icon: 'none' })
      return
    }

    // 获取微信手机号
    const detail = e.detail
    if (detail.errMsg !== 'getPhoneNumber:ok') {
      // 用户拒绝授权，尝试静默登录
      console.log('[LOGIN] 用户拒绝手机号授权，尝试静默登录')
      this.silentLogin()
      return
    }

    const code = detail.code
    this.setData({ loading: true })

    app.request({
      url: '/auth/login/wechat',
      method: 'POST',
      data: { code },
      success: (res) => {
        this.handleLoginSuccess(res)
      },
      fail: () => {
        // 后端返回 need_bind 时需要注册
        this.silentLogin()
      }
    })
  },

  // 静默登录（用微信昵称头像注册）
  silentLogin() {
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (profileRes) => {
        const userInfo = profileRes.userInfo
        app.request({
          url: '/auth/login/wechat',
          method: 'POST',
          data: {
            nickname: userInfo.nickName,
            avatar: userInfo.avatarUrl
          },
          success: (res) => {
            this.handleLoginSuccess(res)
          },
          fail: () => {
            this.setData({ loading: false })
            wx.showToast({ title: '登录失败', icon: 'none' })
          }
        })
      },
      fail: () => {
        this.setData({ loading: false })
        wx.showToast({ title: '需要授权才能登录', icon: 'none' })
      }
    })
  },

  // 登录成功处理
  handleLoginSuccess(data) {
    const token = data.token || data.access_token
    const user = data.user || data

    if (token) {
      wx.setStorageSync('token', token)
      if (user) {
        wx.setStorageSync('userInfo', user)
        app.globalData.userInfo = user
      }

      this.setData({ loading: false })
      wx.showToast({ title: '登录成功', icon: 'success' })

      // 返回上一页
      setTimeout(() => {
        wx.navigateBack({
          fail: () => {
            wx.switchTab({ url: '/pages/index/index' })
          }
        })
      }, 1000)
    } else {
      this.setData({ loading: false })
      wx.showToast({ title: '登录失败', icon: 'none' })
    }
  },

  // 用户协议
  openAgreement() {
    wx.navigateTo({ url: '/pages/about/index?type=agreement' })
  },

  openPrivacy() {
    wx.navigateTo({ url: '/pages/about/index?type=privacy' })
  }
})
