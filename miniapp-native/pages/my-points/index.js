// 我的积分
const app = getApp()

Page({
  data: { loading: true, points: 0, monthlyGain: 0, monthlyUsed: 0, records: [] },

  onLoad() { this.loadData() },
  onShow() { this.loadData() },

  loadData() {
    this.setData({ loading: true })
    app.request({
      url: '/user/points',
      success: (res) => {
        const data = res || {}
        const records = data.records || data.items || []
        let monthlyGain = 0, monthlyUsed = 0
        const now = new Date()
        records.forEach(r => {
          if (r.created_at) {
            const d = new Date(r.created_at)
            if (d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()) {
              if (r.amount > 0) monthlyGain += r.amount
              else monthlyUsed += Math.abs(r.amount)
            }
          }
        })
        this.setData({
          points: data.total || data.balance || 0,
          monthlyGain,
          monthlyUsed,
          records: records.map(r => ({
            ...r,
            createdAt: this.formatTime(r.created_at),
            amount: parseInt(r.amount) || 0
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ loading: false, points: 0, records: [] }) }
    })
  },

  goExchange() { wx.navigateTo({ url: '/pages/points-exchange/index' }) },
  goTasks() { wx.navigateTo({ url: '/pages/points-tasks/index' }) },
  goRules() { wx.navigateTo({ url: '/pages/points-rules/index' }) },

  formatTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }
})