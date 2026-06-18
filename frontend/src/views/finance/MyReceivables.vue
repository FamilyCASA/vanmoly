<template>
  <div class="my-receivables">
    <div class="page-header">
      <h2>我的收款</h2>
      <el-button type="primary" @click="openCreateDialog">+ 新建收款</el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="items" v-loading="loading" stripe empty-text="暂无收款记录">
        <el-table-column prop="receivable_no" label="编号" width="160" />
        <el-table-column label="客户" width="100">
          <template #default="{ row }">{{ row.customer_name || '—' }}</template>
        </el-table-column>
        <el-table-column prop="title" label="事由" min-width="160" show-overflow-tooltip />
        <el-table-column label="应收金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="已收" width="110" align="right">
          <template #default="{ row }">¥{{ formatNum(row.received_amount) }}</template>
        </el-table-column>
        <el-table-column label="待收" width="110" align="right">
          <template #default="{ row }">
            <span :class="{ 'warning-text': row.remaining_amount > 0 }">¥{{ formatNum(row.remaining_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="凭据" width="80" align="center">
          <template #default="{ row }">
            <el-button v-if="hasVouchers(row)" link type="primary" size="small" @click="viewVouchers(row)">查看</el-button>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-upload
              v-if="row.status !== 'received' && row.status !== 'cancelled'"
              :show-file-list="false"
              :before-upload="() => false"
              :on-change="(f) => uploadVoucher(row, f)"
              accept=".jpg,.jpeg,.png,.pdf"
            >
              <el-button link type="success" size="small">上传凭据</el-button>
            </el-upload>
            <el-button v-if="row.status === 'pending' || row.status === 'draft'" link type="primary" size="small" @click="submitForReview(row)">提交审核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建收款弹窗 -->
    <el-dialog v-model="createDialog" title="新建收款" width="600px" destroy-on-close>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="收款事由" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入收款事由" />
        </el-form-item>
        <el-form-item label="应收金额" prop="amount">
          <el-input-number v-model="createForm.amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="收款类型" prop="receivable_type">
          <el-select v-model="createForm.receivable_type" style="width: 100%">
            <el-option label="合同收款" value="contract" />
            <el-option label="分期收款" value="installment" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计收款日" prop="due_date">
          <el-date-picker v-model="createForm.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="客户">
          <el-select v-model="createForm.customer_id" filterable remote :remote-method="searchCustomers" placeholder="搜索客户" clearable style="width: 100%">
            <el-option v-for="c in customerOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="凭据附件">
          <el-upload
            v-model:file-list="createForm.voucherFiles"
            :auto-upload="false"
            :limit="5"
            accept=".jpg,.jpeg,.png,.pdf"
            list-type="text"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <template #tip>
              <div class="upload-tip">支持 JPG/PNG/PDF，最多5个</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">提交</el-button>
      </template>
    </el-dialog>

    <!-- 凭据查看弹窗 -->
    <el-dialog v-model="voucherDialog" title="凭据附件" width="500px">
      <div v-for="(v, i) in voucherList" :key="i" class="voucher-item">
        <el-icon><Document /></el-icon>
        <span>{{ v.name || v.path }}</span>
      </div>
      <div v-if="!voucherList.length" style="color: #999; text-align: center; padding: 20px;">暂无凭据</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

const loading = ref(false)
const items = ref([])
const createDialog = ref(false)
const submitting = ref(false)
const voucherDialog = ref(false)
const voucherList = ref([])
const customerOptions = ref([])
const createFormRef = ref(null)

const createForm = ref({
  title: '',
  amount: null,
  receivable_type: 'contract',
  due_date: '',
  customer_id: null,
  voucherFiles: []
})

const createRules = {
  title: [{ required: true, message: '请输入收款事由', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'change' }],
  receivable_type: [{ required: true, message: '请选择收款类型', trigger: 'change' }]
}

const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const statusType = (s) => ({ pending: 'warning', partial: 'primary', received: 'success', overdue: 'danger', cancelled: 'info', draft: 'info' })[s] || 'info'
const statusLabel = (s) => ({ pending: '待审核', partial: '部分收款', received: '已收齐', overdue: '已逾期', cancelled: '已取消', draft: '草稿' })[s] || s

const hasVouchers = (row) => {
  if (!row.remark) return false
  try {
    const parsed = JSON.parse(row.remark)
    return !!(parsed.vouchers?.length)
  } catch { return false }
}

const loadItems = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getMyReceivables()
    items.value = d.data || d || []
  } catch (e) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const searchCustomers = async (kw) => {
  if (!kw) return
  try {
    const d = await request({ url: '/customers/search', method: 'get', params: { keyword: kw } })
    customerOptions.value = d.data || d || []
  } catch (e) { /* ignore */ }
}

const openCreateDialog = () => {
  createForm.value = { title: '', amount: null, receivable_type: 'contract', due_date: '', customer_id: null, voucherFiles: [] }
  createDialog.value = true
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate()
  submitting.value = true
  try {
    const res = await financeAPI.createReceivable({
      title: createForm.value.title,
      amount: createForm.value.amount,
      receivable_type: createForm.value.receivable_type,
      due_date: createForm.value.due_date,
      customer_id: createForm.value.customer_id,
      status: 'pending'
    })
    
    const itemId = res.data?.id
    if (itemId && createForm.value.voucherFiles?.length) {
      for (const f of createForm.value.voucherFiles) {
        const fd = new FormData()
        fd.append('file', f.raw)
        try { await financeAPI.uploadReceivableVoucher(itemId, fd) } catch (e) { console.warn('凭据上传失败', e) }
      }
    }
    
    ElMessage.success('收款记录已提交，等待审核')
    createDialog.value = false
    loadItems()
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

const submitForReview = (row) => {
  ElMessageBox.confirm('确认提交审核？', '提示', { type: 'warning' }).then(async () => {
    try {
      await financeAPI.updateReceivable(row.id, { status: 'pending' })
      ElMessage.success('已提交审核')
      loadItems()
    } catch (e) { ElMessage.error('操作失败') }
  }).catch(() => {})
}

const uploadVoucher = async (row, file) => {
  const fd = new FormData()
  fd.append('file', file.raw)
  try {
    await financeAPI.uploadReceivableVoucher(row.id, fd)
    ElMessage.success('凭据已上传')
    loadItems()
  } catch (e) { ElMessage.error('上传失败') }
}

const viewVouchers = (row) => {
  try {
    const parsed = JSON.parse(row.remark)
    voucherList.value = parsed.vouchers || []
  } catch {
    voucherList.value = []
  }
  voucherDialog.value = true
}

onMounted(loadItems)
</script>

<style scoped>
.my-receivables { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 20px; }
.table-card :deep(.el-card__body) { padding: 0; }
:deep(.el-table__empty-block) { min-height: 200px; }
.warning-text { color: #E6A23C; font-weight: bold; }
.voucher-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #eee; }
.upload-tip { color: #999; font-size: 12px; }
</style>
