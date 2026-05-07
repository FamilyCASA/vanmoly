<template>
  <div class="category-manage">
    <!-- 操作栏 -->
    <div class="section-toolbar">
      <el-button type="primary" @click="openCategoryDialog(null)">
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

    <!-- 分类表单对话框 -->
    <el-dialog v-model="categoryDialog.visible" :title="categoryDialog.isEdit ? '编辑分类' : '新建分类'" width="520px" append-to-body>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, FolderOpened, Box } from '@element-plus/icons-vue'
import request from '@/utils/request'

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

onMounted(() => { loadCategories() })
</script>

<style scoped>
.category-manage { padding: 0; }
.section-toolbar { margin-bottom: 16px; }
.stat-card {
  background: #fff; padding: 16px; border-radius: 8px;
  display: flex; align-items: center; gap: 12px;
  border: 1px solid #f0f0f0;
}
.stat-icon {
  width: 40px; height: 40px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.stat-info { flex: 1; }
.stat-value { font-size: 20px; font-weight: bold; color: #333; line-height: 1.2; }
.stat-label { font-size: 12px; color: #999; }
.color-dot {
  display: inline-block; width: 14px; height: 14px;
  border-radius: 3px; margin-right: 6px; vertical-align: middle;
}
</style>
