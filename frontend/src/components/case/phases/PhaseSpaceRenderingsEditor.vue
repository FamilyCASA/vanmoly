<template>
  <div class="phase-space-renderings-editor">
    <!-- 报价表引用提示 -->
    <div v-if="!quoteId" class="quote-tip">
      <el-alert
        title="提示：关联报价表后，空间名称可从报价表引用"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 空间列表 -->
    <div class="spaces-list">
      <div
        v-for="(space, idx) in spaces"
        :key="space.id || idx"
        class="space-block"
      >
        <div class="space-header">
          <el-select
            v-model="space.space_name"
            placeholder="选择或输入空间名称（支持自定义）"
            filterable
            allow-create
            default-first-option
            style="width: 240px"
            @change="saveSpaceName(idx)"
          >
            <el-option
              v-for="name in availableSpaceNames"
              :key="name"
              :label="name"
              :value="name"
            />
          </el-select>
          <div class="space-actions">
            <!-- 批量上传按钮 -->
            <el-button type="success" size="small" @click="triggerBatchUpload(idx)">
              <el-icon><Upload /></el-icon> 批量上传图片
            </el-button>
            <el-button type="warning" size="small" @click="openMaterialConfig(space)">
              <el-icon><Setting /></el-icon> 物料配置
            </el-button>
            <el-button type="danger" size="small" link @click="removeSpace(idx)">
              删除空间
            </el-button>
          </div>
        </div>

        <!-- 效果图列表 -->
        <div class="renderings-grid">
          <div
            v-for="(item, i) in space.renderings"
            :key="item.id || i"
            class="rendering-card"
          >
            <div class="rendering-image">
              <img v-if="item.image_url" :src="item.image_url" />
              <div v-else class="upload-placeholder" @click="triggerSingleUpload(idx, i)">
                <el-icon><Plus /></el-icon>
                <span>点击上传</span>
              </div>
              <div v-if="item.image_url" class="img-overlay">
                <el-button size="small" @click="triggerSingleUpload(idx, i)">替换</el-button>
                <el-button type="danger" size="small" @click="removeRendering(idx, i)">删除</el-button>
              </div>
              <div v-if="item.uploading" class="uploading-mask">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>上传中...</span>
              </div>
            </div>
            <div class="rendering-info">
              <div style="display: flex; gap: 6px; margin-bottom: 8px">
                <el-input
                  v-model="item.title"
                  placeholder="效果图标题"
                  size="small"
                  style="flex: 1"
                />
                <el-button
                  size="small"
                  type="primary"
                  :loading="item.saving"
                  @click="saveRendering(idx, i, item)"
                >保存</el-button>
              </div>
              <div class="rich-label">简介文案（富文本）</div>
              <RichTextEditor
                v-model="item.description"
                placeholder="请输入效果图的详细介绍..."
              />
              <el-button
                size="small"
                type="success"
                :loading="item.saving"
                :disabled="item.saving"
                @click="saveRendering(idx, i, item)"
                style="margin-top: 8px; width: 100%"
              >
                <span v-if="item.saving">保存中...</span>
                <span v-else>💾 保存简介文案</span>
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加空间按钮 -->
    <el-button type="primary" @click="addSpace" style="margin-top: 16px">
      + 添加空间
    </el-button>

    <!-- 隐藏的上传组件 - 单张 -->
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :show-file-list="false"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :before-upload="beforeUpload"
      accept="image/*"
      style="display: none;"
    />

    <!-- 隐藏的上传组件 - 批量 -->
    <el-upload
      ref="batchUploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :show-file-list="false"
      :multiple="true"
      :on-success="handleBatchSuccess"
      :on-error="handleBatchError"
      :before-upload="beforeBatchUpload"
      accept="image/*"
      style="display: none;"
    />

    <!-- 物料配置弹窗 -->
    <el-dialog
      v-model="materialDialogVisible"
      :title="'物料配置 — ' + (currentMaterialSpace?.space_name || '')"
      width="92%"
      top="3vh"
      destroy-on-close
      append-to-body
    >
      <div class="material-config-body">
        <div class="mat-toolbar">
          <span class="mat-toolbar-hint">配置该空间的物料清单，将在幻灯片中以表格形式展示</span>
          <el-button type="primary" size="small" @click="addMatRow">+ 添加行</el-button>
        </div>
        <div class="config-table-wrapper">
          <table class="config-table">
            <thead>
              <tr>
                <th>名称</th><th>一级分类</th><th>二级分类</th><th>物料</th>
                <th>规格</th><th>宽mm</th><th>深mm</th><th>高mm</th>
                <th>计量</th><th>数量</th><th>单价</th><th>金额</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIdx) in matRows" :key="rIdx">
                <td><input v-model="row.name" placeholder="自定义名称" class="cfg-input" /></td>
                <td>
                  <select v-model="row.cat1Id" class="cfg-select" @change="onCat1Change(rIdx)">
                    <option value="">一级分类</option>
                    <option v-for="c in l1Categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </td>
                <td>
                  <select v-model="row.cat2Id" class="cfg-select" :disabled="!row.cat1Id" @change="onCat2Change(rIdx)">
                    <option value="">二级分类</option>
                    <option v-for="c in getL2Categories(row.cat1Id)" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </td>
                <td>
                  <el-select
                    v-model="row.material_id"
                    filterable
                    clearable
                    placeholder="输入关键字搜索物料"
                    :filter-method="(q) => onMatFilter(rIdx, q)"
                    @visible-change="(visible) => { if(visible) onMatFilter(rIdx, '') }"
                    @change="onMatSelect(rIdx)"
                    style="width:100%"
                  >
                    <el-option
                      v-for="m in getFilteredSKUs(row)"
                      :key="m.id"
                      :label="m.name + (m.sku_code ? ' ['+m.sku_code+']' : '')"
                      :value="m.id"
                    >
                      <span style="font-weight:500">{{ m.name }}</span>
                      <span style="color:#999;font-size:11px;margin-left:6px">{{ m.sku_code || '' }} {{ m.brand || '' }}</span>
                    </el-option>
                  </el-select>
                </td>
                <td><input v-model="row.spec" readonly class="cfg-input" /></td>
                <td><input v-model.number="row.width" type="number" class="cfg-input" @input="recalcMatRow(rIdx)" /></td>
                <td><input v-model.number="row.depth" type="number" class="cfg-input" @input="recalcMatRow(rIdx)" /></td>
                <td><input v-model.number="row.height" type="number" class="cfg-input" @input="recalcMatRow(rIdx)" /></td>
                <td class="cfg-calc">{{ row.calcVal || '-' }}</td>
                <td><input v-model.number="row.quantity" type="number" class="cfg-input" min="1" @input="recalcMatRow(rIdx)" /></td>
                <td><input v-model.number="row.price" type="number" step="0.01" class="cfg-input" @input="recalcMatRow(rIdx)" /></td>
                <td class="cfg-amount">{{ row.amount?.toFixed(2) || '0.00' }}</td>
                <td class="cfg-actions">
                  <button class="cfg-btn-clone" @click="cloneMatRow(rIdx)" title="克隆">📋</button>
                  <button class="cfg-btn-delete" @click="removeMatRow(rIdx)" title="删除">🗑</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <template #footer>
        <el-button @click="materialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMaterialConfig" :loading="matSaving">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading, Upload, Setting } from '@element-plus/icons-vue'
