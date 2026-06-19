<template>
  <div class="knowledge-manage">
    <div class="km-layout">
      <!-- 左侧分类导航 -->
      <div class="km-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">分类导航</span>
        </div>
        <el-tree
          ref="categoryTreeRef"
          :data="categoryTreeData"
          :props="{ label: 'name', children: 'children' }"
          node-key="id"
          default-expand-all
          highlight-current
          :expand-on-click-node="false"
          @node-click="onCategoryClick"
        >
          <template #default="{ node, data }">
            <div class="cat-tree-node">
              <span class="cat-name">{{ data.name }}</span>
              <el-badge :value="data.base_count || 0" :max="99" class="cat-badge" />
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 右侧内容区 -->
      <div class="km-content">
        <el-tabs v-model="activeTab" class="km-tabs">
          <!-- Tab 1: 知识库管理 -->
          <el-tab-pane label="知识库管理" name="bases">
            <div class="tab-toolbar">
              <div class="toolbar-left">
                <el-button type="primary" @click="openBaseDialog()">
                  <el-icon><Plus /></el-icon> 新建知识库
                </el-button>
              </div>
              <div class="toolbar-right">
                <el-input v-model="baseSearch" placeholder="搜索知识库..." clearable style="width:200px" @clear="loadBases" @keyup.enter="loadBases">
                  <template #prefix><el-icon><Search /></el-icon></template>
                </el-input>
                <el-button @click="loadBases"><el-icon><Refresh /></el-icon></el-button>
              </div>
            </div>

            <div v-loading="baseLoading" class="base-grid">
              <div v-for="base in bases" :key="base.id" class="base-card" :style="{ borderTopColor: base.theme_color || '#409EFF' }">
                <div class="base-card-header">
                  <span class="base-icon">{{ base.icon || '📚' }}</span>
                  <div class="base-card-info">
                    <h3>{{ base.name }}</h3>
                    <el-tag v-if="base.category_name" size="small" :style="{ backgroundColor: base.theme_color || '#409EFF', color: '#fff', border: 'none' }">{{ base.category_name }}</el-tag>
                  </div>
                </div>
                <p class="base-desc">{{ base.description || '暂无描述' }}</p>
                <div class="base-tags" v-if="base.tags">
                  <el-tag v-for="tag in normalizeTags(base.tags)" :key="tag" size="small" effect="plain" style="margin-right:4px">{{ tag }}</el-tag>
                </div>
                <div class="base-stats">
                  <span>📄 {{ base.article_count || 0 }} 文章</span>
                  <span>📂 {{ base.node_count || 0 }} 节点</span>
                </div>
                <div class="base-card-actions">
                  <el-button size="small" type="primary" plain @click="openTree(base)">编辑结构</el-button>
                  <el-button size="small" @click="openBaseDialog(base)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="deleteBase(base)">删除</el-button>
                </div>
              </div>
              <el-empty v-if="!baseLoading && bases.length === 0" description="暂无知识库" />
            </div>
          </el-tab-pane>

          <!-- Tab 2: 文章管理 -->
          <el-tab-pane label="文章管理" name="articles">
            <div class="tab-toolbar">
              <div class="toolbar-left">
                <el-button type="primary" @click="openArticleDialog()">
                  <el-icon><Plus /></el-icon> 新建文章
                </el-button>
              </div>
              <div class="toolbar-right">
                <el-input v-model="articleSearch" placeholder="搜索文章..." clearable style="width:200px" @clear="loadArticles" @keyup.enter="loadArticles">
                  <template #prefix><el-icon><Search /></el-icon></template>
                </el-input>
                <el-select v-model="articleStatusFilter" placeholder="状态" clearable style="width:110px" @change="loadArticles">
                  <el-option label="草稿" value="draft" />
                  <el-option label="已发布" value="published" />
                  <el-option label="待审" value="pending" />
                </el-select>
                <el-button @click="loadArticles"><el-icon><Refresh /></el-icon></el-button>
              </div>
            </div>

            <el-table :data="articles" v-loading="articleLoading" stripe>
              <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
              <el-table-column prop="node_name" label="所属节点" width="150" show-overflow-tooltip />
              <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="view_count" label="浏览" width="80" align="center" />
              <el-table-column prop="like_count" label="点赞" width="80" align="center" />
              <el-table-column prop="updated_at" label="更新时间" width="160" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="openArticleDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="deleteArticle(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              class="mt16"
              background
              layout="total, prev, pager, next"
              :total="articleTotal"
              :page-size="articlePageSize"
              :current-page="articlePage"
              @current-change="loadArticles"
            />
          </el-tab-pane>

          <!-- Tab 3: 分类管理 -->
          <el-tab-pane label="分类管理" name="categories">
            <div class="tab-toolbar">
              <div class="toolbar-left">
                <el-button type="primary" @click="openCategoryDialog()">
                  <el-icon><Plus /></el-icon> 新建分类
                </el-button>
              </div>
              <div class="toolbar-right">
                <el-button @click="loadCategories"><el-icon><Refresh /></el-icon></el-button>
              </div>
            </div>

            <el-table :data="categoryTableData" v-loading="categoryLoading" row-key="id" border default-expand-all
              :tree-props="{ children: 'children' }">
              <el-table-column prop="name" label="分类名称" min-width="200" />
              <el-table-column prop="sort_order" label="排序" width="80" align="center" />
              <el-table-column prop="base_count" label="知识库数" width="100" align="center" />
              <el-table-column prop="created_at" label="创建时间" width="160" />
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="openCategoryDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="deleteCategory(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 知识库编辑弹窗 -->
    <el-dialog v-model="baseDialogVisible" :title="editingBase ? '编辑知识库' : '新建知识库'" width="560px">
      <el-form :model="baseForm" label-width="100px">
        <el-form-item label="知识库名称" required>
          <el-input v-model="baseForm.name" placeholder="如：设记家商学院" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="baseForm.description" type="textarea" :rows="3" placeholder="知识库功能说明" maxlength="500" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="baseForm.category_id" placeholder="选择分类" clearable style="width:100%">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-select v-model="baseForm.icon" placeholder="选择图标" style="width:100%">
            <el-option v-for="icon in iconOptions" :key="icon" :label="icon" :value="icon" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题色">
          <el-color-picker v-model="baseForm.theme_color" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="baseForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="关联模块">
          <el-input v-model="baseForm.related_module" placeholder="如：门店赋能" maxlength="50" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="baseForm.sort_order" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="baseForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="baseDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveBase">保存</el-button>
      </template>
    </el-dialog>

    <!-- 文章编辑弹窗 -->
    <el-dialog v-model="articleDialogVisible" :title="editingArticle ? '编辑文章' : '新建文章'" width="900px"
      :fullscreen="articleFullscreen" @opened="initRichEditor">
      <el-form :model="articleForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="知识库" required>
              <el-select v-model="articleForm.base_id" placeholder="选择知识库" style="width:100%" @change="onArticleBaseChange">
                <el-option v-for="base in allBases" :key="base.id" :label="base.name" :value="base.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="节点" required>
              <el-cascader
                v-model="articleForm.nodePath"
                :options="articleNodeOptions"
                :props="{ value: 'id', label: 'node_name', children: 'children', checkStrictly: true, emitPath: false }"
                placeholder="选择节点"
                style="width:100%"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标题" required>
          <el-input v-model="articleForm.title" placeholder="文章标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="articleForm.summary" type="textarea" :rows="2" placeholder="文章摘要" maxlength="500" />
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="articleForm.cover_image" placeholder="封面图URL" />
        </el-form-item>
        <el-form-item label="正文">
          <div class="rich-editor-wrap">
            <div class="rich-toolbar">
              <el-button-group>
                <el-button size="small" @click="execCmd('bold')" title="加粗"><b>B</b></el-button>
                <el-button size="small" @click="execCmd('italic')" title="斜体"><i>I</i></el-button>
                <el-button size="small" @click="execCmd('underline')" title="下划线"><u>U</u></el-button>
                <el-button size="small" @click="execCmd('strikeThrough')" title="删除线"><s>S</s></el-button>
              </el-button-group>
              <el-button-group>
                <el-button size="small" @click="execCmd('formatBlock', 'H1')" title="标题1">H1</el-button>
                <el-button size="small" @click="execCmd('formatBlock', 'H2')" title="标题2">H2</el-button>
                <el-button size="small" @click="execCmd('formatBlock', 'H3')" title="标题3">H3</el-button>
              </el-button-group>
              <el-button-group>
                <el-button size="small" @click="execCmd('insertOrderedList')" title="有序列表">📊</el-button>
                <el-button size="small" @click="execCmd('insertUnorderedList')" title="无序列表">📝</el-button>
              </el-button-group>
              <el-button-group>
                <el-button size="small" @click="execCmd('formatBlock', 'BLOCKQUOTE')" title="引用">❝</el-button>
                <el-button size="small" @click="insertLink" title="链接">🔗</el-button>
                <el-button size="small" @click="insertImage" title="图片">🖼️</el-button>
                <el-button size="small" @click="execCmd('insertHorizontalRule')" title="分割线">―</el-button>
                <el-button size="small" @click="insertCodeBlock" title="代码块">&lt;/&gt;</el-button>
              </el-button-group>
              <el-button size="small" @click="articleFullscreen = !articleFullscreen" title="全屏">
                {{ articleFullscreen ? '退出全屏' : '全屏' }}
              </el-button>
            </div>
            <div ref="articleEditorRef" class="rich-editor" contenteditable="true"></div>
          </div>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="视频URL">
              <el-input v-model="articleForm.video_url" placeholder="视频链接" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签">
              <el-input v-model="articleForm.tags" placeholder="多个标签用逗号分隔" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-radio-group v-model="articleForm.status">
            <el-radio value="draft">草稿</el-radio>
            <el-radio value="published">已发布</el-radio>
            <el-radio value="pending">待审</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="articleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveArticle">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分类编辑弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="editingCategory ? '编辑分类' : '新建分类'" width="460px">
      <el-form :model="categoryForm" label-width="90px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" placeholder="如：前端营销" maxlength="50" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="categoryForm.parent_id" placeholder="无（顶级分类）" clearable style="width:100%">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 树状结构编辑器 -->
    <el-drawer v-model="treeVisible" :title="`编辑结构：${currentBase?.name}`" size="720px">
      <div class="tree-editor">
        <div class="tree-toolbar">
          <el-button type="primary" plain size="small" @click="openNodeDialog(0)">
            <el-icon><Plus /></el-icon> 新增一级标题
          </el-button>
          <el-button size="small" @click="loadTree(currentBase.id)"><el-icon><Refresh /></el-icon> 刷新</el-button>
        </div>

        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="{ label: 'node_name', children: 'children' }"
          node-key="id"
          default-expand-all
          highlight-current
          :expand-on-click-node="false"
          class="knowledge-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node-wrap">
              <div class="tree-node-left">
                <el-tag v-if="data.level === 1" type="primary" size="small">一级</el-tag>
                <el-tag v-else-if="data.level === 2" type="success" size="small">二级</el-tag>
                <el-tag v-else type="warning" size="small">三级</el-tag>
                <span class="node-name">{{ data.node_name }}</span>
                <span v-if="data.summary" class="node-summary" :title="data.summary">{{ data.summary }}</span>
                <el-tag v-if="data.status === 0" type="info" size="small">隐藏</el-tag>
                <span v-if="data.article_count" class="node-articles">📄 {{ data.article_count }}篇</span>
                <span v-if="data.level < 3" class="node-views">{{ data.view_count || 0 }}次浏览</span>
              </div>
              <div class="tree-node-actions">
                <el-button v-if="data.level < 3" size="small" type="primary" plain
                  @click.stop="openNodeDialog(data.id, data.level + 1)">+子节点</el-button>
                <el-button size="small" @click.stop="openContentEditor(data)" type="warning" plain>
                  <el-icon><Document /></el-icon> 文案
                </el-button>
                <el-button size="small" @click.stop="openNodeDialog(data.parent_id, data.level, data)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" type="danger" plain @click.stop="deleteNode(data)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </el-drawer>

    <!-- 节点编辑弹窗 -->
    <el-dialog v-model="nodeDialogVisible" :title="editingNode ? '编辑节点' : '新增节点'" width="520px">
      <el-form :model="nodeForm" label-width="100px">
        <el-form-item label="节点名称" required>
          <el-input v-model="nodeForm.node_name" placeholder="如：第一章 市场调查" maxlength="200" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="nodeForm.summary" type="textarea" :rows="2" placeholder="节点摘要" maxlength="300" />
        </el-form-item>
        <el-form-item label="封面图URL">
          <el-input v-model="nodeForm.cover_image" placeholder="节点封面图链接" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="nodeForm.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="nodeForm.status">
            <el-radio :value="1">展示</el-radio>
            <el-radio :value="0">隐藏</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="视频URL">
          <el-input v-model="nodeForm.video_url" placeholder="视频号/抖音/B站链接" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveNode">保存</el-button>
      </template>
    </el-dialog>

    <!-- 文案编辑器弹窗 -->
    <el-dialog v-model="contentDialogVisible" :title="`编辑文案：${currentNode?.node_name}`" width="900px"
      :fullscreen="contentFullscreen" @opened="initContentEditor">
      <div class="content-editor-area">
        <div class="editor-toolbar">
          <el-button-group>
            <el-button size="small" @click="execContentCmd('bold')"><b>B</b></el-button>
            <el-button size="small" @click="execContentCmd('italic')"><i>I</i></el-button>
            <el-button size="small" @click="execContentCmd('underline')"><u>U</u></el-button>
            <el-button size="small" @click="execContentCmd('strikeThrough')"><s>S</s></el-button>
          </el-button-group>
          <el-button-group>
            <el-button size="small" @click="execContentCmd('formatBlock', 'H1')">H1</el-button>
            <el-button size="small" @click="execContentCmd('formatBlock', 'H2')">H2</el-button>
            <el-button size="small" @click="execContentCmd('formatBlock', 'H3')">H3</el-button>
          </el-button-group>
          <el-button-group>
            <el-button size="small" @click="execContentCmd('insertOrderedList')">📊</el-button>
            <el-button size="small" @click="execContentCmd('insertUnorderedList')">📝</el-button>
          </el-button-group>
          <el-button-group>
            <el-button size="small" @click="execContentCmd('formatBlock', 'BLOCKQUOTE')">❝</el-button>
            <el-button size="small" @click="insertContentLink">🔗</el-button>
            <el-button size="small" @click="insertContentImage">🖼️</el-button>
            <el-button size="small" @click="execContentCmd('insertHorizontalRule')">―</el-button>
            <el-button size="small" @click="insertContentCodeBlock">&lt;/&gt;</el-button>
          </el-button-group>
          <el-button size="small" @click="contentFullscreen = !contentFullscreen">
            {{ contentFullscreen ? '退出全屏' : '全屏' }}
          </el-button>
        </div>
        <div ref="contentEditorRef" class="rich-editor" contenteditable="true"></div>
      </div>
      <template #footer>
        <el-button @click="contentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveContent">保存文案</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete, Document, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

// ==================== 布局 ====================
const activeTab = ref('bases')
const selectedCategory = ref(null)

// ==================== 分类 ====================
const categoryTreeData = ref([])
const categoryTableData = ref([])
const flatCategories = ref([])
const categoryLoading = ref(false)
const categoryTreeRef = ref(null)

const categoryDialogVisible = ref(false)
const editingCategory = ref(null)
const categoryForm = reactive({
  name: '',
  parent_id: null,
  sort_order: 0,
})

// ==================== 知识库 ====================
const bases = ref([])
const allBases = ref([])
const baseLoading = ref(false)
const baseSearch = ref('')
const baseDialogVisible = ref(false)
const editingBase = ref(null)
const baseForm = reactive({
  name: '',
  description: '',
  category_id: null,
  icon: '📚',
  theme_color: '#409EFF',
  tags: '',
  related_module: '',
  sort_order: 0,
  status: 1,
})

const iconOptions = ['📚', '📖', '🎓', '🏗️', '🎨', '💡', '🔧', '📋', '🎯', '⭐', '🚀', '💼']

// ==================== 文章 ====================
const articles = ref([])
const articleLoading = ref(false)
const articleTotal = ref(0)
const articlePage = ref(1)
const articlePageSize = ref(20)
const articleSearch = ref('')
const articleStatusFilter = ref('')
const articleDialogVisible = ref(false)
const editingArticle = ref(null)
const articleFullscreen = ref(false)
const articleEditorRef = ref(null)
const articleNodeOptions = ref([])
const articleForm = reactive({
  base_id: null,
  node_id: null,
  nodePath: null,
  title: '',
  summary: '',
  cover_image: '',
  content: '',
  video_url: '',
  tags: '',
  status: 'draft',
})

// ==================== 树状结构 ====================
const treeVisible = ref(false)
const currentBase = ref(null)
const treeData = ref([])
const treeRef = ref(null)

const nodeDialogVisible = ref(false)
const editingNode = ref(null)
const nodeForm = reactive({
  node_name: '',
  summary: '',
  cover_image: '',
  sort_order: 0,
  status: 1,
  video_url: '',
})
const parentNodeId = ref(0)

// ==================== 文案编辑 ====================
const contentDialogVisible = ref(false)
const contentFullscreen = ref(false)
const currentNode = ref(null)
const contentEditorRef = ref(null)
const contentForm = reactive({ content: '' })

const saving = ref(false)

// ==================== 初始化 ====================
onMounted(() => {
  loadCategories()
  loadBases()
  loadAllBases()
})

// ==================== 分类管理 ====================
function loadCategories() {
  categoryLoading.value = true
  request.get('/knowledge/categories').then(res => {
    if (res) {
      categoryTreeData.value = res || []
      categoryTableData.value = res || []
      flattenCategories(res || [])
    }
  }).finally(() => { categoryLoading.value = false })
}

function flattenCategories(list) {
  const result = []
  function walk(items) {
    for (const item of items) {
      result.push(item)
      if (item.children && item.children.length) walk(item.children)
    }
  }
  walk(list)
  flatCategories.value = result
}

function onCategoryClick(data) {
  selectedCategory.value = data.id
  loadBases()
}

function openCategoryDialog(cat = null) {
  editingCategory.value = cat
  if (cat) {
    Object.assign(categoryForm, {
      name: cat.name,
      parent_id: cat.parent_id || null,
      sort_order: cat.sort_order || 0,
    })
  } else {
    Object.assign(categoryForm, { name: '', parent_id: null, sort_order: 0 })
  }
  categoryDialogVisible.value = true
}

function saveCategory() {
  if (!categoryForm.name.trim()) {
    ElMessage.warning('分类名称不能为空')
    return
  }
  saving.value = true
  const payload = { ...categoryForm }
  const req = editingCategory.value
    ? request.put(`/knowledge/categories/${editingCategory.value.id}`, payload)
    : request.post('/knowledge/categories', payload)
  req.then(res => {
    if (res && res.id) {
      ElMessage.success('保存成功')
      categoryDialogVisible.value = false
      loadCategories()
    }
  }).finally(() => { saving.value = false })
}

function deleteCategory(cat) {
  ElMessageBox.confirm(`确定删除分类「${cat.name}」？`, '确认删除', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
  }).then(() => {
    request.delete(`/knowledge/categories/${cat.id}`).then(() => {
      ElMessage.success('已删除')
      loadCategories()
    })
  }).catch(() => {})
}

// ==================== 知识库管理 ====================
// Normalize tags to array (backend may return array or string)
function normalizeTags(tags) {
  if (Array.isArray(tags)) return tags.filter(Boolean)
  if (typeof tags === 'string') return tags.split(',').map(t => t.trim()).filter(Boolean)
  return []
}

function loadBases() {
  baseLoading.value = true
  const params = {}
  if (selectedCategory.value) params.category = selectedCategory.value
  if (baseSearch.value) params.search = baseSearch.value
  request.get('/knowledge/bases', { params }).then(res => {
    if (res && res.items) {
      bases.value = res.items
    } else if (Array.isArray(res)) {
      bases.value = res
    } else {
      bases.value = []
    }
  }).finally(() => { baseLoading.value = false })
}

function loadAllBases() {
  request.get('/knowledge/bases').then(res => {
    if (res && res.items) allBases.value = res.items
    else if (Array.isArray(res)) allBases.value = res
    else allBases.value = []
  })
}

function openBaseDialog(base = null) {
  editingBase.value = base
  if (base) {
    Object.assign(baseForm, {
      name: base.name,
      description: base.description || '',
      category_id: base.category_id || null,
      icon: base.icon || '📚',
      theme_color: base.theme_color || '#409EFF',
      tags: Array.isArray(base.tags) ? base.tags.join(',') : (base.tags || ''),
      related_module: base.related_module || '',
      sort_order: base.sort_order || 0,
      status: base.status,
    })
  } else {
    Object.assign(baseForm, {
      name: '', description: '', category_id: selectedCategory.value || null,
      icon: '📚', theme_color: '#409EFF', tags: '', related_module: '', sort_order: 0, status: 1
    })
  }
  baseDialogVisible.value = true
}

function saveBase() {
  if (!baseForm.name.trim()) {
    ElMessage.warning('名称不能为空')
    return
  }
  saving.value = true
  const payload = { ...baseForm }
  // tags: string → array for backend
  if (typeof payload.tags === 'string') {
    payload.tags = payload.tags.split(',').map(t => t.trim()).filter(Boolean)
  }
  const req = editingBase.value
    ? request.put(`/knowledge/bases/${editingBase.value.id}`, payload)
    : request.post('/knowledge/bases', payload)
  req.then(res => {
    if (res && res.id) {
      ElMessage.success('保存成功')
      baseDialogVisible.value = false
      loadBases()
      loadAllBases()
      loadCategories()
    } else {
      ElMessage.error('保存失败')
    }
  }).finally(() => { saving.value = false })
}

function deleteBase(base) {
  ElMessageBox.confirm(`确定删除知识库「${base.name}」？将同时删除所有节点和文章！`, '确认删除', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
  }).then(() => {
    request.delete(`/knowledge/bases/${base.id}`).then(() => {
      ElMessage.success('已删除')
      loadBases()
      loadAllBases()
      loadCategories()
    })
  }).catch(() => {})
}

