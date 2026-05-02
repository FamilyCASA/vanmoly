<template>
  <div class="material-selector">
    <el-form :inline="true" class="search-bar">
      <el-form-item label="关键词">
        <el-input v-model="keyword" placeholder="搜索物料名称/规格/品牌" clearable @keyup.enter="search" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="categoryId" placeholder="全部分类" clearable style="width:180px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">搜索</el-button>
        <el-button @click="reset">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table
      ref="tableRef"
      :data="materials"
      v-loading="loading"
      height="400"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="45" />
      <el-table-column prop="name" label="物料名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="spec" label="规格" width="120" show-overflow-tooltip />
      <el-table-column prop="brand" label="品牌" width="100" show-overflow-tooltip />
      <el-table-column prop="unit" label="单位" width="60" align="center" />
      <el-table-column label="单价" width="100" align="right">
        <template #default="{ row }">
          ¥{{ row.sale_price || row.base_price || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="category_name" label="分类" width="120" show-overflow-tooltip />
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, prev, pager, next"
        @current-change="loadMaterials"
      />
    </div>

    <div class="selector-footer">
      <span class="selected-count">已选 {{ selected.length }} 项</span>
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="confirm" :disabled="selected.length === 0">确定添加</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const emit = defineEmits(['select'])

const tableRef = ref(null)
const loading = ref(false)
const materials = ref([])
const categories = ref([])
const selected = ref([])

const keyword = ref('')
const categoryId = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const search = () => {
  page.value = 1
  loadMaterials()
}

const reset = () => {
  keyword.value = ''
  categoryId.value = null
  page.value = 1
  loadMaterials()
}

const loadCategories = async () => {
  try {
    const res = await request.get('/materials/categories')
    categories.value = res.items || res || []
  } catch {
    categories.value = []
  }
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (categoryId.value) params.category_id = categoryId.value

    const res = await request.get('/materials', params)
    materials.value = res.items || res || []
    total.value = res.total || materials.value.length
  } catch (e) {
    ElMessage.error('加载物料列表失败')
    materials.value = []
  } finally {
    loading.value = false
  }
}

const onSelectionChange = (rows) => {
  selected.value = rows
}

const cancel = () => {
  emit('select', [])
}

const confirm = () => {
  if (selected.value.length === 0) {
    ElMessage.warning('请先选择物料')
    return
  }
  emit('select', selected.value)
}

onMounted(() => {
  loadCategories()
  loadMaterials()
})
</script>

<style scoped>
.material-selector {
  min-height: 300px;
}

.search-bar {
  margin-bottom: 12px;
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.selector-footer {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
}

.selected-count {
  color: #909399;
  font-size: 13px;
}
</style>
