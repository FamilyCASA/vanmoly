<template>



  <div class="home-page">



    <Navbar />












    <!-- Hero Section -->



    <section class="hero">



      <div class="hero-visual">



        <div class="hero-image-wrapper">



          <div class="hero-image hero-image-a" :class="{ 'hero-image-active': activeLayer === 'a' }" :style="{ backgroundImage: `url(${heroImageA})` }"></div>
          <div class="hero-image hero-image-b" :class="{ 'hero-image-active': activeLayer === 'b' }" :style="{ backgroundImage: `url(${heroImageB})` }"></div>



          <div class="hero-overlay"></div>



        </div>



        <div class="hero-slider-dots">



          <span 



            v-for="(img, index) in heroSlides" 



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



        <div class="hero-brand-card">



          <img src="/images/designary-logo.png" class="hero-brand-logo" alt="DESIGNARY" />



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








    <!-- About Section -->



    <!-- About Section - 动态从后台加载 -->

    <section id="about" class="about">

      <div class="section-container">

        <div class="about-grid">

          <div class="about-content">

            <span class="section-label">About Us</span>

            <h2 class="section-title">{{ aboutSection?.title || '关于D&B 帝标|设记家' }}</h2>

            <div v-if="aboutSection?.description" class="about-text" v-html="aboutSection.description"></div>

            <template v-else>

              <p class="about-text">D&B 帝标|设记家成立于2014年，专注于高端全屋定制与全案设计服务。我们相信，每一个家都应该是一件艺术品，承载着居住者的生活理想与审美追求。</p>

              <p class="about-text">从空间规划、硬装设计到软装搭配，我们的专业团队为您提供一站式解决方案，让装修不再是烦恼，而是一次美好的创作之旅。</p>

            </template>

            <div class="about-stats">

              <div class="about-stat" v-for="(stat, si) in (aboutSection?.stats || defaultStats)" :key="si">

                <span class="stat-value">{{ stat.value }}</span>

                <span class="stat-label">{{ stat.label }}</span>

              </div>

            </div>

          </div>

          <div class="about-image">

            <div class="image-frame">

              <img v-if="aboutSection?.image" :src="resolveImgUrl(aboutSection.image)" alt="品牌展示" style="width:100%;height:100%;object-fit:cover;border-radius:12px;" />

              <div v-else class="image-placeholder">

                <el-icon><OfficeBuilding /></el-icon>

                <span>品牌展示图</span>

              </div>

            </div>

          </div>

        </div>

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





    <section id="process" class="process holo-dome-section">

      <div class="section-container">

        <div class="section-header light">

          <span class="section-label">Our Process</span>

          <h2 class="section-title">全案落地服务流程</h2>

          <p class="section-desc">6大阶段，54个标准节点，品质全程可追溯</p>

        </div>



        <div v-if="workflowLoading" class="holo-loading">

          <div class="holo-loader"></div>

          <span>加载服务流程...</span>

        </div>



        <div v-else class="holo-dome">

          <div class="holo-spheres">

            <div

              v-for="(phase, idx) in workflowPhases"

              :key="phase.code"

              class="holo-sphere-wrap"
              :class="{ active: expandedPhase === phase.code }"

              @click="togglePhase(phase.code)"
              @keydown.enter.prevent="togglePhase(phase.code)"
              @keydown.space.prevent="togglePhase(phase.code)"
              role="button"
              tabindex="0"
              :aria-expanded="expandedPhase === phase.code"

            >

              <div class="holo-sphere" :style="{ '--phase-color': phase.color || '#8B7355' }">

                <div class="sphere-ring"></div>

                <div class="sphere-core">

                  <div class="sphere-phase-name">{{ phase.name }}</div>

                  <div class="sphere-node-count">{{ phase.nodes?.length || 0 }}节点</div>

                </div>



              </div>

              <!-- Arrow: flowing water effect -->

              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">
                <svg class="arrow-shaft" viewBox="0 0 48 20" xmlns="http://www.w3.org/2000/svg">
                  <line x1="0" y1="10" x2="32" y2="10" stroke="rgba(196,167,125,0.5)" stroke-width="2" stroke-linecap="round"/>
                  <polygon points="30,4 44,10 30,16" fill="rgba(196,167,125,0.6)"/>
                </svg>
              </div>

            </div>

          </div>

          <transition name="phase-panel">
            <div v-if="selectedWorkflowPhase" class="phase-nodes-panel">

              <div class="nodes-panel-header" :style="{ borderColor: selectedWorkflowPhase.color || '#8B7355' }">

                <span class="nodes-phase-title">{{ selectedWorkflowPhase.name }}</span>

                <span class="nodes-count">{{ selectedWorkflowPhase.nodes?.length || 0 }}个节点</span>

              </div>

              <div class="nodes-list">

                <div v-for="(node, ni) in selectedWorkflowPhase.nodes" :key="getNodeCode(node) || ni" class="node-item">

                  <span v-if="getNodeCode(node)" class="node-code">{{ getNodeCode(node) }}</span>

                  <span class="node-name">{{ getNodeName(node) }}</span>

                </div>

              </div>

            </div>
          </transition>

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



    <!-- Process Section - HoloDome 全息穹顶 -->



    

    <!-- Brand Showcase 品牌背书 -->

    <section id="partners" v-if="brandLogos.length > 0" class="brands-showcase">

      <div class="section-container">

        <div class="section-header">

          <span class="section-label">Partners</span>

          <h2 class="section-title">品牌背书</h2>

          <p class="section-desc">携手知名品牌，为您提供品质保障</p>

        </div>

        <div class="brands-grid">

          <div v-for="(logo, idx) in brandLogos" :key="idx" class="brand-item">

            <img :src="resolveImgUrl(logo.url)" :alt="logo.name || ''" />

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



              <span>{{ ctaData.primaryBtn }}</span>



            </router-link>



            <a href="tel:400-888-8888" class="btn-large btn-outline-light">



              <el-icon><Phone /></el-icon>



              <span>{{ ctaData.secondaryBtn }}</span>



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



                  <span class="contact-value">{{ contactInfo.address }}</span>



                </div>



              </div>



              <div class="contact-item">



                <div class="contact-icon">



                  <el-icon><Phone /></el-icon>



                </div>



                <div class="contact-detail">



                  <span class="contact-label">服务热线</span>



                  <span class="contact-value">{{ contactInfo.phone }}</span>



                </div>



              </div>



              <div class="contact-item">



                <div class="contact-icon">



                  <el-icon><Clock /></el-icon>



                </div>



                <div class="contact-detail">



                  <span class="contact-label">营业时间</span>



                  <span class="contact-value">{{ contactInfo.hours }}</span>



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



          <p>&copy; 2026 D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 · 蜀ICP备XXXXXXXX号</p>



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

