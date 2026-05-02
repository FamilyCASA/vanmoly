<template>
  <div class="store-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">分店管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增分店
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索分店编码/名称"
          style="width: 200px"
          clearable
          @clear="loadStores"
        />
        <el-select
          v-model="searchForm.status"
          placeholder="状态"
          style="width: 120px"
          clearable
          @clear="loadStores"
        >
          <el-option label="运营中" value="active" />
          <el-option label="已停用" value="inactive" />
          <el-option label="已删除" value="deleted" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="loadStores">查询</el-button>
        <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="stores"
        v-loading="loading"
        stripe
        border
        style="margin-top: 20px"
      >
        <el-table-column prop="code" label="分店编码" width="100" />
        <el-table-column prop="name" label="分店名称" min-width="150" />
        <el-table-column label="地址" min-width="200">
          <template #default="{ row }">
            {{ row.province }}{{ row.city }}{{ row.district }}{{ row.address }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column label="店长" width="100">
          <template #default="{ row }">
            {{ row.manager_name || '未指定' }}
          </template>
        </el-table-column>
        <el-table-column label="数据库状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.db_status === 'initialized' ? 'success' : row.db_status === 'failed' ? 'danger' : 'warning'"
              size="small"
            >
              {{ row.db_status === 'initialized' ? '已初始化' : row.db_status === 'failed' ? '失败' : '待初始化' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'info'"
              size="small"
            >
              {{ row.status === 'active' ? '运营中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ row.created_at }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="loadStores"
        @current-change="loadStores"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分店编码" prop="code">
              <el-input
                v-model="form.code"
                placeholder="如：CD001"
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分店名称" prop="name">
              <el-input v-model="form.name" placeholder="如：成都旗舰店" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="省份">
              <el-input v-model="form.province" placeholder="省" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="城市">
              <el-input v-model="form.city" placeholder="市" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="区县">
              <el-input v-model="form.district" placeholder="区/县" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="详细地址">
          <el-input v-model="form.address" placeholder="详细地址" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="分店联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店长">
              <el-select
                v-model="form.manager_id"
                placeholder="选择店长"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="emp in managers"
                  :key="emp.id"
                  :label="emp.name + (emp.department_name ? ' - ' + emp.department_name : '')"
                  :value="emp.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开业日期">
              <el-date-picker
                v-model="form.opening_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="营业时间">
              <el-input v-model="form.business_hours" placeholder="如：09:00-21:00" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">运营中</el-radio>
            <el-radio value="inactive">已停用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="分店描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="分店简介"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="分店详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="分店编码">{{ currentStore.code }}</el-descriptions-item>
        <el-descriptions-item label="分店名称">{{ currentStore.name }}</el-descriptions-item>
        <el-descriptions-item label="租户ID">{{ currentStore.tenant_id }}</el-descriptions-item>
        <el-descriptions-item label="数据库状态">
          <el-tag :type="currentStore.db_status === 'initialized' ? 'success' : 'warning'" size="small">
            {{ currentStore.db_status === 'initialized' ? '已初始化' : '待初始化' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="省份">{{ currentStore.province }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ currentStore.city }}</el-descriptions-item>
        <el-descriptions-item label="区县">{{ currentStore.district }}</el-descriptions-item>
        <el-descriptions-item label="详细地址" :span="2">{{ currentStore.address }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentStore.phone }}</el-descriptions-item>
        <el-descriptions-item label="店长">{{ currentStore.manager_name || '未指定' }}</el-descriptions-item>
        <el-descriptions-item label="开业日期">{{ currentStore.opening_date }}</el-descriptions-item>
        <el-descriptions-item label="营业时间">{{ currentStore.business_hours }}</el-descriptions-item>
        <el-descriptions-item label="员工数">{{ currentStore.employee_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentStore.status === 'active' ? 'success' : 'info'" size="small">
            {{ currentStore.status === 'active' ? '运营中' : '已停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentStore.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ currentStore.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="分店描述" :span="2">{{ currentStore.description }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button type="primary" @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 数据
const loading = ref(false)
const stores = ref([])
const managers = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const currentStore = ref({})

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive({
  code: '',
  name: '',
  province: '',
  city: '',
  district: '',
  address: '',
  phone: '',
  manager_id: null,
  opening_date: null,
  business_hours: '',
  description: '',
  status: 'active'
})

const rules = {
  code: [
    { required: true, message: '请输入分店编码', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入分店名称', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => isEdit.value ? '编辑分店' : '新增分店')

// 方法
const loadStores = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const res = await request.get('/stores', { params })
    if (res.list !== undefined) {
      stores.value = res.list
      pagination.total = res.total
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载分店列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadManagers = async () => {
  try {
    // 加载所有在职员工供选择店长（不限role，因为店长可能在各种岗位）
    const res = await request.get('/employees', { params: { page_size: 200, status: 'active' } })
    if (res.items !== undefined) {
      managers.value = res.items || []
    } else {
      ElMessage.error(res.message || '加载员工列表失败')
    }
  } catch (error) {
    console.error('加载员工列表失败:', error)
    ElMessage.error('加载员工列表失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    code: row.code,
    name: row.name,
    province: row.province || '',
    city: row.city || '',
    district: row.district || '',
    address: row.address || '',
    phone: row.phone || '',
    manager_id: row.manager_id,
    opening_date: row.opening_date,
    business_hours: row.business_hours || '',
    description: row.description || '',
    status: row.status
  })
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await request.get(`/stores/${row.id}`)
    if (res) {
      currentStore.value = res
      detailVisible.value = true
    }
  } catch (error) {
    console.error('加载分店详情失败:', error)
    ElMessage.error('加载失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分店"${row.name}"吗？删除后不可恢复`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await request.delete(`/stores/${row.id}`)
    if (res) {
      ElMessage.success('删除成功')
      loadStores()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除分店失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  submitting.value = true
  try {
    let res
    if (isEdit.value) {
      res = await request.put(`/stores/${form.id}`, form)
    } else {
      res = await request.post('/stores', form)
    }

    if (res) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadStores()
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    code: '',
    name: '',
    province: '',
    city: '',
    district: '',
    address: '',
    phone: '',
    manager_id: null,
    opening_date: null,
    business_hours: '',
    description: '',
    status: 'active'
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  pagination.page = 1
  loadStores()
}

// 生命周期
onMounted(() => {
  loadStores()
  loadManagers()
})
</script>

<style scoped>
.store-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 18px;
  font-weight: 600;
}

.search-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
