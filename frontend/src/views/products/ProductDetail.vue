<template>
  <div class="product-detail-page">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-text">D&B 帝标|设记家</router-link>
      </div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/cases">案例展示</router-link>
        <router-link to="/products">产品中心</router-link>
        <router-link to="/book">预约量尺</router-link>
      </div>
      <div class="nav-actions">
        <router-link to="/selection-center" class="selection-link">
          <el-icon><ShoppingBag /></el-icon>
          选品清单
          <span v-if="selectionCount > 0" class="badge">{{ selectionCount }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 产品详情 -->
    <div v-else-if="product" class="product-content">
      <div class="container">
        <!-- 面包屑 -->
        <el-breadcrumb class="breadcrumb">
          <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
          <el-breadcrumb-item to="/products">产品中心</el-breadcrumb-item>
          <el-breadcrumb-item>{{ product.name }}</el-breadcrumb-item>
        </el-breadcrumb>

        <!-- 产品主图和信息 -->
        <div class="product-main">
          <div class="product-gallery">
            <div class="main-image">
              <img v-if="currentImage" :src="currentImage" :alt="product.name">
              <div v-else class="no-image">
                <el-icon :size="64"><Picture /></el-icon>
              </div>
            </div>
            <div class="thumbnail-list" v-if="product.images && product.images.length > 0">
              <div
                v-for="(img, index) in product.images"
                :key="index"
                class="thumbnail"
                :class="{ active: currentImage === img }"
                @click="currentImage = img"
              >
                <img :src="img" :alt="product.name">
              </div>
            </div>
          </div>

          <div class="product-info">
            <h1 class="product-title">{{ product.name }}</h1>
            <p class="product-subtitle" v-if="product.brand || product.model">
              {{ product.brand }} {{ product.model }}
            </p>

            <div class="product-price-box">
              <div class="price-row">
                <span class="price-label">销售价</span>
                <span class="price-value">
                  <span class="symbol">¥</span>
                  <span class="number">{{ formatPrice(product.sale_price) }}</span>
                  <span class="unit">/{{ product.unit || '件' }}</span>
                </span>
              </div>
              <div class="price-row market" v-if="product.market_price">
                <span class="price-label">市场价</span>
                <span class="market-price">¥{{ formatPrice(product.market_price) }}</span>
              </div>
              <div class="price-row cost" v-if="isAdmin">
                <span class="price-label">成本价</span>
                <span class="cost-price">¥{{ formatPrice(product.cost_price) }}</span>
              </div>
            </div>

            <div class="product-meta">
              <div class="meta-item">
                <span class="meta-label">分类</span>
                <span class="meta-value">{{ product.category_name || '-' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">计价方式</span>
                <span class="meta-value">{{ calcTypeLabel(product.calc_type) }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">库存</span>
                <span class="meta-value" :class="{ 'low-stock': product.stock_quantity < product.stock_warning }">
                  {{ product.stock_quantity || 0 }} {{ product.unit || '件' }}
                </span>
              </div>
              <div class="meta-item" v-if="product.origin">
                <span class="meta-label">产地</span>
                <span class="meta-value">{{ product.origin }}</span>
              </div>
              <div class="meta-item" v-if="product.material">
                <span class="meta-label">材质</span>
                <span class="meta-value">{{ product.material }}</span>
              </div>
              <div class="meta-item" v-if="product.specification">
                <span class="meta-label">规格</span>
                <span class="meta-value">{{ product.specification }}</span>
              </div>
            </div>

            <!-- 变体选择 -->
            <div class="variant-section" v-if="product.variants && product.variants.length > 0">
              <h3>选择规格</h3>
              <div class="variant-list">
                <div
                  v-for="variant in product.variants"
                  :key="variant.id"
                  class="variant-item"
                  :class="{ active: selectedVariant?.id === variant.id, disabled: !variant.is_enabled || variant.stock_quantity <= 0 }"
                  @click="selectVariant(variant)"
                >
                  <img v-if="variant.image" :src="variant.image" class="variant-img">
                  <span class="variant-name">{{ variant.variant_name }}</span>
                  <span class="variant-price" v-if="variant.price_adjustment > 0">+¥{{ variant.price_adjustment }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="product-actions">
              <el-button type="primary" size="large" @click="addToSelection">
                <el-icon><ShoppingCart /></el-icon>
                加入选品清单
              </el-button>
              <el-button size="large" @click="consultProduct">
                <el-icon><ChatDotRound /></el-icon>
                咨询产品
              </el-button>
            </div>

            <!-- 产品标签 -->
            <div class="product-tags" v-if="product.tags && product.tags.length > 0">
              <el-tag v-for="tag in product.tags" :key="tag" size="small" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 产品详情 -->
        <div class="product-detail-section">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="产品详情" name="detail">
              <div class="detail-content">
                <div v-if="product.description" class="description" v-html="product.description"></div>
                <div v-else class="empty-description">
                  <el-empty description="暂无详细描述" />
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="定制选项" name="custom" v-if="product.customization_rules && product.customization_rules.length > 0">
              <div class="custom-rules">
                <div v-for="(rule, index) in product.customization_rules" :key="index" class="rule-item">
                  <h4>{{ rule.name }}</h4>
                  <p class="rule-desc">{{ ruleDescription(rule) }}</p>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="相关案例" name="cases">
              <div class="related-cases">
                <el-empty description="暂无相关案例" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-empty description="产品不存在或已下架">
        <el-button type="primary" @click="$router.push('/products')">返回产品列表</el-button>
      </el-empty>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 D&B 帝标|设记家全案落地服务系统 DEMO V.0.1</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Picture, ShoppingCart, ChatDotRound, ShoppingBag } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const route = useRoute()
const router = useRouter()
const { addItem, totalCount } = useAnonymousSelection()

// 状态
const loading = ref(true)
const product = ref(null)
const currentImage = ref('')
const selectedVariant = ref(null)
const activeTab = ref('detail')
const selectionCount = computed(() => totalCount.value)

// 计算属性
const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.role === 'admin' || user.role === 'manager'
})

// 获取产品详情
const fetchProductDetail = async () => {
  const id = route.params.id
  if (!id) {
    router.push('/products')
    return
  }

  loading.value = true
  try {
    const res = await request.get(`/materials/${id}`)
    product.value = res.data
    currentImage.value = res.data.main_image || ''
    
    // 如果有变体，默认选中第一个启用的
    if (res.data.variants && res.data.variants.length > 0) {
      const enabled = res.data.variants.find(v => v.is_enabled && v.stock_quantity > 0)
      if (enabled) selectedVariant.value = enabled
    }
  } catch (error) {
    console.error('获取产品详情失败:', error)
    ElMessage.error('获取产品详情失败')
  } finally {
    loading.value = false
  }
}

// 选择变体
const selectVariant = (variant) => {
  if (!variant.is_enabled || variant.stock_quantity <= 0) return
  selectedVariant.value = variant
  if (variant.image) {
    currentImage.value = variant.image
  }
}

// 加入选品清单
const addToSelection = () => {
  // 使用新的 composable
  const item = {
    id: product.value.id,
    type: 'product',
    name: product.value.name,
    sku_code: product.value.sku_code,
    image: product.value.main_image,
    price: product.value.sale_price,
    unit: product.value.unit,
    brand: product.value.brand,
    specification: product.value.specification,
    space_name: '未分类' // 默认空间
  }
  
  addItem(item)
  ElMessage.success(`已加入选品清单，共 ${totalCount.value} 件产品`)
}

// 咨询产品
const consultProduct = () => {
  router.push('/book')
}

// 格式化价格
const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00'
  return Number(price).toFixed(2)
}

// 计价方式标签
const calcTypeLabel = (type) => {
  const map = {
    quantity: '按件计价',
    area: '按面积 (㎡)',
    length: '按长度 (m)',
    weight: '按重量 (kg)'
  }
  return map[type] || type
}

// 规则描述
const ruleDescription = (rule) => {
  const typeMap = {
    coefficient: `系数计算，默认系数: ${rule.default || 1}`,
    fee: `固定费用，默认: ¥${rule.default || 0}`,
    increment: `增量计算，步进值: ${rule.default || 0}`
  }
  return typeMap[rule.type] || rule.type
}

onMounted(() => {
  fetchProductDetail()
})
</script>

<style scoped>
.product-detail-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 导航栏 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5%;
  height: 64px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand .brand-text {
  font-size: 24px;
  font-weight: 600;
  color: #8B5A2B;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: #666;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
}

.nav-links a:hover,
.nav-links a.active {
  color: #8B5A2B;
}

.nav-actions {
  display: flex;
  align-items: center;
}

.selection-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s;
}

