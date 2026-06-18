<template>
  <div class="customer-manage">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新建客户
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">总客户</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.this_month || 0 }}</div>
          <div class="stat-label">本月新增</div>
        </el-card>
      </el-col>
      <el-col :span="4" v-for="(count, status) in stats.by_status" :key="status">
        <el-card class="stat-card">
          <div class="stat-value">{{ count }}</div>
          <div class="stat-label">{{ status }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="姓名/电话/楼盘" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option v-for="s in options.status_list" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.customer_type" placeholder="全部类型" clearable>
            <el-option v-for="t in options.customer_types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filterForm.source" placeholder="全部来源" clearable>
            <el-option v-for="s in options.sources" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <el-table :data="customers" v-loading="loading" border>
        <el-table-column prop="name" label="客户姓名" width="100" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="building_name" label="楼盘名称" width="150" />
        <el-table-column prop="house_type" label="户型" width="100" />
        <el-table-column prop="house_area" label="面积" width="80">
          <template #default="{ row }">
            {{ row.house_area ? row.house_area + '㎡' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="预算" width="100" />
        <el-table-column prop="source" label="来源" width="100" />
        <el-table-column prop="customer_type" label="客户类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.customer_type)">
              {{ row.customer_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="跟进人" width="100" />
        <el-table-column prop="follow_count" label="跟进" width="80">
          <template #default="{ row }">
            <el-button link type="primary" @click="openFollowDialog(row)">
              {{ row.follow_count || 0 }}次
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
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

    <!-- 客户表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑客户' : '新建客户'"
      width="700px"
    >
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="未知" value="未知" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="微信">
              <el-input v-model="form.wechat" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="楼盘名称">
              <el-input v-model="form.building_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="户型">
              <el-input v-model="form.house_type" placeholder="如：三室两厅" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="面积">
              <el-input-number v-model="form.house_area" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预算">
              <el-input v-model="form.budget" placeholder="如：20-30万" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="详细地址">
          <el-input v-model="form.detail_address" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="客户类型">
              <el-select v-model="form.customer_type" style="width: 100%">
                <el-option v-for="t in options.customer_types" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in options.status_list" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in options.priorities" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="来源">
              <el-select v-model="form.source" style="width: 100%">
                <el-option v-for="s in options.sources" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="跟进人">
              <el-select v-model="form.owner_id" style="width: 100%" clearable>
                <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="风格偏好">
          <el-input v-model="form.style_preference" />
        </el-form-item>

        <el-form-item label="装修需求">
          <el-input v-model="form.requirements" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 跟进记录对话框 -->
    <el-dialog v-model="followDialog.visible" title="跟进记录" width="600px">
      <div class="follow-list">
        <div v-for="f in followDialog.list" :key="f.id" class="follow-item">
          <div class="follow-header">
            <el-tag size="small">{{ f.follow_type }}</el-tag>
            <span class="follow-time">{{ formatDate(f.created_at) }}</span>
            <span class="follow-operator">{{ f.operator_name }}</span>
          </div>
          <div class="follow-content">{{ f.content }}</div>
          <div v-if="f.next_follow_at" class="follow-next">
            下次跟进：{{ formatDate(f.next_follow_at) }}
          </div>
        </div>
      </div>

      <el-divider>添加跟进</el-divider>

      <el-form :model="followForm" label-width="80px">
        <el-form-item label="跟进方式">
          <el-select v-model="followForm.follow_type" style="width: 100%">
            <el-option v-for="t in options.follow_types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容">
          <el-input v-model="followForm.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="下次跟进">
          <el-date-picker
            v-model="followForm.next_follow_at"
            type="datetime"
            style="width: 100%"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="followDialog.visible = false">关闭</el-button>
        <el-button type="primary" @click="handleAddFollow">添加记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

const loading = ref(false)
const customers = ref([])
const employees = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({
  keyword: '',
  status: '',
  customer_type: '',
  source: ''
})

const options = reactive({
  sources: [],
  customer_types: [],
  status_list: [],
  priorities: [],
  follow_types: []
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  name: '',
  phone: '',
  gender: '未知',
  wechat: '',
  building_name: '',
  house_type: '',
  house_area: null,
  budget: '',
  detail_address: '',
  customer_type: '已接触',
  status: '待跟进',
  priority: '普通',
  source: '',
  owner_id: null,
  style_preference: '',
  requirements: '',
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const formRef = ref(null)

const followDialog = reactive({
  visible: false,
  customerId: null,
  list: []
})

const followForm = reactive({
  follow_type: '电话',
  content: '',
  next_follow_at: null
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/customers', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status,
        customer_type: filterForm.customer_type,
        source: filterForm.source
      }
    })
    customers.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载客户列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await request.get('/customers/stats')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 加载选项
const loadOptions = async () => {
  try {
    const res = await request.get('/customers/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

// 加载员工列表
const loadEmployees = async () => {
  try {
    const res = await request.get('/employees')
    employees.value = res.items || []
  } catch (error) {
    console.error('加载员工列表失败', error)
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  filterForm.customer_type = ''
  filterForm.source = ''
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
      phone: '',
      gender: '未知',
      wechat: '',
      building_name: '',
      house_type: '',
      house_area: null,
      budget: '',
      detail_address: '',
      customer_type: '已接触',
      status: '待跟进',
      priority: '普通',
      source: '',
      owner_id: null,
      style_preference: '',
      requirements: '',
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
      await request.put(`/customers/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/customers', form)
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

// 删除客户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该客户吗？', '提示', { type: 'warning' })
    await request.delete(`/customers/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 打开跟进对话框
const openFollowDialog = async (row) => {
  followDialog.customerId = row.id
  followDialog.visible = true

  // 加载客户详情获取跟进记录
  try {
    const res = await request.get(`/customers/${row.id}`)
    followDialog.list = res.follows || []
  } catch (error) {
    console.error('加载跟进记录失败', error)
  }
}

// 添加跟进记录
const handleAddFollow = async () => {
  if (!followForm.content) {
    ElMessage.warning('请输入跟进内容')
    return
  }

  try {
    await request.post(`/customers/${followDialog.customerId}/follow`, followForm)
    ElMessage.success('添加成功')
    followForm.content = ''
    followForm.next_follow_at = null
    openFollowDialog({ id: followDialog.customerId })
    loadData()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 查看详情
const openDetail = (row) => {
  router.push(`/admin/customers/${row.id}`)
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = {
    '待跟进': 'info',
    '跟进中': 'warning',
    '已成交': 'success',
    '已流失': 'danger'
  }
  return map[status] || 'info'
}

// 获取类型标签类型
const getTypeTagType = (type) => {
  const map = {
    '已接触': 'info',
    '已拜访': 'info',
    '提案已经确认': 'warning',
    '跟进中': 'warning',
    '定金已收': 'success',
    '已成交': 'success'
  }
  return map[type] || 'info'
}

onMounted(() => {
  loadData()
  loadStats()
  loadOptions()
  loadEmployees()
})
</script>

<style scoped>
.customer-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.follow-list {
  max-height: 300px;
  overflow-y: auto;
}

.follow-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.follow-item:last-child {
  border-bottom: none;
}

.follow-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.follow-time {
  font-size: 12px;
  color: #999;
}

.follow-operator {
  font-size: 12px;
  color: #666;
}

.follow-content {
  color: #333;
  line-height: 1.5;
}

.follow-next {
  font-size: 12px;
  color: #409EFF;
  margin-top: 5px;
}
</style>
