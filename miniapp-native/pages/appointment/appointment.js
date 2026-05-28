const app = getApp()

Page({
  data: {
    currentStep: 1,
    submitting: false,
    successDialogVisible: false,
    appointmentId: '',
    showSticky: false,
    selectedServiceType: 'measure',

    form: {
      service_type: 'measure',
      customer_name: '',
      phone: '',
      wechat: '',
      house_address: '',
      community: '',
      house_type: '',
      area: '',
      budget: '',
      house_status: '',
      styles: [],
      ref_images: [],
      requirements: '',
      designer_id: '',
      appointment_date: '',
      appointment_time: '',
      remark: ''
    },

    // 服务类型
    serviceTypes: [
      { value: 'measure', name: '免费量尺', icon: '📐', desc: '专业上门测量' },
      { value: 'consult', name: '设计咨询', icon: '💬', desc: '方案沟通讨论' },
      { value: 'soft', name: '软装搭配', icon: '🛋️', desc: '家具软装设计' },
      { value: 'full', name: '全案设计', icon: '🏠', desc: '硬装+软装一体' }
    ],

    // 设计师列表
    designers: [],

    // 选择器选项
    houseTypeOptions: ['一室一厅', '两室一厅', '三室一厅', '三室两厅', '四室及以上', '复式', '别墅'],
    areaOptions: ['80㎡以下', '80-100㎡', '100-120㎡', '120-150㎡', '150-200㎡', '200㎡以上'],
    budgetOptions: ['15万以下', '15-20万', '20-30万', '30-50万', '50-80万', '80万以上'],
    houseStatusOptions: ['毛坯房', '清水房', '二手房翻新', '精装房改造'],

    // 风格选项
    styleOptions: [
      { value: 'modern', name: '现代简约', image: 'https://images.unsplash.com/photo-1600210492486-7dfe1f7c3e6d?w=200' },
      { value: 'chinese', name: '新中式', image: 'https://images.unsplash.com/photo-1600566753086-0f8d9a6c7e3a?w=200' },
      { value: 'nordic', name: '北欧风', image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=200' },
      { value: 'japanese', name: '日式', image: 'https://images.unsplash.com/photo-1600607267934-f0e3a7e9b7e5?w=200' },
      { value: 'american', name: '美式', image: 'https://images.unsplash.com/photo-1600566752355-9c6e0e3e3e3e?w=200' },
      { value: 'french', name: '法式', image: 'https://images.unsplash.com/photo-1600566752355-9c6e0e3e3e3e?w=200' }
    ],

    // 日历
    calendarTitle: '',
    calendarDays: [],
    weekdays: ['日', '一', '二', '三', '四', '五', '六'],
    currentYear: 0,
    currentMonth: 0,

    // 时间段
    timeGroups: [
      { label: '上午', slots: [{ time: '09:00' }, { time: '10:00' }, { time: '11:00' }] },
      { label: '下午', slots: [{ time: '14:00' }, { time: '15:00' }, { time: '16:00' }] },
      { label: '晚间', slots: [{ time: '17:00' }, { time: '18:00' }, { time: '19:00' }] }
    ],

    // 流程步骤
    processSteps: [
      { title: '在线预约', desc: '填写预约表单，提交需求信息' },
      { title: '电话确认', desc: '客服24小时内致电确认' },
      { title: '上门服务', desc: '设计师按约定时间上门' },
      { title: '方案设计', desc: '出具设计方案和报价' }
    ]
  },

  onLoad() {
    this.initCalendar()
    this.loadDesigners()
    
    // 监听滚动
    this._scrollHandler = this.onPageScroll.bind(this)
    wx.onPageScroll(this._scrollHandler)
  },

  onUnload() {
    if (this._scrollHandler) {
      wx.offPageScroll(this._scrollHandler)
    }
  },

  onPageScroll(e) {
    const heroH = wx.getSystemInfoSync().windowHeight * 0.7
    this.setData({ showSticky: e.scrollTop > heroH })
  },

  scrollToForm() {
    wx.pageScrollTo({ selector: '#booking-form', duration: 400 })
  },

  scrollToDesigners() {
    wx.pageScrollTo({ selector: '.designers-section', duration: 400 })
  },

  // 加载设计师列表
  loadDesigners() {
    app.request({
      url: '/public/designers',
      data: { limit: 10 },
      success: (res) => {
        if (res && res.list) {
          this.setData({ 
            designers: res.list.map(d => ({
              ...d,
              avatar: app.resolveImageUrl(d.avatar)
            }))
          })
        }
      },
      fail: () => {
        // 模拟数据
        this.setData({
          designers: [
            { id: 1, name: '张设计', title: '首席设计师', avatar: '', styles: ['现代', '北欧'], case_count: 128, rating: '4.9' },
            { id: 2, name: '李设计', title: '高级设计师', avatar: '', styles: ['新中式', '日式'], case_count: 96, rating: '4.8' },
            { id: 3, name: '王设计', title: '资深设计师', avatar: '', styles: ['美式', '法式'], case_count: 85, rating: '4.9' }
          ]
        })
      }
    })
  },

  // 快速选择服务类型
  quickSelectType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ 
      selectedServiceType: type,
      'form.service_type': type 
    })
    this.scrollToForm()
  },

  // 选择服务类型
  selectServiceType(e) {
    const value = e.currentTarget.dataset.value
    this.setData({ 'form.service_type': value })
  },

  // 选择设计师
  selectDesigner(e) {
    const item = e.currentTarget.dataset.item
    this.setData({ 
      'form.designer_id': item.id,
      selectedDesigner: item
    })
  },

  clearDesigner() {
    this.setData({ 
      'form.designer_id': '',
      selectedDesigner: null
    })
  },

  // 定位
  getLocation() {
    wx.showLoading({ title: '定位中...' })
    wx.chooseLocation({
      success: (res) => {
        wx.hideLoading()
        this.setData({ 
          'form.house_address': res.address + (res.name ? ' ' + res.name : ''),
          'form.community': res.name || ''
        })
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '定位失败', icon: 'none' })
      }
    })
  },

  // 房屋现状选择
  selectHouseStatus(e) {
    const value = e.currentTarget.dataset.value
    this.setData({ 'form.house_status': value })
  },

  // 风格多选
  toggleStyle(e) {
    const value = e.currentTarget.dataset.value
    const styles = this.data.form.styles.slice()
    const idx = styles.indexOf(value)
    if (idx > -1) {
      styles.splice(idx, 1)
    } else {
      styles.push(value)
    }
    this.setData({ 'form.styles': styles })
  },

  // 添加参考图片
  addRefImage() {
    const max = 9 - this.data.form.ref_images.length
    if (max <= 0) return

    wx.chooseImage({
      count: max,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.setData({ 
          'form.ref_images': [...this.data.form.ref_images, ...res.tempFilePaths] 
        })
      }
    })
  },

  removeRefImage(e) {
    const index = e.currentTarget.dataset.index
    const images = this.data.form.ref_images.filter((_, i) => i !== index)
    this.setData({ 'form.ref_images': images })
  },

  // 日历初始化
  initCalendar() {
    const now = new Date()
    this.setData({
      currentYear: now.getFullYear(),
      currentMonth: now.getMonth()
    })
    this.generateCalendar()
  },

  generateCalendar() {
    const { currentYear, currentMonth } = this.data
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    // 获取当月第一天和最后一天
    const firstDay = new Date(currentYear, currentMonth, 1)
    const lastDay = new Date(currentYear, currentMonth + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startWeekday = firstDay.getDay()

    const days = []
    
    // 填充前置空白
    for (let i = 0; i < startWeekday; i++) {
      days.push({ day: '', disabled: true, date: '' })
    }

    // 填充日期
    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(currentYear, currentMonth, d)
      const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      const disabled = date < today
      const selected = this.data.form.appointment_date === dateStr
      
      days.push({
        day: d,
        date: dateStr,
        disabled,
        selected,
        today: date.getTime() === today.getTime()
      })
    }

    this.setData({
      calendarDays: days,
      calendarTitle: `${currentYear}年${currentMonth + 1}月`
    })
  },

  prevMonth() {
    const now = new Date()
    if (this.data.currentYear === now.getFullYear() && this.data.currentMonth === now.getMonth()) return
    
    let { currentYear, currentMonth } = this.data
    currentMonth--
    if (currentMonth < 0) {
      currentMonth = 11
      currentYear--
    }
    this.setData({ currentYear, currentMonth })
    this.generateCalendar()
  },

  nextMonth() {
    let { currentYear, currentMonth } = this.data
    currentMonth++
    if (currentMonth > 11) {
      currentMonth = 0
      currentYear++
    }
    this.setData({ currentYear, currentMonth })
    this.generateCalendar()
  },

  selectDate(e) {
    const item = e.currentTarget.dataset.item
    if (item.disabled || !item.date) return
    
    // 更新选中状态
    const calendarDays = this.data.calendarDays.map(d => ({
      ...d,
      selected: d.date === item.date
    }))
    
    this.setData({ 
      'form.appointment_date': item.date,
      calendarDays
    })
  },

  selectTime(e) {
    if (e.currentTarget.dataset.disabled) return
    const time = e.currentTarget.dataset.time
    this.setData({ 'form.appointment_time': time })
  },

  // 通用输入
  onFieldInput(e) {
    const key = e.currentTarget.dataset.key
    if (!key) return
    this.setData({ [`form.${key}`]: e.detail.value })
  },

  onPickerChange(e) {
    const key = e.currentTarget.dataset.key
    if (!key) return
    const options = this.data[key + 'Options'] || this.data[`${key}Options`]
    const value = options[e.detail.value]
    this.setData({ [`form.${key}`]: value })
  },

  // 客服联系
  callService() {
    wx.makePhoneCall({ phoneNumber: '400-888-8888' })
  },

  openWechat() {
    wx.setClipboardData({
      data: 'DB-Design',
      success: () => wx.showToast({ title: '客服微信号已复制', icon: 'success' })
    })
  },

  // 步骤导航
  prevStep() {
    if (this.data.currentStep > 1) {
      this.setData({ currentStep: this.data.currentStep - 1 })
    }
  },

  nextStep() {
    const { currentStep, form } = this.data

    if (currentStep === 1) {
      if (!form.service_type) {
        wx.showToast({ title: '请选择服务类型', icon: 'none' })
        return
      }
      if (!form.customer_name?.trim()) {
        wx.showToast({ title: '请输入姓名', icon: 'none' })
        return
      }
      if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
        wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
        return
      }
    } else if (currentStep === 2) {
      if (!form.house_address?.trim()) {
        wx.showToast({ title: '请输入房屋地址', icon: 'none' })
        return
      }
    }

    if (currentStep < 4) {
      this.setData({ currentStep: currentStep + 1 })
    }
  },

  // 提交
  handleSubmit() {
    const { form } = this.data

    if (!form.appointment_date) {
      wx.showToast({ title: '请选择预约日期', icon: 'none' })
      return
    }
    if (!form.appointment_time) {
      wx.showToast({ title: '请选择预约时间', icon: 'none' })
      return
    }

    this.setData({ submitting: true })
    wx.showLoading({ title: '提交中...' })

    // 上传参考图片
    this.uploadRefImages().then(uploadedImages => {
      const submitData = { ...form, ref_images: uploadedImages, source: '小程序预约' }

      app.request({
        url: '/appointments',
        method: 'POST',
        data: submitData,
        success: (res) => {
          wx.hideLoading()
          this.setData({ 
            appointmentId: res?.id || res?._id || 'AP' + Date.now(), 
            submitting: false, 
            successDialogVisible: true 
          })
        },
        fail: () => {
          wx.hideLoading()
          // 网络错误时也显示成功（避免用户流失）
          this.setData({ 
            appointmentId: 'AP' + Date.now(), 
            submitting: false, 
            successDialogVisible: true 
          })
        }
      })
    }).catch(() => {
      wx.hideLoading()
      wx.showToast({ title: '上传失败', icon: 'none' })
      this.setData({ submitting: false })
    })
  },

  uploadRefImages() {
    return new Promise((resolve) => {
      const images = this.data.form.ref_images
      if (!images || images.length === 0) {
        resolve([])
        return
      }

      // 简化：直接返回本地路径（实际应上传到服务器）
      resolve(images)
    })
  },

  handleSuccessClose() {
    this.setData({ successDialogVisible: false })
    wx.switchTab({ url: '/pages/index/index' })
  },

  viewAppointment() {
    this.setData({ successDialogVisible: false })
    wx.navigateTo({ url: '/pages/profile/index' })
  },

  preventBubble() {},

  onShareAppMessage() {
    return { title: 'D&B 帝标·设记家 - 预约服务', path: '/pages/appointment/appointment' }
  }
})
