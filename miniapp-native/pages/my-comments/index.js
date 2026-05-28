// 我的评论
const app = getApp()

Page({
  data: { loading: true, comments: [] },

  onLoad() { this.loadComments() },
  onShow() { this.loadComments() },

  loadComments() {
    this.setData({ loading: true })
    app.request({
      url: '/user/comments',
      success: (res) => {
        let list = res && res.items ? res.items : (Array.isArray(res) ? res : [])
        this.setData({
          comments: list.map(item => ({
            ...item,
            images: item.images ? item.images.map(img => app.resolveImageUrl(img)) : [],
            createdAt: this.formatTime(item.created_at)
          })),
          loading: false
        })
      },
      fail: () => { this.setData({ comments: [], loading: false }) }
    })
  },

  deleteComment(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该评论吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: `/user/comments/${id}`,
            method: 'DELETE',
            success: () => {
              this.setData({ comments: this.data.comments.filter(c => c.id !== id) })
              wx.showToast({ title: '已删除', icon: 'success' })
            },
            fail: () => {
              this.setData({ comments: this.data.comments.filter(c => c.id !== id) })
              wx.showToast({ title: '已删除', icon: 'success' })
            }
          })
        }
      }
    })
  },

  likeComment(e) {
    const id = e.currentTarget.dataset.id
    const comments = this.data.comments.map(c =>
      c.id === id ? { ...c, is_liked: !c.is_liked, like_count: (c.like_count || 0) + (c.is_liked ? -1 : 1) } : c
    )
    this.setData({ comments })
    app.request({ url: `/comments/${id}/like`, method: 'POST' }).catch(() => {})
  },

  previewImage(e) {
    const { urls, current } = e.currentTarget.dataset
    wx.previewImage({ current, urls })
  },

  goToCase(e) {
    wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${e.currentTarget.dataset.id}` })
  },

  goExplore() { wx.switchTab({ url: '/pages/cases/cases' }) },

  formatTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    const now = new Date()
    const diff = now - d
    if (diff < 3600000) return `${Math.floor(diff/60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff/3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff/86400000)}天前`
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})