import Navbar from '@/components/Navbar.vue'

import request from '@/utils/request'



const router = useRouter()



// 导航滚动效果

const scrolled = ref(false)

const mobileMenuOpen = ref(false)



const handleScroll = () => {
  const heroEl = document.querySelector('.hero')
  scrolled.value = window.scrollY > (heroEl ? heroEl.offsetHeight - 80 : 50)
}



const scrollToTop = () => {

  window.scrollTo({ top: 0, behavior: 'smooth' })

}



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



// ===== Hero 轮播（从后台API加载） =====

const heroSlides = ref([])

const currentHeroIndex = ref(0)

const activeLayer = ref('a')
const heroImageA = ref('')
const heroImageB = ref('')

const showHeroImage = (index) => {
  const url = heroSlides.value.length > 0 ? resolveImgUrl(heroSlides.value[index]?.url || '') : ''
  if (activeLayer.value === 'a') {
    heroImageB.value = url
    activeLayer.value = 'b'
  } else {
    heroImageA.value = url
    activeLayer.value = 'a'
  }
  currentHeroIndex.value = index
}



let heroInterval = null

const startHeroSlider = () => {
  console.log('[HeroSlider] start called, slides:', heroSlides.value)
  if (heroSlides.value.length <= 1) return
  // 显示第一张图
  heroImageA.value = resolveImgUrl(heroSlides.value[0]?.url || '')
  activeLayer.value = 'a'
  currentHeroIndex.value = 0
  heroInterval = setInterval(() => {
    const nextIndex = (currentHeroIndex.value + 1) % heroSlides.value.length
    showHeroImage(nextIndex)
  }, 10000)
}



const setHeroImage = (index) => {
  showHeroImage(index)
  clearInterval(heroInterval)
  startHeroSlider()
}



