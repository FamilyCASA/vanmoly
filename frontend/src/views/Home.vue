<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <nav class="navbar" :class="{ 'scrolled': scrolled, 'transparent': !scrolled }">
      <div class="nav-container">
        <div class="nav-brand" @click="scrollToTop">
          <div class="logo-mark">
            <span class="logo-icon">
              <svg viewBox="0 0 40 40" fill="none">
                <rect x="4" y="12" width="14" height="20" rx="2" fill="currentColor" opacity="0.9"/>
                <rect x="22" y="8" width="14" height="24" rx="2" fill="currentColor" opacity="0.6"/>
              </svg>
            </span>
            <div class="logo-text">
              <span class="brand-name">D&B 帝标|设记家</span>
              <span class="brand-tag">DESIGNARY</span>
            </div>
          </div>
        </div>
        
        <div class="nav-menu">
          <a href="#services" class="nav-link">服务</a>
          <a href="#cases" class="nav-link">案例</a>
          <a href="#about" class="nav-link">关于</a>
          <a href="#contact" class="nav-link">联系</a>
        </div>
        
        <div class="nav-actions">
          <router-link to="/products" class="btn-text">产品中心</router-link>
          <router-link to="/cases" class="btn-text">案例展示</router-link>
          <router-link to="/book" class="btn-primary">
            <span>预约量尺</span>
            <el-icon><ArrowRight /></el-icon>
          </router-link>
          <SelectionButton />
        </div>
        
        <!-- 移动端菜单按钮 -->
        <button class="menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
          <span :class="{ 'open': mobileMenuOpen }"></span>
        </button>
      </div>
      
      <!-- 移动端菜单 -->
      <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">
        <a href="#services" @click="mobileMenuOpen = false">服务</a>
        <a href="#cases" @click="mobileMenuOpen = false">案例</a>
        <a href="#about" @click="mobileMenuOpen = false">关于</a>
        <a href="javascript:void(0)" @click="goToSelection">我的选品</a>
        <router-link to="/book" class="btn-primary" @click="mobileMenuOpen = false">预约量尺</router-link>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-visual">
        <div class="hero-image-wrapper">
          <div class="hero-image" :style="{ backgroundImage: `url(${currentHeroImage})` }"></div>
          <div class="hero-overlay"></div>
        </div>
        <div class="hero-slider-dots">
          <span 
            v-for="(img, index) in heroImages" 
            :key="index"
            :class="{ 'active': currentHeroIndex === index }"
            @click="setHeroImage(index)"
          ></span>
        </div>
      </div>
      
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>专注全案落地服务</span>
        </div>
         <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>专注全案室内设计</span>
        </div>
         <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>专注高端全屋定制</span>
        </div>
         <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>专注软装饰品陈设</span>
        </div>
        <h1 class="hero-title">
          <span class="title-line">让家成为</span>
          <span class="title-line highlight">艺术品</span>
        </h1>
        <p class="hero-desc">从空间规划到软装搭配，D&B 帝标|设记家为您提供一站式全案设计服务</p>
        <div class="hero-stats-row">
          <div class="stat-item">
            <span class="stat-num">12</span>
            <span class="stat-unit">年</span>
            <span class="stat-label">行业深耕</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-num">2000</span>
            <span class="stat-unit">+</span>
            <span class="stat-label">实景案例</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-num">98</span>
            <span class="stat-unit">%</span>
            <span class="stat-label">客户满意度</span>
          </div>
        </div>
        <div class="hero-actions">
          <router-link to="/cases" class="btn-large btn-primary">
            <span>浏览案例</span>
            <el-icon><ArrowRight /></el-icon>
          </router-link>
          <router-link to="/book" class="btn-large btn-outline">
            <el-icon><Calendar /></el-icon>
            <span>预约量尺</span>
          </router-link>
        </div>
      </div>
      
      <div class="scroll-indicator" @click="scrollToServices">
        <div class="mouse">
          <div class="wheel"></div>
        </div>
        <span>向下滚动</span>
      </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="services">
      <div class="section-container">
        <div class="section-header">
          <span class="section-label">Our Services</span>
          <h2 class="section-title">全案服务，一站搞定</h2>
          <p class="section-desc">从设计到交付，每一个环节都为您精心把控</p>
        </div>
        
        <div class="services-grid">
          <div class="service-card" v-for="(service, index) in services" :key="index">
            <div class="service-icon">
              <component :is="service.icon" />
            </div>
            <h3 class="service-title">{{ service.title }}</h3>
            <p class="service-desc">{{ service.desc }}</p>
            <ul class="service-features">
              <li v-for="(feature, fIndex) in service.features" :key="fIndex">
                <el-icon><Check /></el-icon>
                <span>{{ feature }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Cases Section -->
    <section id="cases" class="cases">
      <div class="section-container">
        <div class="section-header">
          <span class="section-label">Featured Cases</span>
          <h2 class="section-title">精选案例</h2>
          <p class="section-desc">每一个家，都是独一无二的艺术品</p>
        </div>
        
        <div class="cases-filter">
          <button 
            v-for="filter in caseFilters" 
            :key="filter.value"
            :class="{ 'active': currentFilter === filter.value }"
            @click="currentFilter = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <div class="cases-grid">
          <div 
            v-for="caseItem in filteredCases" 
            :key="caseItem.id" 
            class="case-item"
            @click="goToCase(caseItem.id)"
          >
            <div class="case-image-wrapper">
              <img v-if="caseItem.cover_image" :src="caseItem.cover_image" :alt="caseItem.title">
              <div v-else class="case-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
              <div class="case-overlay">
                <span class="view-btn">查看详情</span>
              </div>
              <span class="case-type">{{ caseItem.type }}</span>
            </div>
            <div class="case-content">
              <h4 class="case-title">{{ caseItem.title }}</h4>
              <div class="case-meta">
                <span class="case-location">
                  <el-icon><Location /></el-icon>
                  {{ caseItem.location || '成都' }}
                </span>
                <span class="case-area">{{ caseItem.area }}㎡</span>
              </div>
              <div class="case-tags">
                <span class="tag">{{ caseItem.style }}</span>
                <span class="tag">{{ caseItem.space_type }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="cases-more">
          <router-link to="/cases" class="btn-outline">
            <span>查看全部案例</span>
            <el-icon><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Process Section -->
    <section class="process">
      <div class="section-container">
        <div class="section-header light">
          <span class="section-label">Our Process</span>
          <h2 class="section-title">服务流程</h2>
          <p class="section-desc">简单四步，开启品质生活</p>
        </div>
        
        <div class="process-timeline">
          <div class="process-step" v-for="(step, index) in processSteps" :key="index">
            <div class="step-number">0{{ index + 1 }}</div>
            <div class="step-content">
              <div class="step-icon">
                <component :is="step.icon" />
              </div>
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-desc">{{ step.desc }}</p>
            </div>
            <div v-if="index < processSteps.length - 1" class="step-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="about">
      <div class="section-container">
        <div class="about-grid">
          <div class="about-content">
            <span class="section-label">About Us</span>
            <h2 class="section-title">关于D&B 帝标|设记家</h2>
            <p class="about-text">
              D&B 帝标|设记家成立于2014年，专注于高端全屋定制与全案设计服务。我们相信，每一个家都应该是一件艺术品，承载着居住者的生活理想与审美追求。
            </p>
            <p class="about-text">
              从空间规划、硬装设计到软装搭配，我们的专业团队为您提供一站式解决方案，让装修不再是烦恼，而是一次美好的创作之旅。
            </p>
            <div class="about-stats">
              <div class="about-stat">
                <span class="stat-value">50+</span>
                <span class="stat-label">专业设计师</span>
              </div>
              <div class="about-stat">
                <span class="stat-value">30+</span>
                <span class="stat-label">合作品牌</span>
              </div>
              <div class="about-stat">
                <span class="stat-value">100%</span>
                <span class="stat-label">环保材料</span>
              </div>
            </div>
          </div>
          <div class="about-image">
            <div class="image-frame">
              <div class="image-placeholder">
                <el-icon><OfficeBuilding /></el-icon>
                <span>品牌展示图</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-background">
        <div class="cta-pattern"></div>
      </div>
      <div class="section-container">
        <div class="cta-content">
          <h2 class="cta-title">准备好打造您的理想之家了吗？</h2>
          <p class="cta-desc">立即预约免费量尺，获取专属设计方案与报价</p>
          <div class="cta-actions">
            <router-link to="/book" class="btn-large btn-primary">
              <el-icon><Calendar /></el-icon>
              <span>预约免费量尺</span>
            </router-link>
            <a href="tel:400-888-8888" class="btn-large btn-outline-light">
              <el-icon><Phone /></el-icon>
              <span>400-888-8888</span>
            </a>
          </div>
          <p class="cta-note">* 免费量尺服务限成都地区，设计师将在24小时内与您联系</p>
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="contact">
      <div class="section-container">
        <div class="contact-grid">
          <div class="contact-info">
            <span class="section-label">Contact Us</span>
            <h2 class="section-title">联系我们</h2>
            <p class="contact-desc">期待与您的每一次交流</p>
            
            <div class="contact-items">
              <div class="contact-item">
                <div class="contact-icon">
                  <el-icon><Location /></el-icon>
                </div>
                <div class="contact-detail">
                  <span class="contact-label">先锋展厅地址</span>
                  <span class="contact-value">成都市青羊区蔡桥街道天府匠芯北区A座6-10</span>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon">
                  <el-icon><Phone /></el-icon>
                </div>
                <div class="contact-detail">
                  <span class="contact-label">服务热线</span>
                  <span class="contact-value">139 0817 9177</span>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="contact-detail">
                  <span class="contact-label">营业时间</span>
                  <span class="contact-value">周一至周日 9:00-18:00</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="contact-form-wrapper">
            <div class="quick-lead-form">
              <h3>快速咨询</h3>
              <p>留下您的联系方式，我们将尽快与您联系</p>
              <form @submit.prevent="submitQuickLead">
                <div class="form-group">
                  <input 
                    v-model="quickLead.name" 
                    type="text" 
                    placeholder="您的称呼"
                    required
                  >
                </div>
                <div class="form-group">
                  <input 
                    v-model="quickLead.phone" 
                    type="tel" 
                    placeholder="手机号码"
                    required
                  >
                </div>
                <div class="form-group">
                  <select v-model="quickLead.budget">
                    <option value="">装修预算</option>
                    <option value="10-20万">10-20万</option>
                    <option value="20-30万">20-30万</option>
                    <option value="30-50万">30-50万</option>
                    <option value="50万以上">50万以上</option>
                  </select>
                </div>
                <button type="submit" class="btn-primary btn-block" :disabled="submitting">
                  <span v-if="!submitting">提交咨询</span>
                  <span v-else>提交中...</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="section-container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="logo-mark">
              <span class="logo-icon">
                <svg viewBox="0 0 40 40" fill="none">
                  <rect x="4" y="12" width="14" height="20" rx="2" fill="currentColor" opacity="0.9"/>
                  <rect x="22" y="8" width="14" height="24" rx="2" fill="currentColor" opacity="0.6"/>
                </svg>
              </span>
              <div class="logo-text">
                <span class="brand-name">D&B 帝标|设记家</span>
                <span class="brand-tag">DESIGNARY</span>
              </div>
            </div>
            <p class="footer-desc">专注高端全屋定制，让家成为艺术品</p>
            <div class="footer-social">
              <a href="#" class="social-link">
                <el-icon><ChatDotRound /></el-icon>
              </a>
              <a href="#" class="social-link">
                <el-icon><VideoCamera /></el-icon>
              </a>
              <a href="#" class="social-link">
                <el-icon><Share /></el-icon>
              </a>
            </div>
          </div>
          
          <div class="footer-links">
            <div class="footer-col">
              <h4>服务</h4>
              <a href="#services">全案服务</a>
              <a href="#services">软装搭配</a>
              <a href="#services">全屋定制</a>
              <a href="#services">施工管理</a>
            </div>
            <div class="footer-col">
              <h4>案例</h4>
              <router-link to="/cases">实景案例</router-link>
              <router-link to="/cases">在建工地</router-link>
              <router-link to="/cases">设计方案</router-link>
            </div>
            <div class="footer-col">
              <h4>关于</h4>
              <a href="#about">品牌故事</a>
              <a href="#about">设计团队</a>
              <a href="#about">合作伙伴</a>
            </div>
            <div class="footer-col">
              <h4>联系</h4>
              <router-link to="/book">预约量尺</router-link>
              <a href="#contact">展厅地址</a>
              <router-link to="/login">员工登录</router-link>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; 2026 D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 · 蜀ICP备XXXXXXXX号</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowRight, Calendar, Check, Picture, Location, 
  OfficeBuilding, Phone, Clock, ChatDotRound, 
  VideoCamera, Share, EditPen, House, Tools, Brush, Present 
} from '@element-plus/icons-vue'
import { getFeaturedCases } from '@/api/case'
import { createLead } from '@/api/lead'
import { ElMessage } from 'element-plus'
import SelectionButton from '@/components/SelectionButton.vue'

const router = useRouter()

// 导航滚动效果
const scrolled = ref(false)
const mobileMenuOpen = ref(false)

const handleScroll = () => {
  scrolled.value = window.scrollY > 50
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 跳转到选品中心
const goToSelection = () => {
  mobileMenuOpen.value = false
  const customerToken = localStorage.getItem('customer_token')
  if (!customerToken) {
    router.push('/register?redirect=' + encodeURIComponent('/selection-center'))
  } else {
    router.push('/selection-center')
  }
}

const scrollToServices = () => {
  document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' })
}

// Hero轮播
const heroImages = ref([
  'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=80',
  'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80',
  'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80'
])
const currentHeroIndex = ref(0)
const currentHeroImage = computed(() => heroImages.value[currentHeroIndex.value])

let heroInterval = null
const startHeroSlider = () => {
  heroInterval = setInterval(() => {
    currentHeroIndex.value = (currentHeroIndex.value + 1) % heroImages.value.length
  }, 5000)
}

const setHeroImage = (index) => {
  currentHeroIndex.value = index
  clearInterval(heroInterval)
  startHeroSlider()
}

// 服务数据
const services = ref([
  {
    icon: 'EditPen',
    title: '全案设计',
    desc: '从空间规划到软装搭配，提供完整的设计方案',
    features: ['空间规划设计', '效果图呈现', '施工图深化', '材料选型']
  },
  {
    icon: 'House',
    title: '定制家具',
    desc: '自有工厂生产，品质可控，风格统一',
    features: ['衣柜定制', '橱柜定制', '木门定制', '护墙板']
  },
  {
    icon: 'Tools',
    title: '施工监理',
    desc: '专业监理团队，全程把控施工质量',
    features: ['节点验收', '质量把控', '进度管理', '问题协调']
  },
  {
    icon: 'Brush',
    title: '软装搭配',
    desc: '专业软装设计师，打造完整家居风格',
    features: ['家具选配', '窗帘布艺', '灯具搭配', '饰品陈列']
  }
])

// 案例数据
const caseFilters = ref([
  { label: '全部', value: 'all' },
  { label: '现代', value: '现代' },
  { label: '北欧', value: '北欧' },
  { label: '新中式', value: '新中式' },
  { label: '轻奢', value: '轻奢' }
])
const currentFilter = ref('all')
const featuredCases = ref([])

const filteredCases = computed(() => {
  if (currentFilter.value === 'all') return featuredCases.value
  return featuredCases.value.filter(c => c.atmosphere === currentFilter.value)
})

const fetchCases = async () => {
  try {
    const res = await getFeaturedCases(6)
    featuredCases.value = res || []
  } catch (error) {
    console.log('获取精选案例失败，使用示例数据:', error)
    // 使用示例数据
    featuredCases.value = [
      { id: 1, title: '龙湖天街·现代轻奢', type: '实景', location: '龙湖天街', area: 128, atmosphere: '温馨', space_type: '四室两厅' },
      { id: 2, title: '万科城·北欧简约', type: '实景', location: '万科城', area: 105, atmosphere: '清新', space_type: '三室两厅' },
      { id: 3, title: '保利中心·新中式', type: '设计', location: '保利中心', area: 156, atmosphere: '雅致', space_type: '四室两厅' },
      { id: 4, title: '华润二十四城·轻奢风', type: '实景', location: '华润二十四城', area: 142, atmosphere: '浪漫', space_type: '四室两厅' },
      { id: 5, title: '中海国际·现代极简', type: '在建', location: '中海国际', area: 98, atmosphere: '简约', space_type: '三室一厅' },
      { id: 6, title: '仁恒置地·法式优雅', type: '实景', location: '仁恒置地', area: 180, atmosphere: '沉稳', space_type: '大平层' }
    ]
  }
}

const goToCase = (id) => {
  router.push(`/cases/${id}`)
}

// 流程步骤
const processSteps = ref([
  { icon: 'Calendar', title: '在线预约', desc: '填写信息，选择方便的时间' },
  { icon: 'EditPen', title: '上门量尺', desc: '设计师上门，精准测量' },
  { icon: 'House', title: '方案设计', desc: '3-5天出具完整方案' },
  { icon: 'Present', title: '施工交付', desc: '全程监理，品质保障' }
])

// 快速咨询表单
const quickLead = ref({
  name: '',
  phone: '',
  budget: ''
})
const submitting = ref(false)

const submitQuickLead = async () => {
  submitting.value = true
  try {
    await createLead({
      ...quickLead.value,
      source: '首页快速咨询'
    })
    ElMessage.success('提交成功，我们将尽快与您联系！')
    quickLead.value = { name: '', phone: '', budget: '' }
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  fetchCases()
  startHeroSlider()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  clearInterval(heroInterval)
})
</script>

<style scoped>
/* CSS Variables */
.home-page {
  --primary: #8B7355;
  --primary-light: #A68B6A;
  --primary-dark: #6B5344;
  --accent: #C4A77D;
  --dark: #2C2420;
  --light: #FAF8F5;
  --gray: #6B6560;
  --gray-light: #E8E4E0;
  --white: #FFFFFF;
  --shadow: 0 4px 20px rgba(44, 36, 32, 0.08);
  --shadow-lg: 0 10px 40px rgba(44, 36, 32, 0.12);
}

/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Navigation */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.4s ease;
}

.navbar.transparent {
  background: transparent;
}

.navbar.scrolled {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  cursor: pointer;
}

.logo-mark {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  color: var(--primary);
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--dark);
  letter-spacing: 2px;
}

