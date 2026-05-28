// 我的预约
const app = getApp()

Page({
  data: {
    activeStatus: 'all',
    loading: true,
    appointments: [],
    pendingCount: 0
  },

  onLoad() {
    this.loadAppointments()
  },

  onShow() {
    this.loadAppointments()
  },

  // 切换状态Tab
  switchStatus(e) {
    const status = e.currentTarget.dataset.status
    this.setData({ activeStatus: status })
    this.loadAppointments()
  },

  // 加载预约列表
  loadAppointments() {
    this.setData({ loading: true })
    
    const { activeStatus } = this.data
    const data = {}
    if (activeStatus !== 'all') {
      data.status = activeStatus
    }

    app.request({
      url: '/user/appointments',
      data,
      success: (res) => {
        let list = []
        if (res && res.items) {
          list = res.items
        } else if (Array.isArray(res)) {
          list = res
        }
        
        const appointments = list.map(item => ({
          ...item,
          statusText: this.getStatusText(item.status),
          appointmentTime: this.formatDateTime(item.appointment_time || item.time),
          createdAt: this.formatDate(item.created_at)
        }))
        
        const pendingCount = list.filter(item => item.status === 'pending').length
        
        this.setData({ appointments, pendingCount, loading: false })
      },
      fail: () => {
        this.setData({ appointments: [], pendingCount: 0, loading: false })
      }
    })
  },

  // 取消预约
  cancelAppointment(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认取消',
      content: '确定要取消该预约吗？',
      success: (res) => {
        if (res.confirm) {
          app.request({
            url: `/user/appointments/${id}`,
            method: 'DELETE',
            success: () => {
              wx.showToast({ title: '已取消', icon: 'success' })
              this.loadAppointments()
            },
            fail: () => {
              const appointments = this.data.appointments.filter(item => item.id !== id)
              this.setData({ appointments })
              wx.showToast({ title: '已取消', icon: 'success' })
            }
          })
        }
      }
    })
  },

  // 修改预约
  confirmAppointment(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/appointment/appointment?id=${id}` })
  },

  // 查看详情
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/appointment-detail/index?id=${id}` })
  },

  // 新建预约
  goAppointment() {
    wx.navigateTo({ url: '/pages/appointment/appointment' })
  },

  // 工具方法
  getStatusText(status) {
    const map = {
      'pending': '待确认',
      'confirmed': '已确认',
      'completed': '已完成',
      'cancelled': '已取消'
    }
    return map[status] || status
  },
  formatDateTime(dateStr) {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    const weekDays = ['日', '一', '二', '三', '四', '五', '六']
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} 周${weekDays[d.getDay()]} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  },
  formatDate(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})