<template>
  <div class="product-page">
    <Navbar />

    <!-- ===== 页面标题栏 ===== -->
    <section class="page-header">
      <div class="header-bg"></div>
      <div class="header-inner">
        <p class="header-eyebrow">D&B 帝标|设记家</p>
        <h1 class="page-title">产品中心</h1>
        <p class="page-sub">家居产品只是舒适的生活构成元素<br class="sub-br" />全案服务才是还原落地的保障</p>
        <div class="header-line"></div>
      </div>
    </section>

    <!-- ===== 分类导航（粘性） ===== -->
    <div class="cat-bar" :class="{ sticky: catSticky }" ref="catBarRef">
      <div class="cat-inner">
        <button
          class="cat-btn"
          :class="{ active: filters.category_id === null }"
          @click="selectCat(null)"
        >全部</button>

        <template v-for="cat in visibleCategoryTree" :key="cat.id">
          <button
            class="cat-btn cat-parent"
            :class="{ active: filters.category_id === cat.id }"
            @click="selectCat(cat.id)"
          >{{ cat.name }}</button>
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
      <!-- 统计 -->
      <div class="cat-stat" v-if="total > 0">{{ total }} 款产品</div>
    </div>

    <!-- ===== 筛选栏 ===== -->
    <div class="filter-bar">
      <div class="filter-inner">
        <div class="search-box">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
          <input
            v-model="filters.keyword"
            @input="onSearchInput"
            placeholder="搜索产品名称、品牌、SKU..."
            class="search-input"
          />
        </div>
        <div class="filter-selects">
          <select v-model="filters.brand" @change="onFilterChange" class="filter-select">
            <option value="">全部品牌</option>
            <option v-for="b in filterOptions.brands" :key="b" :value="b">{{ b }}</option>
          </select>
          <select v-model="filters.unit" @change="onFilterChange" class="filter-select">
            <option value="">全部单位</option>
            <option v-for="u in filterOptions.units" :key="u" :value="u">{{ u }}</option>
          </select>
          <select v-model="filters.env_level" @change="onFilterChange" class="filter-select">
            <option value="">全部环保等级</option>
            <option v-for="e in filterOptions.env_levels" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ===== 产品网格 ===== -->
    <main class="products-wrap" ref="productsRef">
      <!-- 骨架屏 -->
      <div v-if="loading" class="product-grid">
        <div v-for="i in 12" :key="i" class="product-card skeleton">
          <div class="card-img skeleton-img"></div>
          <div class="card-body"><div class="skeleton-line w70"></div><div class="skeleton-line w40"></div></div>
        </div>
      </div>

      <!-- 产品列表 -->
      <div v-else class="product-grid">
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ 'in-selection': isInSelection(product.id) }"
          @mouseenter="hoveredId = product.id"
          @mouseleave="hoveredId = null"
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
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
            </div>

            <!-- 悬浮覆盖层 -->
            <transition name="fade">
              <div v-if="hoveredId === product.id" class="card-overlay">
                <button class="overlay-btn primary" @click.stop="quickAdd(product)">
                  {{ isInSelection(product.id) ? '✓ 已选 · 再加一件' : '加入选品' }}
                </button>
                <button class="overlay-btn ghost" @click.stop="openCustomize(product)">
                  查看详情 →
                </button>
              </div>
            </transition>

            <!-- 已选标记 -->
            <div v-if="isInSelection(product.id)" class="selected-badge">
              <span class="badge-dot"></span>已选
            </div>
          </div>

          <!-- 信息区 -->
          <div class="card-body">
            <p class="card-brand" v-if="product.brand">{{ product.brand }}</p>
            <h3 class="card-name">{{ product.name }}</h3>
            <div class="card-meta">
              <span class="card-price">¥{{ formatPrice(product.sale_price) }}</span>
              <span class="card-unit" v-if="product.unit">/ {{ product.unit }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="!loading && hasMore" class="load-more-wrap">
        <button class="load-more-btn" :disabled="loadingMore" @click="loadMore">
          {{ loadingMore ? '加载中…' : '查看更多 ↓' }}
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && products.length === 0" class="empty">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#444" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg>
        <p>暂无产品</p>
      </div>
    </main>

    <!-- ===== 深度定制抽屉 ===== -->
    <transition name="drawer-slide">
      <div v-if="drawer.visible" class="drawer-mask" @click.self="closeDrawer">
        <div class="drawer">
          <button class="drawer-close" @click="closeDrawer">✕</button>
          <div class="drawer-scroll">
            <div class="drawer-hero">
              <img
                v-if="drawer.product?.main_image"
                :src="getImageUrl(drawer.product.main_image)"
                :alt="drawer.product?.name"
                class="drawer-main-img"
              />
              <div v-else class="drawer-img-placeholder">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
              </div>
              <div class="drawer-info-overlay">
                <p class="drawer-brand">{{ drawer.product?.brand || 'D&B 帝标|设记家' }}</p>
                <h2 class="drawer-name">{{ drawer.product?.name }}</h2>
              </div>
            </div>

            <div class="drawer-info">
              <p class="drawer-spec" v-if="drawer.product?.specification">{{ drawer.product.specification }}</p>
            </div>

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

            <div class="drawer-section" v-if="drawer.customOptions.length > 0">
              <h4 class="section-title">定制选项</h4>
              <div v-for="opt in drawer.customOptions" :key="opt.key" class="custom-option">
                <label class="opt-label">{{ opt.label }}</label>
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
                <div v-else-if="opt.type === 'select'" class="opt-chips">
                  <button
                    v-for="c in opt.choices"
                    :key="c.value"
                    class="opt-chip"
                    :class="{ active: drawer.customValues[opt.key] === c.value }"
                    @click="setCustomValue(opt.key, c.value, c.price_delta || 0)"
                  >{{ c.label }}</button>
                </div>
              </div>
            </div>

            <div class="drawer-section">
              <h4 class="section-title">数量</h4>
              <div class="qty-row">
                <button class="qty-btn" @click="changeQty(-1)" :disabled="drawer.quantity <= 1">−</button>
                <span class="qty-val">{{ drawer.quantity }}</span>
                <button class="qty-btn" @click="changeQty(1)">+</button>
              </div>
            </div>

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

    <!-- 选品单侧边栏 -->
    <transition name="drawer-slide">
      <div v-if="selectionDrawer" class="drawer-mask" @click.self="selectionDrawer = false">
        <div class="drawer">
          <button class="drawer-close" @click="selectionDrawer = false">✕</button>
          <div class="drawer-scroll">
            <h2 class="selection-title">我的选品单</h2>
            <p class="selection-sub">共 {{ totalCount }} 件 · 合计 ¥{{ formatPrice(totalPrice) }}</p>

            <div v-if="items.length === 0" class="selection-empty">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="1"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 001.97-1.61L23 6H6"/></svg>
              <p>还没有选品，去逛逛吧</p>
            </div>

            <div v-else class="selection-items">
              <div v-for="item in items" :key="item.id + item.type" class="sel-item">
                <img v-if="item.image" :src="getImageUrl(item.image)" :alt="item.name" class="sel-img" />
                <div v-else class="sel-img-placeholder">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
                </div>
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

    <!-- 固定悬浮选品按钮 -->
    <div class="selection-float">
      <SelectionButton />
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'
import SelectionButton from '@/components/SelectionButton.vue'

const { addItem, updateQuantity, removeItem, items, totalCount, totalPrice } = useAnonymousSelection()

// 分类
const catBarRef = ref(null)
const productsRef = ref(null)
const catSticky = ref(false)
const categoryTree = ref([])
const filterOptions = ref({ brands: [], units: [], env_levels: [] })

const visibleCategoryTree = computed(() => {
  return categoryTree.value.filter(cat => {
    const selfHasPublic = cat.public_count > 0
    const childrenHasPublic = (cat.children || []).some(c => c.public_count > 0)
    return selfHasPublic || childrenHasPublic
  }).map(cat => ({
    ...cat,
    children: (cat.children || []).filter(c => c.public_count > 0)
  }))
})

// 筛选 & 分页
const filters = reactive({ category_id: null, keyword: '', brand: '', unit: '', env_level: '' })
const pagination = reactive({ page: 1, page_size: 24 })
const total = ref(0)
const products = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = computed(() => products.value.length < total.value)

// 悬浮交互
const hoveredId = ref(null)

// 空间选项
const spaceOptions = ['客厅', '主卧', '次卧', '书房', '餐厅', '厨房', '阳台', '其他']

// 抽屉状态
const selectionDrawer = ref(false)
const drawer = reactive({
  visible: false,
  product: null,
  variants: [],
  selectedVariant: null,
  customOptions: [],
  customValues: {},
  customPriceDeltas: {},
  quantity: 1,
  spaceName: '客厅'
})

// 价格计算
const drawerTotalPrice = computed(() => {
  if (!drawer.product) return 0
  let base = Number(drawer.product.sale_price || 0)
  if (drawer.selectedVariant?.price_delta) base += Number(drawer.selectedVariant.price_delta)
  Object.values(drawer.customPriceDeltas).forEach(d => { base += Number(d || 0) })
  return base * drawer.quantity
})

// 图片 URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://localhost:8080${path.startsWith('/') ? '' : '/'}${path}`
}

