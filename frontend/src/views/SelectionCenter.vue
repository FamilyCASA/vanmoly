<template>
  <div class="selection-center-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-left">
        <h2>我的选品中心</h2>
        <p class="subtitle">管理您的心仪产品，定制专属方案</p>
      </div>
      <div class="header-actions">
        <el-button @click="goToProducts">
          <el-icon><Plus /></el-icon>
          继续选品
        </el-button>
        <el-button type="primary" @click="submitSelection">
          <el-icon><Check /></el-icon>
          提交需求
        </el-button>
      </div>
    </div>

    <!-- 三列布局 -->
    <div class="three-column-layout">
      <!-- 左侧：空间与产品树状结构 -->
      <div class="left-column">
        <el-card shadow="never" class="tree-card">
          <template #header>
            <div class="card-header">
              <span>空间分类</span>
              <el-button text size="small" @click="expandAll">
                {{ allExpanded ? '收起' : '展开' }}
              </el-button>
            </div>
          </template>
          
          <el-tree
            :data="spaceTreeData"
            :props="treeProps"
            node-key="id"
            :default-expanded-keys="expandedKeys"
            @node-click="handleNodeClick"
            highlight-current
            ref="treeRef"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <span class="node-label">{{ node.label }}</span>
                <el-tag v-if="data.count" size="small" type="primary">{{ data.count }}</el-tag>
              </div>
            </template>
          </el-tree>
        </el-card>
      </div>

      <!-- 中间：套餐、物料、服务列表 -->
      <div class="center-column">
        <el-card shadow="never" class="list-card">
          <template #header>
            <div class="list-header">
              <div class="header-tabs">
                <div 
                  class="tab-item" 
                  :class="{ active: activeTab === 'all' }"
                  @click="activeTab = 'all'"
                >
                  全部
                </div>
                <div 
                  class="tab-item" 
                  :class="{ active: activeTab === 'package' }"
                  @click="activeTab = 'package'"
                >
                  套餐
                </div>
                <div 
                  class="tab-item" 
                  :class="{ active: activeTab === 'product' }"
                  @click="activeTab = 'product'"
                >
                  单品
                </div>
                <div 
                  class="tab-item" 
                  :class="{ active: activeTab === 'service' }"
                  @click="activeTab = 'service'"
                >
                  服务
                </div>
              </div>
              <div class="header-filter">
                <el-checkbox v-model="showOnlySelected">仅看已选</el-checkbox>
              </div>
            </div>
          </template>

          <!-- 空状态 -->
          <el-empty v-if="filteredItems.length === 0" description="暂无选品">
            <el-button type="primary" @click="goToProducts">去选品</el-button>
          </el-empty>

          <!-- 选品列表 -->
          <div v-else class="selection-list">
            <div 
              v-for="item in filteredItems" 
              :key="`${item.type}-${item.id}`"
              class="selection-item"
              :class="{ 'is-selected': isSelected(item) }"
              @click="toggleSelect(item)"
            >
              <div class="item-image">
                <img :src="item.image || '/placeholder-product.jpg'" :alt="item.name">
                <div class="item-type-tag" :class="item.type">
                  {{ typeLabel(item.type) }}
                </div>
              </div>
              <div class="item-info">
                <h4 class="item-name">{{ item.name }}</h4>
                <p class="item-space">{{ item.space_name || '未分类' }}</p>
                <div class="item-specs" v-if="item.specs">
                  <el-tag size="small" v-for="spec in item.specs" :key="spec">{{ spec }}</el-tag>
                </div>
                <div class="item-price-row">
                  <span class="item-price">¥{{ formatPrice(item.price) }}</span>
                  <div class="quantity-control">
                    <el-button 
                      circle 
                      size="small" 
                      :icon="Minus"
                      @click.stop="decreaseQuantity(item)"
                      :disabled="getQuantity(item) <= 1"
                    />
                    <span class="quantity">{{ getQuantity(item) }}</span>
                    <el-button 
                      circle 
                      size="small" 
                      :icon="Plus"
                      @click.stop="increaseQuantity(item)"
                    />
                  </div>
                </div>
              </div>
              <div class="item-actions">
                <el-button 
                  type="danger" 
                  text 
                  size="small"
                  @click.stop="removeItem(item)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：汇总价格和推荐 -->
      <div class="right-column">
        <!-- 价格汇总 -->
        <el-card shadow="never" class="summary-card">
          <template #header>
            <span>价格汇总</span>
          </template>
          
          <div class="summary-content">
            <div class="summary-row" v-for="(items, space) in itemsBySpace" :key="space">
              <span class="space-name">{{ space }}</span>
              <span class="space-price">¥{{ formatPrice(calculateSpaceTotal(items)) }}</span>
            </div>
            
            <el-divider />
            
            <div class="summary-row total">
              <span>总计</span>
              <span class="total-price">¥{{ formatPrice(totalPrice) }}</span>
            </div>
            
            <div class="summary-stats">
              <span>共 {{ totalCount }} 件商品</span>
            </div>
          </div>
        </el-card>

        <!-- 智能推荐 -->
        <el-card shadow="never" class="recommend-card" v-if="recommendPackages.length > 0">
          <template #header>
            <div class="recommend-header">
              <span>为您推荐</span>
              <el-tooltip content="基于您的选品总价，推荐接近的套餐方案">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          
          <div class="recommend-list">
            <div 
              v-for="pkg in recommendPackages" 
              :key="pkg.id"
              class="recommend-item"
              :class="{ 'is-highlight': pkg.isHighlight }"
              @click="viewPackageDetail(pkg)"
            >
              <div class="recommend-image">
                <img :src="pkg.image" :alt="pkg.name">
                <div v-if="pkg.isHighlight" class="recommend-badge">推荐</div>
              </div>
              <div class="recommend-info">
                <h4>{{ pkg.name }}</h4>
                <p class="recommend-desc">{{ pkg.description }}</p>
                <div class="recommend-price-row">
                  <span class="recommend-price">¥{{ formatPrice(pkg.price) }}</span>
                  <span class="price-diff" :class="pkg.diffType">
                    {{ pkg.diffText }}
                  </span>
                </div>
                <div class="recommend-tags">
                  <el-tag size="small" type="success" v-if="pkg.includesAll">包含全部已选</el-tag>
                  <el-tag size="small" v-else-if="pkg.includesCount > 0">
                    包含{{ pkg.includesCount }}件已选
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
          
          <div class="recommend-tip">
            <el-icon><Coffee /></el-icon>
            <span>星巴克大杯原理：选择略高于预算的方案，往往性价比更高</span>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" size="large" class="full-width" @click="submitSelection">
            提交需求
          </el-button>
          <el-button size="large" class="full-width" @click="saveAsDraft">
            保存草稿
          </el-button>
        </div>
      </div>
    </div>

    <!-- 注册引导弹窗 -->
    <el-dialog
      v-model="showLoginDialog"
      title="注册后查看选品"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="login-prompt">
        <el-icon :size="48" color="#8B5A2B"><ShoppingCart /></el-icon>
        <p>您有 {{ anonymousCount }} 件商品在选品清单中</p>
        <p class="prompt-sub">注册后即可查看和管理您的选品，获取专属方案推荐</p>
      </div>
      <template #footer>
        <el-button @click="showLoginDialog = false">稍后</el-button>
        <el-button type="primary" @click="goToRegister">立即注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Check, Minus, Delete, InfoFilled, Coffee, ShoppingCart
} from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const router = useRouter()
const { items, totalCount, totalPrice, itemsBySpace, removeItem, updateQuantity } = useAnonymousSelection()

