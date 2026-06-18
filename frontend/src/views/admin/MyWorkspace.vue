<template>
  <div class="my-workspace">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>我的工作台</h2>
      <el-button text @click="$router.push('/admin/dashboard')">
        <el-icon><ArrowLeft /></el-icon> 返回管理后台
      </el-button>
    </div>

    <!-- Tab 导航 -->
    <div class="workspace-tabs-wrap">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="我的报销" name="reimbursements">
          <template #label>
            <span><el-icon><Document /></el-icon> 我的报销</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="我的收款" name="receivables">
          <template #label>
            <span><el-icon><Money /></el-icon> 我的收款</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="我的付款" name="payables">
          <template #label>
            <span><el-icon><Wallet /></el-icon> 我的付款</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 内容区 -->
    <div class="workspace-content">
      <!-- 我的报销 -->
      <div v-if="activeTab === 'reimbursements'" class="tab-content">
        <div class="content-header">
          <el-button type="primary" @click="openReimbDialog">+ 新建报销</el-button>
        </div>
        <el-card shadow="never" class="table-card">
          <el-table :data="reimbItems" v-loading="reimbLoading" stripe empty-text="暂无报销记录">
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
                <el-button v-if="row.payment_voucher" link type="primary" size="small" @click="viewVouchers(row, 'reimbursement')">查看</el-button>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column label="审核备注" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ row.review_note || '—' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'draft'" link type="primary" size="small" @click="submitReimb(row)">提交审核</el-button>
                <el-upload
                  v-if="row.status === 'submitted' || row.status === 'draft'"
                  :show-file-list="false"
                  :before-upload="() => false"
                  :on-change="(f) => uploadVoucher(row, f, 'reimbursement')"
                  accept=".jpg,.jpeg,.png,.pdf"
                >
                  <el-button link type="success" size="small">上传凭据</el-button>
                </el-upload>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 我的收款 -->
      <div v-if="activeTab === 'receivables'" class="tab-content">
        <div class="content-header">
          <el-button type="primary" @click="openRecvDialog">+ 新建收款登记</el-button>
        </div>
        <el-card shadow="never" class="table-card">
          <el-table :data="recvItems" v-loading="recvLoading" stripe empty-text="暂无收款记录">
            <el-table-column prop="receivable_no" label="编号" width="170" />
            <el-table-column prop="created_at" label="创建时间" width="100">
              <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
            </el-table-column>
            <el-table-column prop="customer_name" label="客户" width="120" show-overflow-tooltip />
            <el-table-column prop="title" label="款项说明" min-width="160" show-overflow-tooltip />
            <el-table-column label="应收金额" width="120" align="right">
              <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="已收金额" width="120" align="right">
              <template #default="{ row }">¥{{ formatNum(row.received_amount) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="recvStatusType(row.status)" size="small" effect="plain">{{ recvStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'draft'" link type="primary" size="small" @click="submitRecv(row)">提交审核</el-button>
                <el-upload
                  v-if="row.status === 'submitted' || row.status === 'draft'"
                  :show-file-list="false"
                  :before-upload="() => false"
                  :on-change="(f) => uploadVoucher(row, f, 'receivable')"
                  accept=".jpg,.jpeg,.png,.pdf"
                >
                  <el-button link type="success" size="small">上传凭据</el-button>
                </el-upload>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 我的付款 -->
      <div v-if="activeTab === 'payables'" class="tab-content">
        <div class="content-header">
          <el-button type="primary" @click="openPayDialog">+ 新建付款登记</el-button>
        </div>
        <el-card shadow="never" class="table-card">
          <el-table :data="payItems" v-loading="payLoading" stripe empty-text="暂无付款记录">
            <el-table-column prop="payable_no" label="编号" width="170" />
            <el-table-column prop="created_at" label="创建时间" width="100">
              <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
            </el-table-column>
            <el-table-column prop="supplier_name" label="供应商/对方" width="130" show-overflow-tooltip />
            <el-table-column prop="title" label="款项说明" min-width="160" show-overflow-tooltip />
            <el-table-column label="应付金额" width="120" align="right">
              <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain">{{ payTypeLabel(row.payable_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="payStatusType(row.status)" size="small" effect="plain">{{ payStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 'draft'" link type="primary" size="small" @click="submitPay(row)">提交审核</el-button>
                <el-upload
                  v-if="row.status === 'submitted' || row.status === 'draft'"
                  :show-file-list="false"
                  :before-upload="() => false"
                  :on-change="(f) => uploadVoucher(row, f, 'payable')"
                  accept=".jpg,.jpeg,.png,.pdf"
                >
                  <el-button link type="success" size="small">上传上传凭据</el-button>
                </el-upload>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- 新建报销弹窗 -->
    <el-dialog v-model="reimbDialog" title="新建报销" width="600px" destroy-on-close>
      <el-form :model="reimbForm" :rules="reimbRules" ref="reimbFormRef" label-width="100px">
        <el-form-item label="报销事由" prop="summary">
          <el-input v-model="reimbForm.summary" placeholder="请输入报销事由" />
        </el-form-item>
        <el-form-item label="报销金额" prop="total_amount">
          <el-input-number v-model="reimbForm.total_amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="费用日期" prop="expense_date">
          <el-date-picker v-model="reimbForm.expense_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="报销分类" prop="category_id">
          <el-select v-model="reimbForm.category_id" placeholder="选择分类" clearable style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="凭据附件">
          <el-upload
            v-model:file-list="reimbForm.voucherFiles"
            :auto-upload="false"
            :limit="5"
            accept=".jpg,.jpeg,.png,.pdf"
            list-type="text"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <template #tip><div class="upload-tip">支持 JPG/PNG/PDF，最多5个</div></template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reimbDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateReimb">提交报销</el-button>
      </template>
    </el-dialog>

    <!-- 新建收款弹窗 -->
    <el-dialog v-model="recvDialog" title="新建收款登记" width="600px" destroy-on-close>
      <el-form :model="recvForm" :rules="recvRules" ref="recvFormRef" label-width="100px">
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="recvForm.customer_name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="款项说明" prop="title">
          <el-input v-model="recvForm.title" placeholder="如：全案设计服务费-张先生" />
        </el-form-item>
        <el-form-item label="应收金额" prop="amount">
          <el-input-number v-model="recvForm.amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="到期日期" prop="due_date">
          <el-date-picker v-model="recvForm.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="recvForm.remark" type="textarea" :rows="3" placeholder="可选填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recvDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateRecv">提交登记</el-button>
      </template>
    </el-dialog>

    <!-- 新建付款弹窗 -->
    <el-dialog v-model="payDialog" title="新建付款登记" width="600px" destroy-on-close>
      <el-form :model="payForm" :rules="payRules" ref="payFormRef" label-width="110px">
        <el-form-item label="供应商/对方" prop="supplier_name">
          <el-input v-model="payForm.supplier_name" placeholder="请输入供应商或对方名称" />
        </el-form-item>
        <el-form-item label="款项说明" prop="title">
          <el-input v-model="payForm.title" placeholder="如：主材采购-瓷砖（含运费）" />
        </el-form-item>
        <el-form-item label="应付金额" prop="amount">
          <el-input-number v-model="payForm.amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="付款类型" prop="payable_type">
          <el-select v-model="payForm.payable_type" placeholder="选择类型" style="width: 100%">
            <el-option label="采购付款" value="purchase" />
            <el-option label="分期付款" value="installment" />
            <el-option label="其他付款" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期日期" prop="due_date">
          <el-date-picker v-model="payForm.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="payForm.remark" type="textarea" :rows="3" placeholder="可选填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreatePay">提交登记</el-button>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Money, Wallet, ArrowLeft } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

