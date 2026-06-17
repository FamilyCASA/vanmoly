<template>
  <div class="shareholder-list">
    <div class="page-header">
      <h2>股东信息</h2>
      <el-button type="primary" @click="openCreateDialog" :icon="Plus">添加股东</el-button>
    </div>

    <!-- 汇总卡 -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-label">股东总数</div>
        <div class="card-value">{{ shareholders.length }}</div>
      </div>
      <div class="summary-card">
        <div class="card-label">总投资额</div>
        <div class="card-value">¥{{ formatNum(totalInvestment) }}</div>
      </div>
      <div class="summary-card">
        <div class="card-label">持股总计</div>
        <div class="card-value" :class="{ warning: totalRatio > 100 }">{{ totalRatio }}%</div>
      </div>
    </div>

    <!-- 表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="shareholders" v-loading="loading" stripe empty-text="暂无股东信息">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small" effect="plain">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="持股比例" width="110" align="right">
          <template #default="{ row }">
            <span :class="{ 'ratio-warn': row.share_ratio > 50 }">{{ row.share_ratio }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="投资金额" width="140" align="right">
          <template #default="{ row }">¥{{ formatNum(row.investment_amount) }}</template>
        </el-table-column>
        <el-table-column prop="investment_date" label="投资日期" width="110" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑股东' : '添加股东'"
      width="560px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="股东" prop="name">
              <el-select
                v-model="form.name"
                filterable
                remote
                reserve-keyword
                placeholder="搜索员工作为股东"
                :remote-method="searchEmployees"
                :loading="loadingEmployees"
                style="width: 100%"
                @change="handleEmployeeSelected"
              >
                <el-option
                  v-for="item in employeeOptions"
                  :key="item.id"
                  :label="`${item.name}（${item.employee_no || '无工号'} / ${item.phone || '无电话'}）`"
                  :value="item.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="手机号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="持股比例" prop="share_ratio">
              <el-input-number v-model="form.share_ratio" :min="0" :max="100" :precision="2" :step="1" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="投资金额" prop="investment_amount">
              <el-input-number v-model="form.investment_amount" :min="0" :precision="2" :step="10000" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="投资日期">
              <el-date-picker v-model="form.investment_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="form.role" style="width: 100%">
                <el-option label="执行董事" value="director" />
                <el-option label="经理" value="manager" />
                <el-option label="隐名投资人" value="silent_investor" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="活跃" value="active" />
                <el-option label="已退出" value="exited" />
                <el-option label="待确认" value="pending" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="form.id_card" placeholder="加密存储" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="其他备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

const loading = ref(false)
const shareholders = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  name: '', phone: '', id_card: '',
  employee_id: null,
  share_ratio: 0, investment_amount: 0,
  investment_date: '', role: 'silent_investor',
  status: 'active', notes: ''
})

// 员工搜索下拉框
const employeeOptions = ref([])
const loadingEmployees = ref(false)

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

// 选中员工后自动填入电话
const handleEmployeeSelected = (name) => {
  const emp = employeeOptions.value.find(e => e.name === name)
  if (emp) {
    form.value.employee_id = emp.id
    if (emp.phone) form.value.phone = emp.phone
  } else {
    form.value.employee_id = null
  }
}

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  share_ratio: [{ required: true, message: '请输入持股比例', trigger: 'change' }],
  investment_amount: [{ required: true, message: '请输入投资金额', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const totalInvestment = computed(() => shareholders.value.reduce((s, r) => s + Number(r.investment_amount || 0), 0))
const totalRatio = computed(() => shareholders.value.reduce((s, r) => s + Number(r.share_ratio || 0), 0).toFixed(2))

const formatNum = (v) => {
  if (!v) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
const roleType = (r) => ({ director: 'danger', manager: 'warning', silent_investor: 'info' }[r] || 'info')
const roleLabel = (r) => ({ director: '执行董事', manager: '经理', silent_investor: '隐名投资人' }[r] || r)
const statusType = (s) => ({ active: 'success', exited: 'info', pending: 'warning' }[s] || 'info')
const statusLabel = (s) => ({ active: '活跃', exited: '已退出', pending: '待确认' }[s] || s)

const loadData = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getShareholders()
    shareholders.value = d || []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingId.value = null
  form.value = { name: '', phone: '', id_card: '', employee_id: null, share_ratio: 0, investment_amount: 0, investment_date: '', role: 'silent_investor', status: 'active', notes: '' }
  employeeOptions.value = []
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  form.value = { ...row, employee_id: row.employee_id || null }
  // 预加载已选员工名称到下拉框
  if (row.name) {
    employeeOptions.value = [{ id: row.employee_id, name: row.name, phone: row.phone, employee_no: '' }]
  } else {
    employeeOptions.value = []
  }
  dialogVisible.value = true
}

const resetForm = () => { formRef.value?.resetFields(); employeeOptions.value = [] }

const submitForm = async () => {
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    if (editingId.value) {
      await financeAPI.updateShareholder(editingId.value, form.value)
    } else {
      await financeAPI.createShareholder(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除股东「${row.name}」？此操作不可恢复。`, '删除确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await financeAPI.deleteShareholder(row.id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadData)
</script>

<style scoped>
.shareholder-list { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; font-size: 20px; }

.summary-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.summary-card {
  flex: 1;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 14px 18px;
}
.card-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.card-value { font-size: 20px; font-weight: 600; color: #303133; }
.card-value.warning { color: #f56c6c; }

.table-card :deep(.el-card__body) { padding: 0; }
.ratio-warn { color: #e6a23c; font-weight: 600; }

:deep(.el-table__empty-block) { min-height: 200px; }
</style>
