<template>
  <div class="receivable-list">
    <!-- 汇总卡片 -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">应收总额</div>
            <div class="summary-value primary">¥{{ formatNum(summary.total_amount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">已收金额</div>
            <div class="summary-value success">¥{{ formatNum(summary.received_amount) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-inner">
            <div class="summary-label">剩余应收</div>
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
            <el-option label="待收款" value="pending" />
            <el-option label="部分收款" value="partial" />
            <el-option label="已收齐" value="received" />
            <el-option label="已逾期" value="overdue" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="搜索事由" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">登记应收</el-button>
    </div>

    <!-- 列表 -->
    <el-card shadow="never">
      <el-table :data="list" stripe v-loading="loading" empty-text="暂无应收记录">
        <el-table-column prop="receivable_no" label="编号" width="150" />
        <el-table-column prop="title" label="应收事由" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.receivable_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="应收金额" width="130" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ formatNum(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已收" width="120" align="right">
          <template #default="{ row }">
            <span class="amount success">¥{{ formatNum(row.received_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余" width="120" align="right">
          <template #default="{ row }">
            <span class="amount warning">¥{{ formatNum(row.remaining_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="预计收款日" width="110" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button text type="success" @click="openReceiveDialog(row)">收款</el-button>
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
    <el-dialog v-model="showDialog" :title="form.id ? '编辑应收' : '登记应收'" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="应收事由" required>
          <el-input v-model="form.title" placeholder="如：XX客户合同首期款" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="应收类型" required>
              <el-select v-model="form.receivable_type" style="width: 100%;">
                <el-option label="合同应收" value="contract" />
                <el-option label="分期收款" value="installment" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应收金额" required>
              <el-input-number v-model="form.amount" :min="0" :step="1000" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="预计收款日">
              <el-date-picker v-model="form.due_date" type="date" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%;">
                <el-option label="待收款" value="pending" />
                <el-option label="部分收款" value="partial" />
                <el-option label="已收齐" value="received" />
                <el-option label="已逾期" value="overdue" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">关联信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户">
              <el-select v-model="form.customer_id" placeholder="搜索客户" filterable remote
                         :remote-method="searchCustomers" :loading="loadingCustomers" clearable>
                <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone || ''})`" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="楼盘">
              <el-select v-model="form.building_id" placeholder="搜索楼盘" filterable remote
                         :remote-method="searchBuildings" :loading="loadingBuildings" clearable>
                <el-option v-for="b in buildingOptions" :key="b.id" :label="b.name" :value="b.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合同">
              <el-select v-model="form.contract_id" placeholder="搜索合同" filterable remote
                         :remote-method="searchContracts" :loading="loadingContracts" clearable>
                <el-option v-for="c in contractOptions" :key="c.id" :label="c.contract_no || c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
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

    <!-- 收款确认弹窗 -->
    <el-dialog v-model="showReceiveDialog" title="确认收款" width="450px">
      <el-form :model="receiveForm" label-width="100px">
        <el-form-item label="应收金额">
          <span>¥{{ formatNum(currentRow?.amount) }}</span>
        </el-form-item>
        <el-form-item label="已收金额">
          <span>¥{{ formatNum(currentRow?.received_amount) }}</span>
        </el-form-item>
        <el-form-item label="本次收款" required>
          <el-input-number v-model="receiveForm.amount" :min="0" :max="maxReceive" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="收款日期">
          <el-date-picker v-model="receiveForm.actual_date" type="date" placeholder="选择日期" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReceiveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReceive">确认收款</el-button>
      </template>
    </el-dialog>

    <!-- 分期计划弹窗 -->
    <el-dialog v-model="showPlanDialog" title="付款计划" width="700px">
      <div class="plan-header">
        <span>{{ currentRow?.receivable_no }} - {{ currentRow?.title }}</span>
        <el-button type="primary" size="small" @click="openAddPlanDialog">添加分期</el-button>
      </div>
      <el-table :data="plans" stripe empty-text="暂无分期计划">
        <el-table-column prop="installment_no" label="期数" width="80">
          <template #default="{ row }">第{{ row.installment_no }}期</template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="已收" width="120" align="right">
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
            <el-button v-if="row.status !== 'paid'" text type="success" @click="confirmPlanPay(row)">确认收款</el-button>
            <el-button text type="danger" @click="deletePlan(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加分期 -->
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
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'
import request from '@/api/request'

const loading = ref(false)
const list = ref([])
const summary = ref({ total_amount: 0, received_amount: 0, remaining_amount: 0, overdue_count: 0 })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const filterForm = reactive({ status: '', keyword: '' })

// 搜索下拉框
const customerOptions = ref([])
const buildingOptions = ref([])
const contractOptions = ref([])
const quoteOptions = ref([])
const loadingCustomers = ref(false)
const loadingBuildings = ref(false)
const loadingContracts = ref(false)
const loadingQuotes = ref(false)

// 弹窗
const showDialog = ref(false)
const form = ref(getDefaultForm())
const showReceiveDialog = ref(false)
const currentRow = ref(null)
const receiveForm = ref({ amount: 0, actual_date: null })

// 分期计划
const showPlanDialog = ref(false)
const plans = ref([])
const showAddPlan = ref(false)
const planForm = ref({ installment_no: 1, amount: 0, due_date: null })

import { reactive } from 'vue'

function getDefaultForm() {
  return {
    id: null, receivable_type: 'contract', title: '', amount: 0,
    due_date: null, status: 'pending', customer_id: null, building_id: null,
    contract_id: null, quote_id: null, remark: ''
  }
}

const maxReceive = computed(() => {
  if (!currentRow.value) return 0
  return Number(currentRow.value.remaining_amount || 0)
})

const formatNum = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const typeLabel = (t) => ({ contract: '合同应收', installment: '分期收款', other: '其他' }[t] || t)
const statusType = (s) => ({ pending: 'warning', partial: '', received: 'success', overdue: 'danger', cancelled: 'info' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待收款', partial: '部分收款', received: '已收齐', overdue: '已逾期', cancelled: '已取消' }[s] || s)
const planStatusType = (s) => ({ pending: 'warning', paid: 'success', partial: '', overdue: 'danger', cancelled: 'info' }[s] || 'info')
const planStatusLabel = (s) => ({ pending: '待收', paid: '已收', partial: '部分', overdue: '逾期', cancelled: '已取消' }[s] || s)

// 搜索方法
const searchCustomers = async (q) => {
  if (!q) return
  loadingCustomers.value = true
  try { customerOptions.value = (await request({ url: '/customers/search', params: { keyword: q } })).items || [] } catch {}
  loadingCustomers.value = false
}
const searchBuildings = async (q) => {
  if (!q) return
  loadingBuildings.value = true
  try { buildingOptions.value = (await request({ url: '/buildings', params: { keyword: q } })).items || [] } catch {}
  loadingBuildings.value = false
}
const searchContracts = async (q) => {
  if (!q) return
  loadingContracts.value = true
  try { contractOptions.value = (await request({ url: '/contracts', params: { keyword: q } })).items || [] } catch {}
  loadingContracts.value = false
}
const searchQuotes = async (q) => {
  if (!q) return
  loadingQuotes.value = true
  try { quoteOptions.value = (await request({ url: '/quotes', params: { keyword: q } })).items || [] } catch {}
  loadingQuotes.value = false
}

const loadList = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getReceivables({ page: pagination.page, page_size: pagination.pageSize, ...filterForm })
    list.value = d.items || []
    pagination.total = d.total || 0
    summary.value = d.summary || summary.value
  } catch (e) {
    ElMessage.error('加载应收列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.status = ''
  filterForm.keyword = ''
  loadList()
}

const openCreateDialog = () => {
  form.value = getDefaultForm()
  showDialog.value = true
}

const openEditDialog = (row) => {
  form.value = { ...row }
  if (row.due_date) form.value.due_date = row.due_date
  showDialog.value = true
}

const handleSave = async () => {
  try {
    const data = { ...form.value }
    if (data.due_date && data.due_date instanceof Date) data.due_date = data.due_date.toISOString().split('T')[0]
    if (form.value.id) {
      await financeAPI.updateReceivable(form.value.id, data)
    } else {
      await financeAPI.createReceivable(data)
    }
    ElMessage.success('保存成功')
    showDialog.value = false
    loadList()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.message || '未知错误'))
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除此应收记录？', '确认删除', { type: 'warning' }).then(async () => {
    await financeAPI.deleteReceivable(row.id)
    ElMessage.success('删除成功')
    loadList()
  }).catch(() => {})
}

// 收款
const openReceiveDialog = (row) => {
  currentRow.value = row
  receiveForm.value = { amount: Number(row.remaining_amount || 0), actual_date: new Date() }
  showReceiveDialog.value = true
}

const handleReceive = async () => {
  try {
    const received = Number(currentRow.value.received_amount || 0) + Number(receiveForm.value.amount)
    const data = { received_amount: received }
    if (receiveForm.value.actual_date) {
      data.actual_date = receiveForm.value.actual_date.toISOString().split('T')[0]
    }
    await financeAPI.updateReceivable(currentRow.value.id, data)
    ElMessage.success('收款确认成功')
    showReceiveDialog.value = false
    loadList()
  } catch (e) {
    ElMessage.error('收款确认失败')
  }
}

// 分期计划
const viewPlans = async (row) => {
  currentRow.value = row
  showPlanDialog.value = true
  showAddPlan.value = false
  try {
    const d = await financeAPI.getPaymentPlans({ plan_type: 'receivable', parent_id: row.id })
    plans.value = d || []
  } catch (e) {
    plans.value = []
  }
}

const openAddPlanDialog = () => {
  planForm.value = { installment_no: plans.value.length + 1, amount: 0, due_date: null }
  showAddPlan.value = true
}

const addPlan = async () => {
  try {
    const data = {
      plan_type: 'receivable',
      parent_id: currentRow.value.id,
      installments: [{
        amount: planForm.value.amount,
        due_date: planForm.value.due_date ? planForm.value.due_date.toISOString().split('T')[0] : null,
        remark: ''
      }]
    }
    await financeAPI.createPaymentPlan(data)
    ElMessage.success('分期添加成功')
    showAddPlan.value = false
    viewPlans(currentRow.value)
  } catch (e) {
    ElMessage.error('添加分期失败')
  }
}

const confirmPlanPay = async (plan) => {
  try {
    await financeAPI.updatePaymentPlan(plan.id, {
      paid_amount: plan.amount,
      actual_date: new Date().toISOString().split('T')[0],
      status: 'paid'
    })
    ElMessage.success('确认收款成功')
    viewPlans(currentRow.value)
    loadList()
  } catch (e) {
    ElMessage.error('确认收款失败')
  }
}

const deletePlan = async (plan) => {
  try {
    await financeAPI.deletePaymentPlan(plan.id)
    ElMessage.success('删除成功')
    viewPlans(currentRow.value)
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => loadList())
</script>

<style scoped>
.receivable-list { padding: 0; }
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
