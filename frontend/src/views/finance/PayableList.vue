<template>
  <div class="payable-list">
    <!-- 汇总卡片 -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">应付总额</div>
            <div class="summary-value primary">¥{{ formatNum(summary.total_amount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">已付金额</div>
            <div class="summary-value success">¥{{ formatNum(summary.paid_amount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">剩余应付</div>
            <div class="summary-value warning">¥{{ formatNum(summary.remaining_amount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">逾期笔数</div>
            <div class="summary-value danger">{{ summary.overdue_count }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px;">
            <el-option label="待付款" value="pending" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付清" value="paid" />
            <el-option label="已逾期" value="overdue" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="搜索事由/供应商" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">登记应付</el-button>
    </div>

    <!-- 列表 -->
    <el-card shadow="never">
      <el-table :data="list" stripe v-loading="loading" empty-text="暂无应付记录">
        <el-table-column prop="payable_no" label="编号" width="150" />
        <el-table-column prop="title" label="应付事由" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.payable_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="供应商" width="130" show-overflow-tooltip />
        <el-table-column label="应付金额" width="130" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ formatNum(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已付" width="120" align="right">
          <template #default="{ row }">
            <span class="amount success">¥{{ formatNum(row.paid_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余" width="120" align="right">
          <template #default="{ row }">
            <span class="amount warning">¥{{ formatNum(row.remaining_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="预计付款日" width="110" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button text type="success" @click="openPayDialog(row)">付款</el-button>
            <el-button text type="info" @click="viewPlans(row)">分期</el-button>
            <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="form.id ? '编辑应付' : '登记应付'" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="应付事由" required>
          <el-input v-model="form.title" placeholder="如：XX供应商物料采购款" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="应付类型" required>
              <el-select v-model="form.payable_type" style="width: 100%;">
                <el-option label="供应商付款" value="supplier" />
                <el-option label="分包付款" value="subcontract" />
                <el-option label="物料采购" value="material" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应付金额" required>
              <el-input-number v-model="form.amount" :min="0" :step="1000" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-input v-model="form.supplier_name" placeholder="供应商/收款方名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计付款日">
              <el-date-picker v-model="form.due_date" type="date" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">关联信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="楼盘">
              <el-select v-model="form.building_id" placeholder="搜索楼盘" filterable remote
                         :remote-method="searchBuildings" :loading="loadingBuildings" clearable>
                <el-option v-for="b in buildingOptions" :key="b.id" :label="b.name" :value="b.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同">
              <el-select v-model="form.contract_id" placeholder="搜索合同" filterable remote
                         :remote-method="searchContracts" :loading="loadingContracts" clearable>
                <el-option v-for="c in contractOptions" :key="c.id" :label="c.contract_no || c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="报价单">
              <el-select v-model="form.quote_id" placeholder="搜索报价单" filterable remote
                         :remote-method="searchQuotes" :loading="loadingQuotes" clearable>
                <el-option v-for="q in quoteOptions" :key="q.id" :label="q.quote_no" :value="q.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 付款确认弹窗 -->
    <el-dialog v-model="showPayDialog" title="确认付款" width="450px">
      <el-form :model="payForm" label-width="100px">
        <el-form-item label="应付金额">
          <span>¥{{ formatNum(currentRow?.amount) }}</span>
        </el-form-item>
        <el-form-item label="已付金额">
          <span>¥{{ formatNum(currentRow?.paid_amount) }}</span>
        </el-form-item>
        <el-form-item label="本次付款" required>
          <el-input-number v-model="payForm.amount" :min="0" :max="maxPay" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="付款日期">
          <el-date-picker v-model="payForm.actual_date" type="date" placeholder="选择日期" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPayDialog = false">取消</el-button>
        <el-button type="primary" @click="handlePay">确认付款</el-button>
      </template>
    </el-dialog>

    <!-- 分期计划弹窗 -->
    <el-dialog v-model="showPlanDialog" title="付款计划" width="700px">
      <div class="plan-header">
        <span>{{ currentRow?.payable_no }} - {{ currentRow?.title }}</span>
        <el-button type="primary" size="small" @click="openAddPlanDialog">添加分期</el-button>
      </div>
      <el-table :data="plans" stripe empty-text="暂无分期计划">
        <el-table-column prop="installment_no" label="期数" width="80">
          <template #default="{ row }">第{{ row.installment_no }}期</template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="已付" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.paid_amount) }}</template>
        </el-table-column>
        <el-table-column prop="due_date" label="预计日期" width="110" />
        <el-table-column prop="actual_date" label="实际日期" width="110" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="planStatusType(row.status)" size="small">{{ planStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'paid'" text type="success" @click="confirmPlanPay(row)">确认付款</el-button>
            <el-button text type="danger" @click="deletePlan(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="showAddPlan" class="add-plan-form">
        <el-divider />
        <el-form :model="planForm" :inline="true">
          <el-form-item label="期数">
            <el-input-number v-model="planForm.installment_no" :min="1" style="width: 100px;" />
          </el-form-item>
          <el-form-item label="金额">
            <el-input-number v-model="planForm.amount" :min="0" :step="1000" style="width: 140px;" />
          </el-form-item>
          <el-form-item label="预计日期">
            <el-date-picker v-model="planForm.due_date" type="date" placeholder="日期" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addPlan">添加</el-button>
            <el-button @click="showAddPlan = false">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'
import request from '@/api/request'

const loading = ref(false)
const list = ref([])
const summary = ref({ total_amount: 0, paid_amount: 0, remaining_amount: 0, overdue_count: 0 })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const filterForm = reactive({ status: '', keyword: '' })

const buildingOptions = ref([])
const contractOptions = ref([])
const quoteOptions = ref([])
const loadingBuildings = ref(false)
const loadingContracts = ref(false)
const loadingQuotes = ref(false)

const showDialog = ref(false)
const form = ref(getDefaultForm())
const showPayDialog = ref(false)
const currentRow = ref(null)
const payForm = ref({ amount: 0, actual_date: null })

const showPlanDialog = ref(false)
const plans = ref([])
const showAddPlan = ref(false)
const planForm = ref({ installment_no: 1, amount: 0, due_date: null })

function getDefaultForm() {
  return {
    id: null, payable_type: 'supplier', title: '', amount: 0,
    supplier_name: '', due_date: null, status: 'pending', building_id: null,
    contract_id: null, quote_id: null, remark: ''
  }
}

const maxPay = computed(() => {
  if (!currentRow.value) return 0
  return Number(currentRow.value.remaining_amount || 0)
})

const formatNum = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const typeLabel = (t) => ({ supplier: '供应商', subcontract: '分包', material: '物料', other: '其他' }[t] || t)
const statusType = (s) => ({ pending: 'warning', partial: '', paid: 'success', overdue: 'danger', cancelled: 'info' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待付款', partial: '部分付款', paid: '已付清', overdue: '已逾期', cancelled: '已取消' }[s] || s)
const planStatusType = (s) => ({ pending: 'warning', paid: 'success', partial: '', overdue: 'danger', cancelled: 'info' }[s] || 'info')
const planStatusLabel = (s) => ({ pending: '待付', paid: '已付', partial: '部分', overdue: '逾期', cancelled: '已取消' }[s] || s)

const searchBuildings = async (q) => {
  if (!q) return; loadingBuildings.value = true
  try { buildingOptions.value = (await request({ url: '/buildings', params: { keyword: q } })).items || [] } catch {}
  loadingBuildings.value = false
}
const searchContracts = async (q) => {
  if (!q) return; loadingContracts.value = true
  try { contractOptions.value = (await request({ url: '/contracts', params: { keyword: q } })).items || [] } catch {}
  loadingContracts.value = false
}
const searchQuotes = async (q) => {
  if (!q) return; loadingQuotes.value = true
  try { quoteOptions.value = (await request({ url: '/quotes', params: { keyword: q } })).items || [] } catch {}
  loadingQuotes.value = false
}

const loadList = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getPayables({ page: pagination.page, page_size: pagination.pageSize, ...filterForm })
    list.value = d.items || []
    pagination.total = d.total || 0
    summary.value = d.summary || summary.value
  } catch (e) {
    ElMessage.error('加载应付列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => { filterForm.status = ''; filterForm.keyword = ''; loadList() }

const openCreateDialog = () => { form.value = getDefaultForm(); showDialog.value = true }
const openEditDialog = async (row) => {
  form.value = { ...row }
  // 预加载关联下拉框的已选项
  buildingOptions.value = []
  contractOptions.value = []
  quoteOptions.value = []
  if (row.building_id) {
    try {
      const res = await request({ url: `/buildings`, params: { keyword: row.building_name || row.building_id } })
      buildingOptions.value = res.items || []
    } catch { buildingOptions.value = [{ id: row.building_id, name: row.building_name || `ID:${row.building_id}` }] }
  }
  if (row.contract_id) {
    try {
      const res = await request({ url: `/contracts`, params: { keyword: row.contract_no || row.contract_id } })
      contractOptions.value = res.items || []
    } catch { contractOptions.value = [{ id: row.contract_id, contract_no: row.contract_no || `ID:${row.contract_id}`, name: row.contract_no || `ID:${row.contract_id}` }] }
  }
  if (row.quote_id) {
    try {
      const res = await request({ url: `/quotes`, params: { keyword: row.quote_no || row.quote_id } })
      quoteOptions.value = res.items || []
    } catch { quoteOptions.value = [{ id: row.quote_id, quote_no: row.quote_no || `ID:${row.quote_id}` }] }
  }
  showDialog.value = true
}

const handleSave = async () => {
  try {
    const data = { ...form.value }
    if (data.due_date && data.due_date instanceof Date) data.due_date = data.due_date.toISOString().split('T')[0]
    if (form.value.id) {
      await financeAPI.updatePayable(form.value.id, data)
    } else {
      await financeAPI.createPayable(data)
    }
    ElMessage.success('保存成功'); showDialog.value = false; loadList()
  } catch (e) { ElMessage.error('保存失败：' + (e.message || '')) }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除此应付记录？', '确认删除', { type: 'warning' }).then(async () => {
    await financeAPI.deletePayable(row.id); ElMessage.success('删除成功'); loadList()
  }).catch(() => {})
}

const openPayDialog = (row) => {
  currentRow.value = row
  payForm.value = { amount: Number(row.remaining_amount || 0), actual_date: new Date() }
  showPayDialog.value = true
}

const handlePay = async () => {
  try {
    const paid = Number(currentRow.value.paid_amount || 0) + Number(payForm.value.amount)
    const data = { paid_amount: paid }
    if (payForm.value.actual_date) data.actual_date = payForm.value.actual_date.toISOString().split('T')[0]
    await financeAPI.updatePayable(currentRow.value.id, data)
    ElMessage.success('付款确认成功'); showPayDialog.value = false; loadList()
  } catch (e) { ElMessage.error('付款确认失败') }
}

const viewPlans = async (row) => {
  currentRow.value = row; showPlanDialog.value = true; showAddPlan.value = false
  try { plans.value = (await financeAPI.getPaymentPlans({ plan_type: 'payable', parent_id: row.id })) || [] } catch { plans.value = [] }
}

const openAddPlanDialog = () => {
  planForm.value = { installment_no: plans.value.length + 1, amount: 0, due_date: null }; showAddPlan.value = true
}

const addPlan = async () => {
  try {
    await financeAPI.createPaymentPlan({
      plan_type: 'payable', parent_id: currentRow.value.id,
      installments: [{ amount: planForm.value.amount, due_date: planForm.value.due_date ? planForm.value.due_date.toISOString().split('T')[0] : null, remark: '' }]
    })
    ElMessage.success('分期添加成功'); showAddPlan.value = false; viewPlans(currentRow.value)
  } catch (e) { ElMessage.error('添加分期失败') }
}

const confirmPlanPay = async (plan) => {
  try {
    await financeAPI.updatePaymentPlan(plan.id, { paid_amount: plan.amount, actual_date: new Date().toISOString().split('T')[0], status: 'paid' })
    ElMessage.success('确认付款成功'); viewPlans(currentRow.value); loadList()
  } catch (e) { ElMessage.error('确认付款失败') }
}

const deletePlan = async (plan) => {
  try { await financeAPI.deletePaymentPlan(plan.id); ElMessage.success('删除成功'); viewPlans(currentRow.value) } catch { ElMessage.error('删除失败') }
}

onMounted(() => loadList())
</script>

<style scoped>
.payable-list { padding: 0; }
.summary-row { margin-bottom: 16px; }
.summary-card { height: 100%; }
.summary-inner { padding: 12px; text-align: center; }
.summary-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.summary-value { font-size: 22px; font-weight: bold; font-family: 'SF Mono', monospace; }
.summary-value.primary { color: #409eff; }
.summary-value.success { color: #67c23a; }
.summary-value.warning { color: #e6a23c; }
.summary-value.danger { color: #f56c6c; }
.filter-card { margin-bottom: 12px; }
.action-bar { margin-bottom: 12px; }
.amount { font-weight: 600; font-family: 'SF Mono', monospace; }
.amount.success { color: #67c23a; }
.amount.warning { color: #e6a23c; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.plan-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; font-weight: 600; }
.add-plan-form { margin-top: 8px; }
</style>
