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

      <!-- 系统设置弹窗 -->
      <el-drawer v-model="settingsVisible" title="系统设置" size="900px" :destroy-on-close="true">
        <div v-if="!hasSettingsPermission" style="padding:40px;text-align:center;color:#999;">
          <p>您没有权限访问系统设置</p>
          <p style="font-size:13px;">仅超级管理员和门店负责人可使用此功能</p>
        </div>
        <div v-else>
          <!-- 分类管理 -->
          <div class="settings-section">
            <h3 class="section-title">
              <el-icon><Folder /></el-icon>
              物料分类管理
            </h3>
            <!-- 操作栏 -->
            <div class="section-toolbar">
              <el-button type="primary" @click="categoryDialog.visible = true; categoryDialog.isEdit = false; resetCategoryForm()">
                <el-icon><Plus /></el-icon> 新建分类
              </el-button>
            </div>
            <!-- 统计卡片 -->
            <el-row :gutter="16" style="margin-bottom:16px;">
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background:#E6F7FF;color:#1890FF;"><el-icon><Folder /></el-icon></div>
                  <div class="stat-info">
                    <div class="stat-value">{{ categoryStats.total || 0 }}</div>
                    <div class="stat-label">总分类</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background:#F6FFED;color:#52C41A;"><el-icon><FolderOpened /></el-icon></div>
                  <div class="stat-info">
                    <div class="stat-value">{{ categoryStats.enabled || 0 }}</div>
                    <div class="stat-label">已启用</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background:#FFF7E6;color:#FA8C16;"><el-icon><Box /></el-icon></div>
                  <div class="stat-info">
                    <div class="stat-value">{{ categoryStats.withMaterials || 0 }}</div>
                    <div class="stat-label">有物料</div>
                  </div>
                </div>
              </el-col>
            </el-row>
            <!-- 分类树表格 -->
            <el-table :data="categoryTree" row-key="id" default-expand-all :tree-props="{ children: 'children' }" v-loading="categoryLoading" size="small">
              <el-table-column label="分类名称" min-width="180">
                <template #default="{ row }">
                  <span class="color-dot" :style="{ background: row.color }"></span>
                  <span>{{ row.name }}</span>
                  <el-tag v-if="!row.is_enabled" type="info" size="small" style="margin-left:6px;">已禁用</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="编码" width="100" size="small"><template #default="{ row }"><code>{{ row.code || '-' }}</code></template></el-table-column>
              <el-table-column label="层级" width="70" align="center" size="small">
                <template #default="{ row }">
                  <el-tag size="small" :type="row.level === 1 ? 'primary' : 'success'">{{ row.level }}级</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="排序" width="70" align="center" size="small">
                <template #default="{ row }">{{ row.sort_order }}</template>
              </el-table-column>
              <el-table-column label="操作" width="160" size="small">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="openCategoryDialog(row)">编辑</el-button>
                  <el-button link type="primary" size="small" @click="openCategoryDialog(null, row.id)">添加子类</el-button>
                  <el-button link type="danger" size="small" @click="deleteCategory(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-drawer>

      <!-- 分类表单对话框 -->
      <el-dialog v-model="categoryDialog.visible" :title="categoryDialog.isEdit ? '编辑分类' : '新建分类'" width="520px">
        <el-form ref="categoryFormRef" :model="categoryForm" :rules="categoryRules" label-width="90px">
          <el-form-item label="上级分类">
            <el-cascader v-model="categoryForm.parent_id" :options="categoryOptions" :props="{ value:'id', label:'name', checkStrictly:true }" placeholder="作为一级分类" clearable style="width:100%" :disabled="categoryDialog.isEdit" />
          </el-form-item>
          <el-form-item label="分类名称" prop="name">
            <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
          </el-form-item>
          <el-form-item label="分类编码">
            <el-input v-model="categoryForm.code" placeholder="可选" />
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="颜色">
                <el-color-picker v-model="categoryForm.color" show-alpha />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="排序">
                <el-input-number v-model="categoryForm.sort_order" :min="0" style="width:100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="状态">
            <el-switch v-model="categoryForm.is_enabled" active-text="启用" inactive-text="禁用" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="categoryDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="submitCategory" :loading="categoryDialog.loading">确定</el-button>
        </template>
      </el-dialog>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine, Picture, User, Calendar, Folder, Setting, Fold, Expand, UserFilled, ArrowDown, Box, Connection, Document, OfficeBuilding, Money, Shop, Plus, FolderOpened } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const isCollapse = ref(false)
