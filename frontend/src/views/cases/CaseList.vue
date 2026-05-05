<template>
  <div class="case-list-page">
    <!-- 统一导航栏 -->
    <Navbar />

    <!-- 第一层：氛围选择Tab（蔚来车型Tab风格） -->
    <div class="atmosphere-tabs">
      <div 
        v-for="atm in atmospheres" 
        :key="atm.key"
        class="tab-item"
        :class="{ active: filters.atmosphere === atm.value }"
        @click="selectAtmosphere(atm.key)"
      >
        <span class="tab-label">{{ atm.label }}</span>
        <span class="tab-count" v-if="atm.count">{{ atm.count }}</span>
      </div>
    </div>

    <!-- 全屏英雄区（杂志封面风格） -->
    <header class="hero-section" v-if="featuredCase">
      <!-- 多图轮播背景 -->
      <div class="hero-bg">
        <transition :name="carouselTransition" mode="out-in">
          <div :key="currentCarouselIndex" class="hero-slide">
            <img 
              v-if="hasValidCoverImage(currentHeroImage)" 
              :src="currentHeroImage" 
              :alt="featuredCase.title" 
              loading="lazy" 
              @error="e => handleImageError(e, featuredCase.atmosphere)"
            >
            <div v-else class="hero-placeholder" :style="{ background: getAtmosphereGradient(featuredCase.atmosphere) }"></div>
          </div>
        </transition>
        <div class="hero-overlay"></div>
        
        <!-- 轮播指示器 -->
        <div class="carousel-indicators" v-if="heroImages.length > 1">
          <span 
            v-for="(img, idx) in heroImages" 
            :key="idx"
            class="indicator"
            :class="{ active: idx === currentCarouselIndex }"
            @click="goToSlide(idx)"
          ></span>
        </div>
      </div>
      
      <!-- 杂志风格覆盖层 -->
      <div class="hero-magazine-overlay">
        <!-- 左上角品牌标识 -->
        <div class="brand-mark">
          <span class="brand-cn">帝标·设记家</span>
          <span class="brand-en">DESIGNARY</span>
        </div>
        
        <!-- 左侧服务团队 -->
        <div class="service-team-sidebar">
          <div class="team-label">SERVICE TEAM</div>
          <div class="team-members">
            <div class="team-member" v-if="featuredCase.planner">
              <span class="member-role">规划师</span>
              <span class="member-name">{{ featuredCase.planner.name }}</span>
            </div>
            <div class="team-member" v-if="featuredCase.designer">
              <span class="member-role">设计师</span>
              <span class="member-name">{{ featuredCase.designer.name }}</span>
            </div>
            <div class="team-member" v-if="featuredCase.responsible">
              <span class="member-role">客户经理</span>
              <span class="member-name">{{ featuredCase.responsible.name }}</span>
            </div>
            <div class="team-member" v-if="!featuredCase.planner && !featuredCase.designer && !featuredCase.responsible">
              <span class="member-name" style="color: rgba(255,255,255,0.5);">暂无团队信息</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧核心信息区（深色蒙版 + 去掉重复的面积/户型） -->
        <div class="hero-content">
          <div class="hero-badge" v-if="featuredCase.atmosphere">
            {{ getAtmosphereLabel(featuredCase.atmosphere) }}
          </div>
          <h1 class="hero-title">{{ featuredCase.title }}</h1>
          <p class="hero-subtitle">
            <span v-if="featuredCase.building_name">{{ featuredCase.building_name }}</span>
            <span v-if="featuredCase.building_name"> · </span>
            {{ featuredCase.location }}
            <span v-if="featuredCase.area"> · {{ featuredCase.area }}㎡ {{ featuredCase.house_type }}</span>
          </p>
          
          <!-- 数字参数展示（价格为主） -->
          <div class="hero-specs">
            <div class="spec-item" v-if="featuredCase.total_price">
              <span class="spec-value">¥{{ formatPrice(featuredCase.total_price) }}</span>
              <span class="spec-unit">万</span>
            </div>
          </div>
        </div>
        
        <!-- 底部 VR 二维码 + 按钮 -->
        <div class="hero-footer">
          <div class="vr-section" v-if="featuredCase.vr_qrcode">
            <img :src="featuredCase.vr_qrcode" alt="VR体验" class="vr-qrcode">
            <span class="vr-label">扫码体验VR</span>
          </div>
          <div class="hero-actions">
            <button class="btn-primary" @click="goToDetail(featuredCase.id)">
              查看详情
            </button>
            <button class="btn-secondary" @click="handleSubscribe(featuredCase)">
              <el-icon><Bell /></el-icon>
              {{ featuredCase.is_subscribed ? '已订阅' : '订阅更新' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 第二层：服务流程阶段横向筛选（横排按钮，点击展开细分节点） -->
    <div class="workflow-phase-filter-bar">
      <div class="phase-filter-row">
        <button
          v-for="phase in workflowPhases"
          :key="phase.key"
          class="phase-filter-btn"
          :class="{ active: selectedWorkflowPhase === phase.key, expanded: expandedPhase === phase.key }"
          @click="togglePhaseExpand(phase)"
        >
          <span class="phase-dot breathing-dot" v-if="phase.count > 0"></span>
          <span class="phase-name">{{ phase.label }}</span>
          <span class="phase-count" v-if="phase.count">({{ phase.count }})</span>
          <el-icon class="phase-arrow" :class="{ rotated: expandedPhase === phase.key }"><CaretBottom /></el-icon>
        </button>
        <button class="phase-clear-btn" v-if="selectedWorkflowPhase" @click="clearWorkflowFilter">
          <el-icon><Close /></el-icon> 清除筛选
        </button>
      </div>

      <!-- 展开的节点列表（横向滚动） -->
      <transition name="slide-down">
        <div class="phase-nodes-panel" v-if="expandedPhase && phaseNodes[expandedPhase]?.length > 0">
          <div class="nodes-scroll">
            <button
              v-for="node in phaseNodes[expandedPhase]"
              :key="node.id"
              class="node-chip"
              :class="{ selected: selectedNodeId === node.id }"
              @click="selectNode(node)"
              :title="node.caseTitle + ' - ' + node.node_name"
            >
              <span class="node-phase-tag">{{ getPhaseShortLabel(node.phase) }}</span>
              <span class="node-name">{{ node.node_name }}</span>
              <span class="node-case" v-if="node.caseTitle">{{ node.caseTitle }}</span>
            </button>
          </div>
        </div>
        <div class="phase-nodes-panel phase-nodes-loading" v-else-if="expandedPhase && loadingNodes">
          <span class="loading-text">加载节点中...</span>
        </div>
        <div class="phase-nodes-panel phase-nodes-empty" v-else-if="expandedPhase">
          <span>该阶段暂无节点数据</span>
        </div>
      </transition>
    </div>

    <!-- 第三层：颜色筛选色条（暖色→冷色→灰度，hover显示潘通名，点击筛选） -->
    <div class="color-strip-bar" v-if="colorPalette.length > 0">
      <div class="color-strip-row">
        <span class="strip-label">配色</span>
        <!-- 动态色条：每格宽度 = 100% / 颜色总数 -->
        <div class="color-strip-track" @mouseleave="hoveredHex = null">
          <div
            v-for="color in colorPalette"
            :key="color.hex"
            class="color-strip-cell"
            :style="{
              backgroundColor: color.hex,
              width: (1 / colorPalette.length * 100).toFixed(2) + '%',
              opacity: hoveredHex && hoveredHex !== color.hex ? 0.5 : 1
            }"
            :title="color.pantone_name ? color.pantone_name + ' / ' + color.hex : color.hex"
            @mouseenter="hoveredHex = color.hex"
            @click="selectColor(color.hex)"
          >
            <!-- 当前选中指示 -->
            <span class="strip-active-dot" v-if="selectedColor === color.hex"></span>
            <!-- Hover Tooltip -->
            <div class="strip-tooltip" v-if="hoveredHex === color.hex">
              <span class="tooltip-hex">{{ color.hex }}</span>
              <span class="tooltip-pantone" v-if="color.pantone_name">{{ color.pantone_name }}</span>
              <span class="tooltip-count" v-if="color.count > 0">{{ color.count }}&nbsp;case{{ color.count > 1 ? 's' : '' }}</span>
            </div>
          </div>
        </div>
        <button class="strip-clear-btn" v-if="selectedColor" @click="clearColorFilter">
          <el-icon><Close /></el-icon>{{ selectedColor }}
        </button>
      </div>
    </div>

    <!-- 全案规划师/设计师展示 -->
    <div class="designer-bar" v-if="featuredCase">
      <div class="designer-section" v-if="featuredCase.planner || featuredCase.designer">
        <div class="designer-item" v-if="featuredCase.planner" @click="showDesignerInfo(featuredCase.planner, 'planner')">
          <div class="designer-label">全案规划师</div>
          <div class="designer-name">{{ featuredCase.planner.name || '待分配' }}</div>
          <div class="designer-arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
        <div class="designer-divider" v-if="featuredCase.planner && featuredCase.designer"></div>
        <div class="designer-item" v-if="featuredCase.designer" @click="showDesignerInfo(featuredCase.designer, 'designer')">
          <div class="designer-label">全案设计师</div>
          <div class="designer-name">{{ featuredCase.designer.name || '待分配' }}</div>
          <div class="designer-arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </div>
      <div class="designer-placeholder" v-else>
        <span>专业团队为您量身定制</span>
      </div>
    </div>

    <!-- 第三层：配置方案展示（理想i8版本选择风格） -->
    <div class="section-title">
      <h2>精选配置方案</h2>
      <p>每个案例包含多种空间配置方案，满足不同需求</p>
    </div>

    <!-- 案例网格（蔚来卡片风格） -->
    <div class="case-grid">
      <div
        v-for="(caseItem, index) in cases"
        :key="caseItem.id"
        class="case-card"
        :class="{ large: index % 6 === 0 }"
        @click="goToDetail(caseItem.id)"
      >
        <div class="card-image-wrapper">
          <img 
            v-if="hasValidCoverImage(caseItem.cover_image)" 
            :src="caseItem.cover_image" 
            :alt="caseItem.title"
            loading="lazy"
          >
          <div v-else class="no-image" :style="{ background: getAtmosphereGradient(caseItem.atmosphere) }">
            <span>{{ getAtmosphereLabel(caseItem.atmosphere) }}</span>
          </div>
          
          <!-- 氛围标签 -->
          <div class="card-badge" v-if="caseItem.atmosphere">
            {{ getAtmosphereLabel(caseItem.atmosphere) }}
          </div>
          
          <!-- 悬浮信息层 -->
          <div class="card-overlay">
            <div class="card-info">
              <h3 class="card-title">{{ caseItem.title }}</h3>
              
              <!-- 参数化展示（理想i8风格） -->
              <div class="card-specs">
                <span class="spec">{{ caseItem.area }}㎡</span>
                <span class="spec">{{ caseItem.house_type }}</span>
                <span class="spec price">¥{{ formatPrice(caseItem.total_price) }}</span>
              </div>
              
              <!-- 色系卡片（蔚来配色风格） -->
              <div class="color-swatches" v-if="getCaseColorDots(caseItem).length > 0">
                <div
                  v-for="(hex, idx) in getCaseColorDots(caseItem)"
                  :key="idx"
                  class="swatch"
                  :style="{ backgroundColor: hex }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="!loading && cases.length > 0 && hasMore">
      <button class="load-more-btn" @click="loadMore" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '查看更多方案' }}
      </button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading && cases.length === 0" class="empty-state">
      <el-empty description="暂无符合条件的案例" />
    </div>

    <!-- 统一页脚 -->
    <Footer />

    <!-- 订阅弹窗 -->
    <el-dialog v-model="subscribeDialogVisible" title="订阅案例更新" width="400px">
      <div class="subscribe-dialog-content">
        <p>订阅「{{ currentCase?.title }}」后，案例更新时将通过微信通知您</p>
        <el-form :model="subscribeForm" label-position="top">
          <el-form-item label="手机号">
            <el-input v-model="subscribeForm.phone" placeholder="请输入手机号" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="subscribeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSubscribe" :loading="subscribing">确认订阅</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Bell, Plus, Minus, CaretBottom, Close, ArrowRight } from '@element-plus/icons-vue'
