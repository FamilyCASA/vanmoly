// 我的订阅
const app = getApp()

Page({
  data: {
    loading: true,
    subscriptions: []
  },

  onLoad() { this.loadSubscriptions() },
  onShow() { this.loadSubscriptions() },

  loadSubscriptions() {
    this.setData({ loading: true })
    app.request({
      url: '/user/subscriptions',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          subscriptions: list.map(item => ({
            ...item,
            cover: item.cover_image || item.hero_image ? app.resolveImageUrl(item.cover_image || item.hero_image) : '',
            notifyStatusText: item.notify_status === 'paused' ? '已暂停' : '订阅中',
            latestUpdateText: this.formatTime(item.latest_update || item.updated_at)
          })),
          loading: false
        })
      },
      fail: () => {
        this.setData({ subscriptions: [], loading: false })
      }
    })
  },

  toggleSubscription(e) {
    const id = e.currentTarget.dataset.id
    const sub = this.data.subscriptions.find(s => s.id === id)
    if (!sub) return

    const newStatus = sub.notify_status === 'paused' ? 'active' : 'paused'
    app.request({
      url: `/user/subscriptions/${id}`,
      method: 'PUT',
      data: { notify_status: newStatus },
      success: () => {
        const subscriptions = this.data.subscriptions.map(s =>
          s.id === id ? { ...s, notify_status: newStatus, notifyStatusText: newStatus === 'paused' ? '已暂停' : '订阅中' } : s
        )
        this.setData({ subscriptions })
        wx.showToast({ title: newStatus === 'paused' ? '已暂停' : '已恢复', icon: 'success' })
      },
      fail: () => {
        wx.showToast({ title: '操作失败', icon: 'none' })
      }
    })
  },

  goToCase(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${id}` })
  },

  goExplore() {
    wx.switchTab({ url: '/pages/cases/cases' })
  },

  formatTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    const now = new Date()
    const diff = now - d
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff/60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff/3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff/86400000)}天前`
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})