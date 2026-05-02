const app = getApp();

Page({
  data: {
    // 搜索
    searchKeyword: '',
    
    // 筛选
    currentStyle: '全部',
    currentBudget: '全部',
    styleFilters: ['全部', '现代简约', '北欧', '轻奢', '新中式', '日式', '美式'],
    budgetFilters: ['全部', '10万以下', '10-15万', '15-20万', '20-30万', '30万以上'],
    
    // 案例数据
    cases: [
      {
        id: 1,
        title: '龙湖天街·现代轻奢',
        cover: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600',
        style: '轻奢',
        spaceType: '三室两厅',
        area: 128,
        budget: '18-25万',
        isFeatured: true,
        viewCount: 2340,
        likes: 186
      },
      {
        id: 2,
        title: '万科城·北欧简约',
        cover: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600',
        style: '北欧',
        spaceType: '两室一厅',
        area: 95,
        budget: '12-16万',
        isFeatured: false,
        viewCount: 1856,
        likes: 142
      },
      {
        id: 3,
        title: '保利心语·新中式',
        cover: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600',
        style: '新中式',
        spaceType: '四室两厅',
        area: 145,
        budget: '22-30万',
        isFeatured: true,
        viewCount: 3102,
        likes: 267
      },
      {
        id: 4,
        title: '中海国际·现代简约',
        cover: 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=600',
        style: '现代简约',
        spaceType: '三室一厅',
        area: 110,
        budget: '15-20万',
        isFeatured: false,
        viewCount: 1523,
        likes: 98
      },
      {
        id: 5,
        title: '金地天境·日式原木',
        cover: 'https://images.unsplash.com/photo-1600573472592-401b489a3cdc?w=600',
        style: '日式',
        spaceType: '两室两厅',
        area: 88,
        budget: '10-14万',
        isFeatured: false,
        viewCount: 987,
        likes: 76
      },
      {
        id: 6,
        title: '融创壹号·美式田园',
        cover: 'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=600',
        style: '美式',
        spaceType: '别墅',
        area: 260,
        budget: '45-60万',
        isFeatured: true,
        viewCount: 4521,
        likes: 389
      }
    ],
    
    // 分页
    hasMore: true,
    page: 1
  },

  onLoad() {
    this.loadCases();
  },

  // 加载案例
  loadCases() {
    // 这里应该调用API
    // app.request({
    //   url: '/cases',
    //   data: { page: this.data.page, style: this.data.currentStyle, budget: this.data.currentBudget },
    //   success: (res) => {
    //     this.setData({ cases: res.data });
    //   }
    // });
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
    // 防抖搜索
    clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => {
      this.filterCases();
    }, 500);
  },

  // 清除搜索
  clearSearch() {
    this.setData({ searchKeyword: '' });
    this.filterCases();
  },

  // 风格筛选
  onStyleFilter(e) {
    const style = e.currentTarget.dataset.style;
    this.setData({ currentStyle: style });
    this.filterCases();
  },

  // 预算筛选
  onBudgetFilter(e) {
    const budget = e.currentTarget.dataset.budget;
    this.setData({ currentBudget: budget });
    this.filterCases();
  },

  // 筛选案例
  filterCases() {
    // 实际应该调用API筛选
    wx.showLoading({ title: '加载中' });
    setTimeout(() => {
      wx.hideLoading();
    }, 500);
  },

  // 跳转到详情
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/case-detail/case-detail?id=${id}`
    });
  },

  // 留资按钮
  onLeadTap(e) {
    e.stopPropagation();
    const caseItem = e.currentTarget.dataset.case;
    
    app.showLeadPopup({
      source: '案例列表',
      sourceId: caseItem.id,
      title: `获取「${caseItem.title}」同款方案`
    });
  },

  // 跳转到留资
  goToLead() {
    wx.navigateTo({
      url: '/pages/lead/lead?source=案例页底部'
    });
  },

  // 加载更多
  loadMore() {
    this.setData({ page: this.data.page + 1 });
    // 加载更多数据
  },

  // 分享
  onShareAppMessage() {
    return {
      title: 'D&B 帝标|设记家精选装修案例，找到您家的灵感',
      path: '/pages/cases/cases'
    };
  }
});