const app = getApp()

Page({
  data: {
    loading: true,
    product: null,
    images: [],
    currentImageIndex: 0,
    variants: [],
    selectedVariant: null,
    recommendations: [],
    quantity: 1,
    selectionCount: 0,
    showNavBar: false,
    showShareModal: false,
    isAdding: false
  },

  onLoad(options) {
    const { id } = options
    if (id) {
      this.loadProductDetail(id)
      this.loadRecommendations(id)
    }
    this.updateSelectionCount()
  },

  onShow() {
    this.updateSelectionCount()
  },

  onPageScroll(e) {
    const scrollTop = e.scrollTop
    const showNavBar = scrollTop > 200
    
    if (showNavBar !== this.data.showNavBar) {
      this.setData({ showNavBar })
    }
  },

  onShareAppMessage() {
    const { product } = this.data
    return {
      title: product?.name || 'D&B 帝标|设记家精选产品',
      path: `/pages/product-detail/index?id=${product?.id}`,
      imageUrl: product?.main_image
    }
  },

  // 加载产品详情
  loadProductDetail(id) {
    this.setData({ loading: true })
    
    app.request({
      url: `/materials/${id}`,
      success: (product) => {
        
        // 处理图片列表
        const images = []
        if (product.main_image) images.push(app.resolveImageUrl(product.main_image))
        if (product.sub_image) images.push(app.resolveImageUrl(product.sub_image))
        if (product.images && Array.isArray(product.images)) {
          images.push(...product.images.map(img => app.resolveImageUrl(img)))
        }
        
        // 处理规格变体
        const variants = product.variants || []
        const selectedVariant = variants.length > 0 ? variants[0] : null

        // 计算折扣
        const discountPercent = product.market_price > product.sale_price
          ? Math.round((1 - product.sale_price / product.market_price) * 100)
          : 0

        this.setData({
          product,
          discountPercent,
          images: images.length > 0 ? images : ['/images/placeholder.png'],
          variants,
          selectedVariant,
          loading: false
        })

        wx.setNavigationBarTitle({
          title: product.name
        })
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'error' })
        this.setData({ loading: false })
      }
    })
  },

  // 加载推荐产品
  loadRecommendations(id) {
    app.request({
      url: `/materials/${id}/recommendations`,
      success: (res) => {
        this.setData({
          recommendations: Array.isArray(res) ? res : []
        })
      },
      fail: () => {}
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

  // 图片切换
  onImageChange(e) {
    this.setData({
      currentImageIndex: e.detail.current
    })
  },

  // 预览图片
  previewImage(e) {
    const { index } = e.currentTarget.dataset
    const { images } = this.data
    
    wx.previewImage({
      current: images[index],
      urls: images
    })
  },

  // 选择规格
  selectVariant(e) {
    const { variant } = e.currentTarget.dataset
    
    if (variant.stock <= 0) {
      wx.showToast({
        title: '该规格暂时缺货',
        icon: 'none'
      })
      return
    }
    
    this.setData({
      selectedVariant: variant,
      quantity: 1
    })
  },

  // 减少数量
  decreaseQty() {
    if (this.data.quantity > 1) {
      this.setData({
        quantity: this.data.quantity - 1
      })
    }
  },

  // 增加数量
  increaseQty() {
    const { selectedVariant, product, quantity } = this.data
    const maxStock = selectedVariant ? selectedVariant.stock : product.stock
    
    if (maxStock && quantity >= maxStock) {
      wx.showToast({
        title: '已达到最大库存',
        icon: 'none'
      })
      return
    }
    
    this.setData({
      quantity: quantity + 1
    })
  },

  // 添加到选品清单
  addToSelection() {
    const { product, selectedVariant, quantity } = this.data
    
    // 获取当前选品清单
    const selection = wx.getStorageSync('selection') || []
    
    const selectionItem = {
      id: product.id,
      sku_code: selectedVariant ? selectedVariant.sku_code : product.sku_code,
      name: product.name,
      variant_name: selectedVariant ? selectedVariant.name : null,
      main_image: selectedVariant && selectedVariant.image ? selectedVariant.image : product.main_image,
      sale_price: selectedVariant ? selectedVariant.sale_price : product.sale_price,
      quantity: quantity,
      unit: product.unit || '件',
      added_at: new Date().toISOString()
    }
    
    // 检查是否已存在（同规格）
    const existingIndex = selection.findIndex(s => 
      s.id === selectionItem.id && s.variant_name === selectionItem.variant_name
    )
    
    if (existingIndex > -1) {
      selection[existingIndex].quantity += quantity
    } else {
      selection.push(selectionItem)
    }
    
    wx.setStorageSync('selection', selection)
    
    // 显示成功状态
    this.setData({
      isAdding: true,
      selectionCount: selection.length
    })
    
    setTimeout(() => {
      this.setData({ isAdding: false })
    }, 1500)
    
    wx.showToast({
      title: '已加入选品清单',
      icon: 'success'
    })
  },

  // 更新选品数量
  updateSelectionCount() {
    const selection = wx.getStorageSync('selection') || []
    this.setData({ selectionCount: selection.length })
  },

  // 跳转到选品清单
  goToSelection() {
    wx.navigateTo({
      url: '/pages/selection/index'
    })
  },

  // 跳转到产品详情
  goToProduct(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product-detail/index?id=${id}`
    })
  },

  // 联系客服
  contactService() {
    // 复制客服微信号到剪贴板
    wx.setClipboardData({
      data: 'vanmoly_service',
      success: () => {
        wx.showModal({
          title: '联系客服',
          content: '客服微信号已复制到剪贴板，请添加微信咨询',
          showCancel: false
        })
      }
    })
  },

  // 显示分享弹窗
  handleShare() {
    this.setData({ showShareModal: true })
  },

  // 隐藏分享弹窗
  hideShareModal() {
    this.setData({ showShareModal: false })
  },

  // 阻止冒泡
  preventBubble() {
    // 什么都不做
  },

  // 复制链接
  copyLink() {
    const { product } = this.data
    const url = `https://vanmoly.com/product/${product.id}`
    
    wx.setClipboardData({
      data: url,
      success: () => {
        wx.showToast({
          title: '链接已复制',
          icon: 'success'
        })
        this.hideShareModal()
      }
    })
  },

  // 生成海报
  generatePoster() {
    wx.showToast({
      title: '海报生成中...',
      icon: 'loading'
    })
    
    // 这里可以调用后端生成海报的 API
    setTimeout(() => {
      wx.showToast({
        title: '海报已保存',
        icon: 'success'
      })
      this.hideShareModal()
    }, 1500)
  }
})
