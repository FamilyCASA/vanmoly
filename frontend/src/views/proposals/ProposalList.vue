<template>
  <div class="proposal-list-page">
    <Navbar />

    <!-- 英雄区 -->
    <header class="hero-section">
      <div class="hero-bg" v-if="featuredCase">
        <img :src="resolveImageUrl(currentHeroImage)" :alt="featuredCase.title" v-if="currentHeroImage" />
        <div v-else class="hero-placeholder"></div>
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-bg" v-else>
        <div class="hero-placeholder"></div>
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-content">
        <span class="hero-label">PROPOSAL CENTER</span>
        <h1 class="hero-title">提案中心</h1>
        <p class="hero-subtitle">为每个家，呈现完整的全案设计提案</p>
      </div>
    </header>

    <!-- 筛选栏 -->
    <section class="filter-section">
      <div class="filter-container">
        <div class="filter-group">
          <button class="filter-btn" :class="{ active: !filters.style }" @click="clearFilter('style')">全部风格</button>
          <button class="filter-btn" :class="{ active: filters.style === style }" v-for="style in styleOptions" :key="style" @click="setFilter('style', style)">{{ style }}</button>
        </div>
        <div class="filter-group">
          <button class="filter-btn" :class="{ active: !filters.house_type }" @click="clearFilter('house_type')">全部户型</button>
          <button class="filter-btn" :class="{ active: filters.house_type === ht }" v-for="ht in houseTypeOptions" :key="ht" @click="setFilter('house_type', ht)">{{ ht }}</button>
        </div>
      </div>
    </section>

    <!-- 提案网格 -->
    <section class="proposals-section">
      <div class="proposals-container">
        <div class="proposals-grid" v-if="!loading && cases.length">
          <div class="proposal-card" v-for="item in cases" :key="item.id" @click="openSlide(item.id)">
            <div class="card-image">
              <img :src="resolveImageUrl(getCoverImage(item))" :alt="item.title" v-if="getCoverImage(item)" />
              <div class="card-placeholder" v-else>
                <span>{{ item.title?.charAt(0) || 'P' }}</span>
              </div>
              <div class="card-badge">
                <span v-if="item.style">{{ item.style }}</span>
                <span v-if="item.house_type">{{ item.house_type }}</span>
              </div>
              <div class="card-overlay">
                <span class="view-btn">查看提案 →</span>
              </div>
            </div>
            <div class="card-info">
              <h3 class="card-title">{{ item.title || '未命名提案' }}</h3>
              <p class="card-desc" v-if="item.atmosphere">{{ item.atmosphere }}</p>
              <div class="card-meta">
                <span v-if="item.area">{{ item.area }}m²</span>
                <span v-if="item.total_price">¥{{ formatPrice(item.total_price) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div class="loading-state" v-if="loading">
          <div class="spinner"></div>
          <p>加载提案中...</p>
        </div>

        <!-- 空状态 -->
        <div class="empty-state" v-if="!loading && !cases.length">
          <div class="empty-icon">📋</div>
          <p>暂无提案</p>
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore && !loading">
          <button class="load-more-btn" @click="loadMore">加载更多</button>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getPublicCases } from '@/api/case'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()
const loading = ref(true)
const cases = ref([])
const total = ref(0)
const hasMore = ref(false)
const featuredCase = ref(null)
const currentHeroImage = ref('')
const pagination = { page: 1, page_size: 12 }
const filters = ref({ style: '', house_type: '' })

const styleOptions = ['现代简约', '新中式', '轻奢', '北欧', '日式', '美式']
const houseTypeOptions = ['三室两厅', '四室两厅', '两室两厅', '复式', '别墅']

const fetchCases = async (isLoadMore = false) => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filters.value.style) params.style = filters.value.style
    if (filters.value.house_type) params.house_type = filters.value.house_type

    const res = await getPublicCases(params)
    const items = res?.items || []

    if (isLoadMore) {
      cases.value = [...cases.value, ...items]
    } else {
      cases.value = items
      if (items.length > 0 && !featuredCase.value) {
        featuredCase.value = items[0]
        currentHeroImage.value = getCoverImage(items[0])
      }
    }

    total.value = res?.total || 0
    hasMore.value = cases.value.length < total.value
  } catch (e) {
    console.error('Failed to fetch proposals:', e)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  pagination.page++
  fetchCases(true)
}

