<template>
  <div class="template-settings">
    <div class="page-header">
      <el-page-header @back="$router.back()">
        <template #content>报价模板管理</template>
        <template #extra>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建模板
          </el-button>
        </template>
      </el-page-header>
    </div>

    <el-table :data="templates" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="模板名称" min-width="150" />
      <el-table-column prop="template_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ typeLabel(row.template_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="主题色" width="120">
        <template #default="{ row }">
          <div style="display:flex;gap:4px;align-items:center">
            <span class="color-dot" :style="{ background: row.style_config?.primary_color || '#409eff' }"></span>
            <span class="color-dot" :style="{ background: row.style_config?.secondary_color || '#67c23a' }"></span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="背景图" width="80" align="center">
        <template #default="{ row }">
          {{ (row.background_images || []).length }}张
        </template>
      </el-table-column>
      <el-table-column prop="is_default" label="默认" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="70" align="center" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="form.template_type">
            <el-option label="现代" value="modern" />
            <el-option label="经典" value="classic" />
            <el-option label="极简" value="minimal" />
            <el-option label="奢华" value="luxury" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">样式配置</el-divider>
        <el-form-item label="主色">
          <el-color-picker v-model="form.style_config.primary_color" />
        </el-form-item>
        <el-form-item label="副色">
          <el-color-picker v-model="form.style_config.secondary_color" />
        </el-form-item>
        <el-form-item label="背景色">
          <el-color-picker v-model="form.style_config.background_color" />
        </el-form-item>
        <el-form-item label="字体">
          <el-select v-model="form.style_config.font_family" style="width:200px">
            <el-option label="微软雅黑" value="Microsoft YaHei" />
            <el-option label="宋体" value="SimSun" />
            <el-option label="黑体" value="SimHei" />
            <el-option label="楷体" value="KaiTi" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">水印配置</el-divider>
        <el-form-item label="水印文字">
          <el-input v-model="form.watermark_config.text" placeholder="例如：公司名称" />
        </el-form-item>
        <el-form-item label="透明度">
          <el-slider v-model="form.watermark_config.opacity" :min="0" :max="1" :step="0.05" show-input />
        </el-form-item>
        <el-divider content-position="left">其他</el-divider>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const templates = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editingId = ref(null)

const defaultForm = {
  name: '',
  template_type: 'modern',
  style_config: {
    primary_color: '#409eff',
    secondary_color: '#67c23a',
    background_color: '#ffffff',
    font_family: 'Microsoft YaHei'
  },
  watermark_config: {
    text: '',
    opacity: 0.1,
    font_size: 48,
    angle: -45
  },
  background_images: [],
  is_default: false,
  sort_order: 0
}

const form = reactive({ ...JSON.parse(JSON.stringify(defaultForm)) })

const typeLabel = (type) => {
  const map = { modern: '现代', classic: '经典', minimal: '极简', luxury: '奢华' }
  return map[type] || type
}

const loadTemplates = async () => {
  try {
    loading.value = true
    const res = await request.get('/quotes/templates')
    templates.value = res.data?.data || res.data || []
  } catch (e) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(form, JSON.parse(JSON.stringify(defaultForm)))
  isEditing.value = false
  editingId.value = null
}

const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEditing.value = true
  editingId.value = row.id
  form.name = row.name
  form.template_type = row.template_type
  form.style_config = { ...defaultForm.style_config, ...(row.style_config || {}) }
  form.watermark_config = { ...defaultForm.watermark_config, ...(row.watermark_config || {}) }
  form.background_images = row.background_images || []
  form.is_default = row.is_default || false
  form.sort_order = row.sort_order || 0
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  try {
    saving.value = true
    if (isEditing.value) {
      await request.put(`/quotes/templates/${editingId.value}`, {
        name: form.name,
        template_type: form.template_type,
        style_config: form.style_config,
        watermark_config: form.watermark_config,
        background_images: form.background_images,
        is_default: form.is_default,
        sort_order: form.sort_order
      })
      ElMessage.success('更新成功')
    } else {
      await request.post('/quotes/templates', {
        name: form.name,
        template_type: form.template_type,
        style_config: form.style_config,
        watermark_config: form.watermark_config,
        background_images: form.background_images,
        is_default: form.is_default,
        sort_order: form.sort_order
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除模板「${row.name}」？`, '提示', { type: 'warning' })
    await request.delete(`/quotes/templates/${row.id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-settings {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #ddd;
  display: inline-block;
}
</style>
