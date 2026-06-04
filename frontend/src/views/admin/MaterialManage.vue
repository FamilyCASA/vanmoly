<template>
  <div class="material-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>物料管理</h2>
        <span class="subtitle">管理产品SKU、分类、库存</span>
      </div>
      <el-button type="primary" size="large" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新建物料
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6F7FF; color: #1890FF;">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total || 0 }}</div>
            <div class="stat-label">总物料</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F6FFED; color: #52C41A;">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.by_status?.active || 0 }}</div>
            <div class="stat-label">在售</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF7E6; color: #FA8C16;">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.low_stock || 0 }}</div>
            <div class="stat-label">库存预警</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F9F0FF; color: #722ED1;">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ categoryList.length }}</div>
            <div class="stat-label">分类</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 分类筛选按钮 -->
    <el-card class="category-filter-card" shadow="never" v-if="categoryStats.length > 0">
      <div class="category-buttons">
        <div
          class="category-btn"
          :class="{ active: selectedCategory === null }"
          @click="selectCategory(null)"
        >
          <div class="category-name">全部物料</div>
          <div class="category-count">{{ stats.total || 0 }}项</div>
        </div>
        <div
          v-for="cat in categoryStats"
          :key="cat.id"
          class="category-btn"
          :class="{ active: selectedCategory === cat.id }"
          @click="selectCategory(cat.id)"
        >
          <div class="category-name">{{ cat.name }}</div>
          <div class="category-count">{{ cat.count }}项</div>
        </div>
      </div>
    </el-card>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="名称/编码/品牌"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-cascader
            v-model="filterForm.category_id"
            :options="categoryTree"
            :props="{ value: 'id', label: 'name', checkStrictly: true }"
            placeholder="选择分类"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option
              v-for="s in options.sku_status"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            >
              <el-tag :type="s.type" size="small">{{ s.label }}</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="filterForm.low_stock">仅看低库存</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        :data="materials"
        v-loading="loading"
        row-key="id"
        style="width: 100%"
      >
        <el-table-column type="expand" width="40">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="SKU编码">{{ row.sku_code }}</el-descriptions-item>
                <el-descriptions-item label="材质">{{ row.material || '-' }}</el-descriptions-item>
                <el-descriptions-item label="产地">{{ row.origin || '-' }}</el-descriptions-item>
                <el-descriptions-item label="成本价">¥{{ row.cost_price }}</el-descriptions-item>
                <el-descriptions-item label="市场价">¥{{ row.market_price || '-' }}</el-descriptions-item>
                <el-descriptions-item label="计价方式">
                  {{ calcTypeLabel(row.calc_type) }}
                </el-descriptions-item>
              </el-descriptions>
              <div v-if="row.customization_rules?.length" class="rules-section">
                <div class="section-title">定制规则</div>
                <el-tag
                  v-for="rule in row.customization_rules"
                  :key="rule.field"
                  size="small"
                  class="rule-tag"
                >
                  {{ rule.name }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="物料信息" min-width="280">
          <template #default="{ row }">
            <div class="material-info">
              <el-image
                :src="row.main_image || '/images/default-material.png'"
                class="material-image"
                fit="cover"
              />
              <div class="material-detail">
                <div class="material-name">{{ row.name }}</div>
                <div class="material-meta">
                  <el-tag size="small" effect="plain">{{ row.category_name || '未分类' }}</el-tag>
                  <span class="brand">{{ row.brand || '无品牌' }}</span>
                </div>
                <div class="material-spec">{{ row.specification || '暂无规格' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="价格" width="150" align="right">
          <template #default="{ row }">
            <div class="price-section">
              <div class="sale-price">¥{{ row.sale_price }}</div>
              <div class="unit">/{{ row.unit }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="库存" width="120" align="center">
          <template #default="{ row }">
            <div class="stock-section">
              <div
                class="stock-value"
                :class="{ 'low-stock': row.stock_quantity <= row.stock_warning }"
              >
                {{ row.stock_quantity }}
              </div>
              <div class="stock-warning" v-if="row.stock_quantity <= row.stock_warning">
                库存不足
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="变体" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_variants" type="info" size="small">有</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="openVariantDialog(row)">变体</el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button link type="primary">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="preview">
                    <el-icon><View /></el-icon> 预览
                  </el-dropdown-item>
                  <el-dropdown-item :command="row.status === 'active' ? 'unpublish' : 'publish'">
                    <el-icon><Upload v-if="row.status !== 'active'" /><Download v-else /></el-icon>
                    {{ row.status === 'active' ? '下架' : '上架' }}
                  </el-dropdown-item>
                  <el-dropdown-item command="copy">复制</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 物料表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑物料' : '新建物料'"
      width="800px"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="物料名称" prop="name">
                  <el-input v-model="form.name" placeholder="请输入物料名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="SKU编码">
                  <el-input v-model="form.sku_code" placeholder="留空自动生成" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="分类">
                  <el-cascader
                    v-model="form.category_id"
                    :options="categoryTree"
                    :props="{ value: 'id', label: 'name', checkStrictly: true }"
                    placeholder="选择分类"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-select v-model="form.status" style="width: 100%">
                    <el-option
                      v-for="s in options.sku_status"
                      :key="s.value"
                      :label="s.label"
                      :value="s.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="品牌">
                  <el-input v-model="form.brand" placeholder="品牌" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="型号">
                  <el-input v-model="form.model" placeholder="型号" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="产地">
                  <el-input v-model="form.origin" placeholder="产地" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="规格">
              <el-input v-model="form.specification" placeholder="规格参数" />
            </el-form-item>

            <el-form-item label="材质">
              <el-input v-model="form.material" placeholder="材质说明" />
            </el-form-item>

            <el-form-item label="主图">
              <el-upload
                class="avatar-uploader"
                action="/api/v3/upload"
                :show-file-list="false"
                :on-success="handleImageSuccess"
                :before-upload="beforeImageUpload"
              >
                <img v-if="form.main_image" :src="form.main_image" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="价格库存" name="price">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="成本价">
                  <el-input-number v-model="form.cost_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="销售价">
                  <el-input-number v-model="form.sale_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="市场价">
                  <el-input-number v-model="form.market_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="计价方式">
                  <el-select v-model="form.calc_type" style="width: 100%">
                    <el-option
                      v-for="t in options.calc_types"
                      :key="t.value"
                      :label="t.label"
                      :value="t.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="单位">
                  <el-input v-model="form.unit" placeholder="如：件、㎡、m" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="库存预警">
                  <el-input-number v-model="form.stock_warning" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="当前库存">
              <el-input-number v-model="form.stock_quantity" :min="0" style="width: 200px" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="定制规则" name="rules">
            <div class="rules-header">
              <span>配置定制加价规则</span>
              <el-button type="primary" link @click="addRule">
                <el-icon><Plus /></el-icon> 添加规则
              </el-button>
            </div>

            <div v-for="(rule, index) in form.customization_rules" :key="index" class="rule-item">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-select v-model="rule.type" placeholder="规则类型">
                    <el-option
                      v-for="t in options.customization_rule_types"
                      :key="t.value"
                      :label="t.label"
                      :value="t.value"
                    />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-input v-model="rule.name" placeholder="规则名称" />
                </el-col>
                <el-col :span="6">
                  <el-input v-model="rule.field" placeholder="字段名" />
                </el-col>
                <el-col :span="4">
                  <el-input-number v-model="rule.default" placeholder="默认值" style="width: 100%" />
                </el-col>
                <el-col :span="2">
                  <el-button type="danger" link @click="removeRule(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
              <div v-if="rule.type === 'increment'" class="rule-extra">
                <el-input-number v-model="rule.step" placeholder="步长" :min="1" />
                <span class="sep">每增加</span>
                <el-input-number v-model="rule.price_per_step" placeholder="加价" :min="0" />
                <span>元</span>
              </div>
            </div>

            <el-empty v-if="!form.customization_rules?.length" description="暂无定制规则" />
          </el-tab-pane>

          <el-tab-pane label="变体配置" name="variants">
            <el-form-item>
              <el-checkbox v-model="form.has_variants">启用变体（花色/尺寸）</el-checkbox>
            </el-form-item>

            <template v-if="form.has_variants">
              <div class="variant-options">
                <div class="option-header">
                  <span>变体选项定义</span>
                  <el-button type="primary" link @click="addVariantOption">
                    <el-icon><Plus /></el-icon> 添加选项
                  </el-button>
                </div>

                <div v-for="(opt, idx) in form.variant_options" :key="idx" class="option-item">
                  <el-input v-model="opt.name" placeholder="选项名称（如：颜色）" style="width: 150px" />
                  <el-select-v2
                    v-model="opt.values"
                    placeholder="输入选项值，按回车确认"
                    :options="[]"
                    multiple
                    filterable
                    allow-create
                    style="flex: 1; margin: 0 10px"
                  />
                  <el-button type="danger" link @click="removeVariantOption(idx)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tab-pane>

          <el-tab-pane label="其他" name="other">
            <el-form-item label="标签">
              <el-select-v2
                v-model="form.tags"
                placeholder="输入标签，按回车确认"
                :options="[]"
                multiple
                filterable
                allow-create
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="产品描述">
              <el-input v-model="form.description" type="textarea" :rows="4" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 变体管理对话框 -->
    <el-dialog v-model="variantDialog.visible" title="变体管理" width="700px">
      <el-table :data="variantDialog.variants" border size="small">
        <el-table-column label="变体名称" prop="variant_name" />
        <el-table-column label="属性">
          <template #default="{ row }">
            <el-tag
              v-for="(val, key) in row.variant_values"
              :key="key"
              size="small"
              class="variant-tag"
            >
              {{ key }}: {{ val }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格调整" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.price_adjustment" :min="-9999" :precision="2" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="库存" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.stock_quantity" :min="0" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeVariant($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="variant-actions">
        <el-button type="primary" @click="generateVariants">
          <el-icon><Refresh /></el-icon> 根据选项生成变体
        </el-button>
        <el-button @click="addCustomVariant">
          <el-icon><Plus /></el-icon> 手动添加
        </el-button>
      </div>

      <template #footer>
        <el-button @click="variantDialog.visible = false">关闭</el-button>
        <el-button type="primary" @click="saveVariants">保存变体</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Box, Check, Warning, FolderOpened, ArrowDown, Delete, Refresh, View, Upload, Download } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const materials = ref([])
const categoryList = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const activeTab = ref('basic')

const filterForm = reactive({
  keyword: '',
  category_id: null,
  status: '',
  low_stock: false
})

const options = reactive({
  calc_types: [],
  customization_rule_types: [],
  sku_status: []
})

// 分类统计
const categoryStats = ref([])
const selectedCategory = ref(null)

// 分类树
const categoryTree = computed(() => {
  return buildTree(categoryList.value)
})

const buildTree = (items, parentId = null) => {
  return items
    .filter(item => item.parent_id === parentId)
    .map(item => ({
      ...item,
      children: buildTree(items, item.id)
    }))
}

// 对话框
const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  sku_code: '',
  name: '',
  category_id: null,
  brand: '',
  model: '',
  specification: '',
  material: '',
  origin: '',
  main_image: '',
  images: [],
  cost_price: 0,
  sale_price: 0,
  market_price: null,
  unit: '件',
  calc_type: 'quantity',
  stock_quantity: 0,
  stock_warning: 10,
  customization_rules: [],
  has_variants: false,
  variant_options: [],
  has_craft_parts: false,
  craft_parts: [],
  description: '',
  tags: [],
  status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }]
}

const formRef = ref(null)

// 变体对话框
const variantDialog = reactive({
  visible: false,
  skuId: null,
  variants: []
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/materials', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        category_id: filterForm.category_id,
        status: filterForm.status,
        low_stock: filterForm.low_stock
      }
    })
    materials.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载物料列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载分类
