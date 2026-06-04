<template>
  <div class="points-manage">
    <!-- 顶部统计 -->
    <div class="stats-row">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-value">{{ stats.totalRules }}</div>
        <div class="stat-label">积分规则</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-value">{{ stats.activeRules }}</div>
        <div class="stat-label">启用规则</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-value">{{ stats.pendingAudits }}</div>
        <div class="stat-label">待审核</div>
      </el-card>
      <el-card shadow="hover" class="stat-card">
        <div class="stat-value">{{ stats.totalEmployees }}</div>
        <div class="stat-label">参与员工</div>
      </el-card>
    </div>

    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 积分规则 -->
      <el-tab-pane label="积分规则" name="rules">
        <div class="toolbar">
          <el-select v-model="ruleFilter.category" placeholder="分类筛选" clearable style="width: 120px" @change="loadRules">
            <el-option label="获客" value="获客" />
            <el-option label="转化" value="转化" />
            <el-option label="成交" value="成交" />
            <el-option label="施工" value="施工" />
            <el-option label="售后" value="售后" />
          </el-select>
          <el-button type="primary" @click="openRuleDialog()">
            <el-icon><Plus /></el-icon> 新建规则
          </el-button>
        </div>
        <el-table :data="rules" stripe>
          <el-table-column prop="action_key" label="动作标识" width="150" />
          <el-table-column prop="action_name" label="动作名称" width="180" />
          <el-table-column prop="category" label="分类" width="80">
            <template #default="{ row }">
              <el-tag :type="categoryTagType(row.category)">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="points" label="积分" width="80" />
          <el-table-column prop="unit" label="单位" width="60" />
          <el-table-column label="高客单叠加" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.high_value_enabled" type="success">启用</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="需审核" width="80">
            <template #default="{ row }">
              {{ row.is_auditable ? '是' : '否' }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-switch v-model="row.is_active" @change="toggleRuleStatus(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="openRuleDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteRule(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 积分审核 -->
      <el-tab-pane label="积分审核" name="audit">
        <div class="toolbar">
          <el-select v-model="auditFilter.status" placeholder="状态筛选" style="width: 120px" @change="loadAudits">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </div>
        <el-table :data="audits" stripe>
          <el-table-column prop="employee_name" label="申请人" width="100" />
          <el-table-column prop="action_name" label="动作" width="180" />
          <el-table-column prop="category" label="分类" width="80">
            <template #default="{ row }">
              <el-tag :type="categoryTagType(row.category)">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="points_applied" label="申请积分" width="100" />
          <el-table-column label="凭证" width="80">
            <template #default="{ row }">
              <el-link v-if="row.proof_url" :href="row.proof_url" target="_blank" type="primary">查看</el-link>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'pending'" type="warning">待审核</el-tag>
              <el-tag v-else-if="row.status === 'approved'" type="success">已通过</el-tag>
              <el-tag v-else-if="row.status === 'rejected'" type="danger">已驳回</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <template v-if="row.status === 'pending'">
                <el-button type="success" size="small" @click="approveAudit(row)">通过</el-button>
                <el-button type="danger" size="small" @click="openRejectDialog(row)">驳回</el-button>
              </template>
              <span v-else>{{ row.audited_by_name || '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 员工积分 -->
      <el-tab-pane label="员工积分" name="employees">
        <div class="toolbar">
          <el-input v-model="empFilter.keyword" placeholder="搜索员工" style="width: 200px" clearable @keyup.enter="loadEmployeePoints" />
          <el-button @click="loadEmployeePoints">查询</el-button>
        </div>
        <el-table :data="employeePoints" stripe>
          <el-table-column prop="employee_name" label="员工" width="120" />
          <el-table-column prop="position" label="岗位" width="120" />
          <el-table-column prop="current_points" label="当前积分" width="120">
            <template #default="{ row }">
              <span class="points-value">{{ row.current_points?.toFixed(0) || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_earned" label="累计获得" width="120">
            <template #default="{ row }">
              {{ row.total_earned?.toFixed(0) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="total_used" label="累计使用" width="120">
            <template #default="{ row }">
              {{ row.total_used?.toFixed(0) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="level_name" label="等级" width="80">
            <template #default="{ row }">
              <el-tag :type="levelTagType(row.level)">{{ row.level_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEmployeeDetail(row)">明细</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 团建申请 -->
      <el-tab-pane label="团建申请" name="building">
        <div class="toolbar">
          <el-select v-model="buildingFilter.status" placeholder="状态筛选" clearable style="width: 120px" @change="loadBuildings">
            <el-option label="投票中" value="voting" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已完成" value="completed" />
          </el-select>
          <el-button type="primary" @click="openBuildingDialog()">
            <el-icon><Plus /></el-icon> 发起团建
          </el-button>
        </div>
        <el-table :data="buildings" stripe>
          <el-table-column prop="team_name" label="团队" width="150" />
          <el-table-column prop="leader_name" label="负责人" width="100" />
          <el-table-column prop="member_count" label="人数" width="80" />
          <el-table-column prop="total_points_required" label="所需积分" width="120" />
          <el-table-column prop="fund_amount" label="团建基金" width="120">
            <template #default="{ row }">
              ¥{{ row.fund_amount?.toFixed(0) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="buildingStatusType(row.status)">{{ buildingStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="openBuildingDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 规则编辑对话框 -->
    <el-dialog v-model="ruleDialogVisible" :title="ruleForm.id ? '编辑规则' : '新建规则'" width="600px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="动作标识" required>
          <el-input v-model="ruleForm.action_key" placeholder="唯一标识，如：building_survey" />
        </el-form-item>
        <el-form-item label="动作名称" required>
          <el-input v-model="ruleForm.action_name" placeholder="如：楼盘调查" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="ruleForm.category" placeholder="选择分类">
            <el-option label="获客" value="获客" />
            <el-option label="转化" value="转化" />
            <el-option label="成交" value="成交" />
            <el-option label="施工" value="施工" />
            <el-option label="售后" value="售后" />
          </el-select>
        </el-form-item>
        <el-form-item label="积分值" required>
          <el-input-number v-model="ruleForm.points" :min="0" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="ruleForm.unit" placeholder="次/条/人/单" />
        </el-form-item>
        <el-form-item label="需审核">
          <el-switch v-model="ruleForm.is_auditable" />
        </el-form-item>
        <el-form-item label="需凭证">
          <el-switch v-model="ruleForm.requires_proof" />
        </el-form-item>
        <el-form-item label="启用高客单">
          <el-switch v-model="ruleForm.high_value_enabled" />
        </el-form-item>
        <el-form-item v-if="ruleForm.high_value_enabled" label="高客单阈值">
          <div class="threshold-list">
            <div v-for="(th, idx) in ruleForm.thresholds" :key="idx" class="threshold-item">
              <el-input-number v-model="th.min" :min="0" placeholder="最低" style="width: 100px" />
              ~
              <el-input-number v-model="th.max" :min="0" placeholder="最高" style="width: 100px" />
              奖励
              <el-input-number v-model="th.bonus" :min="0" style="width: 80px" />
              分
              <el-button link type="danger" @click="ruleForm.thresholds.splice(idx, 1)">删除</el-button>
            </div>
            <el-button size="small" @click="ruleForm.thresholds.push({min:0,max:0,bonus:0})">添加阈值</el-button>
          </div>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="ruleForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>

    <!-- 驳回对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="驳回原因" width="400px">
      <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="请填写驳回原因（必填）" />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="rejectAudit">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 员工积分明细对话框 -->
    <el-dialog v-model="empDetailVisible" title="积分明细" width="800px">
      <el-table :data="empTransactions" stripe max-height="400">
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'earn'" type="success">获取</el-tag>
            <el-tag v-else-if="row.type === 'use'" type="warning">使用</el-tag>
            <el-tag v-else>调整</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="100">
          <template #default="{ row }">
            <span :class="row.points > 0 ? 'points-positive' : 'points-negative'">
              {{ row.points > 0 ? '+' : '' }}{{ row.points }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 统计
const stats = reactive({
  totalRules: 0,
  activeRules: 0,
  pendingAudits: 0,
  totalEmployees: 0
})

// Tab
const activeTab = ref('rules')

// ===== 规则 =====
const rules = ref([])
const ruleFilter = reactive({ category: '' })
const ruleDialogVisible = ref(false)
const ruleForm = reactive({
  id: null,
  action_key: '',
  action_name: '',
  category: '获客',
  points: 0,
  unit: '次',
  is_auditable: true,
  requires_proof: false,
  high_value_enabled: false,
  thresholds: [],
  description: ''
})

const loadRules = async () => {
  const res = await request.get('/hr/points/rules', { params: ruleFilter })
  if (res.data?.ok) {
    rules.value = res.data.data || []
    stats.totalRules = rules.value.length
    stats.activeRules = rules.value.filter(r => r.is_active).length
  }
}

const openRuleDialog = (row) => {
  if (row) {
    Object.assign(ruleForm, row)
  } else {
    Object.assign(ruleForm, {
      id: null,
      action_key: '',
      action_name: '',
      category: '获客',
      points: 0,
      unit: '次',
      is_auditable: true,
      requires_proof: false,
      high_value_enabled: false,
      thresholds: [],
      description: ''
    })
  }
  ruleDialogVisible.value = true
}

const saveRule = async () => {
  if (!ruleForm.action_key || !ruleForm.action_name || !ruleForm.category) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    if (ruleForm.id) {
      await request.put(`/hr/points/rules/${ruleForm.id}`, ruleForm)
    } else {
      await request.post('/hr/points/rules', ruleForm)
    }
    ElMessage.success('保存成功')
    ruleDialogVisible.value = false
    loadRules()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  }
}

const toggleRuleStatus = async (row) => {
  try {
    await request.put(`/hr/points/rules/${row.id}`, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch (e) {
    row.is_active = !row.is_active
    ElMessage.error('操作失败')
  }
}

const deleteRule = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该规则？', '提示', { type: 'warning' })
    await request.delete(`/hr/points/rules/${row.id}`)
    ElMessage.success('删除成功')
    loadRules()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 审核 =====
const audits = ref([])
const auditFilter = reactive({ status: 'pending' })
const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const currentAudit = ref(null)

const loadAudits = async () => {
  const res = await request.get('/hr/points/audit', { params: auditFilter })
  if (res.data?.ok) {
    audits.value = res.data.data?.items || []
    if (auditFilter.status === 'pending') {
      stats.pendingAudits = res.data.data?.total || 0
    }
  }
}

const approveAudit = async (row) => {
  try {
    await request.post(`/hr/points/audit/${row.id}/approve`)
    ElMessage.success('审核通过，积分已发放')
    loadAudits()
    loadEmployeePoints()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '审核失败')
  }
}

const openRejectDialog = (row) => {
  currentAudit.value = row
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

const rejectAudit = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  try {
    await request.post(`/hr/points/audit/${currentAudit.value.id}/reject`, { reject_reason: rejectReason.value })
    ElMessage.success('已驳回')
    rejectDialogVisible.value = false
    loadAudits()
  } catch (e) {
    ElMessage.error('驳回失败')
  }
}

// ===== 员工积分 =====
const employeePoints = ref([])
const empFilter = reactive({ keyword: '' })
const empDetailVisible = ref(false)
const empTransactions = ref([])

const loadEmployeePoints = async () => {
  const res = await request.get('/hr/points/rank', { params: { limit: 100 } })
  if (res.data?.ok) {
    employeePoints.value = res.data.data || []
    stats.totalEmployees = employeePoints.value.length
  }
}

const openEmployeeDetail = async (row) => {
  const res = await request.get(`/hr/me/points/detail`, { params: { employee_id: row.employee_id, page_size: 100 } })
  if (res.data?.ok) {
    empTransactions.value = res.data.data?.items || []
    empDetailVisible.value = true
  }
}

// ===== 团建 =====
const buildings = ref([])
const buildingFilter = reactive({ status: '' })

const loadBuildings = async () => {
  const res = await request.get('/hr/team-building', { params: buildingFilter })
  if (res.data?.ok) {
    buildings.value = res.data.data?.items || []
  }
}

const openBuildingDialog = () => {
  ElMessage.info('团建申请功能开发中')
}

const openBuildingDetail = (row) => {
  ElMessage.info('团建详情功能开发中')
}

// ===== 工具函数 =====
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '-'

const categoryTagType = (c) => {
  const map = { '获客': 'primary', '转化': 'success', '成交': 'warning', '施工': 'info', '售后': 'danger' }
  return map[c] || ''
}

const levelTagType = (l) => {
  const map = { 1: '', 2: 'info', 3: 'success', 4: 'warning', 5: 'danger', 6: 'primary' }
  return map[l] || ''
}

const buildingStatusType = (s) => {
  const map = { voting: 'info', pending: 'warning', approved: 'success', completed: 'primary', rejected: 'danger' }
  return map[s] || ''
}

const buildingStatusText = (s) => {
  const map = { voting: '投票中', pending: '待审核', approved: '已通过', completed: '已完成', rejected: '已驳回' }
  return map[s] || s
}

onMounted(() => {
  loadRules()
  loadAudits()
  loadEmployeePoints()
  loadBuildings()
})
</script>

<style scoped>
.points-manage {
  padding: 0;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409EFF;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.main-tabs {
  margin-top: 0;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.points-value {
  font-weight: 600;
  color: #409EFF;
}

.points-positive {
  color: #67C23A;
}

.points-negative {
  color: #F56C6C;
}

.threshold-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.threshold-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
