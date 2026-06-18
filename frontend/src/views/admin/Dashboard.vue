<template>
  <div class="dashboard-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据驾驶舱</h1>
        <div class="current-time">{{ currentTime }}</div>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Refresh" @click="handleRefresh" :loading="refreshing">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 核心KPI指标行 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <div class="kpi-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="kpi-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatNumber(overview.core?.total_customers) }}</div>
            <div class="kpi-label">总客户数</div>
            <div class="kpi-sub">今日新增 <span class="kpi-sub-value">{{ overview.today?.new_customers || 0 }}</span></div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="kpi-icon">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatNumber(overview.core?.total_leads) }}</div>
            <div class="kpi-label">总线索数</div>
            <div class="kpi-sub">今日新增 <span class="kpi-sub-value">{{ overview.today?.new_leads || 0 }}</span></div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="kpi-icon">
            <el-icon :size="32"><Money /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatAmount(overview.finance?.total_quote_amount) }}</div>
            <div class="kpi-label">总报价金额</div>
            <div class="kpi-sub">共 <span class="kpi-sub-value">{{ overview.core?.total_quotes || 0 }}</span> 单</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <div class="kpi-icon">
            <el-icon :size="32"><DocumentChecked /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatAmount(overview.finance?.total_contract_amount) }}</div>
            <div class="kpi-label">总合同金额</div>
            <div class="kpi-sub">本月新增 <span class="kpi-sub-value">{{ overview.month?.new_contracts || 0 }}</span></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 财务数据行 -->
    <el-row :gutter="16" class="finance-row">
      <el-col :span="4" v-for="(item, index) in financeCards" :key="index">
        <div class="finance-card" :style="{ borderLeftColor: item.color }">
          <div class="finance-label">{{ item.label }}</div>
          <div class="finance-value" :style="{ color: item.color }">{{ formatAmount(item.value) }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行第一排 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">月度收支趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">客户来源分布</span>
            </div>
          </template>
          <div ref="sourceChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行第二排 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">报价状态分布</span>
            </div>
          </template>
          <div ref="quoteChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">客户状态分布</span>
            </div>
          </template>
          <div ref="customerChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办事项行 -->
    <el-row :gutter="16" class="todo-row">
      <el-col :span="6" v-for="(item, index) in todoCards" :key="index">
        <div class="todo-card" :style="{ background: item.bgColor }" @click="handleTodoClick(item)">
          <div class="todo-icon">
            <el-icon :size="24"><component :is="item.icon" /></el-icon>
          </div>
          <div class="todo-content">
            <div class="todo-value">{{ item.value }}</div>
            <div class="todo-label">{{ item.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作行 -->
    <el-card shadow="hover" class="quick-actions-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">快捷操作</span>
        </div>
      </template>
      <div class="quick-actions">
        <el-button type="primary" :icon="Plus" @click="$router.push('/admin/customers')">新建客户</el-button>
        <el-button type="success" :icon="Money" @click="$router.push('/admin/quotes')">新建报价</el-button>
        <el-button type="warning" :icon="DocumentChecked" @click="$router.push('/admin/contracts')">新建合同</el-button>
        <el-button type="info" :icon="Wallet" @click="$router.push('/admin/finance')">收支登记</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, TrendCharts, Money, DocumentChecked, Wallet,
  Refresh, Plus, Document, Calendar, Phone
} from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getDashboardOverview } from '@/api/dashboard'

echarts.use([
  BarChart, PieChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  CanvasRenderer
])

const router = useRouter()
const refreshing = ref(false)
const currentTime = ref('')
const overview = ref({
  core: {},
  today: {},
  month: {},
  finance: {},
  distributions: {},
  todos: {},
  monthly_trend: []
})

let timeInterval = null
let trendChartInstance = null
let sourceChartInstance = null
let quoteChartInstance = null
let customerChartInstance = null

const trendChartRef = ref(null)
const sourceChartRef = ref(null)
const quoteChartRef = ref(null)
const customerChartRef = ref(null)

// 财务卡片数据
const financeCards = computed(() => [
  { label: '累计收入', value: overview.value.finance?.total_income || 0, color: '#67C23A' },
  { label: '累计支出', value: overview.value.finance?.total_expense || 0, color: '#F56C6C' },
  { label: '累计利润', value: overview.value.finance?.total_profit || 0, color: '#E6A23C' },
  { label: '待收金额', value: overview.value.finance?.pending_receivable || 0, color: '#722ED1' },
  { label: '待付金额', value: overview.value.finance?.pending_payable || 0, color: '#409EFF' }
])

// 待办卡片数据
const todoCards = computed(() => [
  {
    label: '待审核报价',
    value: overview.value.todos?.pending_quotes || 0,
    icon: Document,
    bgColor: '#FFF7E6',
    path: '/admin/quotes'
  },
  {
    label: '待跟进客户',
    value: overview.value.todos?.follow_up_customers || 0,
    icon: Phone,
    bgColor: '#E6F7FF',
    path: '/admin/customers'
  },
  {
    label: '待确认预约',
    value: overview.value.todos?.pending_appointments || 0,
    icon: Calendar,
    bgColor: '#F6FFED',
    path: '/admin/appointments'
  },
  {
    label: '待审批报销',
    value: overview.value.todos?.pending_reimbursements || 0,
    icon: Wallet,
    bgColor: '#F9F0FF',
    path: '/admin/finance'
  }
])

// 格式化数字
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return num.toLocaleString()
}

