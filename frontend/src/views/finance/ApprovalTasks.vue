<template>
  <div class="approval-tasks">
    <div class="approval-header">
      <div>
        <h3>我的审核</h3>
        <p>统一处理报销、收付款、报价和服务流程节点资料验收</p>
      </div>
      <el-button @click="loadAll">刷新</el-button>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane :label="`待审批报销 ${reimbList.length}`" name="reimbursements">
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
              <el-button type="primary" size="small" @click="handleApproveReimb(row)">确认</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="`待确认收款 ${receivList.length}`" name="receivables">
        <el-table :data="receivList" v-loading="loadingReceiv" stripe empty-text="暂无待确认收款">
          <el-table-column prop="receivable_no" label="编号" width="150" />
          <el-table-column label="客户" width="120">
            <template #default="{ row }">{{ row.customer_name || '-' }}</template>
          </el-table-column>
          <el-table-column label="应收金额" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
          </el-table-column>
          <el-table-column label="待收" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.remaining_amount) }}</template>
          </el-table-column>
          <el-table-column prop="title" label="事由" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleConfirmReceipt(row)">确认收款</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="`待确认付款 ${payableList.length}`" name="payables">
        <el-table :data="payableList" v-loading="loadingPayable" stripe empty-text="暂无待确认付款">
          <el-table-column prop="payable_no" label="编号" width="150" />
          <el-table-column prop="supplier_name" label="收款方" width="140" show-overflow-tooltip />
          <el-table-column label="应付金额" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
          </el-table-column>
          <el-table-column label="待付" width="120" align="right">
            <template #default="{ row }">¥{{ formatNum(row.remaining_amount) }}</template>
          </el-table-column>
          <el-table-column prop="title" label="付款事由" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleConfirmPayment(row)">确认付款</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="`报价审核 ${quoteList.length}`" name="quotes">
        <el-table :data="quoteList" v-loading="loadingQuote" stripe empty-text="暂无待审核报价">
          <el-table-column prop="quote_no" label="报价编号" width="160" />
          <el-table-column prop="customer_name" label="客户" width="140" show-overflow-tooltip />
          <el-table-column label="报价金额" width="130" align="right">
            <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column label="创建时间" width="120">
            <template #default="{ row }">{{ row.created_at?.slice(0, 10) || '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="210" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="router.push(`/admin/quotes/${row.id}`)">查看</el-button>
              <el-button link type="success" @click="approveQuote(row)">通过</el-button>
              <el-button link type="danger" @click="rejectQuote(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="`节点资料验收 ${workflowRecordList.length}`" name="workflow">
        <el-table :data="workflowRecordList" v-loading="loadingWorkflow" stripe empty-text="暂无待验收节点资料">
          <el-table-column prop="node_code" label="节点" width="90" />
          <el-table-column prop="node_name" label="节点名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="executor_name" label="提交人" width="110" />
          <el-table-column prop="content" label="汇报内容" min-width="220" show-overflow-tooltip />
          <el-table-column label="附件" width="90" align="center">
            <template #default="{ row }">{{ row.attachments?.length || 0 }}</template>
          </el-table-column>
          <el-table-column label="提交时间" width="120">
            <template #default="{ row }">{{ row.updated_at?.slice(0, 10) || row.created_at?.slice(0, 10) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="success" @click="approveWorkflowRecord(row)">通过</el-button>
              <el-button link type="danger" @click="rejectWorkflowRecord(row)">重做</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

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

    <el-dialog v-model="paymentDialog.visible" title="确认付款" width="500px">
      <el-form :model="paymentDialog.form" label-width="100px">
        <el-form-item label="应付金额">¥{{ formatNum(paymentDialog.item?.amount) }}</el-form-item>
        <el-form-item label="已付金额">¥{{ formatNum(paymentDialog.item?.paid_amount) }}</el-form-item>
        <el-form-item label="本次付款">
          <el-input-number v-model="paymentDialog.form.paid_amount" :min="0" :max="paymentDialog.item?.remaining_amount" :precision="2" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-input v-model="paymentDialog.form.payment_method" placeholder="如：银行转账、微信、现金" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paymentDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitConfirmPayment">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

const router = useRouter()
const activeTab = ref('reimbursements')
const reimbList = ref([])
const receivList = ref([])
const payableList = ref([])
const quoteList = ref([])
const workflowRecordList = ref([])
const loadingReimb = ref(false)
const loadingReceiv = ref(false)
const loadingPayable = ref(false)
const loadingQuote = ref(false)
const loadingWorkflow = ref(false)

