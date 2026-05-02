<template>
  <div class="user-manage-v2">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>用户权限管理</h2>
        <p class="subtitle">账号生命周期 · 权限分级 · 资产管控</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          新建用户
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon blue">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.active }}</div>
          <div class="stat-label">正常</div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon orange">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.locked }}</div>
          <div class="stat-label">已锁定</div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon gray">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.resigned }}</div>
          <div class="stat-label">已离职</div>
        </div>
      </el-card>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="昵称/手机号/账号"
            clearable
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filterForm.role" placeholder="全部角色" clearable style="width: 120px;">
            <el-option label="超管" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="店长" value="manager" />
            <el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="正常" value="active" />
            <el-option label="锁定" value="locked" />
            <el-option label="离职" value="resigned" />
          </el-select>
        </el-form-item>
        <el-form-item label="门店" v-if="isSuperAdmin">
          <el-select v-model="filterForm.store_id" placeholder="全部门店" clearable style="width: 150px;">
            <el-option
              v-for="store in storeList"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshRight" @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="never">
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="40" :icon="User" />
              <div class="user-detail">
                <div class="user-name">
                  {{ row.nickname }}
                  <el-tag v-if="row.role === 'super_admin'" type="danger" size="small">超管</el-tag>
                  <el-tag v-else-if="row.role === 'admin'" type="warning" size="small">管理员</el-tag>
                  <el-tag v-else-if="row.role === 'manager'" type="success" size="small">店长</el-tag>
                  <el-tag v-else size="small">员工</el-tag>
                </div>
                <div class="user-meta">{{ row.username }} | {{ row.phone }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="门店" width="150">
          <template #default="{ row }">
            {{ getStoreName(row.store_id) }}
          </template>
        </el-table-column>
        <el-table-column label="登录方式" width="120">
          <template #default="{ row }">
            <div class="login-methods">
              <el-icon v-if="true" title="账号密码"><Key /></el-icon>
              <el-icon v-if="row.wx_bound" title="微信" color="#07c160"><ChatDotRound /></el-icon>
              <el-icon v-if="row.qq_bound" title="QQ" color="#12b7f5"><ChatSquare /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login_at || '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'active'" type="success">正常</el-tag>
            <el-tag v-else-if="row.status === 'locked'" type="warning">锁定</el-tag>
            <el-tag v-else-if="row.status === 'resigned'" type="info">离职</el-tag>
            <el-tag v-else type="danger">异常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleViewDetail(row)">详情</el-button>
              <el-button 
                size="small" 
                type="warning" 
                @click="handleResetPassword(row)"
                :disabled="!canResetPassword(row)"
              >
                重置密码
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="handleResign(row)"
                v-if="row.status !== 'resigned'"
                :disabled="!canResign(row)"
              >
                离职
              </el-button>
            </el-button-group>
            <el-button 
              v-if="row.status === 'locked'"
              size="small" 
              type="success" 
              @click="handleUnlock(row)"
              style="margin-left: 8px;"
            >
              解锁
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建用户弹窗 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="createForm.nickname" placeholder="请输入用户昵称" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="createForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" placeholder="选择角色" style="width: 100%;">
            <el-option label="超级管理员" value="super_admin" v-if="isSuperAdmin" />
            <el-option label="管理员" value="admin" v-if="isSuperAdmin" />
            <el-option label="店长" value="manager" />
            <el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属门店" prop="store_id" v-if="isSuperAdmin || createForm.role === 'manager'">
          <el-select v-model="createForm.store_id" placeholder="选择门店" style="width: 100%;">
            <el-option
              v-for="store in storeList"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateUser">创建</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog
      v-model="showResetDialog"
      title="重置密码"
      width="400px"
    >
      <div class="reset-password-content">
        <el-alert
          title="确认重置密码？"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>用户：<strong>{{ selectedUser?.nickname }}</strong></p>
            <p>密码将重置为：<strong>van654321</strong></p>
            <p>用户首次登录需修改密码</p>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="confirmResetPassword">确认重置</el-button>
      </template>
    </el-dialog>

    <!-- 离职处理弹窗 -->
    <el-dialog
      v-model="showResignDialog"
      title="员工离职处理"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="resign-content">
        <el-alert
          title="⚠️ 离职后操作不可撤销"
          type="error"
          :closable="false"
          show-icon
          style="margin-bottom: 20px;"
        />
        <p class="resign-user">员工：<strong>{{ selectedUser?.nickname }}</strong> ({{ selectedUser?.phone }})</p>
        
        <el-form :model="resignForm" label-width="100px">
          <el-form-item label="离职类型">
            <el-radio-group v-model="resignForm.reason">
              <el-radio label="resignation">主动离职</el-radio>
              <el-radio label="dismissal">辞退</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="备注说明">
            <el-input
              v-model="resignForm.notes"
              type="textarea"
              rows="3"
              placeholder="请输入离职原因或其他说明"
            />
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="asset-transfer-preview">
          <h4>📦 数字资产归集预览</h4>
          <p class="transfer-desc">该员工的以下资产将归集到公海，由管理员重新分配：</p>
          <div class="asset-list">
            <div class="asset-item">
              <el-icon><UserFilled /></el-icon>
              <span>客户资源</span>
              <el-tag type="warning">待归集</el-tag>
            </div>
            <div class="asset-item">
              <el-icon><Document /></el-icon>
              <span>线索资源</span>
              <el-tag type="warning">待归集</el-tag>
            </div>
            <div class="asset-item">
              <el-icon><Files /></el-icon>
              <span>方案/报价</span>
              <el-tag type="warning">待归集</el-tag>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResignDialog = false">取消</el-button>
        <el-button type="danger" :loading="resigning" @click="confirmResign">
          确认离职处理
        </el-button>
      </template>
    </el-dialog>

    <!-- 用户详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="用户详情"
      width="600px"
    >
      <div v-if="selectedUser" class="user-detail-panel">
        <div class="detail-header">
          <el-avatar :size="64" :icon="User" />
          <div class="detail-title">
            <h3>{{ selectedUser.nickname }}</h3>
            <p>{{ selectedUser.username }}</p>
          </div>
          <el-tag :type="getStatusType(selectedUser.status)">
            {{ getStatusLabel(selectedUser.status) }}
          </el-tag>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="手机号">{{ selectedUser.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedUser.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ getRoleLabel(selectedUser.role) }}</el-descriptions-item>
          <el-descriptions-item label="门店">{{ getStoreName(selectedUser.store_id) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedUser.created_at }}</el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ selectedUser.last_login_at || '从未登录' }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="section-title">第三方绑定</h4>
        <div class="binding-list">
          <div class="binding-item">
            <div class="binding-info">
              <el-icon :size="24" color="#07c160"><ChatDotRound /></el-icon>
              <span>微信</span>
            </div>
            <el-tag v-if="selectedUser.wx_bound" type="success">已绑定</el-tag>
            <el-tag v-else type="info">未绑定</el-tag>
          </div>
          <div class="binding-item">
            <div class="binding-info">
              <el-icon :size="24" color="#12b7f5"><ChatSquare /></el-icon>
              <span>QQ</span>
            </div>
            <el-tag v-if="selectedUser.qq_bound" type="success">已绑定</el-tag>
            <el-tag v-else type="info">未绑定</el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, RefreshRight, User, Lock, CircleCheck, CircleClose,
  Key, ChatDotRound, ChatSquare, UserFilled, Document, Files
} from '@element-plus/icons-vue'
import request from '@/api/request'

