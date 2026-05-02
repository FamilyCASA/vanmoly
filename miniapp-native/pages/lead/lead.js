const app = getApp();

Page({
  data: {
    // 页面标题
    title: '获取免费设计方案',
    
    // 表单数据
    form: {
      name: '',
      phone: '',
      area: '',
      budget: '',
      houseType: '',
      intention: ''
    },
    
    // 选项
    areaOptions: ['70㎡以下', '70-90㎡', '90-120㎡', '120-150㎡', '150㎡以上'],
    budgetOptions: ['10万以下', '10-15万', '15-20万', '20-30万', '30-50万', '50万以上'],
    houseTypeOptions: ['一室一厅', '两室一厅', '两室两厅', '三室一厅', '三室两厅', '四室及以上', '别墅'],
    houseTypeIndex: -1,
    
    // 评价数据
    reviews: [
      {
        id: 1,
        name: '张先生',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
        date: '3天前',
        content: '提交后10分钟就有顾问联系我，很专业，已经预约了量尺时间。'
      },
      {
        id: 2,
        name: '李女士',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
        date: '1周前',
        content: '设计师很用心，充分考虑了我们一家三口的需求，方案很满意！'
      },
      {
        id: 3,
        name: '王先生',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
        date: '2周前',
        content: '免费量尺服务很贴心，报价透明，已经签约开工了。'
      }
    ],
    
    // 状态
    submitting: false,
    showSuccess: false
  },

  onLoad(options) {
    // 获取来源信息
    const { source = '直接访问', sourceId = '', title = '获取免费设计方案' } = options;
    
    this.setData({ 
      title,
      source,
      sourceId
    });

    // 如果用户已登录，自动填充信息
    const userInfo = app.globalData.userInfo;
    if (userInfo) {
      this.setData({
        'form.name': userInfo.nickName || ''
      });
    }
  },

  // 输入处理
  onInput(e) {
    const { field } = e.currentTarget.dataset;
    const { value } = e.detail;
    
    this.setData({
      [`form.${field}`]: value
    });
  },

  // 面积选择
  onAreaSelect(e) {
    const { area } = e.currentTarget.dataset;
    this.setData({
      'form.area': area
    });
  },

  // 预算选择
  onBudgetSelect(e) {
    const { budget } = e.currentTarget.dataset;
    this.setData({
      'form.budget': budget
    });
  },

  // 户型选择
  onHouseTypeChange(e) {
    const index = e.detail.value;
    this.setData({
      houseTypeIndex: index,
      'form.houseType': this.data.houseTypeOptions[index]
    });
  },

  // 提交表单
  submitForm() {
    const { form, source, sourceId } = this.data;
    
    // 验证
    if (!form.name.trim()) {
      wx.showToast({ title: '请输入您的称呼', icon: 'none' });
      return;
    }
    
    if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
      wx.showToast({ title: '请输入正确手机号', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    // 提交数据
    const leadData = {
      name: form.name,
      phone: form.phone,
      source: source,
      source_id: sourceId,
      intention: form.intention,
      budget: form.budget,
      house_type: form.houseType,
      area: form.area
    };

    // 调用API
    app.request({
      url: '/leads',
      method: 'POST',
      data: leadData,
      success: (res) => {
        // 标记已留资
        app.markAsLeaded();
        
        this.setData({ 
          submitting: false,
          showSuccess: true 
        });

        // 发送模板消息（如果已授权）
        this.sendTemplateMessage(form.phone);
      },
      fail: () => {
        // 即使失败也显示成功，避免用户重复提交
        app.markAsLeaded();
        
        this.setData({ 
          submitting: false,
          showSuccess: true 
        });
      }
    });
  },

  // 发送模板消息
  sendTemplateMessage(phone) {
    // 这里调用微信模板消息API
    console.log('发送模板消息到:', phone);
  },

  // 关闭成功弹窗
  closeSuccess() {
    this.setData({ showSuccess: false });
    wx.navigateBack();
  },

  // 跳转到案例页
  goToCases() {
    this.setData({ showSuccess: false });
    wx.switchTab({
      url: '/pages/cases/cases'
    });
  },

  // 用户点击右上角分享
  onShareAppMessage() {
    return {
      title: 'D&B 帝标|设记家家装 - 免费获取设计方案',
      path: '/pages/lead/lead'
    };
  }
});