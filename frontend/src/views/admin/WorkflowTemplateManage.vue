<template>
  <div class="workflow-template-manage">
    <!-- 阶段统计卡片（可编辑） -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="phase in phases" :key="phase.code">
        <div
          class="stat-card"
          :class="{ active: activePhase === phase.code }"
          :style="{ borderLeftColor: phase.color }"
          @click="selectPhase(phase.code)"
        >
          <div class="stat-title">
            <el-input
              v-model="phase.name"
              size="small"
              class="inline-edit"
              @blur="updatePhase(phase)"
              @keyup.enter="$event.target.blur()"
            />
          </div>
          <div class="stat-value">{{ phase.node_count || 0 }}</div>
          <div class="stat-nodes">节点</div>
          <div class="phase-color-picker">
            <el-color-picker
              v-model="phase.color"
              size="small"
              @change="updatePhase(phase)"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 节点编辑列表 -->
    <el-card shadow="never" v-if="activePhase">
      <template #header>
        <div class="card-header">
          <span>{{ currentPhaseName }} - 节点管理</span>
          <div>
            <el-button type="primary" size="small" @click="addNode">
              <el-icon><Plus /></el-icon> 新增节点
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="currentNodes" stripe row-key="id">
        <el-table-column label="排序" width="60" align="center">
          <template #default>
            <el-icon class="drag-handle"><Rank /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="编码" prop="node_code" width="90">
          <template #default="{ row }">
            <el-input v-model="row.node_code" size="small" style="width:80px" @blur="updateNode(row)" />
          </template>
        </el-table-column>
        <el-table-column label="节点名称" min-width="180">
          <template #default="{ row }">
            <el-input v-model="row.node_name" size="small" @blur="updateNode(row)" @keyup.enter="$event.target.blur()" />
          </template>
        </el-table-column>
        <el-table-column label="负责角色" width="200">
          <template #default="{ row }">
            <el-select
              v-model="row.responsible_roles"
              multiple
              filterable
              allow-create
              size="small"
              style="width:100%"
              @change="updateNode(row)"
            >
              <el-option v-for="r in allRoles" :key="r" :label="r" :value="r" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="关联模块" width="120">
          <template #default="{ row }">
            <el-select v-model="row.related_module" size="small" clearable @change="updateNode(row)">
              <el-option v-for="m in moduleOptions" :key="m.value" :label="m.label" :value="m.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="描述" min-width="140">
          <template #default="{ row }">
            <el-input v-model="row.description" size="small" placeholder="可选" @blur="updateNode(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editNodeDetail(row)">详情</el-button>
            <el-button link type="danger" size="small" @click="deleteNode(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 初始化按钮（仅在无节点时显示） -->
    <div v-if="!hasNodes" class="init-section">
      <el-alert
        description="尚未初始化流程模板，点击下方按钮创建6阶段58节点全案服务流程"
        type="info"
        show-icon
        :closable="false"
      />
      <el-button type="primary" @click="showInitDialog" style="margin-top:12px">
        <el-icon><Setting /></el-icon> 初始化流程模板
      </el-button>
    </div>

    <!-- 初始化确认对话框 -->
    <el-dialog v-model="initDialog.visible" title="初始化服务流程模板" width="500px" append-to-body>
      <el-alert
        description="将创建6阶段58节点全案服务流程模板，已有节点不会被覆盖。确认继续？"
        type="warning"
        show-icon
        :closable="false"
      />
      <div class="phase-preview" style="margin-top:16px">
        <div v-for="phase in phases" :key="phase.code" class="phase-item">
          <span class="phase-dot" :style="{ background: phase.color }"></span>
          <span class="phase-name">{{ phase.name }}</span>
          <span class="phase-nodes">{{ phase.node_count }} 节点</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="initDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="initNodes" :loading="initDialog.loading">确认初始化</el-button>
      </template>
    </el-dialog>

    <!-- 节点详情编辑对话框 -->
    <el-dialog v-model="nodeDetailDialog.visible" :title="`节点详情 - ${nodeDetailDialog.node?.node_code || ''}`" width="600px" append-to-body>
      <el-form :model="nodeDetailDialog.node" label-width="100px" v-if="nodeDetailDialog.node">
        <el-form-item label="节点编码">
          <el-input v-model="nodeDetailDialog.node.node_code" />
        </el-form-item>
        <el-form-item label="节点名称">
          <el-input v-model="nodeDetailDialog.node.node_name" />
        </el-form-item>
        <el-form-item label="所属阶段">
          <el-select v-model="nodeDetailDialog.node.phase" style="width:100%">
            <el-option v-for="p in phases" :key="p.code" :label="p.name" :value="p.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责角色">
          <el-select v-model="nodeDetailDialog.node.responsible_roles" multiple filterable allow-create style="width:100%">
            <el-option v-for="r in allRoles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联模块">
          <el-select v-model="nodeDetailDialog.node.related_module" clearable style="width:100%">
            <el-option v-for="m in moduleOptions" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="nodeDetailDialog.node.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="财务联动">
          <el-switch v-model="nodeDetailDialog.node.finance_trigger" />
        </el-form-item>
        <el-form-item label="财务类型" v-if="nodeDetailDialog.node.finance_trigger">
          <el-select v-model="nodeDetailDialog.node.finance_type" clearable>
            <el-option label="定金" value="deposit" />
            <el-option label="首付款" value="first_payment" />
            <el-option label="进度款" value="progress" />
            <el-option label="尾款" value="final" />
            <el-option label="质保金" value="quality" />
          </el-select>
        </el-form-item>
        <el-form-item label="输入要求">
          <el-select v-model="nodeDetailDialog.node.input_requirements" multiple filterable allow-create style="width:100%">
          </el-select>
        </el-form-item>
        <el-form-item label="交付物">
          <el-select v-model="nodeDetailDialog.node.output_deliverables" multiple filterable allow-create style="width:100%">
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeDetailDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveNodeDetail">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Rank } from '@element-plus/icons-vue'
import request from '@/utils/request'

