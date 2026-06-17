<template>
  <div class="org-structure-manage">
    <div class="page-header">
      <h2>组织架构管理</h2>
      <p class="subtitle">股东结构 · 部门管理 · 岗位管理</p>
    </div>

    <el-tabs v-model="activeTab" class="org-tabs">
      <!-- 股东结构 -->
      <el-tab-pane label="股东结构" name="shareholders">
        <div class="tab-content">
          <div class="section-header">
            <h3>股东信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="openShareholderDialog()">新增股东</el-button>
          </div>
          <el-table :data="shareholderList" stripe v-loading="loadingShareholders">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="phone" label="联系电话" width="130" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag>{{ roleLabel(row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="share_ratio" label="持股比例" width="100">
              <template #default="{ row }">{{ ((row.share_ratio || 0) * 100).toFixed(2) }}%</template>
            </el-table-column>
            <el-table-column prop="investment_amount" label="投资金额" width="130">
              <template #default="{ row }">¥{{ formatNum(row.investment_amount) }}</template>
            </el-table-column>
            <el-table-column prop="investment_date" label="投资日期" width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '正常' : '退出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="openShareholderDialog(row)">编辑</el-button>
                <el-button text type="danger" @click="handleDeleteShareholder(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 部门管理 -->
      <el-tab-pane label="部门管理" name="departments">
        <div class="tab-content">
          <div class="section-header">
            <h3>部门信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="openDeptDialog()">新增部门</el-button>
          </div>
          <el-table :data="departmentList" stripe v-loading="loadingDepts">
            <el-table-column prop="name" label="部门名称" width="150" />
            <el-table-column prop="dept_code" label="部门编码" width="120" />
            <el-table-column prop="leader_name" label="负责人" width="120" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="sort_order" label="排序" width="70" align="center" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="openDeptDialog(row)">编辑</el-button>
                <el-button text type="danger" @click="handleDeleteDept(row)">{{ row.status === 'active' ? '停用' : '启用' }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 岗位管理 -->
      <el-tab-pane label="岗位管理" name="positions">
        <div class="tab-content">
          <div class="section-header">
            <h3>岗位信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="openPositionDialog()">新增岗位</el-button>
          </div>
          <el-table :data="positionList" stripe v-loading="loadingPositions">
            <el-table-column prop="name" label="岗位名称" width="150" />
            <el-table-column prop="position_code" label="岗位编码" width="120" />
            <el-table-column prop="dept_name" label="所属部门" width="120" />
            <el-table-column prop="level" label="岗位等级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.level" type="info" size="small">{{ row.level }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="responsibilities" label="岗位职责" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="openPositionDialog(row)">编辑</el-button>
                <el-button text type="danger" @click="handleDeletePosition(row)">{{ row.status === 'active' ? '停用' : '启用' }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 部门编辑弹窗 -->
    <el-dialog v-model="showDeptDialog" :title="deptForm.id ? '编辑部门' : '新增部门'" width="500px" @close="deptForm = getDefaultDeptForm()">
      <el-form :model="deptForm" label-width="90px">
        <el-form-item label="部门名称" required>
          <el-input v-model="deptForm.name" placeholder="输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码">
          <el-input v-model="deptForm.dept_code" placeholder="如 DEPT-001" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="deptForm.parent_id" placeholder="无（顶级部门）" clearable style="width:100%">
            <el-option v-for="d in departmentList.filter(x => x.id !== deptForm.id)" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="deptForm.leader_name" placeholder="负责人姓名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="deptForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="deptForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeptDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDept" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 岗位编辑弹窗 -->
    <el-dialog v-model="showPositionDialog" :title="positionForm.id ? '编辑岗位' : '新增岗位'" width="500px" @close="positionForm = getDefaultPositionForm()">
      <el-form :model="positionForm" label-width="90px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="positionForm.name" placeholder="输入岗位名称" />
        </el-form-item>
        <el-form-item label="岗位编码">
          <el-input v-model="positionForm.position_code" placeholder="如 POS-001" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select v-model="positionForm.dept_id" placeholder="选择部门" clearable style="width:100%">
            <el-option v-for="d in departmentList" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位等级">
          <el-input v-model="positionForm.level" placeholder="如 P1、P2" />
        </el-form-item>
        <el-form-item label="岗位职责">
          <el-input v-model="positionForm.responsibilities" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="positionForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPositionDialog = false">取消</el-button>
        <el-button type="primary" @click="savePosition" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 股东编辑弹窗 -->
    <el-dialog v-model="showShareholderDialog" :title="shareholderForm.id ? '编辑股东' : '新增股东'" width="600px" @close="shareholderForm = getDefaultShareholderForm()">
      <el-form :model="shareholderForm" label-width="100px">
        <el-form-item label="股东姓名">
          <el-input v-model="shareholderForm.name" placeholder="输入股东姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="shareholderForm.phone" placeholder="输入手机号" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="shareholderForm.role" placeholder="选择角色" style="width:100%">
            <el-option label="执行董事" value="executive_director" />
            <el-option label="经理" value="manager" />
            <el-option label="隐名投资人" value="silent_investor" />
          </el-select>
        </el-form-item>
        <el-form-item label="持股比例">
          <el-input-number v-model="shareholderForm.share_ratio" :min="0" :max="1" :step="0.01" :precision="4" />
          <span style="margin-left: 8px;">{{ ((shareholderForm.share_ratio || 0) * 100).toFixed(2) }}%</span>
        </el-form-item>
        <el-form-item label="投资金额">
          <el-input-number v-model="shareholderForm.investment_amount" :min="0" :step="10000" style="width:200px" />
        </el-form-item>
        <el-form-item label="投资日期">
          <el-date-picker v-model="shareholderForm.investment_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="shareholderForm.status">
            <el-radio value="active">正常</el-radio>
            <el-radio value="exited">退出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shareholderForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShareholderDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShareholder" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'
import request from '@/utils/request'

const activeTab = ref('shareholders')
const saving = ref(false)

// === 加载状态 ===
const loadingShareholders = ref(false)
const loadingDepts = ref(false)
const loadingPositions = ref(false)

// === 列表数据 ===
const shareholderList = ref([])
const departmentList = ref([])
const positionList = ref([])

// === 弹窗控制 ===
const showShareholderDialog = ref(false)
const showDeptDialog = ref(false)
const showPositionDialog = ref(false)

// === 表单默认值 ===
const getDefaultShareholderForm = () => ({
  id: null, name: '', phone: '', role: '', share_ratio: 0,
  investment_amount: 0, investment_date: '', status: 'active', notes: ''
})
const getDefaultDeptForm = () => ({
  id: null, name: '', dept_code: '', parent_id: null, leader_name: '',
  description: '', sort_order: 0, status: 'active'
})
const getDefaultPositionForm = () => ({
  id: null, name: '', position_code: '', dept_id: null, level: '',
  responsibilities: '', sort_order: 0, status: 'active'
})

const shareholderForm = ref(getDefaultShareholderForm())
const deptForm = ref(getDefaultDeptForm())
const positionForm = ref(getDefaultPositionForm())

// === 工具函数 ===
const formatNum = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
const roleLabel = (role) => ({
  'executive_director': '执行董事', 'manager': '经理', 'silent_investor': '隐名投资人'
}[role] || role)

// === 股东 CRUD ===
const loadShareholders = async () => {
  loadingShareholders.value = true
  try {
    const d = await financeAPI.getShareholders()
    shareholderList.value = d.items || d || []
  } catch (e) {
    ElMessage.error('加载股东列表失败')
  } finally {
    loadingShareholders.value = false
  }
}
const openShareholderDialog = (row) => {
  shareholderForm.value = row ? { ...row } : getDefaultShareholderForm()
  showShareholderDialog.value = true
}
const saveShareholder = async () => {
  saving.value = true
  try {
    const data = { ...shareholderForm.value }
    if (data.investment_date && data.investment_date instanceof Date) {
      data.investment_date = data.investment_date.toISOString().split('T')[0]
    }
    if (data.id) {
      await financeAPI.updateShareholder(data.id, data)
    } else {
      await financeAPI.createShareholder(data)
    }
    ElMessage.success('保存成功')
    showShareholderDialog.value = false
    loadShareholders()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.message || ''))
  } finally {
    saving.value = false
  }
}
const handleDeleteShareholder = (row) => {
  ElMessageBox.confirm('确定删除该股东信息？', '确认', { type: 'warning' }).then(async () => {
    await financeAPI.deleteShareholder(row.id)
    ElMessage.success('删除成功')
    loadShareholders()
  }).catch(() => {})
}

// === 部门 CRUD ===
const loadDepartments = async () => {
  loadingDepts.value = true
  try {
    const d = await request({ url: '/finance/departments' })
    departmentList.value = d || []
  } catch (e) {
    ElMessage.error('加载部门列表失败')
  } finally {
    loadingDepts.value = false
  }
}
const openDeptDialog = (row) => {
  deptForm.value = row ? { ...row } : getDefaultDeptForm()
  showDeptDialog.value = true
}
const saveDept = async () => {
  if (!deptForm.value.name) { ElMessage.warning('请输入部门名称'); return }
  saving.value = true
  try {
    if (deptForm.value.id) {
      await request({ url: `/finance/departments/${deptForm.value.id}`, method: 'put', data: deptForm.value })
    } else {
      await request({ url: '/finance/departments', method: 'post', data: deptForm.value })
    }
    ElMessage.success('保存成功')
    showDeptDialog.value = false
    loadDepartments()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.message || ''))
  } finally {
    saving.value = false
  }
}
const handleDeleteDept = (row) => {
  const action = row.status === 'active' ? '停用' : '启用'
  ElMessageBox.confirm(`确定${action}该部门？`, '确认', { type: 'warning' }).then(async () => {
    await request({ url: `/finance/departments/${row.id}`, method: 'put', data: { status: row.status === 'active' ? 'disabled' : 'active' } })
    ElMessage.success(`${action}成功`)
    loadDepartments()
  }).catch(() => {})
}

// === 岗位 CRUD ===
const loadPositions = async () => {
  loadingPositions.value = true
  try {
    const d = await request({ url: '/finance/positions' })
    positionList.value = d || []
  } catch (e) {
    ElMessage.error('加载岗位列表失败')
  } finally {
    loadingPositions.value = false
  }
}
const openPositionDialog = (row) => {
  positionForm.value = row ? { ...row } : getDefaultPositionForm()
  showPositionDialog.value = true
}
const savePosition = async () => {
  if (!positionForm.value.name) { ElMessage.warning('请输入岗位名称'); return }
  saving.value = true
  try {
    if (positionForm.value.id) {
      await request({ url: `/finance/positions/${positionForm.value.id}`, method: 'put', data: positionForm.value })
    } else {
      await request({ url: '/finance/positions', method: 'post', data: positionForm.value })
    }
    ElMessage.success('保存成功')
    showPositionDialog.value = false
    loadPositions()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.message || ''))
  } finally {
    saving.value = false
  }
}
const handleDeletePosition = (row) => {
  const action = row.status === 'active' ? '停用' : '启用'
  ElMessageBox.confirm(`确定${action}该岗位？`, '确认', { type: 'warning' }).then(async () => {
    await request({ url: `/finance/positions/${row.id}`, method: 'put', data: { status: row.status === 'active' ? 'disabled' : 'active' } })
    ElMessage.success(`${action}成功`)
    loadPositions()
  }).catch(() => {})
}

onMounted(() => {
  loadShareholders()
  loadDepartments()
  loadPositions()
})
</script>

<style scoped>
.org-structure-manage {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #303133;
}
.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}
.org-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}
.tab-content {
  margin-top: 20px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
</style>
