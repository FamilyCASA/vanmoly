// 案例详情页 — 深化版
const app = getApp()

Page({
  data: {
    id: '',
    loading: true,
    caseDetail: null,

    // Hero
    heroImages: [],
    currentHero: 0,

    // 服务团队
    team: [],

    // 案例标签
    caseTags: [],

    // 色彩材质
    colorPalettes: [],

    // 案例视频
    caseVideo: null,

    // 全屋图片画廊
    allImages: [],
    totalImageCount: 0,

    // 案例二维码
    caseQrcode: '',

    // 6阶段 Tab
    categories: [
      { key: 'mood', label: '设计意境' },
      { key: 'layout', label: '户型分析' },
      { key: 'plan', label: '户型规划' },
      { key: 'birdview', label: '鸟瞰图' },
      { key: 'showcase', label: '意向图' },
      { key: 'spaces', label: '效果图' }
    ],
    activeCategory: 'mood',

    // 阶段数据
    phase1: {}, phase2: {}, phase3: {}, phase4: {}, phase5: {}, phase6: {},
    spacesByName: [],

    // 施工进度
    workflowProgress: null,
    groupedTimeline: {},
    timelineList: [],

    // 相关产品
    relatedProducts: [],

    // 更多案例 + 相似案例
    relatedCases: [],
    similarCases: [],

    // VR
    vrLink: '',
    vrQrcode: '',

    // 杂志排版
    designConcept: '',

    // 统计
    viewCount: 0,
    likeCount: 0,
    subCount: 0,

    // 交互状态
    isLiked: false,
    isCollected: false,
    isFavorited: false,
    isSubscribed: false,
    showQuotePopup: false,
    quoteItems: [],
    totalPriceStr: '',
    budgetStr: '',
    overviewItems: [],

    // 留资
    showLeadForm: false,
    leadForm: { name: '', phone: '', area: '', message: '' },
    leadSubmitting: false,
    showLeadSuccess: false,

    // 评论
    comments: [],
    commentInput: '',

    // 分享海报
    showPoster: false,
    posterImage: '',

    // 全图画廊
    showGallery: false,

    token: ''
  },

  onLoad(options) {
    const { id } = options
    if (!id) {
      wx.showToast({ title: '参数错误', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    this.setData({ id, token: wx.getStorageSync('token') || '' })
    this.fetchCaseDetail(id)
  },

  onShow() {
    this.checkSelection()
    this.checkCollection()
    this.checkFavorite()
  },

  onShareAppMessage() {
    const detail = this.data.caseDetail || {}
    return {
      title: detail.title || 'D&B 帝标·设记家 - 案例详情',
      path: `/pages/case-detail/case-detail?id=${this.data.id}`,
      imageUrl: this.data.heroImages[0] || ''
    }
  },

  // ===== 获取案例详情 =====
  fetchCaseDetail(id) {
    this.setData({ loading: true })
    app.request({
      url: `/public/cases/${id}`,
      success: (res) => {
        if (res) {
          this.processCaseData(res)
          this.loadSimilarCases(res)
          this.loadComments(id)
          this.checkSubscription(id)
        } else {
          this.processCaseData(this.getMockDetail(id))
        }
      },
      fail: () => {
        this.processCaseData(this.getMockDetail(id))
      }
    })
  },

  processCaseData(detail) {
    // Hero 图片
    let heroImages = []
    if (detail.hero_images && detail.hero_images.length > 0) {
      heroImages = detail.hero_images.map(u => {
        const raw = typeof u === 'string' ? u : (u.url || u.image_url || '')
        return raw ? app.resolveImageUrl(raw) : ''
      }).filter(Boolean)
    }
    if (heroImages.length === 0) {
      const cover = detail.cover_image || detail.cover || ''
      if (cover) heroImages = [app.resolveImageUrl(cover)]
    }
    if (heroImages.length === 0) {
      heroImages = ['https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800']
    }

    // 服务团队
    const team = []
    if (detail.planner) {
      team.push({
        id: detail.planner.id || detail.planner_id,
        name: detail.planner.name || '规划师',
        role: 'planner',
        roleLabel: '全案规划师',
        avatar: detail.planner.avatar ? app.resolveImageUrl(detail.planner.avatar) : '',
        styles: detail.planner.styles || []
      })
    }
    if (detail.designer) {
      team.push({
        id: detail.designer.id || detail.designer_id,
        name: detail.designer.name || '设计师',
        role: 'designer',
        roleLabel: '主案设计师',
        avatar: detail.designer.avatar ? app.resolveImageUrl(detail.designer.avatar) : '',
        styles: detail.designer.styles || []
      })
    }
    if (detail.customer_manager || detail.manager) {
      const m = detail.customer_manager || detail.manager
      team.push({
        id: m.id,
        name: m.name || '客户经理',
        role: 'manager',
        roleLabel: '客户经理',
        avatar: m.avatar ? app.resolveImageUrl(m.avatar) : '',
        styles: []
      })
    }

    // 案例标签云
    const caseTags = []
    if (detail.atmosphere) caseTags.push({ type: 'atmosphere', value: detail.atmosphere, label: '氛围' })
    if (detail.style) caseTags.push({ type: 'style', value: detail.style, label: '风格' })
    if (detail.house_type) caseTags.push({ type: 'house', value: detail.house_type, label: '户型' })
    const colorFields = ['main_colors', 'auxiliary_colors', 'accent_colors', 'background_colors']
    colorFields.forEach(field => {
      if (detail[field] && Array.isArray(detail[field])) {
        detail[field].forEach(c => {
          if (c && typeof c === 'string' && /^#[0-9a-fA-F]{6}$/.test(c)) {
            caseTags.push({ type: 'color', value: c, label: '配色' })
          }
        })
      }
    })

    // 色彩材质面板
    const colorPalettes = []
    if (detail.main_colors && Array.isArray(detail.main_colors)) {
      const mainColors = detail.main_colors.filter(c => typeof c === 'string' && /^#[0-9a-fA-F]{6}$/.test(c))
      if (mainColors.length > 0) {
        colorPalettes.push({ label: '主色', colors: mainColors.map(hex => ({ hex, name: this.getColorName(hex) })) })
      }
    }
    if (detail.auxiliary_colors && Array.isArray(detail.auxiliary_colors)) {
      const auxColors = detail.auxiliary_colors.filter(c => typeof c === 'string' && /^#[0-9a-fA-F]{6}$/.test(c))
      if (auxColors.length > 0) {
        colorPalettes.push({ label: '辅色', colors: auxColors.map(hex => ({ hex, name: this.getColorName(hex) })) })
      }
    }
    if (detail.accent_colors && Array.isArray(detail.accent_colors)) {
      const accentColors = detail.accent_colors.filter(c => typeof c === 'string' && /^#[0-9a-fA-F]{6}$/.test(c))
      if (accentColors.length > 0) {
        colorPalettes.push({ label: '点缀色', colors: accentColors.map(hex => ({ hex, name: this.getColorName(hex) })) })
      }
    }

    // 案例视频
    const caseVideo = detail.video_url ? {
      url: detail.video_url,
      thumbnail: detail.video_thumbnail || '',
      duration: detail.video_duration || ''
    } : null

    // 案例二维码
    const caseQrcode = detail.case_qrcode ? app.resolveImageUrl(detail.case_qrcode) : ''

    // 全屋图片收集
    const allImagesMap = {}
    // Hero 图片
    heroImages.forEach(url => { if (url) allImagesMap[url] = { url, space: '封面' } })
    // 各阶段图片
    const phases = detail.phases || {}
    const phaseLabels = { 1: '户型分析', 2: '设计意境', 3: '户型规划', 4: '鸟瞰图', 5: '设计意向', 6: '空间效果' }
    Object.values(phases).forEach(p => {
      if (!p) return
      const label = phaseLabels[p.phase_number] || '其他'
      ;['layout_images', 'mood_images', 'birdview_images', 'showcase_images'].forEach(field => {
        const imgs = this.parseImgField(p[field])
        imgs.forEach(url => { if (url) allImagesMap[url] = { url, space: label } })
      })
      if (p.plan_image) {
        const url = typeof p.plan_image === 'string' ? p.plan_image : (p.plan_image.url || '')
        if (url) allImagesMap[app.resolveImageUrl(url)] = { url: app.resolveImageUrl(url), space: '户型规划' }
      }
    })
    // 空间效果图
    if (detail.spaces && Array.isArray(detail.spaces)) {
      detail.spaces.forEach(s => {
        const spaceName = s.space_name || '其他'
        if (s.renderings && Array.isArray(s.renderings)) {
          s.renderings.forEach(r => {
            const url = typeof r === 'string' ? r : (r.url || r.rendering_url || '')
            if (url) allImagesMap[app.resolveImageUrl(url)] = { url: app.resolveImageUrl(url), space: spaceName }
          })
        }
      })
    }
    const allImages = Object.values(allImagesMap)

    // 解析阶段数据
    const arr = Array.isArray(phases) ? phases : Object.values(phases)
    const phaseMap = {}
    arr.filter(Boolean).forEach(p => { phaseMap[p.phase_number] = p })

    const p1 = this.parsePhase(phaseMap[1])
    const p2 = this.parsePhase(phaseMap[2])
    const p3 = this.parsePhase(phaseMap[3])
    const p4 = this.parsePhase(phaseMap[4])
    const p5 = this.parsePhase(phaseMap[5])

    // 空间效果图分组
    let spacesByName = []
    const spaces = detail.spaces || (phaseMap[6] ? phaseMap[6].spaces : [])
    if (spaces && spaces.length > 0) {
      const groups = {}
      spaces.forEach(s => {
        const name = s.space_name || '其他空间'
        if (!groups[name]) groups[name] = { name, items: [] }
        groups[name].items.push(...(s.renderings || []))
      })
      spacesByName = Object.values(groups).map(g => ({
        name: g.name,
        items: g.items.map(i => ({
          url: typeof i === 'string' ? (i ? app.resolveImageUrl(i) : '') : (i.url || i.rendering_url ? app.resolveImageUrl(i.url || i.rendering_url) : ''),
          title: i.title || '',
          description: i.description || ''
        }))
      }))
    }

    // 施工进度
    const wp = detail.workflow_progress || null
    const timeline = detail.timeline_nodes || detail.workflow_timeline || []
    const grouped = {}
    if (Array.isArray(timeline)) {
      timeline.forEach(n => {
        const phase = n.phase || '其他'
        if (!grouped[phase]) grouped[phase] = []
        grouped[phase].push(n)
      })
    }

    // 相关产品
    const relatedProducts = (detail.related_products || []).map(p => ({
      ...p,
      mainImage: p.main_image ? app.resolveImageUrl(p.main_image) : '',
      salePriceStr: p.sale_price ? this.formatPrice(p.sale_price) : ''
    }))

    // VR
    const vrLink = detail.vr_link || ''
    const vrQrcode = detail.vr_qrcode ? app.resolveImageUrl(detail.vr_qrcode) : ''

    // 概览网格
    const overviewItems = []
    if (detail.house_type) overviewItems.push({ label: '户型', value: detail.house_type })
    if (detail.area) overviewItems.push({ label: '面积', value: detail.area + '㎡' })
    if (detail.style) overviewItems.push({ label: '风格', value: detail.style })
    overviewItems.push({ label: '工期', value: (detail.duration || '90') + '天' })
    if (detail.total_price) overviewItems.push({ label: '全案总价', value: '¥' + this.formatPrice(detail.total_price), highlight: true })
    if (detail.deal_budget || (detail.quote_info && detail.quote_info.total_amount)) {
      const amt = detail.quote_info ? detail.quote_info.total_amount : detail.deal_budget
      overviewItems.push({ label: '参考造价', value: this.formatWan(amt), highlight: true, clickable: true })
    }

    // 报价
    let quoteItems = []
    if (detail.quote_info && detail.quote_info.items) {
      quoteItems = detail.quote_info.items.map(it => ({
        name: it.name || it.category || '',
        amount: it.amount ? this.formatPrice(it.amount) : '0'
      }))
    }

    this.setData({
      caseDetail: detail,
      heroImages,
      team,
      caseTags,
      colorPalettes,
      caseVideo,
      caseQrcode,
      allImages,
      totalImageCount: allImages.length,
      phase1: p1,
      phase2: p2,
      phase3: p3,
      phase4: p4,
      phase5: p5,
      phase6: phaseMap[6] || {},
      spacesByName,
      workflowProgress: wp,
      timelineList: timeline,
      groupedTimeline: grouped,
      relatedProducts,
      vrLink,
      vrQrcode,
      viewCount: detail.view_count || 0,
      likeCount: detail.like_count || 0,
      subCount: detail.subscription_count || 0,
      totalPriceStr: detail.total_price ? '¥' + this.formatPrice(detail.total_price) : '',
      budgetStr: (detail.deal_budget || (detail.quote_info && detail.quote_info.total_amount)) ? this.formatWan(detail.quote_info ? detail.quote_info.total_amount : detail.deal_budget) : '',
      overviewItems,
      quoteItems,
      designConcept: detail.design_concept || detail.description || '',
      designConceptFormatted: this.formatRichText(detail.design_concept || detail.description || ''),
      loading: false
    })

    // 富文本格式化
    this.setData({
      'phase2.moodFormatted': this.formatRichText(p2.moodText || p2.mood_text || ''),
      'phase1.analysisFormatted': this.formatRichText(p1.layout_analysis || ''),
      'phase3.planFormatted': this.formatRichText(p3.plan_text || ''),
      'phase5.quoteFormatted': this.formatRichText(p5.showcase_quote || '')
    })

    if (detail.title) wx.setNavigationBarTitle({ title: detail.title })
  },

  // ===== 色彩名称映射 =====
  getColorName(hex) {
    const names = {
      '#000000': '黑', '#FFFFFF': '白', '#D4AF37': '金', '#C0C0C0': '银',
      '#2C3E50': '深灰', '#ECF0F1': '浅灰', '#E74C3C': '红', '#3498DB': '蓝',
      '#2ECC71': '绿', '#F39C12': '橙', '#9B59B6': '紫', '#1ABC9C': '青',
      '#34495E': '炭灰', '#95A5A6': '灰', '#BDC3C7': '银灰', '#7F8C8D': '岩灰',
      '#D35400': '赭', '#C0392B': '朱红', '#16A085': '墨绿', '#27AE60': '翠绿',
      '#2980B9': '钴蓝', '#8E44AD': '靛紫', '#F1C40F': '明黄', '#E67E22': '琥珀',
      '#CAMEL': '驼色', '#BEIGE': '米色', '#NAVY': '藏青', '#BURGUNDY': '酒红'
    }
    return names[hex.toUpperCase()] || hex
  },

  // ===== 解析图片字段 =====
  parsePhase(p) {
    if (!p) return {}
    return {
      ...p,
      layoutImages: this.parseImgField(p.layout_images),
      moodImages: this.parseImgField(p.mood_images),
      birdviewImages: this.parseImgField(p.birdview_images),
      showcaseImages: this.parseImgField(p.showcase_images),
      planImage: p.plan_image ? app.resolveImageUrl(typeof p.plan_image === 'string' ? p.plan_image : p.plan_image.url || '') : ''
    }
  },

  parseImgField(val) {
    if (!val || val === '') return []
    if (Array.isArray(val)) return val.map(i => { const raw = typeof i === 'string' ? i : (i.url || i.image_url || ''); return raw ? app.resolveImageUrl(raw) : '' }).filter(Boolean)
    if (typeof val === 'string') {
      try { const r = JSON.parse(val); return Array.isArray(r) ? r.map(i => { const raw = typeof i === 'string' ? i : (i.url || ''); return raw ? app.resolveImageUrl(raw) : '' }).filter(Boolean) : [] } catch { return [] }
    }
    return []
  },

  // ===== 加载相似案例 =====
  loadSimilarCases(detail) {
    app.request({
      url: '/public/cases',
      data: {
        style: detail.style,
        atmosphere: detail.atmosphere,
        page_size: 8,
        status: 'published'
      },
      success: (res) => {
        let list = res
        if (res && res.items) list = res.items
        if (Array.isArray(list)) {
          this.setData({
            similarCases: list.filter(c => c.id !== Number(this.data.id)).slice(0, 4).map(c => ({
              ...c,
              cover: c.cover_image ? app.resolveImageUrl(c.cover_image) : ''
            }))
          })
        }
      },
      fail: () => {}
    })
  },

  // ===== 加载评论 =====
  loadComments(caseId) {
    app.request({
      url: `/public/cases/${caseId}/comments`,
      data: { page_size: 20 },
      success: (res) => {
        if (res && res.items) {
          this.setData({
            comments: res.items.map(c => ({
              ...c,
              avatar: c.avatar ? app.resolveImageUrl(c.avatar) : '',
              timeAgo: this.formatTimeAgo(c.created_at)
            }))
          })
        }
      },
      fail: () => {
        this.setData({
          comments: [
            { id: 1, name: '业主王先生', avatar: '', content: '设计非常有质感，细节处理到位，很喜欢这种现代轻奢风格！', likeCount: 12, isLiked: false, timeAgo: '3天前' },
            { id: 2, name: '装修达人', avatar: '', content: '客厅的灯光设计很棒，营造了温馨的氛围', likeCount: 8, isLiked: false, timeAgo: '1周前' }
          ]
        })
      }
    })
  },

  // ===== 富文本处理 =====
  formatRichText(html) {
    if (!html) return ''
    if (!/<[a-z][\s>]/i.test(html)) {
      const paras = html.split(/\n+/).filter(Boolean)
      html = paras.map(p => '<p>' + p.trim() + '</p>').join('')
    }
    const dcStyle = 'font-size:2.2em;font-weight:800;color:#D4AF37;line-height:0.85;vertical-align:top;margin-right:6rpx;display:inline-block;'
    return html.replace(
      /<p(\b[^>]*)>(\s*)(.)([\s\S]*?)<\/p>/gi,
      function(match, attrs, space, char, rest) {
        if (char === '<' || /\s/.test(char)) return '<p' + attrs + '>' + space + char + rest + '</p>'
        return '<p' + attrs + '>' + space + '<span style="' + dcStyle + '">' + char + '</span>' + rest + '</p>'
      }
    )
  },

  // ===== 时间格式化 =====
  formatTimeAgo(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    if (days > 30) return Math.floor(days / 30) + '月前'
    if (days > 0) return days + '天前'
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours > 0) return hours + '小时前'
    return '刚刚'
  },

  // ===== 返回 =====
  goBack() {
    wx.navigateBack({ delta: 1, fail: () => wx.switchTab({ url: '/pages/cases/cases' }) })
  },

  // ===== Hero =====
  onHeroChange(e) {
    this.setData({ currentHero: e.detail.current })
  },
  onHeroTap(e) {
    const { idx } = e.currentTarget.dataset
    wx.previewImage({ current: this.data.heroImages[idx], urls: this.data.heroImages })
  },
  onHeroMore() {
    wx.showActionSheet({
      itemList: ['分享海报', '收藏案例', '举报案例'],
      success: (res) => {
        if (res.tapIndex === 0) this.shareCase()
        else if (res.tapIndex === 1) this.handleCollect()
      }
    })
  },

  // ===== Tab 切换 =====
  onTabChange(e) {
    this.setData({ activeCategory: e.currentTarget.dataset.key })
  },

  // ===== 图片预览 =====
  previewImage(e) {
    const { idx, list } = e.currentTarget.dataset
    wx.previewImage({ current: list[idx], urls: list })
  },

  // ===== 颜色点击 =====
  onColorTap(e) {
    const hex = e.currentTarget.dataset.hex
    wx.previewImage({ current: hex, urls: [hex] })
  },

  // ===== 视频播放 =====
  playVideo() {
    if (this.data.caseVideo && this.data.caseVideo.url) {
      wx.navigateTo({ url: `/pages/video-play/index?url=${encodeURIComponent(this.data.caseVideo.url)}` })
    }
  },

  // ===== 全图画廊 =====
  showFullGallery() {
    this.setData({ showGallery: true })
  },
  closeGallery() {
    this.setData({ showGallery: false })
  },

  // ===== 案例二维码 =====
  previewQrcode() {
    if (this.data.caseQrcode) {
      wx.previewImage({ current: this.data.caseQrcode, urls: [this.data.caseQrcode] })
    }
  },
  saveQrcode() {
    if (!this.data.caseQrcode) {
      wx.showToast({ title: '暂无可用二维码', icon: 'none' })
      return
    }
    wx.showLoading({ title: '保存中...' })
    wx.downloadFile({
      url: this.data.caseQrcode,
      success: (res) => {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => wx.showToast({ title: '已保存', icon: 'success' }),
          fail: () => wx.showToast({ title: '保存失败', icon: 'none' }),
          complete: () => wx.hideLoading()
        })
      },
      fail: () => { wx.hideLoading(); wx.showToast({ title: '下载失败', icon: 'none' }) }
    })
  },

  // ===== 分享 =====
  shareCase() {
    wx.showActionSheet({
      itemList: ['发送给朋友', '生成分享海报', '复制链接'],
      success: (res) => {
        if (res.tapIndex === 0) {
          // 微信内置分享
        } else if (res.tapIndex === 1) {
          this.generatePoster()
        } else if (res.tapIndex === 2) {
          wx.setClipboardData({
            data: `https://example.com/case/${this.data.id}`,
            success: () => wx.showToast({ title: '链接已复制', icon: 'success' })
          })
        }
      }
    })
  },

  // ===== 收藏 =====
  handleCollect() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    const collected = this.data.isCollected
    app.request({
      url: `/cases/${this.data.id}/collect`,
      method: collected ? 'DELETE' : 'POST',
      success: () => {
        this.setData({ isCollected: !collected })
        wx.showToast({ title: collected ? '已取消收藏' : '已收藏', icon: 'success' })
      },
      fail: () => {
        // Mock
        this.setData({ isCollected: !collected })
        wx.showToast({ title: collected ? '已取消收藏' : '已收藏', icon: 'success' })
      }
    })
  },
  checkCollection() {
    const collections = wx.getStorageSync('collections') || []
    const exists = collections.some(c => String(c.id) === String(this.data.id))
    this.setData({ isCollected: exists })
  },

  // ===== 点赞 =====
  handleLike() {
    const token = wx.getStorageSync('token')
    if (!token) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    const liked = this.data.isLiked
    app.request({
      url: `/cases/${this.data.id}/like`,
      method: 'POST',
      success: () => {
        this.setData({ isLiked: !liked, likeCount: liked ? this.data.likeCount - 1 : this.data.likeCount + 1 })
        wx.showToast({ title: liked ? '已取消收藏' : '已收藏', icon: 'success' })
      },
      fail: () => wx.showToast({ title: '操作失败', icon: 'none' })
    })
  },

  // ===== 订阅 =====
  handleSubscribe() {
    if (this.data.isSubscribed) { wx.showToast({ title: '已订阅该案例', icon: 'none' }); return }
    this.setData({ showLeadForm: true })
  },

  // ===== VR =====
  openVR() {
    if (this.data.vrLink) {
      wx.navigateTo({ url: `/pages/webview/index?url=${encodeURIComponent(this.data.vrLink)}` })
    }
  },

  // ===== 报价弹窗 =====
  showQuote() {
    if (this.data.quoteItems.length > 0) this.setData({ showQuotePopup: true })
  },
  closeQuote() { this.setData({ showQuotePopup: false }) },

  // ===== 跳转 =====
  goToDesigner(e) {
    const id = e.currentTarget.dataset.id
    if (id) wx.navigateTo({ url: `/pages/designer/index?id=${id}` })
  },
  goToProduct(e) {
    wx.navigateTo({ url: `/pages/product-detail/index?id=${e.currentTarget.dataset.id}` })
  },
  goToCaseDetail(e) {
    wx.navigateTo({ url: `/pages/case-detail/case-detail?id=${e.currentTarget.dataset.id}` })
  },
  goToCaseList() {
    wx.switchTab({ url: '/pages/cases/cases' })
  },
  goConsult() {
    wx.navigateTo({ url: `/pages/lead/lead?source=案例详情&sourceId=${this.data.id}` })
  },

  // ===== 留资表单 =====
  onLeadInput(e) {
    this.setData({ [`leadForm.${e.currentTarget.dataset.field}`]: e.detail.value })
  },
  submitLead() {
    const { name, phone } = this.data.leadForm
    if (!name.trim()) { wx.showToast({ title: '请输入称呼', icon: 'none' }); return }
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) { wx.showToast({ title: '请输入正确手机号', icon: 'none' }); return }
    this.setData({ leadSubmitting: true })
    app.request({
      url: '/leads',
      method: 'POST',
      data: { ...this.data.leadForm, source: '案例详情页', source_id: this.data.id },
      success: () => this.setData({ showLeadSuccess: true, leadSubmitting: false, isSubscribed: true }),
      fail: () => this.setData({ showLeadSuccess: true, leadSubmitting: false, isSubscribed: true })
    })
  },
  closeLeadForm() {
    this.setData({ showLeadForm: false, showLeadSuccess: false, leadForm: { name: '', phone: '', area: '', message: '' } })
  },

  // ===== 评论 =====
  onCommentInput(e) { this.setData({ commentInput: e.detail.value }) },
  submitComment() {
    const content = this.data.commentInput.trim()
    if (!content) { wx.showToast({ title: '请输入评论内容', icon: 'none' }); return }
    if (!wx.getStorageSync('token')) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    const newComment = { id: Date.now(), name: '我', avatar: '', content, likeCount: 0, isLiked: false, timeAgo: '刚刚' }
    this.setData({ comments: [newComment, ...this.data.comments], commentInput: '' })
    wx.showToast({ title: '评论成功', icon: 'success' })
  },
  likeComment(e) {
    const id = e.currentTarget.dataset.id
    const comments = this.data.comments.map(c => c.id === id ? { ...c, isLiked: !c.isLiked, likeCount: c.isLiked ? c.likeCount - 1 : c.likeCount + 1 } : c)
    this.setData({ comments })
  },
  replyComment(e) {
    this.setData({ commentInput: `@${e.currentTarget.dataset.name} ` })
  },

  // ===== 预约咨询（打开留资弹窗）=====
  goConsult() {
    this.setData({ showLeadForm: true })
  },

  // ===== 选品单 =====
  checkSelection() {
    const selection = wx.getStorageSync('selection') || []
    const exists = selection.some(item => String(item.id) === String(this.data.id) && item.type === 'case')
    this.setData({ inSelection: exists })
  },
  onAddToSelection() {
    if (this.data.inSelection) { wx.showToast({ title: '已在选品单中', icon: 'none' }); return }
    let selection = wx.getStorageSync('selection') || []
    selection.push({ id: this.data.id, type: 'case', title: this.data.caseDetail ? this.data.caseDetail.title : '', image: this.data.heroImages[0] || '', price: this.data.budgetStr || '' })
    wx.setStorageSync('selection', selection)
    this.setData({ inSelection: true })
    wx.showToast({ title: '已加入选品单', icon: 'success' })
  },

  // ===== 分享海报 =====
  generatePoster() {
    wx.showLoading({ title: '生成中...' })
    setTimeout(() => {
      wx.hideLoading()
      this.setData({ showPoster: true, posterImage: this.data.heroImages[0] || '' })
    }, 1000)
  },
  closePoster() { this.setData({ showPoster: false }) },
  savePoster() {
    wx.saveImageToPhotosAlbum({
      filePath: this.data.posterImage,
      success: () => wx.showToast({ title: '已保存', icon: 'success' }),
      fail: () => wx.showToast({ title: '保存失败', icon: 'none' })
    })
  },
  sharePoster() { wx.showToast({ title: '请使用系统分享', icon: 'none' }) },

  // ===== 工具方法 =====
  formatPrice(price) {
    if (!price) return '0'
    const num = parseFloat(price)
    if (num >= 10000) return (num / 10000).toFixed(1) + '万'
    return num.toLocaleString()
  },
  formatWan(value) {
    if (!value) return '-'
    const wan = Number(value) / 10000
    return wan >= 1 ? wan.toFixed(1) + '万' : Number(value).toLocaleString() + '元'
  },

  // ===== Mock 数据 =====
  getMockDetail(id) {
    return {
      id, title: '龙湖天街·现代轻奢', subtitle: '现代轻奢风格 · 128㎡',
      location: '成都市高新区龙湖天街', area: 128, house_type: '四室两厅',
      style: '现代', atmosphere: '温馨', is_featured: true, is_real_case: true,
      package_type: '全案', duration: '120', total_price: 320000, deal_budget: 350000,
      design_concept: '本案以现代轻奢风格为基调，通过简洁的线条和克制的色彩搭配，营造出舒适而富有质感的居住空间。',
      cover_image: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800',
      hero_images: [
        'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800',
        'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800',
        'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800'
      ],
      view_count: 1280, like_count: 86, subscription_count: 34,
      planner: { id: 1, name: '张规划', avatar: '', styles: ['现代', '轻奢'] },
      designer: { id: 2, name: '李设计', avatar: '', styles: ['现代', '北欧', '新中式'] },
      customer_manager: { id: 3, name: '王经理', avatar: '' },
      main_colors: ['#2C3E50', '#ECF0F1'],
      auxiliary_colors: ['#D4AF37', '#C0C0C0'],
      accent_colors: ['#E74C3C'],
      phases: {
        "1": { phase_number: 1, layout_images: ['https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600'], layout_analysis: '原始户型为四室两厅，南北通透，采光良好。' },
        "2": { phase_number: 2, mood_images: ['https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600', 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600'], mood_text: '以意大利米兰家居展为灵感源泉，提取当代极简主义的精髓。' },
        "3": { phase_number: 3, plan_image: 'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=600', plan_text: '重新规划了动线关系，打通客厅与餐厅的隔墙。' },
        "4": { phase_number: 4, birdview_images: ['https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600'] },
        "5": { phase_number: 5, showcase_title1: '光影诗篇', showcase_images: ['https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600'], showcase_quote: '空间是光的容器，设计是光影的诗篇。' },
        "6": { phase_number: 6, spaces: [
          { space_name: '客厅', renderings: [{ url: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600', title: '客厅全景' }] },
          { space_name: '主卧', renderings: [{ url: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600', title: '主卧' }] }
        ]}
      },
      related_products: [
        { id: 1, name: '意式极简沙发', brand: 'D&B', main_image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=300', sale_price: 28800 },
        { id: 2, name: '大理石茶几', brand: 'D&B', main_image: 'https://images.unsplash.com/photo-1533090481720-856c8141c875?w=300', sale_price: 8600 }
      ],
      timeline_nodes: [
        { id: 1, phase: '策划咨询', node_name: '需求沟通', status: 'completed', photos: [] },
        { id: 2, phase: '策划咨询', node_name: '现场量房', status: 'completed', photos: [] },
        { id: 3, phase: '设计阶段', node_name: '平面方案', status: 'completed', photos: [] },
        { id: 4, phase: '设计阶段', node_name: '效果图确认', status: 'ongoing', photos: [] }
      ]
    }
  },

  // ===== 收藏功能 =====
  checkFavorite() {
    const token = wx.getStorageSync('token')
    if (!token) {
      this.setData({ isFavorited: false })
      return
    }
    app.request({
      url: `/user/collections/check`,
      data: { type: 'case', target_id: this.data.id },
      success: (res) => {
        this.setData({ isFavorited: res && res.is_favorited })
      },
      fail: () => {
        this.setData({ isFavorited: false })
      }
    })
  },

  toggleFavorite() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '收藏案例需要先登录',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' })
          }
        }
      })
      return
    }

    const isFavorited = this.data.isFavorited
    
    app.request({
      url: `/user/collections/${this.data.id}`,
      method: isFavorited ? 'DELETE' : 'POST',
      data: { type: 'case' },
      success: () => {
        this.setData({ isFavorited: !isFavorited })
        wx.showToast({ title: isFavorited ? '已取消收藏' : '收藏成功', icon: 'none' })
      },
      fail: () => {
        // 离线模式也切换状态
        this.setData({ isFavorited: !isFavorited })
        wx.showToast({ title: isFavorited ? '已取消收藏' : '收藏成功', icon: 'none' })
      }
    })
  }
})
