<template>
  <div class="customer-detail">
    <!-- 返回按钮 -->
    <div class="page-header">
      <el-button link @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回客户列表
      </el-button>
    </div>

    <!-- 客户头部信息 -->
    <el-card class="customer-header" v-if="customer">
      <div class="header-content">
        <div class="customer-basic">
          <h2>{{ customer.name }}</h2>
          <div class="customer-tags">
            <el-tag :type="getTypeTagType(customer.customer_type)">
              {{ customer.customer_type }}
            </el-tag>
            <el-tag :type="getStatusTagType(customer.status)">
              {{ customer.status }}
            </el-tag>
            <el-tag v-if="customer.priority" effect="plain">
              {{ customer.priority }}
            </el-tag>
          </div>
        </div>
        <div class="customer-actions">
          <el-button @click="openEditDialog">编辑客户</el-button>
          <el-button type="primary" @click="openCreateWorkflowDialog" v-if="!hasActiveWorkflow">
            创建服务流程
          </el-button>
        </div>
      </div>

      <el-descriptions :column="4" border class="customer-info">
        <el-descriptions-item label="联系电话">{{ customer.phone }}</el-descriptions-item>
        <el-descriptions-item label="微信">{{ customer.wechat || '-' }}</el-descriptions-item>
        <el-descriptions-item label="楼盘">{{ customer.building_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="户型">{{ customer.house_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="面积">{{ customer.house_area ? customer.house_area + '㎡' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="预算">{{ customer.budget || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ customer.source || '-' }}</el-descriptions-item>
        <el-descriptions-item label="跟进人">{{ customer.owner_name || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="customer-extra" v-if="customer.requirements || customer.style_preference">
        <div v-if="customer.style_preference" class="extra-item">
          <span class="label">风格偏好：</span>
          <span class="value">{{ customer.style_preference }}</span>
        </div>
        <div v-if="customer.requirements" class="extra-item">
          <span class="label">装修需求：</span>
          <span class="value">{{ customer.requirements }}</span>
        </div>
      </div>
    </el-card>

    <!-- Tab 切换 -->
    <el-card class="detail-tabs">
      <el-tabs v-model="activeTab">
        <!-- 服务流程 Tab -->
        <el-tab-pane label="服务流程" name="workflow">
          <div v-if="!workflows.length" class="empty-workflow">
            <el-empty description="暂无服务流程">
              <el-button type="primary" @click="openCreateWorkflowDialog">创建流程</el-button>
            </el-empty>
          </div>

          <div v-else class="workflow-section">
            <!-- 流程列表 -->
            <div class="workflow-list">
              <div
                v-for="wf in workflows"
                :key="wf.id"
                class="workflow-item"
                :class="{ active: selectedWorkflow?.id === wf.id }"
                @click="selectWorkflow(wf)"
              >
                <div class="workflow-header">
                  <span class="workflow-id">流程 #{{ wf.id }}</span>
                  <el-tag :type="workflowStatusType(wf.status)" size="small">
                    {{ workflowStatusLabel(wf.status) }}
                  </el-tag>
                </div>
                <div class="workflow-progress">
                  <el-progress :percentage="wf.progress.percentage" :stroke-width="8" />
                  <span class="progress-text">{{ wf.progress.completed }}/{{ wf.progress.total }}</span>
                </div>
                <div class="workflow-meta">
                  <span>开工: {{ formatDate(wf.start_date) }}</span>
                  <span>当前: {{ wf.current_node_name }}</span>
                </div>
              </div>
            </div>

            <!-- 流程详情 -->
            <div v-if="selectedWorkflow" class="workflow-detail">
              <div class="detail-header">
                <h4>节点执行记录</h4>
                <div class="header-actions">
                  <el-button
                    v-if="selectedWorkflow.status === 'active'"
                    type="primary"
                    size="small"
                    @click="advanceWorkflow"
                  >
                    推进到下一节点
                  </el-button>
                  <el-button
                    v-if="selectedWorkflow.status === 'active'"
                    size="small"
                    @click="pauseWorkflow"
                  >
                    暂停
                  </el-button>
                  <el-button
                    v-if="selectedWorkflow.status === 'paused'"
                    type="success"
                    size="small"
                    @click="resumeWorkflow"
                  >
                    恢复
                  </el-button>
                </div>
              </div>

              <!-- 节点时间轴 -->
              <el-timeline class="node-timeline">
                <el-timeline-item
                  v-for="record in workflowRecords"
                  :key="record.id"
                  :type="recordStatusType(record.status)"
                  :timestamp="formatDateTime(record.created_at)"
                  placement="top"
                >
                  <el-card shadow="hover" class="node-card">
                    <div class="node-header">
                      <div class="node-title">
                        <span class="node-code">{{ record.node_code }}</span>
                        <span class="node-name">{{ record.node_name }}</span>
                      </div>
                      <el-tag :type="recordStatusType(record.status)" size="small">
                        {{ recordStatusLabel(record.status) }}
                      </el-tag>
                    </div>

                    <div class="node-info">
                      <div v-if="record.assigned_name" class="info-item">
                        <span class="label">负责人：</span>
                        <span class="value">{{ record.assigned_name }}</span>
                      </div>
                      <div v-if="record.executor_name" class="info-item">
                        <span class="label">执行人：</span>
                        <span class="value">{{ record.executor_name }}</span>
                      </div>
                      <div v-if="record.deadline" class="info-item">
                        <span class="label">截止时间：</span>
                        <span class="value" :class="{ overdue: isOverdue(record) }">
                          {{ formatDateTime(record.deadline) }}
                        </span>
                      </div>
                    </div>

                    <div v-if="record.content" class="node-content">
                      {{ record.content }}
                    </div>

                    <div v-if="record.attachments?.length" class="node-attachments">
                      <el-link
                        v-for="(att, idx) in record.attachments"
                        :key="idx"
                        :href="att.url"
                        target="_blank"
                        type="primary"
                      >
                        {{ att.name }}
                      </el-link>
                    </div>

                    <div class="node-actions">
                      <el-button
                        v-if="record.status === 'pending'"
                        type="primary"
                        size="small"
                        @click="openExecuteDialog(record)"
                      >
                        开始执行
                      </el-button>
                      <el-button
                        v-if="record.status === 'processing'"
                        type="success"
                        size="small"
                        @click="openCompleteDialog(record)"
                      >
                        完成节点
                      </el-button>
                      <el-button
                        v-if="record.status === 'pending'"
                        size="small"
                        @click="openAssignDialog(record)"
                      >
                        指派
                      </el-button>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-tab-pane>

        <!-- 跟进记录 Tab -->
        <el-tab-pane label="跟进记录" name="follows">
          <div class="follow-section">
            <div class="follow-form">
              <el-form :model="followForm" label-width="80px">
                <el-form-item label="跟进方式">
                  <el-select v-model="followForm.follow_type" style="width: 200px">
                    <el-option v-for="t in followTypes" :key="t" :label="t" :value="t" />
                  </el-select>
                </el-form-item>
                <el-form-item label="跟进内容">
                  <el-input
                    v-model="followForm.content"
                    type="textarea"
                    :rows="3"
                    placeholder="输入跟进内容..."
                  />
                </el-form-item>
                <el-form-item label="下次跟进">
                  <el-date-picker
                    v-model="followForm.next_follow_at"
                    type="datetime"
                    placeholder="选择下次跟进时间"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="addFollow">添加跟进</el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-divider />

            <el-timeline>
              <el-timeline-item
                v-for="f in follows"
                :key="f.id"
                :timestamp="formatDateTime(f.created_at)"
                placement="top"
              >
                <el-card shadow="hover">
                  <div class="follow-header">
                    <el-tag size="small">{{ f.follow_type }}</el-tag>
                    <span class="follow-operator">{{ f.operator_name }}</span>
                  </div>
                  <div class="follow-content">{{ f.content }}</div>
                  <div v-if="f.next_follow_at" class="follow-next">
                    下次跟进：{{ formatDateTime(f.next_follow_at) }}
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>

            <el-empty v-if="!follows.length" description="暂无跟进记录" />
          </div>
        </el-tab-pane>

        <!-- 基本信息 Tab -->
        <el-tab-pane label="基本信息" name="basic">
          <el-descriptions :column="2" border v-if="customer">
            <el-descriptions-item label="客户ID">{{ customer.id }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(customer.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDateTime(customer.updated_at) }}</el-descriptions-item>
            <el-descriptions-item label="详细地址">{{ customer.detail_address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ customer.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建流程对话框 -->
    <el-dialog v-model="workflowDialog.visible" title="创建服务流程" width="500px">
      <el-form :model="workflowForm" label-width="100px">
        <el-form-item label="开工日期">
          <el-date-picker v-model="workflowForm.start_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划完工">
          <el-date-picker v-model="workflowForm.planned_end_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="workflowForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workflowDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="createWorkflow" :loading="workflowDialog.loading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 执行节点对话框 -->
    <el-dialog v-model="executeDialog.visible" title="执行节点" width="600px">
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="节点">
          <span>{{ executeForm.node_name }}</span>
        </el-form-item>
        <el-form-item label="执行内容">
          <el-input v-model="executeForm.content" type="textarea" :rows="4" placeholder="记录执行内容..." />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="/api/v3/upload/image"
            :on-success="handleUploadSuccess"
            :file-list="executeForm.attachments"
            multiple
          >
            <el-button type="primary">上传附件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="executeNode" :loading="executeDialog.loading">开始执行</el-button>
      </template>
    </el-dialog>

    <!-- 完成节点对话框 -->
    <el-dialog v-model="completeDialog.visible" title="完成节点" width="600px">
      <el-form :model="completeForm" label-width="100px">
        <el-form-item label="节点">
          <span>{{ completeForm.node_name }}</span>
        </el-form-item>
        <el-form-item label="完成内容">
          <el-input v-model="completeForm.content" type="textarea" :rows="4" placeholder="记录完成情况..." />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="/api/v3/upload/image"
            :on-success="handleCompleteUploadSuccess"
            :file-list="completeForm.attachments"
            multiple
          >
            <el-button type="primary">上传附件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeDialog.visible = false">取消</el-button>
        <el-button type="success" @click="completeNode" :loading="completeDialog.loading">确认完成</el-button>
      </template>
    </el-dialog>

    <!-- 指派对话框 -->
    <el-dialog v-model="assignDialog.visible" title="指派负责人" width="400px">
      <el-form :model="assignForm" label-width="100px">
        <el-form-item label="负责人">
          <el-select v-model="assignForm.employee_id" style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="assignForm.deadline" type="datetime" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="assignNode" :loading="assignDialog.loading">指派</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const customerId = computed(() => route.params.id)

const loading = ref(false)
const customer = ref(null)
const workflows = ref([])
const selectedWorkflow = ref(null)
const workflowRecords = ref([])
const follows = ref([])
const employees = ref([])
const activeTab = ref('workflow')

const followTypes = ['电话', '微信', '上门', '面谈', '其他']

const followForm = reactive({
  follow_type: '电话',
  content: '',
  next_follow_at: null
})

// 对话框
const workflowDialog = reactive({ visible: false, loading: false })
const executeDialog = reactive({ visible: false, loading: false })
const completeDialog = reactive({ visible: false, loading: false })
const assignDialog = reactive({ visible: false, loading: false })

const workflowForm = reactive({
  start_date: null,
  planned_end_date: null,
  remark: ''
})

const executeForm = reactive({
  record_id: null,
  node_name: '',
  content: '',
  attachments: []
})

const completeForm = reactive({
  record_id: null,
  node_name: '',
  content: '',
  attachments: []
})

const assignForm = reactive({
  record_id: null,
  employee_id: null,
  deadline: null
})

const hasActiveWorkflow = computed(() => {
  return workflows.value.some(w => w.status === 'active')
})

// 加载客户详情
const loadCustomer = async () => {
  try {
    const res = await request.get(`/customers/${customerId.value}`)
    customer.value = res
    workflows.value = res.workflows || []
    follows.value = res.follows || []

    // 自动选择第一个活跃流程
    const activeWf = workflows.value.find(w => w.status === 'active')
    if (activeWf) {
      selectWorkflow(activeWf)
    }
  } catch (error) {
    ElMessage.error('加载客户详情失败')
  }
}

// 加载员工列表
const loadEmployees = async () => {
  try {
    const res = await request.get('/employees')
    employees.value = res.items || []
  } catch (error) {
    console.error('加载员工失败', error)
  }
}

// 选择流程
const selectWorkflow = async (wf) => {
  selectedWorkflow.value = wf
  try {
    const res = await request.get(`/workflows/${wf.id}`)
    workflowRecords.value = res.node_records || []
  } catch (error) {
    console.error('加载流程记录失败', error)
  }
}

// 创建流程
const openCreateWorkflowDialog = () => {
  workflowDialog.visible = true
}

const createWorkflow = async () => {
  workflowDialog.loading = true
  try {
    await request.post('/workflows', {
      customer_id: parseInt(customerId.value),
      start_date: workflowForm.start_date,
      planned_end_date: workflowForm.planned_end_date
    })
    ElMessage.success('流程创建成功')
    workflowDialog.visible = false
    loadCustomer()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '创建失败')
  } finally {
    workflowDialog.loading = false
  }
}

// 推进流程
const advanceWorkflow = async () => {
  try {
    await ElMessageBox.confirm('确定要推进到下一节点吗？', '提示', { type: 'warning' })
    await request.post(`/workflows/${selectedWorkflow.value.id}/advance`, {})
    ElMessage.success('推进成功')
    selectWorkflow(selectedWorkflow.value)
    loadCustomer()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('推进失败')
  }
}

// 暂停/恢复流程
const pauseWorkflow = async () => {
  try {
    await request.post(`/workflows/${selectedWorkflow.value.id}/pause`)
    ElMessage.success('已暂停')
    loadCustomer()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resumeWorkflow = async () => {
  try {
    await request.post(`/workflows/${selectedWorkflow.value.id}/resume`)
    ElMessage.success('已恢复')
    loadCustomer()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 执行节点
const openExecuteDialog = (record) => {
  executeForm.record_id = record.id
  executeForm.node_name = record.node_name
  executeForm.content = ''
  executeForm.attachments = []
  executeDialog.visible = true
}

const executeNode = async () => {
  executeDialog.loading = true
  try {
    await request.put(`/workflows/records/${executeForm.record_id}`, {
      status: 'processing',
      content: executeForm.content,
      attachments: executeForm.attachments
    })
    ElMessage.success('已开始执行')
    executeDialog.visible = false
    selectWorkflow(selectedWorkflow.value)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    executeDialog.loading = false
  }
}

// 完成节点
const openCompleteDialog = (record) => {
  completeForm.record_id = record.id
  completeForm.node_name = record.node_name
  completeForm.content = ''
  completeForm.attachments = []
  completeDialog.visible = true
}

const completeNode = async () => {
  completeDialog.loading = true
  try {
    await request.put(`/workflows/records/${completeForm.record_id}`, {
      status: 'completed',
      content: completeForm.content,
      attachments: completeForm.attachments
    })
    ElMessage.success('节点已完成')
    completeDialog.visible = false
    selectWorkflow(selectedWorkflow.value)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    completeDialog.loading = false
  }
}

// 指派节点
const openAssignDialog = (record) => {
  assignForm.record_id = record.id
  assignForm.employee_id = null
  assignForm.deadline = null
  assignDialog.visible = true
}

const assignNode = async () => {
  assignDialog.loading = true
  try {
    await request.post(`/workflows/records/${assignForm.record_id}/assign`, {
      employee_id: assignForm.employee_id,
      deadline: assignForm.deadline
    })
    ElMessage.success('指派成功')
    assignDialog.visible = false
    selectWorkflow(selectedWorkflow.value)
  } catch (error) {
    ElMessage.error('指派失败')
  } finally {
    assignDialog.loading = false
  }
}

// 添加跟进
const addFollow = async () => {
  if (!followForm.content) {
    ElMessage.warning('请输入跟进内容')
    return
  }
  try {
    await request.post(`/customers/${customerId.value}/follow`, followForm)
    ElMessage.success('添加成功')
    followForm.content = ''
    followForm.next_follow_at = null
    loadCustomer()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 上传处理
const handleUploadSuccess = (res) => {
  executeForm.attachments.push({ name: res.name, url: res.url })
}

const handleCompleteUploadSuccess = (res) => {
  completeForm.attachments.push({ name: res.name, url: res.url })
}

// 辅助函数
const getStatusTagType = (status) => {
  const map = { '待跟进': 'info', '跟进中': 'warning', '已成交': 'success', '已流失': 'danger' }
  return map[status] || 'info'
}

const getTypeTagType = (type) => {
  const map = { '已接触': 'info', '已拜访': '', '提案已经确认': 'warning', '定金已收': 'success', '已成交': 'success' }
  return map[type] || ''
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

const isOverdue = (record) => {
  if (!record.deadline || record.status === 'completed') return false
  return new Date(record.deadline) < new Date()
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}

const openEditDialog = () => {
  // 可以打开编辑对话框或跳转到编辑页面
  ElMessage.info('编辑功能可通过客户列表页操作')
}

onMounted(() => {
  loadCustomer()
  loadEmployees()
})
</script>

<style scoped>
.customer-detail {
  padding: 24px;
}

.page-header {
  margin-bottom: 16px;
}

.customer-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.customer-basic h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
}

.customer-tags {
  display: flex;
  gap: 8px;
}

.customer-info {
  margin-bottom: 16px;
}

.customer-extra {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
}

.extra-item {
  margin-bottom: 8px;
}

.extra-item:last-child {
  margin-bottom: 0;
}

.extra-item .label {
  color: #8c8c8c;
}

.detail-tabs {
  min-height: 500px;
}

.empty-workflow {
  padding: 60px 0;
}

.workflow-section {
  display: flex;
  gap: 24px;
}

.workflow-list {
  width: 320px;
  flex-shrink: 0;
}

.workflow-item {
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.workflow-item:hover,
.workflow-item.active {
  border-color: #1890ff;
  background: #e6f7ff;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.workflow-id {
  font-weight: 500;
  color: #262626;
}

.workflow-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.workflow-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #8c8c8c;
  white-space: nowrap;
}

.workflow-meta {
  font-size: 12px;
  color: #8c8c8c;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workflow-detail {
  flex: 1;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h4 {
  margin: 0;
}

.node-timeline {
  max-height: 600px;
  overflow-y: auto;
}

.node-card {
  margin-bottom: 8px;
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-code {
  font-size: 12px;
  color: #8c8c8c;
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.node-name {
  font-weight: 500;
  color: #262626;
}

.node-info {
  margin-bottom: 12px;
}

.info-item {
  font-size: 13px;
  margin-bottom: 4px;
}

.info-item .label {
  color: #8c8c8c;
}

.info-item .overdue {
  color: #f5222d;
}

.node-content {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #595959;
}

.node-attachments {
  margin-bottom: 12px;
}

.node-attachments .el-link {
  margin-right: 12px;
}

.node-actions {
  display: flex;
  gap: 8px;
}

.follow-section {
  max-width: 800px;
}

.follow-form {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.follow-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.follow-operator {
  font-size: 12px;
  color: #8c8c8c;
}

.follow-content {
  color: #262626;
  line-height: 1.6;
}

.follow-next {
  font-size: 12px;
  color: #1890ff;
  margin-top: 8px;
}
</style>
