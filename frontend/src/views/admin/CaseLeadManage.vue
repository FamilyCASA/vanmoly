<template>
  <div class="case-lead-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>客资管理</h2>
        <span class="subtitle">共 {{ pagination.total }} 条留资</span>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>导出Excel
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">总留资</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value text-warning">{{ stats.new || 0 }}</div>
          <div class="stat-label">待跟进</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value text-primary">{{ stats.contacted || 0 }}</div>
          <div class="stat-label">已联系</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value text-success">{{ stats.converted || 0 }}</div>
          <div class="stat-label">已转化</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value">{{ stats.today || 0 }}</div>
          <div class="stat-label">今日新增</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card" shadow="never">
          <div class="stat-value">{{ stats.week || 0 }}</div>
          <div class="stat-label">本周新增</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filterForm" inline class="filter-form">
        <el-form-item label="案例">
          <el-select v-model="filterForm.case_id" placeholder="全部案例" clearable style="width: 180px" filterable>
            <el-option
              v-for="item in caseOptions"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待跟进" value="new" />
            <el-option label="已联系" value="contacted" />
            <el-option label="已转化" value="converted" />
            <el-option label="无效" value="invalid" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filterForm.source" placeholder="全部来源" clearable style="width: 140px">
            <el-option label="页面浏览" value="view_detail" />
            <el-option label="PDF下载" value="pdf_download" />
            <el-option label="在线咨询" value="consult" />
            <el-option label="案例订阅" value="subscribe" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="姓名/手机号"
            clearable
            style="width: 160px"
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

    <!-- 数据表格 -->
    <el-table :data="leads" v-loading="loading" class="lead-table" border>
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column label="客户信息" min-width="180">
        <template #default="{ row }">
          <div class="customer-info">
            <div class="customer-name">{{ row.name || '未填写' }}</div>
            <div class="customer-phone">{{ row.phone || '-' }}</div>
            <div v-if="row.wechat" class="customer-wechat">
              <el-icon><ChatDotRound /></el-icon>{{ row.wechat }}
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="来源案例" min-width="200">
        <template #default="{ row }">
          <div v-if="row.case_id" class="case-info">
            <el-link type="primary" @click="viewCase(row.case_id)">
              {{ getCaseTitle(row.case_id) }}
            </el-link>
          </div>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="来源渠道" width="120">
        <template #default="{ row }">
          <el-tag :type="getSourceType(row.source)" size="small">
            {{ getSourceLabel(row.source) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="留言" min-width="150">
        <template #default="{ row }">
          <el-tooltip v-if="row.message" :content="row.message" placement="top">
            <div class="message-text">{{ row.message }}</div>
          </el-tooltip>
          <span v-else class="text-gray">-</span>
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="150">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="跟进记录" min-width="150">
        <template #default="{ row }">
          <div v-if="row.remark" class="remark-text">{{ row.remark }}</div>
          <span v-else class="text-gray">暂无记录</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button 
            v-if="row.status === 'new'" 
            type="primary" 
            link 
            @click="handleContact(row)"
          >
            标记联系
          </el-button>
          <el-button 
            v-if="row.status === 'contacted'" 
            type="success" 
            link 
            @click="handleConvert(row)"
          >
            标记转化
          </el-button>
          <el-button type="primary" link @click="handleEditRemark(row)">备注</el-button>
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

    <!-- 联系/转化弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="dialogForm" label-position="top">
        <el-form-item label="客户">
          <div>{{ currentLead?.name }} {{ currentLead?.phone }}</div>
        </el-form-item>
        <el-form-item label="跟进备注">
          <el-input 
            v-model="dialogForm.remark" 
            type="textarea" 
            :rows="4" 
            placeholder="记录跟进情况..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDialog" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Search, ChatDotRound } from '@element-plus/icons-vue'
import { getAllLeads, markLeadContacted, markLeadConverted } from '@/api/case'
import { getCases } from '@/api/case'

const router = useRouter()

// 状态
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentLead = ref(null)
const dialogAction = ref('')

// 数据
const leads = ref([])
const caseOptions = ref([])
const stats = reactive({
  total: 0,
  new: 0,
  contacted: 0,
  converted: 0,
  today: 0,
  week: 0
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 筛选
const filterForm = reactive({
  case_id: '',
  status: '',
  source: '',
  date_range: [],
  keyword: ''
})

// 弹窗表单
const dialogForm = reactive({
  remark: ''
})

// 获取客资列表
const fetchLeads = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filterForm
    }
    
    // 处理日期范围
    if (filterForm.date_range && filterForm.date_range.length === 2) {
      params.date_from = filterForm.date_range[0]?.toISOString()
      params.date_to = filterForm.date_range[1]?.toISOString()
    }
    
    const res = await getAllLeads(params)
    leads.value = res?.items || []
    pagination.total = res?.total || 0
    
    // 计算统计
    calculateStats()
  } catch (error) {
    console.error('获取客资失败:', error)
    ElMessage.error('获取客资列表失败')
  } finally {
    loading.value = false
  }
}

