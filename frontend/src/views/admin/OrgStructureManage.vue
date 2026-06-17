<template>
  <div class="org-structure-manage">
    <div class="page-header">
      <h2>组织架构管理</h2>
      <p class="subtitle">股东结构 · 部门管理 · 岗位管理</p>
    </div>

    <!-- Tab 导航 -->
    <el-tabs v-model="activeTab" class="org-tabs">
      <el-tab-pane label="股东结构" name="shareholders">
        <div class="tab-content">
          <div class="section-header">
            <h3>股东信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="showShareholderDialog = true">
              新增股东
            </el-button>
          </div>
          
          <!-- 股东列表 -->
          <el-table :data="shareholderList" stripe v-loading="loadingShareholders">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="phone" label="联系电话" width="130" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag>{{ roleLabel(row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="share_ratio" label="持股比例" width="100">
              <template #default="{ row }">
                {{ (row.share_ratio * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="investment_amount" label="投资金额" width="130">
              <template #default="{ row }">
                ¥{{ formatNum(row.investment_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="investment_date" label="投资日期" width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '正常' : '退出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="editShareholder(row)">编辑</el-button>
                <el-button text type="danger" @click="deleteShareholder(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="部门管理" name="departments">
        <div class="tab-content">
          <div class="section-header">
            <h3>部门信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="showDeptDialog = true">
              新增部门
            </el-button>
          </div>
          
          <!-- 部门列表 -->
          <el-table :data="departmentList" stripe v-loading="loadingDepts">
            <el-table-column prop="name" label="部门名称" width="150" />
            <el-table-column prop="code" label="部门编码" width="120" />
            <el-table-column prop="manager_name" label="部门负责人" width="120" />
            <el-table-column prop="employee_count" label="员工数" width="80" align="center" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="editDepartment(row)">编辑</el-button>
                <el-button text type="danger" @click="deleteDepartment(row)">停用</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="岗位管理" name="positions">
        <div class="tab-content">
          <div class="section-header">
            <h3>岗位信息管理</h3>
            <el-button type="primary" :icon="Plus" @click="showPositionDialog = true">
              新增岗位
            </el-button>
          </div>
          
          <!-- 岗位列表 -->
          <el-table :data="positionList" stripe v-loading="loadingPositions">
            <el-table-column prop="name" label="岗位名称" width="150" />
            <el-table-column prop="code" label="岗位编码" width="120" />
            <el-table-column prop="department_name" label="所属部门" width="120" />
            <el-table-column prop="level" label="岗位等级" width="100">
              <template #default="{ row }">
                <el-tag type="info" size="small">{{ row.level }}级</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="岗位职责" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text type="primary" @click="editPosition(row)">编辑</el-button>
                <el-button text type="danger" @click="deletePosition(row)">停用</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 股东编辑弹窗（简化版，完整版可复用 ShareholderList.vue 的逻辑） -->
    <el-dialog v-model="showShareholderDialog" :title="shareholderForm.id ? '编辑股东' : '新增股东'" width="600px">
      <el-form :model="shareholderForm" label-width="100px">
        <el-form-item label="员工">
          <el-select v-model="shareholderForm.employee_id" placeholder="搜索员工" filterable remote>
            <!-- 员工搜索下拉框 -->
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="shareholderForm.role" placeholder="选择角色">
            <el-option label="执行董事" value="executive_director" />
            <el-option label="经理" value="manager" />
            <el-option label="隐名投资人" value="silent_investor" />
          </el-select>
        </el-form-item>
        <el-form-item label="持股比例">
          <el-input-number v-model="shareholderForm.share_ratio" :min="0" :max="1" :step="0.01" />
          <span style="margin-left: 8px;">{{ (shareholderForm.share_ratio * 100).toFixed(2) }}%</span>
        </el-form-item>
        <el-form-item label="投资金额">
          <el-input-number v-model="shareholderForm.investment_amount" :min="0" :step="1000" />
        </el-form-item>
        <el-form-item label="投资日期">
          <el-date-picker v-model="shareholderForm.investment_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="shareholderForm.status">
            <el-radio value="active">正常</el-radio>
            <el-radio value="exited">退出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shareholderForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShareholderDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShareholder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import financeAPI from '@/api/finance'

const activeTab = ref('shareholders')

const loadingShareholders = ref(false)
const loadingDepts = ref(false)
const loadingPositions = ref(false)

const shareholderList = ref([])
const departmentList = ref([])
const positionList = ref([])

const showShareholderDialog = ref(false)
const showDeptDialog = ref(false)
const showPositionDialog = ref(false)

const shareholderForm = ref({
  id: null,
  employee_id: null,
  name: '',
  phone: '',
  role: '',
  share_ratio: 0,
  investment_amount: 0,
  investment_date: '',
  status: 'active',
  notes: ''
})

const formatNum = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const roleLabel = (role) => {
  const map = {
    'executive_director': '执行董事',
    'manager': '经理',
    'silent_investor': '隐名投资人'
  }
  return map[role] || role
}

const loadShareholders = async () => {
  loadingShareholders.value = true
  try {
    // TODO: 需要后端提供获取股东列表的 API
    // const d = await financeAPI.getShareholders()
    // shareholderList.value = d.items || []
    
    // 临时使用本地数据或空数组
    shareholderList.value = []
    ElMessage.info('股东数据加载中...（需要后端 API）')
  } catch (e) {
    console.error('加载股东失败', e)
    ElMessage.error('加载股东失败')
  } finally {
    loadingShareholders.value = false
  }
}

const loadDepartments = async () => {
  loadingDepts.value = true
  try {
    // TODO: 需要后端提供部门管理的 API
    departmentList.value = []
    ElMessage.info('部门数据加载中...（需要后端 API）')
  } catch (e) {
    console.error('加载部门失败', e)
  } finally {
    loadingDepts.value = false
  }
}

const loadPositions = async () => {
  loadingPositions.value = true
  try {
    // TODO: 需要后端提供岗位管理的 API
    positionList.value = []
    ElMessage.info('岗位数据加载中...（需要后端 API）')
  } catch (e) {
    console.error('加载岗位失败', e)
  } finally {
    loadingPositions.value = false
  }
}

const editShareholder = (row) => {
  shareholderForm.value = { ...row }
  showShareholderDialog.value = true
}

const deleteShareholder = (row) => {
  ElMessageBox.confirm('确定要删除该股东信息吗？', '确认删除', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功（需要后端 API）')
  }).catch(() => {})
}

const saveShareholder = () => {
  ElMessage.success('保存成功（需要后端 API）')
  showShareholderDialog.value = false
  loadShareholders()
}

const editDepartment = (row) => {
  ElMessage.info('部门编辑功能开发中...')
}

const deleteDepartment = (row) => {
  ElMessage.info('部门停用功能开发中...')
}

const editPosition = (row) => {
  ElMessage.info('岗位编辑功能开发中...')
}

const deletePosition = (row) => {
  ElMessage.info('岗位停用功能开发中...')
}

onMounted(() => {
  loadShareholders()
  loadDepartments()
  loadPositions()
})
</script>

<style scoped>
.org-structure-manage {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.org-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}

.tab-content {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
</style>
