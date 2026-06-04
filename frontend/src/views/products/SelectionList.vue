<template>
  <div class="selection-list-page">
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
    </nav>

    <!-- 页面头部 -->
    <header class="page-header">
      <h1>我的选品清单</h1>
      <p>搭配您的专属方案，提交后顾问将为您定制设计</p>
    </header>

    <!-- 清单内容 -->
    <div class="selection-content">
      <div class="container">
        <!-- 空状态 -->
        <div v-if="selection.length === 0" class="empty-state">
          <el-empty description="选品清单为空">
            <template #image>
              <el-icon :size="80" color="#ccc"><ShoppingCart /></el-icon>
            </template>
            <p class="empty-tip">浏览产品中心，将感兴趣的产品加入清单</p>
            <el-button type="primary" @click="$router.push('/products')">
              去选品
            </el-button>
          </el-empty>
        </div>

        <!-- 清单列表 -->
        <template v-else>
          <!-- 方案信息编辑区 -->
          <div class="scheme-section">
            <div class="section-header">
              <h2><el-icon><Edit /></el-icon> 方案信息</h2>
              <p>填写您的需求，帮助我们更好地为您服务</p>
            </div>
            <div class="scheme-form">
              <div class="form-row">
                <div class="form-item">
                  <label>方案名称 <span class="required">*</span></label>
                  <el-input 
                    v-model="scheme.name" 
                    placeholder="如：客厅+卧室定制方案"
                    maxlength="50"
                    show-word-limit
                  />
                </div>
                <div class="form-item">
                  <label>期望风格</label>
                  <el-select v-model="scheme.style" placeholder="选择风格" clearable>
                    <el-option label="现代简约" value="modern" />
                    <el-option label="北欧风" value="nordic" />
                    <el-option label="新中式" value="chinese" />
                    <el-option label="轻奢风" value="luxury" />
                    <el-option label="日式原木" value="japanese" />
                    <el-option label="美式复古" value="american" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </div>
              </div>
              <div class="form-row">
                <div class="form-item">
                  <label>房屋面积</label>
                  <el-input v-model="scheme.area" placeholder="如：120">
                    <template #append>㎡</template>
                  </el-input>
                </div>
                <div class="form-item">
                  <label>装修阶段</label>
                  <el-select v-model="scheme.stage" placeholder="选择阶段" clearable>
                    <el-option label="毛坯房" value="bare" />
                    <el-option label="精装改造" value="renovation" />
                    <el-option label="局部翻新" value="partial" />
                    <el-option label="软装搭配" value="soft" />
                  </el-select>
                </div>
              </div>
              <div class="form-item full-width">
                <label>需求备注</label>
                <el-input 
                  v-model="scheme.remark" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请描述您的特殊需求、预算范围、期望交付时间等..."
                  maxlength="500"
                  show-word-limit
                />
              </div>
            </div>
          </div>

          <!-- 已选产品 - 按空间分组 -->
          <div class="products-section">
            <div class="section-header">
              <h2><el-icon><Goods /></el-icon> 已选产品</h2>
              <div class="section-actions">
                <el-button link @click="$router.push('/products')">
                  <el-icon><Plus /></el-icon> 继续选品
                </el-button>
              </div>
            </div>

            <!-- 空间分组展示 -->
            <div v-for="(roomData, roomName) in groupedByRoom" :key="roomName" class="room-group">
              <div class="room-header">
                <div class="room-title">
                  <el-icon><HomeFilled /></el-icon>
                  <span class="room-name">{{ roomName }}</span>
                  <span class="room-count">{{ roomData.items.length }} 件</span>
                </div>
                <div class="room-amount">
                  小计：¥{{ formatPrice(roomData.subtotal) }}
                </div>
              </div>
              
              <!-- 分类子分组 -->
              <div v-for="(items, category) in roomData.categories" :key="category" class="category-group">
                <div class="category-header">
                  <span class="category-name">{{ category }}</span>
                  <span class="category-count">{{ items.length }} 件</span>
                </div>
                <div class="selection-list">
                  <div
                    v-for="item in items"
                    :key="item.id"
                    class="selection-item"
                  >
                    <div class="item-image" @click="goToDetail(item.id)">
                      <img v-if="item.main_image" :src="item.main_image" :alt="item.name">
                      <div v-else class="no-image">
                        <el-icon :size="32"><Picture /></el-icon>
                      </div>
                    </div>
                    
                    <div class="item-info" @click="goToDetail(item.id)">
                      <h3 class="item-name">{{ item.name }}</h3>
                      <p class="item-spec" v-if="item.specification">{{ item.specification }}</p>
                      <p class="item-brand" v-if="item.brand">{{ item.brand }}</p>
                      <div class="item-meta">
                        <span class="item-category">{{ item.category_level1 }} / {{ item.category_level2 }}</span>
                      </div>
                      <div class="item-price">
                        <span class="price-symbol">¥</span>
                        <span class="price-value">{{ formatPrice(item.sale_price) }}</span>
                        <span class="price-unit">/{{ item.unit || '件' }}</span>
                      </div>
                    </div>

                    <div class="item-actions">
                      <el-input-number 
                        v-model="item.quantity" 
                        :min="1" 
                        :max="99"
                        size="small"
                        @change="updateQuantity(item)"
                      />
                      <div class="item-subtotal">
                        ¥{{ formatPrice((item.sale_price || 0) * (item.quantity || 1)) }}
                      </div>
                      <el-button link type="danger" @click="removeItem(item.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分类汇总 - 与后台报价一致 -->
            <div class="category-summary-section" v-if="categorySummaryList.length > 0">
              <h3><el-icon><List /></el-icon> 分类汇总</h3>
              <div class="category-summary-grid">
                <div 
                  v-for="cat in categorySummaryList" 
                  :key="cat.key"
                  class="category-summary-item"
                  :class="{ 'has-amount': cat.amount > 0 }"
                >
                  <span class="cat-name">{{ cat.name }}</span>
                  <span class="cat-amount">¥{{ formatPrice(cat.amount) }}</span>
                </div>
              </div>
            </div>

            <!-- 费用汇总 - 与后台报价一致 -->
            <div class="selection-summary">
              <div class="summary-grid">
                <div class="summary-item">
                  <span class="summary-label">产品总数</span>
                  <span class="summary-value">{{ totalQuantity }} 件</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">空间数量</span>
                  <span class="summary-value">{{ roomCount }} 个</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">产品种类</span>
                  <span class="summary-value">{{ selection.length }} 种</span>
                </div>
              </div>
              
              <div class="fee-breakdown">
                <div class="fee-row">
                  <span>小计</span>
                  <span>¥{{ formatPrice(summary.subtotal) }}</span>
                </div>
                <div class="fee-row" v-if="summary.managementFee > 0">
                  <span>管理费 ({{ scheme.managementFeeRate || 0 }}%)</span>
                  <span>¥{{ formatPrice(summary.managementFee) }}</span>
                </div>
                <div class="fee-row" v-if="summary.tax > 0">
                  <span>税费 ({{ scheme.taxRate || 0 }}%)</span>
                  <span>¥{{ formatPrice(summary.tax) }}</span>
                </div>
                <div class="fee-row total">
                  <span>参考总价</span>
                  <span class="total-amount">¥{{ formatPrice(summary.totalAmount) }}</span>
                </div>
              </div>
              
              <p class="summary-note">
                <el-icon><InfoFilled /></el-icon>
                以上价格仅供参考，实际价格以设计师最终报价为准
              </p>
            </div>
          </div>

          <!-- 提交操作区 -->
          <div class="submit-section">
            <div class="submit-actions">
              <el-button size="large" @click="saveDraft">
                <el-icon><Document /></el-icon>
                保存草稿
              </el-button>
              <el-button type="primary" size="large" @click="submitScheme">
                <el-icon><Check /></el-icon>
                提交方案
              </el-button>
            </div>
            <p class="submit-tip">
              提交后，我们的设计顾问将在24小时内与您联系，为您定制专属方案
            </p>
          </div>
        </template>
      </div>
    </div>

    <!-- 提交成功对话框 -->
    <el-dialog
      v-model="submitDialog.visible"
      title="方案提交成功"
      width="500px"
      :show-close="false"
      :close-on-click-modal="false"
    >
      <div class="success-content">
        <el-icon class="success-icon" :size="64" color="#67c23a"><CircleCheck /></el-icon>
        <h3>您的方案已提交成功！</h3>
        <p class="success-desc">
          方案编号：<strong>{{ submitDialog.schemeNo }}</strong>
        </p>
        <div class="success-info">
          <p>✓ 设计顾问将在24小时内与您联系</p>
          <p>✓ 可根据您的需求调整产品搭配</p>
          <p>✓ 获取详细报价和设计方案</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="continueShopping">继续选品</el-button>
          <el-button type="primary" @click="viewMySchemes">查看我的方案</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 D&B 帝标|设记家全案落地服务系统 DEMO V.0.1</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ShoppingCart, Picture, Delete, Plus, Edit, Goods,
  Check, Document, InfoFilled, CircleCheck, HomeFilled, List
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()

