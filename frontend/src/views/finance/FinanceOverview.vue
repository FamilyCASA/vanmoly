<template>
  <div class="finance-overview">
    <!-- 标题栏 -->
    <div class="overview-header">
      <h2>财务总览</h2>
      <div class="header-actions">
        <el-radio-group v-model="viewMode" size="small" @change="refreshCharts">
          <el-radio-button value="monthly">月视图</el-radio-button>
          <el-radio-button value="yearly">年视图</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="$router.push('/admin/finance?tab=transactions')">
          <el-icon><Plus /></el-icon> 录入流水
        </el-button>
      </div>
    </div>

    <!-- 1. 收支统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-inner today-card">
            <div class="stat-label">今日收支</div>
            <div class="stat-main">
              <div class="stat-number income">¥{{ formatNum(todayStats.income) }}</div>
              <div class="stat-number expense">¥{{ formatNum(todayStats.expense) }}</div>
            </div>
            <div class="stat-balance">
              结余 <span :class="todayStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ formatNum(todayStats.balance) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-inner month-card">
            <div class="stat-label">本月收支</div>
            <div class="stat-main">
              <div class="stat-number income">¥{{ formatNum(monthStats.income) }}</div>
              <div class="stat-number expense">¥{{ formatNum(monthStats.expense) }}</div>
            </div>
            <div class="stat-balance">
              结余 <span :class="monthStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ formatNum(monthStats.balance) }}
              </span>
            </div>
            <div class="stat-compare" :class="incomeCompareClass">
              {{ incomeCompareText }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-inner year-card">
            <div class="stat-label">本年收支</div>
            <div class="stat-main">
              <div class="stat-number income">¥{{ formatNum(yearStats.income) }}</div>
              <div class="stat-number expense">¥{{ formatNum(yearStats.expense) }}</div>
            </div>
            <div class="stat-balance">
              结余 <span :class="yearStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ formatNum(yearStats.balance) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-inner total-card">
            <div class="stat-label">累计收支</div>
            <div class="stat-main">
              <div class="stat-number income">¥{{ formatNum(totalStats.income) }}</div>
              <div class="stat-number expense">¥{{ formatNum(totalStats.expense) }}</div>
            </div>
            <div class="stat-balance">
              结余 <span :class="totalStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ formatNum(totalStats.balance) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 2. 现金流水趋势 + 分类占比 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>现金流水趋势</span>
              <div class="chart-legend">
                <span class="legend-item"><span class="dot income-dot"></span>收入</span>
                <span class="legend-item"><span class="dot expense-dot"></span>支出</span>
                <span class="legend-item"><span class="dot balance-dot"></span>结余</span>
              </div>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分类占比</span>
              <div class="pie-controls">
                <el-radio-group v-model="pieType" size="small" @change="refreshPieChart">
                  <el-radio-button value="expense">支出</el-radio-button>
                  <el-radio-button value="income">收入</el-radio-button>
                </el-radio-group>
                <el-select v-model="piePeriod" size="small" @change="loadCategoryStats" style="width: 90px; margin-left: 8px;">
                  <el-option label="本月" value="this_month" />
                  <el-option label="本年" value="this_year" />
                  <el-option label="全部" value="all" />
                </el-select>
              </div>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. 流水列表 -->
    <el-row :gutter="16" class="table-row">
      <el-col :span="24">
        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近流水</span>
              <el-button text type="primary" @click="$router.push('/admin/finance?tab=transactions')">
                查看全部 →
              </el-button>
            </div>
          </template>
          <el-table :data="recentTransactions" stripe empty-text="暂无流水记录">
            <el-table-column prop="trans_date" label="日期" width="110" />
            <el-table-column prop="trans_no" label="编号" width="160" />
            <el-table-column label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.trans_type === 'income' ? 'success' : 'danger'" size="small">
                  {{ row.trans_type === 'income' ? '收入' : '支出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="category_name" label="分类" width="120" />
            <el-table-column prop="summary" label="摘要" min-width="200" show-overflow-tooltip />
            <el-table-column label="金额" width="140" align="right">
              <template #default="{ row }">
                <span :class="row.trans_type === 'income' ? 'income' : 'expense'" class="amount-text">
                  {{ row.trans_type === 'income' ? '+' : '-' }}¥{{ formatNum(row.amount) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 4. 应收应付统计卡片 -->
    <el-row :gutter="16" class="placeholder-row">
      <el-col :span="12">
        <el-card shadow="hover" class="rp-card">
          <template #header>
            <div class="card-header">
              <span>应收款项</span>
              <el-button text type="primary" @click="goTab('receivables')">管理 →</el-button>
            </div>
          </template>
          <el-row :gutter="12">
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">应收总额</div>
                <div class="rp-stat-value primary">¥{{ formatNum(receivableSummary.total_amount) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">已收金额</div>
                <div class="rp-stat-value success">¥{{ formatNum(receivableSummary.received_amount) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">剩余应收</div>
                <div class="rp-stat-value warning">¥{{ formatNum(receivableSummary.remaining_amount) }}</div>
              </div>
            </el-col>
          </el-row>
          <div v-if="receivableSummary.overdue_count > 0" class="rp-alert">
            <el-tag type="danger" size="small">{{ receivableSummary.overdue_count }}笔逾期</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="rp-card">
          <template #header>
            <div class="card-header">
              <span>应付款项</span>
              <el-button text type="primary" @click="goTab('payables')">管理 →</el-button>
            </div>
          </template>
          <el-row :gutter="12">
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">应付总额</div>
                <div class="rp-stat-value primary">¥{{ formatNum(payableSummary.total_amount) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">已付金额</div>
                <div class="rp-stat-value success">¥{{ formatNum(payableSummary.paid_amount) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="rp-stat">
                <div class="rp-stat-label">剩余应付</div>
                <div class="rp-stat-value warning">¥{{ formatNum(payableSummary.remaining_amount) }}</div>
              </div>
            </el-col>
          </el-row>
          <div v-if="payableSummary.overdue_count > 0" class="rp-alert">
            <el-tag type="danger" size="small">{{ payableSummary.overdue_count }}笔逾期</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import financeAPI from '@/api/finance'

echarts.use([LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const viewMode = ref('monthly')
const pieType = ref('expense')
const piePeriod = ref('this_month')

const todayStats = ref({ income: 0, expense: 0, balance: 0 })
const monthStats = ref({ income: 0, expense: 0, balance: 0 })
const lastMonthStats = ref({ income: 0, expense: 0, balance: 0 })
const yearStats = ref({ income: 0, expense: 0, balance: 0 })
const totalStats = ref({ income: 0, expense: 0, balance: 0 })

const monthlyTrend = ref([])
const categoryBreakdown = ref([])
const recentTransactions = ref([])

// 应收应付汇总
const receivableSummary = ref({ total_amount: 0, received_amount: 0, remaining_amount: 0, overdue_count: 0 })
const payableSummary = ref({ total_amount: 0, paid_amount: 0, remaining_amount: 0, overdue_count: 0 })

const goTab = (tab) => {
  // Navigate to finance page with specific tab
  window.location.hash = `/admin/finance?tab=${tab}`
}

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

// 同比计算
const incomeCompare = computed(() => {
  const thisM = monthStats.value.income || 0
  const lastM = lastMonthStats.value.income || 0
  if (lastM === 0) return null
  return ((thisM - lastM) / lastM * 100).toFixed(1)
})
const expenseCompare = computed(() => {
  const thisM = monthStats.value.expense || 0
  const lastM = lastMonthStats.value.expense || 0
  if (lastM === 0) return null
  return ((thisM - lastM) / lastM * 100).toFixed(1)
})
const incomeCompareText = computed(() => incomeCompare.value ? `同比${incomeCompare.value > 0 ? '↑' : '↓'}${Math.abs(incomeCompare.value)}%` : '')
const expenseCompareText = computed(() => expenseCompare.value ? `同比${expenseCompare.value > 0 ? '↑' : '↓'}${Math.abs(expenseCompare.value)}%` : '')
const incomeCompareClass = computed(() => incomeCompare.value > 0 ? 'up' : 'down')
const expenseCompareClass = computed(() => expenseCompare.value > 0 ? 'up' : 'down')

const formatNum = (v) => {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const statusType = (s) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', deleted: 'info' }
  return map[s] || 'info'
}
const statusLabel = (s) => {
  const map = { pending: '待审', approved: '已通过', rejected: '已驳回', deleted: '已删' }
  return map[s] || s
}

onMounted(async () => {
  await loadAllData()
  nextTick(() => {
    initCharts()
  })
})

onUnmounted(() => {
  trendChart?.dispose()
  pieChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

const loadAllData = async () => {
  try {
    // 加载总览数据
    const overviewData = await financeAPI.getOverview()
    todayStats.value = {
      income: overviewData.today_income || 0,
      expense: overviewData.today_expense || 0,
      balance: overviewData.today_balance || 0
    }
    monthStats.value = {
      income: overviewData.month_income || 0,
      expense: overviewData.month_expense || 0,
      balance: overviewData.month_balance || 0
    }
    yearStats.value = {
      income: overviewData.year_income || 0,
      expense: overviewData.year_expense || 0,
      balance: overviewData.year_balance || 0
    }
    totalStats.value = {
      income: overviewData.total_income || 0,
      expense: overviewData.total_expense || 0,
      balance: overviewData.total_balance || 0
    }
    monthlyTrend.value = overviewData.monthly_trend || []
    categoryBreakdown.value = overviewData.category_breakdown || []
    recentTransactions.value = overviewData.recent_transactions || []

    // 加载分析数据（获取上月对比）
    const analysisData = await financeAPI.getAnalysisOverview()
    lastMonthStats.value = {
      income: analysisData.last_month?.income || 0,
      expense: analysisData.last_month?.expense || 0,
      balance: analysisData.last_month?.balance || 0
    }
    // 加载应收应付汇总
    try {
      const recvData = await financeAPI.getReceivables({ page: 1, page_size: 1 })
      receivableSummary.value = recvData.summary || receivableSummary.value
    } catch {}
    try {
      const payData = await financeAPI.getPayables({ page: 1, page_size: 1 })
      payableSummary.value = payData.summary || payableSummary.value
    } catch {}
  } catch (e) {
    console.error(e)
    ElMessage.error('加载财务总览数据失败')
  }
}

const loadCategoryStats = async () => {
  try {
    const d = await financeAPI.getCategoryStats({ period: piePeriod.value, trans_type: pieType.value })
    categoryBreakdown.value = d.items || []
    nextTick(() => {
      refreshPieChart()
    })
  } catch (e) {
    console.error('加载分类统计失败', e)
  }
}

const refreshCharts = () => {
  nextTick(() => {
    trendChart?.dispose()
    trendChart = null
    initTrendChart()
  })
}

const refreshPieChart = () => {
  nextTick(() => {
    pieChart?.dispose()
    pieChart = null
    initPieChart()
  })
}

const initCharts = () => {
  initTrendChart()
  initPieChart()
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)

  const months = monthlyTrend.value.map(m => m.month)
  const incomes = monthlyTrend.value.map(m => m.income)
  const expenses = monthlyTrend.value.map(m => m.expense)
  const balances = monthlyTrend.value.map(m => m.balance)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let s = `<strong>${params[0].axisValue}</strong><br/>`
        params.forEach(p => {
          s += `${p.marker} ${p.seriesName}: ¥${formatNum(p.value)}<br/>`
        })
        return s
      }
    },
    legend: {
      data: ['收入', '支出', '结余'],
      bottom: 0
    },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { fontSize: 11, color: '#909399', rotate: months.length > 8 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 11,
        color: '#909399',
        formatter: (v) => v >= 10000 ? (v / 10000).toFixed(0) + '万' : v.toFixed(0)
      },
      splitLine: { lineStyle: { type: 'dashed', color: '#ebeef5' } }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        smooth: true,
        data: incomes,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#67c23a' },
        itemStyle: { color: '#67c23a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.25)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.02)' }
          ])
        }
      },
      {
        name: '支出',
        type: 'line',
        smooth: true,
        data: expenses,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#f56c6c' },
        itemStyle: { color: '#f56c6c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.2)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.02)' }
          ])
        }
      },
      {
        name: '结余',
        type: 'bar',
        data: balances,
        itemStyle: {
          color: (params) => params.value >= 0 ? '#409eff' : '#f56c6c',
          borderRadius: [2, 2, 0, 0]
        }
      }
    ]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', handleResize)
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)

  const filtered = categoryBreakdown.value.filter(c => c.type === pieType.value)
  const data = filtered.slice(0, 8).map(c => ({
    name: c.category_name,
    value: c.total
  }))

  // 归并其他
  if (filtered.length > 8) {
    const others = filtered.slice(8).reduce((sum, c) => sum + c.total, 0)
    if (others > 0) data.push({ name: '其他', value: others })
  }

  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#b37feb', '#5cdbd3', '#ff85c0', '#d9d9d9']

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (p) => `${p.name}: ¥${formatNum(p.value)} (${p.percent}%)`
    },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      padAngle: 2,
      itemStyle: { borderRadius: 4 },
      label: {
        show: true,
        formatter: (p) => `${p.name}\n${p.percent}%`,
        fontSize: 11
      },
      labelLine: { length: 8, length2: 10 },
      emphasis: {
        label: { show: true, fontSize: 13, fontWeight: 'bold' }
      },
      data: data.map((d, i) => ({
        ...d,
        itemStyle: { color: colors[i % colors.length] }
      }))
    }]
  }

  pieChart.setOption(option)
  window.addEventListener('resize', handleResize)
}
</script>

<style scoped>
.finance-overview {
  padding: 0;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 统计卡片 */
.stats-row { margin-bottom: 16px; }

.stat-card { height: 100%; }
.stat-card :deep(.el-card__body) { padding: 0; }

.stat-inner {
  padding: 20px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.stat-inner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.today-card::before { background: linear-gradient(90deg, #409eff, #79bbff); }
.month-card::before { background: linear-gradient(90deg, #67c23a, #95d475); }
.year-card::before { background: linear-gradient(90deg, #e6a23c, #f4d19b); }
.total-card::before { background: linear-gradient(90deg, #909399, #c0c4cc); }

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.stat-main {
  display: flex;
  gap: 24px;
}

.stat-number {
  font-size: 22px;
  font-weight: bold;
  font-family: 'SF Mono', 'Menlo', monospace;
}

.stat-number.income { color: #67c23a; }
.stat-number.expense { color: #f56c6c; }

.stat-balance {
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
}

.stat-balance .income { color: #67c23a; font-weight: 600; font-size: 16px; }
.stat-balance .expense { color: #f56c6c; font-weight: 600; font-size: 16px; }

.stat-compare {
  margin-top: 8px;
  font-size: 12px;
}
.stat-compare.up { color: #f56c6c; }
.stat-compare.down { color: #67c23a; }

/* 图表行 */
.chart-row { margin-bottom: 16px; }

.chart-card { height: 100%; }
.chart-container { width: 100%; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}

.chart-legend { display: flex; gap: 16px; }
.legend-item { font-size: 12px; color: #606266; display: flex; align-items: center; gap: 4px; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.income-dot { background: #67c23a; }
.expense-dot { background: #f56c6c; }
.balance-dot { background: #409eff; }

.pie-controls {
  display: flex;
  align-items: center;
}

/* 表格 */
.table-row { margin-bottom: 16px; }

.recent-card { margin-bottom: 16px; }

.amount-text {
  font-weight: 600;
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 14px;
}
.amount-text.income { color: #67c23a; }
.amount-text.expense { color: #f56c6c; }

/* 应收应付卡片 */
.rp-card { height: 100%; }
.rp-stat { text-align: center; padding: 8px 0; }
.rp-stat-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.rp-stat-value { font-size: 18px; font-weight: bold; font-family: 'SF Mono', monospace; }
.rp-stat-value.primary { color: #409eff; }
.rp-stat-value.success { color: #67c23a; }
.rp-stat-value.warning { color: #e6a23c; }
.rp-alert { margin-top: 10px; text-align: center; }

.placeholder-row { margin-top: 16px; }

.placeholder-card {
  border: 1px dashed #dcdfe6;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
}

.placeholder-content p {
  margin: 8px 0 0 0;
  font-size: 14px;
}

.placeholder-hint {
  font-size: 12px !important;
  color: #c0c4cc !important;
}
</style>