// ==================== 文章管理 ====================
function loadArticles(p = 1) {
  articlePage.value = p
  articleLoading.value = true
  const params = { page: p, pageSize: articlePageSize.value }
  if (articleSearch.value) params.search = articleSearch.value
  if (articleStatusFilter.value) params.status = articleStatusFilter.value
  request.get('/knowledge/articles', { params }).then(res => {
    if (res && res.items) {
      articles.value = res.items
      articleTotal.value = res.total || 0
    } else if (Array.isArray(res)) {
      articles.value = res
      articleTotal.value = res.length
    } else {
      articles.value = []
      articleTotal.value = 0
    }
  }).finally(() => { articleLoading.value = false })
}

function statusLabel(status) {
  const map = { draft: '草稿', published: '已发布', pending: '待审' }
  return map[status] || status
}

function statusTagType(status) {
  const map = { draft: 'info', published: 'success', pending: 'warning' }
  return map[status] || 'info'
}

async function onArticleBaseChange(baseId) {
  articleForm.node_id = null
  articleForm.nodePath = null
  if (!baseId) {
    articleNodeOptions.value = []
    return
  }
  try {
    const res = await request.get(`/knowledge/bases/${baseId}/tree`)
    articleNodeOptions.value = res || []
  } catch {
    articleNodeOptions.value = []
  }
}

