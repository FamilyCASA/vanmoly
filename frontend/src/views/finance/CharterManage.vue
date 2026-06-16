<template>
  <div class="charter-manage">
    <div class="page-header">
      <h2>企业章程管理</h2>
      <el-button type="primary" @click="saveCharter" :loading="saving" :icon="Check">
        {{ charter.id ? '保存修改' : '创建章程' }}
      </el-button>
    </div>

    <el-card shadow="never" v-loading="loading">
      <!-- 章程元信息 -->
      <div class="charter-meta" v-if="charter.id">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="版本号">
            <el-input v-model="charter.version" size="small" style="width: 100px" />
          </el-descriptions-item>
          <el-descriptions-item label="生效日期">
            <el-date-picker v-model="charter.effective_date" type="date" value-format="YYYY-MM-DD" size="small" style="width: 160px" />
          </el-descriptions-item>
          <el-descriptions-item label="最后更新">
            {{ charter.updated_at ? charter.updated_at.slice(0, 16).replace('T', ' ') : '—' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 章程标题 -->
      <div class="charter-title-area">
        <el-input
          v-model="charter.title"
          placeholder="请输入章程标题"
          class="charter-title-input"
          size="large"
        />
      </div>

      <!-- 章程内容编辑 -->
      <div class="charter-editor">
        <div class="editor-toolbar">
          <span class="toolbar-label">章程正文</span>
          <el-button-group>
            <el-button size="small" @click="insertTemplate('chapter')" title="插入章节标题">插入章节</el-button>
            <el-button size="small" @click="insertTemplate('article')" title="插入条款">插入条款</el-button>
            <el-button size="small" @click="insertTemplate('list')" title="插入列表项">插入列表</el-button>
          </el-button-group>
        </div>
        <el-input
          v-model="charter.content"
          type="textarea"
          :rows="20"
          placeholder="请输入章程正文内容&#10;&#10;支持格式：&#10;第X章 章节标题&#10;第X条 条款内容&#10;（X） 列表项"
          resize="vertical"
          class="charter-textarea"
        />
      </div>

      <!-- 预览区 -->
      <div class="charter-preview" v-if="charter.content">
        <el-divider content-position="left">
          <el-button text type="primary" @click="showPreview = !showPreview">
            {{ showPreview ? '收起预览' : '展开预览' }}
          </el-button>
        </el-divider>
        <div v-show="showPreview" class="preview-content" v-html="renderedContent"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import financeAPI from '@/api/finance'

const loading = ref(false)
const saving = ref(false)
const showPreview = ref(false)

const charter = ref({
  id: null,
  title: '企业章程',
  content: '',
  version: '1.0',
  effective_date: '',
  updated_at: null
})

// Simple text → HTML rendering
const renderedContent = computed(() => {
  if (!charter.value.content) return ''
  return charter.value.content
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^(第[一二三四五六七八九十百]+章\s+.+)$/gm, '<h3 class="chapter-title">$1</h3>')
    .replace(/^(第[\d]+条\s+)/gm, '<strong>$1</strong>')
    .replace(/^[（(][\d]+[）)]/gm, (m) => `<span class="list-item">${m}</span>`)
    .replace(/\n/g, '<br/>')
})

const loadData = async () => {
  loading.value = true
  try {
    const d = await financeAPI.getCharter()
    if (d) {
      charter.value = { ...charter.value, ...d }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const saveCharter = async () => {
  if (!charter.value.title.trim()) {
    ElMessage.warning('请输入章程标题')
    return
  }
  if (!charter.value.content.trim()) {
    ElMessage.warning('请输入章程内容')
    return
  }

  saving.value = true
  try {
    const d = await financeAPI.saveCharter({
      title: charter.value.title,
      content: charter.value.content,
      version: charter.value.version,
      effective_date: charter.value.effective_date || null
    })
    charter.value = { ...charter.value, ...d }
    ElMessage.success('章程保存成功')
  } catch (e) {
    console.error(e)
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const insertTemplate = (type) => {
  const templates = {
    chapter: '\n\n第一章 章节标题\n',
    article: '\n第一条 条款内容\n',
    list: '\n（1）列表项内容\n'
  }
  charter.value.content += templates[type] || ''
}

onMounted(loadData)
</script>

<style scoped>
.charter-manage { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; font-size: 20px; }

.charter-meta {
  margin-bottom: 16px;
}

.charter-title-area {
  margin-bottom: 16px;
}
.charter-title-input :deep(.el-input__inner) {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.charter-editor {
  margin-bottom: 16px;
}
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.toolbar-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}
.charter-textarea :deep(.el-textarea__inner) {
  font-family: 'Songti SC', 'SimSun', serif;
  font-size: 14px;
  line-height: 1.8;
}

.charter-preview {
  margin-top: 8px;
}
.preview-content {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 24px 32px;
  font-family: 'Songti SC', 'SimSun', serif;
  font-size: 14px;
  line-height: 2;
  color: #303133;
  max-height: 500px;
  overflow-y: auto;
}
.preview-content :deep(.chapter-title) {
  font-size: 16px;
  font-weight: 700;
  margin: 16px 0 8px;
  text-align: center;
  color: #303133;
}
.preview-content :deep(.list-item) {
  margin-left: 2em;
}
</style>
