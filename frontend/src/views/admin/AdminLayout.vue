<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-text">D&B 帝标|设记家</span>
        <span class="logo-version">V3.3</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#fff"
        text-color="#333"
        active-text-color="#409EFF"
        :collapse="isCollapse"
      >
        <!-- 1. 数据看板 -->
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据看板</span>
        </el-menu-item>

        <!-- 2. 楼盘管理 -->
        <el-menu-item index="/admin/buildings">
          <el-icon><OfficeBuilding /></el-icon>
          <span>楼盘管理</span>
        </el-menu-item>

        <!-- 3. 线索管理 -->
        <el-menu-item index="/admin/leads">
          <el-icon><User /></el-icon>
          <span>线索管理</span>
        </el-menu-item>

        <!-- 4. 客户管理 -->
        <el-menu-item index="/admin/customers">
          <el-icon><UserFilled /></el-icon>
          <span>客户管理</span>
        </el-menu-item>

        <!-- 5. 案例管理 -->
        <el-menu-item index="/admin/cases">
          <el-icon><Picture /></el-icon>
          <span>案例管理</span>
        </el-menu-item>

        <!-- 6. 选品管理 -->
        <el-menu-item index="/admin/schemes">
          <el-icon><Document /></el-icon>
          <span>选品管理</span>
        </el-menu-item>

        <!-- 7. 报价管理 -->
        <el-menu-item index="/admin/quotes">
          <el-icon><Money /></el-icon>
          <span>报价管理</span>
        </el-menu-item>

        <!-- 8. 合同管理 -->
        <el-menu-item index="/admin/contracts">
          <el-icon><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>

        <!-- 9. 服务流程 -->
        <el-menu-item index="/admin/workflow">
          <el-icon><Connection /></el-icon>
          <span>服务流程</span>
        </el-menu-item>

        <!-- 辅助功能 -->
        <el-menu-item index="/admin/appointments">
          <el-icon><Calendar /></el-icon>
          <span>预约管理</span>
        </el-menu-item>

        <!-- 财务管理 -->
        <el-menu-item index="/admin/finance">
          <el-icon><Wallet /></el-icon>
          <span>财务管理</span>
        </el-menu-item>

        <!-- 组织架构 -->
        <el-menu-item index="/admin/org-structure">
          <el-icon><Connection /></el-icon>
          <span>组织架构</span>
        </el-menu-item>

        <!-- 系统设置（集成员工/分店/物料/文件/前端配置/流程模板/分类管理） -->
        <el-menu-item index="/admin/settings">
          <el-icon><Tools /></el-icon>
          <span>系统设置</span>
        </el-menu-item>


      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <span class="breadcrumb">管理后台</span>
        </div>
        <div class="header-right">
          <div class="my-btn" @click="myDrawerVisible = true">
            <el-icon><UserFilled /></el-icon>
            <span>我的</span>
          </div>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 我的 抽屉 -->
    <el-drawer
      v-model="myDrawerVisible"
      title="我的"
      direction="rtl"
      size="380px"
      :append-to-body="true"
    >
      <div class="my-drawer">
        <!-- 用户卡片 -->
        <div class="my-user-card">
          <el-avatar :size="56" :icon="UserFilled" />
          <div class="my-user-info">
            <div class="my-user-name">{{ userInfo?.name || '管理员' }}</div>
            <div class="my-user-role">{{ userInfo?.position || '系统管理员' }}</div>
          </div>
        </div>
        <!-- 我的业务 -->
        <div class="my-section">
          <div class="my-section-title">
            <el-icon><Briefcase /></el-icon>
            <span>我的业务</span>
          </div>
          <div class="my-grid">
            <div class="my-grid-item" @click="goMy('team')">
              <el-icon :size="22" color="#722ED1"><Share /></el-icon>
              <span>我的团队</span>
            </div>
            <div class="my-grid-item" @click="goMy('buildings')">
              <el-icon :size="22" color="#13C2C2"><OfficeBuilding /></el-icon>
              <span>我的楼盘</span>
            </div>
            <div class="my-grid-item" @click="goMy('contracts')">
              <el-icon :size="22" color="#FA8C16"><Document /></el-icon>
              <span>我的合同</span>
            </div>
            <div class="my-grid-item" @click="goMy('quotes')">
              <el-icon :size="22" color="#52C41A"><Money /></el-icon>
              <span>我的报价</span>
            </div>
            <div class="my-grid-item" @click="goMy('reviews')">
              <el-icon :size="22" color="#F5222D"><Finished /></el-icon>
              <span>我的审核</span>
            </div>
            <div class="my-grid-item" @click="goMy('leads')">
              <el-icon :size="22" color="#1890FF"><Promotion /></el-icon>
              <span>我的线索</span>
            </div>
            <div class="my-grid-item" @click="goMy('customers')">
              <el-icon :size="22" color="#2F54EB"><User /></el-icon>
              <span>我的客户</span>
            </div>
            <div class="my-grid-item" @click="goMy('workflow')">
              <el-icon :size="22" color="#EB2F96"><Connection /></el-icon>
              <span>我的服务流程</span>
            </div>
          </div>
        </div>

        <!-- 安全设置 -->
        <div class="my-section">
          <div class="my-section-title">
            <el-icon><Lock /></el-icon>
            <span>安全设置</span>
          </div>
          <div class="my-list">
            <div class="my-list-item" @click="showChangePassword">
              <span>修改登录密码</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
        <!-- 修改密码弹窗 -->
    <el-dialog v-model="changePasswordVisible" title="修改登录密码" width="420px" append-to-body>
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-Password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" @click="submitChangePassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 我的团队弹窗 -->
    <el-dialog v-model="teamDialogVisible" title="我的团队" width="600px" append-to-body>
      <div class="team-header">
        <el-tag type="primary">{{ teamInfo.department || '未分配部门' }}</el-tag>
        <el-tag type="success" v-if="teamInfo.store">{{ teamInfo.store }}</el-tag>
      </div>
      <el-table :data="teamMembers" stripe size="small" style="margin-top:12px">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="position" label="岗位" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status === 'active' ? '在职' : '离职' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataLine, Picture, User, Calendar, Folder, Setting, Fold, Expand,
  UserFilled, Box, Connection, Document, OfficeBuilding,
  Money, Shop, Tools, Briefcase, Share, Finished, Promotion,
  Lock, ArrowRight, Monitor, Wallet
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const isCollapse = ref(false)
const userInfo = ref(null)

