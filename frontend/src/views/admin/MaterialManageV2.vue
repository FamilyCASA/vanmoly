<template>
  <div class="material-manage-v2">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>物料管理 V2</h2>
      <div class="header-actions">
        <el-button type="success" @click="openPublicDialog">
          <el-icon><Grid /></el-icon>前台展示选择
        </el-button>
        <el-button type="primary" @click="openEditDialog()">
          <el-icon><Plus /></el-icon>新增物料
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>下载模板
        </el-button>
        <el-button type="success" @click="openImportDialog">
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索物料名称/编码" clearable />
        </el-col>
        <el-col :span="5">
          <el-cascader
            v-model="filters.category"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true }"
            placeholder="选择分类"
            clearable
            style="width: 100%"
          />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.brand" placeholder="选择品牌" clearable style="width: 100%">
            <el-option v-for="b in brands" :key="b" :label="b" :value="b" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 100%">
            <el-option label="在售" value="active" />
            <el-option label="草稿" value="draft" />
            <el-option label="停售" value="discontinued" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 物料表格 -->
    <el-card>
      <el-table :data="materials" v-loading="loading" stripe>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <h4>变体列表</h4>
              <el-table :data="row.variants || []" size="small" border>
                <el-table-column prop="variant_name" label="变体名称" />
                <el-table-column prop="variant_values" label="属性">
                  <template #default="{ row: v }">
                    <el-tag v-for="(val, key) in v.variant_values" :key="key" size="small" style="margin-right: 5px">
                      {{ key }}: {{ val }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="price_adjustment" label="价格调整" width="100">
                  <template #default="{ row: v }">
                    {{ v.price_adjustment > 0 ? '+' : '' }}{{ v.price_adjustment }}
                  </template>
                </el-table-column>
                <el-table-column prop="stock_quantity" label="库存" width="80" />
                <el-table-column label="图片" width="80">
                  <template #default="{ row: v }">
                    <el-image v-if="v.image" :src="v.image" style="width: 40px; height: 40px" fit="cover" />
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="sku_code" label="SKU编码" width="120" />
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <el-image :src="getImageUrl(row.main_image)" style="width: 50px; height: 50px" fit="cover" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="物料名称" min-width="200" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column label="价格" width="150">
          <template #default="{ row }">
            <div>销售: ¥{{ row.sale_price }}</div>
            <div class="cost-price">成本: ¥{{ row.cost_price }}</div>
          </template>
        </el-table-column>
        <el-table-column label="变体" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.has_variants" type="success" size="small">{{ row.variants?.length || 0 }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="前台展示" width="90" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_public"
              @change="handlePublicChange(row)"
              active-text="是"
              inactive-text="否"
              inline-prompt
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="primary" link @click="openVariantDialog(row)">变体</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialog.visible"
      :title="editDialog.isEdit ? '编辑物料' : '新增物料'"
      width="900px"
      destroy-on-close
    >
      <el-tabs v-model="editDialog.activeTab">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="editDialog.form" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="SKU编码" required>
                  <el-input v-model="editDialog.form.sku_code" placeholder="如: SKU-001" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物料名称" required>
                  <el-input v-model="editDialog.form.name" placeholder="物料名称" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="分类" required>
              <el-cascader
                v-model="editDialog.form.category_id"
                :options="categoryOptions"
                :props="{ value: 'id', label: 'name', children: 'children', emitPath: false }"
                placeholder="选择分类"
                style="width: 100%"
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="品牌">
                  <el-input v-model="editDialog.form.brand" placeholder="品牌" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="型号">
                  <el-input v-model="editDialog.form.model" placeholder="型号" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="单位">
                  <el-select v-model="editDialog.form.unit" style="width: 100%">
                    <el-option label="件" value="件" />
                    <el-option label="套" value="套" />
                    <el-option label="米" value="米" />
                    <el-option label="平方米" value="平方米" />
                    <el-option label="立方米" value="立方米" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="销售价" required>
                  <el-input-number v-model="editDialog.form.sale_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="成本价">
                  <el-input-number v-model="editDialog.form.cost_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="市场价">
                  <el-input-number v-model="editDialog.form.market_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="规格参数">
              <el-input v-model="editDialog.form.specification" placeholder="如: 2000*900*500mm" />
            </el-form-item>

            <el-form-item label="材质">
              <el-input v-model="editDialog.form.material" placeholder="如: 橡木实木+环保漆" />
            </el-form-item>

            <el-form-item label="简短描述">
              <el-input v-model="editDialog.form.description" type="textarea" :rows="2" placeholder="简短描述，显示在列表中" />
            </el-form-item>

            <el-form-item label="前台展示">
              <el-switch v-model="editDialog.form.is_public" active-text="展示" inactive-text="隐藏" />
              <span class="form-tip" style="margin-left: 10px; color: #909399">是否在前台产品中心展示该物料</span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 图片管理 -->
        <el-tab-pane label="图片管理" name="images">
          <el-form label-width="100px">
            <el-form-item label="主图">
              <ImageCropperUpload
                v-model="editDialog.form.main_image"
                placeholder="上传物料主图"
                :crop-enabled="true"
              />
              <div class="upload-tip">建议尺寸 800x800px，支持 JPG/PNG，可裁剪；或直接输入视频链接</div>
            </el-form-item>

            <el-form-item label="辅图">
              <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                list-type="picture-card"
                :file-list="auxImagesList"
                :on-success="handleAuxImageSuccess"
                :on-remove="handleAuxImageRemove"
                multiple
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">实景图、场景图，最多9张</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 富文本详情 -->
        <el-tab-pane label="详情编辑" name="detail">
          <el-form label-width="80px">
            <el-form-item label="详情内容">
              <div class="editor-toolbar">
                <el-button-group>
                  <el-button size="small" @click="insertHtml('<h2>标题</h2>')">H2</el-button>
                  <el-button size="small" @click="insertHtml('<h3>小标题</h3>')">H3</el-button>
                  <el-button size="small" @click="insertHtml('<p>段落</p>')">P</el-button>
                </el-button-group>
                <el-button-group style="margin-left: 10px">
                  <el-button size="small" @click="insertHtml('<strong>加粗</strong>')">加粗</el-button>
                  <el-button size="small" @click="insertHtml('<em>斜体</em>')">斜体</el-button>
                </el-button-group>
                <el-button-group style="margin-left: 10px">
                  <el-button size="small" @click="insertHtml('<ul><li>列表项</li></ul>')">列表</el-button>
                  <el-button size="small" @click="insertHtml('<table><tr><td>单元格</td></tr></table>')">表格</el-button>
                </el-button-group>
                <el-upload
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :show-file-list="false"
                  :on-success="handleEditorImageSuccess"
                  style="display: inline-block; margin-left: 10px"
                >
                  <el-button size="small" type="primary">插入图片</el-button>
                </el-upload>
              </div>
              <el-input
                v-model="editDialog.form.detail_content"
                type="textarea"
                :rows="20"
                placeholder="在此编辑富文本详情内容..."
                class="html-editor"
              />
            </el-form-item>
            <el-form-item label="预览">
              <div class="detail-preview" v-html="editDialog.form.detail_content || '<p style=\'color: #999\'>暂无内容</p>'"></div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 变体设置 -->
        <el-tab-pane label="变体设置" name="variants">
          <el-form label-width="100px">
            <el-form-item label="启用变体">
              <el-switch v-model="editDialog.form.has_variants" />
            </el-form-item>
            
            <template v-if="editDialog.form.has_variants">
              <el-form-item label="变体选项">
                <div v-for="(opt, idx) in variantOptions" :key="idx" class="variant-option-row">
                  <el-input v-model="opt.name" placeholder="选项名，如: 颜色" style="width: 150px" />
                  <el-select
                    v-model="opt.values"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入选项值"
                    style="width: 300px; margin-left: 10px"
                  />
                  <el-button type="danger" link @click="removeVariantOption(idx)" style="margin-left: 10px">删除</el-button>
                </div>
                <el-button type="primary" link @click="addVariantOption" style="margin-top: 10px">
                  <el-icon><Plus /></el-icon>添加选项
                </el-button>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="generateVariants">生成变体组合</el-button>
              </el-form-item>

              <el-form-item label="变体列表">
                <el-table :data="editDialog.form.variants || []" border size="small">
                  <el-table-column prop="variant_name" label="变体名称" />
                  <el-table-column label="属性">
                    <template #default="{ row }">
                      <el-tag v-for="(val, key) in row.variant_values" :key="key" size="small" style="margin-right: 5px">
                        {{ key }}: {{ val }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="图片" width="120">
                    <template #default="{ row, $index }">
                      <el-upload
                        :action="uploadUrl"
                        :headers="uploadHeaders"
                        :show-file-list="false"
                        :on-success="(res) => handleVariantImageSuccess(res, $index)"
                        style="display: inline-block"
                      >
                        <img v-if="row.image" :src="row.image" style="width: 50px; height: 50px; object-fit: cover" />
                        <el-button v-else size="small">上传</el-button>
                      </el-upload>
                    </template>
                  </el-table-column>
                  <el-table-column label="价格调整" width="150">
                    <template #default="{ row, $index }">
                      <el-input-number v-model="row.price_adjustment" :precision="2" style="width: 120px" />
                    </template>
                  </el-table-column>
                  <el-table-column label="库存" width="120">
                    <template #default="{ row, $index }">
                      <el-input-number v-model="row.stock_quantity" :min="0" style="width: 100px" />
                    </template>
                  </el-table-column>
                </el-table>
              </el-form-item>
            </template>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="editDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="editDialog.saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 变体管理对话框 -->
    <el-dialog v-model="variantDialog.visible" title="变体管理" width="800px">
      <el-table :data="variantDialog.variants" border>
        <el-table-column prop="variant_name" label="变体名称" />
        <el-table-column label="属性">
          <template #default="{ row }">
            <el-tag v-for="(val, key) in row.variant_values" :key="key" size="small" style="margin-right: 5px">
              {{ key }}: {{ val }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="图片" width="120">
          <template #default="{ row, $index }">
            <el-upload
              :action="uploadUrl"
              :headers="uploadHeaders"
              :show-file-list="false"
              :on-success="(res) => handleVariantDialogImageSuccess(res, $index)"
            >
              <img v-if="row.image" :src="row.image" style="width: 50px; height: 50px; object-fit: cover" />
              <el-button v-else size="small">上传</el-button>
            </el-upload>
          </template>
        </el-table-column>
        <el-table-column label="价格调整" width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.price_adjustment" :precision="2" style="width: 120px" @change="updateVariant(row)" />
          </template>
        </el-table-column>
        <el-table-column label="库存" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.stock_quantity" :min="0" style="width: 100px" @change="updateVariant(row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 前台展示选择对话框 -->
    <el-dialog v-model="publicDialog.visible" title="前台展示选择" width="900px">
      <div class="public-dialog-content">
        <el-alert
          title="选择要在前台产品中心展示的物料分类和品牌"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />
        
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="12">
            <h4>选择分类</h4>
            <el-tree
              ref="categoryTreeRef"
              :data="categoryOptions"
              :props="{ value: 'id', label: 'name', children: 'children' }"
              show-checkbox
              node-key="id"
              :default-checked-keys="publicDialog.checkedCategories"
              @check="handleCategoryCheck"
            />
          </el-col>
          <el-col :span="12">
            <h4>选择品牌</h4>
            <el-checkbox-group v-model="publicDialog.checkedBrands">
              <el-checkbox v-for="brand in brands" :key="brand" :label="brand" border>{{ brand }}</el-checkbox>
            </el-checkbox-group>
          </el-col>
        </el-row>

        <el-divider />

        <el-row :gutter="20">
          <el-col :span="12">
            <h4>当前已前台展示</h4>
            <div class="public-stats">
              <el-statistic title="分类数" :value="publicDialog.existingCategories.length" />
              <el-statistic title="品牌数" :value="publicDialog.existingBrands.length" />
              <el-statistic title="物料数" :value="publicDialog.existingCount" />
            </div>
          </el-col>
          <el-col :span="12">
            <h4>快捷操作</h4>
            <el-button size="small" @click="selectAllPublic">全选</el-button>
            <el-button size="small" @click="deselectAllPublic">取消全选</el-button>
            <el-button size="small" type="success" @click="invertSelection">反选</el-button>
            <el-button size="small" type="danger" @click="clearAllPublic">清空前台展示</el-button>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="publicDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="savePublicSelection" :loading="publicDialog.saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Grid } from '@element-plus/icons-vue'
import request from '@/api/request'
import ImageCropperUpload from '@/components/ImageCropperUpload.vue'

// 统计数据
const stats = ref([
  { label: '物料总数', value: 0 },
  { label: '在售物料', value: 0 },
  { label: '库存预警', value: 0 },
  { label: '今日新增', value: 0 }
])

// 筛选条件
const filters = reactive({
  keyword: '',
  category: null,
  brand: '',
  status: ''
})

// 数据列表
const materials = ref([])
const loading = ref(false)
const importDialogVisible = ref(false)
const importing = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 分类和品牌选项
const categoryOptions = ref([])
const brands = ref([])

// 上传配置
const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 编辑对话框
const editDialog = reactive({
  visible: false,
  isEdit: false,
  activeTab: 'basic',
  saving: false,
  form: {
    sku_code: '',
    name: '',
    category_id: null,
    brand: '',
    model: '',
    unit: '件',
    sale_price: 0,
    cost_price: 0,
    market_price: 0,
    specification: '',
    material: '',
    description: '',
    detail_content: '',
    main_image: '',
    images: [],
    has_variants: false,
    variant_options: [],
    variants: []
  }
})

// 变体选项编辑
const variantOptions = ref([])

// 辅图列表
const getImageUrl = (url) => {
  if (!url) return '/placeholder.png'
  if (url.startsWith('http') || url.startsWith('data:')) return url
  // Vite proxy handles /upload, /static, /uploads — no prefix needed
  return url
}

const auxImagesList = computed({
  get: () => (editDialog.form.images || []).map((url, idx) => ({ name: `img-${idx}`, url: getImageUrl(url) })),
  set: (val) => { editDialog.form.images = val.map(v => v.url || v.response?.url) }
})

// 变体对话框
const variantDialog = reactive({
  visible: false,
  skuId: null,
  variants: []
})

// 前台展示选择对话框
const publicDialog = reactive({
  visible: false,
  loading: false,
  saving: false,
  checkedCategories: [],
  checkedBrands: [],
  existingCategories: [],
  existingBrands: [],
  existingCount: 0
})

// 分类树引用
const categoryTreeRef = ref(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/materials', {
      params: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        keyword: filters.keyword,
        category_id: filters.category,
        brand: filters.brand,
        status: filters.status
      }
    })
    materials.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await request.get('/materials/stats')
    stats.value = [
      { label: '物料总数', value: res.total || 0 },
      { label: '在售物料', value: res.active || 0 },
      { label: '库存预警', value: res.warning || 0 },
      { label: '今日新增', value: res.today || 0 }
    ]
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 加载分类
const loadCategories = async () => {
  try {
    const res = await request.get('/materials/categories')
    categoryOptions.value = res || []
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

// 加载品牌
const loadBrands = async () => {
  try {
    const res = await request.get('/materials/brands')
    brands.value = res || []
  } catch (error) {
    console.error('加载品牌失败', error)
  }
}

// 打开编辑对话框
const openEditDialog = (row = null) => {
  editDialog.isEdit = !!row
  editDialog.activeTab = 'basic'
  if (row) {
    editDialog.form = { ...row, variants: row.variants || [] }
    variantOptions.value = row.variant_options || []
  } else {
    editDialog.form = {
      sku_code: '',
      name: '',
      category_id: null,
      brand: '',
      model: '',
      unit: '件',
      sale_price: 0,
      cost_price: 0,
      market_price: 0,
      specification: '',
      material: '',
      description: '',
      detail_content: '',
      main_image: '',
      images: [],
      has_variants: false,
      variant_options: [],
      variants: [],
      is_public: true
    }
    variantOptions.value = []
  }
  editDialog.visible = true
}

// 打开变体对话框
const openVariantDialog = (row) => {
  variantDialog.skuId = row.id
  variantDialog.variants = row.variants || []
  variantDialog.visible = true
}

// 保存
const stripApiPrefix = (url) => {
  if (!url) return url
  // Remove /api/v3 prefix if present (shouldn't be, but just in case)
  return url.replace(/^\/api\/v3/, '')
}

const handleSave = async () => {
  editDialog.saving = true
  try {
    const data = {
      ...editDialog.form,
      images: (editDialog.form.images || []).map(stripApiPrefix),
      main_image: stripApiPrefix(editDialog.form.main_image),
      variant_options: variantOptions.value
    }
    if (editDialog.isEdit) {
      await request.put(`/materials/${editDialog.form.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/materials', data)
      ElMessage.success('创建成功')
    }
    editDialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    editDialog.saving = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该物料吗？', '提示', { type: 'warning' })
    await request.delete(`/materials/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 前台展示开关切换
const handlePublicChange = async (row) => {
  try {
    await request.put(`/materials/${row.id}`, { is_public: row.is_public })
    ElMessage.success(row.is_public ? '已设为前台展示' : '已取消前台展示')
  } catch (error) {
    ElMessage.error('更新失败')
    row.is_public = !row.is_public // 回滚
  }
}

// 打开前台展示选择对话框
const openPublicDialog = async () => {
  publicDialog.visible = true
  publicDialog.loading = true
  try {
    // 获取当前已前台展示的分类和品牌
    const res = await request.get('/materials/public-config')
    if (res) {
      publicDialog.checkedCategories = res.categories || []
      publicDialog.checkedBrands = res.brands || []
      publicDialog.existingCategories = res.categories || []
      publicDialog.existingBrands = res.brands || []
      publicDialog.existingCount = res.total || 0
    }
  } catch (error) {
    // 如果没有配置，返回空
    publicDialog.checkedCategories = []
    publicDialog.checkedBrands = []
    publicDialog.existingCategories = []
    publicDialog.existingBrands = []
    publicDialog.existingCount = 0
  } finally {
    publicDialog.loading = false
  }
}

// 分类树选择变化
const handleCategoryCheck = (data, checked) => {
  const checkedNodes = categoryTreeRef.value?.getCheckedNodes() || []
  publicDialog.checkedCategories = checkedNodes.map(n => n.id)
}

// 全选
const selectAllPublic = () => {
  const allCategoryIds = []
  const getAllIds = (nodes) => {
    nodes.forEach(n => {
      allCategoryIds.push(n.id)
      if (n.children) getAllIds(n.children)
    })
  }
  getAllIds(categoryOptions.value)
  publicDialog.checkedCategories = allCategoryIds
  publicDialog.checkedBrands = [...brands.value]
}

// 取消全选
const deselectAllPublic = () => {
  publicDialog.checkedCategories = []
  publicDialog.checkedBrands = []
}

// 反选
const invertSelection = () => {
  const allCategoryIds = []
  const getAllIds = (nodes) => {
    nodes.forEach(n => {
      allCategoryIds.push(n.id)
      if (n.children) getAllIds(n.children)
    })
  }
  getAllIds(categoryOptions.value)
  
  publicDialog.checkedCategories = allCategoryIds.filter(id => !publicDialog.checkedCategories.includes(id))
  publicDialog.checkedBrands = brands.value.filter(b => !publicDialog.checkedBrands.includes(b))
}

// 清空前台展示
const clearAllPublic = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有前台展示吗？', '警告', {
      type: 'warning'
    })
    publicDialog.checkedCategories = []
    publicDialog.checkedBrands = []
    await savePublicSelection()
  } catch (error) {
    // 用户取消
  }
}

// 保存前台展示选择
const savePublicSelection = async () => {
  publicDialog.saving = true
  try {
    await request.post('/materials/public-config', {
      categories: publicDialog.checkedCategories,
      brands: publicDialog.checkedBrands
    })
    ElMessage.success('保存成功')
    publicDialog.visible = false
    // 刷新列表
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    publicDialog.saving = false
  }
}

// 图片上传成功
const handleMainImageSuccess = (res) => {
  // el-upload doesn't go through axios interceptor, res is raw {code, data:{file_url}}
  let url = res?.data?.file_url || res?.file_url || res.url
  if (url) {
    editDialog.form.main_image = url
  }
}

const handleAuxImageSuccess = (res, file) => {
  // el-upload doesn't go through axios interceptor, res is raw {code, data:{file_url}}
  let url = res?.data?.file_url || res?.file_url || res.url
  if (url) {
    editDialog.form.images = [...(editDialog.form.images || []), url]
  }
}

const handleAuxImageRemove = (file) => {
  // file.response 是 el-upload 原始响应
  let url = file.response?.data?.file_url || file.response?.file_url || file.url
  // 补全 /api/v3 前缀
  if (url && !url.startsWith('http') && !url.startsWith('/api')) {
    url = '/api/v3' + url
  }
  editDialog.form.images = (editDialog.form.images || []).filter(u => u !== url)
}

// 编辑器插入图片
const handleEditorImageSuccess = (res) => {
  // el-upload 不经过 axios 拦截器
  let url = res?.data?.file_url || res?.file_url || res.url
  // 补全 /api/v3 前缀
  if (url && !url.startsWith('http') && !url.startsWith('/api')) {
    url = '/api/v3' + url
  }
  if (url) {
    insertHtml(`<img src="${url}" style="max-width:100%" />`)
  }
}

// 插入HTML
const insertHtml = (html) => {
  const content = editDialog.form.detail_content || ''
  editDialog.form.detail_content = content + '\n' + html
}

// 变体选项操作
const addVariantOption = () => {
  variantOptions.value.push({ name: '', values: [] })
}

const removeVariantOption = (idx) => {
  variantOptions.value.splice(idx, 1)
}

// 生成变体组合
const generateVariants = () => {
  const options = variantOptions.value.filter(o => o.name && o.values.length > 0)
  if (options.length === 0) {
    ElMessage.warning('请至少设置一个变体选项')
    return
  }

  // 生成笛卡尔积
  const cartesian = (arrays) => {
    return arrays.reduce((a, b) => a.flatMap(d => b.map(e => ({ ...d, [b.name]: e }))), [{}])
  }

  const combinations = cartesian(options.map(o => o.values.map(v => ({ [o.name]: v }))))
  
  editDialog.form.variants = combinations.map((combo, idx) => ({
    variant_code: `${editDialog.form.sku_code}-${String(idx + 1).padStart(3, '0')}`,
    variant_name: Object.values(combo).join(' / '),
    variant_values: combo,
    image: '',
    price_adjustment: 0,
    stock_quantity: 0,
    is_enabled: true
  }))

  ElMessage.success(`已生成 ${editDialog.form.variants.length} 个变体`)
}

// 变体图片上传
const handleVariantImageSuccess = (res, idx) => {
  // el-upload 不经过 axios 拦截器
  let url = res?.data?.file_url || res?.file_url || res.url
  // 补全 /api/v3 前缀
  if (url && !url.startsWith('http') && !url.startsWith('/api')) {
    url = '/api/v3' + url
  }
  if (url && editDialog.form.variants[idx]) {
    editDialog.form.variants[idx].image = url
  }
}

const handleVariantDialogImageSuccess = (res, idx) => {
  // el-upload 不经过 axios 拦截器
  let url = res?.data?.file_url || res?.file_url || res.url
  // 补全 /api/v3 前缀
  if (url && !url.startsWith('http') && !url.startsWith('/api')) {
    url = '/api/v3' + url
  }
  if (url && variantDialog.variants[idx]) {
    variantDialog.variants[idx].image = url
    updateVariant(variantDialog.variants[idx])
  }
}

// 更新变体
const updateVariant = async (variant) => {
  try {
    await request.put(`/materials/variants/${variant.id}`, variant)
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 状态显示
const getStatusType = (status) => {
  const map = { active: 'success', draft: 'info', discontinued: 'danger' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { active: '在售', draft: '草稿', discontinued: '停售' }
  return map[status] || status
}

onMounted(() => {
  loadData()
  loadStats()
  loadCategories()
  loadBrands()
})
</script>

<style scoped>
.material-manage-v2 {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #8B5A2B;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.filter-card {
  margin-bottom: 20px;
}

.cost-price {
  color: #909399;
  font-size: 12px;
}

.expand-content {
  padding: 10px 20px;
  background: #f5f7fa;
}

.expand-content h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

/* 上传样式 */
.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 150px;
  height: 150px;
}

.avatar-uploader:hover {
  border-color: #8B5A2B;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 150px;
  text-align: center;
  line-height: 150px;
}

.avatar {
  width: 150px;
  height: 150px;
  display: block;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

/* 编辑器样式 */
.editor-toolbar {
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.html-editor {
  font-family: 'Courier New', monospace;
}

.detail-preview {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  min-height: 200px;
  background: #fff;
}

.detail-preview :deep(img) {
  max-width: 100%;
  height: auto;
}

.detail-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.detail-preview :deep(th), .detail-preview :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px;
  text-align: left;
}

/* 变体选项 */
.variant-option-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* 前台展示选择 */
.public-dialog-content {
  min-height: 400px;
}

.public-stats {
  display: flex;
  gap: 20px;
}

.public-dialog-content h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}

.public-dialog-content .el-checkbox {
  margin-right: 10px;
  margin-bottom: 10px;
}
</style>
