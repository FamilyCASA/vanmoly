<template>
  <div class="finance-page">
    <!-- 页面内 Tab 导航 -->
    <div class="finance-tabs-wrap">
      <el-tabs v-model="activeTab">
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
import { Wallet } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

import FinanceOverview from './FinanceOverview.vue'
import TransactionList from './TransactionList.vue'
import ReimbursementList from './ReimbursementList.vue'
import MyReimbursements from './MyReimbursements.vue'
import ShareholderList from './ShareholderList.vue'
import AuditLogList from './AuditLogList.vue'
import FinanceAnalysis from './FinanceAnalysis.vue'
import MemberManage from './MemberManage.vue'

const activeTab = ref('overview')
const isFinanceAdmin = ref(false)

onMounted(async () => {
  try {
    const permData = await financeAPI.getMyPermissions()
    if (permData && permData.permissions) {
      isFinanceAdmin.value = permData.permissions.includes('settings')
    }
  } catch (error) {
    console.error('获取权限失败:', error)
  }
})
</script>

<style scoped>
.finance-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.finance-tabs-wrap {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  flex-shrink: 0;
}

.finance-tabs-wrap :deep(.el-tabs__header) {
  margin: 0;
}

.finance-tabs-wrap :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.finance-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f0f2f5;
}
</style>