function openArticleDialog(article = null) {
  editingArticle.value = article
  if (article) {
    Object.assign(articleForm, {
      base_id: article.base_id || null,
      node_id: article.node_id || null,
      nodePath: article.node_id || null,
      title: article.title || '',
      summary: article.summary || '',
      cover_image: article.cover_image || '',
      content: article.content || '',
      video_url: article.video_url || '',
      tags: Array.isArray(article.tags) ? article.tags.join(',') : (article.tags || ''),
      status: article.status || 'draft',
    })
    if (article.base_id) onArticleBaseChange(article.base_id)
  } else {
    Object.assign(articleForm, {
      base_id: null, node_id: null, nodePath: null,
      title: '', summary: '', cover_image: '', content: '',
      video_url: '', tags: '', status: 'draft',
    })
    articleNodeOptions.value = []
  }
  articleDialogVisible.value = true
}

function initRichEditor() {
  nextTick(() => {
    if (articleEditorRef.value) {
      articleEditorRef.value.innerHTML = articleForm.content || ''
    }
  })
}

function execCmd(cmd, val = null) {
  document.execCommand(cmd, false, val)
  if (articleEditorRef.value) articleForm.content = articleEditorRef.value.innerHTML
}

function insertLink() {
  ElMessageBox.prompt('请输入链接URL', '插入链接', {
    confirmButtonText: '插入',
    cancelButtonText: '取消',
  }).then(({ value }) => {
    if (value) {
      const text = window.getSelection().toString() || value
      document.execCommand('insertHTML', false, `<a href="${value}" target="_blank">${text}</a>`)
      if (articleEditorRef.value) articleForm.content = articleEditorRef.value.innerHTML
    }
  }).catch(() => {})
}

