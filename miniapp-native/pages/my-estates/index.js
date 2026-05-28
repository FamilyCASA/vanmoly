// 我的楼盘/房产
const app = getApp()

Page({
  data: {
    loading: true,
    estates: []
  },

  onLoad() {
    this.loadEstates()
  },

  onShow() {
    this.loadEstates()
  },

  // 加载房产列表
  loadEstates() {
    this.setData({ loading: true })
    
    app.request({
      url: '/user/estates',
      success: (res) => {
        let list = []
        if (res && res.items) {
          list = res.items
        } else if (Array.isArray(res)) {
          list = res
        }
        this.setData({ estates: list, loading: false })
      },
      fail: () => {
        // 无数据时显示空状态
        this.setData({ estates: [], loading: false })
      }
    })
  },

  // 添加房产
  addEstate() {
    if (this.data.estates.length >= 5) {
      wx.showToast({ title: '最多添加5处房产', icon: 'none' })
      return
    }
    wx.navigateTo({ url: '/pages/estate-form/index' })
  },

  // 编辑房产
  editEstate(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/estate-form/index?id=${id}` })
  },

  // 删除房产
  deleteEstate(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该房产信息吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: `/user/estates/${id}`,
            method: 'DELETE',
            success: () => {
              wx.showToast({ title: '已删除', icon: 'success' })
              this.loadEstates()
            },
            fail: () => {
              // 本地删除
              const estates = this.data.estates.filter(item => item.id !== id)
              this.setData({ estates })
              wx.showToast({ title: '已删除', icon: 'success' })
            }
          })
        }
      }
    })
  },

  // 查看详情
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/estate-detail/index?id=${id}` })
  }
})