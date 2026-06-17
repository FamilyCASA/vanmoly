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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import financeAPI from '@/api/finance'

import FinanceOverview from './FinanceOverview.vue'
import TransactionList from './TransactionList.vue'
import ReimbursementList from './ReimbursementList.vue'
import MyReimbursements from './MyReimbursements.vue'
import ShareholderList from './ShareholderList.vue'
import AuditLogList from './AuditLogList.vue'

const activeTab = ref('overview')

onMounted(async () => {
  // 可以在这里添加权限检查或其他初始化逻辑
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
