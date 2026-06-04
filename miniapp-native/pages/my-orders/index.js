// 我的订单
const app = getApp()
const statusMap = { 'pending': '待付款', 'paid': '待发货', 'shipped': '待收货', 'completed': '已完成', 'cancelled': '已取消', 'refunded': '已退款' }

Page({
  data: { activeTab: 'all', loading: true, orders: [] },
  onLoad() { this.loadOrders() },
  onShow() { this.loadOrders() },
  switchTab(e) { this.setData({ activeTab: e.currentTarget.dataset.tab }); this.loadOrders() },

  loadOrders() {
    this.setData({ loading: true })
    const data = {}
    if (this.data.activeTab !== 'all') data.status = this.data.activeTab
    app.request({
      url: '/user/orders',
      data,
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          orders: list.map(o => ({
            ...o,
            statusText: statusMap[o.status] || o.status,
            items: (o.items || []).map(p => ({
              ...p,
              cover: p.main_image ? app.resolveImageUrl(p.main_image) : (p.cover || '')
            }))
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ orders: [], loading: false }) }
    })
  },

  cancelOrder(e) {
    wx.showModal({ title: '确认', content: '确定取消该订单？', success: (r) => {
      if (r.confirm) app.request({ url: `/user/orders/${e.currentTarget.dataset.id}/cancel`, method: 'POST', success: () => this.loadOrders(), fail: () => this.loadOrders() })
    }})
  },
  payOrder(e) {
    wx.showToast({ title: '支付功能开发中', icon: 'none' })
  },
  confirmReceive(e) {
    wx.showModal({ title: '确认', content: '确认已收到商品？', success: (r) => {
      if (r.confirm) app.request({ url: `/user/orders/${e.currentTarget.dataset.id}/confirm`, method: 'POST', success: () => this.loadOrders(), fail: () => this.loadOrders() })
    }})
  },
  goToDetail(e) { wx.navigateTo({ url: `/pages/order-detail/index?id=${e.currentTarget.dataset.id}` }) },
  goProducts() { wx.switchTab({ url: '/pages/products/index' }) }
})