import request from '@/utils/request'
import RichTextEditor from '@/components/RichTextEditor.vue'

const props = defineProps({
  caseId: {
    type: Number,
    required: true
  },
  quoteId: {
    type: Number,
    default: null
  }
})

const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const batchUploadRef = ref(null)
const spaces = ref([])

// 当前上传位置
const uploadPosition = ref({ spaceIdx: 0, renderingIdx: 0 })
// 当前批量上传的空间索引
const batchSpaceIdx = ref(0)

// 更丰富的空间名称列表
const availableSpaceNames = ref([
  '客厅', '餐厅', '主卧', '次卧', '客房', '儿童房', '老人房', '书房',
  '厨房', '主卫', '次卫', '公卫', '阳台', '生活阳台', '景观阳台',
  '玄关', '过道', '门厅', '楼梯间', '电梯厅',
  '储物间', '衣帽间', '杂物间', '设备间',
  '影音室', '健身房', '茶室', '棋牌室', '酒窖', '保姆间', '车库',
  '办公室', '会议室', '接待区', '展示区', '前台'
])

// ==================== 数据加载 ====================

const loadSpaces = async () => {
  try {
    const res = await request.get('/cases/' + props.caseId + '/spaces')
    if (res && Array.isArray(res)) {
      spaces.value = res.map(s => ({
        ...s,
        renderings: s.renderings || []
      }))
    }
  } catch (e) {
    console.error('Load spaces failed:', e)
  }
}

