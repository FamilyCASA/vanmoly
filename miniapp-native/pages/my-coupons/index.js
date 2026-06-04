// 我的优惠券
const app = getApp()

Page({
  data: {
    activeTab: 'available',
    loading: true,
    availableList: [],
    usedList: [],
    expiredList: [],
    availableCount: 0
  },

  onLoad() { this.loadCoupons() },
  onShow() { this.loadCoupons() },

  switchTab(e) {
    this.setData({ activeTab: e.currentTarget.dataset.tab })
  },

  get currentList() {
    const { activeTab, availableList, usedList, expiredList } = this.data
    if (activeTab === 'available') return availableList
    if (activeTab === 'used') return usedList
    return expiredList
  },

  loadCoupons() {
    this.setData({ loading: true })
    app.request({
      url: '/user/coupons',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        const now = new Date()
        const availableList = list.filter(c => c.status === 'available' && new Date(c.end_time) > now)
        const usedList = list.filter(c => c.status === 'used')
        const expiredList = list.filter(c => c.status === 'expired' || new Date(c.end_time) <= now)

        const fmt = (c) => ({
          ...c,
          amount: parseFloat(c.discount || c.amount || 0),
          min_amount: parseFloat(c.min_amount || c.min_spend || 0),
          expireText: this.formatExpire(c.end_time)
        })

        this.setData({
          availableList: availableList.map(fmt),
          usedList: usedList.map(fmt),
          expiredList: expiredList.map(fmt),
          availableCount: availableList.length,
          loading: false
        })
      },
      fail: () => { this.setData({ availableList: [], usedList: [], expiredList: [], loading: false }) }
    })
  },

  useCoupon(e) {
    wx.switchTab({ url: '/pages/products/index' })
  },

  formatExpire(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getMonth()+1}月${d.getDate()}日到期`
  }
})