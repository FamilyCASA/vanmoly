<template>
  <el-container class="admin-layout">
    <el-aside v-if="!isFullPage" width="220px" class="sidebar">
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
        <el-menu-item v-for="item in visibleMenuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
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
          <span class="breadcrumb clickable" @click="router.push('/admin/dashboard')">管理后台</span>
        </div>
        <div class="header-right">
          <div class="my-btn" @click="mineDrawerVisible = true">
            <el-icon><UserFilled /></el-icon>
            <span>{{ currentUserName || '我的' }}</span>
          </div>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <el-drawer v-model="mineDrawerVisible" title="我的快捷入口" size="380px" class="mine-drawer">
      <div class="mine-profile">
        <div class="mine-avatar">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div>
          <h3>我的工作台</h3>
          <p>任务、客户、流程和个人权限入口</p>
        </div>
      </div>

      <el-button type="primary" class="mine-main-btn" @click="goMyWorkspace">
        进入我的界面
      </el-button>

      <div v-if="canOpenAdmin" class="drawer-section">
        <div class="drawer-title">管理入口</div>
        <button class="quick-card admin-card" @click="goAdminDashboard">
          <span class="quick-icon"><el-icon><DataLine /></el-icon></span>
          <span>
            <strong>管理后台</strong>
            <small>进入数据看板与管理模块</small>
          </span>
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>

      <div class="drawer-section">
        <div class="drawer-title">我的权限入口</div>
        <div class="quick-grid">
          <button
            v-for="item in drawerMenuItems"
            :key="item.path"
            class="quick-card compact"
            @click="goQuickPath(item.path)"
          >
            <span class="quick-icon"><el-icon><component :is="item.icon" /></el-icon></span>
            <strong>{{ item.label }}</strong>
          </button>
        </div>
      </div>

      <div class="drawer-footer">
        <el-button text @click="router.push('/')">
          <el-icon><House /></el-icon>
          返回前台
        </el-button>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DataLine, Picture, User, Calendar, Fold, Expand,
  UserFilled, Connection, Document, OfficeBuilding,
  Money, Tools, Wallet, ArrowRight, House, Lock, Coordinate
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)
const visibleModuleKeys = ref([])
const permissionLoaded = ref(false)
const mineDrawerVisible = ref(false)
const currentUserName = ref('')
const isFullPage = computed(() =>
  route.path.startsWith('/admin/settings') || route.path.startsWith('/admin/my-workspace')
)

const menuItems = [
  { key: 'dashboard', path: '/admin/dashboard', label: '数据看板', icon: DataLine },
  { key: 'buildings', path: '/admin/buildings', label: '楼盘管理', icon: OfficeBuilding },
  { key: 'leads', path: '/admin/leads', label: '线索管理', icon: User },
  { key: 'customers', path: '/admin/customers', label: '客户管理', icon: UserFilled },
  { key: 'cases', path: '/admin/cases', label: '案例管理', icon: Picture },
  { key: 'schemes', path: '/admin/schemes', label: '选品管理', icon: Document },
  { key: 'quotes', path: '/admin/quotes', label: '报价管理', icon: Money },
  { key: 'contracts', path: '/admin/contracts', label: '合同管理', icon: Document },
  { key: 'workflow', path: '/admin/workflow', label: '服务流程', icon: Connection },
  { key: 'appointments', path: '/admin/appointments', label: '预约管理', icon: Calendar },
  { key: 'finance', path: '/admin/finance', label: '财务管理', icon: Wallet },
  { key: 'permission', path: '/admin/permission-center', label: '权限矩阵', icon: Lock },
  { key: 'project', path: '/admin/project-organization', label: '项目组织', icon: Coordinate },
  { key: 'settings', path: '/admin/settings', label: '系统设置', icon: Tools }
]

const visibleMenuItems = computed(() => {
  if (!permissionLoaded.value) return menuItems
  return menuItems.filter(item => visibleModuleKeys.value.includes(item.key))
})

