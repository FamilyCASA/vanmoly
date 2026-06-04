<template>
  <div class="lead-manage">
    <div class="page-header">
      <h2>线索管理</h2>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_count || 0 }}</div>
            <div class="stat-label">总线索</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value text-primary">{{ stats.status_stats?.['新线索'] || 0 }}</div>
            <div class="stat-label">新线索</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value text-success">{{ stats.status_stats?.['已成交'] || 0 }}</div>
            <div class="stat-label">已成交</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.today_count || 0 }}</div>
            <div class="stat-label">今日新增</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.week_count || 0 }}</div>
            <div class="stat-label">本周新增</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="新线索" value="新线索" />
            <el-option label="已联系" value="已联系" />
            <el-option label="已到店" value="已到店" />
            <el-option label="已成交" value="已成交" />
            <el-option label="无效" value="无效" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filters.source" placeholder="全部来源" clearable style="width: 140px">
            <el-option v-for="src in sources" :key="src" :label="src" :value="src" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="姓名/手机号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 线索列表 -->
    <el-card>
      <el-table :data="leads" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="source" label="来源" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="intention" label="意向" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="follow_count" label="跟进" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openFollowDialog(row)">跟进</el-button>
            <el-button type="primary" link @click="openDetailDialog(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 跟进弹窗 -->
    <el-dialog v-model="followDialogVisible" title="添加跟进记录" width="500px">
      <el-form :model="followForm" label-position="top">
        <el-form-item label="跟进方式">
          <el-radio-group v-model="followForm.follow_type">
            <el-radio value="电话">电话</el-radio>
            <el-radio value="微信">微信</el-radio>
            <el-radio value="到店">到店</el-radio>
            <el-radio value="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="跟进内容">
          <el-input 
            v-model="followForm.content" 
            type="textarea" 
            :rows="4"
            placeholder="记录跟进情况..."
          />
        </el-form-item>
        <el-form-item label="下次跟进">
          <el-date-picker
            v-model="followForm.next_follow_at"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="followDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFollow" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="线索详情" width="600px">
      <div v-if="currentLead" class="lead-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ currentLead.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentLead.phone }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ currentLead.source }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-select v-model="currentLead.status" size="small" @change="updateStatus">
              <el-option label="新线索" value="新线索" />
              <el-option label="已联系" value="已联系" />
              <el-option label="已到店" value="已到店" />
              <el-option label="已成交" value="已成交" />
              <el-option label="无效" value="无效" />
            </el-select>
          </el-descriptions-item>
          <el-descriptions-item label="户型">{{ currentLead.house_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="面积">{{ currentLead.area || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预算">{{ currentLead.budget || '-' }}</el-descriptions-item>
          <el-descriptions-item label="跟进次数">{{ currentLead.follow_count || 0 }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="section">
          <h4>装修意向</h4>
          <p>{{ currentLead.intention || '无' }}</p>
        </div>

        <div class="section" v-if="currentLead.follows?.length">
          <h4>跟进记录</h4>
          <el-timeline>
            <el-timeline-item 
              v-for="follow in currentLead.follows" 
              :key="follow.id"
              :timestamp="formatDate(follow.created_at)"
            >
              <p><strong>{{ follow.follow_type }}</strong>: {{ follow.content }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLeads, getLeadStats, getLeadSources, addLeadFollow, updateLeadStatus, getLeadDetail } from '@/api/lead'

const loading = ref(false)
const submitting = ref(false)
const leads = ref([])
const sources = ref([])
const stats = ref({})

const filters = reactive({
  status: '',
  source: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 跟进弹窗
const followDialogVisible = ref(false)
const currentLead = ref(null)
const followForm = reactive({
  follow_type: '电话',
  content: '',
  next_follow_at: null
})

// 详情弹窗
const detailDialogVisible = ref(false)

const fetchLeads = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    const res = await getLeads(params)
    leads.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取线索失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await getLeadStats()
    stats.value = res || {}
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const fetchSources = async () => {
  try {
    const res = await getLeadSources()
    sources.value = res || []
  } catch (error) {
    console.error('获取来源失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchLeads()
}

const resetFilters = () => {
  filters.status = ''
  filters.source = ''
  filters.keyword = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchLeads()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchLeads()
}

const getStatusType = (status) => {
  const map = {
    '新线索': 'info',
    '已联系': 'warning',
    '已到店': 'primary',
    '已成交': 'success',
    '无效': 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const openFollowDialog = (row) => {
  currentLead.value = row
  followForm.follow_type = '电话'
  followForm.content = ''
  followForm.next_follow_at = null
  followDialogVisible.value = true
}

const submitFollow = async () => {
  if (!followForm.content.trim()) {
    ElMessage.warning('请输入跟进内容')
    return
  }
  
  submitting.value = true
  try {
    const data = {
      ...followForm,
      next_follow_at: followForm.next_follow_at ? followForm.next_follow_at.toISOString() : null
    }
    await addLeadFollow(currentLead.value.id, data)
    ElMessage.success('跟进记录已保存')
    followDialogVisible.value = false
    fetchLeads()
  } catch (error) {
    console.error('保存跟进失败:', error)
  } finally {
    submitting.value = false
  }
}

const openDetailDialog = async (row) => {
  try {
    const res = await getLeadDetail(row.id, { include_follows: true })
    currentLead.value = res
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

const updateStatus = async (status) => {
  try {
    await updateLeadStatus(currentLead.value.id, { status })
    ElMessage.success('状态已更新')
    fetchLeads()
  } catch (error) {
    console.error('更新状态失败:', error)
  }
}

onMounted(() => {
  fetchLeads()
  fetchStats()
  fetchSources()
})
</script>

<style scoped>
.lead-manage {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-value.text-primary {
  color: #409EFF;
}

.stat-value.text-success {
  color: #67C23A;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.lead-detail .section {
  margin-top: 20px;
}

.lead-detail .section h4 {
  margin-bottom: 10px;
  color: #333;
}

.lead-detail .section p {
  color: #666;
  line-height: 1.6;
}
</style>
