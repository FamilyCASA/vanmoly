<template>
  <div class="supplier-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>供应商管理</h2>
        <span class="subtitle">管理物料供应商信息</span>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新建供应商
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total || 0 }}</div>
            <div class="stat-label">总供应商</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active || 0 }}</div>
            <div class="stat-label">合作中</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF7E6; color: #FA8C16;">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.paused || 0 }}</div>
            <div class="stat-label">暂停合作</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F9F0FF; color: #722ED1;">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.material_count || 0 }}</div>
            <div class="stat-label">关联物料</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="名称/联系人/电话"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="合作中" value="active" />
            <el-option label="暂停合作" value="paused" />
            <el-option label="已终止" value="terminated" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 供应商表格 -->
    <el-card shadow="never">
      <el-table :data="suppliers" v-loading="loading" style="width: 100%">
        <el-table-column label="供应商" min-width="200">
          <template #default="{ row }">
            <div class="supplier-info">
              <div class="supplier-name">{{ row.name }}</div>
              <div class="supplier-address" v-if="row.address">
                <el-icon><Location />{{ row.address }}</el-icon>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="联系人" width="150">
          <template #default="{ row }">
            <div>{{ row.contact_person || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="联系方式" width="180">
          <template #default="{ row }">
            <div v-if="row.phone">📞 {{ row.phone }}</div>
            <div v-if="row.email" class="text-muted">✉️ {{ row.email }}</div>
          </template>
        </el-table-column>

        <el-table-column label="物料数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.material_count || 0 }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="viewMaterials(row)">查看物料</el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button link>
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="status">
                    {{ row.status === 'active' ? '暂停合作' : '恢复合作' }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 供应商表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑供应商' : '新建供应商'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入供应商名称" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_person" placeholder="联系人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="电子邮箱">
          <el-input v-model="form.email" placeholder="邮箱地址" />
        </el-form-item>

        <el-form-item label="公司地址">
          <el-input v-model="form.address" type="textarea" rows="2" placeholder="详细地址" />
        </el-form-item>

        <el-form-item label="合作状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">合作中</el-radio>
            <el-radio value="paused">暂停合作</el-radio>
            <el-radio value="terminated">已终止</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="3" placeholder="其他备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, OfficeBuilding, CircleCheck, Timer, Box, Search, Location, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const suppliers = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  keyword: '',
  status: ''
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  status: 'active',
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }]
}

const formRef = ref(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/materials/suppliers', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status
      }
    })
    suppliers.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载供应商列表失败', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await request.get('/materials/supplier-stats')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  page.value = 1
  loadData()
}

// 打开对话框
const openDialog = (row = null) => {
  dialog.isEdit = !!row
  dialog.visible = true

  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, {
      id: null,
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      address: '',
      status: 'active',
      remark: ''
    })
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  dialog.loading = true
  try {
    if (dialog.isEdit) {
      await request.put(`/materials/suppliers/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/materials/suppliers', form)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    dialog.loading = false
  }
}

// 更多操作
const handleCommand = async (command, row) => {
  if (command === 'status') {
    const newStatus = row.status === 'active' ? 'paused' : 'active'
    try {
      await request.put(`/materials/suppliers/${row.id}`, { status: newStatus })
      ElMessage.success(newStatus === 'active' ? '已恢复合作' : '已暂停合作')
      loadData()
      loadStats()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除该供应商吗？', '提示', { type: 'warning' })
      await request.delete(`/materials/suppliers/${row.id}`)
      ElMessage.success('删除成功')
      loadData()
      loadStats()
    } catch (error) {
      if (error !== 'cancel') ElMessage.error('删除失败')
    }
  }
}

// 查看供应商物料
const viewMaterials = (row) => {
  window.location.href = `/#/materials?supplier_id=${row.id}`
}

// 状态显示
const getStatusType = (status) => {
  const map = {
    active: 'success',
    paused: 'warning',
    terminated: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    active: '合作中',
    paused: '暂停合作',
    terminated: '已终止'
  }
  return map[status] || status
}

// 日期格式化
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.supplier-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin-left: 8px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.filter-card {
  margin-bottom: 20px;
}

.supplier-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.supplier-name {
  font-weight: 500;
}

.supplier-address {
  font-size: 12px;
  color: #999;
}

.text-muted {
  color: #999;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>