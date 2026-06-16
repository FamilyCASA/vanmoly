<template>
  <div class="member-manage">
    <div class="page-header">
      <h2>财务团队管理</h2>
      <el-button type="primary" @click="openAddDialog" :icon="Plus">添加成员</el-button>
    </div>

    <!-- 角色卡片 -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="8" v-for="role in roles" :key="role.id">
        <el-card shadow="never" class="role-card">
          <template #header>
            <div class="role-header">
              <span class="role-name">{{ role.role_name }}</span>
              <el-tag size="small" :type="roleTagType(role.role_code)">
                {{ role.members?.length || 0 }}人
              </el-tag>
            </div>
          </template>

          <div class="member-list">
            <div v-for="member in (role.members || [])" :key="member.id" class="member-item">
              <div class="member-info">
                <span class="member-name">{{ member.user_name || '用户#' + member.user_id }}</span>
                <span class="member-date">{{ member.created_at?.slice(0, 10) || '—' }}</span>
              </div>
              <div class="member-actions">
                <el-button size="small" text type="primary" @click="openEditDialog(member)">编辑</el-button>
                <el-button size="small" text type="danger" @click="handleRemove(member)">移除</el-button>
              </div>
            </div>
            <el-button
              size="small"
              plain
              style="width: 100%; margin-top: 10px"
              @click="openAddToRoleDialog(role)"
            >
              + 添加成员
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑成员' : '添加成员'"
      width="480px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="选择用户" prop="user_id">
          <el-select
            v-model="form.user_id"
            filterable
            placeholder="搜索用户"
            style="width: 100%"
          >
            <el-option
              v-for="u in availableUsers"
              :key="u.id"
              :label="u.name + '（' + u.employee_id + '）'"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="财务角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="选择角色" style="width: 100%">
            <el-option
              v-for="r in roles"
              :key="r.id"
              :label="r.role_name + '（' + r.role_code + '）'"
              :value="r.id"
            />
          </el-select>
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

const roles = ref([])
const availableUsers = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  user_id: null,
  role_id: null
})

const rules = {
  user_id: [{ required: true, message: '请选择用户', trigger: 'change' }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const roleTagType = (code) => {
  const map = {
    finance_super_admin: 'danger',
    finance_admin: 'warning',
    finance_viewer: 'info',
    finance_operator: 'success'
  }
  return map[code] || 'info'
}

const loadData = async () => {
  try {
    const [rolesData, usersData] = await Promise.all([
      financeAPI.getRoles(),
      financeAPI.getAvailableUsers()
    ])
    roles.value = rolesData || []
    availableUsers.value = usersData || []
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  }
}

const openAddDialog = () => {
  editingId.value = null
  form.value = { user_id: null, role_id: null }
  dialogVisible.value = true
}

const openAddToRoleDialog = (role) => {
  editingId.value = null
  form.value = { user_id: null, role_id: role.id }
  dialogVisible.value = true
}

const openEditDialog = (member) => {
  editingId.value = member.id
  form.value = { user_id: member.user_id, role_id: member.role_id }
  dialogVisible.value = true
}

const resetForm = () => { formRef.value?.resetFields() }

const submitForm = async () => {
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    if (editingId.value) {
      await financeAPI.updateMember(editingId.value, form.value)
    } else {
      await financeAPI.createMember(form.value)
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

const handleRemove = async (member) => {
  try {
    await ElMessageBox.confirm(
      `确认移除成员「${member.user_name || '用户#' + member.user_id}」？`,
      '移除确认',
      { confirmButtonText: '确认移除', cancelButtonText: '取消', type: 'warning' }
    )
    await financeAPI.deleteMember(member.id)
    ElMessage.success('已移除')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('移除失败')
    }
  }
}

onMounted(loadData)
</script>

<style scoped>
.member-manage { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; font-size: 20px; }

.role-card { min-height: 200px; }
.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.role-name { font-weight: 600; font-size: 14px; }

.member-list { min-height: 60px; }
.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.member-item:last-of-type { border-bottom: none; }
.member-info { display: flex; flex-direction: column; gap: 2px; }
.member-name { font-size: 13px; font-weight: 500; color: #303133; }
.member-date { font-size: 11px; color: #909399; }
.member-actions { display: flex; gap: 2px; }
</style>
