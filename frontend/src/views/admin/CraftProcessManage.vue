<template>
  <div class="craft-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>特殊工艺数据库</h2>
      <div>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建工艺
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="工艺名称/编码" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="全部分类" clearable>
            <el-option label="全屋定制工艺" value="custom" />
            <el-option label="硬装施工工艺" value="construction" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_enabled" placeholder="全部状态" clearable>
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 工艺列表 -->
    <el-card shadow="never">
      <el-table :data="crafts" v-loading="loading" stripe @selection-change="onSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column label="主图" width="80" align="center">
          <template #default="{ row }">
            <el-image v-if="row.main_image" :src="row.main_image" style="width:50px;height:50px" fit="cover" :preview-src-list="[row.main_image]" preview-teleported />
            <span v-else style="color:#ccc">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="工艺名称" min-width="200" />
        <el-table-column label="分类" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="row.category === 'custom' ? 'warning' : 'success'" size="small">
              {{ row.category === 'custom' ? '全屋定制' : '硬装施工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="工艺系数" width="100" align="center">
          <template #default="{ row }">{{ row.coefficient }}</template>
        </el-table-column>
        <el-table-column label="工艺单价" width="120" align="right">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="70" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_enabled" @change="toggleStatus(row)" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="filterForm.page"
          v-model:page-size="filterForm.page_size"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadData"
          @size-change="loadData"
        />
      </div>

      <div class="batch-actions" v-if="selectedRows.length > 0">
        <el-button type="danger" size="small" @click="batchDelete">
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工艺' : '新建工艺'" width="720px" destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工艺名称" prop="name">
              <el-input v-model="form.name" placeholder="输入工艺名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工艺编码" prop="code">
              <el-input v-model="form.code" placeholder="输入编码（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工艺分类" prop="category">
              <el-select v-model="form.category" placeholder="选择分类" style="width:100%">
                <el-option label="全屋定制工艺" value="custom" />
                <el-option label="硬装施工工艺" value="construction" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="工艺系数" prop="coefficient">
              <el-input-number v-model="form.coefficient" :min="0.001" :max="999" :precision="3" :step="0.1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="工艺单价" prop="unit_price">
              <el-input-number v-model="form.unit_price" :min="0" :precision="2" :step="10" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="项" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 图片上传 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="主图">
              <div class="upload-area">
                <el-image v-if="form.main_image" :src="form.main_image" fit="cover" class="preview-img" />
                <el-upload
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :http-request="(opts) => handleUpload(opts, 'main_image')"
                  accept="image/*"
                >
                  <el-button size="small" type="primary">上传</el-button>
                </el-upload>
                <el-button v-if="form.main_image" size="small" @click="form.main_image = ''" style="margin-top:4px">清除</el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="施工图">
              <div class="upload-area">
                <el-image v-if="form.construction_image" :src="form.construction_image" fit="cover" class="preview-img" />
                <el-upload
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :http-request="(opts) => handleUpload(opts, 'construction_image')"
                  accept="image/*"
                >
                  <el-button size="small" type="primary">上传</el-button>
                </el-upload>
                <el-button v-if="form.construction_image" size="small" @click="form.construction_image = ''" style="margin-top:4px">清除</el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="实景图">
              <div class="upload-area">
                <el-image v-if="form.real_image" :src="form.real_image" fit="cover" class="preview-img" />
                <el-upload
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :http-request="(opts) => handleUpload(opts, 'real_image')"
                  accept="image/*"
                >
                  <el-button size="small" type="primary">上传</el-button>
                </el-upload>
                <el-button v-if="form.real_image" size="small" @click="form.real_image = ''" style="margin-top:4px">清除</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 工艺简介（富文本） -->
        <el-form-item label="工艺简介">
          <div style="width:100%">
            <div class="rich-toolbar">
              <el-button-group>
                <el-button size="small" @click="insertTag('b')" title="加粗"><b>B</b></el-button>
                <el-button size="small" @click="insertTag('i')" title="斜体"><i>I</i></el-button>
                <el-button size="small" @click="insertTag('u')" title="下划线"><u>U</u></el-button>
                <el-button size="small" @click="insertTag('h3')" title="标题">H3</el-button>
                <el-button size="small" @click="insertTag('ul')" title="无序列表">• 列表</el-button>
                <el-button size="small" @click="insertTag('p')" title="段落">¶ 段落</el-button>
              </el-button-group>
            </div>
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="6"
              placeholder="支持HTML富文本格式，可使用上方工具插入标签"
            />
          </div>
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 筛选
const filterForm = reactive({
  keyword: '',
  category: '',
  is_enabled: '',
  page: 1,
  page_size: 20
})

const loading = ref(false)
const crafts = ref([])
const total = ref(0)
const selectedRows = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = { ...filterForm }
    // 清理空值
    Object.keys(params).forEach(k => {
      if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k]
    })
    const res = await request.get('/crafts', { params })
    crafts.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.category = ''
  filterForm.is_enabled = ''
  filterForm.page = 1
  loadData()
}

const onSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 表单
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const formRules = {
  name: [{ required: true, message: '请输入工艺名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择工艺分类', trigger: 'change' }],
}

const defaultForm = () => ({
  id: null,
  name: '',
  category: 'custom',
  code: '',
  coefficient: 1,
  unit_price: 0,
  unit: '项',
  main_image: '',
  construction_image: '',
  real_image: '',
  description: '',
  is_enabled: true,
  sort_order: 0,
})

const form = reactive(defaultForm())

const openCreateDialog = () => {
  isEdit.value = false
  Object.assign(form, defaultForm())
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    category: row.category,
    code: row.code || '',
    coefficient: row.coefficient,
    unit_price: row.unit_price,
    unit: row.unit,
    main_image: row.main_image || '',
    construction_image: row.construction_image || '',
    real_image: row.real_image || '',
    description: row.description || '',
    is_enabled: row.is_enabled,
    sort_order: row.sort_order || 0,
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch { return }

  submitting.value = true
  try {
    const payload = { ...form }
    delete payload.id

    if (isEdit.value) {
      await request.put(`/crafts/${form.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/crafts', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除工艺「${row.name}」？`, '提示', { type: 'warning' })
    await request.delete(`/crafts/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定删除 ${selectedRows.value.length} 条工艺？`, '提示', { type: 'warning' })
    await request.post('/crafts/batch-delete', { ids: selectedRows.value.map(r => r.id) })
    ElMessage.success('批量删除成功')
    loadData()
  } catch {}
}

// 切换状态
const toggleStatus = async (row) => {
  try {
    await request.post('/crafts/toggle-status', { id: row.id })
    row.is_enabled = !row.is_enabled
  } catch {
    ElMessage.error('操作失败')
  }
}

// 图片上传
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB')
    return false
  }
  return true
}

const handleUpload = async (options, field) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await request.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form[field] = res.file_url || res.url || ''
    ElMessage.success('上传成功')
  } catch (e) {
    ElMessage.error('上传失败')
  }
}

// 富文本工具
const insertTag = (tag) => {
  const templates = {
    b: '<b>加粗文本</b>',
    i: '<i>斜体文本</i>',
    u: '<u>下划线文本</u>',
    h3: '<h3>小标题</h3>',
    ul: '<ul><li>列表项1</li><li>列表项2</li></ul>',
    p: '<p>段落文本</p>',
  }
  const insert = templates[tag] || ''
  form.description = (form.description || '') + insert
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.craft-manage {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
}
.filter-card {
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.batch-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.preview-img {
  width: 120px;
  height: 90px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  margin-bottom: 4px;
}
.rich-toolbar {
  margin-bottom: 8px;
}
</style>
