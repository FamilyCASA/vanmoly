Page({
  data: {
    quote: {},
    statusText: {
      draft: '草稿',
      sent: '已发送',
      confirmed: '已确认',
      signed: '已签署',
      expired: '已过期'
    }
  },

  onLoad(options) {
    const id = options.id
    this.loadQuoteDetail(id)
  },

  // 加载报价详情
  loadQuoteDetail(id) {
    // 模拟数据
    this.setData({
      quote: {
        id: id,
        quote_no: 'BJ202604260001',
        status: 'sent',
        customer_name: '张先生',
        customer_phone: '138****8888',
        customer_address: '成都市高新区xxx小区',
        subtotal: '220,000',
        management_fee_rate: 5,
        management_fee: '11,000',
        tax_rate: 6,
        tax: '13,860',
        total_amount: '244,860',
        items: [
          {
            id: 1,
            name: '客厅沙发',
            room_name: '客厅',
            spec: '三人位真皮',
            unit: '件',
            quantity: 1,
            unit_price: '15,800',
            total_price: '15,800'
          },
          {
            id: 2,
            name: '主卧衣柜',
            room_name: '主卧',
            spec: '定制推拉门',
            unit: '套',
            quantity: 1,
            unit_price: '8,500',
            total_price: '8,500'
          },
          {
            id: 3,
            name: '全屋灯具',
            room_name: '全屋',
            spec: 'LED套装',
            unit: '套',
            quantity: 1,
            unit_price: '6,200',
            total_price: '6,200'
          }
        ]
      }
    })

    // 实际 API 调用：
    // wx.request({
    //   url: `http://127.0.0.1:5000/api/v3/quotes/${id}`,
    //   header: {
    //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
    //   },
    //   success: (res) => {
    //     if (res.statusCode === 200) {
    //       this.setData({ quote: res.data })
    //     }
    //   }
    // })
  },

  // 返回
  goBack() {
    wx.navigateBack()
  },

  // 签字确认
  signQuote() {
    wx.navigateTo({
      url: '/pages/signature/index?quote_id=' + this.data.quote.id
    })
  },

  // 分享报价
  shareQuote() {
    wx.showShareMenu({
      withShareTicket: true
    })
  },

  onShareAppMessage() {
    return {
      title: `D&B 帝标|设记家报价单 - ${this.data.quote.quote_no}`,
      path: `/pages/quote-detail/index?id=${this.data.quote.id}`
    }
  }
})