function insertImage() {
  ElMessageBox.prompt('请输入图片URL', '插入图片', {
    confirmButtonText: '插入',
    cancelButtonText: '取消',
  }).then(({ value }) => {
    if (value) {
      document.execCommand('insertHTML', false, `<img src="${value}" style="max-width:100%;border-radius:4px" />`)
      if (articleEditorRef.value) articleForm.content = articleEditorRef.value.innerHTML
    }
  }).catch(() => {})
}

function insertCodeBlock() {
  document.execCommand('insertHTML', false, '<pre><code>// code here\n</code></pre><p></p>')
  if (articleEditorRef.value) articleForm.content = articleEditorRef.value.innerHTML
}

function saveArticle() {
  if (!articleForm.title.trim()) {
    ElMessage.warning('标题不能为空')
    return
  }
  if (!articleForm.base_id) {
    ElMessage.warning('请选择知识库')
    return
  }
  if (articleEditorRef.value) articleForm.content = articleEditorRef.value.innerHTML
  articleForm.node_id = articleForm.nodePath || articleForm.node_id
  if (!articleForm.node_id) {
    ElMessage.warning('请选择节点')
    return
  }
  saving.value = true
  const payload = { ...articleForm }
  delete payload.nodePath
  // tags: string → array for backend
  if (typeof payload.tags === 'string') {
    payload.tags = payload.tags.split(',').map(t => t.trim()).filter(Boolean)
  }
  const req = editingArticle.value
    ? request.put(`/knowledge/articles/${editingArticle.value.id}`, payload)
    : request.post('/knowledge/articles', payload)
  req.then(res => {
    if (res && res.id) {
      ElMessage.success('保存成功')
      articleDialogVisible.value = false
      loadArticles(articlePage.value)
    } else {
      ElMessage.error('保存失败')
    }
  }).finally(() => { saving.value = false })
}