// 状态
const selection = ref([])
const scheme = ref({
  name: '',
  style: '',
  area: '',
  stage: '',
  remark: '',
  managementFeeRate: 0,
  taxRate: 0
})
const submitDialog = ref({
  visible: false,
  schemeNo: ''
})

// 报价分类配置（与后台QUOTE_CATEGORIES对应）
const quoteCategories = {
  hard_material: { name: '硬装主材', order: 1 },
  construction: { name: '施工服务', order: 2 },
  installation: { name: '安装服务', order: 3 },
  delivery: { name: '配送服务', order: 4 },
  moving: { name: '搬运服务', order: 5 },
  design: { name: '设计服务', order: 6 },
  custom: { name: '全屋定制', order: 7 },
  furniture: { name: '成品家具', order: 8 },
  soft: { name: '软装饰品', order: 9 },
  equipment: { name: '电气设备', order: 10 },
  other: { name: '其他', order: 99 }
}

// 分类映射（与后台保持一致）
const categoryMapping = {
  '硬装主材': 'hard_material',
  '施工服务': 'construction',
  '安装服务': 'installation',
  '配送服务': 'delivery',
  '搬运服务': 'moving',
  '设计服务': 'design',
  '全屋定制': 'custom',
  '成品家具': 'furniture',
  '软装饰品': 'soft',
  '电气设备': 'equipment',
  '基装': 'construction',
  '主材': 'hard_material',
  '固装家具': 'custom',
  '活动家具': 'furniture'
}

