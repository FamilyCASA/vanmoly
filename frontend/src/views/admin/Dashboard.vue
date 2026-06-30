<template>
  <div class="dashboard-container">
    <section class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-kicker">运营总览</div>
        <h1 class="page-title">数据驾驶舱</h1>
        <p class="hero-desc">聚合线索、客户、报价、合同与财务数据，快速掌握今日经营状态。</p>
        <div class="hero-meta">
          <span>{{ currentTime }}</span>
          <span>数据实时同步</span>
        </div>
      </div>
      <div class="hero-actions">
        <el-button class="refresh-btn" :icon="Refresh" @click="handleRefresh" :loading="refreshing">
          刷新数据
        </el-button>
      </div>
    </section>

    <section class="kpi-grid">
      <div
        v-for="item in kpiCards"
        :key="item.label"
        class="kpi-card"
        :style="{ '--kpi-color': item.color, '--kpi-bg': item.bgColor }"
      >
        <div class="kpi-topline">
          <div class="kpi-icon">
            <el-icon :size="22"><component :is="item.icon" /></el-icon>
          </div>
          <span class="kpi-chip">{{ item.chip }}</span>
        </div>
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-label">{{ item.label }}</div>
        <div class="kpi-sub">
          <span>{{ item.subLabel }}</span>
          <strong>{{ item.subValue }}</strong>
        </div>
      </div>
    </section>

    <section class="top-workbench">
      <el-card shadow="never" class="panel-card quick-entry-card">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">快捷入口</span>
              <span class="card-subtitle">常用操作一键直达</span>
            </div>
          </div>
        </template>
        <div class="quick-entry-grid">
          <button
            v-for="item in quickEntries"
            :key="item.label"
            class="quick-entry-item"
            :style="{ '--entry-color': item.color, '--entry-bg': item.bgColor }"
            @click="handleQuickEntry(item)"
          >
            <span class="entry-icon">
              <el-icon :size="20"><component :is="item.icon" /></el-icon>
            </span>
            <span class="entry-label">{{ item.label }}</span>
          </button>
        </div>
      </el-card>

      <el-card shadow="never" class="panel-card todo-panel">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">待办提醒</span>
              <span class="card-subtitle">需要优先处理的事项</span>
            </div>
          </div>
        </template>
        <div class="todo-list">
          <button
            v-for="item in todoCards"
            :key="item.label"
            class="todo-card"
            :style="{ '--todo-bg': item.bgColor }"
            @click="handleTodoClick(item)"
          >
            <span class="todo-icon">
              <el-icon :size="20"><component :is="item.icon" /></el-icon>
            </span>
            <span class="todo-copy">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </span>
          </button>
        </div>
      </el-card>
    </section>

    <section class="finance-strip">
      <div class="section-heading">
        <div>
          <h2>财务快照</h2>
          <p>收入、支出、利润与应收应付概览</p>
        </div>
      </div>
      <div class="finance-grid">
        <div
          v-for="(item, index) in financeCards"
          :key="index"
          class="finance-card"
          :style="{ '--finance-color': item.color }"
        >
          <span class="finance-label">{{ item.label }}</span>
          <strong class="finance-value">{{ formatAmount(item.value) }}</strong>
        </div>
      </div>
    </section>

    <section class="chart-grid">
      <el-card shadow="never" class="panel-card chart-card chart-card-wide">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">月度收支趋势</span>
              <span class="card-subtitle">最近月份收入与支出对比</span>
            </div>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-container"></div>
      </el-card>

      <el-card shadow="never" class="panel-card chart-card">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">客户来源分布</span>
              <span class="card-subtitle">识别高质量获客渠道</span>
            </div>
          </div>
        </template>
        <div ref="sourceChartRef" class="chart-container"></div>
      </el-card>

      <el-card shadow="never" class="panel-card chart-card">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">报价状态分布</span>
              <span class="card-subtitle">跟踪报价推进状态</span>
            </div>
          </div>
        </template>
        <div ref="quoteChartRef" class="chart-container"></div>
      </el-card>

      <el-card shadow="never" class="panel-card chart-card chart-card-wide">
        <template #header>
          <div class="card-header">
            <div>
              <span class="card-title">客户状态分布</span>
              <span class="card-subtitle">查看客户生命周期结构</span>
            </div>
          </div>
        </template>
        <div ref="customerChartRef" class="chart-container"></div>
      </el-card>
    </section>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, TrendCharts, Money, DocumentChecked, Wallet,
  Refresh, Plus, Document, Calendar, Phone,
  OfficeBuilding, Upload, Download, Picture,
  List, DocumentAdd, DataAnalysis, Setting,
  Connection, Box, Reading, Notebook, EditPen, Files
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