// 用户登录状态
const isLoggedIn = ref(false)
const showLoginDialog = ref(false)
const anonymousCount = ref(0)

// 树状结构
const treeRef = ref(null)
const allExpanded = ref(false)
const expandedKeys = ref([])
const selectedSpace = ref(null)

const treeProps = {
  label: 'name',
  children: 'children'
}

// 空间树数据
const spaceTreeData = computed(() => {
  const tree = []
  const grouped = itemsBySpace.value
  
  Object.keys(grouped).forEach((spaceName, index) => {
    const items = grouped[spaceName]
    const spaceTotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    
    tree.push({
      id: `space-${index}`,
      name: spaceName,
      count: items.length,
      total: spaceTotal,
      children: items.map((item, i) => ({
        id: `${item.type}-${item.id}`,
        name: item.name,
        price: item.price,
        quantity: item.quantity,
        type: 'item',
        item: item
      }))
    })
  })
  
  return tree
})

// 标签页
const activeTab = ref('all')
const showOnlySelected = ref(false)

// 过滤后的列表
const filteredItems = computed(() => {
  let list = items.value
  
  // 按类型过滤
  if (activeTab.value !== 'all') {
    list = list.filter(item => item.type === activeTab.value)
  }
  
  // 按空间过滤
  if (selectedSpace.value) {
    list = list.filter(item => item.space_name === selectedSpace.value)
  }
  
  return list
})

