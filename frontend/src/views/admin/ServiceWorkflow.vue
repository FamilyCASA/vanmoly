<template>
  <div class="service-workflow">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>服务流程</h2>
        <span class="subtitle">58节点全案服务流程管理</span>
      </div>
      <el-button type="primary" size="large" @click="showInitDialog" v-if="!hasNodes">
        <el-icon><Setting /></el-icon> 初始化流程
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="stat in phaseStats" :key="stat.code">
        <div class="stat-card" :style="{ borderLeftColor: stat.color }">
          <div class="stat-title">{{ stat.name }}</div>
          <div class="stat-value">{{ stat.count || 0 }}</div>
          <div class="stat-nodes">节点 {{ stat.nodes }}</div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card total-card">
          <div class="stat-title">总流程</div>
          <div class="stat-value">{{ totalWorkflows }}</div>
          <div class="stat-nodes">本月新增 {{ newThisMonth }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 流程阶段时间轴 -->
    <el-card class="phase-timeline" shadow="never">
      <div class="timeline-header">
        <span class="title">服务流程阶段</span>
        <span class="subtitle">点击阶段查看详细节点</span>
      </div>
      <el-steps :active="activePhaseIndex" finish-status="success" simple>
        <el-step
          v-for="phase in phases"
          :key="phase.code"
          :title="phase.name"
          @click="selectPhase(phase.code)"
          class="phase-step"
        />
      </el-steps>
    </el-card>

    <!-- 节点列表 -->
    <el-card shadow="never" v-if="currentPhase">
      <template #header>
        <div class="card-header">
          <span>{{ currentPhaseName }} - 节点列表</span>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="list">列表</el-radio-button>
            <el-radio-button value="card">卡片</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <!-- 列表视图 -->
      <el-table v-if="viewMode === 'list'" :data="currentNodes" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column label="节点编码" prop="node_code" width="100" />
        <el-table-column label="节点名称" prop="node_name" min-width="200" />
        <el-table-column label="负责角色" width="150">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.responsible_roles"
              :key="role"
              size="small"
              class="role-tag"
            >
              {{ role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联模块" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.related_module" type="info" size="small">
              {{ moduleLabel(row.related_module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="财务联动" width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.finance_trigger" color="#52C41A"><Check /></el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewNodeDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图 -->
      <div v-else class="node-cards">
        <el-card
          v-for="node in currentNodes"
          :key="node.id"
          class="node-card"
          shadow="hover"
        >
          <div class="node-header">
            <span class="node-code">{{ node.node_code }}</span>
            <el-tag v-if="node.finance_trigger" type="success" size="small">财务</el-tag>
          </div>
          <div class="node-name">{{ node.node_name }}</div>
          <div class="node-roles">
            <el-tag
              v-for="role in node.responsible_roles"
              :key="role"
              size="small"
              effect="plain"
              class="role-tag"
            >
              {{ role }}
            </el-tag>
          </div>
          <div class="node-module" v-if="node.related_module">
            关联: {{ moduleLabel(node.related_module) }}
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 客户流程列表 -->
    <el-card class="workflow-list" shadow="never">
      <template #header>
        <div class="card-header">
          <span>客户流程实例</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 创建流程
          </el-button>
        </div>
      </template>

      <el-table :data="workflows" v-loading="loading">
        <el-table-column label="客户信息" min-width="200">
          <template #default="{ row }">
            <div class="customer-info">
              <div class="customer-name">{{ row.customer_name }}</div>
              <div class="customer-id">ID: {{ row.customer_id }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="当前阶段" width="120">
          <template #default="{ row }">
            <el-tag :color="phaseColor(row.current_phase)" effect="dark" size="small">
              {{ phaseName(row.current_phase) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="当前节点" min-width="150">
          <template #default="{ row }">
            <div class="current-node">
              <div class="node-code">{{ row.current_node_code }}</div>
              <div class="node-name">{{ row.current_node_name }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress.percentage"
              :status="progressStatus(row.progress.percentage)"
            />
            <div class="progress-text">
              {{ row.progress.completed }}/{{ row.progress.total }} 节点
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="workflowStatusType(row.status)" size="small">
              {{ workflowStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="开工日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewWorkflow(row)">查看</el-button>
            <el-button
              v-if="row.status === 'active'"
              link
              type="success"
              @click="advanceWorkflow(row)"
            >
              推进
            </el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button link type="primary">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="pause" v-if="row.status === 'active'">暂停</el-dropdown-item>
                  <el-dropdown-item command="resume" v-if="row.status === 'paused'">恢复</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadWorkflows"
        />
      </div>
    </el-card>

    <!-- 初始化对话框 -->
    <el-dialog v-model="initDialog.visible" title="初始化58节点服务流程" width="500px">
      <div class="init-content">
        <el-alert
          title="即将初始化58节点服务流程"
          description="此操作将创建完整的获客沉淀→转化签约→前期准备→硬装施工→后续阶段全流程节点定义，请确认是否继续？"
          type="warning"
          show-icon
          :closable="false"
        />
        <div class="phase-preview">
          <div v-for="phase in phases" :key="phase.code" class="phase-item">
            <span class="phase-dot" :style="{ background: phase.color }"></span>
            <span class="phase-name">{{ phase.name }}</span>
            <span class="phase-nodes">{{ phase.nodes }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="initDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="initNodes" :loading="initDialog.loading">
          确认初始化
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建流程对话框 -->
    <el-dialog v-model="createDialog.visible" title="为客户创建流程" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="选择客户" required>
          <el-select-v2
            v-model="createForm.customer_id"
            :options="customerOptions"
            placeholder="搜索客户"
            filterable
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开工日期">
          <el-date-picker
            v-model="createForm.start_date"
            type="date"
            placeholder="选择开工日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="计划完工">
          <el-date-picker
            v-model="createForm.planned_end_date"
            type="date"
            placeholder="选择计划完工日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="createWorkflow" :loading="createDialog.loading">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 流程详情抽屉 -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="60%">
      <div v-if="detailDrawer.workflow" class="workflow-detail">
        <!-- 流程头部信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户">{{ detailDrawer.workflow.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="当前阶段">
            <el-tag :color="phaseColor(detailDrawer.workflow.current_phase)" effect="dark" size="small">
              {{ phaseName(detailDrawer.workflow.current_phase) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前节点">{{ detailDrawer.workflow.current_node_name }}</el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress
              :percentage="detailDrawer.workflow.progress.percentage"
              style="width: 150px"
            />
          </el-descriptions-item>
          <el-descriptions-item label="开工日期">{{ formatDate(detailDrawer.workflow.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="计划完工">{{ formatDate(detailDrawer.workflow.planned_end_date) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 节点记录时间轴 -->
        <div class="records-section">
          <h4>节点执行记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="record in detailDrawer.records"
              :key="record.id"
              :type="recordStatusType(record.status)"
              :timestamp="formatDateTime(record.created_at)"
            >
              <div class="record-item">
                <div class="record-header">
                  <span class="node-name">{{ record.node_name }}</span>
                  <el-tag :type="recordStatusType(record.status)" size="small">
                    {{ recordStatusLabel(record.status) }}
                  </el-tag>
                </div>
                <div class="record-info" v-if="record.assigned_name">
                  负责人: {{ record.assigned_name }}
                </div>
                <div class="record-content" v-if="record.content">
                  {{ record.content }}
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Check, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const hasNodes = ref(false)
const phases = ref([])
const nodes = ref({})
const workflows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const activePhase = ref('')
const viewMode = ref('list')
const statistics = ref({})

// 阶段统计
const phaseStats = computed(() => {
  return phases.value.map(p => ({
    ...p,
    count: statistics.value.by_phase?.[p.code] || 0
  }))
})

const totalWorkflows = computed(() => {
  return Object.values(statistics.value.by_status || {}).reduce((a, b) => a + b, 0)
})

const newThisMonth = computed(() => statistics.value.new_this_month || 0)

const currentPhase = computed(() => activePhase.value)
const currentPhaseName = computed(() => {
  const phase = phases.value.find(p => p.code === activePhase.value)
  return phase?.name || ''
})

const currentNodes = computed(() => {
  return nodes.value[activePhase.value]?.nodes || []
})

const activePhaseIndex = computed(() => {
  const index = phases.value.findIndex(p => p.code === activePhase.value)
  return index >= 0 ? index : 0
})

// 对话框
const initDialog = reactive({ visible: false, loading: false })
const createDialog = reactive({ visible: false, loading: false })
const detailDrawer = reactive({ visible: false, title: '', workflow: null, records: [] })

const createForm = reactive({
  customer_id: null,
  start_date: null,
  planned_end_date: null
})

const customerOptions = ref([])

// 加载数据
const loadPhases = async () => {
  try {
    const res = await request.get('/workflows/phases')
    phases.value = res
    if (phases.value.length && !activePhase.value) {
      activePhase.value = phases.value[0].code
    }
  } catch (error) {
    console.error('加载阶段失败', error)
  }
}

const loadNodes = async () => {
  try {
    const res = await request.get('/workflows/nodes')
    nodes.value = res
    hasNodes.value = Object.keys(res).length > 0
  } catch (error) {
    console.error('加载节点失败', error)
  }
}

const loadWorkflows = async () => {
  loading.value = true
  try {
    const res = await request.get('/workflows', {
      params: { page: page.value, page_size: pageSize.value }
    })
    workflows.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载流程失败', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const res = await request.get('/workflows/statistics')
    statistics.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadCustomers = async () => {
  try {
    const res = await request.get('/customers', { params: { page_size: 1000 } })
    customerOptions.value = res.items.map(c => ({
      value: c.id,
      label: `${c.name} (${c.phone})`
    }))
  } catch (error) {
    console.error('加载客户失败', error)
  }
}

// 初始化节点
const showInitDialog = () => {
  initDialog.visible = true
}

const initNodes = async () => {
  initDialog.loading = true
  try {
    await request.post('/workflows/nodes/init')
    ElMessage.success('初始化成功')
    initDialog.visible = false
    loadNodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '初始化失败')
  } finally {
    initDialog.loading = false
  }
}

// 选择阶段
const selectPhase = (code) => {
  activePhase.value = code
}

// 创建流程
const openCreateDialog = () => {
  createDialog.visible = true
  loadCustomers()
}

const createWorkflow = async () => {
  if (!createForm.customer_id) {
    ElMessage.warning('请选择客户')
    return
  }

  createDialog.loading = true
  try {
    await request.post('/workflows', {
      customer_id: createForm.customer_id,
      start_date: createForm.start_date,
      planned_end_date: createForm.planned_end_date
    })
    ElMessage.success('创建成功')
    createDialog.visible = false
    loadWorkflows()
    loadStatistics()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '创建失败')
  } finally {
    createDialog.loading = false
  }
}

// 查看流程
const viewWorkflow = async (row) => {
  try {
    const res = await request.get(`/workflows/${row.id}`)
    detailDrawer.workflow = res
    detailDrawer.records = res.node_records || []
    detailDrawer.title = `流程详情 - ${res.customer_name}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 推进流程
const advanceWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm('确定要推进到下一节点吗？', '提示', { type: 'warning' })
    await request.post(`/workflows/${row.id}/advance`, {})
    ElMessage.success('推进成功')
    loadWorkflows()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('推进失败')
  }
}

// 更多操作
const handleCommand = async (command, row) => {
  if (command === 'pause') {
    try {
      await request.post(`/workflows/${row.id}/pause`)
      ElMessage.success('已暂停')
      loadWorkflows()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  } else if (command === 'resume') {
    try {
      await request.post(`/workflows/${row.id}/resume`)
      ElMessage.success('已恢复')
      loadWorkflows()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }
}

// 辅助函数
const moduleLabel = (module) => {
  const labels = {
    customer: '客户',
    material: '物料',
    finance: '财务',
    quote: '报价',
    contract: '合同'
  }
  return labels[module] || module
}

const phaseColor = (code) => {
  const phase = phases.value.find(p => p.code === code)
  return phase?.color || '#999'
}

const phaseName = (code) => {
  const phase = phases.value.find(p => p.code === code)
  return phase?.name || code
}

const workflowStatusType = (status) => {
  const types = { active: 'success', paused: 'warning', completed: 'info', cancelled: 'danger' }
  return types[status] || 'info'
}

const workflowStatusLabel = (status) => {
  const labels = { active: '进行中', paused: '已暂停', completed: '已完成', cancelled: '已取消' }
  return labels[status] || status
}

const recordStatusType = (status) => {
  const types = { pending: 'info', processing: 'warning', completed: 'success', skipped: 'info' }
  return types[status] || 'info'
}

const recordStatusLabel = (status) => {
  const labels = { pending: '待处理', processing: '进行中', completed: '已完成', skipped: '已跳过' }
  return labels[status] || status
}

const progressStatus = (percentage) => {
  if (percentage >= 100) return 'success'
  if (percentage >= 50) return ''
  return 'exception'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}

const viewNodeDetail = (node) => {
  // 可以打开节点详情弹窗
  console.log('查看节点详情', node)
}

onMounted(() => {
  loadPhases()
  loadNodes()
  loadWorkflows()
  loadStatistics()
})
</script>

<style scoped>
.service-workflow {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  color: #8c8c8c;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

.stat-card.total-card {
  border-left-color: #262626;
  background: linear-gradient(135deg, #262626 0%, #434343 100%);
  color: #fff;
}

.stat-card.total-card .stat-title,
.stat-card.total-card .stat-nodes {
  color: rgba(255,255,255,0.7);
}

.stat-title {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  line-height: 1;
}

.stat-nodes {
  font-size: 12px;
  color: #bfbfbf;
  margin-top: 4px;
}

.phase-timeline {
  margin-bottom: 24px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.timeline-header .title {
  font-weight: 500;
  color: #262626;
}

.timeline-header .subtitle {
  font-size: 12px;
  color: #8c8c8c;
}

.phase-step {
  cursor: pointer;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-tag {
  margin-right: 4px;
  margin-bottom: 2px;
}

.node-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.node-card {
  cursor: pointer;
  transition: all 0.3s;
}

.node-card:hover {
  transform: translateY(-2px);
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.node-code {
  font-size: 12px;
  color: #8c8c8c;
  font-family: monospace;
}

.node-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 8px;
}

.node-roles {
  margin-bottom: 8px;
}

.node-module {
  font-size: 12px;
  color: #bfbfbf;
}

.workflow-list {
  margin-top: 24px;
}

.customer-info .customer-name {
  font-weight: 500;
  color: #262626;
}

.customer-info .customer-id {
  font-size: 12px;
  color: #8c8c8c;
}

.current-node .node-code {
  font-size: 12px;
  color: #8c8c8c;
}

.current-node .node-name {
  font-weight: 500;
  color: #262626;
}

.progress-text {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.init-content {
  padding: 16px 0;
}

.phase-preview {
  margin-top: 24px;
}

.phase-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.phase-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.phase-name {
  flex: 1;
  color: #262626;
}

.phase-nodes {
  font-size: 12px;
  color: #8c8c8c;
}

.workflow-detail {
  padding: 16px;
}

.records-section {
  margin-top: 24px;
}

.records-section h4 {
  margin-bottom: 16px;
  color: #262626;
}

.record-item {
  padding: 8px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.record-header .node-name {
  font-weight: 500;
}

.record-info {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.record-content {
  font-size: 13px;
  color: #595959;
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
}
</style>
