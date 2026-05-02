const app = getApp();

Page({
  data: {
    form: {
      name: '',
      phone: '',
      address: '',
      date: '',
      time: '',
      remark: ''
    },
    
    today: '',
    timeOptions: ['上午 9:00-12:00', '下午 14:00-18:00', '晚上 18:00-20:00'],
    
    submitting: false,
    showSuccess: false
  },

  onLoad() {
    // 设置今天日期
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    
    this.setData({
      today: `${year}-${month}-${day}`
    });
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset;
    const { value } = e.detail;
    
    this.setData({
      [`form.${field}`]: value
    });
  },

  onDateChange(e) {
    this.setData({
      'form.date': e.detail.value
    });
  },

  onTimeSelect(e) {
    const { time } = e.currentTarget.dataset;
    this.setData({
      'form.time': time
    });
  },

  submitForm() {
    const { form } = this.data;
    
    if (!form.name.trim()) {
      wx.showToast({ title: '请输入您的称呼', icon: 'none' });
      return;
    }
    
    if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
      wx.showToast({ title: '请输入正确手机号', icon: 'none' });
      return;
    }
    
    if (!form.address.trim()) {
      wx.showToast({ title: '请输入房屋地址', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    app.request({
      url: '/appointments',
      method: 'POST',
      data: {
        customer_name: form.name,
        phone: form.phone,
        house_address: form.address,
        appointment_date: form.date,
        appointment_time: form.time,
        remark: form.remark,
        source: '小程序预约'
      },
      success: () => {
        app.markAsLeaded();
        this.setData({ 
          submitting: false,
          showSuccess: true 
        });
      },
      fail: () => {
        app.markAsLeaded();
        this.setData({ 
          submitting: false,
          showSuccess: true 
        });
      }
    });
  },

  closeSuccess() {
    this.setData({ showSuccess: false });
    wx.navigateBack();
  }
});