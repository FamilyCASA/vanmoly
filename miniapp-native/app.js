App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'https://your-api-domain.com/api/v3',
    // 留资触发配置
    leadConfig: {
      // 首页停留30秒自动弹窗
      autoPopupDelay: 30000,
      // 案例浏览3个后弹窗
      caseViewThreshold: 3,
      // 是否已留资（避免重复打扰）
      hasLeaded: false
    }
  },

  onLaunch() {
    // 检查是否已留资
    const hasLeaded = wx.getStorageSync('hasLeaded');
    this.globalData.leadConfig.hasLeaded = hasLeaded;
    
    // 获取用户信息
    this.getUserInfo();
  },

  // 获取用户信息
  getUserInfo() {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: (res) => {
              this.globalData.userInfo = res.userInfo;
            }
          });
        }
      }
    });
  },

  // 全局留资方法 - 任何地方都可以调用
  showLeadPopup(options = {}) {
    const { source = '未知', sourceId = '', title = '获取免费设计方案' } = options;
    
    // 如果已留资，不再打扰
    if (this.globalData.leadConfig.hasLeaded) {
      return;
    }

    wx.navigateTo({
      url: `/pages/lead/lead?source=${source}&sourceId=${sourceId}&title=${title}`
    });
  },

  // 标记已留资
  markAsLeaded() {
    this.globalData.leadConfig.hasLeaded = true;
    wx.setStorageSync('hasLeaded', true);
  },

  // 请求封装
  request(options) {
    const { url, method = 'GET', data = {}, success, fail } = options;
    
    wx.request({
      url: `${this.globalData.apiBaseUrl}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          success && success(res.data);
        } else {
          fail && fail(res);
        }
      },
      fail: (err) => {
        fail && fail(err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  }
});