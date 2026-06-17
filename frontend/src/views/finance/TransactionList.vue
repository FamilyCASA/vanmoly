<template>
  <div class="transaction-list">
    <!-- 顶部标题 & 操作 -->
    <div class="list-header">
      <h2>流水管理</h2>
      <div class="header-actions">
        <el-button @click="handleExport" :icon="Download" size="small">导出</el-button>
        <el-button type="primary" @click="openCreateDialog" :icon="Plus">录入流水</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="类型">
          <el-select v-model="filters.type" placeholder="全部" clearable style="width: 110px" @change="loadData">
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category_id" placeholder="全部分类" clearable style="width: 150px" @change="loadData">
            <el-option-group label="收入">
              <el-option v-for="c in incomeCategories" :key="c.id" :label="c.name" :value="c.id" />
            </el-option-group>
            <el-option-group label="支出">
              <el-option v-for="c in expenseCategories" :key="c.id" :label="c.name" :value="c.id" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 110px" @change="loadData">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计条 -->
    <div class="summary-bar">
      <span>共 <strong>{{ total }}</strong> 条记录</span>
      <span class="divider">|</span>
      <span>收入 <strong class="income">¥{{ formatNum(summaryIncome) }}</strong></span>
      <span>支出 <strong class="expense">¥{{ formatNum(summaryExpense) }}</strong></span>
      <span>结余 <strong :class="summaryIncome - summaryExpense >= 0 ? 'income' : 'expense'">¥{{ formatNum(summaryIncome - summaryExpense) }}</strong></span>
    </div>

    <!-- 流水表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="transactions"
        v-loading="loading"
        stripe
        empty-text="暂无流水记录"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="trans_date" label="日期" width="110" sortable="custom" />
        <el-table-column prop="trans_no" label="编号" width="170" show-overflow-tooltip />
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.trans_type === 'income' ? 'success' : 'danger'" size="small" effect="plain">
              {{ row.trans_type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="sub_category" label="子分类" width="100" show-overflow-tooltip />
        <el-table-column prop="summary" label="摘要" min-width="200" show-overflow-tooltip />
        <el-table-column label="金额" width="140" align="right" sortable="custom">
          <template #default="{ row }">
            <span :class="row.trans_type === 'income' ? 'income' : 'expense'" class="amount-text">
              {{ row.trans_type === 'income' ? '+' : '-' }}¥{{ formatNum(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'pending' && hasPermission('review')"
              text type="success" size="small"
              @click="handleReview(row, 'approved')"
            >通过</el-button>
            <el-button
              v-if="row.status === 'pending' && hasPermission('review')"
              text type="warning" size="small"
              @click="handleReview(row, 'rejected')"
            >驳回</el-button>
            <el-button
              v-if="row.status !== 'deleted'"
              text type="danger" size="small"
              @click="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑流水' : '录入流水'"
      width="620px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px" class="trans-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="类型" prop="trans_type">
              <el-radio-group v-model="form.trans_type" @change="handleTypeChange">
                <el-radio-button value="income">收入</el-radio-button>
                <el-radio-button value="expense">支出</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发生日期" prop="trans_date">
              <el-date-picker
                v-model="form.trans_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="金额" prop="amount">
              <el-input-number
                v-model="form.amount"
                :min="0.01"
                :precision="2"
                :step="100"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="支付方式" prop="payment_method">
              <el-select v-model="form.payment_method" placeholder="选择支付方式" style="width: 100%">
                <el-option label="银行转账" value="bank_transfer" />
                <el-option label="微信" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="现金" value="cash" />
                <el-option label="刷卡" value="card" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category_id">
              <el-select v-model="form.category_id" placeholder="选择分类" style="width: 100%">
                <el-option
                  v-for="c in filteredCategories"
                  :key="c.id"
                  :label="c.name"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="子分类">
              <el-input v-model="form.sub_category" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="摘要" prop="summary">
          <el-input v-model="form.summary" placeholder="请输入摘要/备注" maxlength="200" show-word-limit />
        </el-form-item>

        <!-- 关联信息（可折叠） -->
        <el-divider content-position="left">
          <el-button text size="small" @click="showRelation = !showRelation">
            关联信息 <el-icon><ArrowDown v-if="!showRelation" /><ArrowUp v-else /></el-icon>
          </el-button>
        </el-divider>
        <div v-show="showRelation">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="客户">
                <el-select
                  v-model="form.customer_id"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="搜索客户"
                  :remote-method="searchCustomers"
                  :loading="loadingCustomers"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in customerOptions"
                    :key="item.id"
                    :label="`${item.name}${item.phone ? ' (' + item.phone + ')' : ''}`"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="员工">
                <el-select
                  v-model="form.employee_id"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="搜索员工"
                  :remote-method="searchEmployees"
                  :loading="loadingEmployees"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in employeeOptions"
                    :key="item.id"
                    :label="`${item.name}${item.employee_no ? ' (' + item.employee_no + ')' : ''}`"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="楼盘">
                <el-select
                  v-model="form.building_id"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="搜索楼盘"
                  :remote-method="searchBuildings"
                  :loading="loadingBuildings"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in buildingOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="报价单">
                <el-select
                  v-model="form.quote_id"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="搜索报价单"
                  :remote-method="searchQuotes"
                  :loading="loadingQuotes"
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in quoteOptions"
                    :key="item.id"
                    :label="item.quote_no || ('报价 #' + item.id)"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 凭证上传 -->
        <el-form-item label="凭证" prop="voucher_files">
          <el-upload
            v-model:file-list="fileList"
            action=""
            :auto-upload="false"
            :limit="5"
            accept="image/*,.pdf"
            list-type="picture-card"
            :on-exceed="() => ElMessage.warning('最多上传5个文件')"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持图片或PDF，最多5个</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除弹窗 -->
    <el-dialog v-model="deleteDialogVisible" title="删除流水" width="440px">
      <el-form>
        <el-form-item label="删除原因" required>
          <el-input
            v-model="deleteReason"
            type="textarea"
            :rows="3"
            placeholder="请填写删除原因（必填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="deleteSubmitting" @click="confirmDelete">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

// ===== 权限 =====
const myPermissions = ref([])
const hasPermission = (perm) => myPermissions.value.includes(perm)

// ===== 分类数据 =====
const categories = ref([])
const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income' && !c.parent_id))
const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense' && !c.parent_id))
const filteredCategories = computed(() => {
  return categories.value.filter(c => c.type === form.value.trans_type && !c.parent_id)
})

// ===== 列表 =====
const loading = ref(false)
const transactions = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const summaryIncome = ref(0)
const summaryExpense = ref(0)

const filters = ref({
  type: 'all',
  category_id: null,
  status: 'all'
})
const dateRange = ref(null)

// ===== 弹窗 =====
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const showRelation = ref(false)
const fileList = ref([])

// ===== 关联信息搜索下拉框 =====
const customerOptions = ref([])
const employeeOptions = ref([])
const buildingOptions = ref([])
const quoteOptions = ref([])
const loadingCustomers = ref(false)
const loadingEmployees = ref(false)
const loadingBuildings = ref(false)
const loadingQuotes = ref(false)

const form = ref({
  trans_type: 'expense',
  trans_date: '',
  amount: null,
  category_id: null,
  sub_category: '',
  summary: '',
  payment_method: '',
  customer_id: null,
  employee_id: null,
  building_id: null,
  quote_id: null
})

const formRules = {
  trans_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  trans_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  summary: [{ required: true, message: '请输入摘要', trigger: 'blur' }]
}

// 删除弹窗
const deleteDialogVisible = ref(false)
const deleteTarget = ref(null)
const deleteReason = ref('')
const deleteSubmitting = ref(false)

const formRef = ref(null)

// ===== 工具函数 =====
const formatNum = (v) => {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const statusType = (s) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', deleted: 'info' }
  return map[s] || 'info'
}
const statusLabel = (s) => {
  const map = { pending: '待审', approved: '已通过', rejected: '已驳回', deleted: '已删' }
  return map[s] || s
}

// ===== 数据加载 =====
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.type && filters.value.type !== 'all') params.type = filters.value.type
    if (filters.value.category_id) params.category_id = filters.value.category_id
    if (filters.value.status && filters.value.status !== 'all') params.status = filters.value.status
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const d = await financeAPI.getTransactions(params)
    transactions.value = d.items || []
    total.value = d.total || 0

    // 使用后端返回的汇总统计
    summaryIncome.value = d.summary_income || 0
    summaryExpense.value = d.summary_expense || 0
  } catch (e) {
    console.error(e)
    ElMessage.error('加载流水列表失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const d = await financeAPI.getCategories()
    categories.value = d.items || d || []
  } catch (e) {
    console.error(e)
  }
}

const loadPermissions = async () => {
  try {
    const d = await financeAPI.getMyPermissions()
    myPermissions.value = d.permissions || []
  } catch (e) {
    console.error(e)
  }
}

// ===== 关联信息搜索方法 =====
const searchCustomers = async (query) => {
  if (!query || query.length < 1) { customerOptions.value = []; return }
  loadingCustomers.value = true
  try {
    const res = await request({ url: '/customers/search', method: 'get', params: { keyword: query, page_size: 20 } })
    customerOptions.value = res.data?.items || []
  } catch (e) {
    console.error('搜索客户失败:', e)
  } finally {
    loadingCustomers.value = false
  }
}

const searchEmployees = async (query) => {
  if (!query || query.length < 1) { employeeOptions.value = []; return }
  loadingEmployees.value = true
  try {
    const res = await request({ url: '/employees', method: 'get', params: { keyword: query, page_size: 20 } })
    employeeOptions.value = res.data?.items || []
  } catch (e) {
    console.error('搜索员工失败:', e)
  } finally {
    loadingEmployees.value = false
  }
}

const searchBuildings = async (query) => {
  if (!query || query.length < 1) { buildingOptions.value = []; return }
  loadingBuildings.value = true
  try {
    const res = await request({ url: '/buildings', method: 'get', params: { keyword: query, page_size: 20 } })
    buildingOptions.value = res.data?.items || []
  } catch (e) {
    console.error('搜索楼盘失败:', e)
  } finally {
    loadingBuildings.value = false
  }
}

const searchQuotes = async (query) => {
  if (!query || query.length < 1) { quoteOptions.value = []; return }
  loadingQuotes.value = true
  try {
    const res = await request({ url: '/quotes', method: 'get', params: { keyword: query, page_size: 20 } })
    quoteOptions.value = res.data?.items || []
  } catch (e) {
    console.error('搜索报价单失败:', e)
  } finally {
    loadingQuotes.value = false
  }
}

// ===== 筛选 =====
const handleDateChange = () => {
  page.value = 1
  loadData()
}

const resetFilters = () => {
  filters.value = { type: 'all', category_id: null, status: 'all' }
  dateRange.value = null
  page.value = 1
  loadData()
}

const handleSortChange = ({ prop, order }) => {
  // 前端本地排序（数据量小时可用）
  if (!order) return
  const key = prop
  transactions.value.sort((a, b) => {
    const va = a[key], vb = b[key]
    if (key === 'amount') {
      const na = Number(va), nb = Number(vb)
      return order === 'ascending' ? na - nb : nb - na
    }
    return order === 'ascending'
      ? String(va).localeCompare(String(vb))
      : String(vb).localeCompare(String(va))
  })
}

// ===== 创建/编辑 =====
const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  form.value = {
    trans_type: 'expense',
    trans_date: new Date().toISOString().slice(0, 10),
    amount: null,
    category_id: null,
    sub_category: '',
    summary: '',
    payment_method: '',
    customer_id: null,
    employee_id: null,
    building_id: null,
    quote_id: null
  }
  fileList.value = []
  customerOptions.value = []
  employeeOptions.value = []
  buildingOptions.value = []
  quoteOptions.value = []
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    trans_type: row.trans_type,
    trans_date: row.trans_date,
    amount: Number(row.amount),
    category_id: row.category_id,
    sub_category: row.sub_category || '',
    summary: row.summary || '',
    payment_method: row.payment_method || '',
    customer_id: row.customer_id,
    employee_id: row.employee_id,
    building_id: row.building_id,
    quote_id: row.quote_id
  }
  // 预加载已选关联项（让下拉框能显示名称）
  if (row.customer_id) customerOptions.value = [{ id: row.customer_id, name: row.customer_name || `客户#${row.customer_id}`, phone: '' }]
  else customerOptions.value = []
  if (row.employee_id) employeeOptions.value = [{ id: row.employee_id, name: row.employee_name || `员工#${row.employee_id}`, employee_no: '' }]
  else employeeOptions.value = []
  if (row.building_id) buildingOptions.value = [{ id: row.building_id, name: row.building_name || `楼盘#${row.building_id}` }]
  else buildingOptions.value = []
  if (row.quote_id) quoteOptions.value = [{ id: row.quote_id, quote_no: row.quote_no || `报价#${row.quote_id}` }]
  else quoteOptions.value = []
  // 凭证文件回显
  fileList.value = (row.voucher_files || []).map((url, i) => ({
    name: `凭证${i + 1}`,
    url: url
  }))
  dialogVisible.value = true
}

const handleTypeChange = () => {
  form.value.category_id = null
}

const resetForm = () => {
  formRef.value?.resetFields()
  fileList.value = []
  showRelation.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  // 凭证必填
  const voucherFiles = fileList.value.map(f => f.url || f.name)

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      voucher_files: voucherFiles
    }

    if (isEdit.value) {
      await financeAPI.updateTransaction(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await financeAPI.createTransaction(payload)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ===== 审核 =====
const handleReview = async (row, status) => {
  const label = status === 'approved' ? '通过' : '驳回'
  try {
    await ElMessageBox.confirm(`确认${label}此流水？`, '审核确认', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await financeAPI.reviewTransaction(row.id, status)
    ElMessage.success(`${label}成功`)
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('操作失败')
    }
  }
}

// ===== 删除 =====
const handleDelete = (row) => {
  deleteTarget.value = row
  deleteReason.value = ''
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!deleteReason.value.trim()) {
    ElMessage.warning('请填写删除原因')
    return
  }
  deleteSubmitting.value = true
  try {
    await financeAPI.deleteTransaction(deleteTarget.value.id, deleteReason.value)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '删除失败')
  } finally {
    deleteSubmitting.value = false
  }
}

// ===== 导出 =====
const handleExport = () => {
  ElMessage.info('导出功能将在后续版本上线')
}

// ===== 初始化 =====
onMounted(async () => {
  await Promise.all([loadCategories(), loadPermissions()])
  loadData()
})
</script>

<style scoped>
.transaction-list {
  padding: 0;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: 12px;
}
.filter-card :deep(.el-card__body) {
  padding: 12px 16px 0;
}
.filter-form .el-form-item {
  margin-bottom: 12px;
}

/* 统计条 */
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
.summary-bar .divider {
  color: #dcdfe6;
}
.summary-bar strong {
  font-size: 14px;
}
.summary-bar .income { color: #67c23a; }
.summary-bar .expense { color: #f56c6c; }

/* 表格 */
.table-card :deep(.el-card__body) {
  padding: 0;
}

.amount-text {
  font-weight: 600;
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 14px;
}
.amount-text.income { color: #67c23a; }
.amount-text.expense { color: #f56c6c; }

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
}

/* 弹窗表单 */
.trans-form {
  padding-right: 20px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 空状态优化 */
:deep(.el-table__empty-block) {
  min-height: 200px;
}
</style>
