<template>
  <div class="scheme-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>选品管理</h2>
        <span class="subtitle">管理客户选品方案</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total || 0 }}</div>
            <div class="stat-label">总方案</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.approved || 0 }}</div>
            <div class="stat-label">已确认</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF7E6; color: #FA8C16;">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending || 0 }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F9F0FF; color: #722ED1;">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatAmount(stats.totalBudget) }}</div>
            <div class="stat-label">方案总金额</div>
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
            placeholder="方案名称/客户名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已确认" value="approved" />
            <el-option label="已转报价" value="quoted" />
          </el-select>
        </el-form-item>
        <el-form-item label="风格">
          <el-select v-model="filterForm.style" placeholder="全部风格" clearable style="width: 120px">
            <el-option label="现代" value="现代" />
            <el-option label="中式" value="中式" />
            <el-option label="北欧" value="北欧" />
            <el-option label="美式" value="美式" />
            <el-option label="轻奢" value="轻奢" />
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

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        :data="schemes"
        v-loading="loading"
        row-key="id"
        style="width: 100%"
      >
        <el-table-column type="expand" width="40">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="方案编号">{{ row.scheme_no }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ formatDate(row.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="房屋面积">{{ row.area }} m²</el-descriptions-item>
                <el-descriptions-item label="装修阶段">{{ row.renovation_stage }}</el-descriptions-item>
                <el-descriptions-item label="预算范围">{{ formatAmount(row.budget_min) }} - {{ formatAmount(row.budget_max) }}</el-descriptions-item>
                <el-descriptions-item label="备注">{{ row.remark || '-' }}</el-descriptions-item>
              </el-descriptions>
              <div class="category-summary" v-if="row.category_summary">
                <div class="summary-title">分类汇总</div>
                <el-row :gutter="8">
                  <el-col :span="4" v-for="(item, key) in row.category_summary" :key="key">
                    <div class="summary-item">
                      <div class="summary-name">{{ key }}</div>
                      <div class="summary-value">{{ item.count }}项 / {{ formatAmount(item.amount) }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="scheme_no" label="方案编号" width="120" />
        <el-table-column prop="name" label="方案名称" min-width="150" />
        <el-table-column label="客户信息" min-width="150">
          <template #default="{ row }">
            <div>{{ row.customer_name }}</div>
            <div class="text-gray">{{ row.customer_phone }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="style" label="风格" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.style }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_budget" label="预算金额" width="120">
          <template #default="{ row }">
            <span class="amount">{{ formatAmount(row.total_budget) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="item_count" label="选品数" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="primary" link size="small" @click="convertToQuote(row)" v-if="row.status === 'approved'">
              转报价
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
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
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="方案详情"
      width="900px"
      destroy-on-close
    >
      <div v-if="currentScheme" class="scheme-detail">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="方案编号">{{ currentScheme.scheme_no }}</el-descriptions-item>
          <el-descriptions-item label="方案名称">{{ currentScheme.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentScheme.status)">
              {{ getStatusLabel(currentScheme.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentScheme.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentScheme.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="风格">{{ currentScheme.style }}</el-descriptions-item>
          <el-descriptions-item label="面积">{{ currentScheme.area }} m²</el-descriptions-item>
          <el-descriptions-item label="装修阶段">{{ currentScheme.renovation_stage }}</el-descriptions-item>
          <el-descriptions-item label="预算">{{ formatAmount(currentScheme.total_budget) }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">选品清单 ({{ currentScheme.items?.length || 0 }}项)</div>
          <el-table :data="currentScheme.items" size="small" border>
            <el-table-column type="index" width="50" />
            <el-table-column prop="material_name" label="物料名称" min-width="150" />
            <el-table-column prop="category_name" label="分类" width="120" />
            <el-table-column prop="brand" label="品牌" width="100" />
            <el-table-column prop="room_name" label="房间" width="100" />
            <el-table-column prop="quantity" label="数量" width="80" align="center" />
            <el-table-column prop="unit" label="单位" width="60" />
            <el-table-column prop="sale_price" label="单价" width="100">
              <template #default="{ row }">
                {{ formatAmount(row.sale_price) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_price" label="小计" width="100">
              <template #default="{ row }">
                <span class="amount">{{ formatAmount(row.total_price) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-summary" v-if="currentScheme.category_summary">
          <div class="section-title">分类汇总</div>
          <el-row :gutter="16">
            <el-col :span="4" v-for="(item, key) in currentScheme.category_summary" :key="key">
              <el-statistic :title="key" :value="item.count" suffix="项">
                <template #suffix>
                  <div class="stat-amount">{{ formatAmount(item.amount) }}</div>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Check, Timer, Money, Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const detailVisible = ref(false)
const currentScheme = ref(null)

// 统计数据
const stats = ref({
  total: 0,
  approved: 0,
  pending: 0,
  totalBudget: 0
})

// 筛选表单
const filterForm = ref({
  keyword: '',
  status: '',
  style: ''
})

// 分页
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

// 方案列表
const schemes = ref([])

// 状态映射
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已确认', type: 'success' },
  quoted: { label: '已转报价', type: 'primary' }
}

const getStatusLabel = (status) => statusMap[status]?.label || status
const getStatusType = (status) => statusMap[status]?.type || 'info'

// 格式化金额
const formatAmount = (amount) => {
  if (!amount) return '¥0'
  return '¥' + Number(amount).toLocaleString()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据，实际项目中从API获取
    schemes.value = [
      {
        id: 1,
        scheme_no: 'SC202604260001',
        name: '张先生现代简约方案',
        customer_name: '张先生',
        customer_phone: '13800138001',
        style: '现代',
        area: 120,
        renovation_stage: '水电完成',
        total_budget: 285000,
        item_count: 45,
        status: 'approved',
        created_at: '2026-04-26T10:00:00',
        category_summary: {
          '固装家具': { count: 12, amount: 85000 },
          '活动家具': { count: 15, amount: 95000 },
          '灯具': { count: 8, amount: 35000 },
          '窗帘': { count: 5, amount: 25000 },
          '饰品': { count: 5, amount: 45000 }
        },
        items: [
          { material_name: '现代简约沙发', category_name: '活动家具', brand: '帝标', room_name: '客厅', quantity: 1, unit: '套', sale_price: 15000, total_price: 15000 },
          { material_name: '餐厅吊灯', category_name: '灯具', brand: '高晟', room_name: '餐厅', quantity: 1, unit: '盏', sale_price: 3500, total_price: 3500 }
        ]
      },
      {
        id: 2,
        scheme_no: 'SC202604260002',
        name: '李女士北欧风格方案',
        customer_name: '李女士',
        customer_phone: '13800138002',
        style: '北欧',
        area: 89,
        renovation_stage: '毛坯',
        total_budget: 198000,
        item_count: 32,
        status: 'pending',
        created_at: '2026-04-26T14:30:00',
        category_summary: {
          '固装家具': { count: 8, amount: 55000 },
          '活动家具': { count: 12, amount: 68000 },
          '灯具': { count: 6, amount: 28000 },
          '窗帘': { count: 4, amount: 18000 },
          '饰品': { count: 2, amount: 29000 }
        },
        items: []
      },
      {
        id: 3,
        scheme_no: 'SC202604250001',
        name: '王总别墅中式方案',
        customer_name: '王总',
        customer_phone: '13800138003',
        style: '中式',
        area: 350,
        renovation_stage: '设计阶段',
        total_budget: 680000,
        item_count: 86,
        status: 'draft',
        created_at: '2026-04-25T09:00:00',
        category_summary: {},
        items: []
      }
    ]
    pagination.value.total = schemes.value.length
    
    // 更新统计
    stats.value = {
      total: 3,
      approved: 1,
      pending: 1,
      totalBudget: 1163000
    }
  } catch (error) {
    console.error('加载方案列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    keyword: '',
    status: '',
    style: ''
  }
  loadData()
}

// 查看详情
const viewDetail = (row) => {
  currentScheme.value = row
  detailVisible.value = true
}

// 转报价
const convertToQuote = (row) => {
  ElMessageBox.confirm(`确定将方案 "${row.name}" 转为报价单吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('已生成报价单')
    router.push('/admin/quotes')
  }).catch(() => {})
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除方案 "${row.name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {})
}

// 分页
const handleSizeChange = (val) => {
  pagination.value.page_size = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.value.page = val
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.scheme-manage {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 16px;
}

.expand-content {
  padding: 16px;
  background: #F5F7FA;
}

.category-summary {
  margin-top: 16px;
}

.summary-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.summary-item {
  text-align: center;
  padding: 12px;
  background: #fff;
  border-radius: 4px;
}

.summary-name {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.amount {
  color: #F56C6C;
  font-weight: 500;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.scheme-detail {
  padding: 16px 0;
}

.detail-section {
  margin-top: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #EBEEF5;
}

.detail-summary {
  margin-top: 24px;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 4px;
}

.stat-amount {
  font-size: 12px;
  color: #F56C6C;
  margin-top: 4px;
}
</style>