// 获取案例选项
const fetchCases = async () => {
  try {
    const res = await getCases({ page_size: 100, status: '已发布' })
    caseOptions.value = res?.items || []
  } catch (error) {
    console.error('获取案例失败:', error)
  }
}

// 计算统计
const calculateStats = () => {
  stats.total = pagination.total
  stats.new = leads.value.filter(l => l.status === 'new').length
  stats.contacted = leads.value.filter(l => l.status === 'contacted').length
  stats.converted = leads.value.filter(l => l.status === 'converted').length
  
  const today = new Date().toDateString()
  stats.today = leads.value.filter(l => new Date(l.created_at).toDateString() === today).length
  
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  stats.week = leads.value.filter(l => new Date(l.created_at) >= weekAgo).length
}

// 获取案例标题
const getCaseTitle = (caseId) => {
  const c = caseOptions.value.find(item => item.id === caseId)
  return c?.title || '未知案例'
}

// 来源标签
const getSourceLabel = (source) => {
  const map = {
    'view_detail': '页面浏览',
    'pdf_download': 'PDF下载',
    'consult': '在线咨询',
    'subscribe': '案例订阅'
  }
  return map[source] || source
}

const getSourceType = (source) => {
  const map = {
    'view_detail': 'info',
    'pdf_download': 'warning',
    'consult': 'success',
    'subscribe': 'primary'
  }
  return map[source] || 'info'
}

// 状态标签
const getStatusLabel = (status) => {
  const map = {
    'new': '待跟进',
    'contacted': '已联系',
    'converted': '已转化',
    'invalid': '无效'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    'new': 'warning',
    'contacted': 'primary',
    'converted': 'success',
    'invalid': 'info'
  }
  return map[status] || 'info'
}

// 格式化日期时间
const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLeads()
}

// 重置
const handleReset = () => {
  Object.keys(filterForm).forEach(key => {
    if (key === 'date_range') {
      filterForm[key] = []
    } else {
      filterForm[key] = ''
    }
  })
  handleSearch()
}

// 查看案例
const viewCase = (caseId) => {
  window.open(`/cases/${caseId}`, '_blank')
}

// 标记联系
const handleContact = (row) => {
  currentLead.value = row
  dialogAction.value = 'contact'
  dialogTitle.value = '标记已联系'
  dialogForm.remark = row.remark || ''
  dialogVisible.value = true
}

// 标记转化
const handleConvert = (row) => {
  currentLead.value = row
  dialogAction.value = 'convert'
  dialogTitle.value = '标记已转化'
  dialogForm.remark = row.remark || ''
  dialogVisible.value = true
}

// 编辑备注
const handleEditRemark = (row) => {
  currentLead.value = row
  dialogAction.value = 'remark'
  dialogTitle.value = '编辑备注'
  dialogForm.remark = row.remark || ''
  dialogVisible.value = true
}

// 提交弹窗
const submitDialog = async () => {
  submitting.value = true
  try {
    if (dialogAction.value === 'contact') {
      await markLeadContacted(currentLead.value.id, { remark: dialogForm.remark })
      ElMessage.success('标记成功')
    } else if (dialogAction.value === 'convert') {
      await markLeadConverted(currentLead.value.id)
      if (dialogForm.remark) {
        await markLeadContacted(currentLead.value.id, { remark: dialogForm.remark })
      }
      ElMessage.success('标记成功')
    } else if (dialogAction.value === 'remark') {
      await markLeadContacted(currentLead.value.id, { remark: dialogForm.remark })
      ElMessage.success('保存成功')
    }
    
    dialogVisible.value = false
    fetchLeads()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 分页
const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchLeads()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchLeads()
}

onMounted(() => {
  fetchLeads()
  fetchCases()
})
</script>

<style scoped lang="scss">
.case-lead-manage {
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
}

.stats-row {
  margin-bottom: 24px;

  .stat-card {
    text-align: center;

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;

      &.text-warning {
        color: #e6a23c;
      }

      &.text-primary {
        color: #8B5A2B;
      }

      &.text-success {
        color: #67c23a;
      }
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
    }
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

.lead-table {
  .customer-info {
    .customer-name {
      font-weight: 500;
      font-size: 14px;
      margin-bottom: 4px;
    }

    .customer-phone {
      font-size: 13px;
      color: #606266;
      margin-bottom: 4px;
    }

    .customer-wechat {
      font-size: 12px;
      color: #909399;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .case-info {
    font-size: 13px;
  }

  .message-text,
  .remark-text {
    font-size: 13px;
    color: #606266;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 200px;
  }

  .text-gray {
    color: #909399;
    font-size: 13px;
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