.transparent .brand-name {
  color: var(--white);
}

.scrolled .brand-name {
  color: var(--dark);
}

.brand-tag {
  font-size: 10px;
  color: var(--gray);
  letter-spacing: 3px;
  font-weight: 500;
}

.transparent .brand-tag {
  color: rgba(255, 255, 255, 0.7);
}

.scrolled .brand-tag {
  color: var(--gray);
}

.nav-menu {
  display: flex;
  gap: 40px;
}

.nav-link {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
  position: relative;
}

.scrolled .nav-link {
  color: var(--dark);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--primary);
  transition: width 0.3s;
}

.nav-link:hover::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.btn-text {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.scrolled .btn-text {
  color: var(--dark);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary);
  color: var(--white);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.menu-toggle {
  display: none;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
}

.menu-toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--white);
  position: absolute;
  left: 4px;
  transition: all 0.3s;
}

.menu-toggle span::before,
.menu-toggle span::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background: var(--white);
  transition: all 0.3s;
}

.menu-toggle span::before {
  top: -8px;
}

.menu-toggle span::after {
  top: 8px;
}

.menu-toggle span.open {
  background: transparent;
}

.menu-toggle span.open::before {
  transform: rotate(45deg);
  top: 0;
}

.menu-toggle span.open::after {
  transform: rotate(-45deg);
  top: 0;
}

