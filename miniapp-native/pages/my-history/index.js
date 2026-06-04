// 浏览历史
const app = getApp()

Page({
  data: { loading: true, historyList: [] },

  onLoad() { this.loadHistory() },
  onShow() { this.loadHistory() },

  loadHistory() {
    this.setData({ loading: true })
    app.request({
      url: '/user/history',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        // 按日期分组
        const grouped = this.groupByDate(list.map(item => ({
          ...item,
          cover: item.cover_image || item.main_image ? app.resolveImageUrl(item.cover_image || item.main_image) : '',
          typeText: item.type === 'case' ? '案例' : item.type === 'product' ? '产品' : item.type === 'designer' ? '设计师' : '其他',
          viewTime: this.formatTime(item.created_at || item.viewed_at)
        })))
        this.setData({ historyList: grouped, loading: false })
      },
      fail: () => { this.setData({ historyList: [], loading: false }) }
    })
  },

  groupByDate(list) {
    const map = {}
    list.forEach(item => {
      const d = new Date(item.created_at || item.viewed_at)
      const dateStr = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
      const today = new Date()
      const todayStr = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`
      const yesterday = new Date(today - 86400000)
      const yesterdayStr = `${yesterday.getFullYear()}-${String(yesterday.getMonth()+1).padStart(2,'0')}-${String(yesterday.getDate()).padStart(2,'0')}`
      
      let label = dateStr
      if (dateStr === todayStr) label = '今天'
      else if (dateStr === yesterdayStr) label = '昨天'
      
      if (!map[label]) map[label] = { date: label, items: [] }
      map[label].items.push(item)
    })
    return Object.values(map)
  },

  clearHistory() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有浏览记录吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: '/user/history',
            method: 'DELETE',
            success: () => {
              this.setData({ historyList: [] })
              wx.showToast({ title: '已清空', icon: 'success' })
            },
            fail: () => {
              this.setData({ historyList: [] })
              wx.showToast({ title: '已清空', icon: 'success' })
            }
          })
        }
      }
    })
  },

  goToDetail(e) {
    const { type, id } = e.currentTarget.dataset
    if (type === 'case') {
      wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${id}` })
    } else if (type === 'product') {
      wx.navigateTo({ url: `/pages/product-detail/index?id=${id}` })
    } else if (type === 'designer') {
      wx.navigateTo({ url: `/pages/designer/index?id=${id}` })
    }
  },

  goExplore() { wx.switchTab({ url: '/pages/cases/cases' }) },

  formatTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }
})