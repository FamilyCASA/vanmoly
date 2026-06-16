<template>
  <div class="reimbursement-list">
    <div class="page-header">
      <h2>报销管理</h2>
      <el-button type="primary" @click="showAddDialog = true">新建报销</el-button>
    </div>

    <el-card>
      <el-table :data="reimbursements" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="报销标题" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ row.amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="120" />
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新建报销" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="报销标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="报销金额">
          <el-input-number v-model="form.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReimbursement">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const reimbursements = ref([])
const showAddDialog = ref(false)
const form = ref({
  title: '',
  amount: 0,
  description: ''
})

const loadData = async () => {
  try {
    const res = await request.get('/api/v3/finance/reimbursements')
    reimbursements.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const getStatusType = (status) => {
  const map = { '待审核': 'warning', '已通过': 'success', '已拒绝': 'danger' }
  return map[status] || 'info'
}

const submitReimbursement = async () => {
  try {
    await request.post('/api/v3/finance/reimbursements', form.value)
    ElMessage.success('提交成功')
    showAddDialog.value = false
    loadData()
  } catch (e) {
    ElMessage.error('提交失败')
  }
}

const viewDetail = (row) => {
  ElMessage.info('详情: ' + row.title)
}

const deleteItem = async (row) => {
  try {
    await request.delete(`/api/v3/finance/reimbursements/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.reimbursement-list { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
