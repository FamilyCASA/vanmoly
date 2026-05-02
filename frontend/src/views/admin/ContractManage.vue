<template>
  <div class="contract-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>合同管理</h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新建合同
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="(count, status) in stats.by_status" :key="status">
        <el-card class="stat-card" :class="status">
          <div class="stat-value">{{ count }}</div>
          <div class="stat-label">{{ statusLabel(status) }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card total">
          <div class="stat-value">¥{{ formatMoney(stats.total_amount) }}</div>
          <div class="stat-label">合同总额</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="合同编号/标题" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option v-for="s in options.status_list" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.contract_type" placeholder="全部类型" clearable>
            <el-option v-for="t in options.contract_types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 合同列表 -->
    <el-card shadow="never">
      <el-table :data="contracts" v-loading="loading" stripe>
        <el-table-column prop="contract_no" label="合同编号" width="140" />

        <el-table-column label="客户" min-width="150">
          <template #default="{ row }">
            <div class="customer-name">{{ row.customer_name }}</div>
          </template>
        </el-table-column>

        <el-table-column label="合同标题" min-width="200">
          <template #default="{ row }">
            <div class="contract-title">{{ row.title }}</div>
            <div class="contract-type">{{ typeLabel(row.contract_type) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="金额" width="150">
          <template #default="{ row }">
            <div class="amount">¥{{ formatMoney(row.total_amount) }}</div>
            <el-progress
              :percentage="paymentProgress(row)"
              :status="paymentStatus(row)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>

        <el-table-column label="签署状态" width="120" align="center">
          <template #default="{ row }">
            <div class="sign-status">
              <el-tag v-if="row.signed_by_customer" type="success" size="small">客签</el-tag>
              <el-tag v-else type="info" size="small">客未签</el-tag>
            </div>
            <div class="sign-status">
              <el-tag v-if="row.signed_by_company" type="success" size="small">司签</el-tag>
              <el-tag v-else type="info" size="small">司未签</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="signed_date" label="签署日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.signed_date) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button link type="primary">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="submit" v-if="row.status === 'draft'">提交签署</el-dropdown-item>
                  <el-dropdown-item command="sign_customer" v-if="row.status === 'pending' && !row.signed_by_customer">客户签署</el-dropdown-item>
                  <el-dropdown-item command="sign_company" v-if="row.status === 'pending' && !row.signed_by_company">公司签署</el-dropdown-item>
                  <el-dropdown-item command="execute" v-if="row.status === 'signed'">开始执行</el-dropdown-item>
                  <el-dropdown-item command="complete" v-if="row.status === 'executing'">完成合同</el-dropdown-item>
                  <el-dropdown-item command="cancel" divided>取消合同</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 创建合同对话框 -->
    <el-dialog v-model="createDialog.visible" title="新建合同" width="800px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="选择客户" required>
          <el-select-v2
            v-model="createForm.customer_id"
            :options="customerOptions"
            placeholder="搜索客户"
            filterable
            clearable
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="合同类型">
          <el-select v-model="createForm.contract_type" style="width: 100%">
            <el-option v-for="t in options.contract_types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="合同标题">
          <el-input v-model="createForm.title" placeholder="输入合同标题" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同金额">
              <el-input-number v-model="createForm.total_amount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设计费">
              <el-input-number v-model="createForm.design_fee" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="施工费">
              <el-input-number v-model="createForm.construction_fee" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料费">
              <el-input-number v-model="createForm.material_fee" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="付款计划">
          <div class="payment-schedule">
            <div v-for="(item, index) in createForm.payment_schedule" :key="index" class="payment-item">
              <el-select v-model="item.phase" placeholder="阶段" style="width: 120px">
                <el-option v-for="p in options.payment_phases" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
              <el-input-number v-model="item.percentage" :min="0" :max="100" placeholder="占比%" style="width: 100px" />
              <el-input-number v-model="item.amount" :min="0" :precision="2" placeholder="金额" style="width: 150px" />
              <el-date-picker v-model="item.planned_date" type="date" placeholder="计划日期" style="width: 150px" />
              <el-button type="danger" link @click="removePayment(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addPayment">
              <el-icon><Plus /></el-icon> 添加付款阶段
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="合同期限">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="createContract" :loading="createDialog.loading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 合同详情抽屉 -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="70%">
      <div v-if="detailDrawer.contract" class="contract-detail">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="合同编号">{{ detailDrawer.contract.contract_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detailDrawer.contract.customer?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailDrawer.contract.status)">
              {{ statusLabel(detailDrawer.contract.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="合同金额">¥{{ formatMoney(detailDrawer.contract.total_amount) }}</el-descriptions-item>
          <el-descriptions-item label="设计费">¥{{ formatMoney(detailDrawer.contract.design_fee) }}</el-descriptions-item>
          <el-descriptions-item label="施工费">¥{{ formatMoney(detailDrawer.contract.construction_fee) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 付款计划 -->
        <div class="section">
          <h4>付款计划</h4>
          <el-table :data="detailDrawer.contract.payments" size="small" border>
            <el-table-column prop="phase" label="阶段" width="120">
              <template #default="{ row }">
                {{ phaseLabel(row.phase) }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" width="100">
              <template #default="{ row }">
                {{ row.percentage }}%
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="150">
              <template #default="{ row }">
                ¥{{ formatMoney(row.amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_date" label="计划日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.planned_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_date" label="实际日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.actual_date) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'paid' ? 'success' : 'info'" size="small">
                  {{ row.status === 'paid' ? '已付' : '待付' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'pending'"
                  type="primary"
                  size="small"
                  @click="openPayDialog(row)"
                >
                  收款
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-drawer>

    <!-- 收款对话框 -->
    <el-dialog v-model="payDialog.visible" title="记录收款" width="500px">
      <el-form :model="payForm" label-width="100px">
        <el-form-item label="付款阶段">
          <span>{{ phaseLabel(payForm.phase) }}</span>
        </el-form-item>
        <el-form-item label="金额">
          <span>¥{{ formatMoney(payForm.amount) }}</span>
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="payForm.payment_method" style="width: 100%">
            <el-option label="现金" value="cash" />
            <el-option label="银行转账" value="transfer" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信支付" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="交易流水">
          <el-input v-model="payForm.transaction_no" />
        </el-form-item>
        <el-form-item label="付款日期">
          <el-date-picker v-model="payForm.actual_date" type="date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="recordPayment" :loading="payDialog.loading">确认收款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const contracts = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  keyword: '',
  status: '',
  contract_type: ''
})

const options = reactive({
  contract_types: [],
  status_list: [],
  payment_phases: []
})

const customerOptions = ref([])

const createDialog = reactive({ visible: false, loading: false })
const detailDrawer = reactive({ visible: false, title: '', contract: null })
const payDialog = reactive({ visible: false, loading: false })

const createForm = reactive({
  customer_id: null,
  contract_type: 'all_in',
  title: '',
  total_amount: 0,
  design_fee: 0,
  construction_fee: 0,
  material_fee: 0,
  soft_fee: 0,
  payment_schedule: [],
  remark: ''
})

const payForm = reactive({
  payment_id: null,
  phase: '',
  amount: 0,
  payment_method: 'transfer',
  transaction_no: '',
  actual_date: null
})

const dateRange = computed({
  get: () => [createForm.start_date, createForm.end_date],
  set: (val) => {
    createForm.start_date = val?.[0]
    createForm.end_date = val?.[1]
  }
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/contracts', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status,
        contract_type: filterForm.contract_type
      }
    })
    contracts.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await request.get('/contracts/statistics')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadOptions = async () => {
  try {
    const res = await request.get('/contracts/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const loadCustomers = async () => {
  try {
    const res = await request.get('/customers', { params: { page_size: 1000 } })
    customerOptions.value = res.items.map(c => ({
      value: c.id,
      label: `${c.name} (${c.phone})`
    }))
  } catch (error) {
    console.error('加载客户失败', error)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  filterForm.contract_type = ''
  loadData()
}

// 创建合同
const openCreateDialog = () => {
  createDialog.visible = true
  loadCustomers()
  createForm.payment_schedule = []
}

const addPayment = () => {
  createForm.payment_schedule.push({
    phase: '',
    percentage: 0,
    amount: 0,
    planned_date: null
  })
}

const removePayment = (index) => {
  createForm.payment_schedule.splice(index, 1)
}

const createContract = async () => {
  if (!createForm.customer_id) {
    ElMessage.warning('请选择客户')
    return
  }

  createDialog.loading = true
  try {
    await request.post('/contracts', createForm)
    ElMessage.success('创建成功')
    createDialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '创建失败')
  } finally {
    createDialog.loading = false
  }
}

// 查看详情
const viewDetail = async (row) => {
  try {
    const res = await request.get(`/contracts/${row.id}`)
    detailDrawer.contract = res
    detailDrawer.title = `合同详情 - ${res.contract_no}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 更多操作
const handleCommand = async (command, row) => {
  const actions = {
    submit: () => doAction(row.id, 'submit', '提交'),
    sign_customer: () => doSign(row.id, 'customer'),
    sign_company: () => doSign(row.id, 'company'),
    execute: () => doAction(row.id, 'execute', '开始执行'),
    complete: () => doAction(row.id, 'complete', '完成'),
    cancel: () => doCancel(row.id)
  }

  if (actions[command]) {
    actions[command]()
  }
}

const doAction = async (id, action, label) => {
  try {
    await ElMessageBox.confirm(`确定要${label}吗？`, '提示', { type: 'warning' })
    await request.post(`/contracts/${id}/${action}`)
    ElMessage.success('操作成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const doSign = async (id, signer) => {
  try {
    await request.post(`/contracts/${id}/sign`, { signer })
    ElMessage.success('签署成功')
    loadData()
  } catch (error) {
    ElMessage.error('签署失败')
  }
}

const doCancel = async (id) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消合同', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputType: 'textarea'
    })
    await request.post(`/contracts/${id}/cancel`, { reason: value })
    ElMessage.success('已取消')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('取消失败')
  }
}

// 收款
const openPayDialog = (row) => {
  payForm.payment_id = row.id
  payForm.phase = row.phase
  payForm.amount = row.amount
  payForm.payment_method = 'transfer'
  payForm.transaction_no = ''
  payForm.actual_date = new Date()
  payDialog.visible = true
}

const recordPayment = async () => {
  payDialog.loading = true
  try {
    await request.post(`/contracts/${detailDrawer.contract.id}/payments/${payForm.payment_id}/pay`, payForm)
    ElMessage.success('收款记录成功')
    payDialog.visible = false
    viewDetail({ id: detailDrawer.contract.id })
    loadStats()
  } catch (error) {
    ElMessage.error('记录失败')
  } finally {
    payDialog.loading = false
  }
}

// 辅助函数
const statusType = (status) => {
  const types = {
    draft: 'info',
    pending: 'warning',
    signed: 'success',
    executing: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const statusLabel = (status) => {
  const labels = {
    draft: '草稿',
    pending: '待签署',
    signed: '已签署',
    executing: '执行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labels[status] || status
}

const typeLabel = (type) => {
  const labels = {
    design: '设计合同',
    construction: '施工合同',
    all_in: '全案合同',
    soft: '软装合同',
    custom: '定制合同'
  }
  return labels[type] || type
}

const phaseLabel = (phase) => {
  const labels = {
    deposit: '定金',
    first: '首付款',
    progress: '进度款',
    final: '尾款',
    quality: '质保金'
  }
  return labels[phase] || phase
}

const paymentProgress = (row) => {
  if (!row.payment_schedule?.length) return 0
  const paid = row.payment_schedule.filter(p => p.status === 'paid').length
  return Math.round(paid / row.payment_schedule.length * 100)
}

const paymentStatus = (row) => {
  const progress = paymentProgress(row)
  if (progress >= 100) return 'success'
  if (progress > 0) return ''
  return 'exception'
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
  loadStats()
  loadOptions()
})
</script>

<style scoped>
.contract-manage {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-card .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #262626;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.stat-card.total .stat-value {
  color: #52c41a;
}

.filter-card {
  margin-bottom: 24px;
}

.customer-name {
  font-weight: 500;
  color: #262626;
}

.contract-title {
  font-weight: 500;
  color: #262626;
}

.contract-type {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.amount {
  font-weight: 500;
  color: #f5222d;
  margin-bottom: 4px;
}

.sign-status {
  margin-bottom: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.payment-schedule {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.contract-detail {
  padding: 16px;
}

.section {
  margin-top: 32px;
}

.section h4 {
  margin-bottom: 16px;
  color: #262626;
  font-weight: 500;
}
</style>
