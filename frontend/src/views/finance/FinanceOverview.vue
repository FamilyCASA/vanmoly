<template>
  <div class="finance-overview">
    <h2>财务总览</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="12">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>今日收支</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-item">
              <span class="label">收入：</span>
              <span class="amount income">¥{{ todayStats.income.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">支出：</span>
              <span class="amount expense">¥{{ todayStats.expense.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">结余：</span>
              <span class="amount" :class="todayStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ todayStats.balance.toFixed(2) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>本月收支</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-item">
              <span class="label">收入：</span>
              <span class="amount income">¥{{ monthStats.income.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">支出：</span>
              <span class="amount expense">¥{{ monthStats.expense.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">结余：</span>
              <span class="amount" :class="monthStats.balance >= 0 ? 'income' : 'expense'">
                ¥{{ monthStats.balance.toFixed(2) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="action-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <el-button type="primary" @click="$router.push('/finance/transactions')">
            录入流水
          </el-button>
          <el-button type="success" @click="$router.push('/finance/reimbursements')">
            提交报销
          </el-button>
          <el-button @click="$router.push('/finance/transactions')">
            查看流水
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import financeAPI from '@/api/finance'
import { ElMessage } from 'element-plus'

const todayStats = ref({
  income: 0,
  expense: 0,
  balance: 0
})

const monthStats = ref({
  income: 0,
  expense: 0,
  balance: 0
})

onMounted(async () => {
  await loadOverview()
})

const loadOverview = async () => {
  try {
    const res = await financeAPI.getOverview()
    if (res.code === 200) {
      const data = res.data
      todayStats.value = {
        income: data.today_income || 0,
        expense: data.today_expense || 0,
        balance: data.today_balance || 0
      }
      monthStats.value = {
        income: data.month_income || 0,
        expense: data.month_expense || 0,
        balance: data.month_balance || 0
      }
    }
  } catch (error) {
    ElMessage.error('获取财务总览失败')
    console.error(error)
  }
}
</script>

<style scoped>
.finance-overview {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.stat-content {
  padding: 10px 0;
}

.stat-item {
  margin: 10px 0;
  font-size: 14px;
}

.stat-item .label {
  color: #909399;
}

.stat-item .amount {
  font-size: 18px;
  font-weight: bold;
}

.stat-item .amount.income {
  color: #67c23a;
}

.stat-item .amount.expense {
  color: #f56c6c;
}

.action-row {
  margin-top: 20px;
}
</style>
