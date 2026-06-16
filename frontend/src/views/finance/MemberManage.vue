<template>
  <div class="member-manage">
    <div class="page-header">
      <h2>财务团队管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加成员</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="role in roles" :key="role.id">
        <el-card class="role-card">
          <template #header>
            <div class="role-header">
              <span>{{ role.role_name }}</span>
              <el-tag size="small">{{ role.members?.length || 0 }}人</el-tag>
            </div>
          </template>
          <div class="member-list">
            <div v-for="member in role.members" :key="member.id" class="member-item">
              <span class="member-name">{{ member.user_name }}</span>
              <span class="member-actions">
                <el-button size="small" text type="primary" @click="editMember(member)">编辑</el-button>
                <el-button size="small" text type="danger" @click="removeMember(member)">移除</el-button>
              </span>
            </div>
            <el-button size="small" plain style="width: 100%; margin-top: 10px;" @click="addMemberToRole(role)">
              + 添加成员
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showAddDialog" :title="editingId ? '编辑成员' : '添加成员'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择用户">
          <el-select v-model="form.user_id" filterable placeholder="搜索用户">
            <el-option v-for="u in users" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="财务角色">
          <el-select v-model="form.role_id" placeholder="选择角色">
            <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const roles = ref([])
const users = ref([])
const showAddDialog = ref(false)
const editingId = ref(null)
const form = ref({
  user_id: null,
  role_id: null
})

const loadData = async () => {
  try {
    const [rolesRes, usersRes] = await Promise.all([
      request.get('/api/v3/finance/roles'),
      request.get('/api/v3/finance/members/available')
    ])
    roles.value = rolesRes.data || []
    users.value = usersRes.data || []
  } catch (e) {
    console.error(e)
  }
}

const editMember = (member) => {
  editingId.value = member.id
  form.value = { user_id: member.user_id, role_id: member.role_id }
  showAddDialog.value = true
}

const submitForm = async () => {
  try {
    if (editingId.value) {
      await request.put(`/api/v3/finance/members/${editingId.value}`, form.value)
    } else {
      await request.post('/api/v3/finance/members', form.value)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    editingId.value = null
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const removeMember = async (member) => {
  try {
    await ElMessageBox.confirm('确认移除该成员?', '提示')
    await request.delete(`/api/v3/finance/members/${member.id}`)
    ElMessage.success('移除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('移除失败')
  }
}

const addMemberToRole = (role) => {
  editingId.value = null
  form.value = { user_id: null, role_id: role.id }
  showAddDialog.value = true
}

onMounted(loadData)
</script>

<style scoped>
.member-manage { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.role-card { margin-bottom: 20px; }
.role-header { display: flex; justify-content: space-between; align-items: center; }
.member-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
.member-name { font-weight: 500; }
.member-actions { display: flex; gap: 5px; }
</style>
