<template>
  <div class="supplier-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>供应链登记</h2>
        <span class="subtitle">管理供应商信息、关联采购合同与商品列表</span>
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
            placeholder="名称/品牌/联系人/电话"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="合作中" value="active" />
            <el-option label="暂停合作" value="paused" />
            <el-option label="已终止" value="terminated" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="filterForm.level" placeholder="全部等级" clearable style="width: 100px">
            <el-option label="A级" value="A" />
            <el-option label="B级" value="B" />
            <el-option label="C级" value="C" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 供应商表格 -->
    <el-card shadow="never">
      <el-table :data="suppliers" v-loading="loading" style="width: 100%" :row-class-name="rowClassName">
        <el-table-column label="编号" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.supplier_code || '-' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="供应商" min-width="200">
          <template #default="{ row }">
            <div class="supplier-info">
              <div class="supplier-name">{{ row.name }}</div>
              <div class="supplier-brand" v-if="row.brand">
                <el-icon><PriceTag /></el-icon> {{ row.brand }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="主要产品" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.main_products || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="联系人/电话" width="160">
          <template #default="{ row }">
            <div>{{ row.contact_person || '-' }}</div>
            <div class="text-muted" v-if="row.phone">{{ row.phone }}</div>
          </template>
        </el-table-column>

        <el-table-column label="供应链专员" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.specialist_name" size="small" type="success">{{ row.specialist_name }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column label="等级" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">{{ row.level || 'B' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="物料数" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.material_count || 0 }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="viewMaterials(row)">查看物料</el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button link>
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
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
      width="780px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商编号">
              <el-input v-model="form.supplier_code" placeholder="系统自动生成" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" placeholder="多个品牌用逗号分隔" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主要产品">
              <el-input v-model="form.main_products" placeholder="主营品类" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工厂地址">
              <el-input v-model="form.factory_address" placeholder="工厂详细地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="门店地址">
              <el-input v-model="form.store_address" placeholder="门店详细地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 联系信息 -->
        <el-divider content-position="left">联系信息</el-divider>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_person" placeholder="联系人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="电子邮箱">
              <el-input v-model="form.email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="供应链专员">
          <el-select
            v-model="form.specialist_id"
            filterable
            remote
            :remote-method="searchEmployees"
            :loading="empLoading"
            placeholder="搜索并选择员工"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="emp in employeeOptions"
              :key="emp.id"
              :label="emp.display_name || emp.username"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>

        <!-- 合作信息 -->
        <el-divider content-position="left">合作信息</el-divider>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="合作状态">
              <el-radio-group v-model="form.status">
                <el-radio value="active">合作中</el-radio>
                <el-radio value="paused">暂停</el-radio>
                <el-radio value="terminated">终止</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商等级">
              <el-select v-model="form.level" style="width: 100%">
                <el-option label="A级（战略合作伙伴）" value="A" />
                <el-option label="B级（常规合作）" value="B" />
                <el-option label="C级（备选供应商）" value="C" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="合作开始日期">
              <el-date-picker
                v-model="form.cooperation_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="结款方式">
              <el-select v-model="form.payment_method" placeholder="选择结款方式" style="width: 100%">
                <el-option label="月结30天" value="monthly_30" />
                <el-option label="月结60天" value="monthly_60" />
                <el-option label="月结90天" value="monthly_90" />
                <el-option label="预付款" value="prepaid" />
                <el-option label="货到付款" value="cod" />
                <el-option label="分期付款" value="installment" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="银行账户">
              <el-input v-model="form.bank_account" placeholder="银行账号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="开户行">
              <el-input v-model="form.bank_name" placeholder="开户行名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="税号">
          <el-input v-model="form.tax_number" placeholder="统一社会信用代码/税号" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="其他备注信息" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 物料查看抽屉 -->
    <el-drawer
      v-model="materialsDrawer.visible"
      :title="`${materialsDrawer.supplierName || ''} - 关联物料`"
      size="60%"
    >
      <div class="drawer-content">
        <div class="drawer-filter">
          <el-input
            v-model="materialsDrawer.keyword"
            placeholder="搜索物料名称"
            clearable
            style="width: 240px"
            @keyup.enter="loadMaterials"
          />
          <el-button type="primary" @click="loadMaterials" style="margin-left: 8px">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </div>
        <el-table :data="materialsDrawer.items" v-loading="materialsDrawer.loading" style="width: 100%; margin-top: 16px">
          <el-table-column label="物料名称" prop="name" min-width="180" />
          <el-table-column label="SKU" prop="sku_code" width="120" />
          <el-table-column label="分类" prop="category_level1" width="120" />
          <el-table-column label="单位" prop="unit" width="80" align="center" />
          <el-table-column label="单价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.price || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                {{ row.status === 'active' ? '在售' : '停售' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper" style="margin-top: 16px">
          <el-pagination
            v-model:current-page="materialsDrawer.page"
            v-model:page-size="materialsDrawer.pageSize"
            :total="materialsDrawer.total"
            :page-sizes="[20, 50, 100]"
            layout="total, prev, pager, next"
            @current-change="loadMaterials"
          />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, OfficeBuilding, CircleCheck, Timer, Box, Search,
  ArrowDown, PriceTag
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const suppliers = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filterForm = reactive({
  keyword: '',
  status: '',
  level: ''
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const defaultForm = {
  id: null,
  supplier_code: '',
  name: '',
  brand: '',
  main_products: '',
  factory_address: '',
  store_address: '',
  contact_person: '',
  phone: '',
  email: '',
  specialist_id: null,
  status: 'active',
  level: 'B',
  cooperation_date: '',
  payment_method: '',
  bank_account: '',
  bank_name: '',
  tax_number: '',
  address: '',
  remark: ''
}

const form = reactive({ ...defaultForm })

const rules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }]
}

const formRef = ref(null)

// 员工搜索
const employeeOptions = ref([])
const empLoading = ref(false)

const searchEmployees = async (query) => {
  if (!query) {
    employeeOptions.value = []
    return
  }
  empLoading.value = true
  try {
    const res = await request.get('/employees', { params: { keyword: query, page: 1, page_size: 20 } })
    const items = res.items || res.data?.items || res.data || []
    employeeOptions.value = items.map(e => ({ id: e.id, display_name: e.name || e.display_name || e.username }))
  } catch (e) {
    employeeOptions.value = []
  } finally {
    empLoading.value = false
  }
}

// 预加载已选专员名称
const preloadSpecialist = async (specialistId) => {
  if (!specialistId) return
  try {
    const res = await request.get(`/employees/${specialistId}`)
    const emp = res.data || res
    if (emp) {
      employeeOptions.value = [{ id: emp.id, display_name: emp.name || emp.display_name || emp.username }]
    }
  } catch (e) {
    // ignore
  }
}

// 物料抽屉
const materialsDrawer = reactive({
  visible: false,
  supplierId: null,
  supplierName: '',
  items: [],
  total: 0,
  page: 1,
  pageSize: 20,
  keyword: '',
  loading: false
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/materials/suppliers', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status,
        level: filterForm.level
      }
    })
    // @/utils/request 响应拦截器返回 response.data.data
    // 后端返回 { code:200, data:{ items:[...], total:N } }
    suppliers.value = res.items || res.data || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载供应商列表失败', error)
    ElMessage.error('加载失败')
    suppliers.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await request.get('/materials/supplier-stats')
    stats.value = res.data || res || {}
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadData()
}

