// 我的页面 - 完整版
const app = getApp()

Page({
  data: {
    userInfo: {},
    isLoggedIn: false,
    
    // 统计数据
    points: 0,
    couponCount: 0,
    collectCount: 0,
    selectionCount: 0,
    estateCount: 0,
    contractCount: 0,
    quoteCount: 0,
    subCount: 0,
    noteCount: 0,
    commentCount: 0,
    customerCount: 0,
    
    // 提醒数量
    pendingAppointments: 0,
    pendingNodes: 0,
    pendingLeads: 0
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    this.checkLogin()
    this.loadUserStats()
    this.updateSelectionCount()
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.setData({ 
        isLoggedIn: true, 
        userInfo: {
          ...userInfo,
          isEmployee: userInfo.role === 'employee' || userInfo.role === 'admin' || userInfo.isEmployee,
          isVip: userInfo.isVip || userInfo.vipLevel > 0,
          roleName: this.getRoleName(userInfo.role),
          level: userInfo.level || 1
        }
      })
      this.loadUserInfo()
    } else {
      this.setData({ 
        isLoggedIn: false, 
        userInfo: {},
        points: 0,
        couponCount: 0
      })
    }
  },

  // 获取角色名称
  getRoleName(role) {
    const roleMap = {
      'admin': '管理员',
      'employee': '员工',
      'designer': '设计师',
      'planner': '规划师',
      'manager': '客户经理',
      'vip': 'VIP会员'
    }
    return roleMap[role] || ''
  },

  // 加载用户信息
  loadUserInfo() {
    if (!this.data.isLoggedIn) return
    
    app.request({
      url: '/user/profile',
      success: (res) => {
        if (res) {
          const userInfo = {
            ...res,
            isEmployee: res.role === 'employee' || res.role === 'admin' || res.isEmployee,
            isVip: res.isVip || res.vipLevel > 0,
            roleName: this.getRoleName(res.role),
            level: res.level || 1
          }
          this.setData({ userInfo })
          wx.setStorageSync('userInfo', userInfo)
        }
      }
    })
  },

  // 加载统计数据
  loadUserStats() {
    if (!this.data.isLoggedIn) return

    // 积分
    app.request({
      url: '/user/points',
      success: (res) => {
        if (res && res.total !== undefined) {
          this.setData({ points: res.total })
        }
      }
    })

    // 优惠券
    app.request({
      url: '/user/coupons',
      data: { status: 'available' },
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ couponCount: count })
      }
    })

    // 收藏
    app.request({
      url: '/user/collections',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ collectCount: count })
      }
    })

    // 房产
    app.request({
      url: '/user/estates',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ estateCount: count })
      }
    })

    // 合同
    app.request({
      url: '/user/contracts',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ contractCount: count })
      }
    })

    // 报价
    app.request({
      url: '/user/quotes',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ quoteCount: count })
      }
    })

    // 订阅
    app.request({
      url: '/user/subscriptions',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ subCount: count })
      }
    })

    // 笔记
    app.request({
      url: '/user/notes',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ noteCount: count })
      }
    })

    // 评论
    app.request({
      url: '/user/comments',
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ commentCount: count })
      }
    })

    // 员工数据
    if (this.data.userInfo.isEmployee) {
      // 我的客户
      app.request({
        url: '/employee/customers',
        success: (res) => {
          const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
          this.setData({ customerCount: count })
        }
      })

      // 待处理节点
      app.request({
        url: '/employee/pending-nodes',
        success: (res) => {
          const count = res && res.count ? res.count : 0
          this.setData({ pendingNodes: count })
        }
      })

      // 待跟进线索
      app.request({
        url: '/employee/pending-leads',
        success: (res) => {
          const count = res && res.count ? res.count : 0
          this.setData({ pendingLeads: count })
        }
      })
    }

    // 待处理预约
    app.request({
      url: '/user/appointments',
      data: { status: 'pending' },
      success: (res) => {
        const count = res && res.total ? res.total : (res && res.items ? res.items.length : 0)
        this.setData({ pendingAppointments: count })
      }
    })
  },

  // 更新选品单数量
  updateSelectionCount() {
    const sel = wx.getStorageSync('selection') || []
    this.setData({ selectionCount: sel.length })
  },

  // 登录
  login() {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (profileRes) => {
        wx.login({
          success: (res) => {
            if (res.code) {
              app.request({
                url: '/auth/wechat-login',
                method: 'POST',
                data: { 
                  code: res.code,
                  userInfo: profileRes.userInfo
                },
                success: (loginRes) => {
                  if (loginRes && loginRes.token) {
                    wx.setStorageSync('token', loginRes.token)
                    const userInfo = {
                      ...loginRes.user,
                      nickName: loginRes.user.nickName || loginRes.user.nickname || profileRes.userInfo.nickName,
                      avatar: loginRes.user.avatar || profileRes.userInfo.avatarUrl
                    }
                    wx.setStorageSync('userInfo', userInfo)
                    this.setData({ 
                      isLoggedIn: true, 
                      userInfo: {
                        ...userInfo,
                        isEmployee: userInfo.role === 'employee' || userInfo.role === 'admin',
                        isVip: userInfo.isVip || userInfo.vipLevel > 0,
                        roleName: this.getRoleName(userInfo.role)
                      }
                    })
                    this.loadUserStats()
                    wx.showToast({ title: '登录成功', icon: 'success' })
                  } else {
                    this.mockLogin(profileRes.userInfo)
                  }
                },
                fail: () => {
                  this.mockLogin(profileRes.userInfo)
                }
              })
            }
          }
        })
      },
      fail: () => {
        wx.showToast({ title: '授权失败', icon: 'none' })
      }
    })
  },

  // Mock登录（开发调试用）
  mockLogin(userInfo) {
    const mockUser = {
      id: 1,
      nickName: userInfo ? userInfo.nickName : '测试用户',
      avatar: userInfo ? userInfo.avatarUrl : '',
      phone: '138****8888',
      role: 'user',
      isVip: false,
      level: 1
    }
    wx.setStorageSync('token', 'mock_token_' + Date.now())
    wx.setStorageSync('userInfo', mockUser)
    this.setData({ 
      isLoggedIn: true, 
      userInfo: {
        ...mockUser,
        roleName: ''
      },
      points: 1280,
      couponCount: 3,
      collectCount: 12
    })
    wx.showToast({ title: '登录成功', icon: 'success' })
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
            userInfo: {},
            points: 0,
            couponCount: 0,
            collectCount: 0,
            selectionCount: 0,
            estateCount: 0,
            contractCount: 0,
            quoteCount: 0,
            subCount: 0,
            noteCount: 0,
            commentCount: 0,
            customerCount: 0
          })
          wx.showToast({ title: '已退出', icon: 'success' })
        }
      }
    })
  },

  // 需要登录的页面跳转
  requireLogin(url) {
    if (!this.data.isLoggedIn) {
      wx.showModal({
        title: '提示',
        content: '该功能需要登录后使用，是否立即登录？',
        success: (res) => {
          if (res.confirm) this.login()
        }
      })
      return false
    }
    return true
  },

  navigateTo(url) {
    wx.navigateTo({ url }).catch(() => {
      wx.showToast({ title: '页面开发中', icon: 'none' })
    })
  },

  // ===== 跳转方法 =====
  
  // 用户信息
  goToProfile() { 
    if (this.requireLogin()) {
      this.navigateTo('/pages/profile-detail/index')
    }
  },
  goToSettings() { this.navigateTo('/pages/settings/index') },
  
  // 快捷入口
  goToOrders() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-orders/index') 
  },
  goToAppointments() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-appointments/index') 
  },
  goToSelection() { wx.navigateTo({ url: '/pages/selection/index' }) },
  goToSchemes() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-schemes/index') 
  },
  
  // 我的服务
  goToEstates() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-estates/index') 
  },
  goToContracts() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-contracts/index') 
  },
  goToQuotes() { 
    if (this.requireLogin()) this.navigateTo('/pages/quote/index') 
  },
  goToSubscriptions() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-subscriptions/index') 
  },
  
  // 内容管理
  goToCollections() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-collections/index') 
  },
  goToHistory() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-history/index') 
  },
  goToNotes() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-notes/index') 
  },
  goToComments() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-comments/index') 
  },
  
  // 会员权益
  goToPoints() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-points/index') 
  },
  goToCoupons() { 
    if (this.requireLogin()) this.navigateTo('/pages/my-coupons/index') 
  },
  goToVip() { 
    if (this.requireLogin()) this.navigateTo('/pages/vip-center/index') 
  },
  
  // 后台管理
  goToAdmin() { wx.navigateTo({ url: '/pages/admin/index' }) },
  goToNodeReport() { wx.navigateTo({ url: '/pages/admin-node-report/index' }) },
  goToMyCustomers() { 
    if (this.requireLogin()) this.navigateTo('/pages/admin-customers/index') 
  },
  goToMyLeads() { 
    if (this.requireLogin()) this.navigateTo('/pages/admin-leads/index') 
  },
  goToWorkflowManage() { 
    if (this.requireLogin()) this.navigateTo('/pages/admin-workflow/index') 
  },
  
  // 帮助支持
  contactService() {
    wx.makePhoneCall({ 
      phoneNumber: '400-888-8888',
      fail: () => {
        wx.showToast({ title: '拨号失败', icon: 'none' })
      }
    })
  },
  openWechatService() {
    wx.showModal({
      title: '在线客服',
      content: '请添加客服微信：dbkefu\n或拨打客服电话：400-888-8888',
      showCancel: false
    })
  },
  goToHelp() { this.navigateTo('/pages/help/index') },
  goToFeedback() { this.navigateTo('/pages/feedback/index') },
  goToAbout() { this.navigateTo('/pages/about/index') }
})