// 计算属性：按空间和分类分组
const groupedByRoom = computed(() => {
  const rooms = {}
  
  selection.value.forEach(item => {
    const roomName = item.roomName || item.room_name || '默认空间'
    const category = item.category_level1 || item.category_name || item.category || '未分类'
    
    if (!rooms[roomName]) {
      rooms[roomName] = {
        items: [],
        categories: {},
        subtotal: 0
      }
    }
    
    if (!rooms[roomName].categories[category]) {
      rooms[roomName].categories[category] = []
    }
    
    rooms[roomName].items.push(item)
    rooms[roomName].categories[category].push(item)
    rooms[roomName].subtotal += (Number(item.sale_price) || 0) * (item.quantity || 1)
  })
  
  return rooms
})

// 计算属性：分类汇总（与后台一致）
const categorySummaryList = computed(() => {
  const summary = {}
  
  // 初始化所有分类
  Object.keys(quoteCategories).forEach(key => {
    summary[key] = {
      key,
      name: quoteCategories[key].name,
      amount: 0,
      order: quoteCategories[key].order
    }
  })
  
  // 汇总金额
  selection.value.forEach(item => {
    const cat1 = item.category_level1 || item.category_name || item.category || ''
    const quoteCat = categoryMapping[cat1] || 'other'
    const amount = (Number(item.sale_price) || 0) * (item.quantity || 1)
    
    if (summary[quoteCat]) {
      summary[quoteCat].amount += amount
    }
  })
  
  // 按order排序并过滤
  return Object.values(summary)
    .sort((a, b) => a.order - b.order)
    .filter(cat => cat.amount > 0 || cat.key === 'other')
})

// 计算属性：费用汇总（与后台一致）
const summary = computed(() => {
  const subtotal = selection.value.reduce((sum, item) => {
    return sum + (Number(item.sale_price) || 0) * (item.quantity || 1)
  }, 0)
  
  const managementFeeRate = Number(scheme.value.managementFeeRate) || 0
  const taxRate = Number(scheme.value.taxRate) || 0
  
  const managementFee = subtotal * (managementFeeRate / 100)
  const tax = subtotal * (taxRate / 100)
  const totalAmount = subtotal + managementFee + tax
  
  return {
    subtotal: Math.round(subtotal * 100) / 100,
    managementFee: Math.round(managementFee * 100) / 100,
    tax: Math.round(tax * 100) / 100,
    totalAmount: Math.round(totalAmount * 100) / 100
  }
})

// 计算属性：总数量
const totalQuantity = computed(() => {
  return selection.value.reduce((sum, item) => sum + (item.quantity || 1), 0)
})

