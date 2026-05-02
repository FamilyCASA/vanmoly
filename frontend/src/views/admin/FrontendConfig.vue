<template>
  <div class="frontend-config-page">
    <div class="page-header">
      <h2>前端配置管理</h2>
      <p>配置 Web 端页面、主题、导航等资源</p>
    </div>

    <!-- 配置标签页 -->
    <el-tabs v-model="activeTab" class="config-tabs">
      <!-- 页面配置 -->
      <el-tab-pane label="页面配置" name="pages">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openPageDialog()">
              <el-icon><Plus /></el-icon> 新建页面
            </el-button>
          </div>
          
          <el-table :data="pages" v-loading="loading" border>
            <el-table-column prop="page_key" label="页面标识" width="120" />
            <el-table-column prop="page_name" label="页面名称" width="150" />
            <el-table-column prop="page_title" label="页面标题" />
            <el-table-column prop="version" label="版本" width="80" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_enabled ? 'success' : 'info'">
                  {{ row.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="editPage(row)">编辑</el-button>
                <el-button link type="primary" @click="clonePage(row)">克隆</el-button>
                <el-button link type="danger" @click="deletePage(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 主题配置 -->
      <el-tab-pane label="主题配置" name="themes">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openThemeDialog()">
              <el-icon><Plus /></el-icon> 新建主题
            </el-button>
          </div>

          <div class="theme-grid">
            <div 
              v-for="theme in themes" 
              :key="theme.id"
              class="theme-card"
              :class="{ 'active': theme.is_active }"
            >
              <div class="theme-preview">
                <div class="color-bar">
                  <div class="color-block" :style="{ background: theme.colors?.primary }"></div>
                  <div class="color-block" :style="{ background: theme.colors?.secondary }"></div>
                  <div class="color-block" :style="{ background: theme.colors?.background }"></div>
                </div>
              </div>
              <div class="theme-info">
                <h4>{{ theme.theme_name }}</h4>
                <p>{{ theme.theme_key }}</p>
                <div class="theme-actions">
                  <el-tag v-if="theme.is_active" type="success">当前激活</el-tag>
                  <el-button v-else link type="primary" @click="activateTheme(theme)">
                    激活
                  </el-button>
                  <el-button link @click="editTheme(theme)">编辑</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 导航配置 -->
      <el-tab-pane label="导航配置" name="navigation">
        <div class="tab-content">
          <el-tabs tab-position="left" v-model="navPosition">
            <el-tab-pane label="顶部导航" name="header">
              <NavigationEditor 
                position="header"
                :config="navigations.header"
                @save="saveNavigation"
              />
            </el-tab-pane>
            <el-tab-pane label="底部导航" name="footer">
              <NavigationEditor 
                position="footer"
                :config="navigations.footer"
                @save="saveNavigation"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-tab-pane>

      <!-- 资源管理 -->
      <el-tab-pane label="资源管理" name="resources">
        <div class="tab-content">
          <div class="toolbar">
            <el-upload
              action="/api/v3/upload/image"
              :on-success="handleUploadSuccess"
              :show-file-list="false"
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon> 上传资源
              </el-button>
            </el-upload>
          </div>

          <div class="resource-grid">
            <div v-for="res in resources" :key="res.id" class="resource-item">
              <div class="resource-preview">
                <img v-if="res.resource_type === 'image'" :src="res.file_url" />
                <el-icon v-else><Document /></el-icon>
              </div>
              <div class="resource-info">
                <p class="resource-name">{{ res.resource_name }}</p>
                <p class="resource-key">{{ res.resource_key }}</p>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 页面编辑对话框 -->
    <el-dialog
      v-model="pageDialog.visible"
      :title="pageDialog.isEdit ? '编辑页面' : '新建页面'"
      width="900px"
      destroy-on-close
    >
      <el-form :model="pageForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="页面标识">
              <el-input v-model="pageForm.page_key" placeholder="如: home, about" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="页面名称">
              <el-input v-model="pageForm.page_name" placeholder="页面显示名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="页面标题">
          <el-input v-model="pageForm.page_title" placeholder="浏览器标签标题" />
        </el-form-item>
        
        <el-form-item label="SEO描述">
          <el-input v-model="pageForm.meta_description" type="textarea" rows="2" />
        </el-form-item>

        <el-form-item label="页面区块">
          <div class="sections-editor">
            <draggable 
              v-model="pageForm.sections" 
              item-key="id"
              handle=".drag-handle"
            >
              <template #item="{ element, index }">
                <div class="section-item">
                  <div class="section-header">
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    <span>{{ element.name || '未命名区块' }}</span>
                    <el-icon class="delete-btn" @click="removeSection(index)"><Delete /></el-icon>
                  </div>
                  <div class="section-config">
                    <el-select v-model="element.component" placeholder="选择组件">
                      <el-option 
                        v-for="comp in components" 
                        :key="comp.component_key"
                        :label="comp.component_name"
                        :value="comp.component_key"
                      />
                    </el-select>
                  </div>
                </div>
              </template>
            </draggable>
            <el-button link type="primary" @click="addSection">
              <el-icon><Plus /></el-icon> 添加区块
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="自定义CSS">
          <el-input 
            v-model="pageForm.custom_css" 
            type="textarea" 
            rows="6"
            placeholder="输入自定义CSS代码"
            class="code-input"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="pageDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="savePage">保存</el-button>
      </template>
    </el-dialog>

    <!-- 主题编辑对话框 -->
    <el-dialog
      v-model="themeDialog.visible"
      :title="themeDialog.isEdit ? '编辑主题' : '新建主题'"
      width="700px"
    >
      <el-form :model="themeForm" label-width="100px">
        <el-form-item label="主题名称">
          <el-input v-model="themeForm.theme_name" />
        </el-form-item>
        <el-form-item label="主题标识">
          <el-input v-model="themeForm.theme_key" />
        </el-form-item>
        
        <el-divider>颜色配置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12" v-for="(color, key) in themeForm.colors" :key="key">
            <el-form-item :label="colorLabels[key] || key">
              <el-color-picker v-model="themeForm.colors[key]" show-alpha />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="themeDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveTheme">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Rank, Upload, Document } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import NavigationEditor from '@/components/NavigationEditor.vue'
import request from '@/utils/request'

const activeTab = ref('pages')
const loading = ref(false)

// 页面配置
const pages = ref([])
const pageDialog = reactive({
  visible: false,
  isEdit: false
})
const pageForm = reactive({
  id: null,
  page_key: '',
  page_name: '',
  page_title: '',
  meta_description: '',
  meta_keywords: '',
  sections: [],
  custom_css: '',
  is_enabled: true
})

// 主题配置
const themes = ref([])
const themeDialog = reactive({
  visible: false,
  isEdit: false
})
const themeForm = reactive({
  theme_name: '',
  theme_key: '',
  colors: {
    primary: '#8B7355',
    secondary: '#C4A77D',
    accent: '#D4A574',
    background: '#FAF8F5',
    surface: '#FFFFFF',
    text: '#2C2420',
    text_secondary: '#6B6560',
    border: '#E8E4E0'
  }
})
const colorLabels = {
  primary: '主色',
  secondary: '次色',
  accent: '强调色',
  background: '背景色',
  surface: '表面色',
  text: '文字色',
  text_secondary: '次要文字',
  border: '边框色'
}

// 导航配置
const navPosition = ref('header')
const navigations = reactive({
  header: null,
  footer: null
})

// 组件库
const components = ref([])

// 资源
const resources = ref([])

// 加载数据
const loadPages = async () => {
  loading.value = true
  try {
    const res = await request.get('/frontend/pages')
    pages.value = res || []
  } catch (error) {
    ElMessage.error('加载页面配置失败')
  } finally {
    loading.value = false
  }
}

const loadThemes = async () => {
  try {
    const res = await request.get('/frontend/themes')
    themes.value = res || []
  } catch (error) {
    ElMessage.error('加载主题失败')
  }
}

const loadNavigations = async () => {
  try {
    const headerRes = await request.get('/frontend/navigation/header')
    navigations.header = headerRes
    
    const footerRes = await request.get('/frontend/navigation/footer')
    navigations.footer = footerRes
  } catch (error) {
    console.error('加载导航失败', error)
  }
}

const loadComponents = async () => {
  try {
    const res = await request.get('/frontend/components')
    components.value = res || []
  } catch (error) {
    console.error('加载组件库失败', error)
  }
}

const loadResources = async () => {
  try {
    const res = await request.get('/frontend/resources')
    resources.value = res || []
  } catch (error) {
    console.error('加载资源失败', error)
  }
}

// 页面操作
const openPageDialog = (page = null) => {
  pageDialog.isEdit = !!page
  if (page) {
    Object.assign(pageForm, page)
  } else {
    Object.assign(pageForm, {
      id: null,
      page_key: '',
      page_name: '',
      page_title: '',
      meta_description: '',
      meta_keywords: '',
      sections: [],
      custom_css: '',
      is_enabled: true
    })
  }
  pageDialog.visible = true
}

const editPage = (page) => {
  openPageDialog(page)
}

const savePage = async () => {
  try {
    if (pageDialog.isEdit) {
      await request.put(`/frontend/pages/${pageForm.id}`, pageForm)
    } else {
      await request.post('/frontend/pages', pageForm)
    }
    ElMessage.success('保存成功')
    pageDialog.visible = false
    loadPages()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const clonePage = async (page) => {
  try {
    await request.post(`/frontend/pages/${page.id}/clone`, {
      page_key: `${page.page_key}_copy`,
      page_name: `${page.page_name} 副本`
    })
    ElMessage.success('克隆成功')
    loadPages()
  } catch (error) {
    ElMessage.error('克隆失败')
  }
}

const deletePage = async (page) => {
  try {
    await ElMessageBox.confirm('确定删除该页面配置？', '提示', { type: 'warning' })
    await request.delete(`/frontend/pages/${page.id}`)
    ElMessage.success('删除成功')
    loadPages()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addSection = () => {
  pageForm.sections.push({
    id: Date.now(),
    name: `区块 ${pageForm.sections.length + 1}`,
    component: '',
    config: {}
  })
}

const removeSection = (index) => {
  pageForm.sections.splice(index, 1)
}

// 主题操作
const openThemeDialog = (theme = null) => {
  themeDialog.isEdit = !!theme
  if (theme) {
    Object.assign(themeForm, theme)
  } else {
    Object.assign(themeForm, {
      theme_name: '',
      theme_key: '',
      colors: {
        primary: '#8B7355',
        secondary: '#C4A77D',
        accent: '#D4A574',
        background: '#FAF8F5',
        surface: '#FFFFFF',
        text: '#2C2420',
        text_secondary: '#6B6560',
        border: '#E8E4E0'
      }
    })
  }
  themeDialog.visible = true
}

const editTheme = (theme) => {
  openThemeDialog(theme)
}

const saveTheme = async () => {
  try {
    if (themeDialog.isEdit) {
      await request.put(`/frontend/themes/${themeForm.id}`, themeForm)
    } else {
      await request.post('/frontend/themes', themeForm)
    }
    ElMessage.success('保存成功')
    themeDialog.visible = false
    loadThemes()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const activateTheme = async (theme) => {
  try {
    await request.post(`/frontend/themes/${theme.id}/activate`)
    ElMessage.success('主题已激活')
    loadThemes()
  } catch (error) {
    ElMessage.error('激活失败')
  }
}

// 导航操作
const saveNavigation = async (data) => {
  try {
    await request.post('/frontend/navigation', data)
    ElMessage.success('导航配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 资源上传
const handleUploadSuccess = (response) => {
  if (response.code === 200) {
    ElMessage.success('上传成功')
    loadResources()
  }
}

onMounted(() => {
  loadPages()
  loadThemes()
  loadNavigations()
  loadComponents()
  loadResources()
})
</script>

<style scoped>
.frontend-config-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: #666;
}

.config-tabs {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.tab-content {
  padding: 20px 0;
}

.toolbar {
  margin-bottom: 20px;
}

/* 主题卡片 */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.theme-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.theme-card.active {
  border-color: #67c23a;
}

.theme-preview {
  height: 80px;
  background: #f5f7fa;
}

.color-bar {
  display: flex;
  height: 100%;
}

.color-block {
  flex: 1;
}

.theme-info {
  padding: 16px;
}

.theme-info h4 {
  margin: 0 0 4px;
  font-size: 16px;
}

.theme-info p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #999;
}

.theme-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 区块编辑器 */
.sections-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
}

.section-item {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.drag-handle {
  cursor: move;
  color: #999;
}

.delete-btn {
  margin-left: auto;
  cursor: pointer;
  color: #f56c6c;
}

.code-input {
  font-family: 'Courier New', monospace;
}

/* 资源网格 */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.resource-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.resource-preview {
  aspect-ratio: 1;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.resource-preview .el-icon {
  font-size: 48px;
  color: #999;
}

.resource-info {
  padding: 12px;
}

.resource-name {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-key {
  margin: 0;
  font-size: 12px;
  color: #999;
}
</style>
