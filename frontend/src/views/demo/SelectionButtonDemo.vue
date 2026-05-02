<template>
  <div class="demo-page">
    <h1>选品按钮效果演示</h1>
    
    <div class="demo-section">
      <h2>当前选品数量: {{ totalCount }}</h2>
      
      <div class="button-showcase">
        <SelectionButton />
      </div>
      
      <div class="demo-controls">
        <h3>操作按钮</h3>
        <div class="control-buttons">
          <el-button type="primary" @click="addRandomItem">
            <el-icon><Plus /></el-icon>
            添加选品（触发吞咽动画）
          </el-button>
          
          <el-button @click="addMultipleItems">
            <el-icon><CirclePlus /></el-icon>
            批量添加3个
          </el-button>
          
          <el-button type="danger" @click="clearItems">
            <el-icon><Delete /></el-icon>
            清空选品
          </el-button>
        </div>
      </div>
      
      <div class="current-items" v-if="items.length > 0">
        <h3>当前选品列表</h3>
        <el-table :data="items" style="width: 100%">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="space_name" label="空间" width="120" />
          <el-table-column prop="price" label="价格" width="120">
            <template #default="{ row }">
              ¥{{ row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="danger" text size="small" @click="removeItem(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <div class="demo-section features">
      <h2>功能特性</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🫁</div>
          <h4>呼吸动画</h4>
          <p>有选品时按钮持续呼吸，吸引用户注意</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🍽️</div>
          <h4>吞咽动作</h4>
          <p>加入新物料时，金色粒子被"吞"入购物车</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔢</div>
          <h4>数字滚动</h4>
          <p>数量变化时数字平滑滚动，+号弹跳提示</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👁️</div>
          <h4>悬浮预览</h4>
          <p>鼠标悬停显示最近添加的选品和价格汇总</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, CirclePlus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import SelectionButton from '@/components/SelectionButton.vue'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const { items, totalCount, addItem, removeItem, clearAll } = useAnonymousSelection()

const productNames = [
  '北欧风布艺沙发', '实木餐桌', '真皮休闲椅', '简约茶几',
  '落地灯', '装饰画', '地毯', '窗帘', '床品四件套',
  '衣柜', '书桌', '书架', '电视柜', '鞋柜'
]

const spaces = ['客厅', '主卧', '次卧', '书房', '餐厅', '厨房']

const addRandomItem = () => {
  const randomProduct = productNames[Math.floor(Math.random() * productNames.length)]
  const randomSpace = spaces[Math.floor(Math.random() * spaces.length)]
  const randomPrice = Math.floor(Math.random() * 5000) + 500
  
  const item = {
    id: Date.now(),
    type: 'product',
    name: randomProduct,
    space_name: randomSpace,
    price: randomPrice,
    image: null
  }
  
  addItem(item)
  ElMessage.success(`已添加: ${randomProduct}`)
}

const addMultipleItems = () => {
  for (let i = 0; i < 3; i++) {
    setTimeout(() => {
      addRandomItem()
    }, i * 200)
  }
}

const clearItems = () => {
  clearAll()
  ElMessage.info('选品已清空')
}
</script>

<style scoped>
.demo-page {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
  color: #1a1a1a;
}

.demo-section {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.demo-section h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #333;
}

.button-showcase {
  display: flex;
  justify-content: center;
  padding: 40px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px;
  margin-bottom: 32px;
}

.demo-controls {
  margin-bottom: 32px;
}

.demo-controls h3 {
  margin-bottom: 16px;
  color: #666;
}

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.current-items {
  margin-top: 32px;
}

.current-items h3 {
  margin-bottom: 16px;
  color: #666;
}

/* 特性展示 */
.features {
  background: linear-gradient(135deg, #8B5A2B 0%, #A67B5B 100%);
  color: #fff;
}

.features h2 {
  color: #fff;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.feature-card h4 {
  margin: 0 0 8px;
  font-size: 16px;
}

.feature-card p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .demo-page {
    padding: 20px;
  }
  
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
