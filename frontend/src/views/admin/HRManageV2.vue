<template>
  <div class="hr-manage-v2">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-title">
        <h2>人力资源中心</h2>
        <p class="subtitle">员工关怀 · 成长陪伴 · 价值认可</p>
      </div>
      <el-button type="primary" @click="openEmployeeDialog()">
        <el-icon><Plus /></el-icon>新增员工
      </el-button>
    </div>

    <!-- 关怀仪表盘 -->
    <div class="care-dashboard">
      <el-row :gutter="16">
        <el-col :span="4" v-for="card in careCards" :key="card.type">
          <div class="care-card" :class="card.type" @click="handleCareClick(card)">
            <div class="care-icon">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </div>
            <div class="care-info">
              <div class="care-count">{{ card.count }}</div>
              <div class="care-label">{{ card.label }}</div>
            </div>
            <div v-if="card.trend" class="care-trend" :class="card.trend > 0 ? 'up' : 'down'">
              {{ card.trend > 0 ? '+' : '' }}{{ card.trend }}
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷操作栏 -->
    <el-card class="quick-actions">
      <div class="action-list">
        <div class="action-item" v-for="action in quickActions" :key="action.key" @click="handleQuickAction(action)">
          <el-icon :size="20"><component :is="action.icon" /></el-icon>
          <span>{{ action.label }}</span>
        </div>
      </div>
    </el-card>

    <!-- 员工列表 -->
    <el-card>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="搜索姓名/工号/手机号" clearable style="width: 200px" />
        <el-select v-model="filters.department_id" placeholder="部门" clearable style="width: 150px">
          <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="在职" value="active" />
          <el-option label="试用期" value="probation" />
          <el-option label="离职" value="leave" />
        </el-select>
        <el-select v-model="filters.talent_level" placeholder="人才梯队" clearable style="width: 120px">
          <el-option label="A级-核心" value="A" />
          <el-option label="B级-骨干" value="B" />
          <el-option label="C级-成长" value="C" />
          <el-option label="D级-基础" value="D" />
        </el-select>
        <el-button type="primary" @click="loadEmployees">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <!-- 员工表格 -->
      <el-table :data="employees" v-loading="loading" stripe @row-click="handleRowClick">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="employee-expand">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="expand-section">
                    <h4>积分账户</h4>
                    <div class="points-display">
                      <div class="points-value">{{ row.points?.current_points || 0 }}</div>
                      <div class="points-level">{{ row.points?.level_name || '青铜' }} Lv.{{ row.points?.level || 1 }}</div>
                    </div>
                    <el-button type="primary" link @click="openPointsDetail(row)">查看明细</el-button>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="expand-section">
                    <h4>本月薪酬</h4>
                    <div class="salary-display">
                      <div class="salary-value">¥{{ row.current_salary?.net_salary || 0 }}</div>
                      <div class="salary-status" :class="row.current_salary?.status">
                        {{ {draft: '草稿', calculated: '已计算', confirmed: '已确认', paid: '已发放'}[row.current_salary?.status] || '未生成' }}
                      </div>
                    </div>
                    <el-button type="primary" link @click="openSalaryDetail(row)">薪酬详情</el-button>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="expand-section">
                    <h4>最近绩效</h4>
                    <div class="performance-display">
                      <div class="perf-score">{{ row.latest_performance?.total_score || '-' }}</div>
                      <div class="perf-grade">{{ row.latest_performance?.grade || '暂无' }}</div>
                    </div>
                    <el-button type="primary" link @click="openPerformanceDetail(row)">绩效记录</el-button>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="expand-section">
                    <h4>成长路径</h4>
                    <div class="career-display">
                      <div class="career-path">{{ row.career_path?.path_type || '未设定' }}</div>
                      <div class="career-target">目标: {{ row.career_path?.target_level || '-' }}级</div>
                    </div>
                    <el-button type="primary" link @click="openCareerDetail(row)">发展规划</el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="员工" min-width="180">
          <template #default="{ row }">
            <div class="employee-info">
              <el-avatar :size="40" :src="row.avatar || '/default-avatar.png'" />
              <div class="employee-meta">
                <div class="employee-name">
                  {{ row.name }}
                  <el-tag v-if="row.is_key_talent" type="danger" size="small" effect="dark">核心</el-tag>
                </div>
                <div class="employee-no">{{ row.employee_no }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="部门/岗位" min-width="150">
          <template #default="{ row }">
            <div>{{ row.department_name }}</div>
            <div class="position-name">{{ row.position_name }} · {{ row.job_level }}级</div>
          </template>
        </el-table-column>
        
        <el-table-column label="联系方式" min-width="150">
          <template #default="{ row }">
            <div>{{ row.phone }}</div>
            <div class="email-text">{{ row.email }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="入职信息" width="120">
          <template #default="{ row }">
            <div>{{ row.entry_date }}</div>
            <div class="work-years">{{ getWorkYears(row.entry_date) }}年</div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ {active: '在职', probation: '试用期', leave: '离职'}[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="关怀提醒" width="150">
          <template #default="{ row }">
            <div class="care-reminders">
              <el-tag v-if="isBirthdaySoon(row.birthday)" type="warning" size="small" effect="dark">
                <el-icon><Present /></el-icon>生日临近
              </el-tag>
              <el-tag v-if="isAnniversarySoon(row.entry_date)" type="success" size="small" effect="dark" style="margin-top: 4px">
                <el-icon><Trophy /></el-icon>入职周年
              </el-tag>
              <el-tag v-if="row.probation_end_date && isProbationEnding(row.probation_end_date)" type="info" size="small" style="margin-top: 4px">
                <el-icon><Calendar /></el-icon>即将转正
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="openEmployeeDialog(row)">编辑</el-button>
            <el-dropdown @command="(cmd) => handleMoreAction(cmd, row)">
              <el-button type="primary" link>更多<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="salary">薪酬管理</el-dropdown-item>
                  <el-dropdown-item command="performance">绩效考核</el-dropdown-item>
                  <el-dropdown-item command="points">积分明细</el-dropdown-item>
                  <el-dropdown-item command="career">发展规划</el-dropdown-item>
                  <el-dropdown-item command="training">培训记录</el-dropdown-item>
                  <el-dropdown-item command="welfare">福利记录</el-dropdown-item>
                  <el-dropdown-item divided command="archive">员工档案</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="loadEmployees"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 员工编辑对话框 -->
    <el-dialog v-model="employeeDialog.visible" :title="employeeDialog.isEdit ? '编辑员工' : '新增员工'" width="700px">
      <el-form :model="employeeDialog.form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="employeeDialog.form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" required>
              <el-input v-model="employeeDialog.form.employee_no" placeholder="如: VM001" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门" required>
              <el-cascader
                v-model="employeeDialog.form.department_id"
                :options="departmentTree"
                :props="{ value: 'id', label: 'name', checkStrictly: true, emitPath: false }"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位">
              <el-select v-model="employeeDialog.form.position_id" style="width: 100%">
                <el-option v-for="pos in positions" :key="pos.id" :label="pos.name" :value="pos.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职级">
              <el-input-number v-model="employeeDialog.form.job_level" :min="1" :max="15" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期">
              <el-date-picker v-model="employeeDialog.form.entry_date" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="employeeDialog.form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="employeeDialog.form.email" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="关键人才">
          <el-switch v-model="employeeDialog.form.is_key_talent" />
          <span style="margin-left: 10px; color: #909399">标记为核心骨干员工</span>
        </el-form-item>
        
        <el-form-item label="人才梯队">
          <el-radio-group v-model="employeeDialog.form.talent_level">
            <el-radio-button value="A">A级-核心</el-radio-button>
            <el-radio-button value="B">B级-骨干</el-radio-button>
            <el-radio-button value="C">C级-成长</el-radio-button>
            <el-radio-button value="D">D级-基础</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="employeeDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveEmployee" :loading="employeeDialog.saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 薪酬管理对话框 -->
    <el-dialog v-model="salaryDialog.visible" title="薪酬管理" width="900px">
      <div v-if="salaryDialog.employee" class="salary-header">
        <el-avatar :size="50" :src="salaryDialog.employee.avatar" />
        <div class="salary-employee-info">
          <div class="name">{{ salaryDialog.employee.name }}</div>
          <div class="meta">{{ salaryDialog.employee.department_name }} · {{ salaryDialog.employee.position_name }}</div>
        </div>
        <div class="salary-actions">
          <el-button type="primary" @click="openSalaryCalc">计算本月薪酬</el-button>
          <el-button type="success" @click="confirmSalary">确认发放</el-button>
        </div>
      </div>
      
      <el-table :data="salaryDialog.records" border style="margin-top: 20px">
        <el-table-column prop="period" label="月份" width="100" />
        <el-table-column label="应发" min-width="300">
          <template #default="{ row }">
            <div class="salary-breakdown">
              <span>基本:{{ row.base_salary }}</span>
              <span>岗位:{{ row.position_allowance }}</span>
              <span>绩效:{{ row.performance_allowance }}</span>
              <span>工龄:{{ row.seniority_allowance }}</span>
              <span>提成:{{ row.commission }}</span>
              <span>奖金:{{ row.project_bonus }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="gross_salary" label="应发合计" width="100" />
        <el-table-column prop="net_salary" label="实发工资" width="100">
          <template #default="{ row }">
            <strong style="color: #8B5A2B">¥{{ row.net_salary }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="{draft: 'info', calculated: 'warning', confirmed: 'primary', paid: 'success'}[row.status]" size="small">
              {{ {draft: '草稿', calculated: '已算', confirmed: '已确认', paid: '已发'}[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Present, Trophy, Calendar, Star, Medal, 
  Wallet, TrendCharts, UserFilled, ArrowDown 
} from '@element-plus/icons-vue'
import request from '@/api/request'

// 关怀卡片数据
const careCards = ref([
  { type: 'birthday', icon: 'Present', label: '本月生日', count: 3, trend: 1 },
  { type: 'anniversary', icon: 'Trophy', label: '入职周年', count: 5, trend: -2 },
  { type: 'probation', icon: 'Calendar', label: '即将转正', count: 2, trend: 0 },
  { type: 'performance', icon: 'Star', label: '待考核', count: 8, trend: 3 },
  { type: 'points', icon: 'Medal', label: '积分达人', count: 12, trend: 5 },
  { type: 'training', icon: 'UserFilled', label: '培训计划', count: 6, trend: 1 }
])

// 快捷操作
const quickActions = ref([
  { key: 'salary_batch', icon: 'Wallet', label: '批量算薪' },
  { key: 'performance_batch', icon: 'TrendCharts', label: '绩效考核' },
  { key: 'points_award', icon: 'Medal', label: '积分奖励' },
  { key: 'welfare_grant', icon: 'Present', label: '福利发放' },
  { key: 'training_arrange', icon: 'UserFilled', label: '培训安排' },
  { key: 'career_plan', icon: 'Star', label: '发展规划' }
])

// 筛选条件
const filters = reactive({
  keyword: '',
  department_id: null,
  status: 'active',
  talent_level: null
})

// 数据列表
const employees = ref([])
const departments = ref([])
const departmentTree = ref([])
const positions = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

// 对话框
const employeeDialog = reactive({
  visible: false,
  isEdit: false,
  saving: false,
  form: {}
})

const salaryDialog = reactive({
  visible: false,
  employee: null,
  records: []
})

// 加载员工列表
const loadEmployees = async () => {
  loading.value = true
  try {
    const res = await request.get('/hr/employees', {
      params: { ...filters, ...pagination }
    })
    employees.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载员工列表失败')
  } finally {
    loading.value = false
  }
}

// 加载部门和岗位
const loadDepartments = async () => {
  try {
    const res = await request.get('/hr/departments')
    departments.value = res || []
    departmentTree.value = buildTree(res || [])
  } catch (error) {
    console.error('加载部门失败', error)
  }
}

const loadPositions = async () => {
  try {
    const res = await request.get('/hr/positions')
    positions.value = res || []
  } catch (error) {
    console.error('加载岗位失败', error)
  }
}

// 构建部门树
const buildTree = (list, parentId = null) => {
  return list
    .filter(item => item.parent_id === parentId)
    .map(item => ({
      ...item,
      children: buildTree(list, item.id)
    }))
}

// 打开员工编辑对话框
const openEmployeeDialog = (row = null) => {
  employeeDialog.isEdit = !!row
  employeeDialog.form = row ? { ...row, job_level: Number(row.job_level) || 1 } : {
    name: '',
    employee_no: '',
    department_id: null,
    position_id: null,
    job_level: 1,
    is_key_talent: false,
    talent_level: 'C'
  }
  employeeDialog.visible = true
}

// 保存员工
const saveEmployee = async () => {
  employeeDialog.saving = true
  try {
    if (employeeDialog.isEdit) {
      await request.put(`/hr/employees/${employeeDialog.form.id}`, employeeDialog.form)
    } else {
      await request.post('/hr/employees', employeeDialog.form)
    }
    ElMessage.success('保存成功')
    employeeDialog.visible = false
    loadEmployees()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    employeeDialog.saving = false
  }
}

// 更多操作
const handleMoreAction = (cmd, row) => {
  switch (cmd) {
    case 'salary':
      openSalaryDialog(row)
      break
    case 'performance':
      ElMessage.info('绩效考核功能开发中')
      break
    case 'points':
      ElMessage.info('积分明细功能开发中')
      break
    case 'career':
      ElMessage.info('发展规划功能开发中')
      break
    default:
      ElMessage.info(`${cmd} 功能开发中`)
  }
}

// 薪酬管理
const openSalaryDialog = async (row) => {
  salaryDialog.employee = row
  salaryDialog.visible = true
  try {
    const res = await request.get(`/hr/employees/${row.id}/salaries`)
    salaryDialog.records = res || []
  } catch (error) {
    console.error('加载薪酬记录失败', error)
  }
}

// 关怀提醒判断
const isBirthdaySoon = (birthday) => {
  if (!birthday) return false
  const today = new Date()
  const birth = new Date(birthday)
  const thisYearBirth = new Date(today.getFullYear(), birth.getMonth(), birth.getDate())
  const diff = Math.ceil((thisYearBirth - today) / (1000 * 60 * 60 * 24))
  return diff >= 0 && diff <= 7
}

const isAnniversarySoon = (entryDate) => {
  if (!entryDate) return false
  const today = new Date()
  const entry = new Date(entryDate)
  const thisYearAnniv = new Date(today.getFullYear(), entry.getMonth(), entry.getDate())
  const diff = Math.ceil((thisYearAnniv - today) / (1000 * 60 * 60 * 24))
  return diff >= 0 && diff <= 14
}

const isProbationEnding = (endDate) => {
  if (!endDate) return false
  const today = new Date()
  const end = new Date(endDate)
  const diff = Math.ceil((end - today) / (1000 * 60 * 60 * 24))
  return diff >= 0 && diff <= 7
}

const getWorkYears = (entryDate) => {
  if (!entryDate) return 0
  const today = new Date()
  const entry = new Date(entryDate)
  return today.getFullYear() - entry.getFullYear()
}

const handleRowClick = (row) => {
  openEmployeeDialog(row)
}

const getStatusType = (status) => {
  const map = { active: 'success', probation: 'warning', leave: 'info' }
  return map[status] || 'info'
}

const handleQuickAction = (action) => {
  switch (action.key) {
    case 'salary_batch':
      ElMessage.info('批量算薪功能开发中')
      break
    case 'performance_batch':
      ElMessage.info('绩效考核功能开发中')
      break
    case 'points_award':
      ElMessage.info('积分奖励功能开发中')
      break
    case 'welfare_grant':
      ElMessage.info('福利发放功能开发中')
      break
    case 'training_arrange':
      ElMessage.info('培训安排功能开发中')
      break
    case 'career_plan':
      ElMessage.info('发展规划功能开发中')
      break
    default:
      break
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.department_id = null
  filters.status = 'active'
  filters.talent_level = null
  loadEmployees()
}

onMounted(() => {
  loadEmployees()
  loadDepartments()
  loadPositions()
})
</script>

<style scoped>
.hr-manage-v2 {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
}

.header-title .subtitle {
  margin: 5px 0 0;
  color: #909399;
  font-size: 13px;
}

/* 关怀仪表盘 */
.care-dashboard {
  margin-bottom: 20px;
}

.care-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #ebeef5;
}

.care-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.care-card.birthday { border-left: 4px solid #e6a23c; }
.care-card.anniversary { border-left: 4px solid #67c23a; }
.care-card.probation { border-left: 4px solid #909399; }
.care-card.performance { border-left: 4px solid #409eff; }
.care-card.points { border-left: 4px solid #8B5A2B; }
.care-card.training { border-left: 4px solid #f56c6c; }

.care-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.care-card.birthday .care-icon { background: #fdf6ec; color: #e6a23c; }
.care-card.anniversary .care-icon { background: #f0f9eb; color: #67c23a; }
.care-card.probation .care-icon { background: #f4f4f5; color: #909399; }
.care-card.performance .care-icon { background: #ecf5ff; color: #409eff; }
.care-card.points .care-icon { background: #fdf6f0; color: #8B5A2B; }
.care-card.training .care-icon { background: #fef0f0; color: #f56c6c; }

.care-info {
  flex: 1;
}

.care-count {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.care-label {
  font-size: 12px;
  color: #909399;
}

.care-trend {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.care-trend.up {
  color: #67c23a;
  background: #f0f9eb;
}

.care-trend.down {
  color: #f56c6c;
  background: #fef0f0;
}

/* 快捷操作 */
.quick-actions {
  margin-bottom: 20px;
}

.action-list {
  display: flex;
  gap: 20px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #606266;
}

.action-item:hover {
  background: #f5f7fa;
  color: #8B5A2B;
}

.action-item span {
  font-size: 13px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

/* 员工表格 */
.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.employee-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.employee-name {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.employee-no {
  font-size: 12px;
  color: #909399;
}

.position-name {
  font-size: 12px;
  color: #606266;
}

.email-text {
  font-size: 12px;
  color: #909399;
}

.work-years {
  font-size: 12px;
  color: #8B5A2B;
}

.care-reminders {
  display: flex;
  flex-direction: column;
}

/* 展开内容 */
.employee-expand {
  padding: 20px;
  background: #f8f9fa;
}

.expand-section {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.expand-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #606266;
}

.points-display, .salary-display, .performance-display, .career-display {
  margin-bottom: 12px;
}

.points-value {
  font-size: 28px;
  font-weight: bold;
  color: #8B5A2B;
}

.points-level {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.salary-value {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
}

.salary-status {
  font-size: 12px;
  margin-top: 4px;
}

.salary-status.draft { color: #909399; }
.salary-status.calculated { color: #e6a23c; }
.salary-status.confirmed { color: #409eff; }
.salary-status.paid { color: #67c23a; }

.perf-score {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.perf-grade {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.career-path {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.career-target {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 薪酬对话框 */
.salary-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.salary-employee-info {
  flex: 1;
}

.salary-employee-info .name {
  font-size: 16px;
  font-weight: 500;
}

.salary-employee-info .meta {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.salary-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.salary-breakdown span {
  font-size: 12px;
  color: #606266;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
