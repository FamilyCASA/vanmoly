<template>
  <div class="finance-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          class="finance-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/finance/overview">
            <el-icon><DataLine /></el-icon>
            <span>财务总览</span>
          </el-menu-item>
          
          <el-menu-item index="/finance/transactions">
            <el-icon><Document /></el-icon>
            <span>流水管理</span>
          </el-menu-item>
          
          <el-menu-item index="/finance/reimbursements">
            <el-icon><Money /></el-icon>
            <span>报销管理</span>
          </el-menu-item>
          
          <el-menu-item index="/finance/my-reimbursements">
            <el-icon><Document /></el-icon>
            <span>我的报销</span>
          </el-menu-item>
          
          <el-sub-menu index="investment">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>投资管理</span>
            </template>
            <el-menu-item index="/finance/shareholders">
              股东信息
            </el-menu-item>
            <el-menu-item index="/finance/charter">
              企业章程
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/finance/audit-logs">
            <el-icon><List /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          
          <el-menu-item v-if="isFinanceAdmin" index="/finance/members">
            <el-icon><User /></el-icon>
            <span>团队管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataLine, Document, Money, TrendCharts, List, User } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

const router = useRouter()
const route = useRoute()

const activeMenu = ref('/finance/overview')
const isFinanceAdmin = ref(false)

onMounted(async () => {
  // 获取当前用户的财务权限
  try {
    const permData = await financeAPI.getMyPermissions()
    if (permData && permData.permissions) {
      isFinanceAdmin.value = permData.permissions.includes('settings')
    }
  } catch (error) {
    console.error('获取权限失败:', error)
  }
  
  // 设置当前激活的菜单项
  activeMenu.value = route.path
})

const handleMenuSelect = (index) => {
  router.push(index)
}
</script>

<style scoped>
.finance-layout {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: white;
}

.finance-menu {
  border-right: none;
  background-color: #304156;
}

.finance-menu .el-menu-item,
.finance-menu .el-sub-menu__title {
  color: #bfcbd9;
}

.finance-menu .el-menu-item:hover,
.finance-menu .el-sub-menu__title:hover {
  background-color: #263445;
}

.finance-menu .el-menu-item.is-active {
  color: #409eff;
  background-color: #ecf5ff;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
