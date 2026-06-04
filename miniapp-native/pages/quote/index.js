Page({
  data: {
    quotes: [],
    isAdmin: false,
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    statusText: {
      draft: '草稿',
      sent: '已发送',
      confirmed: '已确认',
      signed: '已签署',
      expired: '已过期'
    }
  },

  onLoad(options) {
    // 检查是否为管理员
    const userInfo = wx.getStorageSync('userInfo')
    this.setData({
      isAdmin: userInfo?.is_staff || false
    })
    this.loadQuotes()
  },

  onShow() {
    this.loadQuotes()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  // 加载报价列表
  loadQuotes() {
    this.setData({ loading: true })

    // 模拟数据
    const mockQuotes = [
      {
        id: 1,
        quote_no: 'BJ202604260001',
        customer_name: '张先生',
        total_amount: '258,000',
        status: 'draft',
        created_at: '2026-04-26',
        creator_name: '设计师A'
      },
      {
        id: 2,
        quote_no: 'BJ202604250002',
        customer_name: '李女士',
        total_amount: '186,500',
        status: 'sent',
        created_at: '2026-04-25',
        creator_name: '设计师B'
      },
      {
        id: 3,
        quote_no: 'BJ202604240003',
        customer_name: '王先生',
        total_amount: '320,000',
        status: 'confirmed',
        created_at: '2026-04-24',
        creator_name: '设计师A'
      }
    ]

    this.setData({
      quotes: mockQuotes,
      loading: false,
      hasMore: false
    })

    // 实际 API 调用：
    // wx.request({
    //   url: 'http://127.0.0.1:5000/api/v3/quotes',
    //   header: {
    //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
    //   },
    //   data: {
    //     page: this.data.page,
    //     page_size: this.data.pageSize
    //   },
    //   success: (res) => {
    //     if (res.statusCode === 200) {
    //       this.setData({
    //         quotes: res.data.items,
    //         hasMore: res.data.items.length === this.data.pageSize
    //       })
    //     }
    //   },
    //   complete: () => {
    //     this.setData({ loading: false })
    //   }
    // })
  },

  // 加载更多
  loadMore() {
    this.setData({ page: this.data.page + 1 })
    this.loadQuotes()
  },

  // 创建报价
  createQuote() {
    // 提示用户在 Web 端创建
    wx.showModal({
      title: '提示',
      content: '请在 Web 管理后台创建报价，体验更完整的功能',
      confirmText: '打开Web端',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: 'http://localhost:3000/#/quotes',
            success: () => {
              wx.showToast({ title: '链接已复制', icon: 'success' })
            }
          })
        }
      }
    })
  },

  // 查看详情
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/quote-detail/index?id=${id}`
    })
  },

  // 预览报价
  previewQuote(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    wx.showToast({ title: '预览功能开发中', icon: 'none' })
  },

  // 分享报价
  shareQuote(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    wx.showShareMenu({
      withShareTicket: true
    })
  }
})