const drawerMenuItems = computed(() =>
  visibleMenuItems.value.filter(item => !['dashboard', 'settings'].includes(item.key))
)

const canOpenAdmin = computed(() =>
  visibleMenuItems.value.some(item => item.key === 'dashboard')
)

const loadMyPermissions = async () => {
  try {
    const res = await request.get('/permissions/me')
    visibleModuleKeys.value = (res.visible_modules || []).map(item => item.key)
  } catch (error) {
    visibleModuleKeys.value = menuItems.map(item => item.key)
  } finally {
    permissionLoaded.value = true
  }
}

const loadCurrentUser = async () => {
  try {
    const res = await request.get('/auth/me')
    currentUserName.value = res.nickname || res.employee?.name || res.user?.name || res.name || ''
  } catch (e) {
    // fallback to localStorage
    const local = JSON.parse(localStorage.getItem('user') || '{}')
    currentUserName.value = local.name || local.employee_name || ''
  }
}

const goMyWorkspace = () => {
  mineDrawerVisible.value = false
  router.push('/admin/my-workspace')
}

const goAdminDashboard = () => {
  mineDrawerVisible.value = false
  router.push('/admin/dashboard')
}

const goQuickPath = (path) => {
  mineDrawerVisible.value = false
  router.push(path)
}

onMounted(async () => {
  await loadMyPermissions()
  await loadCurrentUser()
  if (route.query.openMine === '1') {
    mineDrawerVisible.value = true
  }
})

watch(() => route.query.openMine, (value) => {
  if (value === '1') {
    mineDrawerVisible.value = true
  }
})

watch([permissionLoaded, visibleMenuItems, () => route.path], () => {
  if (!permissionLoaded.value || isFullPage.value) return
  const allowed = visibleMenuItems.value.some(item => route.path.startsWith(item.path))
  if (!allowed) router.replace('/admin/my-workspace')
})
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
  background: var(--primary, #409eff);
  border-radius: 4px;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-surface, #fff);
  box-shadow: var(--shadow, 0 1px 4px rgba(0, 0, 0, 0.08));
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
  color: var(--primary, #409eff);
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary, #909399);
}

.breadcrumb.clickable {
  cursor: pointer;
  color: #409eff;
}

.breadcrumb.clickable:hover {
  text-decoration: underline;
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
  color: var(--primary, #409eff);
  background: rgba(64, 158, 255, 0.08);
  transition: all 0.2s;
}

.my-btn:hover {
  background: rgba(64, 158, 255, 0.25);
}

.main-content {
  background: var(--bg-base, #f5f7fa);
  padding: 20px;
  color: var(--text-primary, #333);
}

.mine-profile {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 18px;
  border-radius: 8px;
  background: linear-gradient(135deg, #eef6ff 0%, #f7fbff 100%);
  border: 1px solid #dcecff;
}

.mine-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  background: #409eff;
  font-size: 24px;
}

.mine-profile h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #1f2937;
}

.mine-profile p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.5;
}

.mine-main-btn {
  width: 100%;
  margin: 18px 0 10px;
  min-height: 42px;
}

.drawer-section {
  margin-top: 22px;
}

.drawer-title {
  margin-bottom: 10px;
  font-size: 13px;
  color: #6b7280;
  font-weight: 600;
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.quick-card {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
}

.quick-card:hover {
  border-color: #409eff;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.13);
  transform: translateY(-1px);
}

.quick-card.admin-card {
  display: grid;
  grid-template-columns: 38px 1fr 18px;
  align-items: center;
  gap: 12px;
  padding: 14px;
  text-align: left;
}

.quick-card.compact {
  min-height: 84px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 10px;
  padding: 14px;
}

.quick-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #eef6ff;
  color: #409eff;
}

.quick-card strong {
  font-size: 14px;
  font-weight: 700;
}

.quick-card small {
  display: block;
  margin-top: 4px;
  color: #6b7280;
  font-size: 12px;
}

.drawer-footer {
  margin-top: 26px;
  padding-top: 14px;
  border-top: 1px solid #eef0f3;
}
</style>
