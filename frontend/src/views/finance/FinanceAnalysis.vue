<template>
  <div class="finance-analysis">
    <div class="page-header">
      <h2>财务分析</h2>
      <el-button @click="refreshAll" :icon="Refresh">刷新数据</el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card income-card">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-label">本月收入</div>
            <div class="stat-value">¥{{ formatNum(overview.this_month.income) }}</div>
            <div class="stat-compare" :class="incomeCompareClass">
              {{ incomeCompareText }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card expense-card">
          <div class="stat-icon">📉</div>
          <div class="stat-info">
            <div class="stat-label">本月支出</div>
            <div class="stat-value">¥{{ formatNum(overview.this_month.expense) }}</div>
            <div class="stat-compare" :class="expenseCompareClass">
              {{ expenseCompareText }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card balance-card">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-label">本月结余</div>
            <div class="stat-value" :class="{ negative: overview.this_month.balance < 0 }">
              ¥{{ formatNum(overview.this_month.balance) }}
            </div>
            <div class="stat-compare">
              累计：¥{{ formatNum(overview.total.balance) }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card total-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-label">交易笔数</div>
            <div class="stat-value">{{ recentTransactions.length }}</div>
            <div class="stat-compare">
              最近{{ recentTransactions.length }}笔
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" class="charts-row">
      <!-- 月度趋势图 -->
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>月度收支趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container" style="height: 350px"></div>
        </el-card>
      </el-col>

      <!-- 分类占比图 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>支出分类占比</span>
              <el-radio-group v-model="categoryPeriod" size="small" @change="loadCategoryStats">
                <el-radio-button value="this_month">本月</el-radio-button>
                <el-radio-button value="this_year">本年</el-radio-button>
                <el-radio-button value="all">全部</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近交易 -->
    <el-card shadow="never" class="recent-card">
      <template #header>
        <div class="card-header">
          <span>最近交易</span>
          <router-link to="/finance/transactions">
            <el-button text type="primary">查看全部</el-button>
          </router-link>
        </div>
      </template>
      <el-table :data="recentTransactions" stripe size="small">
        <el-table-column prop="tx_date" label="日期" width="110" />
        <el-table-column prop="tx_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.tx_type === 'income' ? 'success' : 'danger'" size="small" effect="plain">
              {{ row.tx_type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="summary" label="摘要" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="130" align="right">
          <template #default="{ row }">
            <span :class="row.tx_type === 'income' ? 'income-text' : 'expense-text'">
              {{ row.tx_type === 'income' ? '+' : '-' }}¥{{ formatNum(row.amount) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import financeAPI from '@/api/finance'

const overview = ref({
  this_month: { income: 0, expense: 0, balance: 0 },
  last_month: { income: 0, expense: 0, balance: 0 },
  total: { income: 0, expense: 0, balance: 0 }
})

const monthlyTrend = ref([])
const categoryStats = ref({ items: [], total: 0 })
const recentTransactions = ref([])
const categoryPeriod = ref('this_month')

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

// 计算同比
const incomeCompare = computed(() => {
  const thisM = overview.value.this_month.income || 0
  const lastM = overview.value.last_month.income || 0
  if (lastM === 0) return null
  return ((thisM - lastM) / lastM * 100).toFixed(1)
})
const expenseCompare = computed(() => {
  const thisM = overview.value.this_month.expense || 0
  const lastM = overview.value.last_month.expense || 0
  if (lastM === 0) return null
  return ((thisM - lastM) / lastM * 100).toFixed(1)
})
const incomeCompareText = computed(() => incomeCompare.value ? `同比${incomeCompare.value > 0 ? '↑' : '↓'}${Math.abs(incomeCompare.value)}%` : '')
const expenseCompareText = computed(() => expenseCompare.value ? `同比${expenseCompare.value > 0 ? '↑' : '↓'}${Math.abs(expenseCompare.value)}%` : '')
const incomeCompareClass = computed(() => incomeCompare.value > 0 ? 'up' : 'down')
const expenseCompareClass = computed(() => expenseCompare.value > 0 ? 'up' : 'down')

const formatNum = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const loadOverview = async () => {
  try {
    const d = await financeAPI.getAnalysisOverview()
    overview.value = d
  } catch (e) {
    console.error('加载总览失败', e)
  }
}

const loadMonthlyTrend = async () => {
  try {
    const d = await financeAPI.getMonthlyTrend()
    monthlyTrend.value = d
    await nextTick()
    renderTrendChart()
  } catch (e) {
    console.error('加载趋势失败', e)
  }
}

const loadCategoryStats = async () => {
  try {
    const d = await financeAPI.getCategoryStats({ period: categoryPeriod.value, tx_type: 'expense' })
    categoryStats.value = d
    await nextTick()
    renderPieChart()
  } catch (e) {
    console.error('加载分类统计失败', e)
  }
}

const loadRecentTransactions = async () => {
  try {
    const d = await financeAPI.getRecentTransactions({ limit: 10 })
    recentTransactions.value = d || []
  } catch (e) {
    console.error('加载最近交易失败', e)
  }
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  const months = monthlyTrend.value.map(m => m.month)
  const incomes = monthlyTrend.value.map(m => m.income)
  const expenses = monthlyTrend.value.map(m => m.expense)
  const balances = monthlyTrend.value.map(m => m.balance)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出', '结余'], bottom: 0 },
    grid: { left: 60, right: 30, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    series: [
      { name: '收入', type: 'line', data: incomes, smooth: true, itemStyle: { color: '#67c23a' } },
      { name: '支出', type: 'line', data: expenses, smooth: true, itemStyle: { color: '#f56c6c' } },
      { name: '结余', type: 'bar', data: balances, itemStyle: { color: '#409eff' } }
    ]
  })
}

const renderPieChart = () => {
  if (!pieChartRef.value) return
  if (!pieChart) {
    pieChart = echarts.init(pieChartRef.value)
  }
  const items = categoryStats.value.items || []
  const data = items.map(item => ({ name: item.name, value: item.amount }))
  const colors = items.map(item => item.color || '#409eff')

  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', type: 'scroll' },
    color: colors,
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data
    }]
  })
}

const refreshAll = () => {
  loadOverview()
  loadMonthlyTrend()
  loadCategoryStats()
  loadRecentTransactions()
}

// 响应式chart resize
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  refreshAll()
  window.addEventListener('resize', handleResize)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.finance-analysis { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; font-size: 20px; }

/* 统计卡片 */
.stats-row { margin-bottom: 16px; }
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #ebeef5;
}
.stat-icon { font-size: 32px; }
.stat-info { flex: 1; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.stat-value { font-size: 22px; font-weight: 700; color: #303133; }
.stat-value.negative { color: #f56c6c; }
.stat-compare { font-size: 12px; color: #909399; margin-top: 4px; }
.stat-compare.up { color: #f56c6c; }
.stat-compare.down { color: #67c23a; }

.income-card { border-left: 4px solid #67c23a; }
.expense-card { border-left: 4px solid #f56c6c; }
.balance-card { border-left: 4px solid #409eff; }
.total-card { border-left: 4px solid #e6a23c; }

/* 图表区 */
.charts-row { margin-bottom: 16px; }
.chart-container { width: 100%; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 最近交易 */
.recent-card { margin-bottom: 20px; }
.income-text { color: #67c23a; font-weight: 600; }
.expense-text { color: #f56c6c; font-weight: 600; }

:deep(.el-card__header) { padding: 12px 16px; border-bottom: 1px solid #ebeef5; }
:deep(.el-card__body) { padding: 16px; }
</style>
