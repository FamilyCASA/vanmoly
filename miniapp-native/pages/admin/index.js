const app = getApp()

Page({
  data: {
    userName: '',
    userRole: '',        // admin, manager, employee
    isAdmin: false,
    canApprove: false,   // 有审核权限
    canManageTeam: false, // 有团队管理权限
    stats: {
      pendingLeads: 0,
      myTasks: 0,
      pendingApprovals: 0,
      workflowApprovals: 0,
      quoteApprovals: 0,
      contractApprovals: 0,
      pointsApprovals: 0
    }
  },

  onLoad() {
    this.loadUserInfo()
    this.loadStats()
  },

  onShow() {
    this.loadStats()
  },

  // 加载用户信息
  loadUserInfo() {
    // 从本地存储获取登录信息
    const userInfo = wx.getStorageSync('adminUserInfo')
    if (userInfo) {
      const isAdmin = userInfo.role === 'admin'
      const canApprove = isAdmin || userInfo.role === 'manager' || userInfo.permissions?.includes('approve')
      const canManageTeam = isAdmin || userInfo.permissions?.includes('manage_team')
      
      this.setData({
        userName: userInfo.name || userInfo.username || '',
        userRole: userInfo.role || '',
        isAdmin,
        canApprove,
        canManageTeam
      })
    } else {
      // 未登录，跳转到登录页
      this.goToLogin()
    }
  },

  // 加载统计数据
  loadStats() {
    const token = wx.getStorageSync('adminToken')
    if (!token) return

    app.request({
      url: '/admin/dashboard-stats',
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        if (res) {
          this.setData({ stats: res })
        }
      },
      fail: () => {
        // 使用模拟数据
        this.setData({
          stats: {
            pendingLeads: 12,
            myTasks: 8,
            pendingApprovals: 5,
            workflowApprovals: 2,
            quoteApprovals: 3,
            contractApprovals: 1,
            pointsApprovals: 0
          }
        })
      }
    })
  },

  // 跳转到子页面
  goToPage(e) {
    const page = e.currentTarget.dataset.page
    const pageMap = {
      // 日常工作
      'node-report': '/pages/admin-node-report/index',
      'lead-create': '/pages/admin-lead-create/index',
      'lead-follow': '/pages/admin-lead-follow/index',
      'customer-follow': '/pages/admin-customer-follow/index',
      // 信息管理
      'customer-create': '/pages/admin-customer-create/index',
      'buildings': '/pages/admin-buildings/index',
      'case-share': '/pages/admin-case-share/index',
      // 审核管理
      'workflow-mgmt': '/pages/admin-workflow-mgmt/index',
      'approval-workflow': '/pages/admin-approval/index?type=workflow',
      'approval-quote': '/pages/admin-approval/index?type=quote',
      'approval-contract': '/pages/admin-approval/index?type=contract',
      'approval-points': '/pages/admin-approval/index?type=points',
      // 团队管理
      'employees': '/pages/admin-employees/index',
      'task-assign': '/pages/admin-task-assign/index',
      // 管理员
      'settings': '/pages/admin-settings/index',
      'reports': '/pages/admin-reports/index'
    }

    const url = pageMap[page]
    if (url) {
      wx.navigateTo({ url })
    } else {
      wx.showToast({ title: '功能开发中', icon: 'none' })
    }
  },

  // 跳转登录
  goToLogin() {
    wx.navigateTo({ url: '/pages/admin-login/index' })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadStats()
    wx.stopPullDownRefresh()
  }
})
