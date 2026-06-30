<template>
  <div class="case-detail-page">
    <!-- 统一导航栏 -->
    <Navbar />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 案例内容 -->
    <div v-else-if="caseDetail" class="case-content">
      <!-- Hero 区域 - 大图 -->
      <div class="hero-section">
        <div class="hero-image">
          <img :src="caseDetail.cover_image || '/placeholder-case.jpg'" :alt="caseDetail.title">
          <div class="hero-overlay"></div>
        </div>
        <div class="hero-content">
          <div class="container">
            <div class="case-badges">
              <span v-if="caseDetail.is_featured" class="badge featured">精选案例</span>
              <span v-if="caseDetail.construction_phase" class="badge">{{ caseDetail.construction_phase }}</span>
            </div>
            <h1 class="case-title">{{ caseDetail.title }}</h1>
            <p class="case-location" v-if="caseDetail.location">
              <el-icon><Location /></el-icon>
              {{ caseDetail.location }}
              <span v-if="caseDetail.area">· {{ caseDetail.area }}㎡</span>
            </p>
            <div class="case-tags">
              <span v-if="caseDetail.style" class="tag">{{ caseDetail.style }}</span>
              <span v-if="caseDetail.house_type" class="tag">{{ caseDetail.house_type }}</span>
              <span v-if="caseDetail.package_type" class="tag package">{{ caseDetail.package_type }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="container">
          <div class="action-left">
            <el-button :type="isSubscribed ? 'success' : 'default'" @click="handleSubscribe">
              <el-icon><Bell /></el-icon>
              {{ isSubscribed ? '已订阅' : '订阅案例' }}
            </el-button>
            <el-button @click="handleLike" :loading="liking">
              <el-icon><Star /></el-icon>
              {{ caseDetail.like_count || 0 }}
            </el-button>
            <el-button @click="handleShare">
              <el-icon><Share /></el-icon>
              分享
            </el-button>
          </div>
          <div class="action-right">
            <div class="stats">
              <span><el-icon><View /></el-icon>{{ caseDetail.view_count || 0 }} 浏览</span>
              <span><el-icon><Bell /></el-icon>{{ caseDetail.subscription_count || 0 }} 订阅</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="main-section">
        <div class="container">
          <div class="content-grid">
            <!-- 左侧内容 -->
            <div class="content-left">
              <!-- 图片画廊 -->
              <div class="gallery-section" v-if="mediaList.length > 0">
                <h3 class="section-title">案例图集</h3>
                <div class="gallery-grid">
                  <div
                    v-for="(media, index) in mediaList"
                    :key="index"
                    class="gallery-item"
                    :class="{ large: index === 0 }"
                    @click="openImagePreview(index)"
                  >
                    <img :src="media.url || media.file_url" :alt="media.description">
                  </div>
                </div>
              </div>

              <!-- VR 链接 -->
              <div class="vr-section" v-if="caseDetail.vr_link">
                <h3 class="section-title">360° 全景</h3>
                <div class="vr-card" @click="openVR">
                  <div class="vr-preview">
                    <img :src="caseDetail.cover_image" alt="VR预览">
                    <div class="vr-play">
                      <el-icon><VideoPlay /></el-icon>
                      <span>点击体验 VR 全景</span>
                    </div>
                  </div>
                </div>
              </div>

              
              <!-- 时间轴 -->
              <div class="timeline-section" v-if="timelineList.length > 0">
                <h3 class="section-title">施工进度</h3>
                <el-timeline>
                  <el-timeline-item
                    v-for="(node, index) in timelineList"
                    :key="node.id || index"
                    :timestamp="formatDate(node.node_time)"
                    placement="top"
                  >
                    <h4>{{ node.title }}</h4>
                    <p>{{ node.content }}</p>
                    <div v-if="node.media_urls" class="timeline-media">
                      <img
                        v-for="(url, idx) in parseMediaUrls(node.media_urls)"
                        :key="idx"
                        :src="url"
                        @click="openImagePreview(0, [url])"
                      />
                    </div>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </div>

            <!-- 右侧边栏 -->
            <div class="content-right">
              <!-- 报价信息 -->
              <div class="sidebar-card price-card" v-if="caseDetail.total_price">
                <div class="price-header">
                  <span class="price-label">全案总价</span>
                  <span class="price-value">¥{{ formatPrice(caseDetail.total_price) }}</span>
                </div>
                <div class="price-detail" v-if="priceDetailList.length > 0">
                  <div v-for="(item, index) in priceDetailList" :key="index" class="price-item">
                    <span>{{ item.item }}</span>
                    <span>¥{{ formatPrice(item.amount) }}</span>
                  </div>
                </div>
                <el-button type="primary" size="large" style="width: 100%; margin-top: 16px;" @click="showLeadForm = true">
                  获取详细报价
                </el-button>
              </div>

              <!-- 案例信息 -->
              <div class="sidebar-card info-card">
                <h4>案例信息</h4>
                <div class="info-list">
                  <div class="info-item">
                    <span class="label">户型</span>
                    <span class="value">{{ caseDetail.house_type || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">面积</span>
                    <span class="value">{{ caseDetail.area ? caseDetail.area + '㎡' : '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">风格</span>
                    <span class="value">{{ caseDetail.style || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">套餐</span>
                    <span class="value">{{ caseDetail.package_type || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">施工阶段</span>
                    <span class="value">{{ caseDetail.construction_phase || '-' }}</span>
                  </div>
                </div>
              </div>

              <!-- 文件下载 -->
              <div class="sidebar-card files-card" v-if="fileList.length > 0">
                <h4>相关资料</h4>
                <div class="file-list">
                  <div v-for="file in fileList" :key="file.id" class="file-item" @click="downloadFile(file)">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file.file_name }}</span>
                    <el-icon class="download-icon"><Download /></el-icon>
                  </div>
                </div>
              </div>

              <!-- 留资入口 -->
              <div class="sidebar-card lead-card">
                <h4>喜欢这个案例？</h4>
                <p>留下联系方式，获取同款设计方案</p>
                <el-button type="primary" style="width: 100%;" @click="showLeadForm = true">
                  立即咨询
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 404 -->
    <div v-else class="not-found">
      <el-empty description="案例不存在或已下架">
        <el-button type="primary" @click="$router.push('/cases')">返回案例列表</el-button>
      </el-empty>
    </div>

    <!-- 统一页脚 -->
    <Footer />

    <!-- 留资弹窗 -->
    <el-dialog v-model="showLeadForm" title="获取设计方案" width="500px">
      <div class="lead-form-content">
        <p class="lead-desc">填写以下信息，我们的设计师将为您提供同款案例的详细设计方案</p>
        <el-form :model="leadForm" label-position="top">
          <el-form-item label="您的称呼" required>
            <el-input v-model="leadForm.name" placeholder="如：王先生" />
          </el-form-item>
          <el-form-item label="联系电话" required>
            <el-input v-model="leadForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="房屋面积">
            <el-input v-model="leadForm.area" placeholder="如：120">
              <template #append>㎡</template>
            </el-input>
          </el-form-item>
          <el-form-item label="需求描述">
            <el-input v-model="leadForm.message" type="textarea" :rows="3" placeholder="请描述您的装修需求..." />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showLeadForm = false">取消</el-button>
        <el-button type="primary" @click="submitLead" :loading="submittingLead">提交</el-button>
      </template>
    </el-dialog>

    <!-- 订阅弹窗 -->
    <el-dialog v-model="showSubscribeForm" title="订阅案例" width="400px">
      <p>订阅后，案例更新时将通过微信通知您</p>
      <el-form :model="subscribeForm" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="subscribeForm.phone" placeholder="请输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubscribeForm = false">取消</el-button>
        <el-button type="primary" @click="submitSubscribe" :loading="submittingSubscribe">确认订阅</el-button>
      </template>
    </el-dialog>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="imagePreviewVisible"
      :url-list="previewImageList"
      :initial-index="previewIndex"
      @close="imagePreviewVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Bell, Star, Share, View, VideoPlay, Document, Download } from '@element-plus/icons-vue'
import { getPublicCase, likeCase, subscribeCase, createCaseLead, getTimeline, getFiles } from '@/api/case'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const router = useRouter()

const caseId = computed(() => parseInt(route.params.id))
const loading = ref(false)
const caseDetail = ref(null)
const liking = ref(false)
const isSubscribed = ref(false)

// 媒体和时间轴
const mediaList = ref([])
const timelineList = ref([])
const fileList = ref([])

// 留资弹窗
const showLeadForm = ref(false)
const submittingLead = ref(false)
const leadForm = reactive({
  name: '',
  phone: '',
  area: '',
  message: ''
})

// 订阅弹窗
const showSubscribeForm = ref(false)
const submittingSubscribe = ref(false)
const subscribeForm = reactive({
  phone: ''
})

// 图片预览
const imagePreviewVisible = ref(false)
const previewIndex = ref(0)
const previewImageList = ref([])

// 解析造价明细
const priceDetailList = computed(() => {
  if (!caseDetail.value?.price_detail) return []
  try {
    return JSON.parse(caseDetail.value.price_detail)
  } catch {
    return []
  }
})

// 获取案例详情
const fetchCaseDetail = async () => {
  loading.value = true
  try {
    const res = await getPublicCase(caseId.value)
    caseDetail.value = res.data
    
    // 解析媒体列表
    if (res.data?.media) {
      mediaList.value = res.data.media
    }
    
    // 获取时间轴
    fetchTimeline()
    
    // 获取文件
    fetchFiles()
  } catch (error) {
    console.error('获取案例详情失败:', error)
    caseDetail.value = null
  } finally {
    loading.value = false
  }
}

// 获取时间轴
const fetchTimeline = async () => {
  try {
    const res = await getTimeline(caseId.value)
    timelineList.value = res.data || []
  } catch (error) {
    console.error('获取时间轴失败:', error)
  }
}

// 获取文件
const fetchFiles = async () => {
  try {
    const res = await getFiles(caseId.value)
    fileList.value = res.data || []
  } catch (error) {
    console.error('获取文件失败:', error)
  }
}

// 点赞
const handleLike = async () => {
  liking.value = true
  try {
    await likeCase(caseId.value)
    caseDetail.value.like_count = (caseDetail.value.like_count || 0) + 1
    ElMessage.success('点赞成功！')
  } catch (error) {
    console.error('点赞失败:', error)
  } finally {
    liking.value = false
  }
}

// 订阅
const handleSubscribe = () => {
  if (isSubscribed.value) {
    ElMessage.info('您已订阅该案例')
    return
  }
  showSubscribeForm.value = true
}

const submitSubscribe = async () => {
  if (!subscribeForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  
  submittingSubscribe.value = true
  try {
    await subscribeCase(caseId.value, { phone: subscribeForm.phone })
    ElMessage.success('订阅成功')
    isSubscribed.value = true
    caseDetail.value.subscription_count++
    showSubscribeForm.value = false
  } catch (error) {
    console.error('订阅失败:', error)
    ElMessage.error('订阅失败')
  } finally {
    submittingSubscribe.value = false
  }
}

// 分享
const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: caseDetail.value?.title,
      text: caseDetail.value?.description,
      url: window.location.href
    })
  } else {
    // 复制链接
    navigator.clipboard.writeText(window.location.href)
    ElMessage.success('链接已复制')
  }
}

// 提交留资
const submitLead = async () => {
  if (!leadForm.name || !leadForm.phone) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  submittingLead.value = true
  try {
    await createCaseLead(caseId.value, {
      ...leadForm,
      source: 'case_detail'
    })
    ElMessage.success('提交成功，我们会尽快联系您')
    showLeadForm.value = false
    // 清空表单
    leadForm.name = ''
    leadForm.phone = ''
    leadForm.area = ''
    leadForm.message = ''
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submittingLead.value = false
  }
}

// 打开 VR
const openVR = () => {
  window.open(caseDetail.value.vr_link, '_blank')
}

// 打开图片预览
const openImagePreview = (index, urls = null) => {
  if (urls) {
    previewImageList.value = urls
  } else {
    previewImageList.value = mediaList.value.map(m => m.url || m.file_url)
  }
  previewIndex.value = index
  imagePreviewVisible.value = true
}

// 下载文件
const downloadFile = (file) => {
  window.open(file.file_url, '_blank')
}

// 解析媒体 URL
const parseMediaUrls = (urls) => {
  try {
    return JSON.parse(urls)
  } catch {
    return []
  }
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0'
  const num = parseFloat(price)
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCaseDetail()
})
</script>

<style scoped lang="scss">
.case-detail-page {
  min-height: 100vh;
  background: #f8f8f8;
  padding-top: 80px;
}

.loading-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 24px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Hero 区域 */
.hero-section {
  position: relative;
  height: 70vh;
  min-height: 500px;
  overflow: hidden;
}

.hero-image {
  position: absolute;
  inset: 0;
}

.hero-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.45) 30%, rgba(0,0,0,0.75) 100%);
  backdrop-filter: blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
  -webkit-mask: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.2) 15%, black 50%, black 100%);
  mask: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.2) 15%, black 50%, black 100%);
}

.hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 60px 0;
  color: #fff;
  z-index: 2;
}

.case-badges {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.badge {
  padding: 6px 16px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  border-radius: 4px;
  font-size: 13px;
}

.badge.featured {
  background: #8B5A2B;
}

.case-title {
  font-size: 48px;
  font-weight: 300;
  margin-bottom: 16px;
  letter-spacing: 4px;
}

.case-location {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 16px;
}

.case-tags {
  display: flex;
  gap: 12px;
}

.tag {
  padding: 8px 16px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border-radius: 4px;
  font-size: 14px;
}

.tag.package {
  background: #8B5A2B;
}

/* 操作栏 */
.action-bar {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 16px 0;
  position: sticky;
  top: 80px;
  z-index: 10;
}

.action-bar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 12px;
}

.action-right .stats {
  display: flex;
  gap: 24px;
  color: #666;
  font-size: 14px;
}

.action-right .stats span {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 主内容区 */
.main-section {
  padding: 40px 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
}

/* 左侧内容 */
.content-left {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.section-title {
  font-size: 24px;
  font-weight: 400;
  margin-bottom: 24px;
  color: #1a1a1a;
}

/* 图集 */
.gallery-section {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.gallery-item {
  aspect-ratio: 4/3;
  overflow: hidden;
  border-radius: 4px;
  cursor: pointer;
}

.gallery-item.large {
  grid-column: span 2;
  grid-row: span 2;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* VR */
.vr-section {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
}

.vr-card {
  cursor: pointer;
}

.vr-preview {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.vr-preview img {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.vr-play {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.4);
  color: #fff;
  gap: 12px;
}

.vr-play .el-icon {
  font-size: 48px;
}

/* 文案内容 */
.content-section {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
}

.content-text {
  line-height: 2;
  color: #555;
  font-size: 15px;
  white-space: pre-line;
}

/* 时间轴 */
.timeline-section {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
}

.timeline-media {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.timeline-media img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
}

/* 右侧边栏 */
.content-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
}

.sidebar-card h4 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  color: #1a1a1a;
}

/* 报价卡片 */
.price-card {
  .price-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
  }
  
  .price-label {
    font-size: 14px;
    color: #666;
  }
  
  .price-value {
    font-size: 28px;
    font-weight: 600;
    color: #8B5A2B;
  }
  
  .price-detail {
    .price-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      font-size: 14px;
      color: #555;
      border-bottom: 1px dashed #eee;
      
      &:last-child {
        border-bottom: none;
      }
    }
  }
}

/* 信息卡片 */
.info-card {
  .info-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .info-item {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    
    .label {
      color: #999;
    }
    
    .value {
      color: #333;
      font-weight: 500;
    }
  }
}

/* 文件卡片 */
.files-card {
  .file-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .file-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f8f8f8;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s;
    
    &:hover {
      background: #eee;
    }
    
    .file-name {
      flex: 1;
      font-size: 14px;
      color: #333;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .download-icon {
      color: #999;
    }
  }
}

