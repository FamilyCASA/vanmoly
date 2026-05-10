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

      <!-- 首页编辑（8区块） -->
      <el-tab-pane label="首页编辑" name="hero">
        <div class="blocks-list">

          <!-- Block 1: Hero -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'hero' }">
            <div class="block-header" @click="toggleBlock('hero')">
              <div class="block-info">
                <span class="block-order">01</span>
                <div class="block-meta">
                  <h3>Hero 轮播大图</h3>
                  <p>首页顶部横幅轮播，支持多图滑动</p>
                </div>
              </div>
              <div class="block-actions">
                <el-tag type="info">{{ heroSlides.length }} 张</el-tag>
                <el-button type="primary" link @click.stop="toggleBlock('hero')">
                  {{ expandedBlock === 'hero' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'hero'" class="block-body">
              <div class="edit-toolbar">
                <el-button type="primary" size="small" @click="openHeroUpload">
                  <el-icon><Plus /></el-icon> 添加图片
                </el-button>
                <span class="tip">建议尺寸 1920x1080，支持 JPG/PNG</span>
              </div>
              <div class="hero-preview-grid">
                <div v-for="(slide, idx) in heroSlides" :key="slide.id" class="hero-preview-item">
                  <div class="preview-thumb">
                    <img :src="resolveUrl(slide.url)" alt="" />
                  </div>
                  <div class="preview-actions">
                    <el-button link size="small" :disabled="idx === 0" @click="moveHeroSlide(idx, -1)">上移</el-button>
                    <el-button link size="small" :disabled="idx === heroSlides.length - 1" @click="moveHeroSlide(idx, 1)">下移</el-button>
                    <el-button link type="danger" size="small" @click="heroSlides.splice(idx, 1)">删除</el-button>
                  </div>
                </div>
                <div v-if="heroSlides.length === 0" class="empty-tip">暂无轮播图，点击上方按钮添加</div>
              </div>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.hero" @click="saveHero">保存轮播图</el-button>
              </div>
            </div>
          </div>

          <!-- Block 2: 服务优势 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'services' }">
            <div class="block-header" @click="toggleBlock('services')">
              <div class="block-info">
                <span class="block-order">02</span>
                <div class="block-meta">
                  <h3>服务优势</h3>
                  <p>4个服务卡片，标题+描述+特性列表</p>
                </div>
              </div>
              <div class="block-actions">
                <el-tag type="info">{{ services.length }} 个</el-tag>
                <el-button type="primary" link @click.stop="toggleBlock('services')">
                  {{ expandedBlock === 'services' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'services'" class="block-body">
              <div class="edit-toolbar">
                <el-button size="small" @click="addService">
                  <el-icon><Plus /></el-icon> 添加服务
                </el-button>
              </div>
              <div v-for="(svc, idx) in services" :key="idx" class="service-edit-item">
                <div class="item-header">
                  <span>服务 {{ idx + 1 }}</span>
                  <el-button link type="danger" size="small" @click="services.splice(idx, 1)">删除</el-button>
                </div>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="标题" size="small">
                      <el-input v-model="svc.title" placeholder="服务名称，如：全案设计" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="描述" size="small">
                      <el-input v-model="svc.desc" placeholder="简短描述" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="特性（逗号分隔）" size="small">
                      <el-input v-model="svc.featuresText" placeholder="空间规划设计, 效果图呈现" @blur="syncFeatures(svc)" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.services" @click="saveServices">保存服务优势</el-button>
              </div>
            </div>
          </div>

          <!-- Block 3: 精选案例 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'cases' }">
            <div class="block-header" @click="toggleBlock('cases')">
              <div class="block-info">
                <span class="block-order">03</span>
                <div class="block-meta">
                  <h3>精选案例</h3>
                  <p>案例展示区，指向案例管理页面</p>
                </div>
              </div>
              <div class="block-actions">
                <el-button type="primary" link @click.stop="toggleBlock('cases')">
                  {{ expandedBlock === 'cases' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'cases'" class="block-body">
              <el-alert type="info" :closable="false" show-icon>
                精选案例由 <strong>案例管理</strong> 模块控制，请前往
                <router-link to="/admin/cases" class="alert-link">案例管理</router-link> 管理。
              </el-alert>
              <div class="edit-footer">
                <el-button type="default" @click="toggleBlock('cases')">关闭</el-button>
              </div>
            </div>
          </div>

          <!-- Block 4: 关于我们 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'about' }">
            <div class="block-header" @click="toggleBlock('about')">
              <div class="block-info">
                <span class="block-order">04</span>
                <div class="block-meta">
                  <h3>关于我们</h3>
                  <p>品牌介绍文案 + 配图 + 数据统计</p>
                </div>
              </div>
              <div class="block-actions">
                <el-button type="primary" link @click.stop="toggleBlock('about')">
                  {{ expandedBlock === 'about' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'about'" class="block-body">
              <el-form label-width="100px" label-position="left">
                <el-form-item label="品牌介绍">
                  <el-input v-model="aboutData.intro" type="textarea" :rows="3" placeholder="品牌介绍第一段" />
                </el-form-item>
                <el-form-item label="品牌介绍2">
                  <el-input v-model="aboutData.intro2" type="textarea" :rows="3" placeholder="品牌介绍第二段" />
                </el-form-item>
                <el-form-item label="品牌配图">
                  <div class="img-upload-row">
                    <div v-if="aboutData.image" class="img-preview">
                      <img :src="resolveUrl(aboutData.image)" />
                      <div class="img-overlay">
                        <el-button size="small" @click="aboutData.image = ''">更换</el-button>
                      </div>
                    </div>
                    <el-button v-else size="small" @click="uploadAboutImage">上传配图</el-button>
                  </div>
                </el-form-item>
                <el-divider content-position="left">数据统计（最多3个）</el-divider>
                <div v-for="(stat, idx) in aboutData.stats" :key="idx" class="stat-edit-row">
                  <el-input v-model="stat.value" placeholder="数值，如：50+" style="width:120px" />
                  <el-input v-model="stat.label" placeholder="标签，如：专业设计师" style="flex:1" />
                  <el-button link type="danger" @click="aboutData.stats.splice(idx, 1)">删除</el-button>
                </div>
                <el-button size="small" @click="aboutData.stats.push({ value: '', label: '' })" :disabled="aboutData.stats.length >= 3">
                  + 添加统计项
                </el-button>
              </el-form>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.about" @click="saveAbout">保存关于我们</el-button>
              </div>
            </div>
          </div>

          <!-- Block 5: 品牌背书 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'brands' }">
            <div class="block-header" @click="toggleBlock('brands')">
              <div class="block-info">
                <span class="block-order">05</span>
                <div class="block-meta">
                  <h3>品牌背书</h3>
                  <p>合作 logo 展示，3x4宫格排列</p>
                </div>
              </div>
              <div class="block-actions">
                <el-tag type="info">{{ brandLogos.length }} 个</el-tag>
                <el-button type="primary" link @click.stop="toggleBlock('brands')">
                  {{ expandedBlock === 'brands' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'brands'" class="block-body">
              <div class="edit-toolbar">
                <el-button type="primary" size="small" @click="uploadBrandLogo">
                  <el-icon><Plus /></el-icon> 添加品牌 Logo
                </el-button>
                <span class="tip">建议尺寸 200×200，兼容 JPG/PNG/WEBP</span>
              </div>
              <div class="brand-grid-edit">
                <div v-for="(logo, idx) in brandLogos" :key="idx" class="brand-logo-item">
                  <div class="logo-preview">
                    <img :src="resolveUrl(logo.url)" alt="" />
                  </div>
                  <el-button link type="danger" size="small" @click="brandLogos.splice(idx, 1)">删除</el-button>
                </div>
                <div v-if="brandLogos.length === 0" class="empty-tip">暂无 logo，点击上方按钮添加</div>
              </div>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.brands" @click="saveBrands">保存品牌背书</el-button>
              </div>
            </div>
          </div>

          <!-- Block 6: CTA -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'cta' }">
            <div class="block-header" @click="toggleBlock('cta')">
              <div class="block-info">
                <span class="block-order">06</span>
                <div class="block-meta">
                  <h3>CTA 行动号召</h3>
                  <p>主标题 + 副标题 + 按钮文字</p>
                </div>
              </div>
              <div class="block-actions">
                <el-button type="primary" link @click.stop="toggleBlock('cta')">
                  {{ expandedBlock === 'cta' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'cta'" class="block-body">
              <el-form label-width="100px" label-position="left">
                <el-form-item label="主标题">
                  <el-input v-model="ctaData.title" placeholder="准备好打造您的理想之家了吗？" />
                </el-form-item>
                <el-form-item label="副标题">
                  <el-input v-model="ctaData.subtitle" placeholder="立即预约免费量尺..." />
                </el-form-item>
                <el-form-item label="主按钮文字">
                  <el-input v-model="ctaData.primaryBtn" placeholder="预约免费量尺" />
                </el-form-item>
                <el-form-item label="副按钮文字">
                  <el-input v-model="ctaData.secondaryBtn" placeholder="400 6118 315"" />
                </el-form-item>
              </el-form>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.cta" @click="saveCta">保存 CTA</el-button>
              </div>
            </div>
          </div>

          <!-- Block 7: 联系信息 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'contact' }">
            <div class="block-header" @click="toggleBlock('contact')">
              <div class="block-info">
                <span class="block-order">07</span>
                <div class="block-meta">
                  <h3>联系信息</h3>
                  <p>展厅地址、电话、营业时间</p>
                </div>
              </div>
              <div class="block-actions">
                <el-button type="primary" link @click.stop="toggleBlock('contact')">
                  {{ expandedBlock === 'contact' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'contact'" class="block-body">
              <el-form label-width="100px" label-position="left">
                <el-form-item label="展厅地址">
                  <el-input v-model="contactData.address" placeholder="成都市青羊区蔡桥街道..." />
                </el-form-item>
                <el-form-item label="服务热线">
                  <el-input v-model="contactData.phone" placeholder="139 0817 9177" />
                </el-form-item>
                <el-form-item label="营业时间">
                  <el-input v-model="contactData.hours" placeholder="周一至周日 9:00-18:00" />
                </el-form-item>
              </el-form>
              <div class="edit-footer">
                <el-button type="primary" :loading="saving.contact" @click="saveContact">保存联系信息</el-button>
              </div>
            </div>
          </div>

          <!-- Block 8: 底部导航 -->
          <div class="block-card" :class="{ expanded: expandedBlock === 'footer' }">
            <div class="block-header" @click="toggleBlock('footer')">
              <div class="block-info">
                <span class="block-order">08</span>
                <div class="block-meta">
                  <h3>底部导航</h3>
                  <p>底部链接和版权信息</p>
                </div>
              </div>
              <div class="block-actions">
                <el-button type="primary" link @click.stop="toggleBlock('footer')">
                  {{ expandedBlock === 'footer' ? '收起编辑' : '编辑' }}
                </el-button>
              </div>
            </div>
            <div v-if="expandedBlock === 'footer'" class="block-body">
              <el-alert type="info" :closable="false" show-icon>
                底部导航由 <strong>系统设置 → 导航配置</strong> 统一管理，
                请前往 <router-link to="/admin/settings" class="alert-link">系统设置</router-link> 编辑。
              </el-alert>
              <div class="edit-footer">
                <el-button type="default" @click="toggleBlock('footer')">关闭</el-button>
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

// ===== 首页编辑（8区块） =====
const expandedBlock = ref(null)
const toggleBlock = (key) => { expandedBlock.value = expandedBlock.value === key ? null : key }
const baseURL = 'http://localhost:8080'
const resolveUrl = (path) => { if (!path) return ''; if (path.startsWith('http')) return path; return baseURL + path }
const hiddenUpload = () => { const input = document.createElement('input'); input.type = 'file'; input.accept = 'image/*'; return input }
const saving = reactive({ hero: false, services: false, about: false, brands: false, cta: false, contact: false })

// Hero 轮播图
const heroSlides = ref([])
const loadHero = async () => {
  try { const res = await request.get('/frontend/hero-slides'); heroSlides.value = res || [] } catch (e) { console.error(e) }
}
const openHeroUpload = () => {
  const input = hiddenUpload()
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData(); fd.append('file', file)
    try {
      const res = await request.post('/upload/image', fd)
      const url = res.file_url || res.data?.file_url || res.url || ''
      if (url) { heroSlides.value.push({ id: Date.now(), url, order: heroSlides.value.length }); ElMessage.success('上传成功') }
      else { ElMessage.error('上传失败：未获取到图片地址') }
    } catch (e) { ElMessage.error('上传失败') }
  }
  input.click()
}
const moveHeroSlide = (idx, dir) => {
  const newIdx = idx + dir
  if (newIdx < 0 || newIdx >= heroSlides.value.length) return
  ;[heroSlides.value[idx], heroSlides.value[newIdx]] = [heroSlides.value[newIdx], heroSlides.value[idx]]
  heroSlides.value.forEach((s, i) => { s.order = i })
}
const saveHero = async () => {
  saving.hero = true
  try { await request.put('/frontend/hero-slides', { slides: heroSlides.value.map((s, i) => ({ ...s, order: i })) }); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.hero = false }
}

// 服务优势
const services = ref([
  { title: '全案设计', desc: '从空间规划到软装搭配，提供完整的设计方案', features: ['空间规划设计', '效果图呈现', '施工图深化', '材料选型'], featuresText: '空间规划设计, 效果图呈现, 施工图深化, 材料选型' },
  { title: '定制家具', desc: '自有工厂生产，品质可控，风格统一', features: ['衣柜定制', '橱柜定制', '木门定制', '护墙板'], featuresText: '衣柜定制, 橱柜定制, 木门定制, 护墙板' },
  { title: '施工监理', desc: '专业监理团队，全程把控施工质量', features: ['节点验收', '质量把控', '进度管理', '问题协调'], featuresText: '节点验收, 质量把控, 进度管理, 问题协调' },
  { title: '软装搭配', desc: '专业软装设计师，打造完整家居风格', features: ['家具选配', '窗帘布艺', '灯具搭配', '饰品陈列'], featuresText: '家具选配, 窗帘布艺, 灯具搭配, 饰品陈列' }
])
const syncFeatures = (svc) => { svc.features = svc.featuresText.split(',').map(s => s.trim()).filter(Boolean) }
const addService = () => { services.value.push({ title: '', desc: '', features: [], featuresText: '' }) }
const saveServices = async () => {
  saving.services = true
  try { await request.put('/frontend/services-section', { services: services.value }); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.services = false }
}

// 关于我们
const aboutData = reactive({ intro: '', intro2: '', image: '', stats: [] })
const loadAbout = async () => {
  try { const res = await request.get('/frontend/about-section'); if (res) Object.assign(aboutData, res) } catch (e) { console.error(e) }
}
const uploadAboutImage = () => {
  const input = hiddenUpload()
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData(); fd.append('file', file)
    try {
      const res = await request.post('/upload/image', fd)
      aboutData.image = res.file_url || res.data?.file_url || res.url || ''
      ElMessage.success('上传成功')
    } catch (e) { ElMessage.error('上传失败') }
  }
  input.click()
}
const saveAbout = async () => {
  saving.about = true
  try { await request.put('/frontend/about-section', aboutData); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.about = false }
}

// 品牌背书
const brandLogos = ref([])
const loadBrands = async () => {
  try { const res = await request.get('/frontend/brand-logos'); brandLogos.value = res || [] } catch (e) { console.error(e) }
}
const uploadBrandLogo = () => {
  const input = hiddenUpload()
  input.accept = 'image/jpeg,image/png,image/webp'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData(); fd.append('file', file)
    try {
      const res = await request.post('/upload/image', fd)
      const url = res.file_url || res.data?.file_url || res.url || ''
      if (url) { brandLogos.value.push({ url, name: file.name.replace(/\.[^.]+$/, '') }); ElMessage.success('上传成功') }
      else { ElMessage.error('上传失败') }
    } catch (e) { ElMessage.error('上传失败') }
  }
  input.click()
}
const saveBrands = async () => {
  saving.brands = true
  try { await request.put('/frontend/brand-logos', { logos: brandLogos.value }); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.brands = false }
}

// CTA
const ctaData = reactive({ title: '准备好打造您的理想之家了吗？', subtitle: '立即预约免费量尺，获取专属设计方案与报价', primaryBtn: '预约免费量尺', secondaryBtn: '400-888-8888' })
const loadCta = async () => {
  try { const res = await request.get('/frontend/cta-section'); if (res) Object.assign(ctaData, res) } catch (e) { console.error(e) }
}
const saveCta = async () => {
  saving.cta = true
  try { await request.put('/frontend/cta-section', ctaData); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.cta = false }
}

// 联系信息
const contactData = reactive({ address: '成都市青羊区蔡桥街道天府匠芯北区A座6-10', phone: '139 0817 9177', hours: '周一至周日 9:00-18:00' })
const loadContact = async () => {
  try { const res = await request.get('/frontend/contact-section'); if (res) Object.assign(contactData, res) } catch (e) { console.error(e) }
}
const saveContact = async () => {
  saving.contact = true
  try { await request.put('/frontend/contact-section', contactData); ElMessage.success('保存成功') }
  catch (e) { ElMessage.error('保存失败') }
  finally { saving.contact = false }
}

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
  loadHero()
  loadAbout()
  loadBrands()
  loadCta()
  loadContact()
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

/* 首页编辑 blocks-list */
.blocks-list { display: flex; flex-direction: column; gap: 12px; }
.block-card { background: #fff; border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; transition: all 0.3s; }
.block-card.expanded { border-color: #8B7355; box-shadow: 0 4px 12px rgba(139, 115, 85, 0.1); }
.block-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; cursor: pointer; transition: background 0.2s; }
.block-header:hover { background: #faf8f5; }
.block-info { display: flex; align-items: center; gap: 16px; }
.block-order { font-size: 28px; font-weight: 700; color: #C4A77D; opacity: 0.5; line-height: 1; min-width: 40px; }
.block-meta h3 { margin: 0 0 4px; font-size: 16px; font-weight: 600; }
.block-meta p { margin: 0; font-size: 13px; color: #999; }
.block-actions { display: flex; align-items: center; gap: 12px; }
.block-body { padding: 20px; border-top: 1px solid #f0f0f0; background: #fafaf8; }
.edit-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.tip { font-size: 12px; color: #999; }
.hero-preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px; }
.hero-preview-item { border: 1px solid #e4e7ed; border-radius: 6px; overflow: hidden; background: #fff; }
.preview-thumb { aspect-ratio: 16/9; overflow: hidden; background: #f5f5f5; }
.preview-thumb img { width: 100%; height: 100%; object-fit: cover; }
.preview-actions { display: flex; justify-content: center; gap: 4px; padding: 8px; }
.service-edit-item { background: #fff; border: 1px solid #e4e7ed; border-radius: 6px; padding: 16px; margin-bottom: 12px; }
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-weight: 600; color: #8B7355; }
.img-upload-row { display: flex; align-items: center; gap: 16px; }
.img-preview { position: relative; width: 200px; height: 120px; border-radius: 6px; overflow: hidden; border: 1px solid #e4e7ed; }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.img-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; }
.img-preview:hover .img-overlay { opacity: 1; }
.stat-edit-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.brand-grid-edit { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
.brand-logo-item { border: 1px solid #d0d0d0; border-radius: 6px; padding: 12px; background: #999; text-align: center; }
.logo-preview { height: 60px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
.logo-preview img { max-width: 100%; max-height: 60px; object-fit: contain; }
.empty-tip { grid-column: 1 / -1; text-align: center; color: #999; padding: 32px; font-size: 14px; }
.edit-footer { padding-top: 16px; border-top: 1px solid #e4e7ed; display: flex; justify-content: flex-end; gap: 12px; }
.alert-link { color: #8B7355; font-weight: 600; text-decoration: none; }
.alert-link:hover { text-decoration: underline; }
</style>
