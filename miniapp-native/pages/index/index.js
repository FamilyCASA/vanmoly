const app = getApp()

Page({
  data: {
    // Hero
    heroSlides: [],
    heroBadges: [],

    // 全案服务
    services: [
      { icon: '🎨', title: '全案设计', desc: '从空间规划到软装搭配，提供完整设计方案', features: ['空间规划', '效果图', '施工图', '材料选型'] },
      { icon: '🪑', title: '定制家具', desc: '自有工厂生产，品质可控，风格统一', features: ['衣柜定制', '橱柜定制', '木门定制', '护墙板'] },
      { icon: '🔧', title: '施工监理', desc: '专业监理团队，全程把控施工质量', features: ['节点验收', '质量把控', '进度管理'] },
      { icon: '✨', title: '软装搭配', desc: '专业软装设计师，打造完整家居风格', features: ['家具选配', '窗帘布艺', '灯具搭配', '饰品陈列'] }
    ],

    // 服务流程
    workflowPhases: [],
    workflowLoading: true,
    expandedPhase: null,
    expandedPhaseIndex: -1,
    expandedPhaseName: '',
    totalNodeCount: 0,

    // 关于
    aboutSection: { title: '', description: '', image: '' },
    aboutStats: [
      { value: '50+', label: '专业设计师' },
      { value: '30+', label: '合作品牌' },
      { value: '100%', label: '环保材料' }
    ],

    // 品牌背书
    brandLogos: [],

    // 联系
    contactInfo: {
      address: '成都市青羊区蔡桥街道天府匠芯北区A座6-10',
      phone: '139 0817 9177',
      hours: '周一至周日 9:00-18:00'
    },

    // 快速预约
    quickLead: { name: '', phone: '', budget: '' },
    budgetOptions: ['10万以下', '10-20万', '20-30万', '30-50万', '50万以上'],
    budgetIndex: -1,
    leadSubmitting: false,
    showLeadSuccess: false,

    // 锚点导航
    anchorList: [
      { id: 'services', label: '全案服务' },
      { id: 'process', label: '服务流程' },
      { id: 'about', label: '关于我们' },
      { id: 'brands', label: '品牌背书' },
      { id: 'contact', label: '联系我们' }
    ],
    activeAnchor: 'services',
    anchorNavFixed: false,

    // 节点详情弹窗
    showNodeDetail: false,
    nodeDetail: { phaseName: '', code: '', name: '', description: '' }
  },

  onLoad() {
    this.loadAll()
  },

  onShow() {
    // 首页显示时注册滚动监听
    this._setupScrollObserver()
  },

  onHide() {
    // 离开首页时移除滚动监听
    this._cleanupScrollObserver()
  },

  onUnload() {
    this._cleanupScrollObserver()
  },

  onPageScroll(e) {
    // 滚动超过 200px 时给锚点导航加阴影（吸顶状态）
    const isFixed = e.scrollTop > 200
    if (this.data.anchorNavFixed !== isFixed) {
      this.setData({ anchorNavFixed: isFixed })
    }
  },

  // ===== 锚点导航：滚动监听 =====
  _setupScrollObserver() {
    this._observers = []
    const ids = ['services', 'process', 'about', 'brands', 'contact']
    ids.forEach(id => {
      const observer = this.createIntersectionObserver({
        thresholds: [0.3]
      })
      observer.relativeToViewport({ top: -100, bottom: -100 })
      observer.observe(`#${id}`, (res) => {
        if (res.intersectionRatio > 0) {
          this.setData({ activeAnchor: id })
        }
      })
      this._observers.push(observer)
    })
  },

  _cleanupScrollObserver() {
    if (this._observers) {
      this._observers.forEach(o => o.disconnect())
      this._observers = null
    }
  },

  // ===== 锚点导航：点击跳转 =====
  scrollToAnchor(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ activeAnchor: id })
    wx.pageScrollTo({
      selector: `#${id}`,
      duration: 400
    })
  },

  // ===== 加载所有数据 =====
  loadAll() {
    this.loadHeroSlides()
    this.loadServices()
    this.loadWorkflowPhases()
    this.loadAboutSection()
    this.loadBrandLogos()
    this.loadContactSection()
  },

  // ===== Hero =====
  loadHeroSlides() {
    console.log('[HOME] Loading hero slides...')
    app.request({
      url: '/frontend/hero-slides',
      success: (res) => {
        console.log('[HOME] Hero slides loaded:', res ? (Array.isArray(res) ? res.length + ' items' : typeof res) : 'null')
        if (res && res.length > 0) {
          // 解析图片URL（后台配置的可能是相对路径）
          const slides = res.map(s => ({
            ...s,
            url: app.resolveImageUrl(s.url || s.image || '')
          }))
          console.log('[HOME] First slide resolved URL:', slides[0].url)
          this.setData({ heroSlides: slides, heroBadges: this.defaultBadges() })
        } else {
          console.warn('[HOME] Hero slides empty, using defaults')
          this.setData({ heroSlides: this.defaultSlides(), heroBadges: this.defaultBadges() })
        }
      },
      fail: (err) => {
        console.error('[HOME] Hero slides failed:', err)
        this.setData({ heroSlides: this.defaultSlides(), heroBadges: this.defaultBadges() })
      }
    })
  },

  defaultSlides() {
    // Fallback: 使用纯色背景占位（不依赖外网图片）
    return [
      { id: 1, url: '' },
      { id: 2, url: '' },
      { id: 3, url: '' }
    ]
  },

  defaultBadges() {
    return ['全案落地服务', '高端全屋定制', '软装饰品陈设']
  },

  // ===== 服务 =====
  loadServices() {
    app.request({
      url: '/frontend/services-section',
      success: (res) => {
        if (res && res.items && res.items.length > 0) {
          this.setData({ services: res.items })
        }
      },
      fail: () => {}
    })
  },

  // ===== 服务流程：一次性加载所有阶段及节点 =====
  loadWorkflowPhases() {
    console.log('[HOME] Loading workflow phases...')
    this.setData({ workflowLoading: true })
    app.request({
      url: '/workflows/public/phases',
      success: (res) => {
        console.log('[HOME] Workflow response:', res ? (res.phases ? res.phases.length + ' phases' : 'no phases key') : 'null')
        if (res && res.phases) {
          const phases = res.phases.map(p => ({
            ...p,
            nodes: (p.nodes || []).map(n => ({
              ...n,
              // 后端 WorkflowNode.to_dict() 返回 node_code/node_name，统一映射为 code/name
              code: n.code || n.node_code || '',
              name: n.name || n.node_name || '',
              description: n.description || n.desc || ''
            }))
          }))
          let total = 0
          phases.forEach(p => {
            total += (p.nodes && p.nodes.length) || 0
          })
          console.log('[HOME] Workflow processed:', phases.length, 'phases,', total, 'nodes')
          this.setData({
            workflowPhases: phases,
            totalNodeCount: total
          })
        }
      },
      fail: (err) => {
        console.error('[HOME] Workflow failed:', err)
      },
      complete: () => {
        console.log('[HOME] Workflow loading complete')
        this.setData({ workflowLoading: false })
      }
    })
  },

  // ===== 展开/收拢阶段（节点数据已在 loadWorkflowPhases 中一次性加载）=====
  togglePhase(e) {
    const code = e.currentTarget.dataset.code
    const index = e.currentTarget.dataset.index
    const currentExpanded = this.data.expandedPhase

    if (currentExpanded === code) {
      // 收拢
      this.setData({ expandedPhase: null, expandedPhaseIndex: -1, expandedPhaseName: '' })
      return
    }

    // 展开新阶段
    const phase = this.data.workflowPhases[index]
    this.setData({
      expandedPhase: code,
      expandedPhaseIndex: index,
      expandedPhaseName: phase ? phase.name : ''
    })
  },

  // ===== 点击节点，弹出详情 =====
  showNodeDetail(e) {
    const { phaseCode, phaseName, nodeCode, nodeName, nodeDesc } = e.currentTarget.dataset
    this.setData({
      showNodeDetail: true,
      nodeDetail: {
        phaseName: phaseName || '',
        code: nodeCode || '',
        name: nodeName || '',
        description: nodeDesc || ''
      }
    })
  },

  closeNodeDetail() {
    this.setData({ showNodeDetail: false })
  },

  // ===== 关于 =====
  loadAboutSection() {
    app.request({
      url: '/frontend/about-section',
      success: (res) => {
        if (res) {
          // 解析图片URL
          if (res.image) res.image = app.resolveImageUrl(res.image)
          this.setData({ aboutSection: res })
          if (res.stats) this.setData({ aboutStats: res.stats })
        }
      },
      fail: () => {}
    })
  },

  // ===== 品牌背书 =====
  loadBrandLogos() {
    app.request({
      url: '/frontend/brand-logos',
      success: (res) => {
        if (res && res.length > 0) {
          // 解析 logo 图片 URL
          const logos = res.map(b => ({
            ...b,
            url: app.resolveImageUrl(b.url || b.logo || b.image || ''),
            logo: app.resolveImageUrl(b.logo || b.url || b.image || '')
          }))
          this.setData({ brandLogos: logos })
        }
      },
      fail: () => {}
    })
  },

  // ===== 联系 =====
  loadContactSection() {
    app.request({
      url: '/frontend/contact-section',
      success: (res) => {
        if (res) {
          this.setData({ contactInfo: { ...this.data.contactInfo, ...res } })
        }
      },
      fail: () => {}
    })
  },

  // ===== 预约表单 =====
  onLeadInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`quickLead.${field}`]: e.detail.value })
  },

  onBudgetPick(e) {
    const idx = e.detail.value
    this.setData({
      budgetIndex: idx,
      'quickLead.budget': this.data.budgetOptions[idx]
    })
  },

  submitQuickLead() {
    const { name, phone, budget } = this.data.quickLead
    if (!name.trim()) { wx.showToast({ title: '请输入称呼', icon: 'none' }); return }
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) { wx.showToast({ title: '请输入正确手机号', icon: 'none' }); return }
    this.setData({ leadSubmitting: true })
    app.request({
      url: '/leads',
      method: 'POST',
      data: { name, phone, budget, source: '首页预约量房' },
      success: () => {
        app.markAsLeaded()
        this.setData({ showLeadSuccess: true, leadSubmitting: false })
      },
      fail: () => {
        app.markAsLeaded()
        this.setData({ showLeadSuccess: true, leadSubmitting: false })
      }
    })
  },

  closeLeadSuccess() {
    this.setData({ showLeadSuccess: false, quickLead: { name: '', phone: '', budget: '' }, budgetIndex: -1 })
  },

  // ===== 导航 =====
  onHeroImageError(e) {
    console.warn('[HOME] Hero image load error:', e.detail)
  },

  scrollToContact() {
    wx.pageScrollTo({ selector: '#contact', duration: 500 })
  },

  goToCases() {
    wx.switchTab({ url: '/pages/cases/cases' })
  },

  callPhone() {
    wx.makePhoneCall({ phoneNumber: this.data.contactInfo.phone.replace(/\s/g, '') })
  },

  openMap() {
    wx.openLocation({
      latitude: 30.67,
      longitude: 104.07,
      name: 'D&B 帝标·设记家',
      address: this.data.contactInfo.address
    })
  },

  preventBubble() {},

  onShareAppMessage() {
    return { title: 'D&B 帝标·设记家 — 专注高端全屋定制', path: '/pages/index/index' }
  }
})
