// 帮助中心
Page({
  data: {
    keyword: '',
    faqs: [
      { question: '如何预约设计师？', answer: '进入"我的"页面，点击"我的预约"，选择服务类型和预约时间即可。也可以在首页点击"立即预约"按钮。', expanded: false },
      { question: '产品如何购买？', answer: '在"产品"页面浏览产品，将心仪的产品加入选品单，确认后提交订单即可。', expanded: false },
      { question: '如何查看装修进度？', answer: '在案例详情页可以查看服务流程的实时进度，包括各阶段的施工节点和图片更新。', expanded: false },
      { question: '退款政策是什么？', answer: '产品在发货前可申请全额退款，发货后7天内可申请退货退款。定制产品不支持无理由退货。', expanded: false },
      { question: '如何联系客服？', answer: '您可以在"我的"页面点击"联系客服"拨打电话，或在"帮助中心"提交在线反馈。', expanded: false },
      { question: '积分如何获取？', answer: '每日签到、完成预约、购买产品、发表评论等都可以获取积分，积分可在"我的积分"页面查看详情。', expanded: false }
    ]
  },

  toggleFaq(e) {
    const index = e.currentTarget.dataset.index
    const key = `faqs[${index}].expanded`
    this.setData({ [key]: !this.data.faqs[index].expanded })
  },

  onKeywordInput(e) { this.setData({ keyword: e.detail.value }) },
  onSearch() {
    const { keyword, faqs } = this.data
    if (!keyword) return
    const results = faqs.filter(f => f.question.includes(keyword) || f.answer.includes(keyword))
    if (results.length === 0) {
      wx.showToast({ title: '未找到相关问题', icon: 'none' })
    } else {
      // 展开匹配的FAQ
      results.forEach((r, i) => {
        const idx = faqs.indexOf(r)
        this.setData({ [`faqs[${idx}].expanded`]: true })
      })
    }
  },

  callService() {
    wx.makePhoneCall({ phoneNumber: '400-888-8888' })
  },
  goFeedback() { wx.navigateTo({ url: '/pages/feedback/index' }) }
})