import { getPublicCases, getCaseFilters, subscribeCase, getWorkflowTimeline } from '@/api/case'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()

// 六大氛围分类（蔚来车型分类风格）
// key=前端唯一标识，label=显示文本，value=数据库存储值
const atmospheres = reactive([
  { key: 'warm',     label: '温馨', value: '温馨', count: 0 },
  { key: 'fresh',    label: '清新', value: '清新', count: 0 },
  { key: 'minimalist', label: '简约', value: '简约', count: 0 },
  { key: 'romantic', label: '浪漫', value: '浪漫', count: 0 },
  { key: 'elegant',  label: '雅致', value: '雅致', count: 0 },
  { key: 'steady',   label: '沉稳', value: '沉稳', count: 0 }
])

// 状态
const loading = ref(false)
const loadingMore = ref(false)
const cases = ref([])
const featuredCase = ref(null)
const total = ref(0)

// Hero 轮播相关
const heroImages = ref([])
const currentCarouselIndex = ref(0)
const carouselTransition = ref('fade')
const carouselTimer = ref(null)
const transitions = ['fade', 'slide-left', 'slide-right', 'zoom', 'wipe']

// 服务流程步骤（杂志左侧目录）
const processSteps = [
  { name: '转化签约', key: 'conversion' },
  { name: '前期准备', key: 'preparation' },
  { name: '硬装施工', key: 'construction' },
  { name: '软装服务', key: 'soft_service' },
  { name: '售后服务', key: 'after_sales' }
]
const currentProcessStep = ref(0)