.mobile-menu {
  display: none;
  position: absolute;
  top: 80px;
  left: 0;
  right: 0;
  background: var(--white);
  padding: 24px;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--shadow-lg);
  transform: translateY(-100%);
  opacity: 0;
  transition: all 0.3s;
}

.mobile-menu.open {
  transform: translateY(0);
  opacity: 1;
}

.mobile-menu a {
  font-size: 16px;
  color: var(--dark);
  text-decoration: none;
  padding: 12px 0;
  border-bottom: 1px solid var(--gray-light);
}

/* Hero Section */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-visual {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.hero-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transition: opacity 1s ease;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(44, 36, 32, 0.85) 0%,
    rgba(44, 36, 32, 0.6) 50%,
    rgba(44, 36, 32, 0.4) 100%
  );
}

.hero-slider-dots {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 10;
}

.hero-slider-dots span {
  width: 40px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.3s;
}

.hero-slider-dots span.active {
  background: var(--white);
  width: 60px;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  color: var(--white);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 14px;
  margin-bottom: 32px;
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.hero-title {
  margin-bottom: 24px;
}

.title-line {
  display: block;
  font-size: 64px;
  font-weight: 300;
  line-height: 1.2;
  letter-spacing: 4px;
}

.title-line.highlight {
  font-size: 80px;
  font-weight: 700;
  color: var(--accent);
}

.hero-desc {
  font-size: 18px;
  opacity: 0.8;
  max-width: 480px;
  margin-bottom: 40px;
  line-height: 1.8;
}

.hero-stats-row {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 48px;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-num {
  font-size: 48px;
  font-weight: 700;
  color: var(--accent);
}

.stat-unit {
  font-size: 24px;
  font-weight: 600;
  color: var(--accent);
}

.stat-label {
  font-size: 14px;
  opacity: 0.7;
  margin-left: 8px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn-large {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-large.btn-primary {
  background: var(--primary);
  color: var(--white);
}

.btn-large.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 115, 85, 0.3);
}

.btn-large.btn-outline {
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: var(--white);
}

.btn-large.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  z-index: 10;
}

.scroll-indicator span {
  font-size: 12px;
  letter-spacing: 2px;
}

.mouse {
  width: 24px;
  height: 36px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  position: relative;
}

.wheel {
  width: 4px;
  height: 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 2px;
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  animation: scroll 2s infinite;
}

@keyframes scroll {
  0%, 100% { opacity: 1; transform: translateX(-50%) translateY(0); }
  50% { opacity: 0.5; transform: translateX(-50%) translateY(4px); }
}

/* Section Common */
.section-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-header.light {
  color: var(--white);
}

.section-label {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 3px;
  color: var(--primary);
  text-transform: uppercase;
  margin-bottom: 16px;
}

.section-header.light .section-label {
  color: var(--accent);
}

.section-title {
  font-size: 42px;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 16px;
}

.section-header.light .section-title {
  color: var(--white);
}

.section-desc {
  font-size: 16px;
  color: var(--gray);
}

.section-header.light .section-desc {
  color: rgba(255, 255, 255, 0.7);
}

/* Services Section */
.services {
  padding: 120px 0;
  background: var(--light);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.service-card {
  background: var(--white);
  padding: 40px 32px;
  border-radius: 16px;
  transition: all 0.4s;
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.service-icon {
  width: 64px;
  height: 64px;
  background: var(--light);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--primary);
  margin-bottom: 24px;
}

.service-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 12px;
}

.service-desc {
  font-size: 14px;
  color: var(--gray);
  line-height: 1.6;
  margin-bottom: 20px;
}

.service-features {
  list-style: none;
}

.service-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--gray);
  margin-bottom: 8px;
}

