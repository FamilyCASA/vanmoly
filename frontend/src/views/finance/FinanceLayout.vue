<template>
  <div class="finance-container">
    <!-- 页面头部 Tab 导航 -->
    <div class="finance-header">
      <div class="finance-title">
        <el-icon><Wallet /></el-icon>
        <span>财务管理</span>
      </div>
      <el-tabs v-model="activeTab" class="finance-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="财务总览" name="overview" />
        <el-tab-pane label="流水管理" name="transactions" />
        <el-tab-pane label="报销管理" name="reimbursements" />
        <el-tab-pane label="我的报销" name="my-reimbursements" />
        <el-tab-pane label="投资管理" name="shareholders" />
        <el-tab-pane label="操作日志" name="audit-logs" />
        <el-tab-pane label="财务分析" name="analysis" />
        <el-tab-pane v-if="isFinanceAdmin" label="团队管理" name="members" />
      </el-tabs>
    </div>

    <!-- 子模块内容区 -->
    <div class="finance-content">
      <FinanceOverview v-if="activeTab === 'overview'" />
      <TransactionList v-if="activeTab === 'transactions'" />
      <ReimbursementList v-if="activeTab === 'reimbursements'" />
      <MyReimbursements v-if="activeTab === 'my-reimbursements'" />
      <ShareholderList v-if="activeTab === 'shareholders'" />
      <AuditLogList v-if="activeTab === 'audit-logs'" />
      <FinanceAnalysis v-if="activeTab === 'analysis'" />
      <MemberManage v-if="activeTab === 'members' && isFinanceAdmin" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Wallet } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

// 子模块组件
import FinanceOverview from './FinanceOverview.vue'
import TransactionList from './TransactionList.vue'
import ReimbursementList from './ReimbursementList.vue'
import MyReimbursements from './MyReimbursements.vue'
import ShareholderList from './ShareholderList.vue'
import AuditLogList from './AuditLogList.vue'
import FinanceAnalysis from './FinanceAnalysis.vue'
import MemberManage from './MemberManage.vue'

const router = useRouter()
const route = useRoute()

const activeTab = ref('overview')
const isFinanceAdmin = ref(false)

onMounted(async () => {
  // 解析当前路由确定默认 Tab
  const path = route.path
  if (path.includes('transactions')) activeTab.value = 'transactions'
  else if (path.includes('reimbursements/my')) activeTab.value = 'my-reimbursements'
  else if (path.includes('reimbursements')) activeTab.value = 'reimbursements'
  else if (path.includes('shareholders') || path.includes('charter')) activeTab.value = 'shareholders'
  else if (path.includes('audit-logs')) activeTab.value = 'audit-logs'
  else if (path.includes('analysis')) activeTab.value = 'analysis'
  else if (path.includes('members')) activeTab.value = 'members'
  else activeTab.value = 'overview'

  // 获取财务管理员权限
  try {
    const permData = await financeAPI.getMyPermissions()
    if (permData && permData.permissions) {
      isFinanceAdmin.value = permData.permissions.includes('settings')
    }
  } catch (error) {
    console.error('获取权限失败:', error)
  }
})

const handleTabChange = (tabName) => {
  const pathMap = {
    overview: '/finance/overview',
    transactions: '/finance/transactions',
    reimbursements: '/finance/reimbursements',
    'my-reimbursements': '/finance/my-reimbursements',
    shareholders: '/finance/shareholders',
    'audit-logs': '/finance/audit-logs',
    analysis: '/finance/analysis',
    members: '/finance/members'
  }
  router.push(pathMap[tabName] || '/finance/overview')
}
</script>

<style scoped>
.finance-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f0f2f5;
  overflow: hidden;
}

.finance-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-shrink: 0;
}

.finance-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  padding-right: 16px;
  border-right: 1px solid #e4e7ed;
  height: 56px;
}

.finance-tabs {
  flex: 1;
}

.finance-tabs :deep(.el-tabs__header) {
  margin: 0;
}

.finance-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.finance-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
</style>
