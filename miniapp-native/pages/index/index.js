const app = getApp();

Page({
  data: {
    // Banner数据
    banners: [
      {
        id: 1,
        image: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800',
        title: '品质整装 拎包入住',
        subtitle: '58节点服务流程，全程透明可控'
      },
      {
        id: 2,
        image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
        title: '0增项 预算即决算',
        subtitle: '合同价即结算价，拒绝隐形消费'
      },
      {
        id: 3,
        image: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800',
        title: '10年质保 售后无忧',
        subtitle: '国标E0级环保材料，守护家人健康'
      }
    ],

    // 精选案例
    featuredCases: [
      {
        id: 1,
        title: '龙湖天街·现代轻奢',
        cover: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600',
        style: '现代轻奢',
        area: 128,
        budget: '18-25万'
      },
      {
        id: 2,
        title: '万科城·北欧简约',
        cover: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600',
        style: '北欧简约',
        area: 95,
        budget: '12-16万'
      },
      {
        id: 3,
        title: '保利心语·新中式',
        cover: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600',
        style: '新中式',
        area: 145,
        budget: '22-30万'
      }
    ],

    // 客户评价
    reviews: [
      {
        id: 1,
        name: '李先生',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
        date: '2026-04-15',
        content: 'D&B 帝标|设记家的服务真的很专业，从设计到施工全程跟进，58个节点让我对进度了如指掌。最满意的是0增项承诺，预算就是决算！',
        image: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=400'
      },
      {
        id: 2,
        name: '王女士',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
        date: '2026-04-10',
        content: '设计师很用心，充分考虑了我们一家三口的居住需求。材料都是环保E0级的，入住后没有任何异味，孩子住得放心。',
        image: ''
      }
    ],

    // 弹窗控制
    showPopup: false,
    leadCount: 2580,
    phoneNumber: ''
  },

  onLoad() {
    // 30秒后自动弹出留资窗口（如果未留资）
    this.startAutoPopup();
  },

  onShow() {
    // 每次显示页面检查是否需要弹窗
    if (!app.globalData.leadConfig.hasLeaded) {
      this.checkAutoPopup();
    }
  },

  // 启动自动弹窗计时器
  startAutoPopup() {
    setTimeout(() => {
      if (!app.globalData.leadConfig.hasLeaded) {
        this.setData({ showPopup: true });
      }
    }, 30000); // 30秒
  },

  // 检查自动弹窗
  checkAutoPopup() {
    // 可以在这里添加更多触发逻辑
  },

  // Banner点击
  onBannerTap(e) {
    const item = e.currentTarget.dataset.item;
    console.log('Banner点击:', item);
    // 可以跳转到特定页面
  },

  // 跳转到案例列表
  goToCases() {
    wx.switchTab({
      url: '/pages/cases/cases'
    });
  },

  // 跳转到案例详情
  goToCaseDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/case-detail/case-detail?id=${id}`
    });
  },

  // 案例上的留资按钮
  onCaseLeadTap(e) {
    const caseItem = e.currentTarget.dataset.case;
    // 阻止冒泡
    e.stopPropagation();
    
    app.showLeadPopup({
      source: '案例获取同款',
      sourceId: caseItem.id,
      title: `获取「${caseItem.title}」同款方案`
    });
  },

  // 跳转到留资页面
  goToLead(e) {
    const source = e.currentTarget.dataset.source || '首页入口';
    wx.navigateTo({
      url: `/pages/lead/lead?source=${source}`
    });
  },

  // 跳转到预约页面
  goToAppointment() {
    wx.navigateTo({
      url: '/pages/appointment/appointment'
    });
  },

  // 拨打电话
  makePhoneCall() {
    wx.makePhoneCall({
      phoneNumber: '400-888-8888',
      success: () => {
        // 记录电话拨打
        this.trackEvent('phone_call', '首页电话咨询');
      }
    });
  },

  // 关闭弹窗
  closePopup() {
    this.setData({ showPopup: false });
  },

  // 阻止冒泡
  preventBubble() {
    // 什么都不做，只是阻止冒泡
  },

  // 手机号输入
  onPhoneInput(e) {
    this.setData({
      phoneNumber: e.detail.value
    });
  },

  // 提交留资（弹窗内）
  submitLead() {
    const { phoneNumber } = this.data;
    
    if (!phoneNumber || phoneNumber.length !== 11) {
      wx.showToast({
        title: '请输入正确手机号',
        icon: 'none'
      });
      return;
    }

    // 提交留资
    app.request({
      url: '/leads',
      method: 'POST',
      data: {
        phone: phoneNumber,
        source: '首页弹窗',
        intention: '获取免费设计方案'
      },
      success: (res) => {
        // 标记已留资
        app.markAsLeaded();
        
        this.setData({ showPopup: false });
        
        wx.showToast({
          title: '领取成功！',
          icon: 'success'
        });

        // 3秒后跳转到案例页
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/cases/cases'
          });
        }, 1500);
      },
      fail: () => {
        // 即使API失败，也标记为已留资，避免重复打扰
        app.markAsLeaded();
        this.setData({ showPopup: false });
        
        wx.showToast({
          title: '提交成功，顾问将联系您',
          icon: 'success'
        });
      }
    });
  },

  // 事件追踪
  trackEvent(event, label) {
    console.log('Track:', event, label);
    // 这里可以接入统计SDK
  },

  // 分享
  onShareAppMessage() {
    return {
      title: 'D&B 帝标|设记家家装 - 品质整装，拎包入住',
      path: '/pages/index/index',
      imageUrl: this.data.banners[0].image
    };
  }
});