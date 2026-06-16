<template>
  <div class="charter-manage">
    <div class="page-header">
      <h2>企业章程管理</h2>
      <el-button type="primary" @click="showAddDialog = true">新增章节</el-button>
    </div>

    <el-card>
      <el-table :data="chapters" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="chapter_number" label="章节号" width="100" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content" label="内容" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editItem(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editingId ? '编辑章程' : '新增章程'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="章节号">
          <el-input-number v-model="form.chapter_number" :min="1" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" rows="8" />
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

const chapters = ref([])
const showAddDialog = ref(false)
const editingId = ref(null)
const form = ref({
  chapter_number: 1,
  title: '',
  content: ''
})

const loadData = async () => {
  try {
    const res = await request.get('/api/v3/finance/charter')
    chapters.value = res.data || []
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
      await request.put(`/api/v3/finance/charter/${editingId.value}`, form.value)
    } else {
      await request.post('/api/v3/finance/charter', form.value)
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
    await request.delete(`/api/v3/finance/charter/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.charter-manage { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