// 格式化价格
const formatPrice = (v) => {
  if (!v && v !== 0) return '0'
  return Number(v).toLocaleString()
}

// 是否已在选品单
const isInSelection = (productId) => {
  return items.value.some(i => i.id === productId)
}

// 分类操作
const selectCat = (id) => {
  filters.category_id = id
  pagination.page = 1
  fetchProducts()
}

let _searchTimer = null
const onSearchInput = () => {
  clearTimeout(_searchTimer)
  _searchTimer = setTimeout(() => {
    pagination.page = 1
    fetchProducts()
  }, 400)
}

const onFilterChange = () => {
  pagination.page = 1
  fetchProducts()
}

// 获取产品
const fetchProducts = async (isMore = false) => {
  if (isMore) loadingMore.value = true
  else loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size, status: 'active', is_public: true }
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.brand) params.brand = filters.brand
    if (filters.unit) params.unit = filters.unit
    if (filters.env_level) params.env_level = filters.env_level
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

// 获取分类
const fetchCategories = async () => {
  try {
    const res = await request.get('/materials/categories')
    const rawTree = res || []
    try {
      const pubRes = await request.get('/materials/public-config')
      const publicCats = pubRes?.categories || []
      const publicMap = {}
      publicCats.forEach(cid => { publicMap[cid] = true })
      const walk = (list) => list.forEach(c => {
        c.public_count = publicMap[c.id] ? 1 : 0
        if (c.children?.length) walk(c.children)
      })
      walk(rawTree)
    } catch (e) {}
    categoryTree.value = rawTree
  } catch (e) { console.error('获取分类失败', e) }
}