const route = useRoute()
const router = useRouter()

// Tab 状态
const activeTab = ref(route.query.tab || 'reimbursements')

// 报销数据
const reimbItems = ref([])
const reimbLoading = ref(false)
const reimbDialog = ref(false)
const reimbFormRef = ref(null)
const categories = ref([])

// 收款数据
const recvItems = ref([])
const recvLoading = ref(false)
const recvDialog = ref(false)
const recvFormRef = ref(null)

// 付款数据
const payItems = ref([])
const payLoading = ref(false)
const payDialog = ref(false)
const payFormRef = ref(null)

// 公共
const submitting = ref(false)
const voucherDialog = ref(false)
const voucherList = ref([])

// 表单
const reimbForm = ref({
  summary: '', total_amount: null, expense_date: '', category_id: null, voucherFiles: []
})
const reimbRules = {
  summary: [{ required: true, message: '请输入报销事由', trigger: 'blur' }],
  total_amount: [{ required: true, message: '请输入金额', trigger: 'change' }],
  expense_date: [{ required: true, message: '请选择费用日期', trigger: 'change' }]
}

const recvForm = ref({
  customer_name: '', title: '', amount: null, due_date: '', remark: ''
})
const recvRules = {
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  title: [{ required: true, message: '请输入款项说明', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'change' }]
}

