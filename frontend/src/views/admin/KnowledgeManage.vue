<template>
  <div class="knowledge-manage">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="openBaseDialog()">
          <el-icon><Plus /></el-icon> 新建知识库
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:120px" @change="loadBases()">
          <el-option label="全部" :value="null" />
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
        <el-button @click="loadBases()"><el-icon><Refresh /></el-icon></el-button>
      </div>
    </div>

    <!-- 知识库列表 -->
    <el-table :data="bases" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="知识库名称" min-width="200">
        <template #default="{ row }">
          <strong>{{ row.name }}</strong>
          <el-tag v-if="row.status === 1" type="success" size="small" style="margin-left:8px">启用</el-tag>
          <el-tag v-else type="info" size="small" style="margin-left:8px">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="node_count" label="节点数" width="80" align="center" />
      <el-table-column prop="sort_order" label="排序" width="70" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openTree(row)">编辑结构</el-button>
          <el-button size="small" @click="openBaseDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" plain @click="deleteBase(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      class="mt16"
      background
      layout="total, prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="loadBases"
    />

    <!-- 知识库编辑弹窗 -->
    <el-dialog v-model="baseDialogVisible" :title="editingBase ? '编辑知识库' : '新建知识库'" width="520px">
      <el-form :model="baseForm" label-width="100px">
        <el-form-item label="知识库名称" required>
          <el-input v-model="baseForm.name" placeholder="如：设记家商学院" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="baseForm.description" type="textarea" :rows="3" placeholder="知识库功能说明" maxlength="500" />
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

    <!-- 树状结构编辑器 -->
    <el-drawer v-model="treeVisible" :title="`编辑结构：${currentBase?.name}`" size="680px"
      :before-close="treeVisible = false">
      <div class="tree-editor">
        <!-- 添加根节点按钮 -->
        <div class="tree-toolbar">
          <el-button type="primary" plain size="small" @click="openNodeDialog(0)">
            <el-icon><Plus /></el-icon> 新增一级标题
          </el-button>
        </div>

        <!-- 树状结构 -->
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
                <span class="node-name">{{ node.label }}</span>
                <el-tag v-if="data.status === 0" type="info" size="small">隐藏</el-tag>
                <span class="node-views" v-if="data.level < 3">
                  <el-link type="info" :underline="false" size="small">
                    {{ data.view_count || 0 }}次浏览
                  </el-link>
                </span>
              </div>
              <div class="tree-node-actions">
                <!-- 添加子节点（三层以内） -->
                <el-button v-if="data.level < 3" size="small" type="primary" plain
                  @click.stop="openNodeDialog(data.id, data.level + 1)">+子节点</el-button>
                <!-- 文案编辑（四层内容） -->
                <el-button size="small" @click.stop="openContentEditor(data)" type="warning" plain>
                  <el-icon><Document /></el-icon> 文案
                </el-button>
                <!-- 编辑节点 -->
                <el-button size="small" @click.stop="openNodeDialog(data.parent_id, data.level, data)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <!-- 删除 -->
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
    <el-dialog v-model="nodeDialogVisible" :title="editingNode ? '编辑节点' : '新增节点'" width="500px">
      <el-form :model="nodeForm" label-width="100px">
        <el-form-item label="节点名称" required>
          <el-input v-model="nodeForm.node_name" placeholder="如：第一章 市场调查" maxlength="200" />
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
      :fullscreen="contentFullscreen">
      <div class="content-editor-area">
        <div class="editor-toolbar">
          <el-button size="small" @click="contentFullscreen = !contentFullscreen">
            {{ contentFullscreen ? '退出全屏' : '全屏编辑' }}
          </el-button>
        </div>
        <!-- 富文本编辑器（使用 contenteditable + execCommand 简化实现） -->
        <div class="rich-editor" ref="richEditorRef" contenteditable="true"
          v-html="contentForm.content"
          @input="contentForm.content = richEditorRef.innerHTML"
        />
      </div>
      <template #footer>
        <el-button @click="contentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveContent">保存文案</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete, Document } from '@element-plus/icons-vue'
import request from '@/utils/request'

const bases = ref([])
const loading = ref(false)
const saving = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStatus = ref(null)

// 知识库弹窗
const baseDialogVisible = ref(false)
const editingBase = ref(null)
const baseForm = reactive({
  name: '',
  description: '',
  related_module: '',
  sort_order: 0,
  status: 1,
})

// 树状结构
const treeVisible = ref(false)
const currentBase = ref(null)
const treeData = ref([])
const treeRef = ref(null)

