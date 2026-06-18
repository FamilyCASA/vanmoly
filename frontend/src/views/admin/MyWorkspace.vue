<template>
  <div class="workspace-layout">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="top-left">
        <el-button :icon="ArrowLeft" text @click="router.push('/admin/dashboard')">
          返回管理后台
        </el-button>
      </div>
      <div class="top-center">
        <span class="top-title">{{ currentTitle }}</span>
      </div>
      <div class="top-right">
        <el-button type="danger" :icon="SwitchButton" text @click="handleLogout">
          登出
        </el-button>
      </div>
    </div>

    <div class="workspace-body">
      <!-- 左侧导航 -->
      <div class="workspace-sidebar">
        <div class="sidebar-header">
          <h3>我的工作台</h3>
          <p class="sidebar-desc">个人业务、流程与设置</p>
        </div>
        <div class="sidebar-nav">
          <div v-for="group in navGroups" :key="group.title" class="nav-group">
            <div class="nav-section-title">{{ group.title }}</div>
            <div
              v-for="item in group.items"
              :key="item.key"
              class="nav-card"
              :class="{ active: activeKey === item.key }"
              @click="activeKey = item.key"
            >
              <div class="nav-icon" :style="{ background: item.bg, color: item.color }">
                <el-icon :size="20"><component :is="item.icon" /></el-icon>
              </div>
              <div class="nav-info">
                <div class="nav-title">{{ item.title }}</div>
                <div class="nav-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="workspace-content">
        <div class="content-body">
          <!-- 我的线索 -->
          <div v-if="activeKey === 'leads'" v-loading="leadsLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="leadSearch" placeholder="搜索线索名称/电话" clearable style="width: 220px" />
              <el-select v-model="leadStatus" placeholder="状态筛选" clearable style="width: 140px">
                <el-option
                  v-for="opt in leadStatusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-button type="primary" @click="openLeadDialog">+ 新建线索</el-button>
            </div>
            <el-table :data="pagedLeads" stripe size="small" border>
              <el-table-column prop="name" label="线索名称" min-width="140" show-overflow-tooltip />
              <el-table-column prop="phone" label="电话" width="130" />
              <el-table-column prop="source" label="来源" width="120" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="120">
                <template #default="{ row }">{{ row.created_at ? row.created_at.slice(0, 10) : '-' }}</template>
              </el-table-column>
              <el-table-column label="操作" width="130" fixed="right">
                <template #default="{ row }">
                  <el-select
                    size="small"
                    style="width: 100px"
                    placeholder="修改状态"
                    @change="(val) => updateLeadStatus(row, val)"
                  >
                    <el-option
                      v-for="opt in leadStatusOptions.filter((o) => o.value)"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="leadPage"
              v-model:page-size="leadPageSize"
              :total="leadTotal"
              layout="total, sizes, prev, pager, next"
              :page-sizes="[10, 20, 50]"
            />
          </div>

          <!-- 我的客户 -->
          <div v-if="activeKey === 'customers'" v-loading="customersLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="custSearch" placeholder="搜索客户名称" clearable style="width: 260px" />
              <el-button type="primary" @click="loadCustomers">查询</el-button>
            </div>
            <el-table :data="pagedCustomers" stripe size="small" border>
              <el-table-column prop="name" label="客户名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="phone" label="电话" width="130" />
              <el-table-column prop="source" label="来源" width="120" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="120">
                <template #default="{ row }">{{ row.created_at ? row.created_at.slice(0, 10) : '-' }}</template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="custPage"
              v-model:page-size="custPageSize"
              :total="custTotal"
              layout="total, sizes, prev, pager, next"
              :page-sizes="[10, 20, 50]"
            />
          </div>

          <!-- 我的楼盘 -->
          <div v-if="activeKey === 'buildings'" v-loading="buildingsLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="buildingSearch" placeholder="搜索楼盘名称/区域/地址" clearable style="width: 320px" />
              <el-button type="primary" @click="loadBuildings">查询</el-button>
            </div>
            <el-table :data="pagedBuildings" stripe size="small" border>
              <el-table-column prop="name" label="楼盘名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="district" label="区域" width="120" />
              <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
              <el-table-column prop="units_count" label="户数" width="90" align="center" />
            </el-table>
            <el-pagination
              v-model:current-page="buildingPage"
              v-model:page-size="buildingPageSize"
              :total="buildingTotal"
              layout="total, sizes, prev, pager, next"
              :page-sizes="[10, 20, 50]"
            />
          </div>

          <!-- 我的合同 -->
          <div v-if="activeKey === 'contracts'" v-loading="contractsLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="contractSearch" placeholder="搜索合同编号/客户" clearable style="width: 260px" />
              <el-select v-model="contractStatus" placeholder="状态筛选" clearable style="width: 140px">
                <el-option
                  v-for="opt in contractStatusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-button type="primary" @click="loadContracts">查询</el-button>
            </div>
            <el-table :data="pagedContracts" stripe size="small" border>
              <el-table-column prop="contract_no" label="合同编号" width="170" />
              <el-table-column label="合同金额" width="120" align="right">
                <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
              </el-table-column>
              <el-table-column prop="customer_name" label="客户名称" min-width="140" show-overflow-tooltip />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="签约日期" width="120">
                <template #default="{ row }">{{ row.signing_date ? row.signing_date.slice(0, 10) : '-' }}</template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="contractPage"
              v-model:page-size="contractPageSize"
              :total="contractTotal"
              layout="total, sizes, prev, pager, next"
              :page-sizes="[10, 20, 50]"
            />
          </div>

          <!-- 我的报价 -->
          <div v-if="activeKey === 'quotes'" v-loading="quotesLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="quoteSearch" placeholder="搜索报价编号/客户" clearable style="width: 320px" />
              <el-button type="primary" @click="loadQuotes">查询</el-button>
            </div>
            <el-table :data="pagedQuotes" stripe size="small" border>
              <el-table-column label="报价编号" width="170">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="router.push(`/admin/quotes/${row.id}`)">
                    {{ row.quote_no || row.id }}
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column prop="customer_name" label="客户名称" min-width="160" show-overflow-tooltip />
              <el-table-column label="总金额" width="120" align="right">
                <template #default="{ row }">¥{{ formatNum(row.total_amount) }}</template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="120">
                <template #default="{ row }">{{ row.created_at ? row.created_at.slice(0, 10) : '-' }}</template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="quotePage"
              v-model:page-size="quotePageSize"
              :total="quoteTotal"
              layout="total, sizes, prev, pager, next"
              :page-sizes="[10, 20, 50]"
            />
          </div>

          <!-- 我的团队 -->
          <div v-if="activeKey === 'team'" v-loading="teamLoading" class="tab-panel">
            <div class="team-info">
              <el-tag type="primary">{{ teamInfo.department_name || teamInfo.department || '未分配部门' }}</el-tag>
              <el-tag v-if="teamInfo.store_name || teamInfo.store" type="success">{{ teamInfo.store_name || teamInfo.store }}</el-tag>
            </div>
            <el-table :data="teamMembers" stripe size="small" border>
              <el-table-column prop="name" label="姓名" width="120" />
              <el-table-column prop="position" label="岗位" min-width="140" />
              <el-table-column prop="phone" label="电话" width="130" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                    {{ row.status === 'active' ? '在职' : '离职' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 我的审核 -->
          <div v-if="activeKey === 'reviews'" class="tab-panel embedded-view">
            <ApprovalTasks />
          </div>

          <!-- 我的服务流程 -->
          <div v-if="activeKey === 'workflow'" class="tab-panel embedded-view">
            <ServiceWorkflow />
          </div>

          <!-- 我的报销 -->
          <div v-if="activeKey === 'reimbursements'" class="tab-panel embedded-view">
            <MyReimbursements />
          </div>

          <!-- 我的收款 -->
          <div v-if="activeKey === 'receivables'" class="tab-panel embedded-view">
            <MyReceivables />
          </div>

          <!-- 我的付款 -->
          <div v-if="activeKey === 'payables'" class="tab-panel embedded-view">
            <MyPayables />
          </div>

          <!-- 修改登录密码 -->
          <div v-if="activeKey === 'password'" class="tab-panel">
            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="100px"
              style="max-width: 420px"
            >
              <el-form-item label="当前密码" prop="oldPassword">
                <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
              </el-form-item>
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitPassword">确认修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建线索弹窗 -->
    <el-dialog v-model="leadDialogVisible" title="新建线索" width="480px" destroy-on-close>
      <el-form ref="leadFormRef" :model="leadForm" :rules="leadRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="leadForm.name" placeholder="请输入线索名称" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="leadForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="leadForm.source" placeholder="如：官网、转介绍" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="leadForm.status" style="width: 100%">
            <el-option
              v-for="opt in leadStatusOptions.filter((o) => o.value)"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="leadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitLead">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElTable, ElTableColumn, ElButton, ElTag, ElInput, ElSelect, ElOption, ElPagination,
  ElMessage, ElMessageBox, ElForm, ElFormItem, ElDialog
} from 'element-plus'
import {
  ArrowLeft, SwitchButton, User, OfficeBuilding, Document, Money,
  Promotion, Share, Finished, Connection, Wallet, Ticket, Lock
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import ApprovalTasks from '@/views/finance/ApprovalTasks.vue'
import MyReimbursements from '@/views/finance/MyReimbursements.vue'
import MyReceivables from '@/views/finance/MyReceivables.vue'
import MyPayables from '@/views/finance/MyPayables.vue'
import ServiceWorkflow from '@/views/admin/ServiceWorkflow.vue'

const route = useRoute()
const router = useRouter()

const activeKey = ref(route.query.tab || 'leads')
const userId = ref('')
const submitting = ref(false)

// 通用状态标签
const statusTagType = (status) => {
  const s = String(status || '').toLowerCase()
  if (['draft', 'new', 'created', 'unpaid', '未开始'].includes(s)) return 'info'
  if (['pending', 'submitted', '待审核', 'contacted', 'in_progress', '进行中', 'partial', '未收齐'].includes(s)) {
    return 'warning'
  }
  if (['approved', 'signed', 'converted', 'success', 'completed', 'active', 'paid', 'received', 'finished', '通过', '在职'].includes(s)) {
    return 'success'
  }
  if (['rejected', 'cancelled', 'canceled', 'lost', 'closed', 'danger', '驳回', '离职'].includes(s)) {
    return 'danger'
  }
  return 'info'
}

const statusLabel = (status) => {
  const labels = {
    new: '新建',
    contacted: '已联系',
    converted: '已转化',
    lost: '已失效',
    draft: '草稿',
    pending: '待审核',
    submitted: '待审核',
    approved: '已通过',
    rejected: '已驳回',
    signed: '已签约',
    cancelled: '已取消',
    active: '进行中',
    completed: '已完成',
    paid: '已付款',
    received: '已收齐',
    partial: '部分收款'
  }
  return labels[status] || status || '-'
}

const formatNum = (v) => Number(v || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

const normalizeList = (res) => {
  if (Array.isArray(res)) return res
  if (res && Array.isArray(res.items)) return res.items
  if (res && Array.isArray(res.data)) return res.data
  if (res && Array.isArray(res.list)) return res.list
  return []
}

// 左侧导航
const navGroups = [
  {
    title: '业务拓展',
    items: [
      { key: 'leads', title: '我的线索', desc: '个人跟进的线索', icon: Promotion, bg: '#E6F7FF', color: '#1890FF' },
      { key: 'customers', title: '我的客户', desc: '客户档案列表', icon: User, bg: '#F6FFED', color: '#52C41A' },
      { key: 'buildings', title: '我的楼盘', desc: '负责楼盘信息', icon: OfficeBuilding, bg: '#E6FFFB', color: '#13C2C2' },
      { key: 'contracts', title: '我的合同', desc: '合同签约记录', icon: Document, bg: '#FFF2E8', color: '#FA541C' },
      { key: 'quotes', title: '我的报价', desc: '报价单记录', icon: Money, bg: '#F0F5FF', color: '#2F54EB' }
    ]
  },
  {
    title: '工作流转',
    items: [
      { key: 'team', title: '我的团队', desc: '部门成员信息', icon: Share, bg: '#F9F0FF', color: '#722ED1' },
      { key: 'reviews', title: '我的审核', desc: '待审核任务', icon: Finished, bg: '#FFF1F0', color: '#F5222D' },
      { key: 'workflow', title: '我的服务流程', desc: '客户服务流程', icon: Connection, bg: '#FFF0F6', color: '#EB2F96' }
    ]
  },
  {
    title: '财务收支',
    items: [
      { key: 'reimbursements', title: '我的报销', desc: '个人报销记录', icon: Ticket, bg: '#FFF7E6', color: '#FA8C16' },
      { key: 'receivables', title: '我的收款', desc: '收款登记记录', icon: Money, bg: '#F6FFED', color: '#52C41A' },
      { key: 'payables', title: '我的付款', desc: '付款登记记录', icon: Wallet, bg: '#FFF1F0', color: '#F5222D' }
    ]
  },
  {
    title: '安全设置',
    items: [
      { key: 'password', title: '修改登录密码', desc: '账号密码安全', icon: Lock, bg: '#F0F5FF', color: '#2F54EB' }
    ]
  }
]

const currentNav = computed(() => navGroups.flatMap((g) => g.items).find((i) => i.key === activeKey.value))
const currentTitle = computed(() => currentNav.value?.title || '我的工作台')

// 我的线索
const leads = ref([])
const leadsLoading = ref(false)
const leadSearch = ref('')
const leadStatus = ref('')
const leadStatusOptions = [
  { value: '', label: '全部' },
  { value: 'new', label: '新建' },
  { value: 'contacted', label: '已联系' },
  { value: 'converted', label: '已转化' },
  { value: 'lost', label: '已失效' }
]
const leadPage = ref(1)
const leadPageSize = ref(10)
const filteredLeads = computed(() => {
  return leads.value.filter((l) => {
    const text = leadSearch.value.trim().toLowerCase()
    const matchText =
      !text ||
      (l.name || '').toLowerCase().includes(text) ||
      (l.phone || '').toLowerCase().includes(text)
    const matchStatus = !leadStatus.value || (l.status || '') === leadStatus.value
    return matchText && matchStatus
  })
})
const leadTotal = computed(() => filteredLeads.value.length)
const pagedLeads = computed(() => {
  const start = (leadPage.value - 1) * leadPageSize.value
  return filteredLeads.value.slice(start, start + leadPageSize.value)
})
const loadLeads = async () => {
  if (!userId.value) return
  leadsLoading.value = true
  try {
    const res = await request.get('/leads', { params: { assigned_to: userId.value } })
    leads.value = normalizeList(res)
  } catch (e) {
    ElMessage.error('加载线索失败')
  } finally {
    leadsLoading.value = false
  }
}
const leadDialogVisible = ref(false)
const leadFormRef = ref(null)
const leadForm = reactive({ name: '', phone: '', source: '', status: 'new' })
const leadRules = {
  name: [{ required: true, message: '请输入线索名称', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }]
}
const openLeadDialog = () => {
  leadForm.name = ''
  leadForm.phone = ''
  leadForm.source = ''
  leadForm.status = 'new'
  leadDialogVisible.value = true
}
const submitLead = async () => {
  try {
    await leadFormRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    await request.post('/leads', { ...leadForm, assigned_to: userId.value })
    ElMessage.success('线索创建成功')
    leadDialogVisible.value = false
    loadLeads()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}
const updateLeadStatus = async (row, status) => {
  if (!status) return
  try {
    await request.put(`/leads/${row.id}`, { status })
    ElMessage.success('状态已更新')
    loadLeads()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

// 我的客户
const customers = ref([])
const customersLoading = ref(false)
const custSearch = ref('')
const custPage = ref(1)
const custPageSize = ref(10)
const filteredCustomers = computed(() => {
  const text = custSearch.value.trim().toLowerCase()
  if (!text) return customers.value
  return customers.value.filter((c) => (c.name || '').toLowerCase().includes(text))
})
const custTotal = computed(() => filteredCustomers.value.length)
const pagedCustomers = computed(() => {
  const start = (custPage.value - 1) * custPageSize.value
  return filteredCustomers.value.slice(start, start + custPageSize.value)
})
const loadCustomers = async () => {
  customersLoading.value = true
  try {
    const res = await request.get('/customers')
    customers.value = normalizeList(res)
  } catch (e) {
    ElMessage.error('加载客户失败')
  } finally {
    customersLoading.value = false
  }
}

// 我的楼盘
const buildings = ref([])
const buildingsLoading = ref(false)
const buildingSearch = ref('')
const buildingPage = ref(1)
const buildingPageSize = ref(10)
const filteredBuildings = computed(() => {
  const text = buildingSearch.value.trim().toLowerCase()
  if (!text) return buildings.value
  return buildings.value.filter(
    (b) =>
      (b.name || '').toLowerCase().includes(text) ||
      (b.district || '').toLowerCase().includes(text) ||
      (b.address || '').toLowerCase().includes(text)
  )
})
const buildingTotal = computed(() => filteredBuildings.value.length)
const pagedBuildings = computed(() => {
  const start = (buildingPage.value - 1) * buildingPageSize.value
  return filteredBuildings.value.slice(start, start + buildingPageSize.value)
})
const loadBuildings = async () => {
  buildingsLoading.value = true
  try {
    const res = await request.get('/buildings')
    buildings.value = normalizeList(res)
  } catch (e) {
    ElMessage.error('加载楼盘失败')
  } finally {
    buildingsLoading.value = false
  }
}

// 我的合同
const contracts = ref([])
const contractsLoading = ref(false)
const contractSearch = ref('')
const contractStatus = ref('')
const contractStatusOptions = [
  { value: '', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'pending', label: '待审核' },
  { value: 'signed', label: '已签约' },
  { value: 'cancelled', label: '已取消' }
]
const contractPage = ref(1)
const contractPageSize = ref(10)
const filteredContracts = computed(() => {
  return contracts.value.filter((c) => {
    const text = contractSearch.value.trim().toLowerCase()
    const matchText =
      !text ||
      (c.contract_no || '').toLowerCase().includes(text) ||
      (c.customer_name || '').toLowerCase().includes(text)
    const matchStatus = !contractStatus.value || (c.status || '') === contractStatus.value
    return matchText && matchStatus
  })
})
const contractTotal = computed(() => filteredContracts.value.length)
const pagedContracts = computed(() => {
  const start = (contractPage.value - 1) * contractPageSize.value
  return filteredContracts.value.slice(start, start + contractPageSize.value)
})
const loadContracts = async () => {
  contractsLoading.value = true
  try {
    const res = await request.get('/contracts')
    contracts.value = normalizeList(res)
  } catch (e) {
    ElMessage.error('加载合同失败')
  } finally {
    contractsLoading.value = false
  }
}

// 我的报价
const quotes = ref([])
const quotesLoading = ref(false)
const quoteSearch = ref('')
const quotePage = ref(1)
const quotePageSize = ref(10)
const filteredQuotes = computed(() => {
  const text = quoteSearch.value.trim().toLowerCase()
  if (!text) return quotes.value
  return quotes.value.filter(
    (q) =>
      (q.quote_no || '').toLowerCase().includes(text) ||
      (q.customer_name || '').toLowerCase().includes(text)
  )
})
const quoteTotal = computed(() => filteredQuotes.value.length)
const pagedQuotes = computed(() => {
  const start = (quotePage.value - 1) * quotePageSize.value
  return filteredQuotes.value.slice(start, start + quotePageSize.value)
})
const loadQuotes = async () => {
  quotesLoading.value = true
  try {
    const res = await request.get('/quotes')
    quotes.value = normalizeList(res)
  } catch (e) {
    ElMessage.error('加载报价失败')
  } finally {
    quotesLoading.value = false
  }
}

// 我的团队
const teamLoading = ref(false)
const teamInfo = ref({})
const teamMembers = ref([])
const loadTeam = async () => {
  teamLoading.value = true
  try {
    const me = await request.get('/auth/me')
    teamInfo.value = me || {}
    const params = {}
    if (me?.department_id) params.department_id = me.department_id
    if (me?.store_id) params.store_id = me.store_id
    const res = await request.get('/employees', { params })
    let list = normalizeList(res)
    if (me?.department_id || me?.store_id) {
      list = list.filter(
        (m) =>
          (me.department_id && m.department_id === me.department_id) ||
          (me.store_id && m.store_id === me.store_id)
      )
    }
    teamMembers.value = list
  } catch (e) {
    ElMessage.error('加载团队失败')
  } finally {
    teamLoading.value = false
  }
}

// 修改密码
const passwordFormRef = ref(null)
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}
const submitPassword = async () => {
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }
  try {
    const res = await request.post('/auth/change-password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    if (res && (res.ok || res.success || res.id || true)) {
      ElMessage.success('密码修改成功，请重新登录')
      handleLogout()
    } else {
      ElMessage.error(res?.message || '修改失败')
    }
  } catch (e) {
    ElMessage.error('修改失败：' + (e.response?.data?.message || e.message))
  }
}

// 登出
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}

// 按 Tab 加载数据
const loadByKey = (key) => {
  switch (key) {
    case 'leads':
      loadLeads()
      break
    case 'customers':
      loadCustomers()
      break
    case 'buildings':
      loadBuildings()
      break
    case 'contracts':
      loadContracts()
      break
    case 'quotes':
      loadQuotes()
      break
    case 'team':
      loadTeam()
      break
  }
}

watch(activeKey, (val) => {
  router.replace({ query: { ...route.query, tab: val } })
  loadByKey(val)
})

watch(
  () => route.query.tab,
  (val) => {
    if (val && val !== activeKey.value) {
      activeKey.value = val
    }
  }
)

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userId.value = user.id || user.user_id || ''
    } catch {
      userId.value = ''
    }
  }
  loadByKey(activeKey.value)
})
</script>

<style scoped>
.workspace-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: calc(100vh - 60px - 40px);
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.top-bar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.top-left,
.top-right {
  display: flex;
  align-items: center;
}

.top-center {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.workspace-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.workspace-sidebar {
  width: 280px;
  min-width: 280px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.sidebar-header h3 {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 600;
  color: #262626;
}

.sidebar-desc {
  margin: 0;
  font-size: 12px;
  color: #8c8c8c;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.nav-group {
  margin-bottom: 16px;
}

.nav-section-title {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 8px;
  padding-left: 8px;
  letter-spacing: 0.5px;
}

.nav-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 6px;
  border: 2px solid transparent;
}

.nav-card:hover {
  background: #f5f7fa;
}

.nav-card.active {
  background: #fff;
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.12);
}

.nav-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-info {
  flex: 1;
  min-width: 0;
}

.nav-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  line-height: 1.4;
}

.nav-desc {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.workspace-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.tab-panel {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  min-height: 100%;
}

.embedded-view {
  padding: 0;
  background: transparent;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.team-info {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: center;
}

:deep(.el-pagination) {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