// 计算当前显示的 Hero 图片
const currentHeroImage = computed(() => {
  return heroImages.value[currentCarouselIndex.value] || featuredCase.value?.cover_image
})

// 服务流程阶段筛选（与数据库 workflow_phase_config 保持一致）
// 6个阶段全部展示，名称和数量均来自后端
const workflowPhases = ref([
  { key: 'acquisition',   label: '获客沉淀阶段', count: 0, code: 'acquisition' },
  { key: 'conversion',    label: '转化签约阶段', count: 0, code: 'conversion' },
  { key: 'preparation',   label: '前期准备阶段', count: 0, code: 'preparation' },
  { key: 'construction',  label: '硬装施工阶段', count: 0, code: 'construction' },
  { key: 'soft_service',  label: '软装服务阶段', count: 0, code: 'soft_service' },
  { key: 'after_sales',   label: '售后服务阶段', count: 0, code: 'after_sales' }
])
const selectedWorkflowPhase = ref('')
const expandedPhase = ref('')        // 当前展开的阶段 key
const phaseNodes = ref({})           // { phase_key: [...] }
const loadingNodes = ref(false)

// 选择服务流程阶段筛选
const selectWorkflowPhase = (key) => {
  if (selectedWorkflowPhase.value === key) {
    selectedWorkflowPhase.value = ''
  } else {
    selectedWorkflowPhase.value = key
    if (key && !phaseNodes.value[key]) {
      fetchPhaseNodes(key)
    }
  }
  pagination.page = 1
  cases.value = []
  fetchCases()
}

// 切换阶段展开状态
const togglePhaseExpand = async (phase) => {
  if (expandedPhase.value === phase.key) {
    expandedPhase.value = ''
  } else {
    expandedPhase.value = phase.key
    selectedWorkflowPhase.value = phase.key
    if (!phaseNodes.value[phase.key]) {
      await fetchPhaseNodes(phase.key)
    }
    pagination.page = 1
    cases.value = []
    fetchCases()
  }
}

// 选择节点（筛选该节点对应的案例）
const selectedNodeId = ref(null)
const selectNode = (node) => {
  if (selectedNodeId.value === node.id) {
    selectedNodeId.value = null
  } else {
    selectedNodeId.value = node.id
  }
  pagination.page = 1
  cases.value = []
  fetchCases()
}

// 清除工作流筛选
const clearWorkflowFilter = () => {
  selectedWorkflowPhase.value = ''
  selectedNodeId.value = null
  expandedPhase.value = ''
  pagination.page = 1
  cases.value = []
  fetchCases()
}

