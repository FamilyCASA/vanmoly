// 我的方案
const app = getApp()

Page({
  data: { loading: true, schemes: [], isLoggedIn: false },

  onLoad() {
    const token = wx.getStorageSync('token')
    this.setData({ isLoggedIn: !!token })
    this.loadSchemes()
  },
  onShow() { this.loadSchemes() },

  loadSchemes() {
    this.setData({ loading: true })
    app.request({
      url: '/user/schemes',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          schemes: list.map(item => ({
            ...item,
            cover: item.cover_image ? app.resolveImageUrl(item.cover_image) : '',
            statusText: this.getStatusText(item.status),
            updatedAt: this.formatDate(item.updated_at || item.created_at)
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ schemes: [], loading: false }) }
    })
  },

  goToDetail(e) { wx.navigateTo({ url: `/pages/scheme-detail/index?id=${e.currentTarget.dataset.id}` }) },
  goCreate() { wx.navigateTo({ url: '/pages/scheme-create/index' }) },
  goCases() { wx.switchTab({ url: '/pages/cases/cases' }) },

  getStatusText(status) {
    const map = { 'draft': '草稿', 'designing': '设计中', 'reviewing': '待审核', 'confirmed': '已确认', 'completed': '已完成' }
    return map[status] || status
  },
  formatDate(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})