// 计算属性：空间数量
const roomCount = computed(() => {
  const rooms = new Set()
  selection.value.forEach(item => {
    rooms.add(item.roomName || item.room_name || '默认空间')
  })
  return rooms.size
})

// 加载选品清单
const loadSelection = () => {
  const saved = JSON.parse(localStorage.getItem('productSelection') || '[]')
  // 确保每个产品有quantity和roomName字段
  selection.value = saved.map(item => ({
    ...item,
    quantity: item.quantity || 1,
    roomName: item.roomName || item.room_name || '默认空间',
    category_level1: item.category_level1 || item.category_name || item.category || '未分类',
    category_level2: item.category_level2 || '',
    category_level3: item.category_level3 || ''
  }))
  
  // 加载草稿
  const draft = JSON.parse(localStorage.getItem('schemeDraft') || '{}')
  if (draft.name) {
    scheme.value = { 
      name: draft.name || '',
      style: draft.style || '',
      area: draft.area || '',
      stage: draft.stage || '',
      remark: draft.remark || '',
      managementFeeRate: draft.managementFeeRate || 0,
      taxRate: draft.taxRate || 0
    }
  }
}

// 更新数量
const updateQuantity = (item) => {
  localStorage.setItem('productSelection', JSON.stringify(selection.value))
}

// 移除单品
const removeItem = (id) => {
  selection.value = selection.value.filter(item => item.id !== id)
  localStorage.setItem('productSelection', JSON.stringify(selection.value))
  ElMessage.success('已移除')
}

// 保存草稿
const saveDraft = () => {
  const draft = {
    ...scheme.value,
    selection: selection.value,
    savedAt: new Date().toISOString()
  }
  localStorage.setItem('schemeDraft', JSON.stringify(draft))
  ElMessage.success('方案草稿已保存')
}

// 构建分类汇总数据（与后台格式一致）
const buildCategorySummary = () => {
  const summary = {}
  categorySummaryList.value.forEach(cat => {
    summary[cat.key] = {
      name: cat.name,
      amount: cat.amount
    }
  })
  return summary
}

// 提交方案
const submitScheme = async () => {
  if (!scheme.value.name) {
    ElMessage.warning('请填写方案名称')
    return
  }
  
  if (selection.value.length === 0) {
    ElMessage.warning('请至少选择一件产品')
    return
  }

  try {
    // 构建提交数据 - 与后台create_quote格式对齐
    const submitData = {
      name: scheme.value.name,
      style: scheme.value.style,
      area: scheme.value.area,
      stage: scheme.value.stage,
      remark: scheme.value.remark,
      items: selection.value.map((item, idx) => ({
        sku_id: item.id,
        room_name: item.roomName || item.room_name || '默认空间',
        category_level1: item.category_level1 || item.category_name || item.category || '未分类',
        category_level2: item.category_level2 || '',
        category_level3: item.category_level3 || '',
        name: item.name,
        sku_code: item.sku_code || '',
        spec: item.specification || item.spec || '',
        brand: item.brand || '',
        unit: item.unit || '件',
        main_image: item.main_image || '',
        quantity: item.quantity || 1,
        unit_price: item.sale_price || 0,
        total_price: (item.sale_price || 0) * (item.quantity || 1),
        remark: item.remark || '',
        sort_order: idx
      })),
      category_summary: buildCategorySummary(),
      subtotal: summary.value.subtotal,
      management_fee_rate: Number(scheme.value.managementFeeRate) || 0,
      tax_rate: Number(scheme.value.taxRate) || 0,
      total_amount: summary.value.totalAmount,
      total_quantity: totalQuantity.value,
      room_count: roomCount.value
    }

    // 调用API提交
    const res = await request.post('/api/v3/schemes', submitData)
    
    // 显示成功对话框
    submitDialog.value.schemeNo = res.data?.scheme_no || 'SC' + Date.now()
    submitDialog.value.visible = true
    
    // 清空本地数据
    localStorage.removeItem('productSelection')
    localStorage.removeItem('schemeDraft')
    
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '提交失败，请稍后重试')
  }
}

// 继续选品
const continueShopping = () => {
  submitDialog.value.visible = false
  router.push('/products')
}

// 查看我的方案
const viewMySchemes = () => {
  submitDialog.value.visible = false
  // TODO: 跳转到我的方案页面
  router.push('/')
}

// 跳转详情
const goToDetail = (id) => {
  router.push(`/products/${id}`)
}