// 节点弹窗
const nodeDialogVisible = ref(false)
const editingNode = ref(null)
const nodeForm = reactive({
  node_name: '',
  sort_order: 0,
  status: 1,
  video_url: '',
})
const parentNodeId = ref(0)
const parentLevel = ref(1)

// 文案弹窗
const contentDialogVisible = ref(false)
const contentFullscreen = ref(false)
const currentNode = ref(null)
const contentForm = reactive({ content: '' })
const richEditorRef = ref(null)

onMounted(() => {
  loadBases()
})

function loadBases(p = 1) {
  page.value = p
  loading.value = true
  const params = { page: p, pageSize: pageSize.value }
  if (filterStatus.value !== null) params.status = filterStatus.value
  request.get('/knowledge/bases', { params }).then(res => {
    if (res.code === 200) {
      bases.value = res.data.items
      total.value = res.data.total
    }
  }).finally(() => { loading.value = false })
}

function openBaseDialog(base = null) {
  editingBase.value = base
  if (base) {
    Object.assign(baseForm, {
      name: base.name,
      description: base.description || '',
      related_module: base.related_module || '',
      sort_order: base.sort_order || 0,
      status: base.status,
    })
  } else {
    Object.assign(baseForm, { name: '', description: '', related_module: '', sort_order: 0, status: 1 })
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
  const req = editingBase.value
    ? request.put(`/knowledge/bases/${editingBase.value.id}`, payload)
    : request.post('/knowledge/bases', payload)
  req.then(res => {
    if (res.code === 200) {
      ElMessage.success('保存成功')
      baseDialogVisible.value = false
      loadBases(page.value)
    }
  }).finally(() => { saving.value = false })
}

function deleteBase(base) {
  ElMessageBox.confirm(`确定删除知识库「${base.name}」？将同时删除所有节点！`, '确认删除', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
  }).then(() => {
    request.delete(`/knowledge/bases/${base.id}`).then(res => {
      if (res.code === 200) {
        ElMessage.success('已删除')
        loadBases(page.value)
      }
    })
  }).catch(() => {})
}

function openTree(base) {
  currentBase.value = base
  treeVisible.value = true
  loadTree(base.id)
}

function loadTree(baseId) {
  request.get(`/knowledge/bases/${baseId}/tree`).then(res => {
    if (res.code === 200) treeData.value = res.data
  })
}

function openNodeDialog(parentId, level = 1, node = null) {
  parentNodeId.value = parentId
  editingNode.value = node
  if (node) {
    Object.assign(nodeForm, {
      node_name: node.node_name,
      sort_order: node.sort_order || 0,
      status: node.status,
      video_url: node.video_url || '',
    })
  } else {
    Object.assign(nodeForm, { node_name: '', sort_order: 0, status: 1, video_url: '' })
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
    node_name: nodeForm.node_name,
    sort_order: nodeForm.sort_order,
    status: nodeForm.status,
    video_url: nodeForm.video_url,
  }
  const req = editingNode.value
    ? request.put(`/knowledge/nodes/${editingNode.value.id}`, payload)
    : request.post('/knowledge/nodes', payload)
  req.then(res => {
    if (res.code === 200) {
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
    request.delete(`/knowledge/nodes/${node.id}`).then(res => {
      if (res.code === 200) {
        ElMessage.success('已删除')
        loadTree(currentBase.value.id)
      }
    })
  }).catch(() => {})
}

function openContentEditor(node) {
  currentNode.value = node
  contentForm.content = node.content || ''
  contentFullscreen.value = false
  contentDialogVisible.value = true
}

function saveContent() {
  saving.value = true
  request.put(`/knowledge/nodes/${currentNode.value.id}/content`, {
    content: contentForm.content
  }).then(res => {
    if (res.code === 200) {
      ElMessage.success('文案保存成功')
      contentDialogVisible.value = false
      loadTree(currentBase.value.id)
    }
  }).finally(() => { saving.value = false })
}
</script>

<style scoped>
.knowledge-manage {
  padding: 0 4px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}
.mt16 {
  margin-top: 16px;
}
.tree-editor {
  padding: 0 4px;
}
.tree-toolbar {
  margin-bottom: 16px;
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
}
.node-name {
  font-size: 14px;
  color: #262626;
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
.content-editor-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.editor-toolbar {
  display: flex;
  gap: 4px;
}
.rich-editor {
  min-height: 420px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  outline: none;
  line-height: 1.8;
  font-size: 15px;
  color: #262626;
  overflow-y: auto;
  max-height: 60vh;
}
.rich-editor:focus {
  border-color: #409EFF;
}
.rich-editor :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}
</style>