const loadCategories = async () => {
  try {
    const res = await request.get('/materials/categories')
    categoryList.value = res
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await request.get('/materials/stats')
    stats.value = res
    categoryStats.value = res.by_category || []
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 选择分类
const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
  filterForm.category_id = categoryId
  page.value = 1
  loadData()
}

// 加载选项
const loadOptions = async () => {
  try {
    const res = await request.get('/materials/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.category_id = null
  filterForm.status = ''
  filterForm.low_stock = false
  loadData()
}

// 打开对话框
const openDialog = (row = null) => {
  dialog.isEdit = !!row
  dialog.visible = true
  activeTab.value = 'basic'

  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, {
      id: null,
      sku_code: '',
      name: '',
      category_id: null,
      brand: '',
      model: '',
      specification: '',
      material: '',
      origin: '',
      main_image: '',
      images: [],
      cost_price: 0,
      sale_price: 0,
      market_price: null,
      unit: '件',
      calc_type: 'quantity',
      stock_quantity: 0,
      stock_warning: 10,
      customization_rules: [],
      has_variants: false,
      variant_options: [],
      has_craft_parts: false,
      craft_parts: [],
      description: '',
      tags: [],
      status: 'active'
    })
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  dialog.loading = true
  try {
    if (dialog.isEdit) {
      await request.put(`/materials/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/materials', form)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    dialog.loading = false
  }
}

// 更多操作
const handleCommand = async (command, row) => {
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除该物料吗？', '提示', { type: 'warning' })
      await request.delete(`/materials/${row.id}`)
      ElMessage.success('删除成功')
      loadData()
      loadStats()
    } catch (error) {
      if (error !== 'cancel') ElMessage.error('删除失败')
    }
  } else if (command === 'copy') {
    const copyData = { ...row, id: null, sku_code: '', name: row.name + ' (复制)' }
    openDialog(copyData)
  } else if (command === 'preview') {
    // 在新窗口打开产品详情页
    window.open(`/#/products/${row.id}`, '_blank')
  } else if (command === 'publish') {
    // 上架
    try {
      await request.put(`/materials/${row.id}`, { status: 'active' })
      ElMessage.success('已上架到产品中心')
      loadData()
    } catch (error) {
      ElMessage.error('上架失败')
    }
  } else if (command === 'unpublish') {
    // 下架
    try {
      await request.put(`/materials/${row.id}`, { status: 'inactive' })
      ElMessage.success('已下架')
      loadData()
    } catch (error) {
      ElMessage.error('下架失败')
    }
  }
}

// 图片上传
const handleImageSuccess = (res) => {
  if (res) {
    form.main_image = res.file_url || res.url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return false
  }
  return true
}

// 定制规则
const addRule = () => {
  if (!form.customization_rules) form.customization_rules = []
  form.customization_rules.push({
    type: 'coefficient',
    name: '',
    field: '',
    default: 0
  })
}

const removeRule = (index) => {
  form.customization_rules.splice(index, 1)
}

// 变体选项
const addVariantOption = () => {
  if (!form.variant_options) form.variant_options = []
  form.variant_options.push({ name: '', values: [] })
}

const removeVariantOption = (index) => {
  form.variant_options.splice(index, 1)
}

// 变体管理
const openVariantDialog = (row) => {
  variantDialog.skuId = row.id
  variantDialog.variants = row.variants || []
  variantDialog.visible = true
}

const generateVariants = () => {
  // 根据选项组合生成变体
  const options = form.variant_options || []
  if (options.length === 0) {
    ElMessage.warning('请先定义变体选项')
    return
  }

  // 笛卡尔积生成变体
  const cartesian = (arrays) => {
    return arrays.reduce((a, b) =>
      a.flatMap(d => b.values.map(e => ({ ...d, [b.name]: e }))),
      [{}]
    )
  }

  const combinations = cartesian(options)
  variantDialog.variants = combinations.map((combo, idx) => ({
    id: null,
    variant_code: `V${String(idx + 1).padStart(3, '0')}`,
    variant_name: Object.values(combo).join(' / '),
    variant_values: combo,
    price_adjustment: 0,
    stock_quantity: 0
  }))
}

const addCustomVariant = () => {
  variantDialog.variants.push({
    id: null,
    variant_code: '',
    variant_name: '',
    variant_values: {},
    price_adjustment: 0,
    stock_quantity: 0
  })
}

const removeVariant = (index) => {
  variantDialog.variants.splice(index, 1)
}

const saveVariants = async () => {
  try {
    await request.put(`/materials/${variantDialog.skuId}`, {
      variants: variantDialog.variants
    })
    ElMessage.success('保存成功')
    variantDialog.visible = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 辅助函数
const calcTypeLabel = (type) => {
  const found = options.calc_types.find(t => t.value === type)
  return found ? `${found.label}(${found.unit})` : type
}

const getStatusType = (status) => {
  const found = options.sku_status.find(s => s.value === status)
  return found?.type || 'info'
}

const getStatusLabel = (status) => {
  const found = options.sku_status.find(s => s.value === status)
  return found?.label || status
}

onMounted(() => {
  loadData()
  loadCategories()
  loadStats()
  loadOptions()
})
</script>

<style scoped>
.material-manage {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  color: #8c8c8c;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 16px;
}

/* 分类筛选按钮样式 */
.category-filter-card {
  margin-bottom: 16px;
}

.category-filter-card :deep(.el-card__body) {
  padding: 16px;
}

.category-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.category-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 100px;
  padding: 12px 20px;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.category-btn:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}

.category-btn.active {
  background: #1890ff;
  color: #fff;
}

.category-btn.active .category-count {
  color: rgba(255, 255, 255, 0.85);
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.category-count {
  font-size: 12px;
  color: #8c8c8c;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.material-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.material-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}

.material-detail {
  flex: 1;
}

.material-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.material-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}

.brand {
  font-size: 12px;
  color: #8c8c8c;
}

.material-spec {
  font-size: 12px;
  color: #bfbfbf;
}

.price-section {
  text-align: right;
}

.sale-price {
  font-size: 16px;
  font-weight: 600;
  color: #f5222d;
}

.unit {
  font-size: 12px;
  color: #8c8c8c;
}

.stock-section {
  text-align: center;
}

.stock-value {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.stock-value.low-stock {
  color: #fa8c16;
}

.stock-warning {
  font-size: 12px;
  color: #fa8c16;
}

.expand-content {
  padding: 16px;
  background: #fafafa;
}

.rules-section {
  margin-top: 12px;
}

.section-title {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.rule-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 表单样式 */
.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 120px;
  height: 120px;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c8c8c;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 120px;
  height: 120px;
  object-fit: cover;
}

.rules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rule-item {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.rule-extra {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sep {
  color: #8c8c8c;
}

.variant-options {
  margin-top: 16px;
}

.option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.variant-tag {
  margin-right: 4px;
}

.variant-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.text-muted {
  color: #bfbfbf;
}
</style>
