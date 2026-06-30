<template>
  <div class="service-workflow">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>服务流程</h2>
        <span class="subtitle">全案服务流程管理</span>
      </div>
    </div>

    <!-- 统计卡片（只读） -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="phase in phases" :key="phase.code">
        <div
          class="stat-card"
          :class="{ active: activePhase === phase.code }"
          :style="{ borderLeftColor: phase.color }"
          @click="selectPhase(phase.code)"
        >
          <div class="stat-title">{{ phase.name }}</div>
          <div class="stat-value">{{ phase.node_count || 0 }}</div>
          <div class="stat-nodes">节点</div>
        </div>
      </el-col>
    </el-row>

    <!-- 节点列表（只读） -->
    <el-card shadow="never" v-if="activePhase">
      <template #header>
        <div class="card-header">
          <span>{{ currentPhaseName }} - 节点列表</span>
          <div>
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button value="list">列表</el-radio-button>
              <el-radio-button value="card">卡片</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 列表视图（只读） -->
      <el-table v-if="viewMode === 'list'" :data="currentNodes" stripe row-key="id">
        <el-table-column label="编码" prop="node_code" width="90">
          <template #default="{ row }">
            <span class="mono">{{ row.node_code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="节点名称" min-width="200">
          <template #default="{ row }">{{ row.node_name }}</template>
        </el-table-column>
        <el-table-column label="负责角色" width="200">
          <template #default="{ row }">
            <el-tag v-for="role in row.responsible_roles" :key="role" size="small" class="role-tag">
              {{ role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联模块" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.related_module" type="info" size="small">
              {{ moduleLabel(row.related_module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="财务" width="70" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.finance_trigger" color="#52C41A"><Check /></el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewNodeDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片视图（只读） -->
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
            <el-tag v-for="role in node.responsible_roles" :key="role" size="small" effect="plain" class="role-tag">
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
            <div>
              <div class="mono">{{ row.current_node_code }}</div>
              <div>{{ row.current_node_name }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress?.percentage || 0"
              :status="progressStatus(row.progress?.percentage || 0)"
            />
            <div class="progress-text">{{ row.progress?.completed || 0 }}/{{ row.progress?.total || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="workflowStatusType(row.status)" size="small">
              {{ workflowStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewWorkflow(row)">查看</el-button>
            <el-button v-if="row.status === 'active'" link type="success" @click="advanceWorkflow(row)">推进</el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button link type="primary">更多<el-icon class="el-icon--right"><ArrowDown /></el-icon></el-button>
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
          <el-date-picker v-model="createForm.start_date" type="date" placeholder="选择开工日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划完工">
          <el-date-picker v-model="createForm.planned_end_date" type="date" placeholder="选择计划完工日期" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="createWorkflow" :loading="createDialog.loading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 节点详情对话框（只读） -->
    <el-dialog v-model="nodeDetailDialog.visible" :title="`节点详情 - ${nodeDetailDialog.node?.node_code || ''}`" width="600px">
      <el-descriptions :column="2" border v-if="nodeDetailDialog.node">
        <el-descriptions-item label="节点编码">{{ nodeDetailDialog.node.node_code }}</el-descriptions-item>
        <el-descriptions-item label="节点名称">{{ nodeDetailDialog.node.node_name }}</el-descriptions-item>
        <el-descriptions-item label="所属阶段">{{ phaseName(nodeDetailDialog.node.phase) }}</el-descriptions-item>
        <el-descriptions-item label="关联模块">{{ nodeDetailDialog.node.related_module ? moduleLabel(nodeDetailDialog.node.related_module) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责角色" :span="2">
          <el-tag v-for="role in nodeDetailDialog.node.responsible_roles" :key="role" size="small" class="role-tag">{{ role }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="财务联动">
          <el-icon v-if="nodeDetailDialog.node.finance_trigger" color="#52C41A"><Check /></el-icon>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="财务类型" v-if="nodeDetailDialog.node.finance_trigger">
          {{ financeTypeLabel(nodeDetailDialog.node.finance_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ nodeDetailDialog.node.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="输入要求" :span="2" v-if="nodeDetailDialog.node.input_requirements?.length">
          <el-tag v-for="req in nodeDetailDialog.node.input_requirements" :key="req" size="small" type="info" class="role-tag">{{ req }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="交付物" :span="2" v-if="nodeDetailDialog.node.output_deliverables?.length">
          <el-tag v-for="deliv in nodeDetailDialog.node.output_deliverables" :key="deliv" size="small" type="success" class="role-tag">{{ deliv }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="nodeDetailDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 流程详情抽屉 -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="60%">
      <div v-if="detailDrawer.workflow" class="workflow-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客户">{{ detailDrawer.workflow.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="当前阶段">
            <el-tag :color="phaseColor(detailDrawer.workflow.current_phase)" effect="dark" size="small">
              {{ phaseName(detailDrawer.workflow.current_phase) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="当前节点">{{ detailDrawer.workflow.current_node_name }}</el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress :percentage="detailDrawer.workflow.progress?.percentage || 0" style="width: 150px" />
          </el-descriptions-item>
        </el-descriptions>
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
                  <span>{{ record.node_name }}</span>
                  <div class="record-actions">
                    <el-tag :type="recordStatusType(record.status)" size="small">
                      {{ recordStatusLabel(record.status) }}
                    </el-tag>
                    <el-button
                      v-if="['pending', 'processing'].includes(record.status)"
                      link
                      type="primary"
                      size="small"
                      @click="submitNodeReview(record)"
                    >
                      提交验收
                    </el-button>
                  </div>
                </div>
                <div v-if="record.assigned_name">负责人: {{ record.assigned_name }}</div>
                <div v-if="record.content" class="record-content">{{ record.content }}</div>
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
import { Plus, Check, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const phases = ref([])
const nodes = ref({})
const workflows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const activePhase = ref('')
const viewMode = ref('list')

const allRoles = ref([
  '运营', '销售', '规划师', '设计师', '全案规划师', '施工图设计师',
  '施工负责人', '监理', '商务', '财务', '物料专员', '预算专员',
  '水电师傅', '暖通师傅', '木工师傅', '瓦工师傅', '油工师傅',
  '防水师傅', '安装师傅', '售后专员', '客服', '店长', '团队'
])

const moduleOptions = [
  { value: 'customer', label: '客户' },
  { value: 'material', label: '物料' },
  { value: 'finance', label: '财务' },
  { value: 'quote', label: '报价' },
  { value: 'contract', label: '合同' }
]

const currentPhaseName = computed(() => {
  const phase = phases.value.find(p => p.code === activePhase.value)
  return phase?.name || ''
})

const currentNodes = computed(() => {
  return nodes.value[activePhase.value]?.nodes || []
})

// 对话框
const createDialog = reactive({ visible: false, loading: false })
const nodeDetailDialog = reactive({ visible: false, node: null })
const detailDrawer = reactive({ visible: false, title: '', workflow: null, records: [] })

const createForm = reactive({
  customer_id: null,
  start_date: null,
  planned_end_date: null
})

const customerOptions = ref([])

// ========== 数据加载 ==========

const loadPhases = async () => {
  try {
    const res = await request.get('/workflows/phases')
    phases.value = res || []
    if (phases.value.length && !activePhase.value) {
      activePhase.value = phases.value[0].code
    }
  } catch (e) {
    console.error('加载阶段失败', e)
  }
}

const loadNodes = async () => {
  try {
    const res = await request.get('/workflows/nodes')
    nodes.value = res || {}
  } catch (e) {
    console.error('加载节点失败', e)
  }
}

const loadWorkflows = async () => {
  loading.value = true
  try {
    const res = await request.get('/workflows', {
      params: { page: page.value, page_size: pageSize.value }
    })
    workflows.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    console.error('加载流程失败', e)
  } finally {
    loading.value = false
  }
}

const loadCustomers = async () => {
  try {
    const res = await request.get('/customers', { params: { page_size: 1000 } })
    customerOptions.value = (res.items || []).map(c => ({
      value: c.id,
      label: `${c.name} (${c.phone || '无电话'})`
    }))
  } catch (e) {
    console.error('加载客户失败', e)
  }
}

// ========== 阶段操作（只读） ==========

const selectPhase = (code) => {
  activePhase.value = code
}

// ========== 节点操作（只读） ==========

const viewNodeDetail = (node) => {
  nodeDetailDialog.node = JSON.parse(JSON.stringify(node))
  nodeDetailDialog.visible = true
}

// ========== 流程操作 ==========

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
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '创建失败')
  } finally {
    createDialog.loading = false
  }
}

const viewWorkflow = async (row) => {
  try {
    const res = await request.get(`/workflows/${row.id}`)
    detailDrawer.workflow = res
    detailDrawer.records = res.node_records || []
    detailDrawer.title = `流程详情 - ${res.customer_name}`
    detailDrawer.visible = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const submitNodeReview = async (record) => {
  try {
    const { value } = await ElMessageBox.prompt('请填写节点资料/任务完成说明', '提交节点验收', {
      confirmButtonText: '提交验收',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputValue: record.content || '',
      inputPattern: /\S+/,
      inputErrorMessage: '请填写提交说明'
    })
    await request.post(`/workflows/records/${record.id}/submit-review`, {
      content: value,
      attachments: record.attachments || []
    })
    ElMessage.success('已提交节点资料验收')
    if (detailDrawer.workflow) {
      await viewWorkflow({ id: detailDrawer.workflow.id })
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('提交验收失败')
  }
}

const advanceWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm('确定要推进到下一节点吗？', '提示', { type: 'warning' })
    await request.post(`/workflows/${row.id}/advance`, {})
    ElMessage.success('推进成功')
    loadWorkflows()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('推进失败')
  }
}

const handleCommand = async (command, row) => {
  try {
    if (command === 'pause') {
      await request.post(`/workflows/${row.id}/pause`)
      ElMessage.success('已暂停')
    } else if (command === 'resume') {
      await request.post(`/workflows/${row.id}/resume`)
      ElMessage.success('已恢复')
    }
    loadWorkflows()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// ========== 辅助函数 ==========

const moduleLabel = (mod) => {
  const labels = { customer: '客户', material: '物料', finance: '财务', quote: '报价', contract: '合同' }
  return labels[mod] || mod
}

const financeTypeLabel = (type) => {
  const labels = { deposit: '定金', first_payment: '首付款', progress: '进度款', final: '尾款', quality: '质保金' }
  return labels[type] || type || '-'
}

const phaseColor = (code) => {
  const phase = phases.value.find(p => p.code === code)
  return phase?.color || '#999'
}

const phaseName = (code) => {
  const phase = phases.value.find(p => p.code === code)
  return phase?.name || code
}

const workflowStatusType = (s) => {
  return { active: 'success', paused: 'warning', completed: 'info', cancelled: 'danger' }[s] || 'info'
}

const workflowStatusLabel = (s) => {
  return { active: '进行中', paused: '已暂停', completed: '已完成', cancelled: '已取消' }[s] || s
}

const recordStatusType = (s) => {
  return { pending: 'info', processing: 'warning', submitted: 'warning', completed: 'success', skipped: 'info' }[s] || 'info'
}

const recordStatusLabel = (s) => {
  return { pending: '待处理', processing: '进行中', submitted: '待验收', completed: '已完成', skipped: '已跳过' }[s] || s
}

const progressStatus = (p) => {
  if (p >= 100) return 'success'
  if (p >= 50) return ''
  return 'exception'
}

const formatDateTime = (dt) => {
  return dt ? new Date(dt).toLocaleString('zh-CN') : '-'
}

onMounted(() => {
  loadPhases()
  loadNodes()
  loadWorkflows()
})
</script>

<style scoped>
.service-workflow { padding: 24px; }

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px;
}
.header-left { display: flex; align-items: baseline; gap: 12px; }
.header-left h2 { margin: 0; font-size: 24px; font-weight: 600; }
.header-right { display: flex; align-items: center; }
.subtitle { color: #8c8c8c; font-size: 14px; }

.stats-row { margin-bottom: 24px; }

.stat-card {
  background: #fff; border-radius: 8px; padding: 16px;
  border-left: 4px solid; box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  cursor: pointer; transition: all 0.2s;
}
.stat-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.stat-card.active { box-shadow: 0 2px 12px rgba(0,0,0,0.15); }

.stat-title { font-size: 12px; color: #8c8c8c; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: 600; color: #262626; line-height: 1; }
.stat-nodes { font-size: 12px; color: #bfbfbf; margin-top: 4px; }

.phase-color-picker { margin-top: 8px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.role-tag { margin-right: 4px; margin-bottom: 2px; }
.mono { font-family: monospace; font-size: 12px; color: #8c8c8c; }

.node-cards {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.node-card { cursor: pointer; transition: all 0.3s; }
.node-card:hover { transform: translateY(-2px); }
.node-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.node-code { font-size: 12px; color: #8c8c8c; font-family: monospace; }
.node-name { font-weight: 500; color: #262626; margin-bottom: 8px; }
.node-roles { margin-bottom: 8px; }
.node-module { font-size: 12px; color: #bfbfbf; }

.workflow-list { margin-top: 24px; }
.customer-info .customer-name { font-weight: 500; color: #262626; }
.customer-info .customer-id { font-size: 12px; color: #8c8c8c; }
.progress-text { font-size: 12px; color: #8c8c8c; margin-top: 4px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }

.phase-preview { margin-top: 16px; }
.phase-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.phase-dot { width: 12px; height: 12px; border-radius: 50%; }
.phase-name { flex: 1; color: #262626; }
.phase-nodes { font-size: 12px; color: #8c8c8c; }

.workflow-detail { padding: 16px; }
.records-section { margin-top: 24px; }
.records-section h4 { margin-bottom: 16px; color: #262626; }
.record-item { padding: 8px; }
.record-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.record-actions { display: inline-flex; align-items: center; gap: 8px; }
.record-header .node-name { font-weight: 500; }
.record-content { font-size: 13px; color: #595959; background: #f5f5f5; padding: 8px; border-radius: 4px; margin-top: 8px; }
</style>