const loadQuoteSpaceNames = async () => {
  if (!props.quoteId) return
  try {
    const res = await request.get('/quotes/' + props.quoteId + '/space-names')
    if (res && Array.isArray(res)) {
      const merged = [...new Set([...res, ...availableSpaceNames.value])]
      availableSpaceNames.value = merged
    }
  } catch (e) {
    console.error('Load quote space names failed:', e)
  }
}

// ==================== 空间操作 ====================

const addSpace = async () => {
  try {
    const res = await request.post('/cases/' + props.caseId + '/spaces', {
      space_name: '新空间'
    })
    if (res) {
      spaces.value.push({
        ...res,
        renderings: []
      })
      ElMessage.success('空间已添加')
    }
  } catch (e) {
    console.error('Add space failed:', e)
    ElMessage.error('添加失败：' + (e.response?.data?.message || e.message))
  }
}

const removeSpace = async (idx) => {
  const space = spaces.value[idx]
  if (!space.id) {
    spaces.value.splice(idx, 1)
    return
  }
  try {
    // API路径修复: /spaces/{id}
    await request.delete('/spaces/' + space.id)
    spaces.value.splice(idx, 1)
    ElMessage.success('空间已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const saveSpaceName = async (idx) => {
  const space = spaces.value[idx]
  if (!space.id) return
  try {
    await request.put('/spaces/' + space.id, {
      space_name: space.space_name
    })
  } catch (e) {
    console.error('Save space name failed:', e)
  }
}

// ==================== 效果图操作 ====================

const addRendering = async (spaceIdx) => {
  const space = spaces.value[spaceIdx]
  if (!space.id) {
    ElMessage.warning('请先保存空间')
    return
  }

  try {
    // API路径修复: /spaces/{id}/renderings
    const res = await request.post('/spaces/' + space.id + '/renderings', {
      image_url: '',
      title: '',
      description: ''
    })
    if (res) {
      if (!space.renderings) {
        space.renderings = []
      }
      space.renderings.push(res)
      ElMessage.success('效果图已添加，可点击图片区域上传')
    }
  } catch (e) {
    console.error('Add rendering failed:', e)
    ElMessage.error('添加效果图失败：' + (e.response?.data?.message || e.message))
  }
}

const removeRendering = async (spaceIdx, renderingIdx) => {
  const space = spaces.value[spaceIdx]
  const item = space.renderings[renderingIdx]

  if (!item.id) {
    space.renderings.splice(renderingIdx, 1)
    return
  }

  try {
    // API路径修复: /renderings/{id}
    await request.delete('/renderings/' + item.id)
    space.renderings.splice(renderingIdx, 1)
    ElMessage.success('效果图已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const saveRendering = async (spaceIdx, renderingIdx, item) => {
  if (!item.id) return
  item.saving = true
  try {
    // API路径: /renderings/{id}
    const saved = await request.put('/renderings/' + item.id, {
      title: item.title,
      description: item.description
    })
    // 用后端返回数据更新本地，确保 description 正确回填
    if (saved) {
      Object.assign(item, saved)
    }
    ElMessage.success('保存成功')
  } catch (e) {
    console.error('Save rendering failed:', e)
    ElMessage.error('保存失败：' + (e.message || '网络错误'))
  } finally {
    item.saving = false
  }
}

// ==================== 单张上传 ====================

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }

  const sp = uploadPosition.value
  const item = spaces.value[sp.spaceIdx]?.renderings[sp.renderingIdx]
  if (item) {
    item.uploading = true
  }
  return true
}

const triggerSingleUpload = (spaceIdx, renderingIdx) => {
  uploadPosition.value = { spaceIdx, renderingIdx }
  uploadRef.value?.$el?.querySelector('input')?.click()
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const pos = uploadPosition.value
    const item = spaces.value[pos.spaceIdx]?.renderings[pos.renderingIdx]
    if (item) {
      item.image_url = url
      item.uploading = false
      if (item.id) {
        request.put('/renderings/' + item.id, { image_url: url }).catch(e => console.error(e))
      }
    }
    ElMessage.success('图片上传成功')
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const pos = uploadPosition.value
  const item = spaces.value[pos.spaceIdx]?.renderings[pos.renderingIdx]
  if (item) {
    item.uploading = false
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

// ==================== 批量上传 ====================

const triggerBatchUpload = (spaceIdx) => {
  batchSpaceIdx.value = spaceIdx
  batchUploadRef.value?.$el?.querySelector('input')?.click()
}

const beforeBatchUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error(file.name + ' 不是图片，已跳过')
    return false
  }
  return true
}

const handleBatchSuccess = (res, file) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (!url) return

  const space = spaces.value[batchSpaceIdx.value]
  if (!space || !space.id) return

  // 为每张上传的图片自动创建效果图记录
  request.post('/spaces/' + space.id + '/renderings', {
    image_url: url,
    title: file.name.replace(/\.[^/.]+$/, ''),
    description: ''
  }).then(response => {
    if (response) {
      if (!space.renderings) space.renderings = []
      space.renderings.push({
        ...response,
        uploading: false
      })
    }
  }).catch(e => {
    console.error('Create rendering for uploaded image failed:', e)
    ElMessage.error(file.name + ' 创建记录失败')
  })
}

const handleBatchError = (err) => {
  ElMessage.error('部分图片上传失败：' + (err?.message || '未知错误'))
}


// ==================== 物料配置 ====================
const materialDialogVisible = ref(false)
const currentMaterialSpace = ref(null)
const matSearching = ref(false)
const matSaving = ref(false)
const matRows = ref([])
// 分类树 + 物料库（三级筛选：L1分类 → L2分类 → 材质 → SKU列表）
const categoryTree = ref([])  // L1 categories with children
const materialSKUs = ref([])  // flat SKU list

const l1Categories = computed(() => categoryTree.value)

const getL2Categories = (cat1Id) => {
  if (!cat1Id) return []
  const l1 = categoryTree.value.find(c => c.id === cat1Id)
  return l1?.children || []
}

const getMaterialNames = (cat2Id) => {
  if (!cat2Id) return []
  const names = new Set()
  materialSKUs.value
    .filter(m => m.category_id === cat2Id && m.material && m.material !== '-')
    .forEach(m => names.add(m.material))
  return Array.from(names).sort()
}

const getFilteredSKUs = (row) => {
  if (!row.cat2Id) return []
  let list = materialSKUs.value.filter(m => m.category_id === row.cat2Id)
  if (row.material_name) list = list.filter(m => m.material === row.material_name)
  // 按搜索关键词过滤（名称、SKU编码、品牌）
  const kw = (row._searchKeyword || '').trim().toLowerCase()
  if (kw) {
    list = list.filter(m =>
      (m.name || '').toLowerCase().includes(kw) ||
      (m.sku_code || '').toLowerCase().includes(kw) ||
      (m.brand || '').toLowerCase().includes(kw) ||
      (m.material || '').toLowerCase().includes(kw)
    )
  }
  return list
}

const loadMaterialLibrary = async () => {
  if (categoryTree.value.length > 0 && materialSKUs.value.length > 0) return
  try {
    // 并行加载分类树和物料列表
    const [catRes, skuRes] = await Promise.all([
      request.get('/materials/categories'),
      request.get('/materials', { params: { page_size: 2000, is_public: 1 } })
    ])
    // 分类树（拦截器已解包 res.data → 数组）
    categoryTree.value = Array.isArray(catRes) ? catRes : (Array.isArray(catRes?.data) ? catRes.data : [])
    
    // 物料列表（拦截器已解包 → { items, total, ... }）
    const skuItems = Array.isArray(skuRes?.items) ? skuRes.items : (Array.isArray(skuRes) ? skuRes : [])
    materialSKUs.value = skuItems.filter(m => m.status === 'active')
  } catch(e) {
    console.warn('Load material library failed:', e)
  }
}

const openMaterialConfig = async (space) => {
  currentMaterialSpace.value = space
  await loadMaterialLibrary()
  matRows.value = []
  try {
    const res = await request.get('/spaces/' + space.id + '/materials')
    const items = Array.isArray(res) ? res : (res?.data || [])
    if (items.length) {
      matRows.value = items.map(c => {
        // Reverse-lookup category IDs from saved text names
        const l1Cat = (c.category_level1 && categoryTree.value.length)
          ? categoryTree.value.find(ct => ct.name === c.category_level1) : null
        const l2Cat = (l1Cat && c.category_level2)
          ? (l1Cat.children || []).find(ct => ct.name === c.category_level2) : null
        return {
          name: c.material_name || '',
          cat1Id: l1Cat ? l1Cat.id : '',
          cat2Id: l2Cat ? l2Cat.id : '',
          material_id: c.sku_id, _searchKeyword: '',
          spec: c.spec || '', width: c.width || null, depth: c.depth || null, height: c.height || null,
          quantity: c.quantity || 1, price: c.unit_price || null, amount: c.total_price || 0,
          unit: c.unit || '', calcVal: null,
          sku_code: c.sku_code || '', brand: c.brand || '', material: c.material || '', main_image: c.material_image || '',
          env_level: c.env_level || '合格', supply_chain: c.supply_chain || '直供', color_name: c.color_name || '', custom_name: c.custom_name || '', custom_measure: c.custom_measure || '',
          category_level1: c.category_level1 || '', category_level2: c.category_level2 || ''
        }
      })
    }
  } catch(e) {
    console.warn('Load space materials failed:', e)
  }
  // 加载完成后重新计算每行的 calcVal 和 amount
  matRows.value.forEach((_, idx) => recalcMatRow(idx))
  if (matRows.value.length === 0) addMatRow()
  materialDialogVisible.value = true
}

const addMatRow = () => {
  matRows.value.push({ name:'',cat1Id:'',cat2Id:'',material_name:'',material_id:null,spec:'',width:null,depth:null,height:null,quantity:1,price:null,amount:0,unit:'',calcVal:null,sku_code:'',brand:'',material:'',main_image:'',env_level:'合格',supply_chain:'直供',color_name:'',custom_name:'',custom_measure:'',category_level1:'',category_level2:'' })
}

const cloneMatRow = (idx) => { matRows.value.push({ ...matRows.value[idx], name: matRows.value[idx].name + ' (副本)' }) }
const removeMatRow = (idx) => { matRows.value.splice(idx, 1) }

const onCat1Change = (rIdx) => {
  const row = matRows.value[rIdx]
  row.cat2Id = ''; row.material_name = ''; row.material_id = null; row.spec = ''; row.price = null; row.unit = ''; row.calcVal = null; row.amount = 0
}
const onCat2Change = (rIdx) => {
  const row = matRows.value[rIdx]
  row.material_name = ''; row.material_id = null; row.spec = ''; row.price = null; row.unit = ''; row.calcVal = null; row.amount = 0
}
const onMaterialNameChange = (rIdx) => {
  const row = matRows.value[rIdx]
  row.material_id = null; row.spec = ''; row.price = null; row.unit = ''; row.calcVal = null; row.amount = 0
}

const onMatFilter = async (rIdx, query) => {
  // 本地过滤物料：按关键词过滤已加载的SKU列表
  const row = matRows.value[rIdx]
  // 如果本地列表未加载，先加载
  if (materialSKUs.value.length === 0) await loadMaterialLibrary()
  // 用 _searchKeyword 存储搜索词，getFilteredSKUs 会用它来过滤
  row._searchKeyword = (query || '').trim()
}

const onMatSelect = (rIdx) => {
  const row = matRows.value[rIdx]
  const mat = materialSKUs.value.find(m => m.id == row.material_id)
  if (mat) {
    row.spec = mat.specification || ''
    row.price = parseFloat(mat.sale_price) || null
    row.unit = mat.unit || ''
    row.name = row.name || mat.name || ''
    row.sku_code = mat.sku_code || ''
    row.brand = mat.brand || ''
    row.material = mat.material || ''
    row.main_image = mat.main_image || ''
    row.env_level = mat.env_level || '合格'
    row.supply_chain = mat.supply_chain || '直供'
    row.color_name = mat.color_name || ''
    // 不再清空 custom_name 和 custom_measure，保留用户手动输入的值
    if (!row.custom_name) row.custom_name = ''
    if (!row.custom_measure) row.custom_measure = ''
  }
  recalcMatRow(rIdx)
}

const recalcMatRow = (rIdx) => {
  const row = matRows.value[rIdx]
  const w=parseFloat(row.width)||0, d=parseFloat(row.depth)||0, h=parseFloat(row.height)||0
  const qty=parseFloat(row.quantity)||0, price=parseFloat(row.price)||0
  const unit=(row.unit||'').toLowerCase()
  let cv=null
  if(unit==='m'||unit==='米'||unit==='延米') cv=Math.max(w,d,h)/1000
  else if(unit.includes('㎡')||unit.includes('平方米')||unit.toLowerCase().includes('m2')) {
    const areas=[w*h,w*d,h*d].filter(a=>a>0); cv=areas.length?Math.max(...areas)/1000000:null
  }
  else if(unit.includes('m³')||unit.includes('立方米')) cv=(w*d*h)/1000000000
  else cv=1
  row.calcVal=cv!==null?cv.toFixed(3):'-'
  row.amount=cv!==null?cv*qty*price:0
  // 将计算结果同步到 custom_measure，确保保存后能持久化显示
  if (cv !== null) {
    row.custom_measure = cv.toFixed(3)
  }
}

const saveMaterialConfig = async () => {
  matSaving.value=true
  try {
    await request.put('/spaces/'+currentMaterialSpace.value.id+'/full', {
      configs: matRows.value.map(r => {
        // Resolve category names from IDs
        const l1 = l1Categories.value.find(c => c.id === r.cat1Id)
        const l2 = l1 ? (l1.children || []).find(c => c.id === r.cat2Id) : null
        return {
          name: r.name, material_id: r.material_id, sku_code: r.sku_code, brand: r.brand,
          material: r.material, spec: r.spec,
          width: r.width, depth: r.depth, height: r.height,
          quantity: r.quantity, price: r.price, amount: r.amount, unit: r.unit,
          main_image: r.main_image,
          env_level: r.env_level, supply_chain: r.supply_chain, color_name: r.color_name,
          custom_name: r.custom_name, custom_measure: r.custom_measure,
          category_level1: l1 ? l1.name : (r.category_level1 || ''),
          category_level2: l2 ? l2.name : (r.category_level2 || '')
        }
      })
    })
    ElMessage.success('物料配置已保存')
    materialDialogVisible.value=false
  } catch(e) {
    ElMessage.error('保存失败: '+(e.message||'未知错误'))
  } finally { matSaving.value=false }
}


onMounted(() => {
  loadSpaces()
  loadQuoteSpaceNames()
})

watch(() => props.quoteId, () => {
  loadQuoteSpaceNames()
})
</script>

<style scoped>
.phase-space-renderings-editor {
  width: 100%;
}

.quote-tip {
  margin-bottom: 16px;
}

.space-block {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fafafa;
}

.space-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.space-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.renderings-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.rendering-card {
  width: 420px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.rendering-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.rendering-image {
  width: 100%;
  height: 240px;
  position: relative;
  background: #f5f7fa;
}

.rendering-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
  gap: 8px;
  transition: background 0.2s;
}

.upload-placeholder:hover {
  background: #e6e8eb;
}

.img-overlay {
  position: absolute; inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.rendering-image:hover .img-overlay {
  opacity: 1;
}

.uploading-mask {
  position: absolute; inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 13px;
  gap: 6px;
}

.rendering-info {
  padding: 14px;
}

.rich-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}
/* 物料配置弹窗 */
.material-config-body{padding:0}
.mat-toolbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #f0f0f0}
.mat-toolbar-hint{font-size:13px;color:#909399}
.config-table-wrapper{overflow-x:auto;max-height:55vh;overflow-y:auto}
.config-table{width:100%;font-size:12px;border-collapse:collapse;min-width:1100px}
.config-table th{padding:7px 5px;text-align:center;border:1px solid #e8e8e8;background:#fafafa;font-weight:500;color:#666;white-space:nowrap}
.config-table td{padding:5px 4px;border:1px solid #e8e8e8;vertical-align:middle}
.cfg-input{width:100%;padding:4px;border:1px solid #e8e8e8;border-radius:3px;font-size:11px;box-sizing:border-box}
.cfg-input:focus{border-color:#722F37;outline:none;box-shadow:0 0 0 2px rgba(114,47,55,.1)}
.cfg-select{width:100%;padding:4px;border:1px solid #d4b896;border-radius:3px;font-size:11px;color:#722F37;background:#fff;box-sizing:border-box}
.cfg-select:disabled{background:#e8e8e8;color:#999;border-color:#e8e8e8}
.cfg-calc{text-align:center;font-size:11px;color:#722F37}
.cfg-amount{text-align:center;font-weight:600;color:#722F37;font-size:12px}
.cfg-actions{text-align:center;white-space:nowrap}
.cfg-btn-clone{padding:2px 6px;border:1px solid #722F37;background:#fff;color:#722F37;border-radius:3px;cursor:pointer;font-size:11px;margin-right:2px}
.cfg-btn-clone:hover{background:#722F37;color:#fff}
.cfg-btn-delete{padding:2px 6px;border:1px solid #ff4d4f;background:#fff;color:#ff4d4f;border-radius:3px;cursor:pointer;font-size:11px}
.cfg-btn-delete:hover{background:#ff4d4f;color:#fff}
</style>
