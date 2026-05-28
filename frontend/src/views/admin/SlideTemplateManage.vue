<template>
  <div class="slide-template-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>幻灯片模板管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新建模板
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模板名称"
          style="width: 200px"
          clearable
          @clear="loadTemplates"
        />
        <el-button type="primary" :icon="Search" @click="loadTemplates">查询</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="filteredTemplates"
        v-loading="loading"
        stripe
        border
        style="margin-top: 16px"
      >
        <el-table-column prop="name" label="模板名称" min-width="150">
          <template #default="{ row }">
            <span class="template-name">
              {{ row.name }}
              <el-tag v-if="row.is_default" size="small" type="success">默认</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="aspect_ratio" label="画幅" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.aspect_ratio || '16:9' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="template_style" label="风格" width="90" align="center">
          <template #default="{ row }">
            {{ row.template_style === 'dark' ? '深色' : row.template_style === 'light' ? '浅色' : '极简' }}
          </template>
        </el-table-column>
        <el-table-column prop="primary_color" label="主色" width="80" align="center">
          <template #default="{ row }">
            <div class="color-swatch" :style="{ background: row.primary_color || '#8B4513' }"></div>
          </template>
        </el-table-column>
        <el-table-column label="背景图" width="90" align="center">
          <template #default="{ row }">
            <span class="has-bg">{{ (row.cover_bg_image || row.inner_bg_image || row.back_bg_image) ? '有' : '无' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="启用状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" size="small" @click="handleDuplicate(row)">复制</el-button>
            <el-button link type="warning" size="small" @click="handleSetDefault(row)" v-if="!row.is_default">
              设为默认
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)" :disabled="row.is_default">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '新建模板' : '编辑模板'"
      width="720px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-position="top" class="edit-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板名称" required>
              <el-input v-model="form.name" placeholder="如：标准版 16:9" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认模板">
              <el-switch v-model="form.is_default" />
              <span class="form-tip">新建案例时自动应用此模板</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="模板描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="简要描述此模板的用途" maxlength="500" />
        </el-form-item>

        <el-divider content-position="left">幻灯片样式</el-divider>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="模板风格">
              <el-select v-model="form.template_style" style="width:100%">
                <el-option value="dark" label="深色风格" />
                <el-option value="light" label="浅色风格" />
                <el-option value="minimal" label="极简风格" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="画幅比例">
              <el-select v-model="form.aspect_ratio" style="width:100%">
                <el-option value="16:9" label="16:9 标准" />
                <el-option value="21:9" label="21:9 宽屏" />
                <el-option value="4:3" label="4:3 经典" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="主色调">
              <el-color-picker v-model="form.primary_color" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">背景图</el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="封面背景图">
              <ImageCropperUpload v-model="form.cover_bg_image" />
              <div class="form-tip">用于封面页（首页）</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="内页背景图">
              <ImageCropperUpload v-model="form.inner_bg_image" />
              <div class="form-tip">用于内容页（默认背景）</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="封底背景图">
          <ImageCropperUpload v-model="form.back_bg_image" />
          <div class="form-tip">用于结束页（最后一页）</div>
        </el-form-item>

        <el-divider content-position="left">封面配置</el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品牌名称">
              <el-input v-model="form.brand_name" placeholder="默认：DESIGNARY" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="封面标题（可覆盖案例标题）">
              <el-input v-model="form.cover_title" placeholder="留空则使用案例标题" maxlength="200" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="封面副标题">
          <el-input v-model="form.cover_subtitle" placeholder="可选" maxlength="200" />
        </el-form-item>

        <el-divider content-position="left">关于我们页</el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标题">
              <el-input v-model="form.about_title" placeholder="默认：关于我们" maxlength="200" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="副标题">
              <el-input v-model="form.about_subtitle" placeholder="可选" maxlength="200" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="内容">
          <el-input v-model="form.about_content" type="textarea" :rows="3" placeholder="公司口号或简介" />
        </el-form-item>

        <el-divider content-position="left">页面开关</el-divider>

        <div class="switch-grid">
          <div class="switch-item">
            <span>关于我们</span>
            <el-switch v-model="form.show_about" />
          </div>
          <div class="switch-item">
            <span>团队展示</span>
            <el-switch v-model="form.show_team" />
          </div>
          <div class="switch-item">
            <span>目录</span>
            <el-switch v-model="form.show_toc" />
          </div>
          <div class="switch-item">
            <span>材质展示</span>
            <el-switch v-model="form.show_material" />
          </div>
          <div class="switch-item">
            <span>物料展示</span>
            <el-switch v-model="form.show_product" />
          </div>
          <div class="switch-item">
            <span>工法展示</span>
            <el-switch v-model="form.show_process" />
          </div>
          <div class="switch-item">
            <span>物料汇总</span>
            <el-switch v-model="form.show_summary" />
          </div>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import ImageCropperUpload from '@/components/ImageCropperUpload.vue'
import {
  getSlideTemplates, createSlideTemplate, updateSlideTemplate,
  deleteSlideTemplate, duplicateSlideTemplate
} from '@/api/case'

const loading = ref(false)
const saving = ref(false)
const templates = ref([])
const searchKeyword = ref('')

const dialogVisible = ref(false)
const dialogMode = ref('add') // 'add' | 'edit'

const defaultForm = () => ({
  name: '',
  description: '',
  is_default: false,
  is_active: true,
  template_style: 'dark',
  primary_color: '#8B4513',
  aspect_ratio: '16:9',
  cover_title: '',
  cover_subtitle: '',
  brand_name: 'DESIGNARY',
  cover_bg_image: '',
  inner_bg_image: '',
  back_bg_image: '',
  about_title: '关于我们',
  about_subtitle: '',
  about_content: '',
  about_image: '',
  show_about: true,
  show_team: true,
  show_toc: true,
  show_material: true,
  show_product: true,
  show_process: true,
  show_summary: true,
})

const form = ref(defaultForm())

const filteredTemplates = computed(() => {
  if (!searchKeyword.value) return templates.value
  const kw = searchKeyword.value.toLowerCase()
  return templates.value.filter(t =>
    t.name.toLowerCase().includes(kw) ||
    (t.description && t.description.toLowerCase().includes(kw))
  )
})

const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await getSlideTemplates()
    templates.value = res || []
  } catch (e) {
    console.error('Load templates failed:', e)
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  form.value = defaultForm()
  dialogMode.value = 'add'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.value = { ...defaultForm(), ...row }
  dialogMode.value = 'edit'
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('模板名称不能为空')
    return
  }
  saving.value = true
  try {
    if (dialogMode.value === 'add') {
      await createSlideTemplate(form.value)
      ElMessage.success('模板创建成功')
    } else {
      await updateSlideTemplate(form.value.id, form.value)
      ElMessage.success('模板已更新')
    }
    dialogVisible.value = false
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDuplicate = async (row) => {
  try {
    await duplicateSlideTemplate(row.id, { name: `${row.name} (副本)` })
    ElMessage.success('模板已复制')
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.message || '复制失败')
  }
}

const handleSetDefault = async (row) => {
  try {
    await updateSlideTemplate(row.id, { ...row, is_default: true })
    ElMessage.success('已设为默认模板')
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除模板「${row.name}」？删除后无法恢复。`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteSlideTemplate(row.id)
    ElMessage.success('模板已删除')
    loadTemplates()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  display: flex;
  gap: 8px;
  align-items: center;
}
.template-name {
  display: flex;
  align-items: center;
  gap: 8px;
}
.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #ddd;
  display: inline-block;
}
.has-bg {
  font-size: 12px;
  color: #52c41a;
}
.switch-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 13px;
}
.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>