/* 留资卡片 */
.lead-card {
  text-align: center;
  
  p {
    font-size: 13px;
    color: #999;
    margin-bottom: 16px;
  }
}

/* 留资弹窗 */
.lead-form-content {
  .lead-desc {
    color: #666;
    margin-bottom: 20px;
    line-height: 1.6;
  }
}

/* 404 */
.not-found {
  padding: 80px 24px;
}

/* 响应式 */
@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-section {
    height: 50vh;
    min-height: 400px;
  }
  
  .case-title {
    font-size: 32px;
  }
  
  .action-bar {
    top: 64px;
  }
  
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .gallery-item.large {
    grid-column: span 2;
    grid-row: span 1;
  }
}

@media (max-width: 768px) {
  .case-detail-page {
    padding-top: 64px;
  }
  
  .hero-section {
    height: 40vh;
    min-height: 300px;
  }
  
  .hero-content {
    padding: 40px 24px;
  }
  
  .case-title {
    font-size: 24px;
  }
  
  .case-location {
    font-size: 14px;
  }
  
  .action-bar .container {
    flex-direction: column;
    gap: 16px;
  }
  
  .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .gallery-item.large {
    grid-column: span 1;
  }
  
  .gallery-section,
  .vr-section,
  .content-section,
  .timeline-section {
    padding: 20px;
  }
  
  .section-title {
    font-size: 20px;
  }
}
</style>
