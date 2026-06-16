<template>
  <div class="my-reimbursements">
    <div class="page-header">
      <h2>我的报销</h2>
      <el-button type="primary" @click="$router.push('/finance/reimbursements')" size="small">
        返回报销管理
      </el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="items" v-loading="loading" stripe empty-text="暂无报销记录">
        <el-table-column prop="reimb_no" label="编号" width="160" />
        <el-table-column prop="created_at" label="申请时间" width="100">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="110" />
        <el-table-column prop="summary" label="事由" min-width="200" show-overflow-tooltip />
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核备注" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.review_note || '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import financeAPI from '@/api/finance'

const loading = ref(false)
const items = ref([])

const formatNum = (v) => {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
const statusType = (s) => {
  const map = { draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger', paid: 'primary', cancelled: 'info' }
  return map[s] || 'info'
}
const statusLabel = (s) => {
  const map = { draft: '草稿', submitted: '待审核', approved: '已通过', rejected: '已驳回', paid: '已付款', cancelled: '已取消' }
  return map[s] || s
}

onMounted(async () => {
  loading.value = true
  try {
    const d = await financeAPI.getMyReimbursements()
    items.value = d || []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.my-reimbursements { padding: 0; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; font-size: 20px; }
.table-card :deep(.el-card__body) { padding: 0; }
:deep(.el-table__empty-block) { min-height: 200px; }
</style>
