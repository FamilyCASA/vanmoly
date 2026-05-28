// 我的收藏
const app = getApp()

Page({
  data: {
    activeTab: 'case',
    loading: true,
    caseList: [],
    productList: [],
    designerList: [],
    caseCount: 0,
    productCount: 0,
    designerCount: 0
  },

  onLoad() {
    this.loadAllCollections()
  },

  onShow() {
    this.loadAllCollections()
  },

  get currentList() {
    const { activeTab, caseList, productList, designerList } = this.data
    if (activeTab === 'case') return caseList
    if (activeTab === 'product') return productList
    return designerList
  },

  // 切换Tab
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab })
  },

  // 加载所有收藏
  loadAllCollections() {
    this.setData({ loading: true })
    
    // 加载案例收藏
    app.request({
      url: '/user/collections',
      data: { type: 'case' },
      success: (res) => {
        const list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({ 
          caseList: list.map(item => ({
            ...item,
            cover: item.cover_image ? app.resolveImageUrl(item.cover_image) : (item.cover || ''),
            collectTime: this.formatTime(item.created_at || item.collect_time)
          })),
          caseCount: list.length
        })
      },
      fail: () => {
        this.setData({ caseList: [], caseCount: 0 })
      }
    })

    // 加载产品收藏
    app.request({
      url: '/user/collections',
      data: { type: 'product' },
      success: (res) => {
        const list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({ 
          productList: list.map(item => ({
            ...item,
            cover: item.main_image ? app.resolveImageUrl(item.main_image) : (item.cover || ''),
            price: this.formatPrice(item.sale_price || item.price)
          })),
          productCount: list.length
        })
      },
      fail: () => {
        this.setData({ productList: [], productCount: 0 })
      }
    })

    // 加载设计师关注
    app.request({
      url: '/user/following',
      data: { type: 'designer' },
      success: (res) => {
        const list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({ 
          designerList: list.map(item => ({
            ...item,
            avatar: item.avatar ? app.resolveImageUrl(item.avatar) : ''
          })),
          designerCount: list.length,
          loading: false
        })
      },
      fail: () => {
        this.setData({ designerList: [], designerCount: 0, loading: false })
      }
    })
  },

  // 删除收藏
  deleteItem(e) {
    const { id, type } = e.currentTarget.dataset
    wx.showModal({
      title: '确认取消',
      content: '确定要取消收藏吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: `/user/collections/${id}`,
            method: 'DELETE',
            data: { type },
            success: () => {
              this.removeItemFromList(type, id)
              wx.showToast({ title: '已取消收藏', icon: 'success' })
            },
            fail: () => {
              this.removeItemFromList(type, id)
              wx.showToast({ title: '已取消收藏', icon: 'success' })
            }
          })
        }
      }
    })
  },

  removeItemFromList(type, id) {
    if (type === 'case') {
      const caseList = this.data.caseList.filter(item => item.id !== id)
      this.setData({ caseList, caseCount: caseList.length })
    } else if (type === 'product') {
      const productList = this.data.productList.filter(item => item.id !== id)
      this.setData({ productList, productCount: productList.length })
    }
  },

  // 取消关注设计师
  unfollowDesigner(e) {
    const id = e.currentTarget.dataset.id
    app.request({
      url: `/user/following/${id}`,
      method: 'DELETE',
      success: () => {
        const designerList = this.data.designerList.filter(item => item.id !== id)
        this.setData({ designerList, designerCount: designerList.length })
        wx.showToast({ title: '已取消关注', icon: 'success' })
      },
      fail: () => {
        const designerList = this.data.designerList.filter(item => item.id !== id)
        this.setData({ designerList, designerCount: designerList.length })
        wx.showToast({ title: '已取消关注', icon: 'success' })
      }
    })
  },

  // 跳转
  goExplore() {
    const tab = this.data.activeTab
    if (tab === 'case') {
      wx.switchTab({ url: '/pages/cases/cases' })
    } else if (tab === 'product') {
      wx.switchTab({ url: '/pages/products/index' })
    }
  },
  goToCase(e) {
    wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${e.currentTarget.dataset.id}` })
  },
  goToProduct(e) {
    wx.navigateTo({ url: `/pages/product-detail/index?id=${e.currentTarget.dataset.id}` })
  },
  goToDesigner(e) {
    wx.navigateTo({ url: `/pages/designer/index?id=${e.currentTarget.dataset.id}` })
  },

  // 工具方法
  formatTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  },
  formatPrice(price) {
    if (!price) return '0'
    const num = parseFloat(price)
    return num >= 10000 ? (num/10000).toFixed(1) + '万' : num.toLocaleString()
  }
})