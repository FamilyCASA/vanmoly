<template>
  <div class="product-detail-v2">
    <Navbar />
    
    <div class="product-container">
      <!-- 面包屑 -->
      <el-breadcrumb class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/products' }">产品中心</el-breadcrumb-item>
        <el-breadcrumb-item>{{ product.name }}</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="product-main" v-loading="loading">
        <!-- 左侧图片区 -->
        <div class="product-gallery">
          <div class="main-image">
            <el-image :src="selectedImage || product.main_image" fit="cover" />
            <div v-if="selectedVariant" class="variant-badge">{{ selectedVariant.variant_name }}</div>
          </div>
          <div class="thumbnail-list">
            <div 
              v-for="(img, idx) in galleryImages" 
              :key="idx"
              class="thumb-item"
              :class="{ active: selectedImage === img }"
              @click="selectedImage = img"
            >
              <el-image :src="img" fit="cover" />
            </div>
          </div>
        </div>

        <!-- 右侧信息区 -->
        <div class="product-info">
          <h1 class="product-name">{{ product.name }}</h1>
          <p class="product-desc">{{ product.description }}</p>
          
          <div class="product-meta">
            <div class="meta-item">
              <span class="meta-label">品牌</span>
              <span class="meta-value">{{ product.brand || 'D&B 帝标|设记家' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">型号</span>
              <span class="meta-value">{{ product.model || product.sku_code }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">材质</span>
              <span class="meta-value">{{ product.material || '实木' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">规格</span>
              <span class="meta-value">{{ product.specification || '标准尺寸' }}</span>
            </div>
          </div>

          <!-- 价格区 -->
          <div class="price-section">
            <div class="price-row">
              <span class="price-label">销售价</span>
              <span class="price-value sale">¥{{ displayPrice }}</span>
            </div>
            <div v-if="product.market_price" class="price-row">
              <span class="price-label">市场价</span>
              <span class="price-value market">¥{{ product.market_price }}</span>
            </div>
          </div>

          <!-- 变体选择 -->
          <div v-if="product.has_variants && product.variants?.length > 0" class="variant-section">
            <h3>选择花色</h3>
            <div class="variant-list">
              <div 
                v-for="variant in product.variants" 
                :key="variant.id"
                class="variant-item"
                :class="{ active: selectedVariant?.id === variant.id, disabled: !variant.is_enabled }"
                @click="selectVariant(variant)"
              >
                <el-image v-if="variant.image" :src="variant.image" fit="cover" />
                <div v-else class="variant-placeholder">{{ variant.variant_name.slice(0, 2) }}</div>
                <span class="variant-name">{{ variant.variant_name }}</span>
                <span v-if="variant.price_adjustment !== 0" class="variant-price">
                  {{ variant.price_adjustment > 0 ? '+' : '' }}¥{{ variant.price_adjustment }}
                </span>
              </div>
            </div>
          </div>

          <!-- 数量选择 -->
          <div class="quantity-section">
            <span class="section-label">数量</span>
            <el-input-number v-model="quantity" :min="1" :max="99" />
            <span class="unit">{{ product.unit || '件' }}</span>
            <span v-if="selectedVariant?.stock_quantity > 0" class="stock-info">
              库存 {{ selectedVariant.stock_quantity }}
            </span>
            <span v-else-if="product.stock_quantity > 0" class="stock-info">
              库存 {{ product.stock_quantity }}
            </span>
          </div>

          <!-- 操作按钮 -->
          <div class="action-section">
            <el-button type="primary" size="large" @click="addToSelection">
              <el-icon><Plus /></el-icon>加入选品清单
            </el-button>
            <el-button size="large" @click="openConsult">
              <el-icon><ChatDotRound /></el-icon>咨询客服
            </el-button>
          </div>

          <!-- 社交分享 -->
          <div class="share-section">
            <span class="share-label">分享到</span>
            <div class="share-buttons">
              <button class="share-btn wechat" @click="shareToWechat">
                <el-icon><ChatDotRound /></el-icon>
                <span>微信</span>
              </button>
              <button class="share-btn moments" @click="shareToMoments">
                <el-icon><Share /></el-icon>
                <span>朋友圈</span>
              </button>
              <button class="share-btn copy" @click="copyLink">
                <el-icon><Link /></el-icon>
                <span>复制链接</span>
              </button>
            </div>
          </div>

          <!-- 服务承诺 -->
          <div class="service-tags">
            <el-tag type="info" effect="plain"><el-icon><Check /></el-icon>正品保证</el-tag>
            <el-tag type="info" effect="plain"><el-icon><Check /></el-icon>免费配送</el-tag>
            <el-tag type="info" effect="plain"><el-icon><Check /></el-icon>售后无忧</el-tag>
          </div>
        </div>
      </div>

      <!-- 详情内容区 -->
      <div class="product-detail-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="详情介绍" name="detail">
            <div v-if="product.detail_content" class="rich-content" v-html="product.detail_content"></div>
            <div v-else class="empty-content">
              <el-empty description="暂无详情介绍" />
            </div>
          </el-tab-pane>
          <el-tab-pane label="规格参数" name="specs">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="SKU编码">{{ product.sku_code }}</el-descriptions-item>
              <el-descriptions-item label="品牌">{{ product.brand || '-' }}</el-descriptions-item>
              <el-descriptions-item label="型号">{{ product.model || '-' }}</el-descriptions-item>
              <el-descriptions-item label="材质">{{ product.material || '-' }}</el-descriptions-item>
              <el-descriptions-item label="规格">{{ product.specification || '-' }}</el-descriptions-item>
              <el-descriptions-item label="产地">{{ product.origin || '-' }}</el-descriptions-item>
              <el-descriptions-item label="单位">{{ product.unit || '件' }}</el-descriptions-item>
              <el-descriptions-item label="计价方式">
                {{ { quantity: '按数量', area: '按面积', length: '按长度' }[product.calc_type] || '按数量' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          <el-tab-pane label="变体信息" name="variants" v-if="product.has_variants">
            <el-table :data="product.variants || []" border>
              <el-table-column prop="variant_name" label="变体名称" />
              <el-table-column label="属性">
                <template #default="{ row }">
                  <el-tag v-for="(val, key) in row.variant_values" :key="key" size="small" style="margin-right: 5px">
                    {{ key }}: {{ val }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="price_adjustment" label="价格调整" width="120">
                <template #default="{ row }">
                  {{ row.price_adjustment > 0 ? '+' : '' }}¥{{ row.price_adjustment }}
                </template>
              </el-table-column>
              <el-table-column prop="stock_quantity" label="库存" width="100" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ChatDotRound, Check, Share, Link } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const product = ref({})
const selectedImage = ref('')
const selectedVariant = ref(null)
const quantity = ref(1)
const activeTab = ref('detail')

// 图库图片（主图 + 辅图 + 变体图）
const galleryImages = computed(() => {
  const images = []
  if (product.value.main_image) images.push(product.value.main_image)
  if (product.value.images?.length) images.push(...product.value.images)
  if (product.value.variants?.length) {
    product.value.variants.forEach(v => {
      if (v.image && !images.includes(v.image)) images.push(v.image)
    })
  }
  return images.length > 0 ? images : ['/placeholder.png']
})

// 显示价格（基础价 + 变体调整）
const displayPrice = computed(() => {
  const basePrice = parseFloat(product.value.sale_price) || 0
  const adjustment = parseFloat(selectedVariant.value?.price_adjustment) || 0
  return (basePrice + adjustment).toFixed(2)
})

// 加载产品详情
const loadProduct = async () => {
  loading.value = true
  try {
    const res = await request.get(`/materials/${route.params.id}`)
    product.value = res.data || {}
    selectedImage.value = product.value.main_image
    
    // 默认选中第一个启用的变体
    if (product.value.variants?.length > 0) {
      selectedVariant.value = product.value.variants.find(v => v.is_enabled) || product.value.variants[0]
    }
  } catch (error) {
    ElMessage.error('加载产品详情失败')
  } finally {
    loading.value = false
  }
}

// 选择变体
const selectVariant = (variant) => {
  if (!variant.is_enabled) return
  selectedVariant.value = variant
  if (variant.image) {
    selectedImage.value = variant.image
  }
}

// 加入选品清单
const addToSelection = () => {
  const selection = JSON.parse(localStorage.getItem('selection') || '[]')
  
  const item = {
    id: product.value.id,
    sku_code: product.value.sku_code,
    name: product.value.name,
    main_image: selectedVariant.value?.image || product.value.main_image,
    variant_id: selectedVariant.value?.id,
    variant_name: selectedVariant.value?.variant_name,
    sale_price: displayPrice.value,
    quantity: quantity.value,
    unit: product.value.unit || '件',
    added_at: new Date().toISOString()
  }
  
  // 检查是否已存在
  const exists = selection.find(s => 
    s.id === item.id && s.variant_id === item.variant_id
  )
  
  if (exists) {
    exists.quantity += item.quantity
    ElMessage.success('已更新数量')
  } else {
    selection.push(item)
    ElMessage.success('已加入选品清单')
  }
  
  localStorage.setItem('selection', JSON.stringify(selection))
}

// 打开咨询
const openConsult = () => {
  // 可以跳转到客服页面或打开咨询弹窗
  ElMessage.info('客服功能开发中，请拨打：400-888-8888')
}

// 分享到微信
const shareToWechat = () => {
  const shareData = {
    title: product.value.name,
    desc: product.value.description?.slice(0, 50) + '...',
    link: window.location.href,
    imgUrl: product.value.main_image
  }
  
  // 生成分享二维码/链接
  ElMessageBox.alert(
    `<div style="text-align:center">
      <p>请使用微信扫一扫分享</p>
      <div style="margin:20px 0;padding:20px;background:#f5f5f5;border-radius:8px">
        <p style="font-size:12px;color:#999;word-break:break-all">${shareData.link}</p>
      </div>
    </div>`,
    '分享到微信',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '复制链接',
      callback: () => copyLink()
    }
  )
}

// 分享到朋友圈
const shareToMoments = () => {
  shareToWechat() // 微信朋友圈也使用同样的分享方式
}

// 复制链接
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success('链接已复制到剪贴板')
  } catch (err) {
    // 降级方案
    const input = document.createElement('input')
    input.value = window.location.href
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    ElMessage.success('链接已复制到剪贴板')
  }
}

// 设置页面分享元数据（用于微信等社交平台抓取）
const setShareMeta = () => {
  const title = `${product.value.name} - D&B 帝标|设记家全案服务`
  const desc = product.value.description?.slice(0, 100) || '精选优质家居产品'
  const image = product.value.main_image
  
  // 更新页面标题
  document.title = title
  
  // 更新 meta 标签
  const metas = [
    { name: 'description', content: desc },
    { property: 'og:title', content: title },
    { property: 'og:description', content: desc },
    { property: 'og:image', content: image },
    { property: 'og:url', content: window.location.href },
    { property: 'og:type', content: 'product' }
  ]
  
  metas.forEach(meta => {
    let tag = document.querySelector(`meta[name="${meta.name}"], meta[property="${meta.property}"]`)
    if (!tag) {
      tag = document.createElement('meta')
      if (meta.name) tag.setAttribute('name', meta.name)
      if (meta.property) tag.setAttribute('property', meta.property)
      document.head.appendChild(tag)
    }
    tag.setAttribute('content', meta.content)
  })
}

onMounted(() => {
  loadProduct().then(() => {
    setShareMeta()
  })
})
</script>

<style scoped>
.product-detail-v2 {
  min-height: 100vh;
  background: #f5f5f5;
}

.product-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

/* 主产品区 */
.product-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

/* 图片画廊 */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.main-image {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f8f8;
}

.main-image :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.main-image :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.variant-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(139, 90, 43, 0.9);
  color: #fff;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.thumb-item {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.thumb-item.active {
  border-color: #8B5A2B;
}

.thumb-item :deep(.el-image) {
  width: 100%;
  height: 100%;
}

/* 产品信息 */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-name {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.product-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.product-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 15px;
  background: #f8f8f8;
  border-radius: 6px;
}

.meta-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.meta-label {
  color: #999;
}

.meta-value {
  color: #333;
  font-weight: 500;
}

/* 价格区 */
.price-section {
  padding: 20px;
  background: linear-gradient(135deg, #fdf6f0 0%, #f9f0e8 100%);
  border-radius: 8px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.price-row:not(:last-child) {
  margin-bottom: 8px;
}

.price-label {
  font-size: 13px;
  color: #999;
}

.price-value.sale {
  font-size: 28px;
  font-weight: bold;
  color: #8B5A2B;
}

.price-value.market {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

/* 变体选择 */
.variant-section h3 {
  font-size: 14px;
  color: #333;
  margin: 0 0 12px 0;
}

.variant-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.variant-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 8px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  min-width: 80px;
  transition: all 0.2s;
}

.variant-item:hover {
  border-color: #c0a080;
}

.variant-item.active {
  border-color: #8B5A2B;
  background: #fdf6f0;
}

.variant-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.variant-item :deep(.el-image) {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.variant-placeholder {
  width: 50px;
  height: 50px;
  background: #f0f0f0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #999;
}

.variant-name {
  font-size: 12px;
  color: #333;
  text-align: center;
}

.variant-price {
  font-size: 11px;
  color: #8B5A2B;
}

/* 数量选择 */
.quantity-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.section-label {
  font-size: 14px;
  color: #333;
}

.unit {
  font-size: 13px;
  color: #666;
}

.stock-info {
  font-size: 12px;
  color: #67c23a;
}

/* 操作按钮 */
.action-section {
  display: flex;
  gap: 15px;
}

.action-section .el-button {
  flex: 1;
}

.action-section .el-button--primary {
  background: #8B5A2B;
  border-color: #8B5A2B;
}

.action-section .el-button--primary:hover {
  background: #6d4620;
  border-color: #6d4620;
}

/* 服务标签 */
.service-tags {
  display: flex;
  gap: 10px;
}

.service-tags .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 社交分享 */
.share-section {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-top: 15px;
  border-top: 1px dashed #e0e0e0;
}

.share-label {
  font-size: 13px;
  color: #999;
}

.share-buttons {
  display: flex;
  gap: 10px;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: #fff;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.share-btn:hover {
  border-color: #8B5A2B;
  color: #8B5A2B;
  background: #fdf6f0;
}

.share-btn.wechat:hover {
  border-color: #07c160;
  color: #07c160;
  background: #f0f9f4;
}

.share-btn.moments:hover {
  border-color: #07c160;
  color: #07c160;
  background: #f0f9f4;
}

/* 详情内容区 */
.product-detail-content {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
}

.rich-content {
  line-height: 1.8;
  color: #333;
}

.rich-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 15px 0;
}

.rich-content :deep(h2), .rich-content :deep(h3) {
  color: #333;
  margin: 20px 0 15px;
}

.rich-content :deep(p) {
  margin: 10px 0;
}

.rich-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.rich-content :deep(th), .rich-content :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 10px;
  text-align: left;
}

.rich-content :deep(th) {
  background: #f5f5f5;
}

.empty-content {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .product-main {
    grid-template-columns: 1fr;
  }
  
  .product-meta {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
}
</style>
