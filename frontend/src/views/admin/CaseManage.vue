<template>
  <div class="case-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>案例管理</h2>
        <span class="subtitle">共 {{ pagination.total }} 个案例</span>
      </div>
      <div class="header-right">
        <el-button @click="showTemplateDialog = true">
          <el-icon><Document /></el-icon>模板库
        </el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>新建案例
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filterForm" inline class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="草稿" value="草稿" />
            <el-option label="已发布" value="已发布" />
            <el-option label="已下架" value="已下架" />
          </el-select>
        </el-form-item>
        <el-form-item label="小区">
          <el-select v-model="filterForm.building_id" placeholder="全部" clearable style="width: 150px">
            <el-option
              v-for="item in buildingOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="面积">
          <el-select v-model="filterForm.area_range" placeholder="全部" clearable style="width: 120px">
            <el-option label="< 80㎡" value="0-80" />
            <el-option label="80-120㎡" value="80-120" />
            <el-option label="120-160㎡" value="120-160" />
            <el-option label="> 160㎡" value="160-999" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格">
          <el-select v-model="filterForm.price_range" placeholder="全部" clearable style="width: 120px">
            <el-option label="< 20万" value="0-20" />
            <el-option label="20-30万" value="20-30" />
            <el-option label="30-50万" value="30-50" />
            <el-option label="> 50万" value="50-999" />
          </el-select>
        </el-form-item>
        <el-form-item label="套餐">
          <el-select v-model="filterForm.package_type" placeholder="全部" clearable style="width: 120px">
            <el-option label="全案A套餐" value="全案A" />
            <el-option label="全案B套餐" value="全案B" />
            <el-option label="全案S套餐" value="全案S" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="filterForm.responsible_id" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="item in employeeOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="置顶">
          <el-select v-model="filterForm.is_featured" placeholder="全部" clearable style="width: 100px">
            <el-option label="已置顶" :value="true" />
            <el-option label="未置顶" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="标题/小区/编号"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 批量操作栏 -->
    <div class="batch-bar">
      <el-dropdown @command="handleBatchCommand" :disabled="selectedCases.length === 0">
        <el-button :disabled="selectedCases.length === 0">
          批量操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="publish">批量发布</el-dropdown-item>
            <el-dropdown-item command="unpublish">批量下架</el-dropdown-item>
            <el-dropdown-item command="feature">批量置顶</el-dropdown-item>
            <el-dropdown-item command="unfeature">批量取消置顶</el-dropdown-item>
            <el-dropdown-item command="delete" divided>批量删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <div class="sort-options">
        <span>排序：</span>
        <el-select v-model="sortBy" style="width: 140px" @change="handleSearch">
          <el-option label="最新更新" value="updated_at" />
          <el-option label="发布时间" value="publish_time" />
          <el-option label="浏览量" value="view_count" />
          <el-option label="订阅数" value="subscription_count" />
        </el-select>
        <el-switch
          v-model="sortOrder"
          active-value="desc"
          inactive-value="asc"
          active-text="降序"
          inactive-text="升序"
          @change="handleSearch"
        />
      </div>
    </div>

    <!-- 案例列表 -->
    <el-table
      :data="cases"
      v-loading="loading"
      @selection-change="handleSelectionChange"
      class="case-table"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column label="案例" min-width="280">
        <template #default="{ row }">
          <div class="case-info">
            <el-image
              :src="row.cover_image || '/placeholder-case.jpg'"
              class="case-cover"
              fit="cover"
            />
            <div class="case-meta">
              <div class="case-title">{{ row.title }}</div>
              <div class="case-no">{{ row.case_no || row.id }}</div>
              <div class="case-tags">
                <el-tag size="small" v-if="row.style">{{ row.style }}</el-tag>
                <el-tag size="small" v-if="row.house_type">{{ row.house_type }}</el-tag>
              </div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="小区/户型" width="150">
        <template #default="{ row }">
          <div>{{ row.location || '-' }}</div>
          <div class="text-gray">{{ row.house_type || '-' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="面积/总价" width="120">
        <template #default="{ row }">
          <div>{{ row.area ? row.area + '㎡' : '-' }}</div>
          <div class="text-primary">{{ row.total_price ? '¥' + formatPrice(row.total_price) : '-' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="套餐配置" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.package_type" type="info" size="small">{{ row.package_type }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <div class="status-cell">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
            <el-icon v-if="row.is_featured" class="feature-icon" title="已置顶"><Star /></el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="数据" width="150">
        <template #default="{ row }">
          <div class="stats-row">
            <span title="浏览"><el-icon><View /></el-icon>{{ row.view_count || 0 }}</span>
            <span title="订阅"><el-icon><Bell /></el-icon>{{ row.subscription_count || 0 }}</span>
            <span title="留资"><el-icon><User /></el-icon>{{ row.lead_count || 0 }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="100">
        <template #default="{ row }">
          {{ getEmployeeName(row.responsible_id) }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleView(row)">查看</el-button>
          <el-button type="success" link @click="handleSlide(row)">幻灯片</el-button>
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-dropdown @command="(cmd) => handleMoreCommand(cmd, row)">
            <el-button type="primary" link>更多<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="copy">复制</el-dropdown-item>
                <el-dropdown-item command="template">存为模板</el-dropdown-item>
                <el-dropdown-item v-if="row.status === '草稿'" command="publish">发布</el-dropdown-item>
                <el-dropdown-item v-if="row.status === '已发布'" command="unpublish">下架</el-dropdown-item>
                <el-dropdown-item v-if="!row.is_featured" command="feature"><el-icon><Star /></el-icon>置顶</el-dropdown-item>
                <el-dropdown-item v-if="row.is_featured" command="unfeature"><el-icon><StarFilled /></el-icon>取消置顶</el-dropdown-item>
                <el-dropdown-item divided command="delete" style="color: #f56c6c">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 模板库弹窗 -->
    <el-dialog v-model="showTemplateDialog" title="案例模板库" width="800px">
      <el-table :data="templates" v-loading="templateLoading">
        <el-table-column prop="template_name" label="模板名称" />
        <el-table-column prop="package_type" label="套餐类型" width="120" />
        <el-table-column label="价格区间" width="150">
          <template #default="{ row }">
            {{ row.price_min ? '¥' + formatPrice(row.price_min) : '-' }}
            ~
            {{ row.price_max ? '¥' + formatPrice(row.price_max) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="useTemplate(row)">使用</el-button>
            <el-button link @click="previewTemplate(row)">预览</el-button>
            <el-button link type="danger" @click="deleteTemplate(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, ArrowDown, View, Bell, User, Document, Star, StarFilled
} from '@element-plus/icons-vue'
import { getCases, deleteCase as deleteCaseApi, batchOperation, getTemplates } from '@/api/case'
import { getBuildings } from '@/api/building'
import { getEmployees } from '@/api/employee'

const router = useRouter()

// 加载状态
const loading = ref(false)
const templateLoading = ref(false)

// 数据列表
const cases = ref([])
const templates = ref([])
const buildingOptions = ref([])
const employeeOptions = ref([])
const selectedCases = ref([])

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 排序
const sortBy = ref('updated_at')
const sortOrder = ref('desc')

// 筛选表单
const filterForm = reactive({
  status: '',
  building_id: '',
  area_range: '',
  price_range: '',
  package_type: '',
  responsible_id: '',
  is_featured: '',
  keyword: ''
})

// 弹窗控制
const showTemplateDialog = ref(false)

// 获取案例列表
const fetchCases = async () => {
  loading.value = true
  try {
    // 过滤掉空字符串/null/undefined，避免后端误解析（如 is_featured='' 被 Flask bool 解析为 True）
    const rawParams = {
      page: pagination.page,
      page_size: pagination.page_size,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      ...filterForm
    }
    const params = Object.fromEntries(
      Object.entries(rawParams).filter(([, v]) => v !== '' && v !== null && v !== undefined)
    )
    
    // 处理面积区间
    if (filterForm.area_range) {
      const [min, max] = filterForm.area_range.split('-')
      params.area_min = parseFloat(min)
      params.area_max = parseFloat(max)
      delete params.area_range
    }
    
    // 处理价格区间
    if (filterForm.price_range) {
      const [min, max] = filterForm.price_range.split('-')
      params.price_min = parseFloat(min) * 10000
      params.price_max = parseFloat(max) * 10000
      delete params.price_range
    }
    
    const res = await getCases(params)
    cases.value = res?.items || []
    pagination.total = res?.total || 0
  } catch (error) {
    console.error('获取案例失败:', error)
    ElMessage.error('获取案例列表失败')
  } finally {
    loading.value = false
  }
}

// 获取模板列表
const fetchTemplates = async () => {
  templateLoading.value = true
  try {
    const res = await getTemplates()
    templates.value = res || []
  } catch (error) {
    console.error('获取模板失败:', error)
  } finally {
    templateLoading.value = false
  }
}

// 获取楼盘选项
const fetchBuildings = async () => {
  try {
    const res = await getBuildings({ page_size: 100 })
    buildingOptions.value = res?.items || []
  } catch (error) {
    console.error('获取楼盘失败:', error)
  }
}

// 获取员工选项
const fetchEmployees = async () => {
  try {
    const res = await getEmployees({ page_size: 100 })
    employeeOptions.value = res?.items || []
  } catch (error) {
    console.error('获取员工失败:', error)
  }
}

// 获取员工姓名
const getEmployeeName = (id) => {
  const emp = employeeOptions.value.find(e => e.id === id)
  return emp?.name || '-'
}

// 状态标签类型
const getStatusType = (status) => {
  const map = {
    '草稿': 'info',
    '已发布': 'success',
    '已下架': 'warning'
  }
  return map[status] || 'info'
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0'
  const num = parseFloat(price)
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchCases()
}

// 重置筛选
const handleReset = () => {
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = ''
  })
  handleSearch()
}

// 多选变化
const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

// 批量操作
const handleBatchCommand = async (command) => {
  const ids = selectedCases.value.map(item => item.id)
  
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${ids.length} 个案例吗？`,
        '确认删除',
        { type: 'warning' }
      )
      await batchOperation({ ids, action: 'delete' })
      ElMessage.success('删除成功')
      fetchCases()
    } catch {
      // 取消
    }
  } else {
    try {
      await batchOperation({ ids, action: command })
      ElMessage.success('操作成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }
}

// 更多操作
const handleMoreCommand = async (command, row) => {
  if (command === 'view') {
    window.open(`/cases/${row.id}`, '_blank')
  } else if (command === 'edit') {
    router.push(`/admin/cases/edit/${row.id}`)
  } else if (command === 'copy') {
    // 复制案例
    try {
      await batchOperation({ ids: [row.id], action: 'copy' })
      ElMessage.success('复制成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('复制失败')
    }
  } else if (command === 'template') {
    // 存为模板
    // TODO: 实现存为模板功能
    ElMessage.info('功能开发中')
  } else if (command === 'publish') {
    try {
      await batchOperation({ ids: [row.id], action: 'publish' })
      ElMessage.success('发布成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('发布失败')
    }
  } else if (command === 'unpublish') {
    try {
      await batchOperation({ ids: [row.id], action: 'unpublish' })
      ElMessage.success('下架成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('下架失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除该案例吗？', '确认删除', { type: 'warning' })
      await deleteCaseApi(row.id)
      ElMessage.success('删除成功')
      fetchCases()
    } catch {
      // 取消
    }
  } else if (command === 'feature') {
    try {
      await toggleFeature(row.id, true)
      ElMessage.success('置顶成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('置顶失败')
    }
  } else if (command === 'unfeature') {
    try {
      await toggleFeature(row.id, false)
      ElMessage.success('取消置顶成功')
      fetchCases()
    } catch (error) {
      ElMessage.error('取消置顶失败')
    }
  }
}

// 查看
const handleView = (row) => {
  window.open(`/cases/${row.id}`, '_blank')
}

// 编辑
const handleEdit = (row) => {
  router.push(`/admin/cases/edit/${row.id}`)
}

// 幻灯片演示
const handleSlide = (row) => {
  window.open(`/slides/${row.id}`, '_blank')
}

// 置顶/取消置顶
const toggleFeature = async (id, is_featured) => {
  const { data } = await fetch(`/api/v3/cases/${id}/feature`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ is_featured })
  })
  const res = await data.json()
  if (res.code !== 200) throw new Error(res.message)
  return res.data
}

// 创建
const handleCreate = () => {
  router.push('/admin/cases/create')
}

// 使用模板
const useTemplate = (template) => {
  router.push({
    path: '/admin/cases/create',
    query: { template_id: template.id }
  })
}

// 预览模板
const previewTemplate = (template) => {
  // TODO: 实现模板预览
  ElMessage.info('功能开发中')
}

// 删除模板
const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '确认删除', { type: 'warning' })
    // TODO: 实现删除模板API
    ElMessage.success('删除成功')
    fetchTemplates()
  } catch {
    // 取消
  }
}

// 分页变化
const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchCases()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchCases()
}

onMounted(() => {
  fetchCases()
  fetchBuildings()
  fetchEmployees()
  fetchTemplates()
})
</script>

<style scoped lang="scss">
.case-manage {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  .header-left {
    display: flex;
    align-items: baseline;
    gap: 12px;
    
    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
    
    .subtitle {
      color: #909399;
      font-size: 14px;
    }
  }
  
  .header-right {
    display: flex;
    gap: 12px;
  }
}

.filter-card {
  margin-bottom: 16px;
  
  .filter-form {
    :deep(.el-form-item) {
      margin-bottom: 0;
      margin-right: 16px;
    }
  }
}

.batch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .sort-options {
    display: flex;
    align-items: center;
    gap: 12px;
    
    span {
      color: #606266;
      font-size: 14px;
    }
  }
}

.case-table {
  .case-info {
    display: flex;
    gap: 12px;
    align-items: center;
    
    .case-cover {
      width: 80px;
      height: 60px;
      border-radius: 4px;
      flex-shrink: 0;
    }
    
    .case-meta {
      flex: 1;
      min-width: 0;
      
      .case-title {
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .case-no {
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }
      
      .case-tags {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
      }
    }
  }
  
  .text-gray {
    color: #909399;
    font-size: 13px;
  }
  
  .text-primary {
    color: #8B5A2B;
    font-weight: 500;
  }
  
  .stats-row {
    display: flex;
    gap: 16px;
    
    span {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #606266;
      
      .el-icon {
        font-size: 14px;
      }
    }
  }
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  
  .feature-icon {
    color: #f7ba2a;
    font-size: 16px;
    animation: twinkle 2s ease-in-out infinite;
  }
}

@keyframes twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
