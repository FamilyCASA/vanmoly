<template>
  <div class="reimbursement-list">
    <!-- 标题 & 操作 -->
    <div class="list-header">
      <h2>报销管理</h2>
      <div class="header-actions">
        <el-button @click="$router.push('/finance/my-reimbursements')" size="small">我的报销</el-button>
        <el-button type="primary" @click="openCreateDialog" :icon="Plus">新建报销</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 130px" @change="loadData">
            <el-option label="待审核" value="submitted" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已付款" value="paid" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category_id" placeholder="全部分类" clearable style="width: 150px" @change="loadData">
            <el-option v-for="c in allCategories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计条 -->
    <div class="summary-bar">
      <span>共 <strong>{{ total }}</strong> 条</span>
      <span class="divider">|</span>
      <span>待审核 <strong class="warning">{{ pendingCount }}</strong> 条</span>
      <span>申请总额 <strong>¥{{ formatNum(summaryTotal) }}</strong></span>
    </div>

    <!-- 表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="items" v-loading="loading" stripe empty-text="暂无报销记录">
        <el-table-column prop="reimb_no" label="编号" width="160" />
        <el-table-column prop="created_at" label="申请时间" width="100">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column prop="expense_date" label="费用日期" width="100" />
        <el-table-column prop="category_name" label="分类" width="110" />
        <el-table-column prop="summary" label="报销事由" min-width="200" show-overflow-tooltip />
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openDetailDrawer(row)">详情</el-button>
            <el-button
              v-if="row.status === 'submitted' && hasPermission('review')"
              text type="success" size="small"
              @click="handleReview(row, 'approved')"
            >通过</el-button>
            <el-button
              v-if="row.status === 'submitted' && hasPermission('review')"
              text type="warning" size="small"
              @click="handleReview(row, 'rejected')"
            >驳回</el-button>
            <el-button
              v-if="row.status === 'approved' && hasPermission('pay')"
              text type="primary" size="small"
              @click="openPayDialog(row)"
            >付款</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- ===== 新建报销弹窗 ===== -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建报销申请"
      width="680px"
      :close-on-click-modal="false"
      @closed="resetCreateForm"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="费用日期" prop="expense_date">
              <el-date-picker
                v-model="createForm.expense_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类" prop="category_id">
              <el-select v-model="createForm.category_id" placeholder="选择分类" style="width: 100%">
                <el-option v-for="c in allCategories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="报销事由" prop="summary">
          <el-input v-model="createForm.summary" placeholder="简要说明报销事由" maxlength="200" show-word-limit />
        </el-form-item>

        <!-- 费用明细 -->
        <el-divider content-position="left">费用明细</el-divider>
        <div class="detail-items-area">
          <div v-for="(item, idx) in createForm.detail_items" :key="idx" class="detail-item-row">
            <el-input
              v-model="item.desc"
              placeholder="费用说明"
              style="width: 200px"
              size="small"
            />
            <el-input-number
              v-model="item.amount"
              :min="0.01"
              :precision="2"
              :step="50"
              controls-position="right"
              size="small"
              style="width: 160px"
            />
            <el-input
              v-model="item.category"
              placeholder="分类"
              size="small"
              style="width: 120px"
            />
            <el-button
              v-if="idx > 0"
              text type="danger"
              size="small"
              @click="removeDetailItem(idx)"
            >删除</el-button>
          </div>
          <el-button
            text type="primary"
            size="small"
            @click="addDetailItem"
            :icon="Plus"
          >添加明细</el-button>
        </div>
        <div class="detail-total">合计：<strong>¥{{ formatNum(detailTotal) }}</strong></div>

        <!-- 凭证 -->
        <el-divider content-position="left">凭证</el-divider>
        <div class="refund-info">
          <el-alert title="提交后请将纸质凭证交至财务部" type="info" :closable="false" show-icon />
        </div>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="submitReimbursement">
          提交申请
        </el-button>
      </template>
    </el-dialog>

    <!-- ===== 详情抽屉 ===== -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="detailItem?.reimb_no || '报销详情'"
      size="500px"
    >
      <template v-if="detailItem">
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="编号">{{ detailItem.reimb_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusType(detailItem.status)" size="small">{{ statusLabel(detailItem.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="申请时间">{{ detailItem.created_at }}</el-descriptions-item>
            <el-descriptions-item label="费用日期">{{ detailItem.expense_date }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ detailItem.category_name }}</el-descriptions-item>
            <el-descriptions-item label="金额">¥{{ formatNum(detailItem.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="事由" :span="2">{{ detailItem.summary }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>费用明细</h4>
          <el-table :data="detailItem.detail_items" stripe size="small">
            <el-table-column prop="desc" label="说明" min-width="140" />
            <el-table-column prop="amount" label="金额" width="120" align="right">
              <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100" />
          </el-table>
        </div>

        <div class="detail-section" v-if="detailItem.reviewed_at">
          <h4>审核信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="审核结果">
              <el-tag :type="detailItem.status === 'approved' ? 'success' : 'danger'" size="small">
                {{ detailItem.status === 'approved' ? '已通过' : '已驳回' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审核时间">{{ detailItem.reviewed_at }}</el-descriptions-item>
            <el-descriptions-item label="审核备注" :span="2">{{ detailItem.review_note || '无' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="detailItem.paid_at">
          <h4>付款信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="付款时间">{{ detailItem.paid_at }}</el-descriptions-item>
            <el-descriptions-item label="支付方式">{{ detailItem.payment_method || '—' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
    </el-drawer>

    <!-- ===== 付款弹窗 ===== -->
    <el-dialog v-model="payDialogVisible" title="确认付款" width="480px">
      <el-form ref="payFormRef" :model="payForm" :rules="payRules" label-width="100px">
        <div class="pay-info">
          <div class="pay-label">报销单：{{ payTarget?.reimb_no }}</div>
          <div class="pay-label">申请人：{{ payTarget?.applicant_id }}</div>
          <div class="pay-amount">付款金额：<strong>¥{{ formatNum(payTarget?.total_amount) }}</strong></div>
        </div>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="payForm.payment_method" placeholder="选择支付方式" style="width: 100%">
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="现金" value="cash" />
            <el-option label="刷卡" value="card" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="paySubmitting" @click="confirmPay">确认付款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

// ===== 权限 =====
const myPermissions = ref([])
const hasPermission = (perm) => myPermissions.value.includes(perm)

// ===== 分类 =====
const categories = ref([])
const allCategories = computed(() => categories.value.filter(c => !c.parent_id))

// ===== 列表 =====
const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const summaryTotal = ref(0)
const pendingCount = ref(0)

const filters = ref({ status: 'all', category_id: null })

// ===== 新建 =====
const createDialogVisible = ref(false)
const createSubmitting = ref(false)
const createFormRef = ref(null)
const createForm = ref({
  expense_date: '',
  category_id: null,
  summary: '',
  detail_items: [{ desc: '', amount: null, category: '' }]
})
const createRules = {
  expense_date: [{ required: true, message: '请选择费用日期', trigger: 'change' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  summary: [{ required: true, message: '请输入报销事由', trigger: 'blur' }]
}

const detailTotal = computed(() =>
  createForm.value.detail_items.reduce((s, i) => s + Number(i.amount || 0), 0)
)

// ===== 详情抽屉 =====
const detailDrawerVisible = ref(false)
const detailItem = ref(null)

// ===== 付款 =====
const payDialogVisible = ref(false)
const payTarget = ref(null)
const paySubmitting = ref(false)
const payFormRef = ref(null)
const payForm = ref({ payment_method: '' })
const payRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

// ===== 工具 =====
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

// ===== 数据加载 =====
const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.status !== 'all') params.status = filters.value.status
    if (filters.value.category_id) params.category_id = filters.value.category_id

    const d = await financeAPI.getReimbursements(params)
    items.value = d.items || []
    total.value = d.total || 0

    summaryTotal.value = items.value.reduce((s, r) => s + Number(r.total_amount || 0), 0)
    pendingCount.value = items.value.filter(r => r.status === 'submitted').length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载报销列表失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const d = await financeAPI.getCategories()
    categories.value = d.items || d || []
  } catch (e) { console.error(e) }
}

const loadPermissions = async () => {
  try {
    const d = await financeAPI.getMyPermissions()
    myPermissions.value = d.permissions || []
  } catch (e) { console.error(e) }
}

const resetFilters = () => {
  filters.value = { status: 'all', category_id: null }
  page.value = 1
  loadData()
}

// ===== 新建报销 =====
const openCreateDialog = () => {
  createForm.value = {
    expense_date: '',
    category_id: null,
    summary: '',
    detail_items: [{ desc: '', amount: null, category: '' }]
  }
  createDialogVisible.value = true
}

const addDetailItem = () => {
  createForm.value.detail_items.push({ desc: '', amount: null, category: '' })
}

const removeDetailItem = (idx) => {
  createForm.value.detail_items.splice(idx, 1)
}

const resetCreateForm = () => {
  createFormRef.value?.resetFields()
}

const submitReimbursement = async () => {
  try {
    await createFormRef.value.validate()
  } catch {
    return
  }

  if (createForm.value.detail_items.length === 0 ||
      !createForm.value.detail_items.some(i => i.desc && i.amount > 0)) {
    ElMessage.warning('请至少填写一条有效的费用明细')
    return
  }

  createSubmitting.value = true
  try {
    await financeAPI.createReimbursement({
      ...createForm.value,
      total_amount: detailTotal.value
    })
    ElMessage.success('报销申请已提交，请等待审核')
    createDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '提交失败')
  } finally {
    createSubmitting.value = false
  }
}

// ===== 详情 =====
const openDetailDrawer = (row) => {
  detailItem.value = row
  detailDrawerVisible.value = true
}

// ===== 审核 =====
const handleReview = async (row, status) => {
  const label = status === 'approved' ? '通过' : '驳回'
  try {
    if (status === 'rejected') {
      await ElMessageBox.prompt('请填写驳回原因', '驳回报销', {
        confirmButtonText: '确认驳回',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '驳回原因...'
      }).then(async ({ value }) => {
        await financeAPI.reviewReimbursement(row.id, status, value || '')
        ElMessage.success('已驳回')
        loadData()
      })
    } else {
      await ElMessageBox.confirm('确认通过此报销申请？', '审核确认', {
        confirmButtonText: '确认通过',
        cancelButtonText: '取消',
        type: 'success'
      })
      await financeAPI.reviewReimbursement(row.id, status, '')
      ElMessage.success('已通过，可进行付款')
      loadData()
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('操作失败')
    }
  }
}

// ===== 付款 =====
const openPayDialog = (row) => {
  payTarget.value = row
  payForm.value = { payment_method: '' }
  payDialogVisible.value = true
}

const confirmPay = async () => {
  try {
    await payFormRef.value.validate()
  } catch { return }

  paySubmitting.value = true
  try {
    await financeAPI.payReimbursement(payTarget.value.id, payForm.value)
    ElMessage.success('付款成功，已自动生成支出流水')
    payDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '付款失败')
  } finally {
    paySubmitting.value = false
  }
}

// ===== 初始化 =====
onMounted(async () => {
  await Promise.all([loadCategories(), loadPermissions()])
  loadData()
})
</script>

<style scoped>
.reimbursement-list { padding: 0; }

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.list-header h2 { margin: 0; font-size: 20px; color: #303133; }
.header-actions { display: flex; gap: 8px; }

.filter-card { margin-bottom: 12px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px 0; }

.summary-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #fafafa;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}
.summary-bar .divider { color: #dcdfe6; }
.summary-bar .warning { color: #e6a23c; }
.summary-bar strong { font-size: 14px; }

.table-card :deep(.el-card__body) { padding: 0; }
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
}

/* 费用明细 */
.detail-items-area {
  background: #fafafa;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
}
.detail-item-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.detail-item-row:last-child { margin-bottom: 0; }
.detail-total {
  text-align: right;
  font-size: 14px;
  color: #303133;
  margin-top: 4px;
}
.detail-total strong { font-size: 16px; color: #409eff; }

.refund-info { margin-bottom: 8px; }

/* 详情抽屉 */
.detail-section { margin-bottom: 20px; }
.detail-section h4 {
  font-size: 14px;
  color: #303133;
  margin: 0 0 10px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

/* 付款弹窗 */
.pay-info {
  background: #f0f9eb;
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 16px;
}
.pay-label { font-size: 13px; color: #606266; margin-bottom: 4px; }
.pay-amount { font-size: 14px; color: #303133; margin-top: 8px; }
.pay-amount strong { font-size: 20px; color: #f56c6c; }

:deep(.el-table__empty-block) { min-height: 200px; }
</style>