// 当前用户信息
const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const isSuperAdmin = computed(() => currentUser.value.role === 'super_admin')
const isManager = computed(() => currentUser.value.role === 'manager')

// 统计数据
const stats = reactive({
  total: 0,
  active: 0,
  locked: 0,
  resigned: 0
})

// 列表数据
const loading = ref(false)
const userList = ref([])
const storeList = ref([])
const selectedUsers = ref([])

// 筛选
const filterForm = reactive({
  keyword: '',
  role: '',
  status: '',
  store_id: null
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 创建用户
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  nickname: '',
  phone: '',
  role: 'staff',
  store_id: null
})

const createRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 重置密码
const showResetDialog = ref(false)
const resetting = ref(false)
const selectedUser = ref(null)

// 离职
const showResignDialog = ref(false)
const resigning = ref(false)
const resignForm = reactive({
  reason: 'resignation',
  notes: ''
})

// 详情
const showDetailDialog = ref(false)

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    const res = await request.get('/auth/users', {
      params: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        keyword: filterForm.keyword,
        role: filterForm.role,
        status: filterForm.status,
        store_id: filterForm.store_id
      }
    })
    if (res.items) {
      userList.value = res.items
      pagination.total = res.total || 0
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 获取门店列表
const fetchStoreList = async () => {
  try {
    const res = await request.get('/auth/stores')
    if (res) {
      storeList.value = res
    }
  } catch (error) {
    console.error('获取门店列表失败')
  }
}

// 获取统计数据
const fetchStats = async () => {
  // 模拟统计数据
  stats.total = userList.value.length
  stats.active = userList.value.filter(u => u.status === 'active').length
  stats.locked = userList.value.filter(u => u.status === 'locked').length
  stats.resigned = userList.value.filter(u => u.status === 'resigned').length
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUserList()
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.role = ''
  filterForm.status = ''
  filterForm.store_id = null
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchUserList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchUserList()
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

// 创建用户
const handleCreateUser = async () => {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return

  creating.value = true
  try {
    const res = await request.post('/auth/register', createForm)
    if (res) {
      ElMessage.success('用户创建成功')
      showCreateDialog.value = false
      fetchUserList()
      // 重置表单
      createForm.nickname = ''
      createForm.phone = ''
      createForm.role = 'staff'
      createForm.store_id = null
    } else {
      ElMessage.error('创建失败')
    }
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

// 权限检查
const canResetPassword = (user) => {
  if (isSuperAdmin.value) return true
  if (isManager.value && user.store_id === currentUser.value.store_id) return true
  return false
}

const canResign = (user) => {
  if (user.id === currentUser.value.id) return false
  if (isSuperAdmin.value) return true
  if (isManager.value && user.store_id === currentUser.value.store_id) return true
  return false
}

// 重置密码
const handleResetPassword = (user) => {
  selectedUser.value = user
  showResetDialog.value = true
}

const confirmResetPassword = async () => {
  resetting.value = true
  try {
    const res = await request.post('/auth/password/admin-reset', {
      user_id: selectedUser.value.id
    })
    if (res) {
      ElMessage.success('密码重置成功')
      showResetDialog.value = false
    } else {
      ElMessage.error('重置失败')
    }
  } catch (error) {
    ElMessage.error('重置失败')
  } finally {
    resetting.value = false
  }
}

// 离职
const handleResign = (user) => {
  selectedUser.value = user
  showResignDialog.value = true
}

const confirmResign = async () => {
  resigning.value = true
  try {
    const res = await request.post(`/auth/users/${selectedUser.value.id}/resign`, {
      reason: resignForm.reason,
      notes: resignForm.notes
    })
    if (res) {
      ElMessage.success('离职处理完成，资产已归集到公海')
      showResignDialog.value = false
      fetchUserList()
    } else {
      ElMessage.error('处理失败')
    }
  } catch (error) {
    ElMessage.error('处理失败')
  } finally {
    resigning.value = false
  }
}

// 解锁
const handleUnlock = async (user) => {
  try {
    const res = await request.post(`/auth/users/${user.id}/unlock`)
    if (res) {
      ElMessage.success('账号已解锁')
      fetchUserList()
    }
  } catch (error) {
    ElMessage.error('解锁失败')
  }
}

// 详情
const handleViewDetail = (user) => {
  selectedUser.value = user
  showDetailDialog.value = true
}

// 辅助函数
const getStoreName = (storeId) => {
  const store = storeList.value.find(s => s.id === storeId)
  return store?.name || '-'
}

const getRoleLabel = (role) => {
  const map = {
    super_admin: '超级管理员',
    admin: '管理员',
    manager: '店长',
    staff: '员工'
  }
  return map[role] || role
}

const getStatusType = (status) => {
  const map = {
    active: 'success',
    locked: 'warning',
    resigned: 'info'
  }
  return map[status] || 'danger'
}

const getStatusLabel = (status) => {
  const map = {
    active: '正常',
    locked: '锁定',
    resigned: '离职'
  }
  return map[status] || status
}

onMounted(() => {
  fetchUserList()
  fetchStoreList()
})
</script>

<style scoped>
.user-manage-v2 {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1a1a1a;
}

.subtitle {
  margin: 4px 0 0;
  color: #999;
  font-size: 14px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    padding: 20px;
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.stat-icon.blue {
  background: #e6f7ff;
  color: #1890ff;
}

.stat-icon.green {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.orange {
  background: #fff7e6;
  color: #fa8c16;
}

.stat-icon.gray {
  background: #f5f5f5;
  color: #999;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

/* 筛选 */
.filter-card {
  margin-bottom: 16px;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-detail {
  flex: 1;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  margin-bottom: 4px;
}

.user-meta {
  font-size: 12px;
  color: #999;
}

.login-methods {
  display: flex;
  gap: 8px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 重置密码 */
.reset-password-content {
  padding: 10px 0;
}

.reset-password-content p {
  margin: 8px 0;
}

/* 离职处理 */
.resign-content {
  padding: 10px 0;
}

.resign-user {
  margin-bottom: 20px;
  color: #666;
}

.asset-transfer-preview {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.asset-transfer-preview h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #1a1a1a;
}

.transfer-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.asset-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.asset-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
}

.asset-item span {
  flex: 1;
}

/* 用户详情 */
.user-detail-panel {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-title h3 {
  margin: 0 0 4px;
  font-size: 18px;
}

.detail-title p {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.section-title {
  margin: 24px 0 16px;
  font-size: 16px;
  color: #1a1a1a;
}

.binding-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.binding-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.binding-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
