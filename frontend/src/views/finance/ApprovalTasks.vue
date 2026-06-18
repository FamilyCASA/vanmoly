<template>
  <div class="approval-tasks">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="待审批报销" name="reimbursements">
        <el-table :data="reimbList" v-loading="loadingReimb" stripe empty-text="暂无待审批报销">
          <el-table-column prop="reimb_no" label="编号" width="150" />
          <el-table-column label="申请人" width="100">
            <template #default="{ row }">{{ row.applicant_name || row.applicant_id }}</template>
          </el-table-column>
          <el-table-column label="金额" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column prop="summary" label="事由" min-width="200" show-overflow-tooltip />
          <el-table-column label="提交时间" width="110">
            <template #default="{ row }">{{ row.submit_at?.slice(0, 10) || row.created_at?.slice(0, 10) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleApprove(row)">确认</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="待确认收款" name="receivables">
        <el-table :data="receivList" v-loading="loadingReceiv" stripe empty-text="暂无待确认收款">
          <el-table-column prop="receivable_no" label="编号" width="150" />
          <el-table-column label="客户" width="100">
            <template #default="{ row }">{{ row.customer_name || '-' }}</template>
          </el-table-column>
          <el-table-column label="应收金额" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
          </el-table-column>
          <el-table-column label="已收" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.received_amount) }}</template>
          </el-table-column>
          <el-table-column label="待收" width="120" align="right">
            <template #default="{ row }" class="warning-text">¥{{ formatNum(row.remaining_amount) }}</template>
          </el-table-column>
          <el-table-column prop="title" label="事由" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleConfirmReceipt(row)">确认收款</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 收款确认弹窗 -->
    <el-dialog v-model="receiptDialog.visible" title="确认收款" width="500px">
      <el-form :model="receiptDialog.form" label-width="100px">
        <el-form-item label="应收金额">¥{{ formatNum(receiptDialog.item?.amount) }}</el-form-item>
        <el-form-item label="已收金额">¥{{ formatNum(receiptDialog.item?.received_amount) }}</el-form-item>
        <el-form-item label="本次收款">
          <el-input-number v-model="receiptDialog.form.received_amount" :min="0" :max="receiptDialog.item?.remaining_amount" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiptDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitConfirmReceipt">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

const activeTab = ref('reimbursements')
const reimbList = ref([])
const receivList = ref([])
const loadingReimb = ref(false)
const loadingReceiv = ref(false)

const receiptDialog = ref({
  visible: false,
  item: null,
  form: { received_amount: 0 }
})

const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

const loadPendingReimbursements = async () => {
  loadingReimb.value = true
  try {
    const d = await request({ url: '/finance/reimbursements', method: 'get', params: { status: 'submitted' } })
    reimbList.value = d.data || d.items || d || []
  } catch (e) { ElMessage.error('加载报销失败') }
  finally { loadingReimb.value = false }
}

const loadPendingReceivables = async () => {
  loadingReceiv.value = true
  try {
    const d = await financeAPI.getReceivables({ status: 'pending' })
    receivList.value = d.data || d.items || d || []
  } catch (e) { ElMessage.error('加载应收款失败') }
  finally { loadingReceiv.value = false }
}

const handleApprove = (row) => {
  ElMessageBox.confirm(`确认审批通过报销 ${row.reimb_no}，并自动登记支出流水？`, '审批确认', { type: 'warning' })
    .then(async () => {
      try {
        await financeAPI.approveReimbursementWithTransaction(row.id, {})
        ElMessage.success('审批完成，已自动登记流水')
        loadPendingReimbursements()
      } catch (e) { ElMessage.error('操作失败') }
    }).catch(() => {})
}

const handleConfirmReceipt = (row) => {
  receiptDialog.value = {
    visible: true,
    item: row,
    form: { received_amount: row.remaining_amount }
  }
}

const submitConfirmReceipt = async () => {
  const { item, form } = receiptDialog.value
  if (!form.received_amount || form.received_amount <= 0) {
    ElMessage.warning('请输入收款金额')
    return
  }
  try {
    await financeAPI.confirmReceipt(item.id, { received_amount: form.received_amount })
    ElMessage.success('收款确认成功，已自动登记收入流水')
    receiptDialog.value.visible = false
    loadPendingReceivables()
  } catch (e) { ElMessage.error('操作失败') }
}

onMounted(() => {
  loadPendingReimbursements()
  loadPendingReceivables()
})
</script>

<style scoped>
.approval-tasks { padding: 20px; }
.warning-text { color: #E6A23C; font-weight: bold; }
</style>
