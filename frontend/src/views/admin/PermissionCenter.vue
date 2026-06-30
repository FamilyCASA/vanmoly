<template>
  <div class="permission-center">
    <section class="permission-hero">
      <div>
        <p>ACCESS CONTROL</p>
        <h2>细粒度权限中心</h2>
        <span>把页面访问、任务动作、项目范围和授权边界统一管理。</span>
      </div>
      <el-button @click="loadAll">刷新</el-button>
    </section>

    <div class="permission-grid">
      <el-card shadow="never" class="grant-card">
        <template #header>分配权限</template>
        <el-form :model="grantForm" label-width="90px">
          <el-form-item label="授权员工" required>
            <el-select v-model="grantForm.employee_id" filterable clearable style="width:100%" @change="loadAssignments">
              <el-option v-for="item in employees" :key="item.id" :label="employeeLabel(item)" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="操作权限" required>
            <el-cascader
              v-model="selectedPermissionPaths"
              :options="permissionCascader"
              :props="{ multiple: true, emitPath: true }"
              filterable
              clearable
              collapse-tags
              collapse-tags-tooltip
              style="width:100%"
              @change="syncPermissionKeys"
            />
          </el-form-item>
          <el-form-item label="权限范围">
            <el-select v-model="grantForm.scope_type" style="width:100%">
              <el-option v-for="item in scopeTypes" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="范围ID">
            <el-input-number v-model="grantForm.scope_id" :min="1" placeholder="项目/门店/部门ID" style="width:100%" />
          </el-form-item>
          <el-form-item label="授权原因">
            <el-input v-model="grantForm.reason" type="textarea" :rows="3" placeholder="例如：担任项目组长、临时负责审核、门店管理授权" />
          </el-form-item>
        </el-form>
        <el-button type="primary" :loading="saving" @click="grantPermission">确认分配</el-button>
      </el-card>

      <el-card shadow="never" class="rules-card">
        <template #header>授权边界</template>
        <div class="rule-item">
          <strong>超级管理员</strong>
          <span>可分配所有管理层和业务权限。</span>
        </div>
        <div class="rule-item">
          <strong>门店店长</strong>
          <span>可分配所辖员工的门店、项目、任务和组织权限。</span>
        </div>
        <div class="rule-item">
          <strong>项目组长</strong>
          <span>可分配自己项目组成员的项目内执行权限。</span>
        </div>
      </el-card>
    </div>

    <el-card shadow="never" class="assignment-card">
      <template #header>
        <div class="card-head">
          <span>当前权限</span>
          <el-select v-model="filterEmployeeId" placeholder="筛选员工" clearable filterable @change="loadAssignments">
            <el-option v-for="item in employees" :key="item.id" :label="employeeLabel(item)" :value="item.id" />
          </el-select>
        </div>
      </template>
      <el-table :data="assignments" v-loading="loading" stripe>
        <el-table-column prop="employee_name" label="员工" width="120" />
        <el-table-column label="权限" min-width="180">
          <template #default="{ row }">{{ permissionLabel(row.permission_key) }}</template>
        </el-table-column>
        <el-table-column label="范围" width="140">
          <template #default="{ row }">{{ scopeLabel(row.scope_type) }} {{ row.scope_id || '' }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="授权时间" width="170" />
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.is_active" link type="danger" @click="revokePermission(row)">撤销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const saving = ref(false)
const employees = ref([])
const permissionGroups = ref([])
const scopeTypes = ref([])
const assignments = ref([])
const filterEmployeeId = ref(null)
const selectedPermissionPaths = ref([])

const grantForm = reactive({
  employee_id: null,
  permission_keys: [],
  scope_type: 'store',
  scope_id: null,
  reason: ''
})

const permissionCascader = computed(() => permissionGroups.value.map(group => ({
  label: group.group,
  value: group.group,
  children: (group.items || []).map(item => ({
    label: item.label,
    value: item.key
  }))
})))

const flatPermissions = computed(() => permissionGroups.value.flatMap(group => group.items || []))

const loadRegistry = async () => {
  const res = await request.get('/permissions/registry')
  permissionGroups.value = res.groups || []
  scopeTypes.value = res.scope_types || []
}

const loadEmployees = async () => {
  employees.value = await request.get('/permissions/manageable-employees')
}

const loadAssignments = async () => {
  loading.value = true
  try {
    const employeeId = filterEmployeeId.value || grantForm.employee_id
    assignments.value = await request.get('/permissions/assignments', {
      params: employeeId ? { employee_id: employeeId } : {}
    })
  } finally {
    loading.value = false
  }
}

const loadAll = async () => {
  await Promise.all([loadRegistry(), loadEmployees()])
  await loadAssignments()
}

const syncPermissionKeys = () => {
  // 多选级联返回 [[group, key], [group, key], ...]
  grantForm.permission_keys = (selectedPermissionPaths.value || [])
    .map(path => Array.isArray(path) ? path[1] : path)
    .filter(Boolean)
}

const grantPermission = async () => {
  if (!grantForm.employee_id || !grantForm.permission_keys.length) {
    ElMessage.warning('请选择员工和权限')
    return
  }
  saving.value = true
  try {
    const res = await request.post('/permissions/assignments', grantForm)
    ElMessage.success(res.message || '权限已分配')
    selectedPermissionPaths.value = []
    await loadAssignments()
  } finally {
    saving.value = false
  }
}

const revokePermission = async (row) => {
  await ElMessageBox.confirm(`确定撤销「${permissionLabel(row.permission_key)}」？`, '撤销权限', { type: 'warning' })
  await request.delete(`/permissions/assignments/${row.id}`)
  ElMessage.success('权限已撤销')
  await loadAssignments()
}

const employeeLabel = (item) => {
  const suffix = [item.department_name, item.position_name].filter(Boolean).join(' / ')
  return suffix ? `${item.name} / ${suffix}` : item.name
}

const permissionLabel = (key) => flatPermissions.value.find(item => item.key === key)?.label || key
const scopeLabel = (value) => scopeTypes.value.find(item => item.value === value)?.label || value

onMounted(loadAll)
</script>

<style scoped>
.permission-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.permission-hero {
  min-height: 148px;
  padding: 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #16324a 0%, #375569 52%, #72613b 100%);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
}

.permission-hero p {
  margin: 0 0 10px;
  color: rgba(255, 255, 255, 0.64);
  font-size: 12px;
  letter-spacing: 4px;
}

.permission-hero h2 {
  margin: 0 0 10px;
  font-size: 28px;
}

.permission-hero span {
  color: rgba(255, 255, 255, 0.8);
}

.permission-grid {
  display: grid;
  grid-template-columns: minmax(360px, 460px) minmax(0, 1fr);
  gap: 16px;
}

.grant-card,
.rules-card,
.assignment-card {
  border-radius: 8px;
}

.rule-item {
  padding: 14px 0;
  border-bottom: 1px solid #edf0f5;
}

.rule-item:last-child {
  border-bottom: 0;
}

.rule-item strong {
  display: block;
  margin-bottom: 6px;
  color: #1f2937;
}

.rule-item span {
  color: #6b7280;
  line-height: 1.7;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

@media (max-width: 960px) {
  .permission-hero,
  .card-head {
    align-items: stretch;
    flex-direction: column;
  }

  .permission-grid {
    grid-template-columns: 1fr;
  }
}
</style>