const kpiCards = computed(() => [
  {
    label: '总客户数',
    value: formatNumber(overview.value.core?.total_customers),
    subLabel: '今日新增',
    subValue: overview.value.today?.new_customers || 0,
    chip: '客户',
    icon: User,
    color: '#2563EB',
    bgColor: '#EFF6FF'
  },
  {
    label: '总线索数',
    value: formatNumber(overview.value.core?.total_leads),
    subLabel: '今日新增',
    subValue: overview.value.today?.new_leads || 0,
    chip: '线索',
    icon: TrendCharts,
    color: '#059669',
    bgColor: '#ECFDF5'
  },
  {
    label: '总报价金额',
    value: formatAmount(overview.value.finance?.total_quote_amount),
    subLabel: '报价单数',
    subValue: overview.value.core?.total_quotes || 0,
    chip: '报价',
    icon: Money,
    color: '#D97706',
    bgColor: '#FFFBEB'
  },
  {
    label: '总合同金额',
    value: formatAmount(overview.value.finance?.total_contract_amount),
    subLabel: '本月新增合同',
    subValue: overview.value.month?.new_contracts || 0,
    chip: '合同',
    icon: DocumentChecked,
    color: '#7C3AED',
    bgColor: '#F5F3FF'
  }
])

// 快捷入口配置
const quickEntries = [
  // 用户指定的 10 个
  { label: '新建楼盘', icon: OfficeBuilding, color: '#409EFF', bgColor: '#E6F4FF', action: () => router.push('/admin/buildings') },
  { label: '新建线索', icon: Connection, color: '#67C23A', bgColor: '#F0F9EB', action: () => router.push('/admin/leads') },
  { label: '导入线索', icon: Download, color: '#E6A23C', bgColor: '#FDF6EC', action: () => router.push('/admin/leads?import=true') },
  { label: '新建客户', icon: User, color: '#F56C6C', bgColor: '#FEF0F0', action: () => router.push('/admin/customers') },
  { label: '新建案例', icon: Picture, color: '#722ED1', bgColor: '#F9F0FF', action: () => router.push('/admin/cases/create') },
  { label: '新建报价', icon: Money, color: '#1890FF', bgColor: '#E6F4FF', action: () => router.push('/admin/quotes') },
  { label: '新建合同', icon: DocumentAdd, color: '#52C41A', bgColor: '#F6FFED', action: () => router.push('/admin/contracts') },
  { label: '流水登记', icon: Wallet, color: '#FA8C16', bgColor: '#FFF7E6', action: () => router.push('/admin/finance') },
  { label: '上传物料', icon: Upload, color: '#13C2C2', bgColor: '#E6FFFB', action: () => router.push('/admin/settings?tab=material') },
  { label: '供应链登记', icon: Box, color: '#EB2F96', bgColor: '#FFF0F6', action: () => router.push('/admin/suppliers') },
  // 知识库相关
  { label: '知识库管理', icon: Reading, color: '#409EFF', bgColor: '#E6F4FF', action: () => router.push('/admin/settings?tab=knowledge') },
  { label: '编辑文章', icon: EditPen, color: '#722ED1', bgColor: '#F9F0FF', action: () => router.push('/admin/settings?tab=knowledge') },
  { label: '分类管理', icon: Files, color: '#13C2C2', bgColor: '#E6FFFB', action: () => router.push('/admin/settings?tab=knowledge') },
  { label: '商学院', icon: Notebook, color: '#FA8C16', bgColor: '#FFF7E6', action: () => router.push('/admin/knowledge') },
]

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

// 快捷入口点击
const handleQuickEntry = (item) => {
  item.action()
}

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

  trendChartInstance?.dispose()
  sourceChartInstance?.dispose()
  quoteChartInstance?.dispose()
  customerChartInstance?.dispose()
  
  // 月度收支趋势图
  if (trendChartRef.value) {
    trendChartInstance = echarts.init(trendChartRef.value)
    const trendData = overview.value.monthly_trend || []
    trendChartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['收入', '支出'], top: 10 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: trendData.map(item => item.month) },
      yAxis: { type: 'value', axisLabel: { formatter: val => val >= 10000 ? (val / 10000) + '万' : val } },
      series: [
        { name: '收入', type: 'bar', barWidth: '35%', itemStyle: { color: '#67C23A' }, data: trendData.map(item => item.income) },
        { name: '支出', type: 'bar', barWidth: '35%', itemStyle: { color: '#F56C6C' }, data: trendData.map(item => item.expense) }
      ]
    })
  }

  // 客户来源分布图
  if (sourceChartRef.value) {
    sourceChartInstance = echarts.init(sourceChartRef.value)
    const sourceData = overview.value.distributions?.customer_source || {}
    const sourceList = Object.entries(sourceData).map(([name, value]) => ({ name, value }))
    sourceChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      series: [{
        name: '客户来源', type: 'pie', radius: ['30%', '70%'], center: ['60%', '50%'],
        roseType: 'area',
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
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
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      series: [{
        name: '报价状态', type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
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
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: customerList.map(item => item.name) },
      series: [{
        name: '客户数量', type: 'bar', barWidth: '60%',
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
  padding: 24px;
  background:
    radial-gradient(circle at 12% 0%, rgba(64, 158, 255, 0.10), transparent 28%),
    linear-gradient(180deg, #F6F8FB 0%, #EEF2F7 100%);
  min-height: calc(100vh - 60px);
  color: #1F2937;
}

.dashboard-hero {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding: 26px 28px;
  margin-bottom: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FBFF 58%, #EEF6FF 100%);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.dashboard-hero::after {
  content: '';
  position: absolute;
  right: -80px;
  top: -100px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.12), transparent 70%);
  pointer-events: none;
}

.hero-content,
.hero-actions {
  position: relative;
  z-index: 1;
}

.hero-kicker {
  margin-bottom: 8px;
  color: #2563EB;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  color: #0F172A;
  font-size: 30px;
  font-weight: 750;
  line-height: 1.2;
}

.hero-desc {
  max-width: 620px;
  margin: 10px 0 16px;
  color: #64748B;
  font-size: 14px;
  line-height: 1.7;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.72);
  color: #475569;
  font-size: 12px;
}

.refresh-btn {
  height: 36px;
  border: 0;
  color: #fff;
  background: #2563EB;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.24);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.kpi-card {
  position: relative;
  min-height: 158px;
  padding: 18px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--kpi-bg), transparent 58%);
  opacity: 0.82;
  pointer-events: none;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.10);
}

