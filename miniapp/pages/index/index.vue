<template>
  <view class="container">
    <!-- Banner区域 -->
    <view class="banner">
      <swiper class="banner-swiper" autoplay circular interval="5000">
        <swiper-item v-for="(item, index) in banners" :key="index">
          <image class="banner-image" :src="item.image" mode="aspectFill" />
        </swiper-item>
      </swiper>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-entry">
      <view class="entry-item" @click="goToCase">
        <view class="entry-icon case-icon">
          <text class="iconfont">&#xe601;</text>
        </view>
        <text class="entry-text">装修案例</text>
      </view>
      <view class="entry-item" @click="goToLead">
        <view class="entry-icon lead-icon">
          <text class="iconfont">&#xe602;</text>
        </view>
        <text class="entry-text">免费咨询</text>
      </view>
      <view class="entry-item" @click="goToAppointment">
        <view class="entry-icon appoint-icon">
          <text class="iconfont">&#xe603;</text>
        </view>
        <text class="entry-text">预约量尺</text>
      </view>
      <view class="entry-item">
        <view class="entry-icon phone-icon">
          <text class="iconfont">&#xe604;</text>
        </view>
        <text class="entry-text">电话咨询</text>
      </view>
    </view>

    <!-- 服务优势 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">服务优势</text>
      </view>
      <view class="advantage-list">
        <view class="advantage-item">
          <text class="advantage-num">58</text>
          <text class="advantage-text">节点服务流程</text>
        </view>
        <view class="advantage-item">
          <text class="advantage-num">100%</text>
          <text class="advantage-text">自有工人</text>
        </view>
        <view class="advantage-item">
          <text class="advantage-num">0</text>
          <text class="advantage-text">增项承诺</text>
        </view>
        <view class="advantage-item">
          <text class="advantage-num">10年</text>
          <text class="advantage-text">质保承诺</text>
        </view>
      </view>
    </view>

    <!-- 精选案例 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">精选案例</text>
        <text class="more" @click="goToCase">查看更多 ></text>
      </view>
      <view class="case-list">
        <view 
          class="case-item" 
          v-for="(item, index) in cases" 
          :key="index"
          @click="goToCaseDetail(item)"
        >
          <image class="case-image" :src="item.cover_image" mode="aspectFill" />
          <view class="case-info">
            <text class="case-title">{{ item.title }}</text>
            <view class="case-tags">
              <text class="tag">{{ item.area }}㎡</text>
              <text class="tag">{{ item.style }}</text>
              <text class="tag">{{ item.house_type }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部联系 -->
    <view class="contact-section">
      <view class="contact-title">D&B 帝标|设记家全案家装</view>
      <view class="contact-desc">原木定制 · 全案服务 · 品质生活</view>
      <button class="contact-btn" @click="goToLead">立即咨询</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      banners: [
        { image: '/static/banner/banner1.jpg', link: '' },
        { image: '/static/banner/banner2.jpg', link: '' }
      ],
      cases: []
    }
  },

  onLoad() {
    this.loadCases()
  },

  methods: {
    // 加载案例
    loadCases() {
      uni.request({
        url: 'http://localhost:5000/api/v3/cases',
        method: 'GET',
        data: { per_page: 4 },
        success: (res) => {
          if (res.data && res.data.items) {
            this.cases = res.data.items
          }
        }
      })
    },

    // 跳转到案例列表
    goToCase() {
      uni.switchTab({
        url: '/pages/case/list'
      })
    },

    // 跳转到案例详情
    goToCaseDetail(item) {
      uni.navigateTo({
        url: `/pages/case/detail?id=${item.id}`
      })
    },

    // 跳转到留资表单
    goToLead() {
      uni.switchTab({
        url: '/pages/lead/form'
      })
    },

    // 跳转到预约
    goToAppointment() {
      uni.navigateTo({
        url: '/pages/appointment/index'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Banner */
.banner {
  height: 400rpx;
}

.banner-swiper {
  height: 100%;
}

.banner-image {
  width: 100%;
  height: 100%;
}

/* 快捷入口 */
.quick-entry {
  display: flex;
  justify-content: space-around;
  padding: 40rpx 20rpx;
  background: #fff;
  margin: -40rpx 20rpx 20rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1;
}

.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.entry-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;

  &.case-icon {
    background: linear-gradient(135deg, #8B4513, #D2691E);
  }

  &.lead-icon {
    background: linear-gradient(135deg, #52c41a, #73d13d);
  }

  &.appoint-icon {
    background: linear-gradient(135deg, #1890ff, #40a9ff);
  }

  &.phone-icon {
    background: linear-gradient(135deg, #fa8c16, #ffa940);
  }
}

.iconfont {
  color: #fff;
  font-size: 48rpx;
}

.entry-text {
  font-size: 26rpx;
  color: #262626;
}

/* 区块 */
.section {
  background: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 16rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #262626;
}

.more {
  font-size: 26rpx;
  color: #8B4513;
}

/* 服务优势 */
.advantage-list {
  display: flex;
  justify-content: space-between;
}

.advantage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.advantage-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #8B4513;
  margin-bottom: 8rpx;
}

.advantage-text {
  font-size: 24rpx;
  color: #595959;
}

/* 案例列表 */
.case-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.case-item {
  border-radius: 12rpx;
  overflow: hidden;
  background: #f5f5f5;
}

.case-image {
  width: 100%;
  height: 240rpx;
}

.case-info {
  padding: 16rpx;
}

.case-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #262626;
  margin-bottom: 12rpx;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.case-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.tag {
  font-size: 22rpx;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

/* 联系区块 */
.contact-section {
  background: linear-gradient(135deg, #8B4513, #5D3A1A);
  margin: 20rpx;
  padding: 60rpx 40rpx;
  border-radius: 16rpx;
  text-align: center;
}

.contact-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16rpx;
}

.contact-desc {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40rpx;
}

.contact-btn {
  background: #fff;
  color: #8B4513;
  font-size: 32rpx;
  font-weight: 600;
  padding: 24rpx 80rpx;
  border-radius: 50rpx;
  border: none;
}
</style>
