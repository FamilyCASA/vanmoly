<template>
  <div class="settings-layout">
    <!-- 左侧功能卡片导航 -->
    <div class="settings-sidebar">
      <div class="sidebar-header">
        <h3>系统设置</h3>
        <p class="sidebar-desc">配置系统参数与业务模板</p>
      </div>
      <div class="sidebar-nav">
        <div
          v-for="item in navItems"
          :key="item.key"
          class="nav-card"
          :class="{ active: activeKey === item.key }"
          @click="activeKey = item.key"
        >
          <div class="nav-icon" :style="{ background: item.bg, color: item.color }">
            <el-icon :size="20"><component :is="item.icon" /></el-icon>
          </div>
          <div class="nav-info">
            <div class="nav-title">{{ item.title }}</div>
            <div class="nav-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧编辑区 -->
    <div class="settings-content">
      <div class="content-header">
        <h3>{{ currentTitle }}</h3>
        <p class="content-desc">{{ currentDesc }}</p>
      </div>
      <div class="content-body">
        <!-- 流程模板管理 -->
        <WorkflowTemplateManage v-if="activeKey === 'workflow'" />
        <!-- 物料分类管理 -->
        <CategoryManage v-if="activeKey === 'category'" />
        <!-- 员工管理 -->
        <EmployeeManage v-if="activeKey === 'employee'" />
        <!-- 分店管理 -->
        <StoreManage v-if="activeKey === 'store'" />
        <!-- 物料管理 -->
        <MaterialManageV2 v-if="activeKey === 'material'" />
        <!-- 文件管理 -->
        <FileManage v-if="activeKey === 'file'" />
        <!-- 前端配置 -->
        <FrontendConfig v-if="activeKey === 'frontend'" />
        <!-- 积分管理 -->
        <PointsManage v-if="activeKey === 'points'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Connection, Folder, User, Shop, Box, FolderOpened, Monitor, Trophy
} from '@element-plus/icons-vue'
import WorkflowTemplateManage from './WorkflowTemplateManage.vue'
import CategoryManage from './CategoryManage.vue'
import EmployeeManage from './EmployeeManage.vue'
import StoreManage from './StoreManage.vue'
import MaterialManageV2 from './MaterialManageV2.vue'
import FileManage from './FileManage.vue'
import FrontendConfig from './FrontendConfig.vue'
import PointsManage from './PointsManage.vue'

const activeKey = ref('workflow')

const navItems = [
  {
    key: 'workflow',
    title: '流程模板管理',
    desc: '全案服务流程阶段与节点',
    icon: Connection,
    bg: '#E6F7FF',
    color: '#1890FF'
  },
  {
    key: 'category',
    title: '物料分类管理',
    desc: '物料分类树与编码规则',
    icon: Folder,
    bg: '#F6FFED',
    color: '#52C41A'
  },
  {
    key: 'employee',
    title: '员工管理',
    desc: '员工档案、岗位与权限',
    icon: User,
    bg: '#FFF7E6',
    color: '#FA8C16'
  },
  {
    key: 'store',
    title: '分店管理',
    desc: '门店信息与组织架构',
    icon: Shop,
    bg: '#F9F0FF',
    color: '#722ED1'
  },
  {
    key: 'material',
    title: '物料管理',
    desc: 'SKU物料库与供应商',
    icon: Box,
    bg: '#E6FFFB',
    color: '#13C2C2'
  },
  {
    key: 'file',
    title: '文件管理',
    desc: '文档存储与版本管理',
    icon: FolderOpened,
    bg: '#FFF1F0',
    color: '#F5222D'
  },
  {
    key: 'frontend',
    title: '前端配置',
    desc: '主题样式与页面参数',
    icon: Monitor,
    bg: '#F0F5FF',
    color: '#2F54EB'
  },
  {
    key: 'points',
    title: '积分管理',
    desc: '积分规则、审核与员工积分',
    icon: Trophy,
    bg: '#FFF0F6',
    color: '#EB2F96'
  }
]

const currentTitle = computed(() => {
  const item = navItems.find(i => i.key === activeKey.value)
  return item?.title || ''
})

const currentDesc = computed(() => {
  const item = navItems.find(i => i.key === activeKey.value)
  return item?.desc || ''
})
</script>

<style scoped>
.settings-layout {
  display: flex;
  height: calc(100vh - 60px - 40px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* 左侧导航 */
.settings-sidebar {
  width: 280px;
  min-width: 280px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.sidebar-header {
  padding: 20px 20px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-header h3 {
  margin: 0 0 4px;
  font-size: 17px;
  color: #262626;
  font-weight: 600;
}

.sidebar-desc {
  margin: 0;
  font-size: 12px;
  color: #8c8c8c;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.nav-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 6px;
  border: 2px solid transparent;
}

.nav-card:hover {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.nav-card.active {
  background: #fff;
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.12);
}

.nav-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-info {
  flex: 1;
  min-width: 0;
}

.nav-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  line-height: 1.4;
}

.nav-desc {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 右侧内容 */
.settings-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.content-header h3 {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.content-desc {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
</style>