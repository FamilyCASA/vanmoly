<template>
  <div class="my-subscriptions-page">
    <!-- 统一导航栏 -->
    <Navbar />

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="container">
        <h1>我的订阅</h1>
        <p>关注喜欢的案例，获取最新动态</p>
      </div>
    </header>

    <!-- 主内容 -->
    <div class="main-content">
      <div class="container">
        <!-- 统计卡片 -->
        <div class="stats-bar">
          <div class="stat-card">
            <div class="stat-value">{{ subscriptions.length }}</div>
            <div class="stat-label">订阅案例</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ unreadCount }}</div>
            <div class="stat-label">未读更新</div>
          </div>
        </div>

        <!-- 订阅列表 -->
        <div v-if="subscriptions.length > 0" class="subscription-list">
          <div
            v-for="item in subscriptions"
            :key="item.id"
            class="subscription-item"
            :class="{ 'has-update': item.has_update }"
          >
            <div class="item-cover" @click="goToCase(item.case_id)">
              <img :src="item.case_cover || '/placeholder-case.jpg'" :alt="item.case_title">
              <div v-if="item.has_update" class="update-badge">有更新</div>
            </div>
            <div class="item-content">
              <div class="item-header">
                <h3 class="item-title" @click="goToCase(item.case_id)">{{ item.case_title }}</h3>
                <el-dropdown @command="(cmd) => handleCommand(cmd, item)">
                  <el-button link>
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="notify">
                        {{ item.notify_enabled ? '关闭通知' : '开启通知' }}
                      </el-dropdown-item>
                      <el-dropdown-item command="unsubscribe" divided style="color: #f56c6c">
                        取消订阅
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              <p class="item-desc">{{ item.case_desc || '暂无描述' }}</p>
              <div class="item-meta">
                <span class="meta-item">
                  <el-icon><View /></el-icon>
                  {{ item.case_views || 0 }} 浏览
                </span>
                <span class="meta-item">
                  <el-icon><Bell /></el-icon>
                  {{ item.case_subscriptions || 0 }} 订阅
                </span>
                <span class="meta-item time">
                  订阅于 {{ formatDate(item.subscribe_time) }}
                </span>
              </div>
              <div v-if="item.last_update" class="update-info">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ item.last_update }}</span>
                <el-button type="primary" link @click="goToCase(item.case_id)">查看更新</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无订阅的案例">
            <template #image>
              <el-icon :size="80" color="#dcdfe6"><Bell /></el-icon>
            </template>
            <el-button type="primary" @click="goToCases">去发现案例</el-button>
          </el-empty>
        </div>

        <!-- 推荐案例 -->
        <div class="recommend-section" v-if="recommendCases.length > 0">
          <h3 class="section-title">猜你喜欢</h3>
          <div class="recommend-grid">
            <div
              v-for="caseItem in recommendCases"
              :key="caseItem.id"
              class="recommend-item"
              @click="goToCase(caseItem.id)"
            >
              <div class="recommend-cover">
                <img :src="caseItem.cover_image || '/placeholder-case.jpg'" :alt="caseItem.title">
              </div>
              <div class="recommend-info">
                <h4>{{ caseItem.title }}</h4>
                <p>{{ caseItem.location }} · {{ caseItem.area }}㎡</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统一页脚 -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, View, More, InfoFilled } from '@element-plus/icons-vue'
import { getPublicCases } from '@/api/case'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()

// 状态
const loading = ref(false)
const subscriptions = ref([])
const recommendCases = ref([])

// 未读数量
const unreadCount = computed(() => {
  return subscriptions.value.filter(s => s.has_update).length
})

