<template>
  <div class="my-reimbursements">
    <div class="page-header">
      <h2>我的报销</h2>
      <el-button type="primary" @click="openCreateDialog">+ 新建报销</el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="items" v-loading="loading" stripe empty-text="暂无报销记录">
        <el-table-column prop="reimb_no" label="编号" width="160" />
        <el-table-column prop="created_at" label="申请时间" width="100">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="110" />
        <el-table-column prop="summary" label="事由" min-width="160" show-overflow-tooltip />
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="凭据" width="80" align="center">
          <template #default="{ row }">
            <el-button v-if="row.payment_voucher" link type="primary" size="small" @click="viewVouchers(row)">查看</el-button>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="审核备注" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.review_note || '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" link type="primary" size="small" @click="submitReimb(row)">提交审核</el-button>
            <el-upload
              v-if="row.status === 'submitted' || row.status === 'draft'"
              :show-file-list="false"
              :before-upload="() => false"
              :on-change="(f) => uploadVoucher(row, f)"
              accept=".jpg,.jpeg,.png,.pdf"
            >
              <el-button link type="success" size="small">上传凭据</el-button>
            </el-upload>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建报销弹窗 -->
    <el-dialog v-model="createDialog" title="新建报销" width="600px" destroy-on-close>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="报销事由" prop="summary">
          <el-input v-model="createForm.summary" placeholder="请输入报销事由" />
        </el-form-item>
        <el-form-item label="报销金额" prop="total_amount">
          <el-input-number v-model="createForm.total_amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="费用日期" prop="expense_date">
          <el-date-picker v-model="createForm.expense_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="报销分类" prop="category_id">
          <el-select v-model="createForm.category_id" placeholder="选择分类" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
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
        <el-button type="primary" :loading="submitting" @click="handleCreate">提交报销</el-button>
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

const loading = ref(false)
const items = ref([])
const categories = ref([])
const createDialog = ref(false)
const submitting = ref(false)
const voucherDialog = ref(false)
const voucherList = ref([])
const createFormRef = ref(null)

const createForm = ref({
  summary: '',
  total_amount: null,
  expense_date: '',
  category_id: null,
  voucherFiles: []
})

const createRules = {
  summary: [{ required: true, message: '请输入报销事由', trigger: 'blur' }],
  total_amount: [{ required: true, message: '请输入金额', trigger: 'change' }],
  expense_date: [{ required: true, message: '请选择费用日期', trigger: 'change' }]
}

const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const statusType = (s) => ({ draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger', paid: 'primary', cancelled: 'info' })[s] || 'info'
const statusLabel = (s) => ({ draft: '草稿', submitted: '待审核', approved: '已通过', rejected: '已驳回', paid: '已付款', cancelled: '已取消' })[s] || s

const loadItems = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getMyReimbursements()
    items.value = d.data || d || []
  } catch (e) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const loadCategories = async () => {
  try {
    const d = await financeAPI.getCategories()
    categories.value = d.data || d || []
  } catch (e) { /* ignore */ }
}

const openCreateDialog = () => {
  createForm.value = { summary: '', total_amount: null, expense_date: '', category_id: null, voucherFiles: [] }
  createDialog.value = true
  if (!categories.value.length) loadCategories()
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate()
  submitting.value = true
  try {
    const res = await financeAPI.createReimbursement({
      summary: createForm.value.summary,
      total_amount: createForm.value.total_amount,
      expense_date: createForm.value.expense_date,
      category_id: createForm.value.category_id,
      status: 'submitted'
    })
    
    // Upload vouchers if any
    const reimbId = res.data?.id
    if (reimbId && createForm.value.voucherFiles?.length) {
      for (const f of createForm.value.voucherFiles) {
        const fd = new FormData()
        fd.append('file', f.raw)
        try { await financeAPI.uploadReimbVoucher(reimbId, fd) } catch (e) { console.warn('凭据上传失败', e) }
      }
    }
    
    ElMessage.success('报销已提交，等待审核')
    createDialog.value = false
    loadItems()
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

const submitReimb = (row) => {
  ElMessageBox.confirm('确认提交审核？', '提示', { type: 'warning' }).then(async () => {
    try {
      await financeAPI.reviewReimbursement(row.id, { status: 'submitted' })
      ElMessage.success('已提交审核')
      loadItems()
    } catch (e) { ElMessage.error('操作失败') }
  }).catch(() => {})
}

const uploadVoucher = async (row, file) => {
  const fd = new FormData()
  fd.append('file', file.raw)
  try {
    await financeAPI.uploadReimbVoucher(row.id, fd)
    ElMessage.success('凭据已上传')
    loadItems()
  } catch (e) { ElMessage.error('上传失败') }
}

const viewVouchers = (row) => {
  try {
    const parsed = JSON.parse(row.payment_voucher)
    voucherList.value = Array.isArray(parsed) ? parsed : [parsed]
  } catch {
    voucherList.value = row.payment_voucher ? [{ name: row.payment_voucher, path: row.payment_voucher }] : []
  }
  voucherDialog.value = true
}

onMounted(loadItems)
</script>

<style scoped>
.my-reimbursements { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 20px; }
.table-card :deep(.el-card__body) { padding: 0; }
:deep(.el-table__empty-block) { min-height: 200px; }
.voucher-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #eee; }
.upload-tip { color: #999; font-size: 12px; }
</style>