const loadHeroSlides = async () => {

  try {

    const res = await request.get('/frontend/hero-slides')
    console.log('[Hero] raw response:', res)
    const slides = Array.isArray(res) ? res : (res?.data && Array.isArray(res.data) ? res.data : null)
    if (slides && slides.length > 0) {
      heroSlides.value = slides

    } else {

      // fallback 默认图

      heroSlides.value = [

        { id: 1, url: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=80' },

        { id: 2, url: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80' },

        { id: 3, url: 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80' }

      ]

    }

  } catch (e) {

    console.log('加载轮播图失败，使用默认图', e)

    heroSlides.value = [

      { id: 1, url: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=80' },

      { id: 2, url: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80' },

      { id: 3, url: 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80' }

    ]

  }

}



// ===== 服务优势（从后台API加载） =====

const services = ref([

  { icon: 'EditPen', title: '全案设计', desc: '从空间规划到软装搭配，提供完整的设计方案', features: ['空间规划设计', '效果图呈现', '施工图深化', '材料选型'] },

  { icon: 'House', title: '定制家具', desc: '自有工厂生产，品质可控，风格统一', features: ['衣柜定制', '橱柜定制', '木门定制', '护墙板'] },

  { icon: 'Tools', title: '施工监理', desc: '专业监理团队，全程把控施工质量', features: ['节点验收', '质量把控', '进度管理', '问题协调'] },

  { icon: 'Brush', title: '软装搭配', desc: '专业软装设计师，打造完整家居风格', features: ['家具选配', '窗帘布艺', '灯具搭配', '饰品陈列'] }

])



const loadServices = async () => {

  try {

    const res = await request.get('/frontend/services-section')

    if (res && Array.isArray(res.items) && res.items.length > 0) {

      services.value = res.items

    }

  } catch (e) {

    console.log('加载服务数据失败，使用默认', e)

  }

}



// ===== 案例数据 =====

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



// ===== 服务流程（从后台API加载，HoloDome全息穹顶） =====

const workflowPhases = ref([])

const workflowLoading = ref(true)

const expandedPhase = ref(null)


const selectedWorkflowPhase = computed(() => {
  return workflowPhases.value.find(phase => phase.code === expandedPhase.value) || null
})


const getNodeCode = (node) => {
  return node?.node_code || node?.code || ''
}

const getNodeName = (node) => {
  return node?.node_name || node?.name || node?.title || node?.label || '未命名节点'
}



const DEFAULT_WORKFLOW_PHASES = [
  { code: "phase1", name: "需求沟通", color: "#8B7355", nodes: [
    { code: "N1.1", name: "客户需求调研" },
    { code: "N1.2", name: "项目背景分析" },
    { code: "N1.3", name: "预算初步评估" }
  ]},
  { code: "phase2", name: "方案设计", color: "#6B8E6B", nodes: [
    { code: "N2.1", name: "设计方案制定" },
    { code: "N2.2", name: "效果图制作" },
    { code: "N2.3", name: "材料选型建议" }
  ]},
  { code: "phase3", name: "合同签订", color: "#7B8BA3", nodes: [
    { code: "N3.1", name: "预算明细确认" },
    { code: "N3.2", name: "合同条款议定" },
    { code: "N3.3", name: "首期款项支付" }
  ]},
  { code: "phase4", name: "施工阶段", color: "#A08060", nodes: [
    { code: "N4.1", name: "拆改工程" },
    { code: "N4.2", name: "水电改造" },
    { code: "N4.3", name: "泥瓦施工" },
    { code: "N4.4", name: "木工制作" },
    { code: "N4.5", name: "油漆涂刷" }
  ]},
  { code: "phase5", name: "竣工验收", color: "#9B7B5B", nodes: [
    { code: "N5.1", name: "整体验收" },
    { code: "N5.2", name: "问题整改" },
    { code: "N5.3", name: "清洁交付" }
  ]},
  { code: "phase6", name: "售后服务", color: "#5B8B7B", nodes: [
    { code: "N6.1", name: "质保说明" },
    { code: "N6.2", name: "定期回访" },
    { code: "N6.3", name: "售后响应" }
  ]}
]

const fetchWorkflowPhases = async () => {

  try {

    const res = await request.get('/workflows/public/phases')

    workflowPhases.value = res?.phases?.length ? res.phases : DEFAULT_WORKFLOW_PHASES

  } catch (e) {

    console.log('加载服务流程失败，使用默认数据', e)
      workflowPhases.value = DEFAULT_WORKFLOW_PHASES

  } finally {

    workflowLoading.value = false

  }

}



const togglePhase = (code) => {

  expandedPhase.value = expandedPhase.value === code ? null : code

}



// ===== 关于我们（从后台API加载） =====

const aboutSection = ref(null)

const defaultStats = [

  { value: '50+', label: '专业设计师' },

  { value: '30+', label: '合作品牌' },

  { value: '100%', label: '环保材料' }

]



const loadAboutSection = async () => {

  try {

    const res = await request.get('/frontend/about-section')

    if (res) {

      aboutSection.value = res

    }

  } catch (e) {

    console.log('加载关于我们失败', e)

  }

}



// ===== 品牌背书（从后台API加载） =====

const brandLogos = ref([])



const loadBrandLogos = async () => {

  try {

    const res = await request.get('/frontend/brand-logos')

    if (res && Array.isArray(res)) {

      brandLogos.value = res

    }

  } catch (e) {

    console.log('加载品牌Logo失败', e)

  }

}



// ===== CTA（从后台API加载） =====

const ctaData = ref({

  title: '准备好打造您的理想之家了吗？',

  subtitle: '立即预约免费量尺，获取专属设计方案与报价',

  primaryBtn: '预约免费量尺',

  secondaryBtn: '400-888-8888'

})



const loadCtaSection = async () => {

  try {

    const res = await request.get('/frontend/cta-section')

    if (res) {

      ctaData.value = { ...ctaData.value, ...res }

    }

  } catch (e) {

    console.log('加载CTA失败', e)

  }

}



// ===== 联系信息（从后台API加载） =====

const contactInfo = ref({

  address: '成都市青羊区蔡桥街道天府匠芯北区A座6-10',

  phone: '139 0817 9177',

  hours: '周一至周日 9:00-18:00'

})



const loadContactSection = async () => {

  try {

    const res = await request.get('/frontend/contact-section')

    if (res) {

      contactInfo.value = { ...contactInfo.value, ...res }

    }

  } catch (e) {

    console.log('加载联系信息失败', e)

  }

}



// ===== 图片URL处理 =====

const resolveImgUrl = (url) => {

  if (!url) return ''

  if (url.startsWith('http')) return url

  // 相对路径：统一通过 /api/v3 代理到后端静态文件
  if (url.startsWith('/')) {
    // 已经是 /api/v3 开头的不重复加
    if (url.startsWith('/api/v3')) return url
    return '/api/v3' + url
  }

  // 其他情况原样返回
  return url

}



// ===== 快速咨询表单 =====

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



onMounted(async () => {

  window.addEventListener('scroll', handleScroll)

  // 加载所有后台配置数据

  await loadHeroSlides()
  startHeroSlider()

  loadServices()

  fetchCases()

  fetchWorkflowPhases()

  loadAboutSection()

  loadBrandLogos()

  loadCtaSection()

  loadContactSection()

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



  transition: all 0.3s ease;

  background: rgba(15, 15, 20, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);



}







.navbar.transparent {
  background: transparent;
  border-bottom: none;
}







.navbar.scrolled {



  background: rgba(15, 15, 20, 0.98);
  backdrop-filter: blur(24px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);



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



  color: #ffffff;
  letter-spacing: 1px;
  font-size: 18px;



}







.transparent .brand-name {
  color: #ffffff;
}







.scrolled .brand-name {
  color: #ffffff;
}







.brand-tag {



  font-size: 10px;



  color: rgba(255, 255, 255, 0.5);
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
  gap: 28px;
}







.nav-link {



  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 400;
  transition: color 0.25s;
  position: relative;
  padding: 6px 0;



}







.scrolled .nav-link {
  color: rgba(255, 255, 255, 0.9);
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
  gap: 16px;
}

.btn-nav {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  padding: 6px 14px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  transition: all 0.25s;
  font-weight: 400;
}

.btn-nav:hover {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.08);
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
  background-repeat: no-repeat;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  opacity: 0;
  transition: opacity 1.5s ease;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
.hero-image-active {
  opacity: 1;
}







.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.25) 50%,
    rgba(0, 0, 0, 0.05) 80%,
    transparent 100%
  );
  backdrop-filter: blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
  -webkit-mask: radial-gradient(ellipse at center, black 40%, transparent 85%);
  mask: radial-gradient(ellipse at center, black 40%, transparent 85%);
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



  padding: 180px 40px 80px;



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







.hero-brand-card {
  position: absolute;
  left: 40px;
  top: 80px;
  z-index: 2;
  background: transparent;
  backdrop-filter: none;
  padding: 12px 20px;
}



.hero-brand-logo {
  width: 420px;
  height: auto;
  display: block;
}



.hero-brand-logo {
  width: 480px;
  height: auto;
  display: block;
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



  background: rgba(44, 36, 32, 0.3);



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





/* ===== HoloDome 全息穹顶 ===== */

.holo-section {

  background: linear-gradient(135deg, #1a1614 0%, #2C2420 40%, #1a1614 100%);

  position: relative;

  overflow: hidden;

}



.holo-loading {

  display: flex;

  flex-direction: column;

  align-items: center;

  gap: 16px;

  padding: 80px 0;

  color: rgba(255,255,255,0.6);

}



.holo-spinner {

  width: 40px;

  height: 40px;

  border: 3px solid rgba(196,167,125,0.2);

  border-top-color: #C4A77D;

  border-radius: 50%;

  animation: holo-spin 1s linear infinite;

}



@keyframes holo-spin {

  to { transform: rotate(360deg); }

}







/* ===== Brand Showcase ===== */

.brands-showcase {

  padding: 80px 0;

  background: var(--light);

}



.brands-grid {

  display: grid;

  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));

  gap: 16px;

}



.brand-item {

  aspect-ratio: 1;

  display: flex;

  align-items: center;

  justify-content: center;

  background: rgba(0,0,0,0.05);

  border-radius: 12px;

  padding: 20px;

  transition: transform 0.3s, box-shadow 0.3s;

}



.brand-item:hover {

  transform: translateY(-4px);

  box-shadow: 0 8px 24px rgba(0,0,0,0.08);

}



.brand-item img {

  max-width: 100%;

  max-height: 100%;

  object-fit: contain;

}



@media (max-width: 768px) {

  .brands-grid {

    grid-template-columns: repeat(3, 1fr);

  }

}





/* ===== HoloDome 全息穹顶样式 ===== */

.holo-dome-section {

  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);

  position: relative;

  overflow: hidden;

}

/* 流动色带：从左到右色相过渡 */

.holo-dome-section::before {

  content: '';

  position: absolute;

  inset: 0;

  background: linear-gradient(90deg,

    rgba(196,119,93,0.18) 0%,

    rgba(139,115,85,0.22) 20%,

    rgba(108,159,192,0.20) 40%,

    rgba(139,115,85,0.22) 60%,

    rgba(196,119,93,0.18) 80%,

    rgba(108,159,192,0.20) 100%

  );

  background-size: 200% 100%;

  animation: holo-color-flow 8s ease-in-out infinite;

  pointer-events: none;

  z-index: 0;

}

.holo-dome-section::after {

  content: '';

  position: absolute;

  inset: 0;

  background-image:

    linear-gradient(rgba(139,115,85,0.05) 1px, transparent 1px),

    linear-gradient(90deg, rgba(139,115,85,0.05) 1px, transparent 1px);

  background-size: 60px 60px;

  pointer-events: none;

  z-index: 1;

}

@keyframes holo-color-flow {

  0%   { background-position: 0% 0%; }

  50%  { background-position: 100% 0%; }

  100% { background-position: 0% 0%; }

}

.holo-loading {

  text-align: center;

  padding: 60px 20px;

  color: rgba(255,255,255,0.6);

}

.holo-loader {

  width: 40px; height: 40px;

  border: 3px solid rgba(139,115,85,0.3);

  border-top-color: var(--primary, #8B7355);

  border-radius: 50%;

  margin: 0 auto 16px;

  animation: holo-spin 1s linear infinite;

}

@keyframes holo-spin { to { transform: rotate(360deg); } }

.holo-dome { padding: 20px 0; }

.holo-spheres {

  display: flex;

  align-items: center;

  justify-content: center;

  gap: 48px;

  flex-wrap: wrap;

  padding: 20px 0;

  overflow: visible;

}

.holo-sphere-wrap {

  position: relative;

  display: flex;

  align-items: center;

  cursor: pointer;

  overflow: visible;
  border-radius: 50%;
  outline: none;

}

.holo-sphere-wrap.active .holo-sphere,
.holo-sphere-wrap:focus-visible .holo-sphere {
  transform: scale(1.08);
}

.holo-sphere-wrap.active .sphere-ring {
  opacity: 0.95;
  box-shadow: 0 0 28px var(--phase-color);
}

.holo-sphere {

  --phase-color: #8B7355;

  width: 130px; height: 130px;

  border-radius: 50%;

  position: relative;

  display: flex;

  align-items: center;

  justify-content: center;

  transition: all 0.4s ease;

}

.holo-sphere:hover { transform: scale(1.08); }

.sphere-ring {

  position: absolute; inset: 0;

  border-radius: 50%;

  border: 6px solid var(--phase-color);

  opacity: 0.4;

  animation: sphere-pulse 3s ease-in-out infinite;

}

@keyframes sphere-pulse {

  0%, 100% { opacity: 0.4; transform: scale(1); }

  50% { opacity: 0.8; transform: scale(1.05); }

}

.sphere-core {

  display: flex;

  flex-direction: column;

  align-items: center;

  justify-content: center;

  gap: 4px;

  z-index: 2;

  pointer-events: none;

}

.sphere-phase-name {

  color: #fff;

  font-size: 14px;

  font-weight: 700;

  letter-spacing: 1px;

  text-align: center;

  line-height: 1.3;

}

.sphere-node-count {

  color: var(--phase-color);

  font-size: 11px;

  text-align: center;

  opacity: 0.9;

  line-height: 1.2;

}






@keyframes arrow-flow {

  0%   { background-position: -70px 0; }

  100% { background-position: 60px 0; }

}

.phase-nodes-panel {

  width: min(980px, calc(100% - 40px));

  margin: 26px auto 0;

  background: rgba(10, 10, 30, 0.82);

  border: 1px solid rgba(139,115,85,0.3);

  border-radius: 12px;

  padding: 18px;

  z-index: 100;

  backdrop-filter: blur(10px);

  box-shadow: 0 8px 32px rgba(0,0,0,0.5);

}

.phase-panel-enter-active,
.phase-panel-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.phase-panel-enter-from,
.phase-panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.nodes-panel-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  padding-bottom: 10px;

  margin-bottom: 10px;

  border-bottom-width: 2px;

  border-bottom-style: solid;

}

.nodes-phase-title {

  color: #fff;

  font-size: 16px;

  font-weight: 700;

}

.nodes-count {

  color: rgba(255,255,255,0.5);

  font-size: 12px;

}

.nodes-list {

  max-height: 320px;

  overflow-y: auto;

  display: grid;

  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));

  gap: 8px;

}

.node-item {

  display: flex;

  align-items: center;

  gap: 8px;

  min-height: 36px;

  padding: 8px 10px;

  border-radius: 6px;

  background: rgba(255,255,255,0.08);

  transition: background 0.2s;

}

.node-item:hover { background: rgba(255,255,255,0.13); }

.node-code {

  color: rgba(139,115,85,0.8);

  font-size: 11px;

  font-family: monospace;

  min-width: 38px;
  flex-shrink: 0;

}

.node-name {

  color: #fff;

  font-size: 14px;
  font-weight: 600;
  line-height: 1.45;

}

@media (max-width: 768px) {

  .holo-spheres { flex-direction: column; gap: 8px; }

  .holo-sphere { width: 100px; height: 100px; }

  .sphere-core { width: 84px; height: 84px; }

  .sphere-phase-name { font-size: 13px; }

  .sphere-node-count { font-size: 10px; }

  .holo-arrow {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    flex-shrink: 0;
  }

  .arrow-shaft {
    width: 48px;
    height: 20px;
  }

  .phase-nodes-panel {
    width: calc(100% - 28px);
    margin-top: 18px;
    padding: 14px;
  }

  .nodes-panel-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .nodes-list {
    grid-template-columns: 1fr;
    max-height: 360px;
  }

}



</style>