function deleteArticle(article) {
  ElMessageBox.confirm(`确定删除文章「${article.title}」？`, '确认删除', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
  }).then(() => {
    request.delete(`/knowledge/articles/${article.id}`).then(() => {
      ElMessage.success('已删除')
      loadArticles(articlePage.value)
    })
  }).catch(() => {})
}

// ==================== 树状结构 ====================
function openTree(base) {
  currentBase.value = base
  treeVisible.value = true
  loadTree(base.id)
}

function loadTree(baseId) {
  request.get(`/knowledge/bases/${baseId}/tree`).then(res => {
    if (res) treeData.value = res
  })
}

function openNodeDialog(parentId, level = 1, node = null) {
  parentNodeId.value = parentId
  editingNode.value = node
  if (node) {
    Object.assign(nodeForm, {
      node_name: node.node_name,
      summary: node.summary || '',
      cover_image: node.cover_image || '',
      sort_order: node.sort_order || 0,
      status: node.status,
      video_url: node.video_url || '',
    })
  } else {
    Object.assign(nodeForm, {
      node_name: '', summary: '', cover_image: '',
      sort_order: 0, status: 1, video_url: ''
    })
  }
  nodeDialogVisible.value = true
}

function saveNode() {
  if (!nodeForm.node_name.trim()) {
    ElMessage.warning('节点名称不能为空')
    return
  }
  saving.value = true
  const payload = {
    base_id: currentBase.value.id,
    parent_id: parentNodeId.value,
    ...nodeForm,
  }
  const req = editingNode.value
    ? request.put(`/knowledge/nodes/${editingNode.value.id}`, payload)
    : request.post('/knowledge/nodes', payload)
  req.then(res => {
    if (res && res.id) {
      ElMessage.success('保存成功')
      nodeDialogVisible.value = false
      loadTree(currentBase.value.id)
    }
  }).finally(() => { saving.value = false })
}

