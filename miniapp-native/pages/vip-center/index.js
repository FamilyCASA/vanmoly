// 会员中心
const app = getApp()

Page({
  data: {
    userInfo: {},
    isVip: false,
    vipExpire: '',
    selectedPlan: 0,
    privileges: [
      { icon: '🏷️', name: '专属折扣', desc: '产品享受VIP折扣' },
      { icon: '👨‍💼', name: '专属设计师', desc: '一对一设计服务' },
      { icon: '📋', name: '优先排单', desc: '施工优先安排' },
      { icon: '🎁', name: '积分翻倍', desc: '消费积分双倍累计' },
      { icon: '📞', name: 'VIP客服', desc: '专属客服通道' },
      { icon: '📦', name: '免费配送', desc: '材料免费送货上门' }
    ],
    plans: [
      { duration: '月卡', price: 99, originalPrice: 199 },
      { duration: '季卡', price: 249, originalPrice: 597 },
      { duration: '年卡', price: 799, originalPrice: 2388 }
    ]
  },

  onLoad() {
    const userInfo = wx.getStorageSync('userInfo') || {}
    this.setData({
      userInfo,
      isVip: userInfo.isVip || false,
      vipExpire: userInfo.vipExpire || ''
    })
  },

  selectPlan(e) {
    this.setData({ selectedPlan: e.currentTarget.dataset.index })
  },

  openVip() {
    const plan = this.data.plans[this.data.selectedPlan]
    wx.showModal({
      title: '确认开通',
      content: `开通${plan.duration}会员，费用¥${plan.price}`,
      success: (res) => {
        if (res.confirm) {
          wx.showToast({ title: '支付功能开发中', icon: 'none' })
        }
      }
    })
  },

  renewVip() {
    wx.showToast({ title: '续费功能开发中', icon: 'none' })
  }
})