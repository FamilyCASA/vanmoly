<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>数据看板</h2>
      <span class="subtitle">实时数据监控与业务分析</span>
    </div>

    <!-- 快捷入口 -->
    <el-row :gutter="16" class="quick-entry-row">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>快捷入口</span>
            </div>
          </template>
          <div class="quick-links">
            <div v-for="(link, index) in quickLinks" :key="index" class="quick-link" @click="$router.push(link.path)">
              <div class="quick-icon" :style="{ background: link.bgColor }">
                <el-icon><component :is="link.icon" /></el-icon>
              </div>
              <div class="quick-name">{{ link.name }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 核心指标卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <div class="stat-card primary">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.customers || 0 }}</div>
            <div class="stat-label">总客户</div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.contracts || 0 }}</div>
            <div class="stat-label">合同数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card warning">
          <div class="stat-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatAmount(stats.contractAmount) }}</div>
            <div class="stat-label">合同金额</div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card danger">
          <div class="stat-icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.materials || 0 }}</div>
            <div class="stat-label">物料数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card info">
          <div class="stat-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.buildings || 0 }}</div>
            <div class="stat-label">楼盘数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card purple">
          <div class="stat-icon">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.employees || 0 }}</div>
            <div class="stat-label">员工数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>业务趋势</span>
              <el-radio-group v-model="trendPeriod" size="small" @change="loadTrends">
                <el-radio-button value="week">本周</el-radio-button>
                <el-radio-button value="month">本月</el-radio-button>
                <el-radio-button value="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>合同金额分布</span>
            </div>
          </template>
          <div ref="contractChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办事项和快捷入口 -->
    <el-row :gutter="16" class="bottom-row">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
              <el-button type="primary" link @click="refreshTodo">刷新</el-button>
            </div>
          </template>
          <div class="todo-list">
            <div v-for="(item, index) in todoList" :key="index" class="todo-item">
              <div class="todo-icon" :class="item.type">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <div class="todo-content">
                <div class="todo-title">{{ item.title }}</div>
                <div class="todo-desc">{{ item.desc }}</div>
              </div>
              <div class="todo-action">
                <el-button type="primary" size="small" text @click="handleTodo(item)">
                  去处理
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近动态 -->
    <el-card shadow="never" class="activity-card">
      <template #header>
        <div class="card-header">
          <span>最近动态</span>
          <el-button type="primary" link @click="loadActivities">刷新</el-button>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(activity, index) in recentActivities"
          :key="index"
          :type="activity.type"
          :timestamp="activity.time"
        >
          {{ activity.content }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([LineChart, PieChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])
import {
  User, DocumentChecked, Money, Box, OfficeBuilding, UserFilled,
  Bell, Document, ShoppingCart, Phone, Plus, TrendCharts,
  Calendar, Setting, Files, Picture,
  Upload, Collection, List, Wallet
} from '@element-plus/icons-vue'
import {
  getDashboardStats,
  getTrends,
  getContractDistribution,
  getRecentActivities
} from '@/api/dashboard'

const router = useRouter()
const trendChart = ref(null)
const contractChart = ref(null)
const trendPeriod = ref('week')
const loading = ref(false)

let trendChartInstance = null
let contractChartInstance = null

// 统计数据
const stats = ref({
  customers: 0,
  contracts: 0,
  contractAmount: 0,
  materials: 0,
  buildings: 0,
  employees: 0
})

// 待办事项
const todoList = ref([
  { type: 'warning', icon: 'Document', title: '待审核报价单', desc: '0个报价单等待审核', action: '/admin/quotes' },
  { type: 'danger', icon: 'ShoppingCart', title: '库存预警', desc: '0个物料库存不足', action: '/admin/materials' },
  { type: 'info', icon: 'Phone', title: '待跟进客户', desc: '0个客户需要今日跟进', action: '/admin/customers' },
  { type: 'success', icon: 'Calendar', title: '今日预约', desc: '0个量尺预约待确认', action: '/admin/appointments' }
])

// 快捷入口 - 按业务时序排列
const quickLinks = ref([
  // 第一排：获客与客户管理
  { name: '批量导入线索', path: '/admin/leads', icon: 'Upload', bgColor: '#409EFF' },
  { name: '新建客户', path: '/admin/customers', icon: 'User', bgColor: '#67C23A' },
  { name: '新建楼盘', path: '/admin/buildings', icon: 'OfficeBuilding', bgColor: '#E6A23C' },
  { name: '预约管理', path: '/admin/appointments', icon: 'Calendar', bgColor: '#909399' },
  // 第二排：核心业务与交付管理
  { name: '新建报价', path: '/admin/quotes', icon: 'Money', bgColor: '#F56C6C' },
  { name: '新建合同', path: '/admin/contracts', icon: 'Collection', bgColor: '#722ED1' },
  { name: '任务发布', path: '/admin/workflow', icon: 'List', bgColor: '#13C2C2' },
  { name: '物料管理', path: '/admin/materials', icon: 'Box', bgColor: '#EB2F96' },
  // 第三排：内容与管理工具
  { name: '新建案例', path: '/admin/cases/create', icon: 'Picture', bgColor: '#F56C6C' },
  { name: '员工管理', path: '/admin/employees', icon: 'User', bgColor: '#409EFF' },
  { name: '文件管理', path: '/admin/files', icon: 'Files', bgColor: '#67C23A' },
  { name: '数据报表', path: '/admin/dashboard', icon: 'TrendCharts', bgColor: '#E6A23C' },
  { name: '系统设置', path: '/admin/frontend', icon: 'Setting', bgColor: '#909399' },
  // 第四排：财务管理
  { name: '收支登记', path: '/finance/transactions', icon: 'Wallet', bgColor: '#722ED1' }
])

// 最近动态
const recentActivities = ref([])

// 格式化金额
const formatAmount = (amount) => {
  if (!amount) return '¥0'
  if (amount >= 10000) {
    return '¥' + (amount / 10000).toFixed(1) + '万'
  }
  return '¥' + amount.toLocaleString()
}

// 初始化图表
const initCharts = () => {
  // 业务趋势图
  if (trendChart.value) {
    trendChartInstance = echarts.init(trendChart.value)
    trendChartInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['新增客户', '合同金额', '报价数'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: []
      },
      yAxis: [
        { type: 'value', name: '数量' },
        { type: 'value', name: '金额', axisLabel: { formatter: (val) => val >= 10000 ? (val/10000) + '万' : val } }
      ],
      series: [
        {
          name: '新增客户',
          type: 'line',
          smooth: true,
          data: []
        },
        {
          name: '合同金额',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: []
        },
        {
          name: '报价数',
          type: 'line',
          smooth: true,
          data: []
        }
      ]
    })
  }

  // 合同金额分布图
  if (contractChart.value) {
    contractChartInstance = echarts.init(contractChart.value)
    contractChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}个 ({d}%)' },
      legend: { orient: 'vertical', left: 'left' },
      series: [
        {
          name: '合同金额',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false, position: 'center' },
          emphasis: {
            label: { show: true, fontSize: 20, fontWeight: 'bold' }
          },
          labelLine: { show: false },
          data: []
        }
      ]
    })
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    loading.value = true
    const res = await getDashboardStats()
    console.log('Dashboard stats response:', res)
    if (res) {
      // 兼容两种返回格式：直接数据对象或嵌套在data中
      const data = res.data || res
      stats.value = data.overview || {}
      
      // 更新待办事项
      const todo = data.todo || {}
      todoList.value = [
        { type: 'warning', icon: 'Document', title: '待审核报价单', desc: `${todo.pendingQuotes || 0}个报价单等待审核`, action: '/admin/quotes' },
        { type: 'danger', icon: 'ShoppingCart', title: '库存预警', desc: `${todo.lowStockMaterials || 0}个物料库存不足`, action: '/admin/materials' },
        { type: 'info', icon: 'Phone', title: '待跟进客户', desc: '点击查看待跟进客户', action: '/admin/customers' },
        { type: 'success', icon: 'Calendar', title: '今日预约', desc: `${todo.pendingAppointments || 0}个量尺预约待确认`, action: '/admin/appointments' }
      ]
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

// 加载趋势数据
const loadTrends = async () => {
  try {
    const res = await getTrends(trendPeriod.value)
    console.log('Trends response:', res)
    if (res && trendChartInstance) {
      const data = res.data || res
      trendChartInstance.setOption({
        xAxis: { data: data.dates || [] },
        series: [
          { name: '新增客户', data: data.newCustomers || [] },
          { name: '合同金额', data: data.contractAmount || [] },
          { name: '报价数', data: data.newQuotes || [] }
        ]
      })
    }
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

// 加载合同分布
const loadContractDistribution = async () => {
  try {
    const res = await getContractDistribution()
    console.log('Contract distribution response:', res)
    if (res && contractChartInstance) {
      const data = res.data || res
      const list = Array.isArray(data) ? data : []
      contractChartInstance.setOption({
        series: [{
          data: list.map(item => ({
            name: item.name,
            value: item.count
          }))
        }]
      })
    }
  } catch (error) {
    console.error('加载合同分布失败:', error)
  }
}

// 加载最近动态
const loadActivities = async () => {
  try {
    const res = await getRecentActivities(10)
    console.log('Activities response:', res)
    if (res) {
      const data = res.data || res
      recentActivities.value = Array.isArray(data) ? data : []
    }
  } catch (error) {
    console.error('加载最近动态失败:', error)
  }
}

// 刷新待办
const refreshTodo = () => {
  loadStats()
  ElMessage.success('已刷新')
}

// 处理待办事项
const handleTodo = (item) => {
  router.push(item.action)
}

onMounted(() => {
  initCharts()
  loadStats()
  loadTrends()
  loadContractDistribution()
  loadActivities()
  
  window.addEventListener('resize', () => {
    trendChartInstance?.resize()
    contractChartInstance?.resize()
  })
})

onUnmounted(() => {
  trendChartInstance?.dispose()
  contractChartInstance?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.stat-card.primary { border-left: 4px solid #409EFF; }
.stat-card.success { border-left: 4px solid #67C23A; }
.stat-card.warning { border-left: 4px solid #E6A23C; }
.stat-card.danger { border-left: 4px solid #F56C6C; }
.stat-card.info { border-left: 4px solid #909399; }
.stat-card.purple { border-left: 4px solid #722ED1; }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 12px;
}

.stat-card.primary .stat-icon { background: #E6F7FF; color: #409EFF; }
.stat-card.success .stat-icon { background: #F6FFED; color: #67C23A; }
.stat-card.warning .stat-icon { background: #FFF7E6; color: #E6A23C; }
.stat-card.danger .stat-icon { background: #FFF1F0; color: #F56C6C; }
.stat-card.info .stat-icon { background: #F4F4F5; color: #909399; }
.stat-card.purple .stat-icon { background: #F9F0FF; color: #722ED1; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.chart-row {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.bottom-row {
  margin-bottom: 16px;
}

.todo-list {
  padding: 8px 0;
}

.todo-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #EBEEF5;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 12px;
}

.todo-icon.warning { background: #FFF7E6; color: #E6A23C; }
.todo-icon.danger { background: #FFF1F0; color: #F56C6C; }
.todo-icon.info { background: #F4F4F5; color: #909399; }
.todo-icon.success { background: #F6FFED; color: #67C23A; }

.todo-content {
  flex: 1;
}

.todo-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.todo-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 12px 0;
}

.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 16px 8px;
  border-radius: 8px;
  transition: background 0.3s;
}

.quick-link:hover {
  background: #F5F7FA;
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  margin-bottom: 8px;
}

.quick-name {
  font-size: 13px;
  color: #606266;
}

.activity-card {
  margin-top: 16px;
}
</style>