// 重置筛选
const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  filterForm.level = ''
  page.value = 1
  loadData()
}

// 打开对话框
const openDialog = async (row = null) => {
  dialog.isEdit = !!row
  dialog.visible = true
  employeeOptions.value = []

  if (row) {
    Object.assign(form, row)
    if (row.specialist_id) {
      await preloadSpecialist(row.specialist_id)
    }
  } else {
    Object.assign(form, defaultForm)
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
  materialsDrawer.visible = true
  materialsDrawer.supplierId = row.id
  materialsDrawer.supplierName = row.name
  materialsDrawer.page = 1
  materialsDrawer.keyword = ''
  loadMaterials()
}

// 加载物料
const loadMaterials = async () => {
  materialsDrawer.loading = true
  try {
    const res = await request.get(`/materials/suppliers/${materialsDrawer.supplierId}/materials`, {
      params: {
        page: materialsDrawer.page,
        page_size: materialsDrawer.pageSize,
        keyword: materialsDrawer.keyword
      }
    })
    materialsDrawer.items = res.items || res.data || []
    materialsDrawer.total = res.total || 0
  } catch (error) {
    console.error('加载物料失败', error)
    materialsDrawer.items = []
  } finally {
    materialsDrawer.loading = false
  }
}

// 状态显示
const getStatusType = (status) => {
  const map = { active: 'success', paused: 'warning', terminated: 'info' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { active: '合作中', paused: '暂停合作', terminated: '已终止' }
  return map[status] || status
}

const getLevelType = (level) => {
  const map = { A: 'danger', B: 'warning', C: 'info' }
  return map[level] || 'info'
}

const rowClassName = ({ row }) => {
  if (row.status === 'paused') return 'row-paused'
  if (row.status === 'terminated') return 'row-terminated'
  return ''
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
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
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
  font-weight: 600;
  font-size: 15px;
}

.supplier-brand {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-muted {
  color: #999;
  font-size: 13px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.row-paused) {
  opacity: 0.7;
}

:deep(.row-terminated) {
  opacity: 0.5;
}

.drawer-content {
  padding: 0 20px 20px;
}

.drawer-filter {
  display: flex;
  align-items: center;
}
</style>