const fetchFilterOptions = async () => {
  try {
    const res = await request.get('/materials/filter-options')
    filterOptions.value = res || { brands: [], units: [], env_levels: [] }
  } catch (e) { console.error('获取筛选选项失败', e) }
}

// 打开抽屉
const openCustomize = async (product) => {
  drawer.product = product
  drawer.variants = []
  drawer.selectedVariant = null
  drawer.customOptions = buildCustomOptions(product)
  drawer.customValues = {}
  drawer.customPriceDeltas = {}
  drawer.quantity = 1
  drawer.spaceName = '客厅'
  drawer.visible = true
  document.body.style.overflow = 'hidden'
}

const buildCustomOptions = (product) => {
  const opts = []
  if (product.color_options) {
    try { const colors = JSON.parse(product.color_options); if (colors.length) opts.push({ key:'color', label:'颜色', type:'color', choices:colors }) } catch(e){}
  }
  if (product.material_options) {
    try { const mats = JSON.parse(product.material_options); if (mats.length) opts.push({ key:'material', label:'材质', type:'select', choices:mats }) } catch(e){}
  }
  if (product.size_options) {
    try { const sizes = JSON.parse(product.size_options); if (sizes.length) opts.push({ key:'size', label:'尺寸', type:'select', choices:sizes }) } catch(e){}
  }
  if (!opts.length && product.specification) {
    opts.push({
      key: 'color', label: '颜色', type: 'color',
      choices: [
        { value: 'natural', label: '原木色', hex: '#C8A882' },
        { value: 'walnut', label: '胡桃色', hex: '#8B6914' },
        { value: 'white', label: '哑白', hex: '#f0ece4' },
        { value: 'black', label: '哑黑', hex: '#2C2C2C' }
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
const changeQty = (delta) => { drawer.quantity = Math.max(1, drawer.quantity + delta) }
const closeDrawer = () => { drawer.visible = false; document.body.style.overflow = '' }

// 加入选品
const confirmAdd = () => {
  if (!drawer.product) return
  addItem({
    id: drawer.product.id, type: 'product',
    name: drawer.product.name, sku_code: drawer.product.sku_code,
    image: drawer.product.main_image, price: Number(drawer.product.sale_price || 0),
    unit: drawer.product.unit, brand: drawer.product.brand,
    specification: drawer.product.specification, space_name: drawer.spaceName,
    quantity: drawer.quantity, custom_options: { ...drawer.customValues },
  })
  ElMessage.success('✓ 已加入选品单')
  closeDrawer()
}

const quickAdd = (product) => {
  addItem({
    id: product.id, type: 'product', name: product.name,
    image: product.main_image, price: Number(product.sale_price || 0),
    unit: product.unit, brand: product.brand, space_name: '客厅', quantity: 1
  })
  ElMessage.success(`✓ ${product.name} 已加入选品单`)
}

// 滚动粘性
const handleScroll = () => {
  if (!catBarRef.value) return
  catSticky.value = window.scrollY > 120
}

onMounted(() => {
  fetchCategories()
  fetchFilterOptions()
  fetchProducts()
  window.addEventListener('scroll', handleScroll, { passive: true })
})
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ===== 全局 ===== */
.product-page {
  min-height: 100vh;
  background: #FAFAFA;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: #1a1a1a;
}

/* ===== 页面标题栏 ===== */
.page-header {
  position: relative;
  padding: 110px 80px 56px;
  overflow: hidden;
}
.header-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 50% at 50% 40%, rgba(64,158,255,0.04) 0%, transparent 70%);
  pointer-events: none;
}
.header-inner {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
}
.header-eyebrow {
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #409EFF;
  margin: 0 0 16px;
  font-weight: 500;
}
.page-title {
  font-size: 42px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px;
  letter-spacing: -1px;
  line-height: 1.2;
}
.page-sub {
  font-size: 15px;
  color: #666;
  margin: 0 auto 24px;
  line-height: 1.7;
  max-width: 520px;
  font-weight: 300;
}
.sub-br { display: none; }
.header-line {
  width: 48px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #409EFF, transparent);
  border-radius: 1px;
  margin: 0 auto;
}

/* ===== 分类栏 ===== */
.cat-bar {
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(0,0,0,0.06);
  padding: 0 80px;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 200;
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.cat-bar.sticky {
  position: sticky;
  top: 64px;
  z-index: 100;
  box-shadow: 0 4px 32px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.02);
  border-bottom-color: transparent;
  padding-top: 14px;
  padding-bottom: 14px;
}
.cat-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 10px 0;
  flex: 1;
}
.cat-btn {
  background: none;
  border: none;
  padding: 7px 18px;
  font-size: 13px;
  color: #999;
  cursor: pointer;
  border-radius: 980px;
  white-space: nowrap;
  transition: all 0.25s ease;
  font-weight: 400;
  height: 34px;
  line-height: 20px;
}
.cat-btn:hover { color: #333; background: rgba(0,0,0,0.04); }
.cat-btn.active {
  color: #1a1a1a;
  background: rgba(0,0,0,0.06);
  font-weight: 500;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.06);
}
.cat-btn.cat-parent {
  font-weight: 500;
  color: #555;
}
.cat-btn.cat-parent.active {
  color: #409EFF;
  background: rgba(64,158,255,0.08);
  box-shadow: none;
}
.cat-btn.cat-child {
  font-size: 12.5px;
  font-weight: 400;
  color: #aaa;
  padding: 5px 14px;
  height: 30px;
}
.cat-btn.cat-child::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #ccc;
  margin-right: 6px;
  vertical-align: middle;
}
.cat-btn.cat-child:hover { color: #666; }
.cat-btn.cat-child.active {
  color: #409EFF;
  background: rgba(64,158,255,0.06);
}
.cat-stat {
  font-size: 12px;
  color: #bbb;
  white-space: nowrap;
  padding-left: 16px;
  border-left: 1px solid rgba(0,0,0,0.06);
  margin-left: 4px;
  flex-shrink: 0;
}

/* ===== 产品区 ===== */
.products-wrap {
  padding: 40px 80px 100px;
  max-width: 1440px;
  margin: 0 auto;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
}

/* ===== 产品卡片 ===== */
.product-card {
  background: #FFFFFF;
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1), box-shadow 0.35s ease;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.05);
}
.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
}
.product-card.in-selection {
  border-color: rgba(64,158,255,0.3);
  box-shadow: 0 0 20px rgba(64,158,255,0.06);
}
.card-img-wrap {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  background: #f5f5f5;
  border-radius: 16px 16px 0 0;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4,0,0.2,1);
}
.product-card:hover .card-img {
  transform: scale(1.06);
}
.card-img-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0;
}
.card-img-placeholder svg { stroke: #ccc; }

/* 悬浮覆盖层 */
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 16px 16px 0 0;
}
.overlay-btn {
  padding: 10px 30px;
  border-radius: 980px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  border: none;
  letter-spacing: 0.3px;
}
.overlay-btn.primary {
  background: #FFFFFF;
  color: #1a1a1a;
  font-weight: 600;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.overlay-btn.primary:hover { background: #333; transform: scale(1.02); }
.overlay-btn.ghost {
  background: rgba(0,0,0,0.55);
  color: #FFFFFF;
  border: 1px solid rgba(255,255,255,0.35);
  font-weight: 500;
  backdrop-filter: blur(4px);
}
.overlay-btn.ghost:hover { background: rgba(0,0,0,0.06); }

/* 已选标记 */
.selected-badge {
  position: absolute;
  top: 14px; left: 14px;
  background: rgba(64,158,255,0.92);
  backdrop-filter: blur(8px);
  color: #fff;
  padding: 4px 12px;
  border-radius: 980px;
  font-size: 11px;
  font-weight: 600;
  display: flex; align-items: center; gap: 5px;
}
.badge-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #fff;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 卡片信息区 */
.card-body {
  padding: 18px 20px 22px;
}
.card-brand {
  font-size: 10.5px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: #409EFF;
  margin: 0 0 6px;
  font-weight: 600;
  opacity: 0.85;
}
.card-name {
  font-size: 14.5px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 10px;
  line-height: 1.45;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.card-meta {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.card-price {
  font-size: 17px;
  font-weight: 650;
  color: #1a1a1a;
  letter-spacing: -0.3px;
}
.card-unit {
  font-size: 12px;
  color: #999;
  font-weight: 400;
}

/* 骨架屏 */
.skeleton { pointer-events: none; }
.skeleton-img {
  aspect-ratio: 1/1;
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s infinite;
  border-radius: 16px 16px 0 0;
}
.skeleton-line {
  height: 14px;
  border-radius: 6px;
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s infinite;
  margin-bottom: 8px;
}
.w70 { width: 70%; }
.w40 { width: 40%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 加载更多 */
.load-more-wrap { padding: 56px 0; text-align: center; }
.load-more-btn {
  background: none;
  border: 1px solid rgba(0,0,0,0.08);
  color: #999;
  padding: 13px 44px;
  font-size: 13px;
  border-radius: 980px;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}
.load-more-btn:hover {
  border-color: rgba(0,0,0,0.18);
  color: #555;
  background: rgba(0,0,0,0.02);
}
.load-more-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.empty {
  padding: 100px 0;
  text-align: center;
  color: #bbb;
  font-size: 15px;
  display: flex; flex-direction: column; align-items: center; gap: 16px;
}
.empty svg { stroke: #ccc; }

/* ===== 抽屉 ===== */
.drawer-mask {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex; align-items: flex-end;
}
.drawer {
  width: 100%;
  max-height: 92vh;
  background: #FFFFFF;
  display: flex; flex-direction: column;
  position: relative;
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -12px 60px rgba(0,0,0,0.12);
}
.drawer-close {
  position: absolute;
  top: 16px; right: 16px;
  background: rgba(0,0,0,0.04);
  border: none;
  width: 32px; height: 32px;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  z-index: 10;
  color: #999;
  transition: background 0.2s;
}
.drawer-close:hover { background: rgba(0,0,0,0.1); color: #333; }
.drawer-scroll {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}
.drawer-hero {
  width: 100%;
  height: 280px;
  overflow: hidden;
  position: relative;
  border-radius: 24px 24px 0 0;
  background: #f5f5f5;
}
.drawer-main-img { width: 100%; height: 100%; object-fit: cover; }
.drawer-img-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0;
}
.drawer-img-placeholder svg { stroke: #ccc; }
.drawer-info-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 20px 24px;
  background: linear-gradient(transparent, rgba(255,255,255,0.95));
  color: #1a1a1a;
}
.drawer-brand { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #409EFF; margin: 0 0 4px; }
.drawer-name { font-size: 19px; font-weight: 600; margin: 0; line-height: 1.3; color: #1a1a1a; }

.drawer-section {
  padding: 20px 28px 0;
  border-top: 1px solid rgba(0,0,0,0.05);
  margin-top: 20px;
}
.section-title {
  font-size: 11px;
  font-weight: 600;
  color: #999;
  margin: 0 0 14px;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.variant-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.variant-btn {
  border: 1.5px solid rgba(0,0,0,0.08);
  background: #fafafa;
  padding: 11px 14px;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  display: flex; justify-content: space-between; align-items: center;
  color: #555;
}
.variant-btn:hover { border-color: rgba(64,158,255,0.3); }
.variant-btn.active { border-color: #409EFF; background: rgba(64,158,255,0.04); color: #1a1a1a; }
.v-name { font-size: 13px; }
.v-price { font-size: 12px; color: #409EFF; font-weight: 600; }

.color-picker { display: flex; gap: 10px; flex-wrap: wrap; }
.color-dot {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 2.5px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  outline: 2.5px solid transparent;
  outline-offset: 2px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.color-dot:hover { transform: scale(1.12); }
.color-dot.active { outline-color: #409EFF; }

.opt-chips, .space-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.opt-chip {
  border: 1.5px solid rgba(0,0,0,0.08);
  background: #fafafa;
  padding: 8px 16px;
  border-radius: 980px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.opt-chip:hover { border-color: rgba(0,0,0,0.15); color: #333; }
.opt-chip.active { border-color: #409EFF; background: rgba(64,158,255,0.06); color: #409EFF; font-weight: 500; }

.qty-row { display: flex; align-items: center; gap: 20px; }
.qty-btn {
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(0,0,0,0.1);
  background: #fff;
  font-size: 17px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  color: #555;
}
.qty-btn:hover:not(:disabled) { border-color: #409EFF; color: #409EFF; }
.qty-btn:disabled { opacity: 0.25; cursor: not-allowed; }
.qty-btn.sm { width: 26px; height: 26px; font-size: 13px; }
.qty-val { font-size: 17px; font-weight: 600; color: #1a1a1a; min-width: 32px; text-align: center; }
.qty-val.sm { font-size: 14px; min-width: 24px; }

.drawer-footer {
  padding: 18px 28px;
  border-top: 1px solid rgba(0,0,0,0.05);
  background: #fff;
}
.price-summary { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.price-label { font-size: 13px; color: #999; }
.price-total { font-size: 24px; font-weight: 700; color: #1a1a1a; }
.add-to-selection-btn {
  width: 100%;
  background: #1a1a1a;
  color: #fff;
  border: none;
  padding: 15px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.3px;
}
.add-to-selection-btn:hover {
  background: #333;
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
}

/* 选品单 */
.selection-title { font-size: 20px; font-weight: 700; color: #1a1a1a; padding: 28px 28px 4px; margin: 0; }
.selection-sub { font-size: 13px; color: #999; padding: 0 28px 20px; margin: 0; }
.selection-empty { padding: 60px 28px; text-align: center; color: #ccc; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.selection-empty svg { stroke: #ddd; }
.selection-empty p { margin: 0; color: #999; }
.selection-items { padding: 0 28px; display: flex; flex-direction: column; gap: 10px; }
.sel-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; background: #fafafa; border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.03);
}
.sel-img { width: 58px; height: 58px; object-fit: cover; border-radius: 10px; flex-shrink: 0; }
.sel-img-placeholder {
  width: 58px; height: 58px; background: #f0f0f0; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sel-img-placeholder svg { stroke: #ccc; }
.sel-info { flex: 1; min-width: 0; }
.sel-name { font-size: 13px; font-weight: 500; color: #1a1a1a; margin: 0 0 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sel-space { font-size: 11px; color: #409EFF; margin: 0 0 8px; }
.sel-qty-row { display: flex; align-items: center; gap: 6px; }
.sel-price { font-size: 13px; font-weight: 600; color: #1a1a1a; margin-left: auto; }
.sel-remove {
  background: none; border: none; color: #ccc; font-size: 14px;
  cursor: pointer; padding: 4px; flex-shrink: 0; transition: color 0.2s;
}
.sel-remove:hover { color: #ff3b30; }

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.drawer-slide-enter-active, .drawer-slide-leave-active { transition: all 0.4s cubic-bezier(0.4,0,0.2,1); }
.drawer-slide-enter-from .drawer, .drawer-slide-leave-to .drawer { transform: translateY(100%); }

/* 固定悬浮选品按钮 */
.selection-float {
  position: fixed;
  right: 32px;
  bottom: 32px;
  z-index: 99;
}

/* ===== 响应式 ===== */
@media (max-width: 1280px) {
  .page-header { padding: 90px 48px 44px; }
  .page-title { font-size: 36px; }
  .cat-bar { padding: 0 48px; }
  .products-wrap { padding: 32px 48px 80px; }
  .product-grid { grid-template-columns: repeat(3, 1fr); gap: 24px; }
}

@media (max-width: 900px) {
  .page-header { padding: 80px 28px 36px; }
  .page-title { font-size: 30px; }
  .page-sub { font-size: 14px; }
  .sub-br { display: inline; }
  .cat-bar { padding: 0 28px; }
  .products-wrap { padding: 24px 28px 60px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); gap: 18px; }
  .drawer { max-height: 95vh; border-radius: 20px 20px 0 0; }
}

@media (max-width: 480px) {
  .page-header { padding: 72px 20px 28px; }
  .page-title { font-size: 26px; }
  .cat-bar { padding: 0 20px; }
  .products-wrap { padding: 20px 16px 60px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .card-body { padding: 12px 14px 16px; }
  .card-name { font-size: 13px; }
  .card-price { font-size: 15px; }
}

/* ===== 筛选栏 ===== */
.filter-bar {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding: 14px 80px;
  position: sticky;
  top: 112px;
  z-index: 99;
}
.filter-inner {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F5F5F5;
  border-radius: 980px;
  padding: 8px 16px;
  flex: 1;
  max-width: 420px;
}
.search-box svg { flex-shrink: 0; }
.search-input {
  border: none;
  background: none;
  outline: none;
  font-size: 13px;
  color: #1a1a1a;
  width: 100%;
  font-family: inherit;
}
.search-input::placeholder { color: #999; }
.filter-selects {
  display: flex;
  gap: 8px;
}
.filter-select {
  appearance: none;
  -webkit-appearance: none;
  background: #F5F5F5;
  border: none;
  border-radius: 980px;
  padding: 8px 32px 8px 16px;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23999'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 10px 6px;
}
.filter-select:hover { background-color: #EBEBEB; }

</style>