.selection-link:hover {
  background: #f5f5f5;
  color: #8B5A2B;
}

.badge {
  background: #f56c6c;
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  padding: 60px 5%;
  max-width: 1200px;
  margin: 0 auto;
}

/* 产品内容 */
.product-content {
  padding: 20px 5% 60px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 20px;
}

/* 产品主区域 */
.product-main {
  display: grid;
  grid-template-columns: 480px 1fr;
  gap: 40px;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 30px;
}

/* 产品图库 */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-image {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #ccc;
}

.thumbnail-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.thumbnail.active {
  border-color: #8B5A2B;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 产品信息 */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.product-subtitle {
  font-size: 16px;
  color: #999;
  margin: 0;
}

/* 价格区域 */
.product-price-box {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
}

.price-row:last-child {
  margin-bottom: 0;
}

.price-label {
  font-size: 14px;
  color: #666;
  width: 60px;
}

.price-value {
  color: #f56c6c;
}

.price-value .symbol {
  font-size: 18px;
}

.price-value .number {
  font-size: 32px;
  font-weight: 600;
}

.price-value .unit {
  font-size: 14px;
  color: #999;
}

.market-price {
  color: #999;
  text-decoration: line-through;
  font-size: 14px;
}

.cost-price {
  color: #67c23a;
  font-size: 14px;
}

