
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { 
  ArrowRight, Calendar, Check, Picture, Location, 
  OfficeBuilding, Phone, Clock, ChatDotRound, 
  VideoCamera, Share, EditPen, House, Tools, Brush, Present, Close, ZoomIn
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
const heroImages = ref([])
const heroLoaded = ref(false)

// 加载后端轮播图
const loadHeroImages = async () => {
  try {
    const slides = await request.get('/frontend/hero-slides')
    if (slides && slides.length > 0) {
      heroImages.value = slides.map(s => s.url || s.image_url || '').filter(Boolean)
    }
  } catch (e) {
    console.error('加载轮播图失败', e)
  }
  if (heroImages.value.length === 0) {
    // 兜底默认图
    heroImages.value = [
      'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=80',
      'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80',
      'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80'
    ]
  }
  heroLoaded.value = true
}
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
// 服务流程（从API动态获取）
const workflowPhases = ref([])
const workflowLoading = ref(true)

const fetchWorkflowPhases = async () => {
  try {
    const res = await request.get('/workflows/public/phases')
    if (res?.phases) {
      workflowPhases.value = res.phases
    }
  } catch (e) {
    console.error('获取服务流程失败:', e)
  } finally {
    workflowLoading.value = false
  }
}

const processSteps = computed(() => {
  return workflowPhases.value.map(phase => ({
    title: phase.name,
    desc: phase.nodes?.map(n => n.node_name).join('、') || '',
    color: phase.color,
    nodeCount: phase.nodes?.length || 0
  }))
})

// 快速咨询表单
const quickLead = ref({
  name: '',
  phone: '',
  budget: ''
})
const submitting = ref(false)

const aboutSection = ref({ intro: '', intro2: '', image: '', stats: [] })
const brandLogos = ref([])
const brandVIUrl = ref('')

// Brand Lightbox
const lightboxOpen = ref(false)
const lightboxImage = ref('')
const lightboxTitle = ref('')

const openBrandVI = () => {
  lightboxImage.value = resolveImgUrl(aboutSection.image || brandVIUrl.value) || '/images/brand-vi.png?v=3'
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const openBrandLightbox = (imageSrc) => {
  lightboxImage.value = imageSrc
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const closeBrandLightbox = () => {
  lightboxOpen.value = false
  document.body.style.overflow = ''
}

const loadAboutSection = async () => {
  try {
    const res = await request.get('/frontend/about-section')
    if (res) {
      aboutSection.value = res
      // 如果有品牌VI图片，设置URL
      if (res.brand_vi_image) {
        brandVIUrl.value = res.brand_vi_image
      }
    }
  } catch (e) { console.error('加载关于我们失败', e) }
}

const loadBrandLogos = async () => {
  try {
    const res = await request.get('/frontend/brand-logos')
    brandLogos.value = res || []
  } catch (e) { console.error('加载品牌logo失败', e) }
}

const resolveImgUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // 使用相对路径，通过 Vite proxy 转发到后端
  return path
}

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
  loadHeroImages().then(() => startHeroSlider())
  loadAboutSection()
  loadBrandLogos()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  clearInterval(heroInterval)
})
