Page({
  data: {
    cases: [],
    currentStyle: '',
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadCases()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  // 加载案例列表
  loadCases() {
    this.setData({ loading: true })
    
    // 模拟数据，实际应从 API 加载
    const mockCases = [
      { id: 1, title: '现代简约·三居室', style: '现代简约', area: 120, cover_image: 'https://via.placeholder.com/400x500/F5F5F5/8B5A2B?text=案例1' },
      { id: 2, title: '新中式·别墅', style: '新中式', area: 350, cover_image: 'https://via.placeholder.com/400x500/FAF0E6/8B5A2B?text=案例2' },
      { id: 3, title: '北欧风·两居室', style: '北欧风', area: 89, cover_image: 'https://via.placeholder.com/400x500/F0F8FF/8B5A2B?text=案例3' },
      { id: 4, title: '轻奢·四居室', style: '轻奢', area: 180, cover_image: 'https://via.placeholder.com/400x500/FFF0F5/8B5A2B?text=案例4' },
      { id: 5, title: '美式·复式', style: '美式', area: 200, cover_image: 'https://via.placeholder.com/400x500/F5F5DC/8B5A2B?text=案例5' },
      { id: 6, title: '现代简约·公寓', style: '现代简约', area: 65, cover_image: 'https://via.placeholder.com/400x500/E8E8E8/8B5A2B?text=案例6' }
    ]

    // 筛选
    let filteredCases = mockCases
    if (this.data.currentStyle) {
      filteredCases = mockCases.filter(c => c.style === this.data.currentStyle)
    }

    this.setData({
      cases: filteredCases,
      loading: false,
      hasMore: false // 模拟无更多数据
    })

    // 实际 API 调用示例：
    // wx.request({
    //   url: 'http://127.0.0.1:5000/api/v3/cases',
    //   data: {
    //     page: this.data.page,
    //     page_size: this.data.pageSize,
    //     style: this.data.currentStyle
    //   },
    //   success: (res) => {
    //     if (res.statusCode === 200) {
    //       this.setData({
    //         cases: res.data.items,
    //         hasMore: res.data.items.length === this.data.pageSize
    //       })
    //     }
    //   },
    //   complete: () => {
    //     this.setData({ loading: false })
    //   }
    // })
  },

  // 按风格筛选
  filterByStyle(e) {
    const style = e.currentTarget.dataset.style
    this.setData({
      currentStyle: style,
      page: 1,
      cases: []
    })
    this.loadCases()
  },

  // 加载更多
  loadMore() {
    this.setData({ page: this.data.page + 1 })
    this.loadCases()
  },

  // 跳转到详情
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/case-detail/index?id=${id}`
    })
  }
})