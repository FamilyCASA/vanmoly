<template>
  <div class="appointment-manage">
    <div class="page-header">
      <h2>预约管理</h2>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_count || 0 }}</div>
            <div class="stat-label">总预约</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value text-primary">{{ stats.status_stats?.['待确认'] || 0 }}</div>
            <div class="stat-label">待确认</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value text-success">{{ stats.status_stats?.['已确认'] || 0 }}</div>
            <div class="stat-label">已确认</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.today_count || 0 }}</div>
            <div class="stat-label">今日</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-item">
            <div class="stat-value">{{ stats.week_count || 0 }}</div>
            <div class="stat-label">本周</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 视图切换 -->
    <el-card class="view-tabs">
      <el-radio-group v-model="currentView" size="large">
        <el-radio-button value="list">列表视图</el-radio-button>
        <el-radio-button value="calendar">日历视图</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 列表视图 -->
    <template v-if="currentView === 'list'">
      <el-card class="filter-card">
        <el-form :model="filters" inline>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 120px">
              <el-option label="待确认" value="待确认" />
              <el-option label="已确认" value="已确认" />
              <el-option label="已完成" value="已完成" />
              <el-option label="已取消" value="已取消" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 280px"
            />
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

      <el-card>
        <el-table :data="appointments" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="customer_name" label="客户姓名" width="100" />
          <el-table-column prop="phone" label="手机号" width="120" />
          <el-table-column prop="house_address" label="地址" show-overflow-tooltip />
          <el-table-column prop="appointment_date" label="预约日期" width="110">
            <template #default="{ row }">
              {{ formatDate(row.appointment_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="appointment_time" label="时间" width="80">
            <template #default="{ row }">
              {{ formatTime(row.appointment_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="提交时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDetailDialog(row)">详情</el-button>
              <el-button 
                v-if="row.status === '待确认'" 
                type="success" 
                link 
                @click="confirmAppointment(row)"
              >
                确认
              </el-button>
              <el-button 
                v-if="row.status !== '已取消'" 
                type="danger" 
                link 
                @click="cancelAppointment(row)"
              >
                取消
              </el-button>
            </template>
          </el-table-column>
        </el-table>

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
    </template>

    <!-- 日历视图 -->
    <template v-else>
      <el-card>
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div class="calendar-cell">
              <p :class="{ 'is-today': data.isSelected }">{{ data.day.split('-').slice(2).join('-') }}</p>
              <div v-if="calendarData[data.day]" class="appointments">
                <el-tag 
                  v-for="apt in calendarData[data.day]" 
                  :key="apt.id"
                  size="small"
                  :type="getStatusType(apt.status)"
                  class="appointment-tag"
                >
                  {{ apt.time?.slice(0, 5) }} {{ apt.customer_name }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-calendar>
      </el-card>
    </template>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="预约详情" width="600px">
      <div v-if="currentAppointment" class="appointment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户姓名">{{ currentAppointment.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentAppointment.phone }}</el-descriptions-item>
          <el-descriptions-item label="房屋地址" :span="2">{{ currentAppointment.house_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="户型">{{ currentAppointment.house_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="面积">{{ currentAppointment.area || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预算">{{ currentAppointment.budget || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预约日期">{{ formatDate(currentAppointment.appointment_date) }}</el-descriptions-item>
          <el-descriptions-item label="预约时间">{{ formatTime(currentAppointment.appointment_time) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentAppointment.status)">{{ currentAppointment.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDateTime(currentAppointment.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentAppointment.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="currentAppointment?.status === '待确认'" 
          type="success" 
          @click="confirmFromDetail"
        >
          确认预约
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getAppointments, 
  getAppointmentStats, 
  getAppointmentCalendar,
  updateAppointment 
} from '@/api/appointment'

const loading = ref(false)
const appointments = ref([])
const stats = ref({})
const calendarData = ref({})
const currentView = ref('list')
const calendarDate = ref(new Date())

const filters = reactive({
  status: '',
  keyword: ''
})

const dateRange = ref([])

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const detailDialogVisible = ref(false)
const currentAppointment = ref(null)

const fetchAppointments = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0].toISOString().split('T')[0]
      params.date_to = dateRange.value[1].toISOString().split('T')[0]
    }
    
    const res = await getAppointments(params)
    appointments.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取预约失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await getAppointmentStats()
    stats.value = res || {}
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const fetchCalendar = async () => {
  try {
    const year = calendarDate.value.getFullYear()
    const month = calendarDate.value.getMonth() + 1
    const res = await getAppointmentCalendar({ year, month })
    calendarData.value = res || {}
  } catch (error) {
    console.error('获取日历失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchAppointments()
}

const resetFilters = () => {
  filters.status = ''
  filters.keyword = ''
  dateRange.value = []
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchAppointments()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchAppointments()
}

const getStatusType = (status) => {
  const map = {
    '待确认': 'warning',
    '已确认': 'success',
    '已完成': 'info',
    '已取消': 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return timeStr.slice(0, 5)
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const openDetailDialog = (row) => {
  currentAppointment.value = row
  detailDialogVisible.value = true
}

const confirmAppointment = async (row) => {
  try {
    await ElMessageBox.confirm('确认此预约吗？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateAppointment(row.id, { status: '已确认' })
    ElMessage.success('预约已确认')
    fetchAppointments()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认失败:', error)
    }
  }
}

const confirmFromDetail = async () => {
  await confirmAppointment(currentAppointment.value)
  detailDialogVisible.value = false
}

const cancelAppointment = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消预约', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入取消原因'
    })
    
    await updateAppointment(row.id, { 
      status: '已取消',
      cancel_reason: value 
    })
    ElMessage.success('预约已取消')
    fetchAppointments()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消失败:', error)
    }
  }
}

// 监听日历月份变化
watch(calendarDate, () => {
  if (currentView.value === 'calendar') {
    fetchCalendar()
  }
}, { immediate: true })

// 监听视图切换
watch(currentView, (view) => {
  if (view === 'calendar') {
    fetchCalendar()
  }
})

onMounted(() => {
  fetchAppointments()
  fetchStats()
})
</script>

<style scoped>
.appointment-manage {
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

.view-tabs {
  margin-bottom: 20px;
  text-align: center;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 日历样式 */
.calendar-cell {
  min-height: 80px;
}

.calendar-cell p {
  margin: 0 0 4px;
  font-size: 14px;
}

.calendar-cell p.is-today {
  color: #409EFF;
  font-weight: bold;
}

.appointments {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.appointment-tag {
  font-size: 11px;
  padding: 0 4px;
}

.appointment-detail {
  padding: 10px 0;
}
</style>
