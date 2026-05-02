<template>
  <div class="case-detail-v2">
    <!-- 固定导航栏（滚动后显示） -->
    <nav class="fixed-nav" :class="{ visible: showFixedNav }">
      <div class="nav-container">
        <div class="nav-left">
          <button class="back-btn" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <span class="nav-title">{{ caseDetail?.title || '案例详情' }}</span>
        </div>
        <div class="nav-right">
          <button class="nav-icon-btn" @click="handleLike">
            <el-icon><Star :class="{ active: isLiked }" /></el-icon>
          </button>
          <button class="nav-icon-btn" @click="handleShare">
            <el-icon><Share /></el-icon>
          </button>
        </div>
      </div>
    </nav>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-screen">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 案例内容 -->
    <div v-else-if="caseDetail" class="case-content">
      <!-- Hero 全屏区域 -->
      <section class="hero-section">
        <!-- 轮播英雄图 -->
        <div v-if="heroImages.length > 0" class="hero-carousel">
          <transition name="fade" mode="out-in">
            <img :key="currentHeroIndex" :src="heroImages[currentHeroIndex].url" :alt="caseDetail.title">
          </transition>
          <div class="hero-gradient"></div>
          <!-- 轮播指示器 -->
          <div class="carousel-indicators" v-if="heroImages.length > 1">
            <span 
 v-for="(img, idx) in heroImages" 
              :key="idx" 
              class="indicator" 
              :class="{ active: idx === currentHeroIndex }"
              @click="currentHeroIndex = idx"
            ></span>
          </div>
        </div>
        <!-- 单图降级 -->
        <div v-else class="hero-bg">
          <img :src="caseDetail.cover_image || '/placeholder-case.jpg'" :alt="caseDetail.title">
          <div class="hero-gradient"></div>
        </div>
        
        <div class="hero-content">
          <div class="back-float" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
          </div>
          
          <div class="hero-text">
            <div class="case-meta">
              <span v-if="caseDetail.is_featured" class="featured-badge">精选案例</span>
              <span class="location" v-if="caseDetail.location">
                <el-icon><Location /></el-icon>
                {{ caseDetail.location }}
              </span>
            </div>
            
            <h1 class="case-title">{{ caseDetail.title }}</h1>
            
            <p class="case-subtitle" v-if="caseDetail.subtitle || caseDetail.style">
              {{ caseDetail.subtitle || `${caseDetail.style} · ${caseDetail.area}㎡` }}
            </p>
            
            <div class="case-tags">
              <span v-if="caseDetail.style" class="tag">{{ caseDetail.style }}</span>
              <span v-if="caseDetail.house_type" class="tag">{{ caseDetail.house_type }}</span>
              <span v-if="caseDetail.area" class="tag">{{ caseDetail.area }}㎡</span>
              <span v-if="caseDetail.package_type" class="tag highlight">{{ caseDetail.package_type }}</span>
              <span v-if="caseDetail.workflow_progress" class="tag workflow-tag">
                <span class="tag-dot" :class="getProgressClass(caseDetail.workflow_progress)"></span>
                {{ caseDetail.workflow_progress.current_phase || '进行中' }} · {{ caseDetail.workflow_progress.progress_pct }}%
              </span>
            </div>
          </div>
          
          <div class="scroll-hint" @click="scrollToContent">
            <span>向下滑动</span>
            <div class="scroll-arrow">
              <el-icon><ArrowDown /></el-icon>
            </div>
          </div>
        </div>
      </section>

      <!-- 项目概览 -->
      <section class="overview-section" ref="contentRef">
        <div class="container">
          <div class="overview-grid">
            <div class="overview-item">
              <span class="label">户型</span>
              <span class="value">{{ caseDetail.house_type || '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">面积</span>
              <span class="value">{{ caseDetail.area ? caseDetail.area + '㎡' : '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">风格</span>
              <span class="value">{{ caseDetail.style || '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">工期</span>
              <span class="value">{{ caseDetail.duration || '90' }}天</span>
            </div>
            <div class="overview-item highlight" v-if="caseDetail.total_price">
              <span class="label">全案总价</span>
              <span class="value price">¥{{ formatPrice(caseDetail.total_price) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 设计理念 -->
      <section class="concept-section" v-if="caseDetail.design_concept">
        <div class="container">
          <h2 class="section-title">设计理念</h2>
          <p class="concept-text">{{ caseDetail.design_concept }}</p>
        </div>
      </section>

      <!-- 图片画廊 -->
      <section class="gallery-section" v-if="galleryList.length > 0">
        <div class="container">
          <h2 class="section-title">案例图集</h2>

          <!-- 杂志风格：有描述的图片 -->
          <div class="magazine-gallery" v-if="describedImages.length > 0">
            <div
              v-for="(item, index) in describedImages"
              :key="'desc-'+index"
              class="magazine-card"
              :style="{ '--img-color': item.extractedColor || '#8B5A2B' }"
              @click="openImagePreview(findMediaIndex(item))"
            >
              <div class="mag-img-wrapper">
                <img :src="item.url" :alt="item.description" loading="lazy" @load="extractColor($event, item)">
                <div class="mag-overlay">
                  <el-icon><ZoomIn /></el-icon>
                </div>
              </div>
              <div class="mag-caption" v-if="item.description">
                <p class="mag-text" v-html="formatDropCap(item.description)"></p>
              </div>
            </div>
          </div>

          <!-- 瀑布流：无描述的图片 -->
          <div class="gallery-masonry" v-if="plainImages.length > 0">
            <div
              v-for="(media, index) in plainImages"
              :key="'plain-'+index"
              class="gallery-item"
              :class="{ large: index % 5 === 0, wide: index % 5 === 3 }"
              @click="openImagePreview(findMediaIndex(media))"
            >
              <img :src="media.url || media.file_url" :alt="media.description" loading="lazy">
              <div class="item-overlay">
                <el-icon><ZoomIn /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- VR 体验 -->
      <section class="vr-section" v-if="caseDetail.vr_link">
        <div class="container">
          <h2 class="section-title">360° 全景体验</h2>
          <div class="vr-card" @click="openVR">
            <img :src="caseDetail.cover_image" alt="VR预览">
            <div class="vr-overlay">
              <div class="vr-play-btn">
                <el-icon><VideoPlay /></el-icon>
              </div>
              <p>点击体验沉浸式 VR 全景</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 设计亮点 -->
      <section class="highlights-section" v-if="caseDetail.design_highlights">
        <div class="container">
          <h2 class="section-title">设计亮点</h2>
          <div class="highlights-content">
            <p>{{ caseDetail.design_highlights }}</p>
          </div>
        </div>
      </section>

      <!-- 施工进度（真实案例服务流程） -->
      <section class="workflow-progress-section" v-if="workflowProgress">
        <div class="container">
          <h2 class="section-title">施工进度</h2>
          
          <!-- 进度概览 -->
          <div class="progress-overview">
            <div class="progress-bar-wrapper">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: workflowProgress.progress_pct + '%' }"></div>
              </div>
              <span class="progress-percent">{{ workflowProgress.progress_pct }}%</span>
            </div>
            <p class="progress-current">
              当前阶段：<strong>{{ workflowProgress.current_phase || '待启动' }}</strong>
            </p>
          </div>
          
          <!-- 阶段进度条 -->
          <div class="phase-steps">
            <div
              v-for="(phase, idx) in workflowProgress.phases"
              :key="idx"
              class="phase-step"
              :class="phase.status"
            >
              <div class="phase-dot">
                <el-icon v-if="phase.status === 'completed'"><Check /></el-icon>
                <span v-else class="dot-inner"></span>
              </div>
              <div class="phase-line" v-if="idx < workflowProgress.phases.length - 1" :class="phase.status"></div>
              <div class="phase-info">
                <span class="phase-name">{{ phase.name }}</span>
                <span class="phase-detail">{{ phase.completed_nodes }}/{{ phase.total_nodes }}</span>
              </div>
            </div>
          </div>
          
          <!-- 工流时间轴（节点详情） -->
          <div class="workflow-nodes" v-if="workflowTimeline.length">
            <div class="nodes-by-phase" v-for="(nodes, phaseName) in groupedTimeline" :key="phaseName">
              <h4 class="phase-group-title">{{ phaseName }}</h4>
              <div class="node-list">
                <div
                  v-for="node in nodes"
                  :key="node.id"
                  class="workflow-node"
                  :class="node.status"
                >
                  <div class="node-status-dot"></div>
                  <div class="node-content">
                    <div class="node-header">
                      <span class="node-name">{{ node.node_name }}</span>
                      <span class="node-status-text">{{ getStatusText(node.status) }}</span>
                    </div>
                    <div class="node-photos" v-if="node.photos && node.photos.length">
                      <img
                        v-for="(url, idx) in node.photos.slice(0, 4)"
                        :key="idx"
                        :src="url"
                        @click="openImagePreview(0, node.photos)"
                      />
                    </div>
                    <div class="node-renderings" v-if="node.renderings && node.renderings.length">
                      <span class="rendering-label">效果图</span>
                      <img
                        v-for="(url, idx) in node.renderings.slice(0, 4)"
                        :key="idx"
                        :src="url"
                        @click="openImagePreview(0, node.renderings)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 施工时间轴（旧版） -->
      <section class="timeline-section" v-if="!workflowProgress && timelineList.length > 0">
        <div class="container">
          <h2 class="section-title">施工进程</h2>
          <div class="timeline">
            <div
              v-for="(node, index) in timelineList"
              :key="node.id || index"
              class="timeline-item"
              :class="{ active: index === 0 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-date">{{ formatDate(node.node_time) }}</span>
                <h4>{{ node.title }}</h4>
                <p>{{ node.content }}</p>
                <div v-if="node.media_urls" class="timeline-images">
                  <img
                    v-for="(url, idx) in parseMediaUrls(node.media_urls).slice(0, 3)"
                    :key="idx"
                    :src="url"
                    @click="openImagePreview(0, [url])"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 相关产品 -->
      <section class="products-section" v-if="relatedProducts.length > 0">
        <div class="container">
          <h2 class="section-title">使用产品</h2>
          <div class="products-grid">
            <div
              v-for="product in relatedProducts"
              :key="product.id"
              class="product-card"
              @click="goToProduct(product.id)"
            >
              <div class="product-image">
                <img :src="product.main_image || '/placeholder.png'" :alt="product.name">
              </div>
              <div class="product-info">
                <h4>{{ product.name }}</h4>
                <p class="product-brand">{{ product.brand }}</p>
                <span class="product-price">¥{{ product.sale_price }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部 CTA -->
      <section class="cta-section">
        <div class="container">
          <h2>喜欢这套设计？</h2>
          <p>预约设计师，获取专属方案</p>
          <div class="cta-buttons">
            <el-button type="primary" size="large" @click="showLeadForm = true">
              免费咨询
            </el-button>
            <el-button size="large" @click="handleSubscribe">
              <el-icon><Bell /></el-icon>
              {{ isSubscribed ? '已订阅' : '订阅更新' }}
            </el-button>
          </div>
        </div>
      </section>

      <!-- 底部信息 -->
      <footer class="case-footer">
        <div class="container">
          <div class="footer-stats">
            <span><el-icon><View /></el-icon> {{ caseDetail.view_count || 0 }} 浏览</span>
            <span><el-icon><Star /></el-icon> {{ caseDetail.like_count || 0 }} 收藏</span>
            <span><el-icon><Bell /></el-icon> {{ caseDetail.subscription_count || 0 }} 订阅</span>
          </div>
          <p class="copyright">© D&B 帝标|设记家全案服务</p>
        </div>
      </footer>
    </div>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="imagePreview.visible"
      :url-list="imagePreview.list"
      :initial-index="imagePreview.index"
      @close="imagePreview.visible = false"
    />

    <!-- 留资表单弹窗 -->
    <el-dialog
      v-model="showLeadForm"
      title="获取专属方案"
      width="90%"
      max-width="500px"
      class="lead-dialog"
    >
      <LeadForm
        :source-type="'case'"
        :source-id="caseDetail?.id"
        @success="onLeadSuccess"
      />
    </el-dialog>

    <!-- 订阅手机弹窗 -->
    <el-dialog
      v-model="showSubscribeDialog"
      title="订阅案例更新"
      width="90%"
      max-width="400px"
      class="subscribe-dialog"
    >
      <div class="subscribe-content">
        <p class="subscribe-tip">订阅「{{ caseDetail?.atmosphere || '该风格' }}」后，案例更新时将通过微信通知您</p>
        <el-input
          v-model="subscribePhone"
          placeholder="请输入手机号"
          type="tel"
          size="large"
          maxlength="11"
          @keyup.enter="doSubscribe"
        />
        <el-button
          type="primary"
          size="large"
          class="subscribe-btn"
          @click="doSubscribe"
          :disabled="!subscribePhone"
        >
          订阅「{{ caseDetail?.atmosphere || '该风格' }}」案例更新
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, ArrowDown, Location, Star, Share,
  View, Bell, VideoPlay, ZoomIn, Check
} from '@element-plus/icons-vue'
import request from '@/api/request'
import LeadForm from '@/components/LeadForm.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const caseDetail = ref(null)
const isLiked = ref(false)
const isSubscribed = ref(false)
const showLeadForm = ref(false)
const showSubscribeDialog = ref(false)
const subscribePhone = ref('')
const showFixedNav = ref(false)
const contentRef = ref(null)
const currentHeroIndex = ref(0)
let heroCarouselTimer = null

// 图片预览
const imagePreview = ref({
  visible: false,
  list: [],
  index: 0
})

// 媒体列表 - 分离有描述和无描述的图片
const heroImages = computed(() => {
  const list = []
  if (caseDetail.value?.hero_images) {
    list.push(...caseDetail.value.hero_images.map(url => ({ url })))
  }
  return list
})

const galleryList = computed(() => {
  const list = []
  // 来自 case_media 表（含 description）
  if (caseDetail.value?.media) {
    list.push(...caseDetail.value.media.map(m => ({
      url: m.url,
      description: m.description || '',
      id: m.id
    })))
  }
  // 来自 gallery 字段
  if (caseDetail.value?.gallery) {
    caseDetail.value.gallery.forEach((url, i) => {
      // 避免与 media 重复
      if (!list.find(item => item.url === url)) {
        list.push({ url, description: '' })
      }
    })
  }
  return list
})

// 有描述的图片（杂志风格展示）
const describedImages = computed(() => {
  return galleryList.value.filter(m => m.description && m.description.trim())
})

// 无描述的图片（普通瀑布流）
const plainImages = computed(() => {
  return galleryList.value.filter(m => !m.description || !m.description.trim())
})

// 合并后的完整媒体列表（用于预览）
const mediaList = computed(() => {
  return [...heroImages.value, ...galleryList.value]
})

// 时间轴列表
const timelineList = computed(() => {
  return caseDetail.value?.timeline_nodes || []
})

// 工作流进度（真实案例）
const workflowProgress = computed(() => {
  return caseDetail.value?.workflow_progress || null
})

// 工作流时间轴节点
const workflowTimeline = computed(() => {
  return caseDetail.value?.workflow_timeline || []
})

// 按阶段分组的时间轴节点
const groupedTimeline = computed(() => {
  const groups = {}
  for (const node of workflowTimeline.value) {
    const phase = node.phase || '其他'
    if (!groups[phase]) groups[phase] = []
    groups[phase].push(node)
  }
  return groups
})

// 首字扩大3倍，杂志风格排版
const formatDropCap = (text) => {
  if (!text || text.length < 2) return text
  const firstChar = text.charAt(0)
  const rest = text.slice(1)
  return `<span class="drop-cap">${firstChar}</span>${rest}`
}

// 从图片提取主色（底色）
const extractColor = (event, item) => {
  const img = event.target
  if (!img) return
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  canvas.width = 50
  canvas.height = 50
  ctx.drawImage(img, 0, 0, 50, 50)
  try {
    const data = ctx.getImageData(25, 25, 1, 1).data
    const r = data[0], g = data[1], b = data[2]
    item.extractedColor = `rgb(${r},${g},${b})`
  } catch (e) {
    item.extractedColor = '#8B5A2B'
  }
}

// 在mediaList中查找图片索引
const findMediaIndex = (item) => {
  return galleryList.value.findIndex(m => m.url === item.url)
}

// 获取状态文本
const getStatusText = (status) => {
  const map = { pending: '待开始', ongoing: '进行中', completed: '已完成' }
  return map[status] || status
}

// 进度CSS类名
const getProgressClass = (wp) => {
  if (!wp) return ''
  if (wp.progress_pct >= 100) return 'completed'
  if (wp.progress_pct > 0) return 'ongoing'
  return 'pending'
}

// 相关产品
const relatedProducts = computed(() => {
  return caseDetail.value?.related_products || []
})

// 加载案例详情
const loadCaseDetail = async () => {
  loading.value = true
  try {
    const res = await request.get(`/public/cases/${route.params.id}`)
    caseDetail.value = res
    document.title = `${res.title} - D&B 帝标|设记家案例`
    checkSubscription()
  } catch (error) {
    ElMessage.error('加载案例详情失败')
  } finally {
    loading.value = false
  }
}

// 检查订阅状态
const checkSubscription = async () => {
  try {
    const res = await request.get(`/public/cases/${route.params.id}/subscription-status`)
    isSubscribed.value = res?.is_subscribed || false
  } catch (e) {
    // 未登录时忽略错误
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 滚动到内容区
const scrollToContent = () => {
  contentRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// 处理滚动事件
const handleScroll = () => {
  const scrollY = window.scrollY
  showFixedNav.value = scrollY > window.innerHeight * 0.6
}

// 点赞
const handleLike = async () => {
  try {
    await request.post(`/cases/${caseDetail.value.id}/like`)
    isLiked.value = !isLiked.value
    caseDetail.value.like_count += isLiked.value ? 1 : -1
    ElMessage.success(isLiked.value ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 分享
const handleShare = () => {
  const shareData = {
    title: caseDetail.value.title,
    desc: caseDetail.value.design_concept?.slice(0, 50) + '...',
    link: window.location.href,
    imgUrl: caseDetail.value.cover_image
  }
  
  // 复制链接
  navigator.clipboard.writeText(window.location.href).then(() => {
    ElMessage.success('链接已复制，快去分享吧！')
  })
}

// 订阅
const handleSubscribe = async () => {
  if (!subscribePhone.value) {
    showSubscribeDialog.value = true
    return
  }
  // 输入手机号后直接订阅
  await doSubscribe()
}

const doSubscribe = async () => {
  try {
    const caseId = caseDetail.value.id
    if (isSubscribed.value) {
      await request.delete(`/cases/${caseId}/subscribe`)
      isSubscribed.value = false
      ElMessage.success('已取消订阅')
    } else {
      await request.post(`/cases/${caseId}/subscribe`, { phone: subscribePhone.value })
      isSubscribed.value = true
      ElMessage.success('订阅成功，案例更新将通过微信通知您')
    }
    showSubscribeDialog.value = false
    subscribePhone.value = ''
  } catch (error) {
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 打开图片预览
const openImagePreview = (index, list = null) => {
  imagePreview.value.list = list || mediaList.value.map(m => m.url || m.file_url)
  imagePreview.value.index = index
  imagePreview.value.visible = true
}

// 打开 VR
const openVR = () => {
  if (caseDetail.value?.vr_link) {
    window.open(caseDetail.value.vr_link, '_blank')
  }
}

// 跳转到产品
const goToProduct = (id) => {
  router.push(`/products/${id}`)
}

// 留资成功
const onLeadSuccess = () => {
  showLeadForm.value = false
  ElMessage.success('提交成功，我们将尽快联系您')
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0'
  return parseFloat(price).toLocaleString('zh-CN')
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 解析媒体URL
const parseMediaUrls = (urls) => {
  if (!urls) return []
  if (typeof urls === 'string') {
    try {
      return JSON.parse(urls)
    } catch {
      return urls.split(',').map(u => u.trim())
    }
  }
  return urls
}

onMounted(() => {
  loadCaseDetail()
  window.addEventListener('scroll', handleScroll)
  // 英雄图轮播
  if (heroImages.value.length > 1) {
    heroCarouselTimer = setInterval(() => {
      currentHeroIndex.value = (currentHeroIndex.value + 1) % heroImages.value.length
    }, 3000)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (heroCarouselTimer) clearInterval(heroCarouselTimer)
})
</script>

<style scoped>
.case-detail-v2 {
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
}

/* 固定导航栏 */
.fixed-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(20px);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}

.fixed-nav.visible {
  transform: translateY(0);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn,
.nav-icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.back-btn:hover,
.nav-icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-title {
  font-size: 16px;
  font-weight: 500;
}

.nav-right {
  display: flex;
  gap: 12px;
}

.nav-icon-btn .active {
  color: #ffd700;
}

/* Hero 全屏区域 */
.hero-section {
  position: relative;
  height: 100vh;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}



.hero-carousel {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-carousel img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-indicators {
  position: absolute;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.carousel-indicators .indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  cursor: pointer;
  transition: all 0.3s;
}

.carousel-indicators .indicator.active {
  background: #fff;
  width: 24px;
  border-radius: 4px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(10, 10, 10, 1) 0%,
    rgba(10, 10, 10, 0.7) 40%,
    rgba(10, 10, 10, 0.3) 70%,
    rgba(10, 10, 10, 0.1) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: 60px 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.back-float {
  position: absolute;
  top: 40px;
  left: 20px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 20px;
}

.back-float:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.hero-text {
  margin-bottom: 40px;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.featured-badge {
  padding: 6px 16px;
  background: linear-gradient(135deg, #8B5A2B 0%, #a67c52 100%);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.case-title {
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.case-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 24px;
  font-weight: 300;
}

.case-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.tag.highlight {
  background: rgba(139, 90, 43, 0.3);
  border-color: rgba(139, 90, 43, 0.5);
  color: #d4a574;
}

.tag.workflow-tag {
  background: rgba(230, 162, 60, 0.15);
  border-color: rgba(230, 162, 60, 0.3);
  color: #E6A23C;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.tag-dot.completed { background: #67C23A; }
.tag-dot.ongoing { background: #E6A23C; animation: pulse-dot 2s infinite; }
.tag-dot.pending { background: #999; }

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.scroll-arrow {
  font-size: 20px;
}

/* 项目概览 */
.overview-section {
  padding: 60px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 30px;
}

.overview-item {
  text-align: center;
}

.overview-item .label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.overview-item .value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #fff;
}

.overview-item .value.price {
  color: #d4a574;
  font-size: 28px;
}

/* 设计理念 */
.concept-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 600;
  margin: 0 0 30px;
  text-align: center;
}

.concept-text {
  font-size: 18px;
  line-height: 2;
  color: rgba(255, 255, 255, 0.8);
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  font-weight: 300;
}

/* 图片画廊 */
.gallery-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.gallery-masonry {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.gallery-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
}

.gallery-item.large {
  grid-column: span 2;
  grid-row: span 2;
}

.gallery-item.wide {
  grid-column: span 2;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

.item-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .item-overlay {
  opacity: 1;
}

.item-overlay .el-icon {
  font-size: 32px;
  color: #fff;
}

/* VR 区域 */
.vr-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.vr-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 21/9;
}

.vr-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.vr-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  transition: background 0.3s;
}

.vr-card:hover .vr-overlay {
  background: rgba(0, 0, 0, 0.4);
}

.vr-play-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #8B5A2B;
  transition: transform 0.3s;
}

.vr-card:hover .vr-play-btn {
  transform: scale(1.1);
}

.vr-overlay p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

/* 设计亮点 */
.highlights-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.highlights-content {
  max-width: 800px;
  margin: 0 auto;
}

.highlights-content p {
  font-size: 16px;
  line-height: 2;
  color: rgba(255, 255, 255, 0.8);
}

/* 时间轴 */
.timeline-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 施工进度（真实案例工作流） */
.workflow-progress-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-overview {
  max-width: 600px;
  margin: 0 auto 40px;
  text-align: center;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8B5A2B, #d4a574);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.progress-percent {
  font-size: 24px;
  font-weight: 700;
  color: #d4a574;
  min-width: 60px;
}

.progress-current {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.progress-current strong {
  color: #fff;
}

/* 阶段进度条 */
.phase-steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  margin-bottom: 60px;
  padding: 0 20px;
  overflow-x: auto;
}

.phase-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 100px;
  max-width: 180px;
}

.phase-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  z-index: 1;
  background: rgba(255, 255, 255, 0.1);
  color: #999;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.phase-step.completed .phase-dot {
  background: #8B5A2B;
  border-color: #8B5A2B;
  color: #fff;
}

.phase-step.ongoing .phase-dot {
  background: transparent;
  border-color: #E6A23C;
  color: #E6A23C;
}

.phase-step.ongoing .dot-inner {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #E6A23C;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.phase-line {
  position: absolute;
  top: 18px;
  left: calc(50% + 18px);
  right: calc(-50% + 18px);
  height: 2px;
  background: rgba(255, 255, 255, 0.15);
}

.phase-line.completed {
  background: #8B5A2B;
}

.phase-info {
  margin-top: 12px;
  text-align: center;
}

.phase-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.phase-detail {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 工作流节点详情 */
.workflow-nodes {
  max-width: 800px;
  margin: 0 auto;
}

.phase-group-title {
  font-size: 18px;
  font-weight: 600;
  color: #d4a574;
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(139, 90, 43, 0.3);
}

.workflow-node {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  position: relative;
}

.workflow-node:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 36px;
  bottom: -16px;
  width: 2px;
  background: rgba(255, 255, 255, 0.08);
}

.node-status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.workflow-node.pending .node-status-dot {
  background: rgba(255, 255, 255, 0.2);
}

.workflow-node.ongoing .node-status-dot {
  background: #E6A23C;
  box-shadow: 0 0 0 4px rgba(230, 162, 60, 0.2);
}

.workflow-node.completed .node-status-dot {
  background: #67C23A;
}

.node-content {
  flex: 1;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.node-name {
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.node-status-text {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.workflow-node.pending .node-status-text {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.4);
}

.workflow-node.ongoing .node-status-text {
  background: rgba(230, 162, 60, 0.15);
  color: #E6A23C;
}

.workflow-node.completed .node-status-text {
  background: rgba(103, 194, 58, 0.15);
  color: #67C23A;
}

.node-photos,
.node-renderings {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.node-photos img,
.node-renderings img {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
}

.node-photos img:hover,
.node-renderings img:hover {
  transform: scale(1.08);
}

.rendering-label {
  display: none;
}

.timeline {
  max-width: 800px;
  margin: 0 auto;
}

.timeline-item {
  display: flex;
  gap: 24px;
  padding: 24px 0;
  position: relative;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 48px;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  margin-top: 6px;
}

.timeline-item.active .timeline-dot {
  background: #8B5A2B;
  box-shadow: 0 0 0 4px rgba(139, 90, 43, 0.3);
}

.timeline-content {
  flex: 1;
}

.timeline-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.timeline-content h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 8px 0;
}

.timeline-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin: 0;
}

.timeline-images {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.timeline-images img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
}

/* 相关产品 */
.products-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.product-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, background 0.3s;
}

.product-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
}

.product-image {
  aspect-ratio: 1;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-info {
  padding: 16px;
}

.product-info h4 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-brand {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 8px;
}

.product-price {
  font-size: 16px;
  font-weight: 600;
  color: #d4a574;
}

/* CTA 区域 */
.cta-section {
  padding: 100px 0;
  text-align: center;
  background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
}

.cta-section h2 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 12px;
}

.cta-section p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 32px;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.cta-buttons .el-button--primary {
  background: #8B5A2B;
  border-color: #8B5A2B;
  padding: 16px 40px;
  font-size: 16px;
}

.cta-buttons .el-button--primary:hover {
  background: #a67c52;
  border-color: #a67c52;
}

/* 底部 */
.case-footer {
  padding: 40px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-stats span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

/* 加载状态 */
.loading-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* 响应式 */
@media (max-width: 768px) {
  .gallery-masonry {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .gallery-item.large,
  .gallery-item.wide {
    grid-column: span 2;
    grid-row: span 1;
  }
  
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hero-content {
    padding: 40px 16px 30px;
  }
  
  .case-title {
    font-size: 28px;
  }
  
  .back-float {
    top: 20px;
    left: 16px;
    width: 40px;
    height: 40px;
  }
}

/* 订阅弹窗 */
.subscribe-content {
  padding: 20px 10px;
}

.subscribe-tip {
  margin-bottom: 20px;
  color: #666;
  text-align: center;
}

.subscribe-btn {
  width: 100%;
  margin-top: 20px;
}

/* 杂志风格画廊 */
.magazine-gallery {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.magazine-card {
  background: var(--img-color, #8B5A2B);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.magazine-card:hover {
  transform: translateY(-4px);
}

.mag-img-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.mag-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.magazine-card:hover .mag-overlay {
  opacity: 1;
}

.mag-overlay .el-icon {
  font-size: 32px;
  color: #fff;
}

.mag-caption {
  padding: 12px;
  background: var(--img-color, #8B5A2B);
  color: #fff;
  font-size: 14px;
  line-height: 1.6;
}

.mag-text {
  margin: 0;
}

.mag-text :deep(.drop-cap) {
  float: left;
  font-size: 3em;
  line-height: 1;
  margin-right: 0.1em;
  color: #fff;
}
</style>
