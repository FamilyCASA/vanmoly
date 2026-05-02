<template>
  <div class="product-page">
    <Navbar />

    <!-- ===== HERO ===== -->
    <section class="hero">
      <div class="hero-text">
        <p class="hero-eyebrow">D&B 帝标|设记家 · 产品中心</p>
        <h1 class="hero-title">装修不用再为<br>"踩坑"焦虑</h1>
        <div class="hero-value-points">
          <div class="value-point">
            <span class="vp-icon">🔍</span>
            <div class="vp-content">
              <strong>怕套路？</strong>
              <span>每款产品都有「身份证」，来源、规格、价格全透明</span>
            </div>
          </div>
          <div class="value-point">
            <span class="vp-icon">🎯</span>
            <div class="vp-content">
              <strong>怕翻车？</strong>
              <span>全案团队全程跟进，从设计到落地，还原度看得见</span>
            </div>
          </div>
          <div class="value-point">
            <span class="vp-icon">🛒</span>
            <div class="vp-content">
              <strong>想省心？</strong>
              <span>{{ total }} 款精选产品覆盖全屋，一站式配齐</span>
            </div>
          </div>
        </div>
        <div class="hero-actions">
          <button class="btn-primary" @click="scrollToProducts">开始选品</button>
          <button class="btn-ghost" @click="$router.push('/cases')">看看案例</button>
        </div>
      </div>
      <div class="hero-visual">
        <img src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200&q=80" alt="家居" />
      </div>
    </section>

    <!-- ===== 分类导航（树状结构） ===== -->
    <div class="cat-bar" :class="{ sticky: catSticky, expanded: catExpanded }" ref="catBarRef">
      <div class="cat-inner tree-cat-inner">
        <!-- 全部 -->
        <button
          class="cat-btn"
          :class="{ active: filters.category_id === null }"
          @click="selectCat(null)"
        >全部</button>

        <!-- 树状分类：只展示有前台展示物料的分类 -->
        <template v-for="cat in visibleCategoryTree" :key="cat.id">
          <!-- 父分类 -->
          <button
            class="cat-btn cat-parent"
            :class="{ active: filters.category_id === cat.id, 'has-children': cat.children?.length }"
            @click="selectCat(cat.id)"
          >{{ cat.name }}</button>
          <!-- 子分类（自动展开） -->
          <template v-if="cat.children?.length">
            <button
              v-for="child in cat.children"
              :key="child.id"
              class="cat-btn cat-child"
              :class="{ active: filters.category_id === child.id }"
              @click="selectCat(child.id)"
            >{{ child.name }}</button>
          </template>
        </template>
      </div>
      <button v-if="showMoreBtn" class="cat-more-btn" @click="catExpanded = !catExpanded">
        {{ catExpanded ? '收起' : '更多' }}
        <span class="more-arrow" :class="{ up: catExpanded }">▼</span>
      </button>
    </div>

    <!-- ===== 产品网格 ===== -->
    <main class="products-wrap" ref="productsRef">
      <!-- 骨架屏 -->
      <div v-if="loading" class="product-grid">
        <div v-for="i in 12" :key="i" class="product-card skeleton">
          <div class="card-img skeleton-img"></div>
          <div class="card-body">
            <div class="skeleton-line w80"></div>
            <div class="skeleton-line w50"></div>
          </div>
        </div>
      </div>

      <!-- 产品列表 -->
      <div v-else class="product-grid">
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ 'in-selection': isInSelection(product.id) }"
          @click="openCustomize(product)"
        >
          <!-- 图片区 -->
          <div class="card-img-wrap">
            <img
              v-if="product.main_image"
              :src="getImageUrl(product.main_image)"
              :alt="product.name"
              class="card-img"
              loading="lazy"
            />
            <div v-else class="card-img-placeholder">
              <img src="/images/default-product.jpg" alt="默认图片" class="card-img default-img" />
            </div>
            <!-- 已选标记 -->
            <div v-if="isInSelection(product.id)" class="selected-mark">
              <span>✓ 已选</span>
            </div>
            <!-- 悬停操作 -->
            <div class="card-hover-actions">
              <button class="hover-btn" @click.stop="quickAdd(product)">
                {{ isInSelection(product.id) ? '再加一件' : '+ 加入选品' }}
              </button>
            </div>
          </div>
          <!-- 信息区 -->
          <div class="card-body">
            <p class="card-brand">{{ product.brand || 'D&B 帝标|设记家' }}</p>
            <h3 class="card-name">{{ product.name }}</h3>
            <div class="card-footer">
              <span class="card-price">¥{{ formatPrice(product.sale_price) }}</span>
              <span class="card-unit">/ {{ product.unit || '件' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="!loading && hasMore" class="load-more-wrap">
        <button class="load-more-btn" :disabled="loadingMore" @click="loadMore">
          {{ loadingMore ? '加载中…' : '加载更多产品' }}
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && products.length === 0" class="empty">
        <p>暂无产品</p>
      </div>
    </main>

    <!-- ===== 深度定制抽屉 ===== -->
    <transition name="drawer-slide">
      <div v-if="drawer.visible" class="drawer-mask" @click.self="closeDrawer">
        <div class="drawer">
          <!-- 关闭 -->
          <button class="drawer-close" @click="closeDrawer">✕</button>

          <div class="drawer-scroll">
            <!-- 产品主图 + 快速加入（顶部固定） -->
            <div class="drawer-hero">
              <img
                v-if="drawer.product?.main_image"
                :src="getImageUrl(drawer.product.main_image)"
                :alt="drawer.product?.name"
                class="drawer-main-img"
              />
              <div v-else class="drawer-img-placeholder"><img src="/images/default-product.jpg" alt="默认图片" style="width:100%;height:100%;object-fit:cover" /></div>
              <!-- 基本信息浮在图片上 -->
              <div class="drawer-info-overlay">
                <p class="drawer-brand">{{ drawer.product?.brand || 'D&B 帝标|设记家' }}</p>
                <h2 class="drawer-name">{{ drawer.product?.name }}</h2>
              </div>
              <!-- 快速加入按钮浮在图片底部 -->
              <button class="drawer-quick-add" @click="confirmAdd">
                {{ isInSelection(drawer.product?.id) ? '✓ 再加一件' : '+ 加入选品单' }}
              </button>
            </div>

            <!-- 基本信息（非图片模式） -->
            <div class="drawer-info">
              <p class="drawer-spec" v-if="drawer.product?.specification">{{ drawer.product.specification }}</p>
            </div>

            <!-- 变体选择 -->
            <div class="drawer-section" v-if="drawer.variants.length > 0">
              <h4 class="section-title">选择规格</h4>
              <div class="variant-grid">
                <button
                  v-for="v in drawer.variants"
                  :key="v.id"
                  class="variant-btn"
                  :class="{ active: drawer.selectedVariant?.id === v.id }"
                  @click="selectVariant(v)"
                >
                  <span class="v-name">{{ v.name }}</span>
                  <span class="v-price" v-if="v.price_delta !== 0">
                    {{ v.price_delta > 0 ? '+' : '' }}¥{{ v.price_delta }}
                  </span>
                </button>
              </div>
            </div>

            <!-- 定制选项 -->
            <div class="drawer-section" v-if="drawer.customOptions.length > 0">
              <h4 class="section-title">定制选项</h4>
              <div
                v-for="opt in drawer.customOptions"
                :key="opt.key"
                class="custom-option"
              >
                <label class="opt-label">{{ opt.label }}</label>
                <!-- 颜色选择 -->
                <div v-if="opt.type === 'color'" class="color-picker">
                  <button
                    v-for="c in opt.choices"
                    :key="c.value"
                    class="color-dot"
                    :class="{ active: drawer.customValues[opt.key] === c.value }"
                    :style="{ background: c.hex }"
                    :title="c.label"
                    @click="setCustomValue(opt.key, c.value, c.price_delta || 0)"
                  ></button>
                </div>
                <!-- 尺寸/材质选择 -->
                <div v-else-if="opt.type === 'select'" class="opt-chips">
                  <button
                    v-for="c in opt.choices"
                    :key="c.value"
                    class="opt-chip"
                    :class="{ active: drawer.customValues[opt.key] === c.value }"
                    @click="setCustomValue(opt.key, c.value, c.price_delta || 0)"
                  >
                    {{ c.label }}
                    <span v-if="c.price_delta" class="chip-delta">
                      {{ c.price_delta > 0 ? '+' : '' }}¥{{ c.price_delta }}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 配件推荐 -->
            <div class="drawer-section" v-if="drawer.accessories.length > 0">
              <h4 class="section-title">搭配配件</h4>
              <div class="accessory-list">
                <div
                  v-for="acc in drawer.accessories"
                  :key="acc.id"
                  class="accessory-item"
                  :class="{ selected: drawer.selectedAccessories.includes(acc.id) }"
                  @click="toggleAccessory(acc)"
                >
                  <img v-if="acc.main_image" :src="getImageUrl(acc.main_image)" :alt="acc.name" class="acc-img" />
                  <div v-else class="acc-img-placeholder"><img src="/images/default-product.jpg" alt="默认" style="width:100%;height:100%;object-fit:cover;border-radius:8px" /></div>
                  <div class="acc-info">
                    <p class="acc-name">{{ acc.name }}</p>
                    <p class="acc-price">+¥{{ formatPrice(acc.sale_price) }}</p>
                  </div>
                  <div class="acc-check">{{ drawer.selectedAccessories.includes(acc.id) ? '✓' : '+' }}</div>
                </div>
              </div>
            </div>

            <!-- 数量 -->
            <div class="drawer-section">
              <h4 class="section-title">数量</h4>
              <div class="qty-row">
                <button class="qty-btn" @click="changeQty(-1)" :disabled="drawer.quantity <= 1">−</button>
                <span class="qty-val">{{ drawer.quantity }}</span>
                <button class="qty-btn" @click="changeQty(1)">+</button>
              </div>
            </div>

            <!-- 空间归属 -->
            <div class="drawer-section">
              <h4 class="section-title">放在哪个空间？</h4>
              <div class="space-chips">
                <button
                  v-for="s in spaceOptions"
                  :key="s"
                  class="opt-chip"
                  :class="{ active: drawer.spaceName === s }"
                  @click="drawer.spaceName = s"
                >{{ s }}</button>
              </div>
            </div>
          </div>

          <!-- 底部价格（深度定制入口） -->
          <div class="drawer-footer">
            <div class="price-summary">
              <span class="price-label">合计</span>
              <span class="price-total">¥{{ formatPrice(drawerTotalPrice) }}</span>
            </div>
            <button class="add-to-selection-btn" @click="confirmAdd">
              {{ isInSelection(drawer.product?.id) ? '更新选品' : '加入选品单' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ===== 选品单侧边栏 ===== -->
    <transition name="drawer-slide">
      <div v-if="selectionDrawer" class="drawer-mask" @click.self="selectionDrawer = false">
        <div class="drawer">
          <button class="drawer-close" @click="selectionDrawer = false">✕</button>
          <div class="drawer-scroll">
            <h2 class="selection-title">我的选品单</h2>
            <p class="selection-sub">共 {{ totalCount }} 件 · 合计 ¥{{ formatPrice(totalPrice) }}</p>

            <div v-if="items.length === 0" class="selection-empty">
              <p>还没有选品，去逛逛吧</p>
            </div>

            <div v-else class="selection-items">
              <div v-for="item in items" :key="item.id + item.type" class="sel-item">
                <img v-if="item.image" :src="getImageUrl(item.image)" :alt="item.name" class="sel-img" />
                <div v-else class="sel-img-placeholder"><img src="/images/default-product.jpg" alt="默认" style="width:100%;height:100%;object-fit:cover;border-radius:8px" /></div>
                <div class="sel-info">
                  <p class="sel-name">{{ item.name }}</p>
                  <p class="sel-space">{{ item.space_name }}</p>
                  <div class="sel-qty-row">
                    <button class="qty-btn sm" @click="updateQuantity(item.id, item.type, (item.quantity||1)-1)">−</button>
                    <span class="qty-val sm">{{ item.quantity || 1 }}</span>
                    <button class="qty-btn sm" @click="updateQuantity(item.id, item.type, (item.quantity||1)+1)">+</button>
                    <span class="sel-price">¥{{ formatPrice((item.price||0) * (item.quantity||1)) }}</span>
                  </div>
                </div>
                <button class="sel-remove" @click="removeItem(item.id, item.type)">✕</button>
              </div>
            </div>
          </div>

          <div class="drawer-footer" v-if="items.length > 0">
            <div class="price-summary">
              <span class="price-label">合计</span>
              <span class="price-total">¥{{ formatPrice(totalPrice) }}</span>
            </div>
            <button class="add-to-selection-btn" @click="$router.push('/selection-center'); selectionDrawer = false">
              查看完整选品单 →
            </button>
          </div>
        </div>
      </div>
    </transition>

    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const router = useRouter()
const { addItem, updateQuantity, removeItem, items, totalCount, totalPrice, hasItems } = useAnonymousSelection()

// ===== 分类 =====
const catBarRef = ref(null)
const productsRef = ref(null)
const catSticky = ref(false)
const catBarTop = ref(0)
const categoryTree = ref([])
const catExpanded = ref(false)        // 分类栏是否展开
const showMoreBtn = ref(false)        // 是否显示"更多"按钮

// ===== 树状分类：只展示有 is_public 物料的分类 =====
const visibleCategoryTree = computed(() => {
  // 过滤出有前台展示物料的分类，保持树结构
  return categoryTree.value.filter(cat => {
    // 父分类有public物料 或 子分类有public物料
    const selfHasPublic = cat.public_count > 0
    const childrenHasPublic = (cat.children || []).some(c => c.public_count > 0)
    return selfHasPublic || childrenHasPublic
  }).map(cat => ({
    ...cat,
    // 子分类也只保留有 public 的
    children: (cat.children || []).filter(c => c.public_count > 0)
  }))
})

// 扁平列表（用于"更多"按钮判断）
const flatCats = computed(() => {
  const result = []
  visibleCategoryTree.value.forEach(cat => {
    result.push(cat)
    ;(cat.children || []).forEach(c => result.push(c))
  })
  return result
})

// ===== 筛选 & 分页 =====
const filters = reactive({ category_id: null, keyword: '' })
const pagination = reactive({ page: 1, page_size: 24 })
const total = ref(0)
const products = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = computed(() => products.value.length < total.value)

// ===== 空间选项 =====
const spaceOptions = ['客厅', '主卧', '次卧', '书房', '餐厅', '厨房', '阳台', '其他']

// ===== 抽屉状态 =====
const selectionDrawer = ref(false)
const drawer = reactive({
  visible: false,
  product: null,
  variants: [],
  selectedVariant: null,
  customOptions: [],
  customValues: {},
  customPriceDeltas: {},
  accessories: [],
  selectedAccessories: [],
  accessoryPrices: {},
  quantity: 1,
  spaceName: '客厅'
})

// ===== 实时价格计算 =====
const drawerTotalPrice = computed(() => {
  if (!drawer.product) return 0
  let base = Number(drawer.product.sale_price || 0)
  // 变体价格
  if (drawer.selectedVariant?.price_delta) base += Number(drawer.selectedVariant.price_delta)
  // 定制选项价格
  Object.values(drawer.customPriceDeltas).forEach(d => { base += Number(d || 0) })
  // 配件价格
  drawer.selectedAccessories.forEach(accId => {
    base += Number(drawer.accessoryPrices[accId] || 0)
  })
  return base * drawer.quantity
})

// ===== 图片 URL =====
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://localhost:8080${path.startsWith('/') ? '' : '/'}${path}`
}

// ===== 格式化价格 =====
const formatPrice = (v) => {
  if (!v && v !== 0) return '0'
  return Number(v).toLocaleString()
}

// ===== 是否已在选品单 =====
const isInSelection = (productId) => {
  return items.value.some(i => i.id === productId)
}

// ===== 分类操作 =====
const selectCat = (id) => {
  filters.category_id = id
  pagination.page = 1
  fetchProducts()
}

// ===== 获取产品 =====
const fetchProducts = async (isMore = false) => {
  if (isMore) loadingMore.value = true
  else loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size, status: 'active' }
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.keyword) params.keyword = filters.keyword
    const res = await request.get('/materials', { params })
    const newItems = res?.items || []
    products.value = isMore ? [...products.value, ...newItems] : newItems
    total.value = res?.total || 0
  } catch (e) {
    console.error('获取产品失败', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => { pagination.page++; fetchProducts(true) }

// ===== 获取分类（树状结构 + public计数） =====
const fetchCategories = async () => {
  try {
    const res = await request.get('/materials/categories')
    const rawTree = res || []
    // 为每个分类附加 public_count
    try {
      const pubRes = await request.get('/materials/public-config')
      const publicCats = pubRes?.categories || []
      const publicMap = {}
      publicCats.forEach(cid => { publicMap[cid] = true })
      // 标记每个分类的public物料数
      const walk = (list) => list.forEach(c => {
        c.public_count = publicMap[c.id] ? 1 : 0
        if (c.children?.length) walk(c.children)
      })
      walk(rawTree)
    } catch (e) { /* public-config 失败不影响 */ }
    categoryTree.value = rawTree
  } catch (e) { console.error('获取分类失败', e) }
}

// ===== 打开定制抽屉 =====
const openCustomize = async (product) => {
  drawer.product = product
  drawer.variants = []
  drawer.selectedVariant = null
  drawer.customOptions = buildCustomOptions(product)
  drawer.customValues = {}
  drawer.customPriceDeltas = {}
  drawer.accessories = []
  drawer.selectedAccessories = []
  drawer.accessoryPrices = {}
  drawer.quantity = 1
  drawer.spaceName = '客厅'
  drawer.visible = true
  document.body.style.overflow = 'hidden'

  // 异步加载同分类配件
  try {
    const params = { page: 1, page_size: 6, status: 'active' }
    if (product.category_id) params.category_id = product.category_id
    const res = await request.get('/materials', { params })
    drawer.accessories = (res?.items || [])
      .filter(p => p.id !== product.id)
      .slice(0, 4)
    drawer.accessories.forEach(a => { drawer.accessoryPrices[a.id] = a.sale_price || 0 })
  } catch (e) { /* 配件加载失败不影响主流程 */ }
}

// 根据产品规格字段构建定制选项（示例逻辑）
const buildCustomOptions = (product) => {
  const opts = []
  // 颜色
  if (product.color_options) {
    try {
      const colors = JSON.parse(product.color_options)
      if (colors.length > 0) {
        opts.push({ key: 'color', label: '颜色', type: 'color', choices: colors })
      }
    } catch (e) {}
  }
  // 材质
  if (product.material_options) {
    try {
      const mats = JSON.parse(product.material_options)
      if (mats.length > 0) {
        opts.push({ key: 'material', label: '材质', type: 'select', choices: mats })
      }
    } catch (e) {}
  }
  // 尺寸
  if (product.size_options) {
    try {
      const sizes = JSON.parse(product.size_options)
      if (sizes.length > 0) {
        opts.push({ key: 'size', label: '尺寸', type: 'select', choices: sizes })
      }
    } catch (e) {}
  }
  // 如果没有定制选项，给一个默认颜色示例
  if (opts.length === 0 && product.specification) {
    opts.push({
      key: 'color', label: '颜色', type: 'color',
      choices: [
        { value: 'natural', label: '原木色', hex: '#C8A882', price_delta: 0 },
        { value: 'walnut', label: '胡桃色', hex: '#5C3D2E', price_delta: 200 },
        { value: 'white', label: '哑白', hex: '#F5F5F0', price_delta: 0 },
        { value: 'black', label: '哑黑', hex: '#2C2C2C', price_delta: 0 }
      ]
    })
  }
  return opts
}

const selectVariant = (v) => { drawer.selectedVariant = v }
const setCustomValue = (key, value, priceDelta) => {
  drawer.customValues[key] = value
  drawer.customPriceDeltas[key] = priceDelta
}
const toggleAccessory = (acc) => {
  const idx = drawer.selectedAccessories.indexOf(acc.id)
  if (idx >= 0) drawer.selectedAccessories.splice(idx, 1)
  else drawer.selectedAccessories.push(acc.id)
}
const changeQty = (delta) => {
  drawer.quantity = Math.max(1, drawer.quantity + delta)
}

const closeDrawer = () => {
  drawer.visible = false
  document.body.style.overflow = ''
}

// ===== 确认加入选品 =====
const confirmAdd = () => {
  if (!drawer.product) return
  const item = {
    id: drawer.product.id,
    type: 'product',
    name: drawer.product.name,
    sku_code: drawer.product.sku_code,
    image: drawer.product.main_image,
    price: Number(drawer.product.sale_price || 0),
    unit: drawer.product.unit,
    brand: drawer.product.brand,
    specification: drawer.product.specification,
    space_name: drawer.spaceName,
    quantity: drawer.quantity,
    custom_options: { ...drawer.customValues },
    selected_accessories: [...drawer.selectedAccessories]
  }
  addItem(item)
  ElMessage.success(`✓ 已加入选品单`)
  closeDrawer()
}

// ===== 快速加入（不打开抽屉）=====
const quickAdd = (product) => {
  const item = {
    id: product.id,
    type: 'product',
    name: product.name,
    image: product.main_image,
    price: Number(product.sale_price || 0),
    unit: product.unit,
    brand: product.brand,
    space_name: '客厅',
    quantity: 1
  }
  addItem(item)
  ElMessage.success(`✓ ${product.name} 已加入选品单`)
}

// ===== 打开选品单侧边栏 =====
const openSelectionDrawer = () => {
  selectionDrawer.value = true
  document.body.style.overflow = 'hidden'
}

watch(selectionDrawer, (v) => {
  if (!v) document.body.style.overflow = ''
})

// ===== 滚动到产品区 =====
const scrollToProducts = () => {
  productsRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// ===== 粘性分类栏 =====
const handleScroll = () => {
  if (!catBarRef.value) return
  catSticky.value = window.scrollY >= catBarTop.value - 60
}

// ===== 检测分类是否需要"更多"按钮 =====
const checkCatOverflow = () => {
  const inner = catBarRef.value?.querySelector('.cat-inner')
  if (!inner) return
  // 计算内容高度 vs 3行高度（按钮高度约36px + gap 4px = 40px/行）
  const lineHeight = 40  // 每行约40px
  const maxHeight = lineHeight * 3  // 最多3行
  showMoreBtn.value = inner.scrollHeight > maxHeight + 4  // +4 容错
}

onMounted(() => {
  fetchCategories()
  fetchProducts()
  setTimeout(() => {
    catBarTop.value = catBarRef.value?.offsetTop || 0
    checkCatOverflow()
  }, 500)
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('resize', checkCatOverflow)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', checkCatOverflow)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ===== 基础 ===== */
.product-page {
  min-height: 100vh;
  background: #fff;
  padding-top: 60px;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
}

/* ===== HERO ===== */
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 88vh;
  align-items: center;
  padding: 0 80px;
  gap: 60px;
  background: #fff;
}

.hero-eyebrow {
  font-size: 13px;
  letter-spacing: 3px;
  color: #8B5A2B;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 56px;
  font-weight: 600;
  line-height: 1.15;
  color: #1d1d1f;
  margin-bottom: 24px;
  letter-spacing: -1px;
}

.hero-sub {
  font-size: 17px;
  color: #6e6e73;
  margin-bottom: 40px;
  line-height: 1.6;
}

/* 价值点 */
.hero-value-points {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 40px;
}

.value-point {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: #f5f5f7;
  border-radius: 14px;
  transition: all 0.2s;
}

.value-point:hover {
  background: #ebebef;
  transform: translateX(4px);
}

.vp-icon {
  font-size: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}

.vp-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vp-content strong {
  font-size: 15px;
  color: #1d1d1f;
  font-weight: 600;
}

.vp-content span {
  font-size: 14px;
  color: #6e6e73;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.btn-primary {
  background: #8B5A2B;
  color: #fff;
  border: none;
  padding: 14px 32px;
  font-size: 15px;
  border-radius: 980px;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  font-weight: 500;
}
.btn-primary:hover { background: #7a4e25; transform: scale(1.02); }

.btn-ghost {
  background: transparent;
  color: #8B5A2B;
  border: 1.5px solid #8B5A2B;
  padding: 14px 32px;
  font-size: 15px;
  border-radius: 980px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.btn-ghost:hover { background: #8B5A2B; color: #fff; }

.hero-visual {
  height: 80vh;
  border-radius: 20px;
  overflow: hidden;
}
.hero-visual img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ===== 分类栏 ===== */
.cat-bar {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid #e5e5ea;
  padding: 0 80px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  z-index: 200;
  transition: box-shadow 0.3s;
}
.cat-bar.sticky {
  position: fixed;
  top: 60px;
  left: 0; right: 0;
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}

.cat-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 12px 0;
  flex: 1;
  /* 不限制最大高度，让树状子分类自然展开 */
  transition: max-height 0.3s ease;
}

/* 树状分类内层 */
.tree-cat-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 0;
  align-items: center;
}

/* 父分类按钮 - 加粗加色 */
.cat-btn.cat-parent {
  font-weight: 600;
  color: #1d1d1f;
  background: transparent;
  border-bottom: 2px solid transparent;
}
.cat-btn.cat-parent:hover,
.cat-btn.cat-parent.active {
  background: #fdf6f0;
  color: #8B5A2B;
  border-bottom-color: #8B5A2B;
}
.cat-btn.cat-parent.has-children::after {
  content: '';
  display: inline-block;
  width: 0; height: 0;
  margin-left: 4px;
  vertical-align: middle;
  border-left: 4px solid #8B5A2B;
  border-top: 3px solid transparent;
  border-bottom: 3px solid transparent;
}

/* 子分类按钮 - 缩进+浅色 */
.cat-btn.cat-child {
  font-size: 13px;
  font-weight: 400;
  color: #6e6e73;
  background: transparent;
  padding: 6px 12px;
  height: 32px;
  opacity: 0.9;
}
.cat-btn.cat-child::before {
  content: '·';
  margin-right: 2px;
  color: #c7c7cc;
}
.cat-btn.cat-child:hover {
  color: #8B5A2B;
  background: #faf5ef;
  opacity: 1;
}
.cat-btn.cat-child.active {
  color: #8B5A2B;
  background: #fdf6f0;
  font-weight: 500;
  opacity: 1;
}
.cat-inner.show-more {
  /* 有"更多"按钮时，保持可展开 */
}
.cat-bar.expanded .cat-inner {
  /* 已移除max-height限制，此样式保留备用 */
}

.cat-btn {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 14px;
  color: #6e6e73;
  cursor: pointer;
  border-radius: 980px;
  white-space: nowrap;
  transition: all 0.2s;
  font-weight: 400;
  height: 36px;
  line-height: 20px;
}
.cat-btn:hover { color: #1d1d1f; background: #f5f5f7; }
.cat-btn.active { color: #1d1d1f; background: #f5f5f7; font-weight: 600; }

/* "更多"按钮 */
.cat-more-btn {
  background: #f5f5f7;
  border: none;
  padding: 8px 16px;
  font-size: 13px;
  color: #8B5A2B;
  cursor: pointer;
  border-radius: 980px;
  white-space: nowrap;
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  height: 36px;
}
.cat-more-btn:hover { background: #ebebef; }
.more-arrow {
  font-size: 10px;
  transition: transform 0.2s;
  display: inline-block;
}
.more-arrow.up {
  transform: rotate(180deg);
}

/* 选品单入口 */
.selection-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1d1d1f;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 980px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s, transform 0.15s;
  flex-shrink: 0;
}
.selection-badge:hover { background: #3a3a3c; transform: scale(1.03); }
.badge-count {
  background: #8B5A2B;
  color: #fff;
  border-radius: 50%;
  width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

/* 淡入动画 */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(20px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(20px); }

/* ===== 产品区 ===== */
.products-wrap {
  padding: 48px 80px 80px;
  background: #fff;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  background: #f5f5f7;
}

/* 产品卡片 */
.product-card {
  background: #fff;
  cursor: pointer;
  transition: transform 0.2s;
  position: relative;
  overflow: hidden;
}
.product-card:hover { transform: translateY(-2px); }
.product-card.in-selection { outline: 2px solid #8B5A2B; }

.card-img-wrap {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  background: #f5f5f7;
}
.card-img {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.product-card:hover .card-img { transform: scale(1.04); }

.card-img-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f5f5f7;
}
.card-img-placeholder .default-img {
  width: 60%; height: 60%;
  object-fit: contain;
  opacity: 0.85;
}

/* 已选标记 */
.selected-mark {
  position: absolute;
  top: 12px; left: 12px;
  background: #8B5A2B;
  color: #fff;
  padding: 4px 10px;
  border-radius: 980px;
  font-size: 11px;
  font-weight: 600;
}

/* 悬停操作 */
.card-hover-actions {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 16px;
  background: linear-gradient(to top, rgba(0,0,0,0.5), transparent);
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  justify-content: center;
}
.product-card:hover .card-hover-actions { opacity: 1; }

.hover-btn {
  background: #fff;
  color: #1d1d1f;
  border: none;
  padding: 10px 20px;
  border-radius: 980px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.hover-btn:hover { background: #f5f5f7; }

/* 卡片信息 */
.card-body {
  padding: 16px 16px 20px;
}
.card-brand {
  font-size: 11px;
  color: #8B5A2B;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.card-name {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 8px;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.card-footer { display: flex; align-items: baseline; gap: 4px; }
.card-price { font-size: 16px; font-weight: 600; color: #1d1d1f; }
.card-unit { font-size: 12px; color: #6e6e73; }

/* 骨架屏 */
.skeleton { pointer-events: none; }
.skeleton-img {
  aspect-ratio: 1/1;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-line {
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 8px;
}
.w80 { width: 80%; }
.w50 { width: 50%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 加载更多 */
.load-more-wrap { padding: 60px; text-align: center; }
.load-more-btn {
  background: none;
  border: 1.5px solid #1d1d1f;
  color: #1d1d1f;
  padding: 14px 48px;
  font-size: 14px;
  border-radius: 980px;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 1px;
}
.load-more-btn:hover { background: #1d1d1f; color: #fff; }
.load-more-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.empty { padding: 120px; text-align: center; color: #6e6e73; font-size: 16px; }

/* ===== 抽屉通用 ===== */
.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.drawer {
  width: 100%;
  max-height: 90vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  position: relative;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -8px 40px rgba(0,0,0,0.15);
}

.drawer-close {
  position: absolute;
  top: 14px; right: 14px;
  background: rgba(255,255,255,0.9);
  border: none;
  width: 32px; height: 32px;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.drawer-close:hover { background: #fff; }

.drawer-scroll {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}
.drawer-scroll::-webkit-scrollbar { width: 4px; }
.drawer-scroll::-webkit-scrollbar-thumb { background: #e5e5ea; border-radius: 2px; }

/* 抽屉产品主图 */
.drawer-hero {
  width: 100%;
  height: 300px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
  background: #f5f5f7;
}
.drawer-main-img { width: 100%; height: 100%; object-fit: cover; }
.drawer-img-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 80px;
}
.drawer-quick-add {
  position: absolute;
  bottom: 16px; left: 50%;
  transform: translateX(-50%);
  background: rgba(255,255,255,0.95);
  border: 1.5px solid #1d1d1f;
  color: #1d1d1f;
  padding: 10px 24px;
  border-radius: 980px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  white-space: nowrap;
  z-index: 2;
}
.drawer-quick-add:hover {
  background: #1d1d1f;
  color: #fff;
}
.drawer-info-overlay {
  position: absolute;
  bottom: 60px; left: 0; right: 0;
  padding: 12px 16px 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  color: #fff;
}
.drawer-info-overlay .drawer-brand { color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 2px; }
.drawer-info-overlay .drawer-name { font-size: 18px; font-weight: 600; line-height: 1.3; }

/* 抽屉基本信息 */
.drawer-info {
  padding: 24px 24px 0;
}
.drawer-brand {
  font-size: 11px;
  color: #8B5A2B;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.drawer-name {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
  line-height: 1.3;
}
.drawer-spec {
  font-size: 13px;
  color: #6e6e73;
  line-height: 1.5;
}

/* 抽屉各节 */
.drawer-section {
  padding: 20px 24px 0;
  border-top: 1px solid #f5f5f7;
  margin-top: 20px;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 14px;
  letter-spacing: 0.5px;
}

/* 变体 */
.variant-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.variant-btn {
  border: 1.5px solid #e5e5ea;
  background: #fff;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.variant-btn:hover { border-color: #8B5A2B; }
.variant-btn.active { border-color: #8B5A2B; background: #fdf6f0; }
.v-name { font-size: 13px; color: #1d1d1f; }
.v-price { font-size: 12px; color: #8B5A2B; font-weight: 600; }

/* 颜色选择器 */
.color-picker { display: flex; gap: 10px; flex-wrap: wrap; }
.color-dot {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  outline: 2px solid transparent;
  outline-offset: 2px;
}
.color-dot:hover { transform: scale(1.1); }
.color-dot.active { outline-color: #8B5A2B; }

/* 选项 chips */
.opt-chips, .space-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.opt-chip {
  border: 1.5px solid #e5e5ea;
  background: #fff;
  padding: 8px 14px;
  border-radius: 980px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.2s;
  display: flex; align-items: center; gap: 4px;
}
.opt-chip:hover { border-color: #8B5A2B; }
.opt-chip.active { border-color: #8B5A2B; background: #fdf6f0; color: #8B5A2B; font-weight: 600; }
.chip-delta { font-size: 11px; color: #8B5A2B; }

/* 配件 */
.accessory-list { display: flex; flex-direction: column; gap: 10px; }
.accessory-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1.5px solid #e5e5ea;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.accessory-item:hover { border-color: #8B5A2B; }
.accessory-item.selected { border-color: #8B5A2B; background: #fdf6f0; }
.acc-img { width: 56px; height: 56px; object-fit: cover; border-radius: 8px; }
.acc-img-placeholder {
  width: 56px; height: 56px;
  background: #f5f5f7;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
}
.acc-info { flex: 1; }
.acc-name { font-size: 13px; color: #1d1d1f; margin-bottom: 2px; }
.acc-price { font-size: 12px; color: #8B5A2B; font-weight: 600; }
.acc-check {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: #f5f5f7;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #8B5A2B;
  flex-shrink: 0;
}

/* 数量 */
.qty-row { display: flex; align-items: center; gap: 16px; }
.qty-btn {
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1.5px solid #e5e5ea;
  background: #fff;
  font-size: 18px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  color: #1d1d1f;
}
.qty-btn:hover:not(:disabled) { border-color: #8B5A2B; color: #8B5A2B; }
.qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.qty-btn.sm { width: 28px; height: 28px; font-size: 14px; }
.qty-val { font-size: 18px; font-weight: 600; color: #1d1d1f; min-width: 32px; text-align: center; }
.qty-val.sm { font-size: 14px; min-width: 24px; }

/* 抽屉底部 */
.drawer-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e5ea;
  background: #fff;
}
.price-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.price-label { font-size: 13px; color: #6e6e73; }
.price-total { font-size: 24px; font-weight: 700; color: #1d1d1f; }

.add-to-selection-btn {
  width: 100%;
  background: #8B5A2B;
  color: #fff;
  border: none;
  padding: 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}
.add-to-selection-btn:hover { background: #7a4e25; transform: scale(1.01); }

/* 选品单 */
.selection-title { font-size: 22px; font-weight: 700; color: #1d1d1f; padding: 24px 24px 4px; }
.selection-sub { font-size: 13px; color: #6e6e73; padding: 0 24px 20px; }
.selection-empty { padding: 60px 24px; text-align: center; color: #6e6e73; }
.selection-items { padding: 0 24px; display: flex; flex-direction: column; gap: 12px; }
.sel-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f5f7;
  border-radius: 12px;
}
.sel-img { width: 64px; height: 64px; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
.sel-img-placeholder {
  width: 64px; height: 64px;
  background: #e5e5ea;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.sel-info { flex: 1; min-width: 0; }
.sel-name { font-size: 13px; font-weight: 500; color: #1d1d1f; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sel-space { font-size: 11px; color: #8B5A2B; margin-bottom: 6px; }
.sel-qty-row { display: flex; align-items: center; gap: 8px; }
.sel-price { font-size: 13px; font-weight: 600; color: #1d1d1f; margin-left: auto; }
.sel-remove {
  background: none; border: none;
  color: #c7c7cc; font-size: 14px;
  cursor: pointer; padding: 4px;
  flex-shrink: 0;
  transition: color 0.2s;
}
.sel-remove:hover { color: #ff3b30; }

/* 抽屉动画 */
.drawer-slide-enter-active, .drawer-slide-leave-active { transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
.drawer-slide-enter-from .drawer, .drawer-slide-leave-to .drawer { transform: translateY(100%); }
.drawer-slide-enter-from, .drawer-slide-leave-to { background: transparent; }

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .hero { padding: 0 40px; }
  .hero-title { font-size: 44px; }
  .cat-bar { padding: 0 40px; }
  .products-wrap { padding: 40px 40px 60px; }
  .product-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding: 60px 24px; min-height: auto; gap: 40px; }
  .hero-visual { height: 50vw; }
  .hero-title { font-size: 36px; }
  .hero-value-points { gap: 12px; }
  .value-point { padding: 12px 16px; }
  .vp-icon { font-size: 20px; }
  .vp-content strong { font-size: 14px; }
  .vp-content span { font-size: 13px; }
  .cat-bar { padding: 0 24px; }
  .products-wrap { padding: 24px 24px 60px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); }
  .drawer { max-height: 95vh; }
}

@media (max-width: 480px) {
  .hero-title { font-size: 28px; }
  .hero-value-points { gap: 10px; }
  .value-point { padding: 10px 14px; border-radius: 12px; }
  .vp-icon { font-size: 18px; }
  .vp-content strong { font-size: 13px; }
  .vp-content span { font-size: 12px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); gap: 1px; }
  .card-body { padding: 10px 10px 14px; }
  .card-name { font-size: 12px; }
  .card-price { font-size: 14px; }
}
</style>
