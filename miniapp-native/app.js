App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://localhost:8080/api/v3',
    // 留资触发配置
    leadConfig: {
      autoPopupDelay: 30000,
      caseViewThreshold: 3,
      hasLeaded: false
    }
  },

  onLaunch() {
    const hasLeaded = wx.getStorageSync('hasLeaded');
    this.globalData.leadConfig.hasLeaded = hasLeaded;
    this.getUserInfo();
  },

  getUserInfo() {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({ success: (res) => { this.globalData.userInfo = res.userInfo; } });
        }
      }
    });
  },

  // 全局留资方法
  showLeadPopup(options = {}) {
    const { source = '未知', sourceId = '', title = '获取免费设计方案' } = options;
    if (this.globalData.leadConfig.hasLeaded) return;
    wx.navigateTo({ url: `/pages/lead/lead?source=${source}&sourceId=${sourceId}&title=${title}` });
  },

  markAsLeaded() {
    this.globalData.leadConfig.hasLeaded = true;
    wx.setStorageSync('hasLeaded', true);
  },

  // 请求封装：与Web端axios拦截器行为一致
  // - apiBaseUrl 已包含 /api/v3 前缀
  // - 传入的 url 不需要 /api/v3 前缀（如 /frontend/hero-slides）
  // - 自动从后端响应 {code, data, message} 提取 data 字段传给 success
  request(options) {
    const { url, method = 'GET', data = {}, success, fail, complete } = options;
    const fullUrl = `${this.globalData.apiBaseUrl}${url}`;
    console.log(`[REQUEST] ${method} ${fullUrl}`);
    wx.request({
      url: fullUrl,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        console.log(`[RESPONSE] ${url} status=${res.statusCode}`, res.data);
        if (res.statusCode === 200 || res.statusCode === 201) {
          const body = res.data;
          // 后端统一响应格式: { code, data, message }
          if (body && (body.code === 200 || body.code === 201)) {
            // 业务成功，提取 data 字段（与Web端axios拦截器行为一致）
            success && success(body.data);
          } else if (body && body.code !== undefined) {
            // 业务错误（有code但非200/201）
            console.warn(`API业务错误 [${url}]: code=${body.code}, msg=${body.message}`);
            fail && fail(body);
          } else {
            // 兼容非标准响应（无code字段，直接返回数据）
            success && success(body);
          }
        } else {
          console.warn(`[HTTP ERROR] ${url} status=${res.statusCode}`);
          fail && fail(res);
        }
      },
      fail: (err) => {
        console.error(`[NETWORK ERROR] ${url}`, err);
        fail && fail(err);
      },
      complete: () => { complete && complete(); }
    });
  },

  // 图片 URL 解析
  resolveImageUrl(path) {
    if (!path) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    let clean = path;
    if (!clean.startsWith('/')) clean = '/' + clean;
    // 剥离路径中可能存在的 /api/v3 前缀（后端有时直接返回 /api/v3/upload/...）
    clean = clean.replace(/^\/api\/v3\/?/, '/');
    // 服务器根地址（不含 /api/v3）
    const serverRoot = this.globalData.apiBaseUrl.replace(/\/api\/v3$/, '');
    const resolved = serverRoot + clean;
    console.log(`[IMG] ${path} → ${resolved}`);
    return resolved;
  },

  // 格式化价格
  formatPrice(v) {
    if (!v && v !== 0) return '0';
    return Number(v).toLocaleString();
  },

  // Toast 提示
  toast(msg, icon = 'none') {
    wx.showToast({ title: msg, icon });
  }
});
