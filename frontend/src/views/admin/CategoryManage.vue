<template>
  <div class="category-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>分类管理</h2>
        <span class="subtitle">管理物料分类体系</span>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新建分类
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
            <el-icon><Folder /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total || 0 }}</div>
            <div class="stat-label">总分类</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.enabled || 0 }}</div>
            <div class="stat-label">已启用</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF7E6; color: #FA8C16;">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.withMaterials || 0 }}</div>
            <div class="stat-label">有物料</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 分类树表格 -->
    <el-card shadow="never">
      <el-table
        :data="categoryTree"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        v-loading="loading"
      >
        <el-table-column label="分类名称" min-width="200">
          <template #default="{ row }">
            <div class="category-name">
              <el-icon v-if="row.icon" :style="{ color: row.color }">
                <component :is="row.icon" />
              </el-icon>
              <span v-else class="color-dot" :style="{ background: row.color }"></span>
              <span>{{ row.name }}</span>
              <el-tag v-if="!row.is_enabled" type="info" size="small" class="ml-2">已禁用</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="编码" width="120">
          <template #default="{ row }">
            <code>{{ row.code || '-' }}</code>
          </template>
        </el-table-column>

        <el-table-column label="层级" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.level === 1 ? 'primary' : row.level === 2 ? 'success' : 'info'">
              {{ row.level }}级
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="物料数" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewMaterials(row)">
              {{ row.material_count || 0 }}
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="排序" width="80" align="center">
          <template #default="{ row }">
            {{ row.sort_order }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="openDialog(null, row.id)">添加子类</el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button link>
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="toggle">
                    {{ row.is_enabled ? '禁用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分类表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑分类' : '新建分类'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="上级分类">
          <el-cascader
            v-model="form.parent_id"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', checkStrictly: true }"
            placeholder="作为一级分类"
            clearable
            style="width: 100%"
            :disabled="dialog.isEdit"
          />
        </el-form-item>

        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>

        <el-form-item label="分类编码">
          <el-input v-model="form.code" placeholder="可选，用于系统识别" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="颜色标识">
              <el-color-picker v-model="form.color" show-alpha />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="状态">
          <el-switch
            v-model="form.is_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, FolderOpened, Box, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const categoryTree = ref([])
const stats = ref({})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  parent_id: null,
  name: '',
  code: '',
  color: '#8B5A2B',
  sort_order: 0,
  is_enabled: true
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const formRef = ref(null)

// 计算属性：分类选项（用于级联选择）
const categoryOptions = computed(() => {
  const flatten = (items) => {
    return items.map(item => ({
      id: item.id,
      name: item.name,
      children: item.children ? flatten(item.children) : []
    }))
  }
  return flatten(categoryTree.value)
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/materials/categories')
    categoryTree.value = res
    calculateStats(res)
  } catch (error) {
    console.error('加载分类失败', error)
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

// 计算统计
const calculateStats = (categories) => {
  let total = 0
  let enabled = 0
  let withMaterials = 0

  const count = (items) => {
    items.forEach(item => {
      total++
      if (item.is_enabled) enabled++
      if (item.material_count > 0) withMaterials++
      if (item.children) count(item.children)
    })
  }

  count(categories)
  stats.value = { total, enabled, withMaterials }
}

// 打开对话框
const openDialog = (row = null, parentId = null) => {
  dialog.isEdit = !!row
  dialog.visible = true

  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, {
      id: null,
      parent_id: parentId,
      name: '',
      code: '',
      color: '#8B5A2B',
      sort_order: 0,
      is_enabled: true
    })
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  dialog.loading = true
  try {
    const data = { ...form }
    if (Array.isArray(data.parent_id)) {
      data.parent_id = data.parent_id[data.parent_id.length - 1]
    }

    if (dialog.isEdit) {
      await request.put(`/materials/categories/${form.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/materials/categories', data)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    dialog.loading = false
  }
}

// 更多操作
const handleCommand = async (command, row) => {
  if (command === 'toggle') {
    try {
      await request.put(`/materials/categories/${row.id}`, {
        is_enabled: !row.is_enabled
      })
      ElMessage.success(row.is_enabled ? '已禁用' : '已启用')
      loadData()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除该分类吗？', '提示', { type: 'warning' })
      await request.delete(`/materials/categories/${row.id}`)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      if (error !== 'cancel') ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

// 查看分类物料
const viewMaterials = (row) => {
  // 跳转到物料管理并筛选该分类
  window.location.href = `/#/materials?category_id=${row.id}`
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.category-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin-left: 8px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.category-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.ml-2 {
  margin-left: 8px;
}
</style>