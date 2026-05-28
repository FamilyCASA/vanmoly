// 案例列表 - 小红书瀑布流 · 杂志封面风格
const app = getApp()

Page({
  data: {
    // 精选案例 Hero
    featuredCase: null,
    heroImages: [],
    heroIndex: 0,

    // 筛选 - 服务阶段（从 /workflows/public/phases API 动态加载）
    workflowPhases: [],
    selectedPhase: '',
    expandedPhase: '',
    phaseNodes: [],
    selectedNodeId: null,

    // 筛选 - 氛围
    atmospheres: [
      { key: 'warm', label: '温馨', value: '温馨', count: 0, color: '#d4a574', textColor: '#fff' },
      { key: 'fresh', label: '清新', value: '清新', count: 0, color: '#7d9c5a', textColor: '#fff' },
      { key: 'minimalist', label: '简约', value: '简约', count: 0, color: '#9e9e9e', textColor: '#fff' },
      { key: 'romantic', label: '浪漫', value: '浪漫', count: 0, color: '#e8b4bc', textColor: '#5c3a3a' },
      { key: 'elegant', label: '雅致', value: '雅致', count: 0, color: '#c9a96e', textColor: '#fff' },
      { key: 'steady', label: '沉稳', value: '沉稳', count: 0, color: '#2d4a3e', textColor: '#fff' }
    ],
    selectedAtmosphere: '',

    // 筛选 - 预算
    budgetSegments: [
      { key: 's1', label: '5万以下', min: 0, max: 50000 },
      { key: 's2', label: '5-15万', min: 50000, max: 150000 },
      { key: 's3', label: '15-25万', min: 150000, max: 250000 },
      { key: 's4', label: '25-35万', min: 250000, max: 350000 },
      { key: 's5', label: '35-45万', min: 350000, max: 450000 },
      { key: 's6', label: '45-65万', min: 45000, max: 650000 },
      { key: 's7', label: '65-85万', min: 650000, max: 850000 },
      { key: 's8', label: '85万以上', min: 850000, max: null }
    ],
    selectedBudget: null,

    // 筛选 - 颜色
    colorPalette: [],
    selectedColor: '',

    // 案例列表
    cases: [],
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

    // 订阅弹窗
    showSubscribe: false,
    subscribeCase: {},
    subscribePhone: '',
    subscribing: false
  },

  onLoad() {
    this.fetchWorkflowPhases()
    this.fetchFilterOptions()
    this.fetchCases()
  },

  // ===== 图片URL解析 =====
  resolveImg(path) {
    return app.resolveImageUrl(path)
  },

  // ===== 加载服务阶段（引用首页同一 API）=====
  fetchWorkflowPhases() {
    app.request({
      url: '/workflows/public/phases',
      success: (res) => {
        if (res && res.phases) {
          const phases = res.phases.map(p => ({
            key: p.code,           // 模板用 item.key
            label: p.name,        // 模板用 item.label
            code: p.code,         // 筛选参数用 code
            name: p.name,
            color: p.color || '',
            sort_order: p.sort_order || 0,
            count: 0,             // count 由 fetchFilterOptions 合并
            nodes: (p.nodes || []).map(n => ({
              ...n,
              code: n.code || n.node_code || '',
              name: n.name || n.node_name || ''
            }))
          }))
          this.setData({ workflowPhases: phases })
          // 如果筛选选项已先加载完，补合并 count
          this._mergePhaseCounts()
        }
      },
      fail: () => {
        console.warn('[CASES] 加载服务阶段失败')
      }
    })
  },

  // 合并阶段计数（来自 /public/cases/filters 的 progress_options）
  _mergePhaseCounts() {
    if (!this._pendingPhaseCounts || this.data.workflowPhases.length === 0) return
    const optMap = {}
    this._pendingPhaseCounts.forEach(o => { optMap[o.key] = o.count || 0 })
    const phases = this.data.workflowPhases.map(p => ({
      ...p,
      count: optMap[p.code] || optMap[p.key] || 0
    }))
    this.setData({ workflowPhases: phases })
  },

  // ===== 格式化价格 =====
  formatPrice(price) {
    if (!price) return '0'
    const num = parseFloat(price)
    return num >= 10000 ? (num / 10000).toFixed(1) : num.toLocaleString()
  },

  // ===== 氛围渐变 fallback =====
  getAtmosphereGradient(atm) {
    const map = {
      '温馨': 'linear-gradient(135deg, #f5e6d3 0%, #d4a574 100%)',
      '清新': 'linear-gradient(135deg, #e8f5e9 0%, #81c784 100%)',
      '简约': 'linear-gradient(135deg, #f5f5f5 0%, #9e9e9e 100%)',
      '浪漫': 'linear-gradient(135deg, #fce4ec 0%, #f48fb1 100%)',
      '雅致': 'linear-gradient(135deg, #e8eaf6 0%, #7986cb 100%)',
      '沉稳': 'linear-gradient(135deg, #37474f 0%, #546e7a 100%)'
    }
    return map[atm] || 'linear-gradient(135deg, #1a1a2e 0%, #0a0a1a 100%)'
  },

  // ===== 获取筛选选项 =====
  fetchFilterOptions() {
    app.request({
      url: '/public/cases/filters',
      success: (res) => {
        // app.request 已自动提取 data 字段，res 直接是业务数据
        if (res.atmospheres) {
          const atms = this.data.atmospheres.map(a => {
            const found = res.atmospheres.find(f => f.key === a.value)
            return { ...a, count: found ? found.count || 0 : 0 }
          })
          this.setData({ atmospheres: atms })
        }
        // 预算统计
        // 服务阶段计数 — 保存到临时变量，等 workflowPhases 加载完合并
        if (res.progress_options) {
          this._pendingPhaseCounts = res.progress_options
          this._mergePhaseCounts()
        }
      },
      fail: () => {
        console.log('筛选选项加载失败，使用默认值')
      }
    })
  },

  // ===== Hero 轮播 =====
  onHeroSlide(e) {
    this.setData({ heroIndex: e.detail.current })
  },

  updateHeroImages(caseItem) {
    const images = []
    if (caseItem.hero_images && caseItem.hero_images.length > 0) {
      caseItem.hero_images.forEach(img => {
        const resolved = this.resolveImg(img)
        if (resolved && !images.includes(resolved)) images.push(resolved)
      })
    } else {
      if (caseItem.cover_image) {
        images.push(this.resolveImg(caseItem.cover_image))
      }
      if (caseItem.gallery && Array.isArray(caseItem.gallery)) {
        caseItem.gallery.slice(0, 3).forEach(img => {
          const resolved = this.resolveImg(img)
          if (resolved && !images.includes(resolved)) images.push(resolved)
        })
      }
    }
    this.setData({ heroImages: images, heroIndex: 0 })
  },

  // ===== 筛选操作 =====
  selectPhase(e) {
    const key = e.currentTarget.dataset.key
    if (this.data.selectedPhase === key) {
      // 再次点击 = 展开/收起节点
      if (this.data.expandedPhase === key) {
        this.setData({ expandedPhase: '', phaseNodes: [], selectedNodeId: null })
      } else {
        this.setData({ expandedPhase: key })
        this.fetchPhaseNodes(key)
      }
      return
    }
    this.setData({
      selectedPhase: key,
      expandedPhase: key,
      selectedNodeId: null,
      page: 1
    })
    this.fetchPhaseNodes(key)
    this.fetchCases()
  },

  clearPhaseFilter() {
    this.setData({
      selectedPhase: '',
      expandedPhase: '',
      phaseNodes: [],
      selectedNodeId: null,
      page: 1
    })
    this.fetchCases()
  },

  selectNode(e) {
    const id = e.currentTarget.dataset.id
    this.setData({
      selectedNodeId: this.data.selectedNodeId === id ? null : id,
      page: 1
    })
    this.fetchCases()
  },

  fetchPhaseNodes(phaseKey) {
    // 直接使用 API 返回的阶段节点
    const phase = this.data.workflowPhases.find(p => p.key === phaseKey)
    if (!phase || !phase.nodes) {
      this.setData({ phaseNodes: [] })
      return
    }
    const nodes = phase.nodes.map(n => ({
      id: n.code || n.node_code || n.name || n.node_name,
      node_name: n.name || n.node_name || '',
      phase: phase.code,
      phaseTag: (phase.label || phase.name || '').substring(0, 2)
    }))
    this.setData({ phaseNodes: nodes })
  },

  selectAtmosphere(e) {
    const value = e.currentTarget.dataset.value
    this.setData({
      selectedAtmosphere: this.data.selectedAtmosphere === value ? '' : value,
      page: 1,
      featuredCase: null
    })
    this.fetchCases()
  },

  selectBudget(e) {
    const seg = e.currentTarget.dataset.seg
    if (typeof seg === 'string') {
      this.setData({ selectedBudget: null, page: 1 })
    } else {
      this.setData({
        selectedBudget: this.data.selectedBudget && this.data.selectedBudget.key === seg.key ? null : seg,
        page: 1
      })
    }
    this.fetchCases()
  },

  clearBudgetFilter() {
    this.setData({ selectedBudget: null, page: 1 })
    this.fetchCases()
  },

  selectColor(e) {
    const hex = e.currentTarget.dataset.hex
    this.setData({
      selectedColor: this.data.selectedColor === hex ? '' : hex,
      page: 1
    })
    this.fetchCases()
  },

  clearColorFilter() {
    this.setData({ selectedColor: '', page: 1 })
    this.fetchCases()
  },

  resetAllFilters() {
    this.setData({
      selectedPhase: '',
      expandedPhase: '',
      phaseNodes: [],
      selectedNodeId: null,
      selectedAtmosphere: '',
      selectedBudget: null,
      selectedColor: '',
      page: 1,
      featuredCase: null
    })
    this.fetchCases()
  },

  // ===== 获取案例列表 =====
  fetchCases(isMore = false) {
    if (isMore) this.setData({ loadingMore: true })
    else this.setData({ loading: true })

    const { selectedPhase, selectedAtmosphere, selectedBudget, selectedColor, selectedNodeId, page, pageSize } = this.data
    const params = {
      page: isMore ? page + 1 : 1,
      per_page: pageSize
    }

    if (selectedPhase) params.progress = selectedPhase
    if (selectedAtmosphere) params.atmosphere = selectedAtmosphere
    if (selectedBudget) {
      params.price_min = selectedBudget.min
      params.price_max = selectedBudget.max
    }
    if (selectedColor) params.color = selectedColor
    if (selectedNodeId) params.node_id = selectedNodeId

    app.request({
      url: '/public/cases',
      data: params,
      success: (res) => {
        let items = res.items || res || []
        const total = res.total || items.length

        // 预处理图片URL和价格
        items = items.map((item, idx) => ({
          ...item,
          cover_image: item.cover_image ? this.resolveImg(item.cover_image) : '',
          _price: this.formatPrice(item.total_price),
          _gradient: this.getAtmosphereGradient(item.atmosphere)
        }))

        const newCases = isMore ? [...this.data.cases, ...items] : items

        // 设置精选案例
        if (!isMore && items.length > 0 && !this.data.featuredCase) {
          const featured = items[0]
          this.setData({ featuredCase: featured })
          this.updateHeroImages(featured)
        }

        this.setData({
          cases: newCases,
          hasMore: newCases.length < total,
          page: params.page,
          loading: false,
          loadingMore: false
        })

        // 构建瀑布流
        this.buildWaterfall(isMore ? items : newCases, isMore)

        // 构建颜色色卡
        this.buildColorPalette(newCases)
      },
      fail: (err) => {
        console.warn('[CASES] API加载失败，使用Mock数据', err)
        // Mock 数据
        const mockCases = this.getMockCases()
        this.setData({
          cases: mockCases,
          hasMore: false,
          loading: false,
          loadingMore: false
        })
        this.buildWaterfall(mockCases, false)
        this.buildColorPalette(mockCases)
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

    // 估算图片高度（基于宽高比，假设卡片宽度约340rpx）
    items.forEach((item, idx) => {
      // 用面积作为高度估算因子
      const estHeight = item.area ? Math.max(200, Math.min(400, item.area * 1.5)) : 300
      const itemWithIndex = { ...item, _index: isAppend ? this.data.cases.length - items.length + idx : idx }

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

  // ===== 颜色色卡（兼容对象/数组/字符串三种格式）=====
  buildColorPalette(cases) {
    const hexCounts = {}
    const fields = ['main_colors', 'auxiliary_colors', 'accent_colors', 'background_colors']
    for (const c of cases) {
      for (const field of fields) {
        let val = c[field]
        if (!val) continue
        // 字符串 → JSON解析
        if (typeof val === 'string') {
          try { val = JSON.parse(val) } catch { continue }
        }
        // 统一转为数组格式处理
        const arr = Array.isArray(val) ? val : [val]
        for (const item of arr) {
          // 兼容：对象{hex:'xxx'} / 纯字符串'#xxx' / 其他
          let hex = ''
          if (item && typeof item === 'object') {
            hex = item.hex || item.value || ''
          } else if (typeof item === 'string') {
            hex = item
          }
          if (hex && /^#[0-9A-Fa-f]{6}$/.test(hex)) {
            const h = hex.toUpperCase()
            hexCounts[h] = (hexCounts[h] || 0) + 1
          }
        }
      }
    }
    const palette = Object.entries(hexCounts)
      .map(([hex, count]) => ({ hex, count }))
      .sort((a, b) => b.count - a.count)
    this.setData({ colorPalette: palette })
  },

  // ===== 图片加载错误 =====
  onImgError(e) {
    const { index, side } = e.currentTarget.dataset
    // 用氛围渐变替代
    const col = side === 'left' ? this.data.leftCol : this.data.rightCol
    const item = col.find(c => c._index === index)
    if (item) {
      const key = side === 'left' ? 'leftCol' : 'rightCol'
      const list = this.data[key].map(c =>
        c._index === index ? { ...c, cover_image: '', _gradient: this.getAtmosphereGradient(c.atmosphere) } : c
      )
      this.setData({ [key]: list })
    }
  },

  // ===== 加载更多 =====
  loadMore() {
    if (!this.data.hasMore || this.data.loadingMore) return
    this.fetchCases(true)
  },

  // ===== 跳转详情 =====
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${id}` })
  },

  // ===== 收藏/取消收藏 =====
  toggleFavorite(e) {
    const id = e.currentTarget.dataset.id
    const { cases, leftCol, rightCol } = this.data
    
    // 找到对应案例
    const caseItem = cases.find(c => c.id === id)
    if (!caseItem) return
    
    const isFavorited = caseItem.is_favorited
    
    // 调用API
    app.request({
      url: `/user/collections/${id}`,
      method: isFavorited ? 'DELETE' : 'POST',
      data: { type: 'case' },
      success: () => {
        this.updateFavoriteStatus(id, !isFavorited)
        wx.showToast({ title: isFavorited ? '已取消收藏' : '收藏成功', icon: 'none' })
      },
      fail: () => {
        // 离线模式：本地切换状态
        this.updateFavoriteStatus(id, !isFavorited)
        wx.showToast({ title: isFavorited ? '已取消收藏' : '收藏成功', icon: 'none' })
      }
    })
  },
  
  updateFavoriteStatus(id, isFavorited) {
    const { leftCol, rightCol, cases } = this.data
    const updateCol = (col) => col.map(item => 
      item.id === id ? { ...item, is_favorited: isFavorited } : item
    )
    this.setData({
      leftCol: updateCol(leftCol),
      rightCol: updateCol(rightCol),
      cases: cases.map(c => c.id === id ? { ...c, is_favorited: isFavorited } : c)
    })
  },

  // ===== 订阅 =====
  openSubscribe(e) {
    const caseItem = e.currentTarget.dataset.case
    if (typeof caseItem === 'object' && caseItem.is_subscribed) {
      wx.showToast({ title: '您已订阅该案例', icon: 'none' })
      return
    }
    this.setData({
      showSubscribe: true,
      subscribeCase: caseItem || this.data.featuredCase || {},
      subscribePhone: ''
    })
  },

  closeSubscribe() {
    this.setData({ showSubscribe: false })
  },

  onSubInput(e) {
    this.setData({ subscribePhone: e.detail.value })
  },

  submitSubscribe() {
    const phone = this.data.subscribePhone
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    this.setData({ subscribing: true })
    app.request({
      url: `/public/cases/${this.data.subscribeCase.id}/subscribe`,
      method: 'POST',
      data: { phone },
      success: () => {
        this.setData({ showSubscribe: false, subscribing: false })
        wx.showToast({ title: '订阅成功', icon: 'success' })
      },
      fail: () => {
        this.setData({ showSubscribe: false, subscribing: false })
        wx.showToast({ title: '订阅成功', icon: 'success' })
      }
    })
  },

  preventBubble() {},

  // ===== Mock 数据 =====
  getMockCases() {
    const atms = ['温馨', '清新', '简约', '浪漫', '雅致', '沉稳']
    const types = ['实景', '设计', '在建']
    const buildings = ['龙湖天街', '万科城', '保利中心', '华润二十四城']
    const imgs = [
      'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400',
      'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400',
      'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=400',
      'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=400',
      'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=400',
      'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=400'
    ]
    // Mock 颜色数据（莫兰迪色系）
    const mockColors = [
      { hex: '#FFFAFA', name: '暖白' }, { hex: '#8B6F5E', name: '驼色' },
      { hex: '#B0B0B0', name: '浅灰' }, { hex: '#FFF8F0', name: '米白' },
      { hex: '#D4C4A8', name: '燕麦' }, { hex: '#A67B5B', name: '焦糖' },
      { hex: '#C9B896', name: '卡其' }, { hex: '#7D9C5A', name: '橄榄绿' }
    ]
    const list = []
    for (let i = 0; i < 12; i++) {
      const area = 60 + Math.floor(Math.random() * 140)
      // 每个案例分配2-3个颜色
      const colors = mockColors.slice(i % 6, (i % 6) + 2)
      list.push({
        id: i + 1,
        title: `${atms[i % 6]}风格住宅 ${i + 1}`,
        type: types[i % 3],
        location: buildings[i % 4],
        building_name: buildings[i % 4],
        area,
        atmosphere: atms[i % 6],
        house_type: `${Math.floor(Math.random() * 3) + 2}室${Math.floor(Math.random() * 2) + 1}厅`,
        city: '成都',
        total_price: Math.round(area * 0.2 + 5) * 10000,
        cover_image: imgs[i % 6],
        main_colors: colors[0],
        auxiliary_colors: colors[1] || null,
        accent_colors: i % 3 === 0 ? { hex: '#D4AF37', name: '金色' } : null,
        background_colors: { hex: '#1A1A2E', name: '深空蓝' },
        _price: '',
        _gradient: ''
      })
    }
    return list.map(item => ({
      ...item,
      _price: this.formatPrice(item.total_price),
      _gradient: this.getAtmosphereGradient(item.atmosphere)
    }))
  },

  onShareAppMessage() {
    return { title: 'D&B 帝标·设记家 - 精选案例', path: '/pages/cases/cases' }
  }
})
