<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-text">D&B 帝标|设记家</span>
        <span class="logo-version">V3.0</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        :collapse="isCollapse"
      >
        <!-- 1. 数据看板 - 全局视角，先掌握大盘 -->
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据看板</span>
        </el-menu-item>

        <!-- 2. 员工管理 - 组织架构是基础，所有业务绑定到人 -->
        <el-menu-item index="/admin/employees">
          <el-icon><UserFilled /></el-icon>
          <span>员工管理</span>
        </el-menu-item>

        <!-- 3. 分店管理 - 多店架构基础，仅超级管理员可访问 -->
        <el-menu-item index="/admin/stores">
          <el-icon><Shop /></el-icon>
          <span>分店管理</span>
        </el-menu-item>

        <!-- 4. 楼盘管理 - 先锁死战场，所有线索/客户都要关联楼盘 -->
        <el-menu-item index="/admin/buildings">
          <el-icon><OfficeBuilding /></el-icon>
          <span>楼盘管理</span>
        </el-menu-item>

        <!-- 5. 线索管理 - 业务源头，先把机会抓进来 -->
        <el-menu-item index="/admin/leads">
          <el-icon><User /></el-icon>
          <span>线索管理</span>
        </el-menu-item>

        <!-- 6. 客户管理 - 线索转化后的核心池，承接线索→推进成交 -->
        <el-menu-item index="/admin/customers">
          <el-icon><UserFilled /></el-icon>
          <span>客户管理</span>
        </el-menu-item>

        <!-- 7. 案例管理 - 获客工具 + 客户转化辅助，既引流也支撑客户谈单 -->
        <el-menu-item index="/admin/cases">
          <el-icon><Picture /></el-icon>
          <span>案例管理</span>
        </el-menu-item>

        <!-- 8. 方案管理 - 客户跟进→提案环节，推进客户到预算/报价 -->
        <el-menu-item index="/admin/schemes">
          <el-icon><Document /></el-icon>
          <span>方案管理</span>
        </el-menu-item>

        <!-- 9. 报价管理 - 方案之后，决定成交的关键环节 -->
        <el-menu-item index="/admin/quotes">
          <el-icon><Money /></el-icon>
          <span>报价管理</span>
        </el-menu-item>

        <!-- 10. 合同管理 - 报价通过后，锁定成交，进入交付阶段 -->
        <el-menu-item index="/admin/contracts">
          <el-icon><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>

        <!-- 11. 服务流程(58节点) - 合同之后，全流程交付管理，核心执行线 -->
        <el-menu-item index="/admin/workflow">
          <el-icon><Connection /></el-icon>
          <span>服务流程</span>
        </el-menu-item>

        <!-- 12. 物料管理 - 支撑服务流程的供应链，为交付提供保障 -->
        <el-menu-item index="/admin/materials">
          <el-icon><Box /></el-icon>
          <span>物料管理</span>
        </el-menu-item>

        <!-- 辅助功能 -->
        <el-menu-item index="/admin/appointments">
          <el-icon><Calendar /></el-icon>
          <span>预约管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/files">
          <el-icon><Folder /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/frontend">
          <el-icon><Setting /></el-icon>
          <span>前端配置</span>
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
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userInfo?.name || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine, Picture, User, Calendar, Folder, Setting, Fold, Expand, UserFilled, ArrowDown, Box, Connection, Document, OfficeBuilding, Money, Shop } from '@element-plus/icons-vue'

const router = useRouter()
const isCollapse = ref(false)
const userInfo = ref(null)

onMounted(() => {
  // 从 localStorage 获取用户信息
  const userStr = localStorage.getItem('user')
  if (userStr) {
    userInfo.value = JSON.parse(userStr)
  }
})

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
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
    // 清除登录信息
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
  background: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1f2d3d;
  color: #fff;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
}

.logo-version {
  font-size: 12px;
  margin-left: 4px;
  padding: 2px 6px;
  background: #409EFF;
  border-radius: 4px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.collapse-btn:hover {
  color: #409EFF;
}

.breadcrumb {
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
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
  background: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
}
</style>
