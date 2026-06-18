<template>
  <div class="finance-page">
    <!-- 页面内 Tab 导航 -->
    <div class="finance-tabs-wrap">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="财务总览" name="overview" />
        <el-tab-pane label="审批任务" name="approval-tasks" />
        <el-tab-pane label="应收管理" name="receivables" />
        <el-tab-pane label="应付管理" name="payables" />
        <el-tab-pane label="流水管理" name="transactions" />
      </el-tabs>
    </div>

    <!-- 子模块内容区 -->
    <div class="finance-content">
      <FinanceOverview v-if="activeTab === 'overview'" />
      <ApprovalTasks v-if="activeTab === 'approval-tasks'" />
      <ReceivableList v-if="activeTab === 'receivables'" />
      <PayableList v-if="activeTab === 'payables'" />
      <TransactionList v-if="activeTab === 'transactions'" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import FinanceOverview from './FinanceOverview.vue'
import ApprovalTasks from './ApprovalTasks.vue'
import ReceivableList from './ReceivableList.vue'
import PayableList from './PayableList.vue'
import TransactionList from './TransactionList.vue'

const route = useRoute()
const activeTab = ref(route.query.tab || 'overview')

watch(() => route.query.tab, (tab) => {
  if (tab) activeTab.value = tab
})

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
