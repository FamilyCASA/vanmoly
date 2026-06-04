// 产品中心 - 小红书瀑布流 · 暗黑深空
const app = getApp()

Page({
  data: {
    // 分类
    categories: [],       // 一级分类 [{id, name, code, icon, color, children:[...]}]
    selectedCatId: 0,     // 0=全部
    activeSubCategories: [],
    selectedSubCatId: 0,  // 0=全部

    // 搜索
    keyword: '',

    // 产品列表
    products: [],
    leftCol: [],
    rightCol: [],
    leftHeight: 0,
    rightHeight: 0,

    // 分页
    loading: false,
    loadingMore: false,
    hasMore: true,
    page: 1,
    pageSize: 12,

    // 选品单（内嵌）
    selectionCount: 0,
    selectionItems: [],
    showSelectionPanel: false,
    groupedSelection: [],
    isEditing: false,
    selectedForDelete: [],
    isAllSelected: false,
    totalCount: 0,
    totalAmount: 0,

    // 方案信息
    scheme: { name: '', room_type: '', area: '', remark: '' },
    roomTypes: ['客厅', '卧室', '餐厅', '书房', '儿童房', '厨房', '卫生间', '阳台', '全屋'],
    showSchemeEdit: false,
    showSubmitSuccess: false
  },

  onLoad() {
    this.loadSelectionFromStorage()
    this.fetchCategories()
    this.fetchProducts()
  },

  onShow() {
    this.loadSelectionFromStorage()
  },

  // ===== 选品单存储 =====
  loadSelectionFromStorage() {
    try {
      const items = wx.getStorageSync('selection') || []
      this.setData({
        selectionItems: items,
        selectionCount: items.reduce((sum, i) => sum + (i.quantity || 1), 0)
      })
      this.markSelectedProducts()
      this.groupAndCalculate()
    } catch (e) { console.log('读取选品单失败', e) }
  },

  markSelectedProducts() {
    const ids = new Set(this.data.selectionItems.map(i => i.id))
    const updateCols = (col) => col.map(p => ({ ...p, _selected: ids.has(p.id) }))
    if (this.data.leftCol.length || this.data.rightCol.length) {
      this.setData({
        leftCol: updateCols(this.data.leftCol),
        rightCol: updateCols(this.data.rightCol)
      })
    }
  },

  // ===== 加入/移出选品单 =====
  toggleSelection(e) {
    const id = e.currentTarget.dataset.id
    const { products, selectionItems } = this.data
    const product = products.find(p => p.id === id)
    if (!product) return

    let items = [...selectionItems]
    const existIdx = items.findIndex(i => i.id === id)

    if (existIdx > -1) {
      items.splice(existIdx, 1)
    } else {
      items.push({
        id: product.id,
        sku_code: product.sku_code || '',
        name: product.name,
        brand: product.brand || '',
        category: product.category_name || '',
        variant_name: '',
        main_image: product.main_image || '',
        sale_price: product.sale_price || 0,
        unit: product.unit || '件',
        quantity: 1
      })
    }

    wx.setStorageSync('selection', items)
    this.setData({
      selectionItems: items,
      selectionCount: items.reduce((sum, i) => sum + (i.quantity || 1), 0)
    })
    this.markSelectedProducts()
    this.groupAndCalculate()
    wx.showToast({ title: existIdx > -1 ? '已移出' : '已加入选品单', icon: 'none' })
  },

  // ===== 选品面板操作 =====
  openSelectionPanel() {
    this.loadSelectionFromStorage()
    this.setData({ showSelectionPanel: true })
  },

  closeSelectionPanel() {
    this.setData({ showSelectionPanel: false, isEditing: false, selectedForDelete: [], isAllSelected: false })
  },

  groupAndCalculate() {
    const { selectionItems } = this.data
    // 分组
    const groups = {}
    selectionItems.forEach(item => {
      const cat = item.category || '未分类'
      if (!groups[cat]) groups[cat] = { category: cat, items: [] }
      groups[cat].items.push(item)
    })
    // 计算总价
    let totalCount = 0, totalAmount = 0
    selectionItems.forEach(item => {
      totalCount += item.quantity
      totalAmount += item.sale_price * item.quantity
    })
    this.setData({
      groupedSelection: Object.values(groups),
      totalCount,
      totalAmount
    })
  },

  decreaseQty(e) {
    const item = e.currentTarget.dataset.item
    const items = [...this.data.selectionItems]
    const idx = items.findIndex(s => s.id === item.id && s.variant_name === item.variant_name)
    if (idx > -1 && items[idx].quantity > 1) {
      items[idx].quantity--
      wx.setStorageSync('selection', items)
      this.loadSelectionFromStorage()
    }
  },

  increaseQty(e) {
    const item = e.currentTarget.dataset.item
    const items = [...this.data.selectionItems]
    const idx = items.findIndex(s => s.id === item.id && s.variant_name === item.variant_name)
    if (idx > -1) {
      items[idx].quantity++
      wx.setStorageSync('selection', items)
      this.loadSelectionFromStorage()
    }
  },

  deleteItem(e) {
    const item = e.currentTarget.dataset.item
    const items = this.data.selectionItems.filter(s => !(s.id === item.id && s.variant_name === item.variant_name))
    wx.setStorageSync('selection', items)
    this.loadSelectionFromStorage()
  },

  toggleEdit() {
    this.setData({ isEditing: !this.data.isEditing, selectedForDelete: [], isAllSelected: false })
  },

  toggleSelect(e) {
    const { id, variant } = e.currentTarget.dataset
    const key = id + '_' + (variant || '')
    const arr = [...this.data.selectedForDelete]
    const idx = arr.indexOf(key)
    if (idx > -1) arr.splice(idx, 1)
    else arr.push(key)
    this.setData({ selectedForDelete: arr, isAllSelected: arr.length === this.data.selectionItems.length })
  },

  toggleSelectAll() {
    const { selectionItems, isAllSelected } = this.data
    if (isAllSelected) {
      this.setData({ selectedForDelete: [], isAllSelected: false })
    } else {
      this.setData({
        selectedForDelete: selectionItems.map(s => s.id + '_' + (s.variant_name || '')),
        isAllSelected: true
      })
    }
  },

  deleteSelected() {
    if (this.data.selectedForDelete.length === 0) return
    wx.showModal({
      title: '确认删除',
      content: '确定删除选中的商品吗？',
      success: (res) => {
        if (res.confirm) {
          const delSet = new Set(this.data.selectedForDelete)
          const items = this.data.selectionItems.filter(s => !delSet.has(s.id + '_' + (s.variant_name || '')))
          wx.setStorageSync('selection', items)
          this.setData({ isEditing: false, selectedForDelete: [], isAllSelected: false })
          this.loadSelectionFromStorage()
        }
      }
    })
  },

  // ===== 方案信息 =====
  toggleSchemeEdit() {
    this.setData({ showSchemeEdit: !this.data.showSchemeEdit })
  },

  onSchemeNameInput(e) { this.setData({ 'scheme.name': e.detail.value }) },
  onRoomTypeChange(e) { this.setData({ 'scheme.room_type': this.data.roomTypes[e.detail.value] }) },
  onAreaInput(e) { this.setData({ 'scheme.area': e.detail.value }) },
  onRemarkInput(e) { this.setData({ 'scheme.remark': e.detail.value }) },

  // ===== 提交方案（需登录）=====
  submitScheme() {
    const { selectionItems } = this.data
    if (selectionItems.length === 0) { wx.showToast({ title: '选品清单为空', icon: 'none' }); return }

    const token = wx.getStorageSync('token')
    if (!token) {
      this.closeSelectionPanel()
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }

    const { scheme, totalAmount } = this.data
    wx.showLoading({ title: '提交中...' })
    app.request({
      url: '/schemes',
      method: 'POST',
      data: {
        name: scheme.name || '未命名方案',
        room_type: scheme.room_type,
        area: scheme.area,
        remark: scheme.remark,
        total_amount: totalAmount,
        items: selectionItems.map(item => ({
          sku_id: item.id,
          sku_code: item.sku_code,
          name: item.name,
          variant_name: item.variant_name,
          main_image: item.main_image,
          sale_price: item.sale_price,
          quantity: item.quantity,
          unit: item.unit
        }))
      },
      success: () => {
        wx.hideLoading()
        wx.removeStorageSync('selection')
        wx.removeStorageSync('scheme_info')
        this.setData({
          showSubmitSuccess: true,
          selectionItems: [],
          groupedSelection: [],
          totalCount: 0,
          totalAmount: 0,
          selectionCount: 0
        })
        this.markSelectedProducts()
      },
      fail: (err) => {
        wx.hideLoading()
        wx.showToast({ title: (err && err.message) || '提交失败', icon: 'error' })
      }
    })
  },

  closeSubmitSuccess() {
    this.setData({ showSubmitSuccess: false, showSelectionPanel: false })
  },

  // ===== 获取分类 =====
  fetchCategories() {
    app.request({
      url: '/materials/categories',
      success: (res) => {
        const cats = Array.isArray(res) ? res : []
        this.setData({ categories: cats })
      },
      fail: () => {
        console.log('分类加载失败，使用空分类')
      }
    })
  },

  // ===== 选择一级分类 =====
  selectCategory(e) {
    const id = e.currentTarget.dataset.id
    const cat = this.data.categories.find(c => c.id === id)

    this.setData({
      selectedCatId: id,
      selectedSubCatId: 0,
      activeSubCategories: cat && cat.children ? cat.children : [],
      page: 1,
      keyword: ''
    })
    this.fetchProducts()
  },

  // ===== 选择二级分类 =====
  selectSubCategory(e) {
    const id = e.currentTarget.dataset.id
    this.setData({
      selectedSubCatId: this.data.selectedSubCatId === id ? 0 : id,
      page: 1
    })
    this.fetchProducts()
  },

  // ===== 搜索 =====
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch(e) {
    this.setData({ page: 1 })
    this.fetchProducts()
  },

  clearSearch() {
    this.setData({ keyword: '', page: 1 })
    this.fetchProducts()
  },

  resetFilters() {
    this.setData({
      selectedCatId: 0,
      selectedSubCatId: 0,
      activeSubCategories: [],
      keyword: '',
      page: 1
    })
    this.fetchProducts()
  },

  // ===== 获取产品列表 =====
  fetchProducts(isMore = false) {
    if (isMore) this.setData({ loadingMore: true })
    else this.setData({ loading: true })

    const { selectedCatId, selectedSubCatId, keyword, page, pageSize } = this.data
    const params = {
      page: isMore ? page + 1 : 1,
      page_size: pageSize,
      is_public: 1
    }

    // 用二级分类优先，否则用一级分类
    const categoryId = selectedSubCatId || (selectedCatId > 0 ? selectedCatId : null)
    if (categoryId) params.category_id = categoryId
    if (keyword) params.keyword = keyword

    app.request({
      url: '/materials',
      data: params,
      success: (res) => {
        console.log('[PRODUCTS] API返回:', res?.items?.length || 0, '条, total:', res?.total)
        let items = res.items || res || []
        const total = res.total || items.length

        // 预处理
        const selectedIds = new Set(this.data.selectionItems.map(i => i.id))
        items = items.map(item => ({
          ...item,
          main_image: item.main_image ? app.resolveImageUrl(item.main_image) : '',
          _displayPrice: this.formatPrice(item.sale_price),
          _selected: selectedIds.has(item.id)
        }))

        const newProducts = isMore ? [...this.data.products, ...items] : items

        this.setData({
          products: newProducts,
          hasMore: newProducts.length < total,
          page: params.page,
          loading: false,
          loadingMore: false
        })

        this.buildWaterfall(isMore ? items : newProducts, isMore)
      },
      fail: (err) => {
        console.warn('[PRODUCTS] API加载失败', err)
        this.setData({
          products: [],
          hasMore: false,
          loading: false,
          loadingMore: false
        })
      }
    })
  },

  // ===== 瀑布流布局 =====
  buildWaterfall(items, isAppend) {
    if (!items || items.length === 0) return

    let left = isAppend ? [...this.data.leftCol] : []
    let right = isAppend ? [...this.data.rightCol] : []
    let lH = this.data.leftHeight
    let rH = this.data.rightHeight

    items.forEach((item, idx) => {
      // 产品图片为1:1，估算高度基于是否有品牌行、规格行
      const estHeight = 280 + (item.brand ? 30 : 0) + (item.has_variants ? 30 : 0)
      const itemWithIndex = { ...item, _index: isAppend ? this.data.products.length - items.length + idx : idx }

      if (lH <= rH) {
        left.push(itemWithIndex)
        lH += estHeight
      } else {
        right.push(itemWithIndex)
        rH += estHeight
      }
    })

    this.setData({
      leftCol: left,
      rightCol: right,
      leftHeight: lH,
      rightHeight: rH
    })
  },

  // ===== 格式化价格 =====
  formatPrice(price) {
    if (!price && price !== 0) return '0'
    return Number(price).toLocaleString()
  },

  // ===== 加载更多 =====
  loadMore() {
    if (!this.data.hasMore || this.data.loadingMore) return
    this.fetchProducts(true)
  },

  // ===== 跳转详情（需登录）=====
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '查看产品详情需要先登录',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' })
          }
        }
      })
      return
    }
    wx.navigateTo({ url: `/pages/product-detail/index?id=${id}` })
  },

  // ===== 跳转选品单（改为内嵌面板）=====
  goToSelection() {
    this.openSelectionPanel()
  },

  // ===== 下拉刷新 =====
  onPullDownRefresh() {
    this.setData({ page: 1 })
    this.fetchProducts()
    wx.stopPullDownRefresh()
  },

  onShareAppMessage() {
    return { title: 'D&B 帝标·设记家 - 甄选好物', path: '/pages/products/index' }
  }
})
