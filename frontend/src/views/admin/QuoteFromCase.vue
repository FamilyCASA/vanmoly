<template>
  <div class="quote-from-case">
    <!-- 顶部导航 -->
    <div class="page-header">
      <el-button link @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2>从案例创建报价</h2>
      <div></div>
    </div>

    <!-- 步骤条 -->
    <el-steps :active="activeStep" finish-status="success" class="steps">
      <el-step title="选择客户" />
      <el-step title="选择案例" />
      <el-step title="配置空间" />
      <el-step title="确认报价" />
    </el-steps>

    <!-- 步骤1: 选择客户 -->
    <div v-show="activeStep === 0" class="step-content">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>选择客户</span>
            <el-input
              v-model="customerSearch"
              placeholder="搜索客户姓名/电话"
              style="width: 200px"
              clearable
              @input="searchCustomers"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </template>

        <el-table
          :data="customers"
          v-loading="loading.customers"
          highlight-current-row
          @current-change="onSelectCustomer"
          style="width: 100%"
        >
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="phone" label="电话" width="140" />
          <el-table-column prop="address" label="房屋地址" min-width="200" />
          <el-table-column prop="source" label="来源" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="customerPage"
            :page-size="10"
            :total="customerTotal"
            layout="prev, pager, next"
            @current-change="loadCustomers"
          />
        </div>
      </el-card>

      <div class="selected-customer" v-if="selectedCustomer">
        <el-alert type="success" :closable="false">
          <template #title>
            <span>已选择客户：<b>{{ selectedCustomer.name }}</b> ({{ selectedCustomer.phone }})</span>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 步骤2: 选择案例 -->
    <div v-show="activeStep === 1" class="step-content">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>选择案例模板</span>
            <div>
              <el-select v-model="caseFilter.style" placeholder="风格" clearable style="width: 120px; margin-right: 8px">
                <el-option label="现代简约" value="modern" />
                <el-option label="北欧" value="nordic" />
                <el-option label="极简" value="minimalist" />
                <el-option label="中式" value="chinese" />
                <el-option label="奶油风" value="cream" />
                <el-option label="轻奢" value="luxury" />
                <el-option label="暗黑" value="dark" />
              </el-select>
              <el-input
                v-model="caseFilter.keyword"
                placeholder="搜索案例"
                style="width: 200px"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>

        <div class="case-grid" v-loading="loading.cases">
          <div
            v-for="c in cases"
            :key="c.id"
            class="case-card"
            :class="{ active: selectedCase?.id === c.id }"
            @click="onSelectCase(c)"
          >
            <div class="case-cover">
              <img v-if="c.cover_image" :src="getImageUrl(c.cover_image)" />
              <div v-else class="no-image">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
            <div class="case-info">
              <h4>{{ c.title }}</h4>
              <div class="case-meta">
                <span>{{ c.style }}</span>
                <span>{{ c.house_type }}</span>
                <span>{{ c.area }}m²</span>
              </div>
              <div class="case-price">参考价：¥{{ formatMoney(c.reference_price) }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 步骤3: 配置空间 -->
    <div v-show="activeStep === 2" class="step-content" v-if="selectedCase">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>配置空间方案</span>
            <el-tag>案例：{{ selectedCase.title }}</el-tag>
          </div>
        </template>

        <el-table :data="spaceConfigs" border>
          <el-table-column label="空间" width="120">
            <template #default="{ row }">
              <div class="space-name">
                <el-icon><House /></el-icon>
                {{ row.space_name || row.space_type }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="面积" width="100">
            <template #default="{ row }">
              <span v-if="row.space_area">{{ row.space_area }}m²</span>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column label="版本选择" width="280">
            <template #default="{ row }">
              <el-radio-group v-model="row.selected_version" @change="onVersionChange(row)">
                <el-radio-button
                  v-for="v in getAvailableVersions(row)"
                  :key="v"
                  :label="v"
                >{{ v }}</el-radio-button>
              </el-radio-group>
            </template>
          </el-table-column>

          <el-table-column label="版本说明" min-width="200">
            <template #default="{ row }">
              <div class="version-desc">{{ getVersionDesc(row) }}</div>
            </template>
          </el-table-column>

          <el-table-column label="价格" width="150">
            <template #default="{ row }">
              <div class="space-price">¥{{ formatMoney(row.selected_price || row.total_price) }}</div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-checkbox v-model="row.is_selected">选择</el-checkbox>
            </template>
          </el-table-column>
        </el-table>

        <div class="config-summary">
          <el-row :gutter="24">
            <el-col :span="6">
              <el-statistic title="已选空间" :value="selectedSpacesCount" suffix="个" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="物料成本" :value="materialTotal" prefix="¥" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="人工费用" :value="laborTotal" prefix="¥" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="设计费用" :value="designTotal" prefix="¥" />
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>

    <!-- 步骤4: 确认报价 -->
    <div v-show="activeStep === 3" class="step-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>报价预览</template>

            <div class="quote-preview">
              <div class="preview-header">
                <h3>帝标·设记家 全案服务报价单</h3>
                <div class="quote-no">{{ form.quote_no || '生成中...' }}</div>
              </div>

              <div class="preview-customer" v-if="selectedCustomer">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="客户姓名">{{ selectedCustomer.name }}</el-descriptions-item>
                  <el-descriptions-item label="联系电话">{{ selectedCustomer.phone }}</el-descriptions-item>
                  <el-descriptions-item label="房屋地址" :span="2">{{ selectedCustomer.address }}</el-descriptions-item>
                </el-descriptions>
              </div>

              <div class="preview-spaces">
                <h4>空间配置方案</h4>
                <el-table :data="selectedSpaces" size="small">
                  <el-table-column prop="space_name" label="空间" width="100" />
                  <el-table-column prop="selected_version" label="版本" width="80" />
                  <el-table-column label="价格">
                    <template #default="{ row }">
                      ¥{{ formatMoney(row.selected_price || row.total_price) }}
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div class="preview-summary">
                <div class="summary-row">
                  <span>物料成本</span>
                  <span>¥{{ formatMoney(materialTotal) }}</span>
                </div>
                <div class="summary-row">
                  <span>人工费用</span>
                  <span>¥{{ formatMoney(laborTotal) }}</span>
                </div>
                <div class="summary-row">
                  <span>设计费用</span>
                  <span>¥{{ formatMoney(designTotal) }}</span>
                </div>
                <div class="summary-row">
                  <span>管理费用 ({{ form.management_fee_rate }}%)</span>
                  <span>¥{{ formatMoney(managementFee) }}</span>
                </div>
                <el-divider />
                <div class="summary-row total">
                  <span>报价总计</span>
                  <span class="total-price">¥{{ formatMoney(grandTotal) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="never">
            <template #header>其他设置</template>

            <el-form :model="form" label-width="100px">
              <el-form-item label="有效期(天)">
                <el-input-number v-model="form.valid_days" :min="1" :max="90" />
              </el-form-item>

              <el-form-item label="管理费率%">
                <el-input-number v-model="form.management_fee_rate" :min="0" :max="20" />
              </el-form-item>

              <el-form-item label="备注">
                <el-input v-model="form.remark" type="textarea" :rows="3" />
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-actions">
      <el-button v-if="activeStep > 0" @click="activeStep--">上一步</el-button>
      <el-button v-if="activeStep < 3" type="primary" @click="nextStep" :disabled="!canNextStep">
        下一步
      </el-button>
      <el-button v-if="activeStep === 3" type="success" @click="submitQuote" :loading="submitting">
        创建报价
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search, Picture, House } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const activeStep = ref(0)
const submitting = ref(false)

// 加载状态
const loading = reactive({
  customers: false,
  cases: false,
  configs: false
})

// 客户相关
const customers = ref([])
const customerSearch = ref('')
const customerPage = ref(1)
const customerTotal = ref(0)
const selectedCustomer = ref(null)

// 案例相关
const caseFilter = reactive({
  style: '',
  keyword: ''
})
const cases = ref([])
const selectedCase = ref(null)

// 空间配置
const spaceConfigs = ref([])

// 表单
const form = reactive({
  quote_no: '',
  valid_days: 30,
  management_fee_rate: 8,
  remark: ''
})

// 计算属性
const selectedSpaces = computed(() => {
  return spaceConfigs.value.filter(s => s.is_selected)
})

const selectedSpacesCount = computed(() => selectedSpaces.value.length)

const materialTotal = computed(() => {
  return selectedSpaces.value.reduce((sum, s) => sum + (s.selected_price || s.total_price || 0), 0)
})

const laborTotal = computed(() => {
  return selectedSpaces.value.reduce((sum, s) => sum + (s.labor_cost || 0), 0)
})

const designTotal = computed(() => {
  return selectedSpaces.value.reduce((sum, s) => sum + (s.design_cost || 0), 0)
})

const managementFee = computed(() => {
  const base = materialTotal.value + laborTotal.value + designTotal.value
  return base * (form.management_fee_rate / 100)
})

const grandTotal = computed(() => {
  return materialTotal.value + laborTotal.value + designTotal.value + managementFee.value
})

const canNextStep = computed(() => {
  if (activeStep.value === 0) return !!selectedCustomer.value
  if (activeStep.value === 1) return !!selectedCase.value
  if (activeStep.value === 2) return selectedSpacesCount.value > 0
  return true
})

// 加载客户
const loadCustomers = async (page = 1) => {
  loading.customers = true
  try {
    const res = await request.get('/customers', {
      params: {
        page,
        page_size: 10,
        keyword: customerSearch.value
      }
    })
    customers.value = res.items
    customerTotal.value = res.total
  } catch (err) {
    console.error('加载客户失败', err)
  } finally {
    loading.customers = false
  }
}

const searchCustomers = () => {
  customerPage.value = 1
  loadCustomers()
}

const onSelectCustomer = (row) => {
  selectedCustomer.value = row
}

// 加载案例
const loadCases = async () => {
  loading.cases = true
  try {
    const res = await request.get('/cases', {
      params: {
        page_size: 20,
        status: '已发布',
        style: caseFilter.style,
        keyword: caseFilter.keyword
      }
    })
    cases.value = res.items
  } catch (err) {
    console.error('加载案例失败', err)
  } finally {
    loading.cases = false
  }
}

const onSelectCase = async (c) => {
  selectedCase.value = c
  // 加载空间配置
  await loadSpaceConfigs(c.id)
}

// 加载空间配置
const loadSpaceConfigs = async (caseId) => {
  loading.configs = true
  try {
    const res = await request.get('/space-configs/by-case/' + caseId)
    // 后端返回按空间分组的字典: {"主卧": [...], "客厅": [...]}
    // 拦截器已解包，res 就是 grouped 对象
    const configs = []
    if (res && typeof res === 'object') {
      // 取每个空间组的第一个配置（默认版本）
      for (const [spaceType, items] of Object.entries(res)) {
        if (Array.isArray(items) && items.length > 0) {
          // 优先取舒适版，否则取第一个
          const comfort = items.find(i => i.version_level === '舒适')
          const config = comfort || items[0]
          configs.push({
            ...config,
            all_versions: items,
            selected_version: config.version_level || '舒适',
            selected_price: config.total_price,
            is_selected: true
          })
        }
      }
    }
    spaceConfigs.value = configs
    if (configs.length === 0) {
      ElMessage.warning('该案例暂无空间配置，请先配置案例')
    }
  } catch (err) {
    console.error('加载空间配置失败', err)
    ElMessage.warning('加载空间配置失败')
  } finally {
    loading.configs = false
  }
}

// 版本变化
const onVersionChange = (row) => {
  // 从 all_versions 中查找对应版本的真实数据
  if (row.all_versions && row.all_versions.length > 0) {
    const target = row.all_versions.find(v => v.version_level === row.selected_version)
    if (target) {
      // 更新为对应版本的配置数据
      row.selected_price = target.total_price
      row.labor_cost = target.labor_cost
      row.design_cost = target.design_cost
      row.total_price = target.total_price
      row.id = target.id
    }
  } else {
    // 无多版本数据时用系数估算
    const multipliers = { '舒适': 1, '豪华': 1.3, '顶配': 1.6 }
    row.selected_price = (row.total_price || 0) * (multipliers[row.selected_version] || 1)
  }
}

const getVersionDesc = (row) => {
  const descs = {
    '舒适': '高性价比配置，满足基本生活需求',
    '豪华': '品质升级配置，更多品牌选择',
    '顶配': '顶级配置，享受极致体验'
  }
  return descs[row.selected_version] || `${row.selected_version}版本配置`
}

// 获取可用版本列表
const getAvailableVersions = (row) => {
  if (row.all_versions && row.all_versions.length > 0) {
    return row.all_versions.map(v => v.version_level)
  }
  // 默认版本
  return ['舒适', '豪华', '顶配']
}

// 下一步
const nextStep = () => {
  if (!canNextStep.value) return
  activeStep.value++
}

// 提交报价
const submitQuote = async () => {
  submitting.value = true
  try {
    const payload = {
      case_id: selectedCase.value.id,
      customer_id: selectedCustomer.value.id,
      selected_configs: selectedSpaces.value.map(s => ({
        space_type: s.space_type,
        config_id: s.id,
        version_level: s.selected_version
      })),
      service_team: [],
      cover_config: {},
      valid_days: form.valid_days,
      remark: form.remark
    }

    const res = await request.post('/quotes/clone-from-template', payload)
    
    ElMessage.success('报价创建成功')
    // 拦截器已解包 res.data，res 就是 quote 对象
    const quoteId = res.id || res.quote_id
    if (quoteId) {
      router.push('/admin/quotes/' + quoteId)
    } else {
      router.push('/admin/quotes')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '创建失败')
  } finally {
    submitting.value = false
  }
}

// 辅助函数
const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/api/v3')) return url
  if (url.startsWith('/upload') || url.startsWith('/static') || url.startsWith('/uploads')) return '/api/v3' + url
  return url
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// 监听筛选条件变化
watch(caseFilter, loadCases, { deep: true })

onMounted(() => {
  loadCustomers()
  loadCases()
})
</script>

<style scoped>
.quote-from-case {
  padding: 24px;
  padding-bottom: 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
}

.steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.selected-customer {
  margin-top: 16px;
}

/* 案例网格 */
.case-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.case-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.case-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.case-card.active {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64,158,255,0.2);
}

.case-cover {
  height: 150px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.case-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.case-cover .no-image {
  color: #ccc;
  font-size: 48px;
}

.case-info {
  padding: 12px;
}

.case-info h4 {
  margin: 0 0 8px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.case-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.case-price {
  font-size: 14px;
  font-weight: 500;
  color: #f5222d;
}

/* 空间配置 */
.space-name {
  display: flex;
  align-items: center;
  gap: 4px;
}

.version-desc {
  font-size: 12px;
  color: #8c8c8c;
}

.space-price {
  font-weight: 500;
  color: #f5222d;
}

.config-summary {
  margin-top: 24px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* 报价预览 */
.quote-preview {
  padding: 20px;
}

.preview-header {
  text-align: center;
  margin-bottom: 24px;
}

.preview-header h3 {
  margin: 0 0 8px;
  font-size: 20px;
}

.quote-no {
  font-size: 14px;
  color: #8c8c8c;
  letter-spacing: 1px;
}

.preview-customer {
  margin-bottom: 24px;
}

.preview-spaces h4 {
  margin: 0 0 12px;
  font-size: 14px;
}

.preview-summary {
  margin-top: 24px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.summary-row.total {
  font-size: 18px;
  font-weight: bold;
}

.total-price {
  color: #f5222d;
  font-size: 24px;
}

/* 底部操作栏 */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 200px;
  right: 0;
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  z-index: 100;
}
</style>