const receiptDialog = ref({
  visible: false,
  item: null,
  form: { received_amount: 0 }
})

const paymentDialog = ref({
  visible: false,
  item: null,
  form: { paid_amount: 0, payment_method: '' }
})

const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

const normalizeItems = (d) => d?.items || d?.data || d || []

const loadPendingReimbursements = async () => {
  loadingReimb.value = true
  try {
    const d = await request({ url: '/finance/reimbursements', method: 'get', params: { status: 'submitted' } })
    reimbList.value = normalizeItems(d)
  } catch (e) { ElMessage.error('加载报销失败') }
  finally { loadingReimb.value = false }
}

const loadPendingReceivables = async () => {
  loadingReceiv.value = true
  try {
    const d = await financeAPI.getReceivables({ status: 'pending', page_size: 100 })
    receivList.value = normalizeItems(d)
  } catch (e) { ElMessage.error('加载应收款失败') }
  finally { loadingReceiv.value = false }
}

const loadPendingPayables = async () => {
  loadingPayable.value = true
  try {
    const d = await financeAPI.getPayables({ status: 'pending', page_size: 100 })
    payableList.value = normalizeItems(d)
  } catch (e) { ElMessage.error('加载应付款失败') }
  finally { loadingPayable.value = false }
}

const loadPendingQuotes = async () => {
  loadingQuote.value = true
  try {
    const d = await request.get('/quotes', { params: { status: 'pending', page_size: 100 } })
    quoteList.value = normalizeItems(d)
  } catch (e) { ElMessage.error('加载报价审核失败') }
  finally { loadingQuote.value = false }
}

const loadWorkflowReviews = async () => {
  loadingWorkflow.value = true
  try {
    const d = await request.get('/workflows/review-records', { params: { status: 'submitted' } })
    workflowRecordList.value = normalizeItems(d)
  } catch (e) { ElMessage.error('加载节点验收失败') }
  finally { loadingWorkflow.value = false }
}

const loadAll = () => {
  loadPendingReimbursements()
  loadPendingReceivables()
  loadPendingPayables()
  loadPendingQuotes()
  loadWorkflowReviews()
}

const handleApproveReimb = (row) => {
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

const handleConfirmPayment = (row) => {
  paymentDialog.value = {
    visible: true,
    item: row,
    form: { paid_amount: row.remaining_amount, payment_method: '' }
  }
}

const submitConfirmPayment = async () => {
  const { item, form } = paymentDialog.value
  if (!form.paid_amount || form.paid_amount <= 0) {
    ElMessage.warning('请输入付款金额')
    return
  }
  try {
    await financeAPI.confirmPayment(item.id, form)
    ElMessage.success('付款确认成功，已自动登记支出流水')
    paymentDialog.value.visible = false
    loadPendingPayables()
  } catch (e) { ElMessage.error('操作失败') }
}

const approveQuote = async (row) => {
  try {
    await ElMessageBox.confirm(`确认通过报价 ${row.quote_no || row.id}？`, '报价审核', { type: 'warning' })
    await request.post(`/quotes/${row.id}/approve`, {})
    ElMessage.success('报价审核通过')
    loadPendingQuotes()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('报价审核失败')
  }
}

const rejectQuote = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回报价', {
      confirmButtonText: '驳回',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请填写驳回原因'
    })
    await request.post(`/quotes/${row.id}/reject`, { reason: value })
    ElMessage.success('报价已驳回')
    loadPendingQuotes()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('驳回失败')
  }
}

const approveWorkflowRecord = async (row) => {
  try {
    await ElMessageBox.confirm(`确认验收通过节点「${row.node_name}」？`, '节点资料验收', { type: 'warning' })
    await request.post(`/workflows/records/${row.id}/approve`, {})
    ElMessage.success('节点资料验收通过')
    loadWorkflowReviews()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('验收失败')
  }
}

const rejectWorkflowRecord = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入重做原因', '退回节点资料', {
      confirmButtonText: '退回重做',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请填写重做原因'
    })
    await request.post(`/workflows/records/${row.id}/reject`, { reason: value })
    ElMessage.success('已退回重做')
    loadWorkflowReviews()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('退回失败')
  }
}

onMounted(loadAll)
</script>

<style scoped>
.approval-tasks {
  padding: 20px;
}

.approval-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.approval-header h3 {
  margin: 0 0 6px;
  color: #1f2937;
}

.approval-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}
</style>
