<template>
  <div class="phase-material-showcase">
    <el-form label-position="top">
      <!-- 筛选栏 -->
      <el-row :gutter="16" style="margin-bottom: 16px;">
        <el-col :span="8">
          <el-select
            v-model="filterL1"
            placeholder="一级分类"
            clearable
            style="width: 100%"
            @change="onL1Change"
          >
            <el-option
              v-for="cat in l1Categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select
            v-model="filterL2"
            placeholder="二级分类"
            clearable
            style="width: 100%"
            :disabled="!filterL1"
          >
            <el-option
              v-for="cat in l2Categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="keyword"
            placeholder="搜索物料名称/品牌"
            clearable
            @clear="loadCandidates"
            @keyup.enter="loadCandidates"
          >
            <template #append>
              <el-button :icon="Search" @click="loadCandidates" />
            </template>
          </el-input>
        </el-col>
      </el-row>

      <!-- 已选提示 -->
      <el-alert
        v-if="selectedIds.length > 0"
        type="success"
        :closable="false"
        style="margin-bottom: 12px"
      >
        已选 <b>{{ selectedIds.length }}</b> 个物料，将在幻灯片"材质展示"页展示
      </el-alert>

      <!-- 物料卡片网格 -->
      <div class="material-grid" v-loading="loading">
        <div
          v-for="item in candidates"
          :key="item.id"
          class="material-card"
          :class="{ selected: selectedIds.includes(item.id) }"
          @click="toggleSelect(item)"
        >
          <div class="card-thumb">
            <img
              v-if="item.main_image"
              :src="item.main_image"
              alt=""
              @error="onImgError"
            />
            <div v-else class="no-image">
              <el-icon :size="32"><Picture /></el-icon>
            </div>
            <!-- 选中角标 -->
            <div class="check-badge" v-if="selectedIds.includes(item.id)">
              <el-icon :size="18"><Check /></el-icon>
            </div>
          </div>
          <div class="card-info">
            <div class="card-name" :title="item.sku_name">{{ item.sku_name }}</div>
            <div class="card-meta">
              <el-tag size="small" type="info">{{ item.l2 || '未分类' }}</el-tag>
              <span class="card-brand" v-if="item.brand">{{ item.brand }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!loading && candidates.length === 0" description="暂无物料，请先去物料管理添加" />

      <!-- 分页 -->
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        style="margin-top: 16px; justify-content: center;"
        @current-change="loadCandidates"
      />
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Check, Picture } from '@element-plus/icons-vue'
import { getShowcaseCandidates } from '@/api/case'

const props = defineProps({
  caseId: { type: [Number, String], default: null },
  modelValue: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)
const candidates = ref([])
const selectedIds = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20

// 筛选
const filterL1 = ref(null)
const filterL2 = ref(null)
const keyword = ref('')
const l1Categories = ref([])
const l2Categories = ref([])

// 初始化：从 modelValue 读取已选 ID
onMounted(() => {
  if (props.modelValue?.showcase_material_ids) {
    selectedIds.value = [...props.modelValue.showcase_material_ids]
  }
  loadCategories()
  loadCandidates()
})

// 监听 caseId 变化
watch(() => props.caseId, () => {
  if (props.modelValue?.showcase_material_ids) {
    selectedIds.value = [...props.modelValue.showcase_material_ids]
  } else {
    selectedIds.value = []
  }
  loadCandidates()
})

watch(() => props.modelValue, (newVal) => {
  if (newVal?.showcase_material_ids) {
    // 仅当外部值确实不同时更新（避免死循环）
    const incoming = newVal.showcase_material_ids.map(Number)
    const current = selectedIds.value.map(Number).sort()
    const incomingSorted = incoming.sort()
    if (JSON.stringify(current) !== JSON.stringify(incomingSorted)) {
      selectedIds.value = [...newVal.showcase_material_ids]
    }
  } else {
    selectedIds.value = []
  }
}, { deep: true })

const loadCategories = async () => {
  try {
    const res = await fetch('/api/v3/materials/filter-options', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    }).then(r => r.json())
    l1Categories.value = res.l1_categories || []
  } catch (e) {
    console.warn('加载分类失败', e)
  }
}

const onL1Change = async () => {
  filterL2.value = null
  l2Categories.value = []
  if (!filterL1.value) return
  try {
    const res = await fetch(`/api/v3/material-categories/${filterL1.value}/children`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    }).then(r => r.json())
    l2Categories.value = res.children || res || []
  } catch (e) {
    console.warn('加载二级分类失败', e)
  }
}

const loadCandidates = async () => {
  if (!props.caseId) return
  loading.value = true
  try {
    const params = {}
    if (filterL1.value) params.l1_category_id = filterL1.value
    if (filterL2.value) params.l2_category_id = filterL2.value
    if (keyword.value) params.keyword = keyword.value
    const res = await getShowcaseCandidates(props.caseId, params)
    candidates.value = res || []
  } catch (e) {
    console.warn('加载材质候选项失败', e)
    candidates.value = []
  } finally {
    loading.value = false
  }
}

const toggleSelect = (item) => {
  const idx = selectedIds.value.indexOf(item.id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(item.id)
  }
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    ...(props.modelValue || {}),
    showcase_material_ids: [...selectedIds.value]
  })
}

const onImgError = (e) => {
  e.target.style.display = 'none'
}
</script>

<style scoped>
.phase-material-showcase {
  width: 100%;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  min-height: 120px;
}

.material-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.material-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.material-card.selected {
  border-color: #67c23a;
  box-shadow: 0 0 0 1px #67c23a;
}

.card-thumb {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #c0c4cc;
}

.check-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #67c23a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-info {
  padding: 8px;
}

.card-name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-brand {
  font-size: 11px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