function deleteNode(node) {
  ElMessageBox.confirm(`确定删除「${node.node_name}」及其所有子节点？`, '确认删除', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
  }).then(() => {
    request.delete(`/knowledge/nodes/${node.id}`).then(() => {
      ElMessage.success('已删除')
      loadTree(currentBase.value.id)
    })
  }).catch(() => {})
}

// ==================== 文案编辑 ====================
function openContentEditor(node) {
  currentNode.value = node
  contentForm.content = node.content || ''
  contentFullscreen.value = false
  contentDialogVisible.value = true
}

function initContentEditor() {
  nextTick(() => {
    if (contentEditorRef.value) {
      contentEditorRef.value.innerHTML = contentForm.content || ''
    }
  })
}

function execContentCmd(cmd, val = null) {
  document.execCommand(cmd, false, val)
  if (contentEditorRef.value) contentForm.content = contentEditorRef.value.innerHTML
}

function insertContentLink() {
  ElMessageBox.prompt('请输入链接URL', '插入链接', {
    confirmButtonText: '插入',
    cancelButtonText: '取消',
  }).then(({ value }) => {
    if (value) {
      const text = window.getSelection().toString() || value
      document.execCommand('insertHTML', false, `<a href="${value}" target="_blank">${text}</a>`)
      if (contentEditorRef.value) contentForm.content = contentEditorRef.value.innerHTML
    }
  }).catch(() => {})
}

