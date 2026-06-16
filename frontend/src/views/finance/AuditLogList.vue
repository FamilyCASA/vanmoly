<template>
  <div class="audit-log-list">
    <div class="page-header">
      <h2>操作日志</h2>
      <div class="header-actions">
        <el-select v-model="filters.action" placeholder="操作类型" clearable style="width: 130px" @change="loadData">
          <el-option label="新增" value="create" />
          <el-option label="修改" value="update" />
          <el-option label="删除" value="delete" />
          <el-option label="审核" value="review" />
          <el-option label="付款" value="pay" />
          <el-option label="导出" value="export" />
        </el-select>
        <el-select v-model="filters.target_type" placeholder="操作对象" clearable style="width: 140px" @change="loadData">
          <el-option label="流水" value="transaction" />
          <el-option label="分类" value="category" />
          <el-option label="报销" value="reimbursement" />
          <el-option label="股东" value="shareholder" />
          <el-option label="章程" value="charter" />
          <el-option label="成员" value="member" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 260px"
          @change="loadData"
        />
      </div>
    </div>

    <!-- 统计条 -->
    <div class="summary-bar">
      <span>共 <strong>{{ total }}</strong> 条记录</span>
      <span class="divider">|</span>
      <span>今天 <strong>{{ todayCount }}</strong> 条</span>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="logs" v-loading="loading" stripe empty-text="暂无操作日志" @row-click="openDetailDrawer">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="actionType(row.action)" size="small" effect="plain">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作对象" width="110">
          <template #default="{ row }">{{ targetLabel(row.target_type) }}</template>
        </el-table-column>
        <el-table-column prop="target_id" label="对象ID" width="90" align="center" />
        <el-table-column label="操作人" width="110">
          <template #default="{ row }">ID:{{ row.operator_id }}</template>
        </el-table-column>
        <el-table-column label="变更摘要" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="change-summary">{{ changeSummary(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column prop="created_at" label="操作时间" width="160" />
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="操作详情"
      size="480px"
    >
      <template v-if="detailLog">
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="日志ID">{{ detailLog.id }}</el-descriptions-item>
            <el-descriptions-item label="操作类型">
              <el-tag :type="actionType(detailLog.action)" size="small">{{ actionLabel(detailLog.action) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="操作对象">{{ targetLabel(detailLog.target_type) }}</el-descriptions-item>
            <el-descriptions-item label="对象ID">{{ detailLog.target_id }}</el-descriptions-item>
            <el-descriptions-item label="操作人ID">{{ detailLog.operator_id }}</el-descriptions-item>
            <el-descriptions-item label="IP地址">{{ detailLog.ip_address || '—' }}</el-descriptions-item>
            <el-descriptions-item label="操作时间" :span="2">{{ detailLog.created_at }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="detailLog.detail_before || detailLog.detail_after">
          <h4>数据变更</h4>
          <el-tabs type="border-card" style="margin-top: 8px">
            <el-tab-pane label="变更前" v-if="detailLog.detail_before">
              <pre class="json-preview">{{ JSON.stringify(detailLog.detail_before, null, 2) }}</pre>
            </el-tab-pane>
            <el-tab-pane label="变更后" v-if="detailLog.detail_after">
              <pre class="json-preview">{{ JSON.stringify(detailLog.detail_after, null, 2) }}</pre>
            </el-tab-pane>
          </el-tabs>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import financeAPI from '@/api/finance'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const todayCount = ref(0)

const filters = ref({ action: 'all', target_type: 'all', dateRange: null })

const detailDrawerVisible = ref(false)
const detailLog = ref(null)

const actionType = (a) => ({ create: 'success', update: 'warning', delete: 'danger', review: 'primary', pay: 'success', export: 'info' }[a] || 'info')
const actionLabel = (a) => ({ create: '新增', update: '修改', delete: '删除', review: '审核', pay: '付款', export: '导出' }[a] || a)
const targetLabel = (t) => ({ transaction: '流水', category: '分类', reimbursement: '报销', shareholder: '股东', charter: '章程', member: '成员' }[t] || t)

const changeSummary = (row) => {
  if (!row.detail_before && !row.detail_after) return '—'
  if (row.action === 'create') return '新增记录'
  if (row.action === 'delete') return '删除记录'
  // 找出变更的字段
  const before = row.detail_before || {}
  const after = row.detail_after || {}
  const changed = []
  for (const key in after) {
    if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) {
      changed.push(key)
    }
  }
  return changed.length ? `变更字段：${changed.join(', ')}` : '无明显变更'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.action !== 'all') params.action = filters.value.action
    if (filters.value.target_type !== 'all') params.target_type = filters.value.target_type
    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.start_date = filters.value.dateRange[0]
      params.end_date = filters.value.dateRange[1]
    }

    const d = await financeAPI.getAuditLogs(params)
    logs.value = d.items || []
    total.value = d.total || 0

    // 统计今天
    const today = new Date().toISOString().slice(0, 10)
    todayCount.value = logs.value.filter(l => l.created_at?.startsWith(today)).length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const openDetailDrawer = (row) => {
  detailLog.value = row
  detailDrawerVisible.value = true
}

onMounted(loadData)
</script>

<style scoped>
.audit-log-list { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}
.page-header h2 { margin: 0; font-size: 20px; }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.summary-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #fafafa;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}
.summary-bar .divider { color: #dcdfe6; }
.summary-bar strong { font-size: 14px; }

.table-card :deep(.el-card__body) { padding: 0; }
.change-summary { font-size: 12px; color: #909399; }

.detail-section { margin-bottom: 20px; }
.detail-section h4 {
  font-size: 14px;
  color: #303133;
  margin: 0 0 10px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.json-preview {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 12px;
  font-size: 12px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  color: #606266;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
}

:deep(.el-table__row) { cursor: pointer; }
:deep(.el-table__empty-block) { min-height: 200px; }
</style>