.service-features li .el-icon {
  color: var(--primary);
  font-size: 14px;
}

/* Cases Section */
.cases {
  padding: 120px 0;
  background: var(--white);
}

.cases-filter {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 48px;
}

.cases-filter button {
  padding: 10px 24px;
  border: 1px solid var(--gray-light);
  background: var(--white);
  border-radius: 24px;
  font-size: 14px;
  color: var(--gray);
  cursor: pointer;
  transition: all 0.3s;
}

.cases-filter button:hover,
.cases-filter button.active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--white);
}

.cases-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 48px;
}

.case-item {
  cursor: pointer;
  border-radius: 16px;
  overflow: hidden;
  background: var(--white);
  box-shadow: var(--shadow);
  transition: all 0.4s;
}

.case-item:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.case-image-wrapper {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.case-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s;
}

.case-item:hover .case-image-wrapper img {
  transform: scale(1.05);
}

.case-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--gray-light) 0%, #ddd 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: var(--gray);
}

.case-overlay {
  position: absolute;
  inset: 0;
  background: rgba(44, 36, 32, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.case-item:hover .case-overlay {
  opacity: 1;
}

.view-btn {
  padding: 12px 24px;
  background: var(--white);
  color: var(--dark);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.case-type {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 12px;
  background: var(--primary);
  color: var(--white);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.case-content {
  padding: 24px;
}

.case-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 12px;
}

.case-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.case-location,
.case-area {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--gray);
}

.case-tags {
  display: flex;
  gap: 8px;
}

.tag {
  padding: 4px 10px;
  background: var(--light);
  color: var(--gray);
  border-radius: 4px;
  font-size: 12px;
}

.cases-more {
  text-align: center;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: 1px solid var(--primary);
  color: var(--primary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: var(--primary);
  color: var(--white);
}

/* Process Section */
.process {
  padding: 120px 0;
  background: var(--dark);
}

.process-timeline {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.process-step {
  display: flex;
  align-items: flex-start;
  gap: 24px;
}

.step-number {
  font-size: 48px;
  font-weight: 700;
  color: var(--accent);
  opacity: 0.3;
  line-height: 1;
}

.step-content {
  text-align: center;
  color: var(--white);
  max-width: 180px;
}

.step-icon {
  width: 64px;
  height: 64px;
  background: rgba(196, 167, 125, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--accent);
  margin: 0 auto 16px;
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 14px;
  opacity: 0.7;
  line-height: 1.6;
}

.step-arrow {
  color: var(--accent);
  font-size: 24px;
  margin-top: 20px;
  opacity: 0.5;
}

/* About Section */
.about {
  padding: 120px 0;
  background: var(--light);
}

.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

.about-content .section-label {
  margin-bottom: 16px;
}

.about-content .section-title {
  margin-bottom: 24px;
}

.about-text {
  font-size: 16px;
  color: var(--gray);
  line-height: 1.8;
  margin-bottom: 20px;
}

.about-stats {
  display: flex;
  gap: 40px;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 1px solid var(--gray-light);
}

.about-stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.about-stat .stat-label {
  font-size: 14px;
  color: var(--gray);
}

.about-image {
  display: flex;
  justify-content: center;
}

.image-frame {
  position: relative;
  width: 100%;
  max-width: 480px;
}

.image-frame::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 20px;
  right: -20px;
  bottom: -20px;
  border: 2px solid var(--primary);
  border-radius: 16px;
  z-index: 0;
}

.image-placeholder {
  position: relative;
  z-index: 1;
  aspect-ratio: 4/3;
  background: var(--white);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 64px;
  color: var(--gray-light);
  box-shadow: var(--shadow);
}

.image-placeholder span {
  font-size: 14px;
  color: var(--gray);
}

/* CTA Section */
.cta {
  position: relative;
  padding: 120px 0;
  background: var(--primary);
  overflow: hidden;
}

.cta-background {
  position: absolute;
  inset: 0;
  opacity: 0.1;
}

.cta-pattern {
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.cta-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: var(--white);
}

.cta-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-desc {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 40px;
}

.cta-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-outline-light {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: var(--white);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
}

.cta-note {
  font-size: 13px;
  opacity: 0.7;
}

/* Contact Section */
.contact {
  padding: 120px 0;
  background: var(--white);
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
}

.contact-info .section-title {
  margin-bottom: 16px;
}

.contact-desc {
  font-size: 16px;
  color: var(--gray);
  margin-bottom: 48px;
}

.contact-items {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.contact-icon {
  width: 48px;
  height: 48px;
  background: var(--light);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--primary);
  flex-shrink: 0;
}

.contact-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.contact-label {
  font-size: 13px;
  color: var(--gray);
}

.contact-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--dark);
}

.quick-lead-form {
  background: var(--light);
  padding: 40px;
  border-radius: 16px;
}

.quick-lead-form h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--dark);
  margin-bottom: 8px;
}

