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
          <span class="breadcrumb clickable" @click="router.push('/admin/dashboard')">管理后台</span>
        </div>
        <div class="header-right">
          <div class="my-btn" @click="$router.push('/admin/my-workspace')">
            <el-icon><UserFilled /></el-icon>
            <span>我的</span>
          </div>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DataLine, Picture, User, Calendar, Fold, Expand,
  UserFilled, Connection, Document, OfficeBuilding,
  Money, Tools, Wallet
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)
const isFullPage = computed(() =>
  route.path.startsWith('/admin/settings') || route.path.startsWith('/admin/my-workspace')
)
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
</style>