const setFilter = (key, value) => {
  filters.value[key] = value
  pagination.page = 1
  cases.value = []
  featuredCase.value = null
  fetchCases()
}

const clearFilter = (key) => {
  filters.value[key] = ''
  pagination.page = 1
  cases.value = []
  featuredCase.value = null
  fetchCases()
}

const getCoverImage = (item) => {
  if (item.hero_images && item.hero_images.length) return item.hero_images[0]
  if (item.cover_image) return item.cover_image
  return ''
}

const resolveImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return window.__API_BASE__ ? window.__API_BASE__ + url : url
}

const formatPrice = (val) => {
  if (!val) return '0'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const openSlide = (id) => {
  router.push(`/slides/${id}`)
}

onMounted(() => {
  fetchCases()
})
</script>

<style scoped>
.proposal-list-page {
  min-height: 100vh;
  background: var(--bg-surface, #1a1a2e);
  color: var(--text-primary, #E8E8E8);
}

/* 英雄区 */
.hero-section {
  position: relative;
  height: 50vh;
  min-height: 400px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #16213e, #0f3460);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(26,26,46,0.3) 0%, rgba(26,26,46,0.85) 100%);
}

.hero-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 40px;
}

.hero-label {
  font-size: 12px;
  letter-spacing: 4px;
  color: var(--primary, #409EFF);
  margin-bottom: 16px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255,255,255,0.7);
  max-width: 500px;
}

/* 筛选栏 */
.filter-section {
  position: sticky;
  top: 80px;
  z-index: 10;
  background: var(--bg-elevated, #16213e);
  border-bottom: 1px solid var(--border, #2a2a3e);
  padding: 16px 0;
}

.filter-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px 32px;
}

.filter-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-btn {
  padding: 6px 16px;
  border: 1px solid var(--border, #2a2a3e);
  border-radius: 20px;
  background: transparent;
  color: var(--text-secondary, #A0A0B8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  border-color: var(--primary, #409EFF);
  color: var(--text-primary, #E8E8E8);
}

.filter-btn.active {
  background: var(--primary, #409EFF);
  border-color: var(--primary, #409EFF);
  color: #fff;
}

/* 提案网格 */
.proposals-section {
  padding: 48px 0 80px;
}

.proposals-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.proposals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 32px;
}

/* 卡片 */
.proposal-card {
  background: var(--bg-card, #1e1e38);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.proposal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}

.card-image {
  position: relative;
  height: 240px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.proposal-card:hover .card-image img {
  transform: scale(1.05);
}

.card-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0f3460, #16213e);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-placeholder span {
  font-size: 48px;
  font-weight: 700;
  color: rgba(255,255,255,0.2);
}

.card-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
}

.card-badge span {
  padding: 4px 10px;
  background: rgba(0,0,0,0.6);
  border-radius: 12px;
  font-size: 12px;
  color: #fff;
  backdrop-filter: blur(8px);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.proposal-card:hover .card-overlay {
  opacity: 1;
}

.view-btn {
  padding: 10px 24px;
  background: var(--primary, #409EFF);
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.card-info {
  padding: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-title, #FFFFFF);
  margin: 0 0 8px;
}

.card-desc {
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-tertiary, #6B6B80);
}

.card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
  color: var(--text-secondary, #A0A0B8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border, #2a2a3e);
  border-top-color: var(--primary, #409EFF);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
  color: var(--text-secondary, #A0A0B8);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 加载更多 */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 48px;
}

.load-more-btn {
  padding: 12px 32px;
  background: transparent;
  border: 1px solid var(--border, #2a2a3e);
  border-radius: 8px;
  color: var(--text-primary, #E8E8E8);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover {
  border-color: var(--primary, #409EFF);
  background: rgba(64,158,255,0.1);
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-section {
    height: 40vh;
    min-height: 300px;
  }

  .hero-title {
    font-size: 32px;
  }

  .proposals-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .proposals-container,
  .filter-container {
    padding: 0 20px;
  }
}
</style>