.quick-lead-form > p {
  font-size: 14px;
  color: var(--gray);
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--gray-light);
  border-radius: 8px;
  font-size: 15px;
  background: var(--white);
  transition: all 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
}

.form-group input::placeholder {
  color: #999;
}

/* Footer */
.footer {
  padding: 80px 0 32px;
  background: var(--dark);
  color: var(--white);
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 2fr;
  gap: 80px;
  margin-bottom: 64px;
}

.footer-brand .logo-mark {
  margin-bottom: 20px;
}

.footer-brand .brand-name,
.footer-brand .brand-tag {
  color: var(--white);
}

.footer-desc {
  font-size: 14px;
  opacity: 0.7;
  margin-bottom: 24px;
  max-width: 280px;
}

.footer-social {
  display: flex;
  gap: 12px;
}

.social-link {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--white);
  font-size: 18px;
  transition: all 0.3s;
}

.social-link:hover {
  background: var(--primary);
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
}

.footer-col h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--white);
}

.footer-col a {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  margin-bottom: 12px;
  transition: color 0.3s;
}

.footer-col a:hover {
  color: var(--white);
}

.footer-bottom {
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-bottom p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 1200px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cases-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .process-timeline {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .step-arrow {
    display: none;
  }
}

@media (max-width: 992px) {
  .nav-menu,
  .nav-actions {
    display: none;
  }
  
  .menu-toggle {
    display: block;
  }
  
  .mobile-menu {
    display: flex;
  }
  
  .title-line {
    font-size: 42px;
  }
  
  .title-line.highlight {
    font-size: 56px;
  }
  
  .hero-stats-row {
    flex-wrap: wrap;
  }
  
  .stat-divider {
    display: none;
  }
  
  .about-grid,
  .contact-grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }
  
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }
  
  .footer-links {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .nav-container,
  .section-container {
    padding: 0 20px;
  }
  
  .services-grid,
  .cases-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-actions {
    flex-direction: column;
  }
  
  .btn-large {
    width: 100%;
    justify-content: center;
  }
  
  .cta-actions {
    flex-direction: column;
  }
  
  .section-title {
    font-size: 32px;
  }
  
  .cta-title {
    font-size: 28px;
  }
}
</style>