function insertContentImage() {
  ElMessageBox.prompt('请输入图片URL', '插入图片', {
    confirmButtonText: '插入',
    cancelButtonText: '取消',
  }).then(({ value }) => {
    if (value) {
      document.execCommand('insertHTML', false, `<img src="${value}" style="max-width:100%;border-radius:4px" />`)
      if (contentEditorRef.value) contentForm.content = contentEditorRef.value.innerHTML
    }
  }).catch(() => {})
}

function insertContentCodeBlock() {
  document.execCommand('insertHTML', false, '<pre><code>// code here\n</code></pre><p></p>')
  if (contentEditorRef.value) contentForm.content = contentEditorRef.value.innerHTML
}

function saveContent() {
  saving.value = true
  if (contentEditorRef.value) contentForm.content = contentEditorRef.value.innerHTML
  request.put(`/knowledge/nodes/${currentNode.value.id}/content`, {
    content: contentForm.content
  }).then(res => {
    if (res) {
      ElMessage.success('文案保存成功')
      contentDialogVisible.value = false
      loadTree(currentBase.value.id)
    }
  }).finally(() => { saving.value = false })
}

// Watch tab change to load data
import { watch } from 'vue'
watch(activeTab, (newTab) => {
  if (newTab === 'articles' && articles.value.length === 0) loadArticles()
  if (newTab === 'categories') loadCategories()
})
</script>