// 格式化金额
const formatAmount = (amount) => {
  if (!amount || amount === 0) return '¥0'
  if (amount >= 10000) {
    return '¥' + (amount / 10000).toFixed(1) + '万'
  }
  return '¥' + amount.toLocaleString()
}

// 更新当前时间
const updateTime = () => {
  const now = new Date()
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  currentTime.value = now.toLocaleString('zh-CN', options)
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 月度收支趋势图
  if (trendChartRef.value) {
    trendChartInstance = echarts.init(trendChartRef.value)
    const trendData = overview.value.monthly_trend || []
    trendChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['收入', '支出'],
        top: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: trendData.map(item => item.month)
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: val => val >= 10000 ? (val / 10000) + '万' : val
        }
      },
      series: [
        {
          name: '收入',
          type: 'bar',
          barWidth: '35%',
          itemStyle: { color: '#67C23A' },
          data: trendData.map(item => item.income)
        },
        {
          name: '支出',
          type: 'bar',
          barWidth: '35%',
          itemStyle: { color: '#F56C6C' },
          data: trendData.map(item => item.expense)
        }
      ]
    })
  }

  // 客户来源分布图
  if (sourceChartRef.value) {
    sourceChartInstance = echarts.init(sourceChartRef.value)
    const sourceData = overview.value.distributions?.customer_source || {}
    const sourceList = Object.entries(sourceData).map(([name, value]) => ({ name, value }))
    sourceChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'center'
      },
      series: [{
        name: '客户来源',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['60%', '50%'],
        roseType: 'area',
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        data: sourceList.length > 0 ? sourceList : [{ name: '暂无数据', value: 1 }]
      }]
    })
  }

  // 报价状态分布图
  if (quoteChartRef.value) {
    quoteChartInstance = echarts.init(quoteChartRef.value)
    const quoteData = overview.value.distributions?.quote_status || {}
    const quoteList = Object.entries(quoteData).map(([name, value]) => ({ name, value }))
    quoteChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'center'
      },
      series: [{
        name: '报价状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold' }
        },
        data: quoteList.length > 0 ? quoteList : [{ name: '暂无数据', value: 1 }]
      }]
    })
  }

  // 客户状态分布图
  if (customerChartRef.value) {
    customerChartInstance = echarts.init(customerChartRef.value)
    const customerData = overview.value.distributions?.customer_status || {}
    const customerList = Object.entries(customerData).map(([name, value]) => ({ name, value }))
    customerChartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: customerList.map(item => item.name)
      },
      series: [{
        name: '客户数量',
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#67C23A' }
          ])
        },
        data: customerList.map(item => item.value)
      }]
    })
  }
}

// 加载数据
const loadData = async () => {
  try {
    refreshing.value = true
    const res = await getDashboardOverview()
    if (res) {
      const data = res.data || res
      overview.value = data
      await nextTick()
      initCharts()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    refreshing.value = false
  }
}

// 刷新数据
const handleRefresh = async () => {
  await loadData()
  ElMessage.success('数据已刷新')
}

// 待办点击
const handleTodoClick = (item) => {
  router.push(item.path)
}

// 窗口大小变化时重新调整图表
const handleResize = () => {
  trendChartInstance?.resize()
  sourceChartInstance?.resize()
  quoteChartInstance?.resize()
  customerChartInstance?.resize()
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  trendChartInstance?.dispose()
  sourceChartInstance?.dispose()
  quoteChartInstance?.dispose()
  customerChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 页面标题栏 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.current-time {
  font-size: 14px;
  color: #909399;
}

/* KPI 卡片 */
.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  border-radius: 12px;
  padding: 24px;
  color: #fff;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.kpi-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  opacity: 0.75;
  margin-top: 8px;
}

.kpi-sub-value {
  font-weight: 600;
  color: #fff;
}

/* 财务卡片 */
.finance-row {
  margin-bottom: 20px;
}

.finance-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px 16px;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s;
}

.finance-card:hover {
  transform: translateY(-2px);
}

.finance-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.finance-value {
  font-size: 22px;
  font-weight: 600;
}

/* 图表卡片 */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  height: 320px;
  width: 100%;
}

/* 待办卡片 */
.todo-row {
  margin-bottom: 20px;
}

.todo-card {
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.todo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.todo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: #606266;
}

.todo-content {
  flex: 1;
}

.todo-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.todo-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* 快捷操作 */
.quick-actions-card {
  border-radius: 8px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
