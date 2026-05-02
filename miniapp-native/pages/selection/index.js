const app = getApp()

Page({
  data: {
    selection: [],
    groupedSelection: [],
    scheme: {
      name: '',
      room_type: '',
      area: '',
      remark: ''
    },
    roomTypes: ['客厅', '卧室', '餐厅', '书房', '儿童房', '厨房', '卫生间', '阳台', '全屋'],
    showSchemeEdit: false,
    isEditing: false,
    selectedItems: [],
    totalCount: 0,
    totalAmount: 0,
    showSuccessModal: false
  },

  onLoad() {
    this.loadSelection()
    this.loadSchemeInfo()
  },

  onShow() {
    this.loadSelection()
  },

  // 加载选品清单
  loadSelection() {
    const selection = wx.getStorageSync('selection') || []
    this.setData({ selection })
    this.groupByCategory()
    this.calculateTotal()
  },

  // 加载方案信息
  loadSchemeInfo() {
    const scheme = wx.getStorageSync('scheme_info') || {
      name: '',
      room_type: '',
      area: '',
      remark: ''
    }
    this.setData({ scheme })
  },

  // 按分类分组
  groupByCategory() {
    const { selection } = this.data
    const groups = {}

    selection.forEach(item => {
      const category = item.category || '未分类'
      if (!groups[category]) {
        groups[category] = {
          category,
          items: []
        }
      }
      groups[category].items.push(item)
    })

    this.setData({
      groupedSelection: Object.values(groups)
    })
  },

  // 计算总价
  calculateTotal() {
    const { selection } = this.data
    let totalCount = 0
    let totalAmount = 0

    selection.forEach(item => {
      totalCount += item.quantity
      totalAmount += item.sale_price * item.quantity
    })

    this.setData({
      totalCount,
      totalAmount
    })
  },

  // 返回上一页
  goBack() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        wx.switchTab({
          url: '/pages/products/index'
        })
      }
    })
  },

  // 去选品
  goToProducts() {
    wx.switchTab({
      url: '/pages/products/index'
    })
  },

  // 切换编辑模式
  toggleEdit() {
    this.setData({
      isEditing: !this.data.isEditing,
      selectedItems: []
    })
  },

  // 切换方案编辑
  toggleSchemeEdit() {
    this.setData({
      showSchemeEdit: !this.data.showSchemeEdit
    })
  },

  // 方案名称输入
  onSchemeNameInput(e) {
    this.setData({
      'scheme.name': e.detail.value
    })
    this.saveSchemeInfo()
  },

  // 房间类型选择
  onRoomTypeChange(e) {
    const { roomTypes } = this.data
    this.setData({
      'scheme.room_type': roomTypes[e.detail.value]
    })
    this.saveSchemeInfo()
  },

  // 面积输入
  onAreaInput(e) {
    this.setData({
      'scheme.area': e.detail.value
    })
    this.saveSchemeInfo()
  },

  // 备注输入
  onRemarkInput(e) {
    this.setData({
      'scheme.remark': e.detail.value
    })
    this.saveSchemeInfo()
  },

  // 保存方案信息
  saveSchemeInfo() {
    wx.setStorageSync('scheme_info', this.data.scheme)
  },

  // 减少数量
  decreaseQty(e) {
    const { item } = e.currentTarget.dataset
    const selection = this.data.selection
    const index = selection.findIndex(s =>
      s.id === item.id && s.variant_name === item.variant_name
    )

    if (index > -1 && selection[index].quantity > 1) {
      selection[index].quantity--
      wx.setStorageSync('selection', selection)
      this.loadSelection()
    }
  },

  // 增加数量
  increaseQty(e) {
    const { item } = e.currentTarget.dataset
    const selection = this.data.selection
    const index = selection.findIndex(s =>
      s.id === item.id && s.variant_name === item.variant_name
    )

    if (index > -1) {
      selection[index].quantity++
      wx.setStorageSync('selection', selection)
      this.loadSelection()
    }
  },

  // 删除单项
  deleteItem(e) {
    const { item } = e.currentTarget.dataset
    const selection = this.data.selection.filter(s =>
      !(s.id === item.id && s.variant_name === item.variant_name)
    )

    wx.setStorageSync('selection', selection)
    this.loadSelection()
  },

  // 切换选中
  toggleSelect(e) {
    const { id, variant } = e.currentTarget.dataset
    const key = id + '_' + (variant || '')
    const { selectedItems } = this.data
    const index = selectedItems.indexOf(key)

    if (index > -1) {
      selectedItems.splice(index, 1)
    } else {
      selectedItems.push(key)
    }

    this.setData({ selectedItems })
  },

  // 全选/取消全选
  toggleSelectAll() {
    const { selection, isAllSelected } = this.data

    if (isAllSelected) {
      this.setData({
        selectedItems: [],
        isAllSelected: false
      })
    } else {
      const selectedItems = selection.map(s => s.id + '_' + (s.variant_name || ''))
      this.setData({
        selectedItems,
        isAllSelected: true
      })
    }
  },

  // 删除选中
  deleteSelected() {
    const { selection, selectedItems } = this.data

    if (selectedItems.length === 0) {
      wx.showToast({
        title: '请选择要删除的商品',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: `确定删除选中的 ${selectedItems.length} 件商品吗？`,
      success: (res) => {
        if (res.confirm) {
          const newSelection = selection.filter(s => {
            const key = s.id + '_' + (s.variant_name || '')
            return !selectedItems.includes(key)
          })

          wx.setStorageSync('selection', newSelection)
          this.setData({
            selectedItems: [],
            isEditing: false
          })
          this.loadSelection()
        }
      }
    })
  },

  // 提交方案
  async submitScheme() {
    const { selection, scheme, totalAmount } = this.data

    if (selection.length === 0) {
      wx.showToast({
        title: '选品清单为空',
        icon: 'none'
      })
      return
    }

    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '需要登录',
        content: '提交方案需要先登录，是否前往登录？',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/login/index'
            })
          }
        }
      })
      return
    }

    wx.showLoading({
      title: '提交中...'
    })

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/schemes`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        data: {
          name: scheme.name || '未命名方案',
          room_type: scheme.room_type,
          area: scheme.area,
          remark: scheme.remark,
          total_amount: totalAmount,
          items: selection.map(item => ({
            sku_id: item.id,
            sku_code: item.sku_code,
            name: item.name,
            variant_name: item.variant_name,
            main_image: item.main_image,
            sale_price: item.sale_price,
            quantity: item.quantity,
            unit: item.unit
          }))
        }
      })

      wx.hideLoading()

      if (res.statusCode === 200 || res.statusCode === 201) {
        // 清空选品清单
        wx.removeStorageSync('selection')
        wx.removeStorageSync('scheme_info')

        this.setData({
          showSuccessModal: true,
          selection: [],
          groupedSelection: [],
          totalCount: 0,
          totalAmount: 0
        })
      } else {
        throw new Error(res.data?.message || '提交失败')
      }
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '提交失败',
        icon: 'error'
      })
    }
  },

  // 关闭成功弹窗
  closeSuccessModal() {
    this.setData({ showSuccessModal: false })
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
