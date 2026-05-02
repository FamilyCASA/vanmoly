const app = getApp()

Page({
  data: {
    // 搜索
    searchKeyword: '',
    
    // 分类
    categories: [],
    currentCategory: '',
    
    // 筛选
    sortBy: 'default',
    showFilterModal: false,
    brands: [],
    styles: [],
    filter: {
      minPrice: '',
      maxPrice: '',
      selectedBrands: [],
      selectedStyles: []
    },
    
    // 产品列表
    products: [],
    page: 1,
    pageSize: 20,
    loading: false,
    isRefreshing: false,
    isLoadingMore: false,
    noMore: false,
    
    // 选品清单
    selectionCount: 0,
    showToast: false
  },

  onLoad() {
    this.loadCategories()
    this.loadProducts()
    this.loadFilterOptions()
    this.updateSelectionCount()
  },

  onShow() {
    this.updateSelectionCount()
  },

  // 加载分类
  async loadCategories() {
    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/materials/categories`,
        method: 'GET'
      })

      if (res.statusCode === 200) {
        const categories = [
          { id: '', name: '全部' },
          ...(res.data || [])
        ]
        this.setData({ categories })
      }
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  },

  // 加载筛选选项
  async loadFilterOptions() {
    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/materials/filter-options`,
        method: 'GET'
      })

      if (res.statusCode === 200) {
        this.setData({
          brands: res.data?.brands || [],
          styles: res.data?.styles || []
        })
      }
    } catch (error) {
      // 忽略错误
    }
  },

  // 加载产品列表
  async loadProducts(reset = false) {
    if (this.data.loading) return

    const { page, pageSize, currentCategory, sortBy, searchKeyword, filter } = this.data
    const currentPage = reset ? 1 : page

    this.setData({ 
      loading: true,
      isRefreshing: reset,
      isLoadingMore: !reset && page > 1
    })

    try {
      const params = {
        page: currentPage,
        per_page: pageSize,
        category_id: currentCategory || undefined,
        sort: sortBy,
        keyword: searchKeyword || undefined,
        min_price: filter.minPrice || undefined,
        max_price: filter.maxPrice || undefined,
        brands: filter.selectedBrands.length > 0 ? filter.selectedBrands.join(',') : undefined,
        styles: filter.selectedStyles.length > 0 ? filter.selectedStyles.join(',') : undefined
      }

      // 移除 undefined 值
      Object.keys(params).forEach(key => {
        if (params[key] === undefined) delete params[key]
      })

      const queryString = Object.keys(params)
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&')

      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/materials?${queryString}`,
        method: 'GET'
      })

      if (res.statusCode === 200) {
        const { items, total } = res.data
        const newProducts = reset ? items : [...this.data.products, ...items]
        const noMore = newProducts.length >= total

        this.setData({
          products: newProducts,
          page: currentPage + 1,
          noMore,
          loading: false,
          isRefreshing: false,
          isLoadingMore: false
        })
      } else {
        throw new Error('加载失败')
      }
    } catch (error) {
      console.error('加载产品失败:', error)
      this.setData({
        loading: false,
        isRefreshing: false,
        isLoadingMore: false
      })
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    }
  },

  // 选择分类
  selectCategory(e) {
    const { id } = e.currentTarget.dataset
    this.setData({ currentCategory: id })
    this.loadProducts(true)
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value })
  },

  // 执行搜索
  onSearch() {
    this.loadProducts(true)
  },

  // 清空搜索
  clearSearch() {
    this.setData({ searchKeyword: '' })
    this.loadProducts(true)
  },

  // 设置排序
  setSort(e) {
    const { type } = e.currentTarget.dataset
    let sortBy = type
    
    if (type === 'price_asc' && this.data.sortBy === 'price_asc') {
      sortBy = 'price_desc'
    }
    
    this.setData({ sortBy })
    this.loadProducts(true)
  },

  // 显示筛选弹窗
  showFilter() {
    this.setData({ showFilterModal: true })
  },

  // 隐藏筛选弹窗
  hideFilter() {
    this.setData({ showFilterModal: false })
  },

  // 阻止冒泡
  preventBubble() {
    // 什么都不做
  },

  // 最低价格输入
  onMinPriceInput(e) {
    this.setData({ 'filter.minPrice': e.detail.value })
  },

  // 最高价格输入
  onMaxPriceInput(e) {
    this.setData({ 'filter.maxPrice': e.detail.value })
  },

  // 切换品牌选择
  toggleBrand(e) {
    const { brand } = e.currentTarget.dataset
    const { selectedBrands } = this.data.filter
    const index = selectedBrands.indexOf(brand)
    
    if (index > -1) {
      selectedBrands.splice(index, 1)
    } else {
      selectedBrands.push(brand)
    }
    
    this.setData({ 'filter.selectedBrands': selectedBrands })
  },

  // 切换风格选择
  toggleStyle(e) {
    const { style } = e.currentTarget.dataset
    const { selectedStyles } = this.data.filter
    const index = selectedStyles.indexOf(style)
    
    if (index > -1) {
      selectedStyles.splice(index, 1)
    } else {
      selectedStyles.push(style)
    }
    
    this.setData({ 'filter.selectedStyles': selectedStyles })
  },

  // 重置筛选
  resetFilter() {
    this.setData({
      filter: {
        minPrice: '',
        maxPrice: '',
        selectedBrands: [],
        selectedStyles: []
      }
    })
  },

  // 确认筛选
  confirmFilter() {
    this.setData({ showFilterModal: false })
    this.loadProducts(true)
  },

  // 下拉刷新
  onRefresh() {
    this.loadProducts(true)
  },

  // 加载更多
  onLoadMore() {
    if (this.data.noMore || this.data.loading) return
    this.loadProducts()
  },

  // 跳转到详情
  goToDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product-detail/index?id=${id}`
    })
  },

  // 快速添加到选品
  quickAdd(e) {
    const { item } = e.currentTarget.dataset
    
    // 获取当前选品清单
    const selection = wx.getStorageSync('selection') || []
    
    const selectionItem = {
      id: item.id,
      sku_code: item.sku_code,
      name: item.name,
      main_image: item.main_image,
      sale_price: item.sale_price,
      quantity: 1,
      unit: item.unit || '件',
      added_at: new Date().toISOString()
    }
    
    // 检查是否已存在
    const exists = selection.find(s => s.id === item.id)
    
    if (exists) {
      exists.quantity += 1
      wx.showToast({
        title: '数量已更新',
        icon: 'success'
      })
    } else {
      selection.push(selectionItem)
      this.showToast()
    }
    
    wx.setStorageSync('selection', selection)
    this.updateSelectionCount()
  },

  // 显示成功提示
  showToast() {
    this.setData({ showToast: true })
    setTimeout(() => {
      this.setData({ showToast: false })
    }, 1500)
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
  }
})