/* 产品元信息 */
.product-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.meta-item {
  display: flex;
  gap: 8px;
}

.meta-label {
  color: #999;
  font-size: 14px;
}

.meta-value {
  color: #333;
  font-size: 14px;
}

.meta-value.low-stock {
  color: #f56c6c;
}

/* 变体选择 */
.variant-section h3 {
  font-size: 16px;
  margin-bottom: 12px;
}

.variant-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.variant-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.variant-item:hover:not(.disabled) {
  border-color: #8B5A2B;
}

.variant-item.active {
  border-color: #8B5A2B;
  background: #fdf6f0;
}

.variant-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.variant-img {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 4px;
}

.variant-name {
  font-size: 14px;
}

.variant-price {
  font-size: 12px;
  color: #f56c6c;
}

/* 操作按钮 */
.product-actions {
  display: flex;
  gap: 12px;
}

.product-actions .el-button {
  flex: 1;
}

/* 产品标签 */
.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 详情区域 */
.product-detail-section {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
}

.detail-content {
  min-height: 200px;
}

.description {
  line-height: 1.8;
  color: #333;
}

.empty-description {
  padding: 60px 0;
}

.custom-rules {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.rule-item {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.rule-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.rule-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 页脚 */
.footer {
  background: #333;
  color: #999;
  padding: 24px 5%;
  text-align: center;
}

/* 响应式 */
@media (max-width: 968px) {
  .product-main {
    grid-template-columns: 1fr;
  }
  
  .product-gallery {
    max-width: 480px;
    margin: 0 auto;
  }
}
</style>