// 格式化价格
const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00'
  return Number(price).toFixed(2)
}

onMounted(() => {
  loadSelection()
})
</script>

<style scoped>
.selection-list-page {
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

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #8B5A2B 0%, #D4A574 100%);
  color: #fff;
  padding: 60px 5%;
  text-align: center;
}

.page-header h1 {
  font-size: 36px;
  margin-bottom: 12px;
}

.page-header p {
  font-size: 16px;
  opacity: 0.9;
}

/* 清单内容 */
.selection-content {
  padding: 40px 5%;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 空状态 */
.empty-state {
  padding: 80px 0;
  text-align: center;
}

.empty-tip {
  color: #999;
  margin: 16px 0 24px;
}

/* 区块样式 */
.scheme-section,
.products-section {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.section-header h2 {
  font-size: 20px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.section-header h2 .el-icon {
  color: #8B5A2B;
}

.section-header p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
}

/* 方案表单 */
.scheme-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full-width {
  grid-column: 1 / -1;
}

.form-item label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.required {
  color: #f56c6c;
}

/* 空间分组 */
.room-group {
  margin-bottom: 32px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.room-group:last-child {
  margin-bottom: 0;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #8B5A2B 0%, #A67B5B 100%);
  color: #fff;
}

.room-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.room-title .el-icon {
  font-size: 18px;
}

.room-name {
  font-weight: 600;
  font-size: 16px;
}

.room-count {
  font-size: 13px;
  opacity: 0.8;
  margin-left: 8px;
}

.room-amount {
  font-weight: 600;
  font-size: 16px;
}

/* 分类组 */
.category-group {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.category-group:last-child {
  border-bottom: none;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  margin-bottom: 12px;
}

.category-name {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.category-count {
  font-size: 13px;
  color: #999;
}

/* 清单列表 */
.selection-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selection-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  transition: all 0.3s;
}

.selection-item:hover {
  background: #f0f0f0;
}

.item-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #ccc;
}

.item-info {
  flex: 1;
  cursor: pointer;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 6px 0;
}

.item-spec {
  font-size: 13px;
  color: #666;
  margin: 0 0 4px 0;
}

.item-brand {
  font-size: 12px;
  color: #999;
  margin: 0 0 4px 0;
}

.item-meta {
  margin-bottom: 8px;
}

.item-category {
  font-size: 12px;
  color: #8B5A2B;
  background: #f5f0eb;
  padding: 2px 8px;
  border-radius: 4px;
}

.item-price {
  color: #f56c6c;
}

.item-price .price-symbol {
  font-size: 12px;
}

.item-price .price-value {
  font-size: 20px;
  font-weight: 600;
}

.item-price .price-unit {
  font-size: 12px;
  color: #999;
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
}

.item-subtotal {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

/* 分类汇总 */
.category-summary-section {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  margin-top: 24px;
}

.category-summary-section h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-summary-section h3 .el-icon {
  color: #8B5A2B;
}

.category-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.category-summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.category-summary-item.has-amount {
  border-color: #8B5A2B;
  background: #fdfbf9;
}

.cat-name {
  font-size: 14px;
  color: #666;
}

.cat-amount {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.category-summary-item.has-amount .cat-amount {
  color: #8B5A2B;
}

/* 汇总信息 */
.selection-summary {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  margin-top: 24px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 费用明细 */
.fee-breakdown {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.fee-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  color: #666;
}

.fee-row.total {
  border-top: 2px solid #e8e8e8;
  margin-top: 12px;
  padding-top: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.total-amount {
  font-size: 24px;
  color: #f56c6c;
}

.summary-note {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* 提交区 */
.submit-section {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.submit-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.submit-tip {
  color: #999;
  font-size: 14px;
  margin: 0;
}

/* 成功对话框 */
.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  margin-bottom: 16px;
}

.success-content h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 12px;
}

.success-desc {
  color: #666;
  margin-bottom: 24px;
}

.success-desc strong {
  color: #8B5A2B;
  font-size: 18px;
}

.success-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: left;
}

.success-info p {
  margin: 8px 0;
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 页脚 */
.footer {
  background: #333;
  color: #999;
  padding: 24px 5%;
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .room-header {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .selection-item {
    flex-direction: column;
  }
  
  .item-image {
    width: 100%;
    height: 200px;
  }
  
  .item-actions {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .category-summary-grid {
    grid-template-columns: 1fr;
  }
  
  .submit-actions {
    flex-direction: column;
  }
}
</style>
