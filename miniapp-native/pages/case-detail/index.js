const app = getApp()

Page({
  data: {
    loading: true,
    caseDetail: null,
    isLiked: false,
    isSubscribed: false,
    showFixedNav: false,
    showLeadModal: false,
    mediaList: [],
    timelineList: [],
    relatedProducts: [],
    leadForm: {
      name: '',
      phone: '',
      remark: ''
    }
  },

  onLoad(options) {
    const { id } = options
    if (id) {
      this.loadCaseDetail(id)
    } else {
      wx.showToast({
        title: '案例ID缺失',
        icon: 'error'
      })
    }
  },

  onShow() {
    // 页面显示时检查订阅状态
    if (this.data.caseDetail) {
      this.checkSubscription()
    }
  },

  onPageScroll(e) {
    const scrollTop = e.scrollTop
    const windowHeight = wx.getSystemInfoSync().windowHeight
    const showFixedNav = scrollTop > windowHeight * 0.6
    
    if (showFixedNav !== this.data.showFixedNav) {
      this.setData({ showFixedNav })
    }
  },

  onShareAppMessage() {
    const { caseDetail } = this.data
    return {
      title: caseDetail?.title || 'D&B 帝标|设记家精选案例',
      path: `/pages/case-detail/index?id=${caseDetail?.id}`,
      imageUrl: caseDetail?.cover_image
    }
  },

  onShareTimeline() {
    const { caseDetail } = this.data
    return {
      title: caseDetail?.title || 'D&B 帝标|设记家精选案例',
      query: `id=${caseDetail?.id}`,
      imageUrl: caseDetail?.cover_image
    }
  },

  // 加载案例详情
  async loadCaseDetail(id) {
    this.setData({ loading: true })
    
    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/cases/${id}`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token') || ''}`
        }
      })

      if (res.statusCode === 200 && res.data) {
        const caseDetail = res.data
        
        // 处理媒体列表
        const mediaList = []
        if (caseDetail.media_files) {
          mediaList.push(...caseDetail.media_files)
        }
        if (caseDetail.images) {
          mediaList.push(...caseDetail.images.map(url => ({ url })))
        }

        // 处理时间轴
        const timelineList = caseDetail.timeline_nodes || []

        // 处理相关产品
        const relatedProducts = caseDetail.related_products || []

        this.setData({
          caseDetail,
          mediaList,
          timelineList,
          relatedProducts,
          loading: false
        })

        // 更新页面标题
        wx.setNavigationBarTitle({
          title: caseDetail.title
        })

        // 检查订阅状态
        this.checkSubscription()
        
        // 增加浏览量
        this.incrementViewCount(id)
      } else {
        throw new Error('加载失败')
      }
    } catch (error) {
      console.error('加载案例详情失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
      this.setData({ loading: false })
    }
  },

  // 检查订阅状态
  async checkSubscription() {
    const { caseDetail } = this.data
    if (!caseDetail) return

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/cases/${caseDetail.id}/subscription-status`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token') || ''}`
        }
      })

      if (res.statusCode === 200) {
        this.setData({
          isSubscribed: res.data?.is_subscribed || false
        })
      }
    } catch (e) {
      // 未登录时忽略错误
    }
  },

  // 增加浏览量
  async incrementViewCount(id) {
    try {
      await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/cases/${id}/view`,
        method: 'POST'
      })
    } catch (e) {
      // 忽略错误
    }
  },

  // 返回上一页
  goBack() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        wx.switchTab({
          url: '/pages/cases/index'
        })
      }
    })
  },

  // 滚动到内容区
  scrollToContent() {
    wx.createSelectorQuery()
      .select('#content')
      .boundingClientRect(rect => {
        if (rect) {
          wx.pageScrollTo({
            scrollTop: rect.top + 200,
            duration: 500
          })
        }
      })
      .exec()
  },

  // 点赞/收藏
  async handleLike() {
    const { caseDetail, isLiked } = this.data
    
    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/cases/${caseDetail.id}/like`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token') || ''}`
        }
      })

      if (res.statusCode === 200) {
        this.setData({
          isLiked: !isLiked,
          'caseDetail.like_count': caseDetail.like_count + (isLiked ? -1 : 1)
        })
        
        wx.showToast({
          title: isLiked ? '已取消收藏' : '已收藏',
          icon: 'success'
        })
      } else if (res.statusCode === 401) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.showToast({
        title: '操作失败',
        icon: 'error'
      })
    }
  },

  // 分享
  handleShare() {
    // 触发系统分享菜单
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
    
    wx.showToast({
      title: '点击右上角分享',
      icon: 'none'
    })
  },

  // 订阅/取消订阅
  async handleSubscribe() {
    const { caseDetail, isSubscribed } = this.data
    
    try {
      const url = `${app.globalData.apiBaseUrl}/api/v3/cases/${caseDetail.id}/subscribe`
      const res = await wx.request({
        url: isSubscribed ? url : url,
        method: isSubscribed ? 'DELETE' : 'POST',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token') || ''}`
        }
      })

      if (res.statusCode === 200) {
        this.setData({
          isSubscribed: !isSubscribed,
          'caseDetail.subscription_count': caseDetail.subscription_count + (isSubscribed ? -1 : 1)
        })
        
        wx.showToast({
          title: isSubscribed ? '已取消订阅' : '订阅成功',
          icon: 'success'
        })
      } else if (res.statusCode === 401) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.showToast({
        title: '操作失败',
        icon: 'error'
      })
    }
  },

  // 预览图片
  previewImage(e) {
    const { index } = e.currentTarget.dataset
    const { mediaList } = this.data
    const urls = mediaList.map(item => item.url || item.file_url)
    
    wx.previewImage({
      current: urls[index],
      urls
    })
  },

  // 预览时间轴图片
  previewTimelineImage(e) {
    const { url } = e.currentTarget.dataset
    
    wx.previewImage({
      current: url,
      urls: [url]
    })
  },

  // 打开 VR
  openVR() {
    const { caseDetail } = this.data
    if (caseDetail.vr_link) {
      wx.navigateTo({
        url: `/pages/webview/index?url=${encodeURIComponent(caseDetail.vr_link)}`
      })
    }
  },

  // 跳转到产品
  goToProduct(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/product-detail/index?id=${id}`
    })
  },

  // 显示留资表单
  showLeadForm() {
    this.setData({
      showLeadModal: true,
      leadForm: { name: '', phone: '', remark: '' }
    })
  },

  // 隐藏留资表单
  hideLeadForm() {
    this.setData({ showLeadModal: false })
  },

  // 阻止冒泡
  preventBubble() {
    // 什么都不做，阻止事件冒泡
  },

  // 输入姓名
  onNameInput(e) {
    this.setData({
      'leadForm.name': e.detail.value
    })
  },

  // 输入手机号
  onPhoneInput(e) {
    this.setData({
      'leadForm.phone': e.detail.value
    })
  },

  // 输入留言
  onRemarkInput(e) {
    this.setData({
      'leadForm.remark': e.detail.value
    })
  },

  // 提交留资
  async submitLead() {
    const { leadForm, caseDetail } = this.data
    
    if (!leadForm.name.trim()) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      })
      return
    }
    
    if (!leadForm.phone.trim() || !/^1[3-9]\d{9}$/.test(leadForm.phone)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/api/v3/leads`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${wx.getStorageSync('token') || ''}`
        },
        data: {
          name: leadForm.name,
          phone: leadForm.phone,
          remark: leadForm.remark,
          source_type: 'case',
          source_id: caseDetail.id,
          source_name: caseDetail.title
        }
      })

      if (res.statusCode === 200 || res.statusCode === 201) {
        wx.showToast({
          title: '提交成功',
          icon: 'success'
        })
        this.setData({ showLeadModal: false })
      } else {
        throw new Error('提交失败')
      }
    } catch (error) {
      wx.showToast({
        title: '提交失败，请重试',
        icon: 'error'
      })
    }
  },

  // 格式化价格
  formatPrice(price) {
    if (!price) return '0'
    return parseFloat(price).toLocaleString('zh-CN')
  },

  // 格式化日期
  formatDate(date) {
    if (!date) return ''
    const d = new Date(date)
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
  },

  // 解析媒体URL
  parseMediaUrls(urls) {
    if (!urls) return []
    if (typeof urls === 'string') {
      try {
        return JSON.parse(urls)
      } catch {
        return urls.split(',').map(u => u.trim())
      }
    }
    return urls
  }
})