// 推荐套餐
const recommendPackages = ref([])

// 计算推荐套餐
const calculateRecommendations = () => {
  const currentTotal = totalPrice.value
  
  // 模拟推荐数据（实际应从API获取）
  const mockPackages = [
    {
      id: 1,
      name: '舒适家套餐',
      description: '两室一厅基础配置，适合小家庭',
      price: 120000,
      image: '/package-1.jpg',
      includesAll: false,
      includesCount: 3
    },
    {
      id: 2,
      name: '品质生活套餐',
      description: '三室两厅升级配置，品质之选',
      price: 164200,
      image: '/package-2.jpg',
      includesAll: false,
      includesCount: 5,
      isHighlight: true
    },
    {
      id: 3,
      name: '尊享全案套餐',
      description: '全屋定制高端配置，尊享服务',
      price: 178500,
      image: '/package-3.jpg',
      includesAll: true,
      includesCount: items.value.length
    }
  ]
  
  // 计算差价和排序
  recommendPackages.value = mockPackages.map(pkg => {
    const diff = pkg.price - currentTotal
    const diffPercent = Math.abs(diff / currentTotal * 100).toFixed(0)
    
    return {
      ...pkg,
      diff: diff,
      diffType: diff > 0 ? 'higher' : 'lower',
      diffText: diff > 0 ? `高出${diffPercent}%` : `节省${diffPercent}%`
    }
  }).sort((a, b) => Math.abs(a.diff) - Math.abs(b.diff)) // 按接近程度排序
}

// 类型标签
const typeLabel = (type) => {
  const map = { package: '套餐', product: '单品', service: '服务' }
  return map[type] || type
}

// 格式化价格
const formatPrice = (price) => {
  return price?.toLocaleString('zh-CN') || '0'
}

// 计算空间总价
const calculateSpaceTotal = (items) => {
  return items.reduce((sum, item) => sum + ((item.price || 0) * (item.quantity || 1)), 0)
}

// 获取数量
const getQuantity = (item) => {
  return item.quantity || 1
}

// 是否选中
const isSelected = (item) => {
  return true // 列表中的都是已选
}

// 切换选择
const toggleSelect = (item) => {
  // 可以扩展多选功能
}

// 增加数量
const increaseQuantity = (item) => {
  updateQuantity(item.id, item.type, getQuantity(item) + 1)
}

// 减少数量
const decreaseQuantity = (item) => {
  const qty = getQuantity(item)
  if (qty > 1) {
    updateQuantity(item.id, item.type, qty - 1)
  }
}

// 树节点点击
const handleNodeClick = (data) => {
  if (data.type === 'item') {
    // 点击具体项目
  } else {
    // 点击空间
    selectedSpace.value = selectedSpace.value === data.name ? null : data.name
  }
}

// 展开/收起全部
const expandAll = () => {
  allExpanded.value = !allExpanded.value
  if (allExpanded.value) {
    expandedKeys.value = spaceTreeData.value.map(node => node.id)
  } else {
    expandedKeys.value = []
  }
}

// 查看套餐详情
const viewPackageDetail = (pkg) => {
  router.push(`/packages/${pkg.id}`)
}

// 提交需求
const submitSelection = () => {
  if (!isLoggedIn.value) {
    showLoginDialog.value = true
    return
  }
  
  if (items.value.length === 0) {
    ElMessage.warning('请先添加选品')
    return
  }
  
  router.push('/submit-requirement')
}