// 获取阶段短标签
const getPhaseShortLabel = (phase) => {
  const map = { 'acquisition': '获客', 'conversion': '签约', 'preparation': '设计', 'construction': '施工', 'soft_service': '软装', 'after_sales': '售后' }
  return map[phase] || phase
}

// 加载阶段节点数据（从已加载案例的 workflow_progress 获取当前节点名称）
const fetchPhaseNodes = async (targetPhaseKey) => {
  if (loadingNodes.value) return
  loadingNodes.value = true
  try {
    const targetPhase = workflowPhases.value.find(p => p.key === targetPhaseKey)
    if (!targetPhase) { loadingNodes.value = false; return }
    const phaseCode = targetPhase.code || targetPhaseKey

    // 直接从 cases.value 提取各案例的当前进行中节点
    const allNodes = []
    const seen = new Set()
    for (const c of cases.value) {
      if (!c.is_real_case) continue
      const wp = c.workflow_progress
      if (!wp) continue
      const curPhase = wp.current_phase
      if (curPhase !== phaseCode) continue
      const ongoingNames = wp.ongoing_node_names || []
      for (const nodeName of ongoingNames) {
        if (!seen.has(nodeName)) {
          seen.add(nodeName)
          allNodes.push({
            id: nodeName,
            node_name: nodeName,
            phase: curPhase,
            caseId: c.id,
            caseTitle: c.title
          })
        }
      }
    }

    phaseNodes.value[targetPhaseKey] = allNodes
    if (targetPhase) targetPhase._nodes = allNodes
  } catch (e) {
    console.error('加载节点失败', e)
  } finally {
    loadingNodes.value = false
  }
}

// 筛选条件
const filters = reactive({
  atmosphere: '',
  color: ''
})

// 颜色筛选（色条模式）
const colorPalette = ref([])  // [{hex, pantone_name, pantone_code, count}]
const selectedColor = ref('')  // hex string
const hoveredHex = ref(null)

const selectColor = (hex) => {
  selectedColor.value = selectedColor.value === hex ? '' : hex
  filters.color = selectedColor.value
  pagination.page = 1
  hasMore.value = true
  fetchCases()
}

const clearColorFilter = () => {
  selectedColor.value = ''
  filters.color = ''
  pagination.page = 1
  hasMore.value = true
  fetchCases()
}

// 分页
const pagination = reactive({
  page: 1,
  page_size: 12
})

// 是否还有更多
const hasMore = ref(true)

// 订阅弹窗
const subscribeDialogVisible = ref(false)
const currentCase = ref(null)
const subscribing = ref(false)
const subscribeForm = reactive({
  phone: ''
})



// 获取筛选选项
const fetchFilterOptions = async () => {
  try {
    const res = await getCaseFilters()
    if (res.atmospheres) {
      atmospheres.forEach(atm => {
        const found = res.atmospheres.find(a => a.key === atm.value)
        if (found) atm.count = found.count || 0
      })
    }
    // 服务流程阶段计数（从后端 progress_options 映射到6个阶段）
    // 后端返回: real_case, designing(acq+conv+prep), construction, soft_service, after_sales
    // 前端需要拆分 designing 为 acquisition/conversion/preparation 三个独立计数
    if (res.progress_options) {
      const optMap = {}
      res.progress_options.forEach(opt => { optMap[opt.key] = opt.count || 0 })
      
      // 直接使用后端返回的各阶段计数
      // designing 是 acquisition+conversion+preparation 的合计，需按比例或查实际数据拆分
      // 更好的方式：后端直接返回6个阶段的独立计数
      workflowPhases.value.forEach(p => {
        if (p.key === 'acquisition') p.count = optMap['acquisition_count'] || 0
        else if (p.key === 'conversion') p.count = optMap['conversion_count'] || 0
        else if (p.key === 'preparation') p.count = optMap['preparation_count'] || 0
        else if (p.key === 'construction') p.count = optMap['construction'] || 0
        else if (p.key === 'soft_service') p.count = optMap['soft_service'] || 0
        else if (p.key === 'after_sales') p.count = optMap['after_sales'] || 0
      })
    }
  } catch (error) {
    console.error('获取筛选选项失败:', error)
  }
}

// 选择氛围
const selectAtmosphere = (key) => {
  // 切换氛围：传入key，找到对应的value（数据库存储的中文值）
  const atm = atmospheres.find(a => a.key === key)
  const newAtm = atm ? atm.value : ''
  filters.atmosphere = filters.atmosphere === newAtm ? '' : newAtm
  pagination.page = 1
  featuredCase.value = null // 清除精选案例
  fetchCases()
}

// 获取氛围标签（数据库存的是中文值，如'温馨'）
const getAtmosphereLabel = (value) => {
  const atm = atmospheres.find(a => a.value === value)
  return atm ? atm.label : value
}

// 从4组颜色字段提取色点
const getCaseColorDots = (caseItem) => {
  const dots = []
  const fields = ['main_colors', 'auxiliary_colors', 'accent_colors', 'background_colors']
  for (const field of fields) {
    try {
      let val = caseItem[field]
      if (!val) continue
      if (typeof val === 'string') val = JSON.parse(val)
      if (Array.isArray(val) && val.length > 0 && val[0]) {
        dots.push(typeof val[0] === 'object' ? val[0].hex : val[0])
      } else if (typeof val === 'object' && !Array.isArray(val) && val.hex) {
        dots.push(val.hex)
      }
    } catch {}
  }
  return dots
}

