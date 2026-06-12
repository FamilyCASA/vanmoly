<template>
  <div class="template-settings">
    <div class="page-header">
      <el-page-header @back="$router.back()">
        <template #content>报价模板管理</template>
      </el-page-header>
    </div>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="template-tabs">
      <!-- 封面模板 Tab -->
      <el-tab-pane label="封面模板" name="cover">
        <el-table :data="coverTemplates" v-loading="loadingCover" stripe>
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
              <el-button link type="primary" @click="openCoverEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteCoverTemplate(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top:16px">
          <el-button type="primary" @click="openCoverCreate">
            <el-icon><Plus /></el-icon> 新建封面模板
          </el-button>
        </div>
      </el-tab-pane>

      <!-- 空间物料模板 Tab -->
      <el-tab-pane label="空间物料模板" name="space">
        <!-- 筛选区 -->
        <div class="filter-bar">
          <el-select v-model="filterSpaceType" placeholder="空间类型" clearable style="width:140px">
            <el-option label="客厅" value="living" />
            <el-option label="主卧" value="master_bedroom" />
            <el-option label="次卧" value="second_bedroom" />
            <el-option label="儿童房" value="children" />
            <el-option label="厨房" value="kitchen" />
            <el-option label="餐厅" value="dining" />
            <el-option label="书房" value="study" />
            <el-option label="卫生间" value="bathroom" />
            <el-option label="阳台" value="balcony" />
            <el-option label="玄关" value="entryway" />
            <el-option label="衣帽间" value="closet" />
          </el-select>
          <el-input v-model="filterKeyword" placeholder="搜索模板名称" clearable style="width:180px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button @click="loadSpaceTemplates">筛选</el-button>
          <el-button type="primary" @click="openSpaceCreate">
            <el-icon><Plus /></el-icon> 新建空间模板
          </el-button>
        </div>

        <!-- 空间模板列表 -->
        <el-table :data="spaceTemplates" v-loading="loadingSpace" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="模板名称" min-width="180" />
          <el-table-column prop="space_name" label="空间" width="90">
            <template #default="{ row }">{{ spaceTypeLabel(row.space_type) }}</template>
          </el-table-column>
          <el-table-column prop="version_level" label="档位" width="80">
            <template #default="{ row }">
              <el-tag size="small" type="warning">{{ row.version_level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="material_count" label="物料数" width="80" align="center" />
          <el-table-column prop="total_price" label="空间总价(元)" width="120" align="right">
            <template #default="{ row }">¥{{ (row.total_price || 0).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="house_type" label="户型" width="100" />
          <el-table-column prop="style" label="风格" width="80" />
          <el-table-column label="物料预览" min-width="200">
            <template #default="{ row }">
              <span class="material-preview">
                {{ getMaterialPreview(row.items) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openSpaceEdit(row)">编辑</el-button>
              <el-button link type="info" @click="previewSpaceTemplate(row)">预览物料</el-button>
              <el-button link type="danger" @click="deleteSpaceTemplate(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-if="spaceTotal > 0"
          v-model:current-page="spacePage"
          :page-size="spacePageSize"
          :total="spaceTotal"
          layout="prev,pager,next"
          style="margin-top:16px"
          @current-change="loadSpaceTemplates"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- ========== 封面模板对话框 ========== -->
    <el-dialog v-model="coverDialogVisible" :title="isCoverEditing ? '编辑封面模板' : '新建封面模板'" width="600px">
      <el-form :model="coverForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="coverForm.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="coverForm.template_type">
            <el-option label="现代" value="modern" />
            <el-option label="经典" value="classic" />
            <el-option label="极简" value="minimal" />
            <el-option label="奢华" value="luxury" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">样式配置</el-divider>
        <el-form-item label="主色">
          <el-color-picker v-model="coverForm.style_config.primary_color" />
        </el-form-item>
        <el-form-item label="副色">
          <el-color-picker v-model="coverForm.style_config.secondary_color" />
        </el-form-item>
        <el-form-item label="背景色">
          <el-color-picker v-model="coverForm.style_config.background_color" />
        </el-form-item>
        <el-form-item label="字体">
          <el-select v-model="coverForm.style_config.font_family" style="width:200px">
            <el-option label="微软雅黑" value="Microsoft YaHei" />
            <el-option label="宋体" value="SimSun" />
            <el-option label="黑体" value="SimHei" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">水印配置</el-divider>
        <el-form-item label="水印文字">
          <el-input v-model="coverForm.watermark_config.text" placeholder="例如：公司名称" />
        </el-form-item>
        <el-form-item label="透明度">
          <el-slider v-model="coverForm.watermark_config.opacity" :min="0" :max="1" :step="0.05" show-input />
        </el-form-item>
        <el-divider content-position="left">其他</el-divider>
        <el-form-item label="排序">
          <el-input-number v-model="coverForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="coverForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="coverDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCoverTemplate" :loading="savingCover">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 空间模板编辑对话框 ========== -->
    <el-dialog v-model="spaceDialogVisible" :title="isSpaceEditing ? '编辑空间模板' : '新建空间模板'" width="900px">
      <el-form :model="spaceForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板名称" required>
              <el-input v-model="spaceForm.name" placeholder="如：现代轻奢-主卧-标配" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="档位">
              <el-select v-model="spaceForm.version_level" style="width:100%">
                <el-option label="标配" value="标配" />
                <el-option label="升级" value="升级" />
                <el-option label="豪华" value="豪华" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="空间类型">
              <el-select v-model="spaceForm.space_type" style="width:100%">
                <el-option label="客厅" value="living" />
                <el-option label="主卧" value="master_bedroom" />
                <el-option label="次卧" value="second_bedroom" />
                <el-option label="儿童房" value="children" />
                <el-option label="厨房" value="kitchen" />
                <el-option label="餐厅" value="dining" />
                <el-option label="书房" value="study" />
                <el-option label="卫生间" value="bathroom" />
                <el-option label="阳台" value="balcony" />
                <el-option label="玄关" value="entryway" />
                <el-option label="衣帽间" value="closet" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="空间名称">
              <el-input v-model="spaceForm.space_name" placeholder="如：主卧" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="户型">
              <el-input v-model="spaceForm.house_type" placeholder="如：三室两厅" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="风格">
              <el-input v-model="spaceForm.style" placeholder="如：现代轻奢" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="面积范围">
              <el-input v-model="spaceForm.area_range" placeholder="如：15-20㎡" />
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 物料列表 -->
        <el-divider content-position="left">
          物料清单（共 {{ spaceForm.items.length }} 项）
          <el-button link type="primary" size="small" @click="addSpaceItem">+ 添加物料</el-button>
        </el-divider>
        <el-table :data="spaceForm.items" border size="small" max-height="300">
          <el-table-column prop="name" label="物料名称" min-width="140" />
          <el-table-column prop="spec" label="规格" width="120" />
          <el-table-column prop="brand" label="品牌" width="90" />
          <el-table-column prop="unit" label="单位" width="60" align="center" />
          <el-table-column prop="quantity" label="数量" width="70" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.1" :step="1" size="small" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价(元)" width="90" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column prop="total_price" label="小计" width="90" align="right">
            <template #default="{ row }">
              {{ ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ $index }">
              <el-button link type="danger" size="small" @click="removeSpaceItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="space-total">
          物料成本合计：¥{{ calcSpaceTotal().toLocaleString() }}
        </div>
      </el-form>
      <template #footer>
        <el-button @click="spaceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSpaceTemplate" :loading="savingSpace">保存</el-button>
      </template>
    </el-dialog>

    <!-- ========== 物料预览对话框 ========== -->
    <el-dialog v-model="previewDialogVisible" title="物料清单预览" width="700px">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="模板名称">{{ previewTemplate?.name }}</el-descriptions-item>
        <el-descriptions-item label="空间">{{ spaceTypeLabel(previewTemplate?.space_type) }}</el-descriptions-item>
        <el-descriptions-item label="档位">{{ previewTemplate?.version_level }}</el-descriptions-item>
        <el-descriptions-item label="物料数量">{{ previewTemplate?.material_count }}</el-descriptions-item>
        <el-descriptions-item label="物料成本">¥{{ (previewTemplate?.material_cost || 0).toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="空间总价">¥{{ (previewTemplate?.total_price || 0).toLocaleString() }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <el-table :data="previewTemplate?.items || []" border size="small">
        <el-table-column prop="name" label="物料名称" min-width="140" />
        <el-table-column prop="spec" label="规格" width="120" />
        <el-table-column prop="brand" label="品牌" width="90" />
        <el-table-column prop="unit" label="单位" width="60" align="center" />
        <el-table-column prop="quantity" label="数量" width="70" align="center" />
        <el-table-column prop="unit_price" label="单价" width="80" align="right">
          <template #default="{ row }">¥{{ (row.unit_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="小计" width="90" align="right">
          <template #default="{ row }">¥{{ (row.total_price || 0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- ========== 物料选择对话框 ========== -->
    <el-dialog v-model="skuDialogVisible" title="选择物料" width="900px">
      <div style="margin-bottom:12px;display:flex;gap:8px">
        <el-input v-model="skuKeyword" placeholder="搜索物料名称/规格" clearable style="width:240px" @clear="loadSkuList" @keyup.enter="loadSkuList">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="skuCategory" placeholder="分类" clearable style="width:160px">
          <el-option v-for="c in skuCategories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button @click="loadSkuList">搜索</el-button>
      </div>
      <el-table :data="skuList" border size="small" height="400" @row-dblclick="selectSku">
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="spec" label="规格" width="120" />
        <el-table-column prop="brand" label="品牌" width="90" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="unit" label="单位" width="60" align="center" />
        <el-table-column prop="retail_price" label="单价" width="80" align="right">
          <template #default="{ row }">¥{{ (row.retail_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column width="70">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="selectSku(row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="skuTotal > 0"
        v-model:current-page="skuPage"
        :page-size="skuPageSize"
        :total="skuTotal"
        layout="prev,pager,next"
        style="margin-top:12px"
        @current-change="loadSkuList"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

// ===== 状态 =====
const activeTab = ref('space') // 默认显示空间物料模板
const loadingCover = ref(false)
const loadingSpace = ref(false)

// ===== 封面模板 =====
const coverTemplates = ref([])
const coverDialogVisible = ref(false)
const isCoverEditing = ref(false)
const savingCover = ref(false)
const editingCoverId = ref(null)

const defaultCoverForm = {
  name: '',
  template_type: 'modern',
  style_config: {
    primary_color: '#409eff',
    secondary_color: '#67c23a',
    background_color: '#ffffff',
    font_family: 'Microsoft YaHei'
  },
  watermark_config: { text: '', opacity: 0.1, font_size: 48, angle: -45 },
  background_images: [],
  is_default: false,
  sort_order: 0
}
const coverForm = reactive({ ...JSON.parse(JSON.stringify(defaultCoverForm)) })

const typeLabel = (type) => {
  const map = { modern: '现代', classic: '经典', minimal: '极简', luxury: '奢华' }
  return map[type] || type
}

const spaceTypeLabel = (type) => {
  const map = {
    living: '客厅', master_bedroom: '主卧', second_bedroom: '次卧',
    children: '儿童房', kitchen: '厨房', dining: '餐厅',
    study: '书房', bathroom: '卫生间', balcony: '阳台',
    entryway: '玄关', closet: '衣帽间'
  }
  return map[type] || type || '-'
}

// ===== 空间模板 =====
const spaceTemplates = ref([])
const spacePage = ref(1)
const spacePageSize = ref(20)
const spaceTotal = ref(0)
const filterSpaceType = ref('')
const filterKeyword = ref('')
const spaceDialogVisible = ref(false)
const isSpaceEditing = ref(false)
const savingSpace = ref(false)
const editingSpaceId = ref(null)
const previewDialogVisible = ref(false)
const previewTemplate = ref(null)

const defaultSpaceForm = () => ({
  name: '',
  space_type: '',
  space_name: '',
  version_level: '标配',
  house_type: '',
  style: '',
  area_range: '',
  items: []
})
const spaceForm = reactive(defaultSpaceForm())

// ===== 物料选择 =====
const skuDialogVisible = ref(false)
const skuList = ref([])
const skuPage = ref(1)
const skuPageSize = ref(20)
const skuTotal = ref(0)
const skuKeyword = ref('')
const skuCategories = ref([])
const skuCategory = ref('')
let pendingItemIndex = -1

// ===== 封面模板方法 =====
const loadCoverTemplates = async () => {
  try {
    loadingCover.value = true
    const res = await request.get('/quotes/templates')
    coverTemplates.value = res.data?.data || res.data || []
  } catch (e) {
    ElMessage.error('加载封面模板失败')
  } finally {
    loadingCover.value = false
  }
}

const resetCoverForm = () => {
  Object.assign(coverForm, JSON.parse(JSON.stringify(defaultCoverForm)))
  isCoverEditing.value = false
  editingCoverId.value = null
}

const openCoverCreate = () => {
  resetCoverForm()
  coverDialogVisible.value = true
}

const openCoverEdit = (row) => {
  isCoverEditing.value = true
  editingCoverId.value = row.id
  coverForm.name = row.name
  coverForm.template_type = row.template_type || 'modern'
  coverForm.style_config = { ...defaultCoverForm.style_config, ...(row.style_config || {}) }
  coverForm.watermark_config = { ...defaultCoverForm.watermark_config, ...(row.watermark_config || {}) }
  coverForm.background_images = row.background_images || []
  coverForm.is_default = row.is_default || false
  coverForm.sort_order = row.sort_order || 0
  coverDialogVisible.value = true
}

const saveCoverTemplate = async () => {
  if (!coverForm.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  try {
    savingCover.value = true
    const payload = {
      name: coverForm.name,
      template_type: coverForm.template_type,
      style_config: coverForm.style_config,
      watermark_config: coverForm.watermark_config,
      background_images: coverForm.background_images,
      is_default: coverForm.is_default,
      sort_order: coverForm.sort_order
    }
    if (isCoverEditing.value) {
      await request.put(`/quotes/templates/${editingCoverId.value}`, payload)
    } else {
      await request.post('/quotes/templates', payload)
    }
    ElMessage.success('保存成功')
    coverDialogVisible.value = false
    loadCoverTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    savingCover.value = false
  }
}

const deleteCoverTemplate = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」？`, '提示', { type: 'warning' })
    await request.delete(`/quotes/templates/${row.id}`)
    ElMessage.success('删除成功')
    loadCoverTemplates()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 空间模板方法 =====
const loadSpaceTemplates = async () => {
  try {
    loadingSpace.value = true
    const params = {
      page: spacePage.value,
      page_size: spacePageSize.value,
      space_type: filterSpaceType.value || undefined,
      keyword: filterKeyword.value || undefined
    }
    const res = await request.get('/quotes/space-templates', { params })
    const data = res.data?.data || res.data || {}
    spaceTemplates.value = data.items || []
    spaceTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载空间模板失败')
  } finally {
    loadingSpace.value = false
  }
}

const getMaterialPreview = (items) => {
  if (!items || items.length === 0) return '-'
  const names = items.slice(0, 3).map(it => it.name).join('、')
  return items.length > 3 ? `${names}...` : names
}

const previewSpaceTemplate = (row) => {
  previewTemplate.value = row
  previewDialogVisible.value = true
}

const resetSpaceForm = () => {
  Object.assign(spaceForm, defaultSpaceForm())
  isSpaceEditing.value = false
  editingSpaceId.value = null
}

const openSpaceCreate = () => {
  resetSpaceForm()
  spaceDialogVisible.value = true
}

const openSpaceEdit = (row) => {
  isSpaceEditing.value = true
  editingSpaceId.value = row.id
  spaceForm.name = row.name
  spaceForm.space_type = row.space_type || ''
  spaceForm.space_name = row.space_name || ''
  spaceForm.version_level = row.version_level || '标配'
  spaceForm.house_type = row.house_type || ''
  spaceForm.style = row.style || ''
  spaceForm.area_range = row.area_range || ''
  // 深拷贝 items
  spaceForm.items = (row.items || []).map(it => ({ ...it }))
  spaceDialogVisible.value = true
}

const calcSpaceTotal = () => {
  return spaceForm.items.reduce((sum, it) => sum + (it.quantity || 0) * (it.unit_price || 0), 0)
}

const addSpaceItem = () => {
  pendingItemIndex = -1
  skuKeyword.value = ''
  skuCategory.value = ''
  skuPage.value = 1
  skuDialogVisible.value = true
  loadSkuList()
  loadSkuCategories()
}

const removeSpaceItem = (index) => {
  spaceForm.items.splice(index, 1)
}

const selectSku = (sku) => {
  const item = {
    sku_id: sku.id,
    sku_code: sku.sku_code,
    name: sku.name,
    spec: sku.spec || sku.specification,
    brand: sku.brand,
    unit: sku.unit,
    material: sku.material,
    quantity: 1,
    unit_price: sku.retail_price || 0,
    total_price: (sku.retail_price || 0)
  }
  if (pendingItemIndex >= 0) {
    spaceForm.items[pendingItemIndex] = item
  } else {
    spaceForm.items.push(item)
  }
  skuDialogVisible.value = false
}

const loadSkuList = async () => {
  try {
    const params = {
      page: skuPage.value,
      page_size: skuPageSize.value,
      keyword: skuKeyword.value || undefined,
      category_id: skuCategory.value || undefined
    }
    const res = await request.get('/v3/materials', { params })
    const data = res.data?.data || res.data || {}
    skuList.value = data.items || []
    skuTotal.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载物料失败')
  }
}

const loadSkuCategories = async () => {
  if (skuCategories.value.length > 0) return
  try {
    const res = await request.get('/v3/material-categories')
    skuCategories.value = res.data?.data || res.data || []
  } catch (e) { /* ignore */ }
}

const saveSpaceTemplate = async () => {
  if (!spaceForm.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  try {
    savingSpace.value = true
    const payload = {
      ...spaceForm,
      material_count: spaceForm.items.length,
      material_cost: calcSpaceTotal(),
      total_price: calcSpaceTotal()
    }
    if (isSpaceEditing.value) {
      await request.put(`/quotes/space-templates/${editingSpaceId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/quotes/space-templates', payload)
      ElMessage.success('创建成功')
    }
    spaceDialogVisible.value = false
    loadSpaceTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    savingSpace.value = false
  }
}

const deleteSpaceTemplate = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」？`, '提示', { type: 'warning' })
    await request.delete(`/quotes/space-templates/${row.id}`)
    ElMessage.success('删除成功')
    loadSpaceTemplates()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

// ===== 生命周期 =====
onMounted(() => {
  loadCoverTemplates()
  loadSpaceTemplates()
})
</script>

<style scoped>
.template-settings { padding: 20px; }
.page-header { margin-bottom: 20px; }
.template-tabs { background: #fff; padding: 16px; border-radius: 8px; }
.filter-bar { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; flex-wrap: wrap; }
.color-dot { width: 16px; height: 16px; border-radius: 50%; border: 1px solid #ddd; display: inline-block; }
.material-preview { font-size: 12px; color: #666; }
.space-total { text-align: right; font-size: 14px; font-weight: bold; color: #409eff; margin-top: 8px; }
</style>
