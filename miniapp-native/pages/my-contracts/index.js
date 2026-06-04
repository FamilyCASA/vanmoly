// 我的合同
const app = getApp()

Page({
  data: { loading: true, contracts: [] },

  onLoad() { this.loadContracts() },
  onShow() { this.loadContracts() },

  loadContracts() {
    this.setData({ loading: true })
    app.request({
      url: '/user/contracts',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          contracts: list.map(item => ({
            ...item,
            statusText: this.getStatusText(item.status),
            signDate: this.formatDate(item.sign_date || item.created_at),
            progress: item.progress || ''
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ contracts: [], loading: false }) }
    })
  },

  goToDetail(e) {
    wx.navigateTo({ url: `/pages/contract-detail/index?id=${e.currentTarget.dataset.id}` })
  },

  getStatusText(status) {
    const map = { 'draft': '待签约', 'active': '履约中', 'completed': '已完成', 'terminated': '已终止', 'cancelled': '已取消' }
    return map[status] || status
  },
  formatDate(dateStr) {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})