// 获取氛围色渐变（封面图不存在时的 fallback）
const getAtmosphereGradient = (atmosphere) => {
  const gradients = {
    '温馨': 'linear-gradient(135deg, #f5e6d3 0%, #d4a574 100%)',
    '清新': 'linear-gradient(135deg, #e8f5e9 0%, #81c784 100%)',
    '简约': 'linear-gradient(135deg, #f5f5f5 0%, #9e9e9e 100%)',
    '浪漫': 'linear-gradient(135deg, #fce4ec 0%, #f48fb1 100%)',
    '雅致': 'linear-gradient(135deg, #e8eaf6 0%, #7986cb 100%)',
    '沉稳': 'linear-gradient(135deg, #37474f 0%, #546e7a 100%)'
  }
  return gradients[atmosphere] || 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)'
}

// 检查图片 URL 是否有效（简单判断）
const handleImageError = (event, atmosphere) => {
  event.target.style.display = 'none'
  event.target.nextElementSibling && (event.target.nextElementSibling.style.display = 'block')
}
const hasValidCoverImage = (coverImage) => {
  return coverImage && coverImage.length > 0 && !coverImage.includes('null') && !coverImage.includes('undefined')
}

// 获取案例列表
const fetchCases = async (isLoadMore = false) => {
  if (isLoadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    // 服务流程阶段筛选参数（直接传阶段code给后端）
    if (selectedWorkflowPhase.value) {
      const targetPhase = workflowPhases.value.find(p => p.key === selectedWorkflowPhase.value)
      // 后端 progress 参数: acquisition/conversion/preparation/construction/soft_service/after_sales
      params.progress = selectedWorkflowPhase.value
    }
    const res = await getPublicCases(params)
    
    // DEBUG: expose to window for console inspection

    
    const items = res?.items || []
    
    if (isLoadMore) {
      cases.value = [...cases.value, ...items]
    } else {
      cases.value = items
      // 设置精选案例（第一个案例）
      if (items.length > 0 && !featuredCase.value) {
        featuredCase.value = items[0]
        updateHeroImages(items[0])
      }
    }
    
    total.value = res?.total || 0
    hasMore.value = cases.value.length < total.value
  } catch (error) {
    console.error('获取案例列表失败:', error)
    debugError.value = { message: error.message, stack: error.stack }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多
const loadMore = () => {
  pagination.page++
  fetchCases(true)
}

// 跳转到详情
const goToDetail = (id) => {
  router.push(`/cases/${id}`)
}

// 处理订阅
const handleSubscribe = (caseItem) => {
  if (caseItem.is_subscribed) {
    ElMessage.info('您已订阅该案例')
    return
  }
  currentCase.value = caseItem
  subscribeForm.phone = ''
  subscribeDialogVisible.value = true
}

// 显示设计师/规划师简介
const showDesignerInfo = (designer, type) => {
  if (!designer || !designer.id) {
    ElMessage.info(`${type === 'planner' ? '规划师' : '设计师'}信息待完善`)
    return
  }
  // 跳转到人员详情页或打开弹窗
  router.push(`/team/${designer.id}`)
}

// 提交订阅
const submitSubscribe = async () => {
  if (!subscribeForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  
  subscribing.value = true
  try {
    await subscribeCase(currentCase.value.id, { phone: subscribeForm.phone })
    ElMessage.success('订阅成功')
    currentCase.value.is_subscribed = true
    currentCase.value.subscription_count++
    subscribeDialogVisible.value = false
  } catch (error) {
    console.error('订阅失败:', error)
    ElMessage.error('订阅失败')
  } finally {
    subscribing.value = false
  }
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0'
  const num = parseFloat(price)
  if (num >= 10000) {
    return (num / 10000).toFixed(1)
  }
  return num.toLocaleString()
}

// Hero 轮播方法
const startCarousel = () => {
  stopCarousel()
  if (heroImages.value.length <= 1) return
  carouselTimer.value = setInterval(() => {
    nextSlide()
  }, 3000)
}

const stopCarousel = () => {
  if (carouselTimer.value) {
    clearInterval(carouselTimer.value)
    carouselTimer.value = null
  }
}

const nextSlide = () => {
  // 随机选择过场效果
  carouselTransition.value = transitions[Math.floor(Math.random() * transitions.length)]
  currentCarouselIndex.value = (currentCarouselIndex.value + 1) % heroImages.value.length
}

const goToSlide = (idx) => {
  if (idx === currentCarouselIndex.value) return
  carouselTransition.value = transitions[Math.floor(Math.random() * transitions.length)]
  currentCarouselIndex.value = idx
  // 重置计时器
  startCarousel()
}

// 更新 Hero 图片列表
const updateHeroImages = (caseItem) => {
  const images = []
  // 主图
  if (caseItem.cover_image && hasValidCoverImage(caseItem.cover_image)) {
    images.push(caseItem.cover_image)
  }
  // 辅助图（最多再加4张）
  if (caseItem.gallery && Array.isArray(caseItem.gallery)) {
    caseItem.gallery.slice(0, 4).forEach(img => {
      if (img && !images.includes(img)) images.push(img)
    })
  }
  heroImages.value = images
  currentCarouselIndex.value = 0
  startCarousel()
}

onMounted(() => {
  fetchFilterOptions()
  fetchCases()
  loadColorGroups()
})

// 加载颜色索引（暖色→冷色→灰度排序色条）
const loadColorGroups = async () => {
  try {
    const res = await fetch('/api/v3/color-index').then(r => r.json())
    const d = (res.data || res || {})
    const colors = Array.isArray(d) ? d : (d.colors || [])
    colorPalette.value = colors
  } catch (e) {
    console.error('loadColorGroups error:', e)
  }
}

onUnmounted(() => {
  stopCarousel()
})
</script>

<style scoped>
/* 蔚来风格 - 极简、大留白、沉浸式 */
.case-list-page {
  min-height: 100vh;
  background: #fff;
  padding-top: 80px;
}


/* 全案规划师/设计师展示栏 */
.designer-bar {
  display: flex;
  justify-content: center;
  padding: 32px 60px;
  background: #fafafa;
}

.designer-section {
  display: flex;
  align-items: center;
  gap: 0;
  background: #fff;
  padding: 16px 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.designer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  border-radius: 8px;
}

.designer-item:hover {
  background: #f8f8f8;
}

.designer-label {
  font-size: 12px;
  color: #999;
  letter-spacing: 1px;
}

.designer-name {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 500;
  letter-spacing: 1px;
}

.designer-arrow {
  color: #ccc;
  transition: color 0.2s;
}

.designer-item:hover .designer-arrow {
  color: #666;
}

.designer-divider {
  width: 1px;
  height: 40px;
  background: #e8e8e8;
  margin: 0 8px;
}

/* 第二层：服务流程阶段横向筛选按钮 */
.workflow-phase-filter-bar {
  background: #fafafa;
  padding: 20px 60px;
  border-bottom: 1px solid #f0f0f0;
}

.phase-filter-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.phase-filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1.5px solid #e0e0e0;
  border-radius: 24px;
  background: #fff;
  color: #555;
  font-size: 14px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}

.phase-filter-btn:hover {
  border-color: #c8a97a;
  color: #1a1a1a;
  background: #fffbf5;
}

.phase-filter-btn.active {
  border-color: #c8a97a;
  background: #c8a97a;
  color: #fff;
}

.phase-filter-btn.expanded {
  border-color: #c8a97a;
  box-shadow: 0 2px 8px rgba(200, 169, 122, 0.3);
}

.phase-dot.breathing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #52c41a;
  flex-shrink: 0;
  animation: breathe-green 2s ease-in-out infinite;
}

.phase-filter-btn.active .phase-dot.breathing-dot {
  background: #fff;
}

.phase-name { font-weight: 500; }
.phase-count { font-size: 12px; opacity: 0.75; }
.phase-arrow { transition: transform 0.2s ease; font-size: 12px; }
.phase-arrow.rotated { transform: rotate(180deg); }

.phase-clear-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 10px 16px;
  border: 1px dashed #ccc;
  border-radius: 24px;
  background: transparent;
  color: #999;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.phase-clear-btn:hover { border-color: #999; color: #666; }

/* 节点列表展开面板（横向滚动） */
.phase-nodes-panel {
  margin-top: 16px;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 12px 20px;
  max-height: 120px;
}

.nodes-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
}
.nodes-scroll::-webkit-scrollbar { height: 4px; }
.nodes-scroll::-webkit-scrollbar-thumb { background: #ddd; border-radius: 2px; }

.node-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid #eee;
  border-radius: 16px;
  background: #fafafa;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  max-width: 200px;
  overflow: hidden;
}
.node-chip:hover { border-color: #c8a97a; background: #fffbf5; color: #1a1a1a; }
.node-chip.selected { border-color: #c8a97a; background: #c8a97a; color: #fff; }
.node-phase-tag { font-size: 11px; background: #eee; padding: 1px 6px; border-radius: 8px; flex-shrink: 0; }
.node-chip.selected .node-phase-tag { background: rgba(255,255,255,0.3); }
.node-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; }
.node-case { font-size: 11px; color: #999; overflow: hidden; text-overflow: ellipsis; }
.node-chip.selected .node-case { color: rgba(255,255,255,0.8); }

.phase-nodes-loading, .phase-nodes-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  min-height: 48px;
}
.loading-text { animation: pulse 1.5s ease-in-out infinite; }

/* slide-down transition */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; max-height: 0; margin-top: 0; padding-top: 0; padding-bottom: 0; }
.slide-down-enter-to, .slide-down-leave-from { opacity: 1; max-height: 200px; }

@keyframes breathe-green {
  0%, 100% { box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.4); }
  50% { box-shadow: 0 0 0 5px rgba(82, 196, 26, 0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 第一层：氛围Tab（蔚来车型Tab风格） */
.atmosphere-tabs {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 40px 60px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.tab-item:hover {
  color: #1a1a1a;
  background: #f8f8f8;
}

.tab-item.active {
  color: #1a1a1a;
  font-weight: 500;
  background: #f5f5f5;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 2px;
  background: #1a1a1a;
}

.tab-label {
  letter-spacing: 2px;
}

.tab-count {
  font-size: 12px;
  color: #999;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 第二层：英雄区（杂志封面风格） */
.hero-section {
  position: relative;
  height: 100vh;
  min-height: 700px;
  overflow: hidden;
  margin-bottom: 0;
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-slide {
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
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.35) 40%, rgba(0,0,0,0.15) 70%, transparent 100%);
}

/* 轮播指示器 */
.carousel-indicators {
  position: absolute;
  bottom: 180px;
  right: 60px;
  display: flex;
  gap: 12px;
  z-index: 10;
}

.indicator {
  width: 32px;
  height: 3px;
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: #fff;
  width: 48px;
}

.indicator:hover {
  background: rgba(255,255,255,0.6);
}

/* 轉播过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.6s ease;
}
.slide-left-enter-from {
  transform: translateX(100%);
}
.slide-left-leave-to {
  transform: translateX(-100%);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.6s ease;
}
.slide-right-enter-from {
  transform: translateX(-100%);
}
.slide-right-leave-to {
  transform: translateX(100%);
}

.zoom-enter-active,
.zoom-leave-active {
  transition: all 0.6s ease;
}
.zoom-enter-from {
  transform: scale(1.1);
  opacity: 0;
}
.zoom-leave-to {
  transform: scale(0.9);
  opacity: 0;
}

.wipe-enter-active,
.wipe-leave-active {
  transition: all 0.7s ease;
}
.wipe-enter-from {
  clip-path: inset(0 100% 0 0);
}
.wipe-leave-to {
  clip-path: inset(0 0 0 100%);
}

/* 杂志风格覆盖层 */
.hero-magazine-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: auto 1fr auto;
  padding: 60px;
  color: #fff;
}

/* 品牌标识 - 杂志标题风格（DESIGNARY 艺术粗体） */
.brand-mark {
  position: absolute;
  top: 60px;
  left: 60px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.brand-en {
  font-family: 'Trebuchet MS', 'Arial Black', Impact, sans-serif;
  font-size: 96px;
  font-weight: 900;
  letter-spacing: 8px;
  color: #fff;
  text-shadow: 0 2px 30px rgba(0,0,0,0.6);
  line-height: 0.9;
}

.brand-cn {
  font-size: 16px;
  font-weight: 400;
  letter-spacing: 6px;
  color: rgba(255,255,255,0.9);
}

/* 左侧服务流程目录 */
.service-team-sidebar {
  grid-column: 1;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 80px;
}

.team-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 4px;
  color: rgba(255,255,255,0.5);
  margin-bottom: 24px;
}

.team-members {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.team-member {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.member-role {
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.5);
}

.member-name {
  font-size: 16px;
  font-weight: 400;
  color: #fff;
  letter-spacing: 1px;
}

.member-role {
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.5);
}

.member-name {
  font-size: 16px;
  font-weight: 400;
  color: #fff;
  letter-spacing: 1px;
}

/* 右侧核心信息区 - 深灰色半透明蒙版 */
.hero-content {
  grid-column: 2;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-end;
  text-align: right;
  padding: 40px 60px;
  max-width: 600px;
  margin-left: auto;
  background: rgba(30, 30, 30, 0.65);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
}

.hero-badge {
  display: inline-block;
  padding: 8px 24px;
  background: rgba(255,255,255,0.15);
  border-radius: 24px;
  font-size: 48px;
  font-weight: 300;
  letter-spacing: 6px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

.hero-title {
  font-size: 52px;
  font-weight: 300;
  margin-bottom: 12px;
  letter-spacing: 3px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 16px;
  font-weight: 300;
  letter-spacing: 2px;
  opacity: 0.85;
  margin-bottom: 32px;
}

/* 数字参数展示 */
.hero-specs {
  display: flex;
  align-items: center;
  gap: 24px;
  justify-content: flex-end;
}

.spec-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.spec-value {
  font-size: 36px;
  font-weight: 200;
  letter-spacing: 1px;
  line-height: 1;
}

.spec-unit {
  font-size: 14px;
  opacity: 0.7;
}

.spec-divider {
  width: 1px;
  height: 32px;
  background: rgba(255,255,255,0.25);
}

/* 底部 VR 二维码 + 按钮 */
.hero-footer {
  grid-column: 1 / -1;
  grid-row: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 40px;
}

.vr-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.vr-qrcode {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: #fff;
  padding: 8px;
}

.vr-label {
  font-size: 13px;
  color: rgba(255,255,255,0.7);
  letter-spacing: 1px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn-primary {
  padding: 16px 48px;
  background: #fff;
  color: #1a1a1a;
  border: none;
  font-size: 16px;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  font-size: 16px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.25);
}

/* 颜色筛选色条 */
.color-strip-bar {
  background: #fafafa;
  padding: 20px 60px;
  border-bottom: 1px solid #f0f0f0;
}

.color-strip-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.strip-label {
  font-size: 13px;
  color: #888;
  letter-spacing: 3px;
  flex-shrink: 0;
  width: 36px;
}

.color-strip-track {
  flex: 1;
  height: 40px;
  display: flex;
  border-radius: 6px;
  overflow: visible;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.color-strip-cell {
  position: relative;
  height: 100%;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  border-right: 1px solid rgba(255,255,255,0.3);
  flex-shrink: 0;
}

.color-strip-cell:hover {
  transform: scaleY(1.12);
  box-shadow: 0 0 0 2px rgba(0,0,0,0.2);
  z-index: 2;
}

.color-strip-cell:last-child {
  border-right: none;
}

.strip-active-dot {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5);
  z-index: 3;
}

/* Hover Tooltip */
.strip-tooltip {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30,30,30,0.92);
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 100;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.strip-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: rgba(30,30,30,0.92);
}

.tooltip-hex {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.tooltip-pantone {
  font-size: 12px;
  color: rgba(255,255,255,0.75);
}

.tooltip-count {
  font-size: 11px;
  color: rgba(255,255,255,0.55);
  margin-top: 2px;
}

.strip-clear-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border: 1px dashed #c8a97a;
  border-radius: 20px;
  background: rgba(200,169,122,0.06);
  color: #8B5A2B;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.strip-clear-btn:hover {
  background: rgba(200,169,122,0.15);
}

/* 第三层：配置方案展示 */
.section-title {
  text-align: center;
  padding: 80px 60px 40px;
}

.section-title h2 {
  font-size: 36px;
  font-weight: 300;
  letter-spacing: 4px;
  margin-bottom: 16px;
  color: #1a1a1a;
}

.section-title p {
  font-size: 16px;
  color: #999;
  letter-spacing: 2px;
}

/* 案例网格（蔚来卡片风格） */
.case-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  padding: 0 60px 80px;
  background: #f5f5f5;
}

.case-card {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  cursor: pointer;
  background: #fff;
}

.case-card.large {
  grid-column: span 2;
  grid-row: span 2;
  aspect-ratio: auto;
}

.card-image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.card-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.case-card:hover .card-image-wrapper img {
  transform: scale(1.05);
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
  font-size: 14px;
  background: #f8f8f8;
}

.card-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.95);
  font-size: 13px;
  color: #1a1a1a;
  letter-spacing: 2px;
  z-index: 3;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.3) 50%, transparent 100%);
  display: flex;
  align-items: flex-end;
  padding: 32px;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.case-card:hover .card-overlay {
  opacity: 1;
}