// 获取订阅列表
const fetchSubscriptions = async () => {
  loading.value = true
  try {
    // TODO: 实现获取订阅列表 API
    // const res = await getMySubscriptions()
    // subscriptions.value = res.data || []
    
    // 模拟数据
    subscriptions.value = [
      {
        id: 1,
        case_id: 1,
        case_title: '现代简约三居室，打造温馨舒适的家',
        case_desc: '本案位于成都市高新区，业主是一对年轻夫妇，希望打造一个简约而不简单的居住空间...',
        case_cover: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800',
        case_views: 1234,
        case_subscriptions: 56,
        subscribe_time: '2026-04-20T10:00:00',
        notify_enabled: true,
        has_update: true,
        last_update: '新增水电阶段照片 5 张'
      },
      {
        id: 2,
        case_id: 2,
        case_title: '新中式别墅，传统与现代的完美融合',
        case_desc: '本案是一套 300㎡ 的别墅，业主喜欢中式风格，但又不希望过于传统...',
        case_cover: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800',
        case_views: 892,
        case_subscriptions: 34,
        subscribe_time: '2026-04-18T14:30:00',
        notify_enabled: true,
        has_update: false
      }
    ]
  } catch (error) {
    console.error('获取订阅列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取推荐案例
const fetchRecommendCases = async () => {
  try {
    const res = await getPublicCases({ page_size: 4 })
    recommendCases.value = res.data?.items || []
  } catch (error) {
    console.error('获取推荐案例失败:', error)
  }
}

// 操作菜单
const handleCommand = async (command, item) => {
  if (command === 'notify') {
    // 切换通知设置
    try {
      // TODO: 实现切换通知 API
      // await toggleNotification(item.id, !item.notify_enabled)
      item.notify_enabled = !item.notify_enabled
      ElMessage.success(item.notify_enabled ? '已开启通知' : '已关闭通知')
    } catch (error) {
      ElMessage.error('操作失败')
    }
  } else if (command === 'unsubscribe') {
    // 取消订阅
    try {
      await ElMessageBox.confirm(
        `确定要取消订阅「${item.case_title}」吗？`,
        '确认取消订阅',
        { type: 'warning' }
      )
      // TODO: 实现取消订阅 API
      // await unsubscribeCase(item.id)
      subscriptions.value = subscriptions.value.filter(s => s.id !== item.id)
      ElMessage.success('已取消订阅')
    } catch {
      // 取消
    }
  }
}

// 跳转
const goToCase = (caseId) => {
  router.push(`/cases/${caseId}`)
}

const goToCases = () => {
  router.push('/cases')
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  // 小于1天显示"今天"、"昨天"
  if (diff < 24 * 60 * 60 * 1000) {
    return '今天'
  } else if (diff < 48 * 60 * 60 * 1000) {
    return '昨天'
  }
  
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  fetchSubscriptions()
  fetchRecommendCases()
})
</script>

<style scoped lang="scss">
.my-subscriptions-page {
  min-height: 100vh;
  background: #f8f8f8;
  padding-top: 80px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
  color: #fff;
  padding: 60px 0;
  text-align: center;
  
  h1 {
    font-size: 36px;
    font-weight: 300;
    margin-bottom: 12px;
    letter-spacing: 4px;
  }
  
  p {
    font-size: 16px;
    opacity: 0.7;
  }
}

/* 主内容 */
.main-content {
  padding: 40px 0;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  
  .stat-value {
    font-size: 36px;
    font-weight: 600;
    color: #8B5A2B;
    margin-bottom: 8px;
  }
  
  .stat-label {
    font-size: 14px;
    color: #999;
  }
}

/* 订阅列表 */
.subscription-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.subscription-item {
  display: flex;
  gap: 20px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  }
  
  &.has-update {
    border-left: 4px solid #8B5A2B;
  }
}

.item-cover {
  position: relative;
  width: 180px;
  height: 120px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
  }
  
  &:hover img {
    transform: scale(1.05);
  }
  
  .update-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    padding: 4px 10px;
    background: #8B5A2B;
    color: #fff;
    font-size: 12px;
    border-radius: 4px;
  }
}

.item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.item-title {
  font-size: 18px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  
  &:hover {
    color: #8B5A2B;
  }
}

.item-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-meta {
  display: flex;
  gap: 20px;
  margin-top: auto;
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #999;
    
    &.time {
      margin-left: auto;
    }
    
    .el-icon {
      font-size: 14px;
    }
  }
}

.update-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: #f5f0eb;
  border-radius: 6px;
  font-size: 13px;
  color: #8B5A2B;
  
  .el-icon {
    font-size: 16px;
  }
  
  span {
    flex: 1;
  }
}

/* 空状态 */
.empty-state {
  padding: 80px 0;
  background: #fff;
  border-radius: 8px;
}

/* 推荐区域 */
.recommend-section {
  margin-top: 48px;
  
  .section-title {
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 20px;
    color: #1a1a1a;
  }
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.recommend-item {
  cursor: pointer;
  
  .recommend-cover {
    aspect-ratio: 4/3;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 12px;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }
  }
  
  &:hover .recommend-cover img {
    transform: scale(1.05);
  }
  
  .recommend-info {
    h4 {
      font-size: 14px;
      font-weight: 500;
      color: #1a1a1a;
      margin-bottom: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    p {
      font-size: 12px;
      color: #999;
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .my-subscriptions-page {
    padding-top: 64px;
  }
  
  .page-header {
    padding: 40px 0;
    
    h1 {
      font-size: 28px;
    }
  }
  
  .stats-bar {
    flex-direction: column;
  }
  
  .subscription-item {
    flex-direction: column;
  }
  
  .item-cover {
    width: 100%;
    height: 180px;
  }
  
  .item-meta {
    flex-wrap: wrap;
    gap: 12px;
    
    .meta-item.time {
      width: 100%;
      margin-left: 0;
    }
  }
  
  .recommend-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