<style scoped>
.knowledge-manage {
  padding: 0;
}
.km-layout {
  display: flex;
  gap: 16px;
  height: calc(100vh - 120px);
}

/* 左侧分类树 */
.km-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
}
.sidebar-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.cat-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
.cat-name {
  font-size: 13px;
}
.cat-badge {
  margin-left: 8px;
}

/* 右侧内容 */
.km-content {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #ebeef5;
}
.km-tabs {
  height: 100%;
}

/* 工具栏 */
.tab-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.toolbar-left, .toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}
.mt16 {
  margin-top: 16px;
}

/* 知识库卡片 */
.base-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.base-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-top: 3px solid #409EFF;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.3s;
}
.base-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
.base-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.base-icon {
  font-size: 32px;
}
.base-card-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #303133;
}
.base-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.base-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.base-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  padding: 8px 0;
  border-top: 1px solid #f5f5f5;
}
.base-card-actions {
  display: flex;
  gap: 4px;
}

/* 富文本编辑器 */
.rich-editor-wrap {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}
.rich-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  align-items: center;
}
.rich-editor {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  outline: none;
  line-height: 1.8;
  font-size: 14px;
  color: #303133;
}
.rich-editor:focus {
  outline: none;
}
.rich-editor :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}
.rich-editor :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}
.rich-editor :deep(blockquote) {
  border-left: 4px solid #dcdfe6;
  padding-left: 16px;
  margin: 8px 0;
  color: #606266;
}
.rich-editor :deep(a) {
  color: #409EFF;
}

/* 树编辑器 */
.tree-editor {
  padding: 0 4px;
}
.tree-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}
.knowledge-tree {
  background: transparent;
}
.tree-node-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}
.tree-node-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  flex-wrap: wrap;
}
.node-name {
  font-size: 14px;
  color: #262626;
}
.node-summary {
  font-size: 12px;
  color: #909399;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.node-articles {
  font-size: 12px;
  color: #409EFF;
}
.node-views {
  font-size: 12px;
  color: #8c8c8c;
}
.tree-node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
:deep(.el-tree-node__content:hover) .tree-node-actions {
  opacity: 1;
}

/* 文案编辑器 */
.content-editor-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .km-layout {
    flex-direction: column;
    height: auto;
  }
  .km-sidebar {
    width: 100%;
  }
  .km-content {
    overflow-y: visible;
  }
}
</style>