.card-info {
  color: #fff;
  width: 100%;
}

.card-title {
  font-size: 20px;
  font-weight: 400;
  margin-bottom: 12px;
  letter-spacing: 2px;
}

/* 参数化展示（理想i8风格） */
.card-specs {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.card-specs .spec {
  font-size: 14px;
  opacity: 0.9;
  letter-spacing: 1px;
}

.card-specs .spec.price {
  color: #f5a623;
  font-weight: 500;
}

/* 色系卡片（蔚来配色风格） */
.color-swatches {
  display: flex;
  gap: 8px;
  align-items: center;
}

.swatch {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.5);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.swatch:hover {
  transform: scale(1.1);
}

.more-colors {
  font-size: 12px;
  opacity: 0.7;
}

/* 加载更多 */
.load-more {
  padding: 80px;
  text-align: center;
  background: #fff;
}

.load-more-btn {
  background: transparent;
  border: 1px solid #1a1a1a;
  color: #1a1a1a;
  padding: 16px 56px;
  font-size: 14px;
  letter-spacing: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover {
  background: #1a1a1a;
  color: #fff;
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 空状态 */
.empty-state {
  padding: 120px 60px;
  background: #fff;
}

/* 响应式 */
@media (max-width: 1200px) {
  .case-grid {
    grid-template-columns: repeat(2, 1fr);
    padding: 0 24px 60px;
  }
  
  .case-card.large {
    grid-column: span 2;
    grid-row: span 1;
    aspect-ratio: 4/3;
  }
  
  .hero-magazine-overlay {
    grid-template-columns: 200px 1fr;
    padding: 40px;
  }
  
  .brand-mark {
    top: 40px;
    left: 40px;
  }
  
  .brand-en {
    font-size: 64px;
    letter-spacing: 6px;
  }
  
  .brand-cn {
    font-size: 14px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-content {
    padding-right: 40px;
  }
  
  .carousel-indicators {
    right: 40px;
    bottom: 120px;
  }
  
  .atmosphere-tabs {
    gap: 16px;
    padding: 24px;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .case-list-page {
    padding-top: 64px;
  }
  
  .hero-section {
    height: 100vh;
    min-height: 600px;
  }
  
  .hero-magazine-overlay {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto auto;
    padding: 24px;
  }
  
  .brand-mark {
    top: 24px;
    left: 24px;
  }
  
  .brand-en {
    font-size: 48px;
    letter-spacing: 4px;
  }
  
  .brand-cn {
    font-size: 12px;
  }
  
  .service-team-sidebar {
    grid-column: 1;
    grid-row: 4;
    padding-top: 20px;
    justify-content: flex-start;
  }
  
  .team-members {
    flex-direction: row;
    gap: 16px;
    flex-wrap: wrap;
  }
  
  .team-member {
    opacity: 1;
  }
  
  .member-role {
    font-size: 10px;
  }
  
  .member-name {
    font-size: 13px;
  }
  
  .hero-content {
    grid-column: 1;
    grid-row: 2;
    align-items: flex-start;
    text-align: left;
    padding: 24px;
    max-width: 100%;
    background: rgba(30, 30, 30, 0.7);
  }
  
  .hero-title {
    font-size: 28px;
    letter-spacing: 2px;
  }
  
  .hero-subtitle {
    font-size: 14px;
  }
  
  .hero-specs {
    gap: 12px;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .spec-value {
    font-size: 24px;
  }
  
  .hero-footer {
    grid-column: 1;
    grid-row: 3;
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .vr-section {
    order: 2;
  }
  
  .vr-qrcode {
    width: 60px;
    height: 60px;
  }
  
  .hero-actions {
    order: 1;
    flex-direction: row;
    width: 100%;
  }
  
  .btn-primary,
  .btn-secondary {
    width: auto;
    min-width: 120px;
  }
  
  .carousel-indicators {
    right: 24px;
    bottom: 24px;
  }
  
  .case-grid {
    grid-template-columns: 1fr;
    padding: 0 16px 40px;
  }
  
  .case-card.large {
    grid-column: span 1;
    aspect-ratio: 4/3;
  }
  
  .card-overlay {
    opacity: 1;
    padding: 20px;
  }
  
  .atmosphere-tabs {
    justify-content: flex-start;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .tab-item {
    white-space: nowrap;
  }
}
</style>
