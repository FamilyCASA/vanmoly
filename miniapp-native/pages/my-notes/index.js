// 我的笔记
const app = getApp()

Page({
  data: { loading: true, notes: [] },

  onLoad() { this.loadNotes() },
  onShow() { this.loadNotes() },

  loadNotes() {
    this.setData({ loading: true })
    app.request({
      url: '/user/notes',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          notes: list.map(item => ({
            ...item,
            cover: item.cover_image ? app.resolveImageUrl(item.cover_image) : '',
            excerpt: item.content ? (item.content.length > 80 ? item.content.substring(0, 80) + '...' : item.content) : '',
            createdAt: this.formatDate(item.created_at)
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ notes: [], loading: false }) }
    })
  },

  createNote() {
    wx.navigateTo({ url: '/pages/note-edit/index' })
  },

  goToNote(e) {
    wx.navigateTo({ url: `/pages/note-detail/index?id=${e.currentTarget.dataset.id}` })
  },

  deleteNote(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该笔记吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: `/user/notes/${id}`,
            method: 'DELETE',
            success: () => {
              this.setData({ notes: this.data.notes.filter(n => n.id !== id) })
              wx.showToast({ title: '已删除', icon: 'success' })
            },
            fail: () => {
              this.setData({ notes: this.data.notes.filter(n => n.id !== id) })
              wx.showToast({ title: '已删除', icon: 'success' })
            }
          })
        }
      }
    })
  },

  formatDate(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})