.kpi-topline,
.kpi-value,
.kpi-label,
.kpi-sub {
  position: relative;
  z-index: 1;
}

.kpi-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.kpi-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--kpi-color);
  background: rgba(255, 255, 255, 0.78);
}

.kpi-chip {
  padding: 4px 8px;
  border-radius: 6px;
  color: var(--kpi-color);
  background: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 650;
}

.kpi-value {
  color: #0F172A;
  font-size: 30px;
  font-weight: 780;
  line-height: 1.1;
}

.kpi-label {
  margin-top: 8px;
  color: #475569;
  font-size: 14px;
  font-weight: 650;
}

.kpi-sub {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.22);
  color: #64748B;
  font-size: 12px;
}

.kpi-sub strong {
  color: var(--kpi-color);
  font-size: 14px;
}

.top-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(340px, 0.85fr);
  gap: 16px;
  margin-bottom: 16px;
}

.panel-card {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
}

.panel-card :deep(.el-card__header) {
  padding: 16px 18px 12px;
  border-bottom: 1px solid #EEF2F7;
}

.panel-card :deep(.el-card__body) {
  padding: 16px 18px 18px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: block;
  color: #0F172A;
  font-size: 15px;
  font-weight: 720;
}

.card-subtitle {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: #94A3B8;
}

.quick-entry-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.quick-entry-item {
  appearance: none;
  border: 1px solid transparent;
  background: #F8FAFC;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  min-height: 74px;
  padding: 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  color: #334155;
  transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.quick-entry-item:hover {
  transform: translateY(-2px);
  border-color: var(--entry-color);
  background: var(--entry-bg);
}

.entry-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--entry-color);
  background: #fff;
}

.entry-label {
  max-width: 100%;
  color: #334155;
  font-size: 12px;
  font-weight: 620;
  text-align: center;
  line-height: 1.25;
  white-space: normal;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.todo-card {
  appearance: none;
  width: 100%;
  min-height: 62px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: var(--todo-bg);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.todo-card:hover {
  transform: translateX(2px);
  border-color: rgba(37, 99, 235, 0.18);
}

.todo-icon {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  color: #334155;
}

.todo-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.todo-copy strong {
  color: #0F172A;
  font-size: 22px;
  line-height: 1;
}

.todo-copy span {
  color: #64748B;
  font-size: 13px;
}

.finance-strip {
  margin-bottom: 16px;
  padding: 18px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-heading h2 {
  margin: 0;
  color: #0F172A;
  font-size: 16px;
  font-weight: 720;
}

.section-heading p {
  margin: 4px 0 0;
  color: #94A3B8;
  font-size: 13px;
}

.finance-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.finance-card {
  background: #fff;
  border: 1px solid #EEF2F7;
  border-radius: 8px;
  padding: 14px;
  border-left: 3px solid var(--finance-color);
}

.finance-label {
  display: block;
  color: #64748B;
  font-size: 13px;
}

.finance-value {
  display: block;
  margin-top: 8px;
  color: var(--finance-color);
  font-size: 21px;
  font-weight: 760;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.chart-card {
  min-width: 0;
}

.chart-container {
  height: 300px;
  width: 100%;
}

@media (max-width: 1400px) {
  .quick-entry-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .top-workbench {
    grid-template-columns: 1fr;
  }

  .finance-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .quick-entry-grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .dashboard-hero {
    flex-direction: column;
    padding: 20px;
  }

  .hero-actions,
  .refresh-btn {
    width: 100%;
  }

  .kpi-grid,
  .finance-grid {
    grid-template-columns: 1fr;
  }

  .quick-entry-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .page-title {
    font-size: 26px;
  }
}
</style>
