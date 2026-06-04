<template>
  <div class="quote-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <span class="quote-no" style="cursor:pointer" title="点击复制报价单号" @click="copyQuoteNo">
            {{ quote.quote_no }} <el-icon><DocumentCopy /></el-icon>
          </span>
          <el-tag :type="statusType(quote.status)" size="small" style="margin-left: 8px">
            {{ statusLabel(quote.status) }}
          </el-tag>
        </template>
        <template #extra>
          <el-button-group>
            <el-button type="primary" @click="editQuote" v-if="quote.status === 'draft'">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button type="success" @click="handleExportPDF">
              <el-icon><Printer /></el-icon> 导出PDF
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button>
                更多操作 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="copy">复制报价</el-dropdown-item>
                  <el-dropdown-item command="convert" v-if="quote.status === 'accepted'">转订单</el-dropdown-item>
                  <el-dropdown-item command="export">导出PDF</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-button-group>
        </template>
      </el-page-header>
    </div>

    <!-- 基本信息 -->
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="客户姓名">{{ quote.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ quote.customer_phone }}</el-descriptions-item>
        <el-descriptions-item label="客户地址">{{ quote.customer_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报价日期">{{ formatDate(quote.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="项目地址">{{ quote.project_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="有效期至">{{ quote.valid_until ? formatDate(quote.valid_until) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="设计师">{{ quote.designer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="销售顾问">{{ quote.sales_name || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 报价空间 -->
    <el-card shadow="never" class="spaces-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>报价空间 ({{ spaces.length }}个)</span>
          <el-button type="primary" size="small" @click="addSpace" v-if="quote.status === 'draft'">
            <el-icon><Plus /></el-icon> 添加空间
          </el-button>
        </div>
      </template>

      <!-- 新格式：空间实例 -->
      <el-tabs v-if="!useLegacyView" v-model="activeSpace" type="card">
        <el-tab-pane
          v-for="space in spaces"
          :key="space.id"
          :label="space.space_name"
          :name="String(space.id)"
        >
          <!-- 空间概览 -->
          <div class="space-overview">
            <el-row :gutter="16">
              <el-col :span="6">
                <el-statistic title="物料数量" :value="space.material_count || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="物料成本" :value="space.material_cost || 0" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="工艺费用" :value="space.labor_cost || 0" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="小计" :value="space.total_price || 0" :precision="2" prefix="¥" />
              </el-col>
            </el-row>
          </div>

          <!-- 物料明细 -->
          <el-table :data="space.items" stripe style="margin-top: 16px">
            <el-table-column type="index" width="50" />
            <el-table-column prop="sku_code" label="物料编码" width="140" />
            <el-table-column prop="sku_name" label="物料名称" min-width="200" />
            <el-table-column prop="brand" label="品牌" width="100" />
            <el-table-column prop="specification" label="规格" width="120" />
            <el-table-column prop="category" label="分类" width="80" />
            <el-table-column prop="quantity" label="数量" width="80" align="right" />
            <el-table-column prop="unit" label="单位" width="60" align="center" />
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">
                ¥{{ row.unit_price }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">
                <span class="amount">¥{{ row.total_price }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" v-if="quote.status === 'draft'">
              <template #default="{ row }">
                <el-button link type="primary" @click="editItem(space, row)">编辑</el-button>
                <el-button link type="danger" @click="deleteItem(space, row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- 旧格式：扁平物料按房间分组 -->
      <el-tabs v-else v-model="activeLegacyRoom" type="card">
        <el-tab-pane
          v-for="group in legacyGrouped"
          :key="group.room_name"
          :label="group.room_name"
          :name="group.room_name"
        >
          <div class="space-overview">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-statistic title="物料数量" :value="group.items.length" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="房间小计" :value="group.total" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="8">
                <el-tag type="info">旧版报价格式</el-tag>
              </el-col>
            </el-row>
          </div>

          <el-table :data="group.items" stripe style="margin-top: 16px">
            <el-table-column type="index" width="50" />
            <el-table-column prop="name" label="物料名称" min-width="200" />
            <el-table-column prop="category_level1" label="分类" width="100">
              <template #default="{ row }">
                {{ row.category_level1 || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="brand" label="品牌" width="100" />
            <el-table-column prop="spec" label="规格" width="140" />
            <el-table-column prop="quantity" label="数量" width="80" align="right" />
            <el-table-column prop="unit" label="单位" width="60" align="center" />
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">
                ¥{{ row.unit_price }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">
                <span class="amount">¥{{ row.total_price }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- 无任何数据 -->
      <el-empty v-if="!useLegacyView && spaces.length === 0" description="暂无报价明细" />
    </el-card>

    <!-- 费用汇总 -->
    <el-card shadow="never" class="summary-card">
      <template #header>
        <div class="card-header">
          <span>费用汇总</span>
        </div>
      </template>
      <el-row :gutter="32">
        <el-col :span="16">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="物料总额">
              ¥{{ formatMoney(quote.material_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="工艺费用">
              ¥{{ formatMoney(quote.craft_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="设计费用">
              ¥{{ formatMoney(quote.design_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="安装费用">
              ¥{{ formatMoney(quote.install_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="管理费率">
              {{ quote.manage_rate || 0 }}%
            </el-descriptions-item>
            <el-descriptions-item label="管理费">
              ¥{{ formatMoney(quote.manage_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="税额">
              ¥{{ formatMoney(quote.tax_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="优惠金额">
              <span class="discount">-¥{{ formatMoney(quote.discount_amount) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
        <el-col :span="8">
          <div class="total-box">
            <div class="total-label">报价总额</div>
            <div class="total-value">¥{{ formatMoney(quote.total_amount) }}</div>
            <div class="total-words">（大写：{{ moneyToChinese(quote.total_amount) }}）</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 备注信息 -->
    <el-card shadow="never" class="remark-card">
      <template #header>
        <div class="card-header">
          <span>备注信息</span>
        </div>
      </template>
      <el-input
        v-model="quote.remark"
        type="textarea"
        :rows="4"
        readonly
        placeholder="暂无备注"
      />
    </el-card>

    <!-- 签字区 -->
    <el-card shadow="never" class="sign-card">
      <template #header>
        <div class="card-header">
          <span>签字确认</span>
        </div>
      </template>
      <el-row :gutter="32">
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">客户签字</div>
            <div class="sign-value">{{ quote.customer_sign || '待签字' }}</div>
            <div class="sign-date" v-if="quote.customer_sign_date">
              {{ formatDate(quote.customer_sign_date) }}
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">设计师签字</div>
            <div class="sign-value">{{ quote.designer_sign || '待签字' }}</div>
            <div class="sign-date" v-if="quote.designer_sign_date">
              {{ formatDate(quote.designer_sign_date) }}
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">公司盖章</div>
            <div class="sign-value">{{ quote.company_seal ? '已盖章' : '待盖章' }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 编辑物料对话框 -->
    <el-dialog v-model="itemDialogVisible" title="编辑物料" width="600px">
      <el-form :model="itemForm" label-width="80px">
        <el-form-item label="数量">
          <el-input-number v-model="itemForm.quantity" :min="0.1" :precision="2" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="itemForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="itemForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, Printer, ArrowDown, Plus, DocumentCopy
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 报价ID
const quoteId = computed(() => route.params.id)

// 数据
const loading = ref(false)
const quote = ref({})
const spaces = ref([])
const activeSpace = ref('')

// 状态映射
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  sent: { label: '已发送', type: 'warning' },
  accepted: { label: '已接受', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  expired: { label: '已过期', type: 'info' }
}

const statusLabel = (status) => statusMap[status]?.label || status
const statusType = (status) => statusMap[status]?.type || 'info'

// 格式化
const formatMoney = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 金额转中文大写
const moneyToChinese = (money) => {
  if (!money || money === 0) return '零元整'
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
  const decimalUnits = ['角', '分']
  
  const str = Math.abs(money).toFixed(2)
  const [integerPart, decimalPart] = str.split('.')
  
  let result = ''
  
  // 整数部分
  const intStr = integerPart.toString()
  for (let i = 0; i < intStr.length; i++) {
    const digit = parseInt(intStr[i])
    const unitIndex = intStr.length - 1 - i
    result += digits[digit] + units[unitIndex]
  }
  result = result.replace(/零+$/, '').replace(/零{2,}/g, '零')
  
  // 小数部分
  if (decimalPart && decimalPart !== '00') {
    for (let i = 0; i < decimalPart.length && i < 2; i++) {
      const digit = parseInt(decimalPart[i])
      if (digit !== 0) {
        result += digits[digit] + decimalUnits[i]
      }
    }
  }
  
  result += '元整'
  return result
}

// 旧报价扁平物料（按room_name分组）
const legacyItems = ref([])
const legacyGrouped = computed(() => {
  if (!legacyItems.value.length) return []
  const groups = {}
  for (const item of legacyItems.value) {
    const room = item.room_name || '未分类'
    if (!groups[room]) {
      groups[room] = { room_name: room, items: [], total: 0 }
    }
    groups[room].items.push(item)
    groups[room].total += Number(item.total_price || 0)
  }
  return Object.values(groups)
})
const useLegacyView = computed(() => spaces.value.length === 0 && legacyItems.value.length > 0)
const activeLegacyRoom = ref('')

// 加载数据
const loadQuote = async () => {
  loading.value = true
  try {
    const res = await request.get(`/quotes/${quoteId.value}`)
    quote.value = res || {}
    
    // 加载空间实例
    try {
      const spacesRes = await request.get(`/quotes/${quoteId.value}/space-instances`)
      spaces.value = Array.isArray(spacesRes) ? spacesRes : []
    } catch (e) {
      spaces.value = []
    }
    
    if (spaces.value.length > 0) {
      activeSpace.value = String(spaces.value[0].id)
    } else {
      // 降级：使用报价自带的扁平items按room_name分组
      const flatItems = quote.value.items || []
      if (flatItems.length > 0) {
        legacyItems.value = flatItems
        const firstRoom = legacyGrouped.value[0]?.room_name
        if (firstRoom) activeLegacyRoom.value = firstRoom
      }
    }
  } catch (error) {
    ElMessage.error('加载报价失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/admin/quotes')
}

// 编辑报价
const editQuote = () => {
  router.push(`/admin/quotes/${quoteId.value}/edit`)
}

// 导出PDF（携带token，fetch+blob触发下载）
const handleExportPDF = async () => {
  const id = quoteId.value
  try {
    // 从 localStorage 取 token（与 request.js 一致）
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token') || ''
    const resp = await fetch(`/api/v3/quotes/${id}/pdf`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!resp.ok) {
      ElMessage.error('下载失败，请先生成PDF')
      return
    }
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `报价单_${quote.value?.quote_no || id}_访客版.pdf`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('PDF 下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出PDF失败')
  }
}

// 下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'copy':
      copyQuote()
      break
    case 'convert':
      ElMessage.info('转订单功能开发中')
      break
    case 'export':
      handleExportPDF()
      break
    case 'delete':
      ElMessageBox.confirm('确定要删除该报价吗？', '提示', {
        type: 'warning'
      }).then(() => {
        ElMessage.success('删除成功')
        goBack()
      }).catch(() => {})
      break
  }
}

// 复制报价单号到剪贴板
const copyQuoteNo = () => {
  const no = quote.value?.quote_no
  if (!no) return
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(no).then(() => {
      ElMessage.success(`报价单号 ${no} 已复制`)
    }).catch(() => {
      ElMessage.error('复制失败，请手动复制')
    })
  } else {
    const ta = document.createElement('textarea')
    ta.value = no
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success(`报价单号 ${no} 已复制`)
  }
}

// 复制报价（跳转新建页面并预填）
const copyQuote = () => {
  router.push({ path: '/admin/quotes/from-case', query: { from: quoteId.value } })
}

// 编辑物料
const itemDialogVisible = ref(false)
const itemForm = reactive({
  id: null,
  space_id: null,
  quantity: 1,
  unit_price: 0,
  remark: ''
})

const editItem = (space, item) => {
  itemForm.id = item.id
  itemForm.space_id = space.id
  itemForm.quantity = item.quantity
  itemForm.unit_price = item.unit_price
  itemForm.remark = item.remark || ''
  itemDialogVisible.value = true
}

const saveItem = async () => {
  try {
    await request.put(
      `/api/v3/quotes/${quoteId.value}/space-instances/${itemForm.space_id}/items/${itemForm.id}`,
      itemForm
    )
    ElMessage.success('保存成功')
    itemDialogVisible.value = false
    loadQuote()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteItem = async (space, item) => {
  try {
    await ElMessageBox.confirm('确定要删除该物料吗？', '提示', { type: 'warning' })
    await request.delete(
      `/api/v3/quotes/${quoteId.value}/space-instances/${space.id}/items/${item.id}`
    )
    ElMessage.success('删除成功')
    loadQuote()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadQuote()
})
</script>

<style scoped>
.quote-detail {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.quote-no {
  font-size: 18px;
  font-weight: 600;
}

.info-card,
.spaces-card,
.summary-card,
.remark-card,
.sign-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-overview {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.amount {
  color: #409eff;
  font-weight: 600;
}

.summary-card .total-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.total-label {
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.total-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.total-words {
  font-size: 12px;
  opacity: 0.8;
}

.discount {
  color: #67c23a;
  font-weight: 600;
}

.sign-box {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  text-align: center;
}

.sign-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.sign-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.sign-date {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

:deep(.el-descriptions__label) {
  width: 100px;
}

:deep(.el-tabs__item) {
  font-weight: 500;
}
</style>
