// 意见反馈
const app = getApp()

Page({
  data: {
    types: ['功能建议', '体验问题', '内容错误', '其他'],
    feedbackType: '功能建议',
    content: '',
    images: [],
    contact: ''
  },

  selectType(e) { this.setData({ feedbackType: e.currentTarget.dataset.type }) },
  onContentInput(e) { this.setData({ content: e.detail.value }) },
  onContactInput(e) { this.setData({ contact: e.detail.value }) },

  addImage() {
    wx.chooseMedia({
      count: 3 - this.data.images.length,
      mediaType: ['image'],
      sizeType: ['compressed'],
      success: (res) => {
        const newImages = res.tempFiles.map(f => f.tempFilePath)
        this.setData({ images: [...this.data.images, ...newImages] })
      }
    })
  },

  deleteImage(e) {
    const index = e.currentTarget.dataset.index
    const images = [...this.data.images]
    images.splice(index, 1)
    this.setData({ images })
  },

  submitFeedback() {
    const { feedbackType, content, contact, images } = this.data
    if (!content.trim()) {
      wx.showToast({ title: '请输入反馈内容', icon: 'none' })
      return
    }
    wx.showLoading({ title: '提交中...' })
    app.request({
      url: '/feedback',
      method: 'POST',
      data: { type: feedbackType, content, contact },
      success: () => {
        wx.hideLoading()
        wx.showToast({ title: '感谢您的反馈', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1500)
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '感谢您的反馈', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1500)
      }
    })
  }
})