// 保存草稿
const saveAsDraft = async () => {
  if (!isLoggedIn.value) {
    showLoginDialog.value = true
    return
  }
  
  try {
    // 调用API保存草稿
    await request.post('/selection/draft', {
      items: items.value
    })
    ElMessage.success('草稿已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 跳转
const goToProducts = () => {
  router.push('/products')
}

// 检查登录/注册状态
const checkLoginStatus = () => {
  const token = localStorage.getItem('customer_token')
  isLoggedIn.value = !!token
  
  if (!isLoggedIn.value) {
    anonymousCount.value = items.value.length
    if (anonymousCount.value > 0) {
      showLoginDialog.value = true
    }
  }
}

const goToRegister = () => {
  showLoginDialog.value = false
  router.push('/register?redirect=/selection-center')
}

onMounted(() => {
  checkLoginStatus()
  calculateRecommendations()
})

watch(totalPrice, () => {
  calculateRecommendations()
})
</script>

<style scoped>
.selection-center-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.subtitle {
  margin: 4px 0 0;
  color: #999;
  font-size: 13px;
}

/* 三列布局 */
.three-column-layout {
  display: grid;
  grid-template-columns: 260px 1fr 320px;
  gap: 16px;
}

/* 左列 */
.left-column {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.tree-card {
  :deep(.el-card__header) {
    padding: 12px 16px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding-right: 8px;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 中列 */
.center-column {
  min-height: 600px;
}

.list-card {
  height: 100%;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-tabs {
  display: flex;
  gap: 4px;
}

.tab-item {
  padding: 6px 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #8B5A2B;
  background: #f5f7fa;
}

.tab-item.active {
  color: #8B5A2B;
  background: #fff7e6;
  font-weight: 500;
}

/* 选品列表 */
.selection-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selection-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.selection-item:hover {
  border-color: #8B5A2B;
  box-shadow: 0 2px 12px rgba(139, 90, 43, 0.1);
}

.selection-item.is-selected {
  border-color: #8B5A2B;
  background: #fff7e6;
}

.item-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-type-tag {
  position: absolute;
  top: 4px;
  left: 4px;
  padding: 2px 8px;
  font-size: 12px;
  border-radius: 4px;
  color: #fff;
}

.item-type-tag.package {
  background: #8B5A2B;
}

.item-type-tag.product {
  background: #52c41a;
}

.item-type-tag.service {
  background: #1890ff;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-name {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 500;
}

.item-space {
  margin: 0 0 8px;
  font-size: 13px;
  color: #999;
}

.item-specs {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.item-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.item-price {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity {
  min-width: 30px;
  text-align: center;
  font-weight: 500;
}

.item-actions {
  display: flex;
  align-items: flex-start;
}

/* 右列 */
.right-column {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.summary-card,
.recommend-card {
  margin-bottom: 16px;
}

.summary-content {
  padding: 8px 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.summary-row.total {
  font-size: 16px;
  font-weight: 600;
}

.total-price {
  font-size: 24px;
  color: #f56c6c;
}

.summary-stats {
  text-align: center;
  color: #999;
  font-size: 13px;
  margin-top: 12px;
}

/* 推荐 */
.recommend-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommend-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.recommend-item:hover {
  background: #fff;
  border-color: #8B5A2B;
}

.recommend-item.is-highlight {
  background: #fff7e6;
  border-color: #8B5A2B;
}

.recommend-image {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.recommend-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommend-badge {
  position: absolute;
  top: 0;
  left: 0;
  background: #8B5A2B;
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px 0 6px 0;
}

.recommend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.recommend-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
}

.recommend-desc {
  margin: 0 0 8px;
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.recommend-price-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
}

.recommend-price {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.price-diff {
  font-size: 12px;
}

.price-diff.higher {
  color: #f56c6c;
}

.price-diff.lower {
  color: #52c41a;
}

.recommend-tags {
  margin-top: 4px;
}

.recommend-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: #e6f7ff;
  border-radius: 6px;
  font-size: 12px;
  color: #1890ff;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.full-width {
  width: 100%;
}

/* 登录提示 */
.login-prompt {
  text-align: center;
  padding: 20px;
}

.login-prompt p {
  margin: 12px 0 4px;
  font-size: 16px;
}

.prompt-sub {
  color: #999;
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .three-column-layout {
    grid-template-columns: 200px 1fr 280px;
  }
}

@media (max-width: 992px) {
  .three-column-layout {
    grid-template-columns: 1fr;
  }
  
  .left-column,
  .right-column {
    position: static;
  }
}
</style>