const userInfo = ref(null)

// 系统设置弹窗
const settingsVisible = ref(false)
const hasSettingsPermission = computed(() => {
  if (!userInfo.value) return false
  const role = userInfo.value.role || userInfo.value.user_type || ''
  return ['super_admin', 'store_manager'].includes(role)
})

const openSettingsDialog = () => {
  if (!hasSettingsPermission.value) {
    ElMessage.warning('您没有权限访问系统设置')
    return
  }
  settingsVisible.value = true
  loadCategories()
}

// 分类管理状态
const categoryLoading = ref(false)
const categoryTree = ref([])
const categoryStats = ref({})
const categoryFormRef = ref(null)
const categoryDialog = reactive({ visible: false, isEdit: false, loading: false })
const categoryForm = reactive({ id: null, parent_id: null, name: '', code: '', color: '#8B5A2B', sort_order: 0, is_enabled: true })
const categoryRules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

const categoryOptions = computed(() => {
  const flatten = (items) => items.map(item => ({ id: item.id, name: item.name, children: item.children ? flatten(item.children) : [] }))
  return flatten(categoryTree.value)
})

const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await request.get('/materials/categories')
    categoryTree.value = res
    let total = 0, enabled = 0, withMaterials = 0
    const count = (items) => items.forEach(item => {
      total++; if (item.is_enabled) enabled++; if (item.material_count > 0) withMaterials++
      if (item.children) count(item.children)
    })
    count(res)
    categoryStats.value = { total, enabled, withMaterials }
  } catch (e) { ElMessage.error('加载分类失败') }
  finally { categoryLoading.value = false }
}

const resetCategoryForm = () => Object.assign(categoryForm, { id: null, parent_id: null, name: '', code: '', color: '#8B5A2B', sort_order: 0, is_enabled: true })

const openCategoryDialog = (row = null, parentId = null) => {
  categoryDialog.isEdit = !!row
  categoryDialog.visible = true
  if (row) Object.assign(categoryForm, row)
  else { resetCategoryForm(); categoryForm.parent_id = parentId }
}

const submitCategory = async () => {
  const valid = await categoryFormRef.value?.validate().catch(() => false)
  if (!valid) return
  categoryDialog.loading = true
  try {
    const data = { ...categoryForm }
    if (Array.isArray(data.parent_id)) data.parent_id = data.parent_id[data.parent_id.length - 1]
    if (categoryDialog.isEdit) await request.put(`/materials/categories/${categoryForm.id}`, data)
    else await request.post('/materials/categories', data)
    ElMessage.success('操作成功')
    categoryDialog.visible = false
    loadCategories()
  } catch (e) { ElMessage.error(e.response?.data?.message || '操作失败') }
  finally { categoryDialog.loading = false }
}

const deleteCategory = async (row) => {
  await ElMessageBox.confirm('确定删除该分类吗？', '提示', { type: 'warning' })
  await request.delete(`/materials/categories/${row.id}`)
  ElMessage.success('删除成功')
  loadCategories()
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) userInfo.value = JSON.parse(userStr)
})

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'settings':
      openSettingsDialog()
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

/* 系统设置弹窗样式 */
.settings-section {
  padding: 0 4px 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.section-toolbar {
  margin-bottom: 12px;
}

.stat-card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.color-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  margin-right: 6px;
  vertical-align: middle;
}
</style>
