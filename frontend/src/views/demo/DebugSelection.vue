<template>
  <div class="debug-page">
    <h1>选品数据调试</h1>
    
    <div class="debug-section">
      <h2>LocalStorage 数据</h2>
      <pre class="data-display">{{ localStorageData }}</pre>
      <el-button @click="refreshData">刷新数据</el-button>
      <el-button type="danger" @click="clearStorage">清空 LocalStorage</el-button>
    </div>
    
    <div class="debug-section">
      <h2>Composable 状态</h2>
      <div class="status-grid">
        <div class="status-item">
          <label>访客ID:</label>
          <span>{{ visitorId || '未生成' }}</span>
        </div>
        <div class="status-item">
          <label>选品总数:</label>
          <span class="highlight">{{ totalCount }}</span>
        </div>
        <div class="status-item">
          <label>选品总价:</label>
          <span class="highlight">¥{{ totalPrice }}</span>
        </div>
        <div class="status-item">
          <label>是否有选品:</label>
          <span :class="hasItems ? 'yes' : 'no'">{{ hasItems ? '是' : '否' }}</span>
        </div>
      </div>
    </div>
    
    <div class="debug-section">
      <h2>选品列表</h2>
      <el-table v-if="items.length > 0" :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="space_name" label="空间" width="120" />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
      </el-table>
      <el-empty v-else description="暂无选品" />
    </div>
    
    <div class="debug-section">
      <h2>测试操作</h2>
      <div class="test-buttons">
        <el-button type="primary" @click="addTestItem">
          添加测试选品
        </el-button>
        <el-button @click="addMultipleItems">
          批量添加5个
        </el-button>
        <el-button type="danger" @click="clearAll">
          清空选品
        </el-button>
      </div>
    </div>
    
    <div class="debug-section">
      <h2>组件状态检查</h2>
      <div class="component-check">
        <SelectionButton />
        <p class="check-hint">↑ 上方是 SelectionButton 组件</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import SelectionButton from '@/components/SelectionButton.vue'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const { 
  visitorId, 
  items, 
  totalCount, 
  totalPrice, 
  hasItems, 
  addItem, 
  clearAll 
} = useAnonymousSelection()

const localStorageData = ref('')

const refreshData = () => {
  const data = localStorage.getItem('vanmoly_anonymous_selection')
  localStorageData.value = data ? JSON.stringify(JSON.parse(data), null, 2) : '无数据'
}

const clearStorage = () => {
  localStorage.removeItem('vanmoly_anonymous_selection')
  localStorage.removeItem('vanmoly_visitor_id')
  refreshData()
  ElMessage.success('LocalStorage 已清空，请刷新页面')
}

let testId = 1

const addTestItem = () => {
  const item = {
    id: `test-${testId++}`,
    type: 'product',
    name: `测试商品 ${testId}`,
    space_name: '客厅',
    price: Math.floor(Math.random() * 5000) + 1000,
    image: null
  }
  
  addItem(item)
  ElMessage.success(`已添加: ${item.name}`)
  
  // 延迟刷新显示
  setTimeout(refreshData, 100)
}

const addMultipleItems = () => {
  for (let i = 0; i < 5; i++) {
    setTimeout(() => {
      addTestItem()
    }, i * 200)
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.debug-page {
  padding: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
}

.debug-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.debug-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
}

.data-display {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 13px;
  overflow-x: auto;
  margin-bottom: 16px;
  min-height: 100px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.status-item label {
  color: #666;
}

.status-item .highlight {
  color: #8B5A2B;
  font-weight: 600;
}

.status-item .yes {
  color: #52c41a;
  font-weight: 600;
}

.status-item .no {
  color: #999;
}

.test-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.component-check {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background: #f5f7fa;
  border-radius: 12px;
}

.check-hint {
  margin-top: 20px;
  color: #999;
  font-size: 14px;
}
</style>
