const app = getApp()

Page({
  data: {
    caseKeyword: '',
    caseList: [],
    selectedCase: null,
    workflowPhases: [],
    selectedNode: null,
    photos: [],
    video: '',
    report: '',
    files: [],
    submitting: false
  },

  onLoad(options) {
    // 如果从案例详情跳转，直接选中案例
    if (options.caseId) {
      this.loadCase(options.caseId)
    } else {
      this.loadCases()
    }
  },

  // 加载案例列表
  loadCases(keyword = '') {
    app.request({
      url: '/admin/cases',
      data: { keyword, status: 'ongoing' },
      success: (res) => {
        if (res && res.list) {
          this.setData({ 
            caseList: res.list.map(c => ({
              ...c,
              cover: app.resolveImageUrl(c.cover_image)
            }))
          })
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  onSearchCase(e) {
    this.setData({ caseKeyword: e.detail.value })
    this.loadCases(e.detail.value)
  },

  // 选择案例
  selectCase(e) {
    const item = e.currentTarget.dataset.item
    this.setData({ selectedCase: item })
    this.loadWorkflowPhases(item.id)
  },

  // 加载工作流阶段
  loadWorkflowPhases(caseId) {
    app.request({
      url: `/admin/cases/${caseId}/workflow`,
      success: (res) => {
        if (res && res.phases) {
          this.setData({ workflowPhases: res.phases })
        }
      }
    })
  },

  // 选择节点
  selectNode(e) {
    const node = e.currentTarget.dataset.node
    this.setData({ selectedNode: node })
  },

  // 拍照
  takePhoto() {
    wx.chooseImage({
      count: 9 - this.data.photos.length,
      sizeType: ['compressed'],
      sourceType: ['camera'],
      success: (res) => {
        this.setData({ photos: [...this.data.photos, ...res.tempFilePaths] })
      }
    })
  },

  // 从相册选择
  chooseImage() {
    wx.chooseImage({
      count: 9 - this.data.photos.length,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        this.setData({ photos: [...this.data.photos, ...res.tempFilePaths] })
      }
    })
  },

  removePhoto(e) {
    const index = e.currentTarget.dataset.index
    const photos = this.data.photos.filter((_, i) => i !== index)
    this.setData({ photos })
  },

  // 拍摄视频
  takeVideo() {
    wx.chooseVideo({
      sourceType: ['camera'],
      maxDuration: 60,
      success: (res) => {
        this.setData({ video: res.tempFilePath })
      }
    })
  },

  removeVideo() {
    this.setData({ video: '' })
  },

  onReportInput(e) {
    this.setData({ report: e.detail.value })
  },

  // 选择文件
  chooseFile() {
    wx.chooseMessageFile({
      count: 5,
      type: 'all',
      success: (res) => {
        const files = res.tempFiles.map(f => ({ name: f.name, path: f.path, size: f.size }))
        this.setData({ files: [...this.data.files, ...files] })
      }
    })
  },

  // 从微信聊天选择文件
  chooseWechatFile() {
    wx.chooseMessageFile({
      count: 5,
      type: 'all',
      success: (res) => {
        const files = res.tempFiles.map(f => ({ name: f.name, path: f.path, size: f.size }))
        this.setData({ files: [...this.data.files, ...files] })
      }
    })
  },

  removeFile(e) {
    const index = e.currentTarget.dataset.index
    const files = this.data.files.filter((_, i) => i !== index)
    this.setData({ files })
  },

  // 提交填报
  async submitReport() {
    const { selectedCase, selectedNode, photos, video, report, files } = this.data
    
    if (!selectedNode) {
      wx.showToast({ title: '请选择节点', icon: 'none' })
      return
    }
    if (photos.length === 0 && !video && !report) {
      wx.showToast({ title: '请至少填写一项内容', icon: 'none' })
      return
    }

    this.setData({ submitting: true })
    wx.showLoading({ title: '提交中...' })

    try {
      // 上传文件
      const uploadedPhotos = []
      for (const p of photos) {
        const url = await this.uploadFile(p, 'photo')
        uploadedPhotos.push(url)
      }

      let uploadedVideo = ''
      if (video) {
        uploadedVideo = await this.uploadFile(video, 'video')
      }

      const uploadedFiles = []
      for (const f of files) {
        const url = await this.uploadFile(f.path, 'file')
        uploadedFiles.push({ name: f.name, url })
      }

      // 提交填报
      app.request({
        url: `/admin/cases/${selectedCase.id}/nodes/${selectedNode.id}/report`,
        method: 'POST',
        data: {
          photos: uploadedPhotos,
          video: uploadedVideo,
          report,
          files: uploadedFiles
        },
        success: (res) => {
          wx.hideLoading()
          wx.showToast({ title: '提交成功', icon: 'success' })
          setTimeout(() => wx.navigateBack(), 1500)
        },
        fail: () => {
          wx.hideLoading()
          wx.showToast({ title: '提交失败', icon: 'none' })
        }
      })
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '上传失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  // 上传文件
  uploadFile(filePath, type) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: app.globalData.apiBaseUrl + '/admin/upload',
        filePath,
        name: 'file',
        formData: { type },
        header: { 'Authorization': 'Bearer ' + wx.getStorageSync('adminToken') },
        success: (res) => {
          const data = JSON.parse(res.data)
          if (data.code === 200) {
            resolve(data.data.url)
          } else {
            reject(new Error(data.message))
          }
        },
        fail: reject
      })
    })
  },

  // 保存草稿
  saveDraft() {
    const { selectedCase, selectedNode, photos, video, report, files } = this.data
    const draft = { selectedCase, selectedNode, photos, video, report, files, savedAt: Date.now() }
    wx.setStorageSync('nodeReportDraft', draft)
    wx.showToast({ title: '已保存', icon: 'success' })
  }
})