// 我的 抽屉
const myDrawerVisible = ref(false)

// 团队
// 团队
const teamDialogVisible = ref(false)
const teamInfo = reactive({ department: '', store: '' })
const teamMembers = ref([])

// 修改密码
const changePasswordVisible = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try { userInfo.value = JSON.parse(userStr) } catch {}
  }
})

// 加载积分余额


const showChangePassword = () => {
  changePasswordVisible.value = true
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const submitChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate()
  try {
    const res = await request.post('/auth/change-password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    if (res.data?.ok) {
      ElMessage.success('密码修改成功，请重新登录')
      changePasswordVisible.value = false
      handleLogout()
    } else {
      ElMessage.error(res.data?.message || '修改失败')
    }
  } catch (e) {
    ElMessage.error('修改失败：' + (e.response?.data?.message || e.message))
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      myDrawerVisible.value = true
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.sidebar {
  background: var(--bg-surface, #fff);
  transition: width 0.3s;
  border-right: 1px solid var(--border, #e4e7ed);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border, #e4e7ed);
  color: var(--text-title, #333);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
}

.logo-version {
  font-size: 12px;
  margin-left: 4px;
  padding: 2px 6px;
  background: var(--primary, #409EFF);
  border-radius: 4px;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-surface, #fff);
  box-shadow: var(--shadow, 0 1px 4px rgba(0,0,0,0.08));
  color: var(--text-primary, #333);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary, #909399);
}

.collapse-btn:hover {
  color: var(--primary, #409EFF);
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary, #909399);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.my-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  color: var(--primary, #409EFF);
  background: rgba(64, 158, 255, 0.08);
  transition: all 0.2s;
}

.my-btn:hover {
  background: rgba(64, 158, 255, 0.25);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-info:hover {
  background: var(--bg-surface-hover, #f5f7fa);
}

.username {
  font-size: 14px;
  color: var(--text-primary, #E8E8E8);
}

.main-content {
  background: var(--bg-base, #f5f7fa);
  padding: 20px;
  color: var(--text-primary, #333);
}

/* 我的抽屉样式 */
.my-drawer {
  padding: 0 4px;
}

.my-user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #ecf5ff 0%, #e0edff 100%);
  border-radius: 12px;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
  border: 1px solid var(--border, #e4e7ed);
}

.my-user-name {
  font-size: 18px;
  font-weight: 600;
}

.my-user-role {
  font-size: 13px;
  opacity: 0.85;
  margin-top: 4px;
  color: var(--text-secondary, #909399);
}

.my-section {
  margin-bottom: 20px;
}

.my-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-title, #333);
  margin-bottom: 12px;
}

.my-section-title .el-icon {
  color: var(--accent, #6C63FF);
}

.my-points-card {
  text-align: center;
  padding: 16px;
  background: rgba(250, 140, 22, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(250, 140, 22, 0.3);
  margin-bottom: 8px;
}

.my-points-num {
  font-size: 32px;
  font-weight: 700;
  color: #FA8C16;
  line-height: 1.2;
}

.my-points-label {
  font-size: 12px;
  color: var(--text-secondary, #606266);
  margin-top: 4px;
}

.my-points-actions {
  display: flex;
  gap: 8px;
}

.my-points-actions .el-button {
  flex: 1;
}

.my-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.my-grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border, #e4e7ed);
}

.my-grid-item:hover {
  background: var(--bg-surface-hover, #22223a);
  transform: translateY(-1px);
}

.my-grid-item span {
  font-size: 12px;
  color: var(--text-secondary, #909399);
  white-space: nowrap;
}

.my-list {
  border: 1px solid var(--border, #e4e7ed);
  border-radius: 8px;
  overflow: hidden;
}

.my-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  color: var(--text-primary, #333);
  border-bottom: 1px solid var(--border, #e4e7ed);
}

.my-list-item:last-child {
  border-bottom: none;
}

.my-list-item:hover {
  background: var(--bg-surface-hover, #f5f7fa);
}

.my-list-item .el-icon {
  color: var(--text-secondary, #909399);
}

/* 积分汇总 */
.points-summary {
  margin-top: 12px;
  text-align: right;
  font-size: 14px;
  color: var(--text-secondary, #606266);
}

.points-summary strong {
  color: #FA8C16;
  font-size: 18px;
}

/* 排行榜 */
.rank-badge {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg-surface, #fff);
  color: var(--text-secondary, #606266);
}

.rank-badge.rank-top {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  color: #fff;
}

/* 团队弹窗 */
.team-header {
  display: flex;
  gap: 8px;
}
</style>