const payForm = ref({
  supplier_name: '', title: '', amount: null, payable_type: 'purchase', due_date: '', remark: ''
})
const payRules = {
  supplier_name: [{ required: true, message: '请输入供应商/对方', trigger: 'blur' }],
  title: [{ required: true, message: '请输入款项说明', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'change' }]
}

// 工具函数
const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const statusType = (s) => ({ draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger', paid: 'primary', cancelled: 'info' })[s] || 'info'
const statusLabel = (s) => ({ draft: '草稿', submitted: '待审核', approved: '已通过', rejected: '已驳回', paid: '已付款', cancelled: '已取消' })[s] || s
const recvStatusType = (s) => ({ draft: 'info', submitted: 'warning', received: 'success', partial: 'warning', cancelled: 'info' })[s] || 'info'
const recvStatusLabel = (s) => ({ draft: '草稿', submitted: '待确认', received: '已收齐', partial: '部分收款', cancelled: '已取消' })[s] || s
const payStatusType = (s) => ({ draft: 'info', submitted: 'warning', approved: 'success', paid: 'primary', cancelled: 'info' })[s] || 'info'
const payStatusLabel = (s) => ({ draft: '草稿', submitted: '待审批', approved: '已批准', paid: '已付款', cancelled: '已取消' })[s] || s
const payTypeLabel = (t) => ({ purchase: '采购付款', installment: '分期付款', other: '其他付款' })[t] || t

// Tab 切换同步 URL
const onTabChange = (tab) => {
  router.replace({ query: { tab } })
}

// ====== 报销 ======
const loadReimb = async () => {
  reimbLoading.value = true
  try {
    const d = await financeAPI.getMyReimbursements()
    reimbItems.value = d.data || d || []
  } catch (e) { ElMessage.error('加载失败') }
  finally { reimbLoading.value = false }
}
const loadCategories = async () => {
  try {
    const d = await financeAPI.getCategories()
    categories.value = d.data || d || []
  } catch (e) { /* ignore */ }
}
const openReimbDialog = () => {
  reimbForm.value = { summary: '', total_amount: null, expense_date: '', category_id: null, voucherFiles: [] }
  if (!categories.value.length) loadCategories()
  reimbDialog.value = true
}
const handleCreateReimb = async () => {
  await reimbFormRef.value.validate()
  submitting.value = true
  try {
    const res = await financeAPI.createReimbursement({ ...reimbForm.value, status: 'submitted' })
    const id = res.data?.id
    if (id && reimbForm.value.voucherFiles?.length) {
      for (const f of reimbForm.value.voucherFiles) {
        const fd = new FormData(); fd.append('file', f.raw)
        try { await financeAPI.uploadReimbVoucher(id, fd) } catch (e) { console.warn('凭据上传失败', e) }
      }
    }
    ElMessage.success('报销已提交，等待审核')
    reimbDialog.value = false; loadReimb()
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}
const submitReimb = (row) => {
  ElMessageBox.confirm('确认提交审核？', '提示', { type: 'warning' }).then(async () => {
    try { await financeAPI.reviewReimbursement(row.id, { status: 'submitted' }); ElMessage.success('已提交'); loadReimb() }
    catch (e) { ElMessage.error('操作失败') }
  }).catch(() => {})
}

// ====== 收款 ======
const loadRecv = async () => {
  recvLoading.value = true
  try {
    const d = await financeAPI.getMyReceivables()
    recvItems.value = d.data || d || []
  } catch (e) { ElMessage.error('加载失败') }
  finally { recvLoading.value = false }
}
const openRecvDialog = () => { recvForm.value = { customer_name: '', title: '', amount: null, due_date: '', remark: '' }; recvDialog.value = true }
const handleCreateRecv = async () => {
  await recvFormRef.value.validate()
  submitting.value = true
  try {
    const res = await financeAPI.createReceivable({ ...recvForm.value, status: 'submitted' })
    ElMessage.success('收款登记已提交')
    recvDialog.value = false; loadRecv()
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}
const submitRecv = (row) => {
  ElMessageBox.confirm('确认提交审核？', '提示', { type: 'warning' }).then(async () => {
    try { await financeAPI.updateReceivable(row.id, { status: 'submitted' }); ElMessage.success('已提交'); loadRecv() }
    catch (e) { ElMessage.error('操作失败') }
  }).catch(() => {})
}

// ====== 付款 ======
const loadPay = async () => {
  payLoading.value = true
  try {
    const d = await financeAPI.getMyPayables()
    payItems.value = d.data || d || []
  } catch (e) { ElMessage.error('加载失败') }
  finally { payLoading.value = false }
}
const openPayDialog = () => { payForm.value = { supplier_name: '', title: '', amount: null, payable_type: 'purchase', due_date: '', remark: '' }; payDialog.value = true }
const handleCreatePay = async () => {
  await payFormRef.value.validate()
  submitting.value = true
  try {
    const res = await financeAPI.createPayable({ ...payForm.value, status: 'submitted' })
    ElMessage.success('付款登记已提交')
    payDialog.value = false; loadPay()
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}
const submitPay = (row) => {
  ElMessageBox.confirm('确认提交审核？', '提示', { type: 'warning' }).then(async () => {
    try { await financeAPI.updatePayable(row.id, { status: 'submitted' }); ElMessage.success('已提交'); loadPay() }
    catch (e) { ElMessage.error('操作失败') }
  }).catch(() => {})
}

// ====== 凭据 ======
const uploadVoucher = async (row, file, type) => {
  const fd = new FormData(); fd.append('file', file.raw)
  try {
    if (type === 'reimbursement') { await financeAPI.uploadReimbVoucher(row.id, fd) }
    else if (type === 'receivable') { await financeAPI.uploadReceivableVoucher(row.id, fd) }
    else if (type === 'payable') { await financeAPI.uploadPayableVoucher(row.id, fd) }
    ElMessage.success('凭据已上传')
    // 刷新对应列表
    if (type === 'reimbursement') loadReimb()
    else if (type === 'receivable') loadRecv()
    else loadPay()
  } catch (e) { ElMessage.error('上传失败') }
}
const viewVouchers = (row, type) => {
  const field = type === 'reimbursement' ? 'payment_voucher' : 'voucher_files'
  try {
    const parsed = JSON.parse(row[field])
    voucherList.value = Array.isArray(parsed) ? parsed : [parsed]
  } catch {
    voucherList.value = row[field] ? [{ name: row[field], path: row[field] }] : []
  }
  voucherDialog.value = true
}

// 监听路由 tab 变化
import { watch } from 'vue'
watch(() => route.query.tab, (tab) => { if (tab) activeTab.value = tab })

onMounted(() => {
  loadReimb(); loadRecv(); loadPay()
})
</script>

<style scoped>
.my-workspace { display: flex; flex-direction: column; height: 100%; background: #f0f2f5; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; background: #fff; border-bottom: 1px solid #e4e7ed;
}
.page-header h2 { margin: 0; font-size: 20px; color: #303133; }

.workspace-tabs-wrap {
  background: #fff; padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
}
.workspace-tabs-wrap :deep(.el-tabs__header) { margin: 0; }
.workspace-tabs-wrap :deep(.el-tabs__nav-wrap::after) { display: none; }

.workspace-content { flex: 1; overflow-y: auto; padding: 16px 24px; }

.tab-content .content-header { margin-bottom: 12px; display: flex; justify-content: flex-end; }
.table-card :deep(.el-card__body) { padding: 0; }
:deep(.el-table__empty-block) { min-height: 200px; }

.voucher-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #eee; }
.upload-tip { color: #999; font-size: 12px; }
</style>