const phases = ref([])
const nodes = ref({})
const activePhase = ref('')
const hasNodes = ref(false)

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

const initDialog = reactive({ visible: false, loading: false })
const nodeDetailDialog = reactive({ visible: false, node: null })

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
    hasNodes.value = Object.keys(nodes.value).length > 0
  } catch (e) {
    console.error('加载节点失败', e)
  }
}

const refresh = async () => {
  await Promise.all([loadPhases(), loadNodes()])
}

// ========== 阶段操作 ==========

const selectPhase = (code) => {
  activePhase.value = code
}

const updatePhase = async (phase) => {
  try {
    await request.put(`/workflows/phases/${phase.id}`, {
      name: phase.name,
      color: phase.color
    })
    ElMessage.success('阶段配置已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

// ========== 节点操作 ==========

const addNode = async () => {
  try {
    await request.post('/workflows/nodes', {
      node_name: '新节点',
      phase: activePhase.value,
      responsible_roles: []
    })
    ElMessage.success('节点已添加')
    refresh()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const updateNode = async (node) => {
  try {
    await request.put(`/workflows/nodes/${node.id}`, {
      node_name: node.node_name,
      node_code: node.node_code,
      description: node.description,
      responsible_roles: node.responsible_roles,
      related_module: node.related_module,
      finance_trigger: node.finance_trigger,
      finance_type: node.finance_type
    })
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const deleteNode = async (node) => {
  try {
    await ElMessageBox.confirm(
      `确定删除节点「${node.node_name}」吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await request.delete(`/workflows/nodes/${node.id}`)
    ElMessage.success('已删除')
    refresh()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const editNodeDetail = (node) => {
  nodeDetailDialog.node = JSON.parse(JSON.stringify(node))
  nodeDetailDialog.visible = true
}

const saveNodeDetail = async () => {
  const node = nodeDetailDialog.node
  try {
    await request.put(`/workflows/nodes/${node.id}`, {
      node_name: node.node_name,
      node_code: node.node_code,
      phase: node.phase,
      description: node.description,
      responsible_roles: node.responsible_roles,
      related_module: node.related_module,
      finance_trigger: node.finance_trigger,
      finance_type: node.finance_type,
      input_requirements: node.input_requirements,
      output_deliverables: node.output_deliverables
    })
    ElMessage.success('保存成功')
    nodeDetailDialog.visible = false
    refresh()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

// ========== 初始化 ==========

const showInitDialog = () => { initDialog.visible = true }

const initNodes = async () => {
  initDialog.loading = true
  try {
    await request.post('/workflows/nodes/init')
    ElMessage.success('初始化成功')
    initDialog.visible = false
    refresh()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '初始化失败')
  } finally {
    initDialog.loading = false
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.workflow-template-manage { padding: 0; }

.stats-row { margin-bottom: 20px; }

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
.inline-edit { width: 100px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.role-tag { margin-right: 4px; margin-bottom: 2px; }
.mono { font-family: monospace; font-size: 12px; color: #8c8c8c; }

.init-section { margin-top: 16px; padding: 16px; text-align: center; }

.phase-preview { margin-top: 16px; }
.phase-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.phase-dot { width: 12px; height: 12px; border-radius: 50%; }
.phase-name { flex: 1; color: #262626; }
.phase-nodes { font-size: 12px; color: #8c8c8c; }

.drag-handle { cursor: move; color: #bfbfbf; }
</style>
