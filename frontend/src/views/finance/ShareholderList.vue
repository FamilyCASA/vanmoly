<template>
  <div class="shareholder-list">
    <div class="page-header">
      <h2>股东信息</h2>
      <el-button type="primary" @click="showAddDialog = true">添加股东</el-button>
    </div>

    <el-card>
      <el-table :data="shareholders" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="shares" label="股份比例" width="120">
          <template #default="{ row }">
            {{ row.shares }}%
          </template>
        </el-table-column>
        <el-table-column prop="investment_amount" label="投资金额" width="150">
          <template #default="{ row }">
            ¥{{ row.investment_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="contact_phone" label="联系电话" width="150" />
        <el-table-column prop="role" label="角色" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editItem(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editingId ? '编辑股东' : '添加股东'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="股份比例">
          <el-input-number v-model="form.shares" :min="0" :max="100" :precision="2" />
        </el-form-item>
        <el-form-item label="投资金额">
          <el-input-number v-model="form.investment_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="普通股东" value="shareholder" />
            <el-option label="执行董事" value="director" />
            <el-option label="监事" value="supervisor" />
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
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const shareholders = ref([])
const showAddDialog = ref(false)
const editingId = ref(null)
const form = ref({
  name: '',
  shares: 0,
  investment_amount: 0,
  contact_phone: '',
  role: 'shareholder'
})

const loadData = async () => {
  try {
    const res = await request.get('/api/v3/finance/shareholders')
    shareholders.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const editItem = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  showAddDialog.value = true
}

const submitForm = async () => {
  try {
    if (editingId.value) {
      await request.put(`/api/v3/finance/shareholders/${editingId.value}`, form.value)
    } else {
      await request.post('/api/v3/finance/shareholders', form.value)
    }
    ElMessage.success('保存成功')
    showAddDialog.value = false
    editingId.value = null
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteItem = async (row) => {
  try {
    await request.delete(`/api/v3/finance/shareholders/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.shareholder-list { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
