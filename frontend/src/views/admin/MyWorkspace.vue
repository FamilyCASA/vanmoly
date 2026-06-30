<template>
  <div class="workspace-layout">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="top-left">
        <el-button v-if="canEnterAdmin" :icon="ArrowLeft" text @click="router.push('/admin/dashboard')">
          返回管理后台
        </el-button>
        <el-button v-else :icon="ArrowLeft" text @click="router.push('/')">
          返回前台
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
          <!-- 我的概览 -->
          <div v-if="activeKey === 'overview'" class="tab-panel overview-panel">
            <!-- 个人英雄区 -->
            <div class="dash-hero">
              <div class="dash-hero-left">
                <div class="dash-avatar">{{ userInitial }}</div>
                <div class="dash-hero-info">
                  <div class="dash-hero-title">
                    <h2>{{ currentUserName }}</h2>
                    <el-tag :type="canEnterAdmin ? 'success' : 'info'" size="small">{{ roleLabel(currentUser.role) }}</el-tag>
                  </div>
                  <p class="dash-hero-desc">{{ greetingText }}，以下是你的专属数据概览。</p>
                  <div class="dash-hero-meta">
                    <span>{{ nowText }}</span>
                    <span v-if="myOverviewData">数据实时同步</span>
                  </div>
                </div>
              </div>
              <div class="dash-hero-right">
                <el-button :icon="Refresh" :loading="overviewLoading" @click="loadMyOverview">刷新</el-button>
              </div>
            </div>

            <!-- KPI 卡片网格 -->
            <div v-loading="overviewLoading" class="dash-kpi-grid">
              <div class="dash-kpi-card" v-for="card in kpiCards" :key="card.label"
                :style="{ '--kpi-color': card.color, '--kpi-bg': card.bg }">
                <div class="kpi-top">
                  <div class="kpi-icon-box" :style="{ background: card.bg }">
                    <el-icon :size="20" :color="card.color"><component :is="card.icon" /></el-icon>
                  </div>
                  <span class="kpi-chip" :style="{ color: card.color, background: card.bg }">{{ card.chip }}</span>
                </div>
                <div class="kpi-num">{{ card.value }}</div>
                <div class="kpi-name">{{ card.label }}</div>
                <div class="kpi-sub">
                  <span>{{ card.subLabel }}</span>
                  <strong :style="{ color: card.color }">{{ card.subValue }}</strong>
                </div>
              </div>
            </div>

            <!-- 图表 + 待办 -->
            <div class="dash-mid-grid">
              <div class="dash-chart-card">
                <div class="dash-card-header">
                  <span class="dash-card-title">月度业务趋势</span>
                  <span class="dash-card-sub">最近6个月线索/客户/报价</span>
                </div>
                <div ref="myTrendChartRef" class="dash-chart-box"></div>
              </div>
              <div class="dash-todo-card">
                <div class="dash-card-header">
                  <span class="dash-card-title">待办提醒</span>
                  <span class="dash-card-sub">需要优先处理的事项</span>
                </div>
                <div class="dash-todo-list">
                  <div v-for="item in todoItems" :key="item.label" class="dash-todo-item"
                    :style="{ '--todo-bg': item.bg }" @click="activeKey = item.tab">
                    <div class="dash-todo-icon">
                      <el-icon :size="18"><component :is="item.icon" /></el-icon>
                    </div>
                    <div class="dash-todo-body">
                      <strong>{{ item.value }}</strong>
                      <span>{{ item.label }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 近期动态 -->
            <div class="dash-activity-card">
              <div class="dash-card-header">
                <span class="dash-card-title">近期动态</span>
                <span class="dash-card-sub">你最近的业务记录</span>
              </div>
              <div class="dash-activity-list">
                <div v-for="(item, idx) in myOverviewData?.recent_activities || []" :key="idx" class="dash-activity-item">
                  <div class="dash-activity-dot" :class="item.type"></div>
                  <div class="dash-activity-content">
                    <div class="dash-activity-title">{{ item.title }}</div>
                    <div class="dash-activity-desc">{{ item.desc }} · <el-tag size="small" :type="statusTagType(item.status)">{{ statusLabel(item.status) }}</el-tag></div>
                  </div>
                  <div class="dash-activity-time">{{ item.time }}</div>
                </div>
                <div v-if="!myOverviewData?.recent_activities?.length" class="dash-empty">暂无近期动态</div>
              </div>
            </div>

            <!-- 可操作范围 -->
            <div class="access-panel">
              <div class="panel-title">当前可操作范围</div>
              <div class="access-list">
                <div v-for="item in allowedFlatItems" :key="item.key" class="access-item" @click="activeKey = item.key">
                  <div class="access-icon" :style="{ background: item.bg, color: item.color }">
                    <el-icon><component :is="item.icon" /></el-icon>
                  </div>
                  <div>
                    <div class="access-title">{{ item.title }}</div>
                    <div class="access-desc">{{ item.desc }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

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

          <!-- 我的项目小组 -->
          <div v-if="activeKey === 'projects'" v-loading="projectsLoading" class="tab-panel">
            <div class="search-bar">
              <el-input v-model="projectSearch" placeholder="搜索项目名称/编码" clearable style="width: 260px" />
              <el-select v-model="projectStatus" placeholder="状态筛选" clearable style="width: 140px">
                <el-option v-for="opt in projectStatusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
              <el-button type="primary" @click="loadProjects">查询</el-button>
            </div>
            <div v-if="projectList.length" class="project-cards">
              <div v-for="proj in filteredProjects" :key="proj.id" class="project-card">
                <div class="project-card-header">
                  <div class="project-name">
                    <el-tag v-if="proj.status === 'active'" type="success" size="small">进行中</el-tag>
                    <el-tag v-else-if="proj.status === 'planning'" type="warning" size="small">规划中</el-tag>
                    <el-tag v-else-if="proj.status === 'completed'" type="info" size="small">已完成</el-tag>
                    <el-tag v-else size="small">{{ proj.status }}</el-tag>
                    <span class="name-text">{{ proj.name }}</span>
                  </div>
                  <span class="project-code">{{ proj.code || `#${proj.id}` }}</span>
                </div>
                <div class="project-card-body">
                  <div class="project-meta">
                    <div class="meta-item">
                      <span class="meta-label">负责人</span>
                      <span class="meta-value">{{ proj.owner_name || '-' }}</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">类型</span>
                      <span class="meta-value">{{ proj.project_type || '-' }}</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">进度</span>
                      <span class="meta-value">{{ proj.progress || 0 }}%</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">成员</span>
                      <span class="meta-value">{{ proj.member_count || 0 }}人</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">待办任务</span>
                      <span class="meta-value">{{ proj.pending_task_count || 0 }}</span>
                    </div>
                  </div>
                  <div v-if="proj.objective" class="project-objective">{{ proj.objective }}</div>
                </div>
                <div class="project-card-footer">
                  <el-button size="small" @click="toggleProjectDetail(proj)">
                    {{ proj._expanded ? '收起' : '查看成员与任务' }}
                  </el-button>
                </div>
                <div v-if="proj._expanded" class="project-detail">
                  <div class="detail-section">
                    <div class="detail-title">项目成员</div>
                    <el-table :data="proj._members || []" size="small" border>
                      <el-table-column prop="employee_name" label="姓名" width="100" />
                      <el-table-column label="角色" width="90">
                        <template #default="{ row }">
                          <el-tag v-if="row.is_leader" type="warning" size="small">组长</el-tag>
                          <span v-else>{{ row.role_code }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="responsibility" label="职责" min-width="140" show-overflow-tooltip />
                      <el-table-column prop="workload" label="工作量" width="80" />
                    </el-table>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title">任务列表</div>
                    <el-table :data="(proj._tasks || []).slice(0, 10)" size="small" border>
                      <el-table-column prop="title" label="任务" min-width="140" show-overflow-tooltip />
                      <el-table-column label="状态" width="90">
                        <template #default="{ row }">
                          <el-tag :type="taskStatusTag(row.status)" size="small">{{ taskStatusLabel(row.status) }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="优先级" width="70">
                        <template #default="{ row }">
                          <el-tag v-if="row.priority === 'urgent'" type="danger" size="small">紧急</el-tag>
                          <el-tag v-else-if="row.priority === 'high'" type="warning" size="small">高</el-tag>
                          <span v-else>{{ row.priority || '普通' }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="截止" width="100">
                        <template #default="{ row }">{{ row.due_date ? row.due_date.slice(0, 10) : '-' }}</template>
                      </el-table-column>
                    </el-table>
                    <div v-if="(proj._tasks || []).length > 10" class="more-tasks">
                      还有 {{ (proj._tasks || []).length - 10 }} 条任务...
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-if="!projectsLoading && !projectList.length" description="暂无参与的项目小组" />
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
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElTable, ElTableColumn, ElButton, ElTag, ElInput, ElSelect, ElOption, ElPagination,
  ElMessage, ElMessageBox, ElForm, ElFormItem, ElDialog
} from 'element-plus'
import {
  ArrowLeft, SwitchButton, User, OfficeBuilding, Document, Money,
  Promotion, Share, Finished, Connection, Wallet, Ticket, Lock,
  Refresh, TrendCharts, DocumentChecked, List, Calendar
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import { getMyOverview } from '@/api/dashboard'
import ApprovalTasks from '@/views/finance/ApprovalTasks.vue'
import MyReimbursements from '@/views/finance/MyReimbursements.vue'
import MyReceivables from '@/views/finance/MyReceivables.vue'
import MyPayables from '@/views/finance/MyPayables.vue'
import ServiceWorkflow from '@/views/admin/ServiceWorkflow.vue'

const route = useRoute()
const router = useRouter()

const activeKey = ref(route.query.tab || 'overview')
const userId = ref('')
const submitting = ref(false)
const permissionProfile = ref(null)
const permissionLoaded = ref(false)

const localUser = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
})
const currentUser = computed(() => permissionProfile.value?.user || localUser.value || {})
const currentUserName = computed(() => currentUser.value.nickname || currentUser.value.name || currentUser.value.username || '员工')
const userInitial = computed(() => currentUserName.value.slice(0, 1))
const currentRole = computed(() => currentUser.value.role || 'staff')
const isManagerLike = computed(() => ['super_admin', 'admin', 'manager'].includes(currentRole.value))
const visibleModuleKeys = computed(() => (permissionProfile.value?.visible_modules || []).map((item) => item.key))
const permissionKeys = computed(() => (permissionProfile.value?.permissions || []).map((item) => item.permission_key))
const myProjectCount = computed(() => (permissionProfile.value?.projects || []).length)
const myTaskCount = computed(() => (permissionProfile.value?.task_cards || []).length)
const canEnterAdmin = computed(() => visibleModuleKeys.value.includes('dashboard'))
const roleLabel = (role) => {
  const labels = {
    super_admin: '超级管理员',
    admin: '管理员',
    manager: '门店店长',
    staff: '员工',
    employee: '员工',
    customer: '客户'
  }
  return labels[role] || '员工'
}

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
const baseNavGroups = [
  {
    title: '个人中心',
    items: [
      { key: 'overview', title: '我的概览', desc: '账号与权限状态', icon: User, bg: '#E6F7FF', color: '#1890FF' }
    ]
  },
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
      { key: 'projects', title: '我的项目小组', desc: '参与的项目组', icon: Connection, bg: '#E6F7FF', color: '#1890FF' },
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

const moduleNavMap = {
  leads: ['leads'],
  customers: ['customers'],
  buildings: ['buildings'],
  contracts: ['contracts'],
  quotes: ['quotes'],
  team: ['settings', 'dashboard'],
  reviews: ['finance', 'quotes', 'workflow'],
  workflow: ['workflow'],
  receivables: ['finance'],
  payables: ['finance']
}
const permissionNavMap = {
  team: ['employee.view', 'employee.permission.assign'],
  projects: ['project.view', 'project.manage'],
  reviews: ['expense.approve', 'payment.confirm', 'quote.approve', 'task.review', 'workflow.review'],
  workflow: ['workflow.view', 'workflow.manage'],
  receivables: ['finance.receivable.view', 'finance.manage'],
  payables: ['finance.payable.view', 'finance.manage']
}
const baseEntryKeys = ['overview', 'reimbursements', 'password']
const hasAny = (source, targets) => targets.some((target) => source.includes(target))
const canShowNavItem = (key) => {
  if (baseEntryKeys.includes(key)) return true
  if (key === 'projects') return isManagerLike.value || myProjectCount.value > 0 || hasAny(permissionKeys.value, permissionNavMap.projects)
  if (moduleNavMap[key] && hasAny(visibleModuleKeys.value, moduleNavMap[key])) return true
  if (permissionNavMap[key] && hasAny(permissionKeys.value, permissionNavMap[key])) return true
  return false
}
const navGroups = computed(() =>
  baseNavGroups
    .map((group) => ({ ...group, items: group.items.filter((item) => canShowNavItem(item.key)) }))
    .filter((group) => group.items.length)
)
const allowedFlatItems = computed(() => navGroups.value.flatMap((g) => g.items))
const allowedEntryCount = computed(() => allowedFlatItems.value.length)
const isAllowedKey = (key) => allowedFlatItems.value.some((item) => item.key === key)
const firstAllowedKey = computed(() => allowedFlatItems.value[0]?.key || 'overview')
const currentNav = computed(() => allowedFlatItems.value.find((i) => i.key === activeKey.value))
const currentTitle = computed(() => currentNav.value?.title || '我的工作台')

// ========== 个人数据驾驶舱 ==========
const myOverviewData = ref(null)
const overviewLoading = ref(false)
const myTrendChartRef = ref(null)
let trendChart = null

const nowText = computed(() => {
  const d = new Date()
  const h = d.getHours()
  if (h < 12) return `${h.toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')} 上午好`
  if (h < 18) return `${h.toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')} 下午好`
  return `${h.toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')} 晚上好`
})
const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const kpiCards = computed(() => {
  const k = myOverviewData.value?.kpi || {}
  return [
    {
      label: '我的线索',
      value: k.leads?.total ?? '-',
      subLabel: '今日新 / 本月新增',
      subValue: `${k.leads?.today ?? 0} / ${k.leads?.month ?? 0}`,
      chip: '线索',
      icon: Promotion,
      color: '#6366f1',
      bg: 'rgba(99,102,241,0.1)',
    },
    {
      label: '我的客户',
      value: k.customers?.total ?? '-',
      subLabel: '今日新 / 需跟进',
      subValue: `${k.customers?.today ?? 0} / ${k.customers?.follow_up ?? 0}`,
      chip: '客户',
      icon: User,
      color: '#10b981',
      bg: 'rgba(16,185,129,0.1)',
    },
    {
      label: '我的报价',
      value: k.quotes?.total ?? '-',
      subLabel: '审批中 / 已通过',
      subValue: `${k.quotes?.pending ?? 0} / ${k.quotes?.approved ?? 0}`,
      chip: '报价',
      icon: Document,
      color: '#f59e0b',
      bg: 'rgba(245,158,11,0.1)',
    },
    {
      label: '我的合同',
      value: k.contracts?.total ?? '-',
      subLabel: '合同总金额（万元）',
      subValue: ((k.contracts?.amount ?? 0) / 10000).toFixed(1),
      chip: '合同',
      icon: Ticket,
      color: '#ef4444',
      bg: 'rgba(239,68,68,0.1)',
    },
    {
      label: '项目小组',
      value: k.projects?.total ?? '-',
      subLabel: '主持项目',
      subValue: `${k.projects?.leading ?? 0}`,
      chip: '项目',
      icon: Share,
      color: '#8b5cf6',
      bg: 'rgba(139,92,246,0.1)',
    },
    {
      label: '待办任务',
      value: k.tasks?.pending ?? '-',
      subLabel: '待审核 / 已完成',
      subValue: `${k.tasks?.reviewing ?? 0} / ${k.tasks?.completed ?? 0}`,
      chip: '任务',
      icon: List,
      color: '#06b6d4',
      bg: 'rgba(6,182,212,0.1)',
    },
    {
      label: '待跟进线索',
      value: k.leads?.follow_up ?? '-',
      subLabel: '需及时跟进',
      subValue: '线索',
      chip: '跟进',
      icon: Connection,
      color: '#f97316',
      bg: 'rgba(249,115,22,0.1)',
    },
    {
      label: '本月签约额',
      value: ((k.contracts?.amount ?? 0)).toLocaleString('zh-CN', { maximumFractionDigits: 0 }),
      subLabel: '报价累计金额（万元）',
      subValue: ((k.quotes?.amount ?? 0) / 10000).toFixed(1),
      chip: '业绩',
      icon: Money,
      color: '#ec4899',
      bg: 'rgba(236,72,153,0.1)',
    },
  ]
})

const todoItems = computed(() => {
  const k = myOverviewData.value?.kpi || {}
  const items = []
  if (k.leads?.follow_up > 0) items.push({
    label: '条线索待跟进', value: k.leads.follow_up, tab: 'leads',
    icon: Promotion, bg: 'rgba(99,102,241,0.1)'
  })
  if (k.customers?.follow_up > 0) items.push({
    label: '位客户待跟进', value: k.customers.follow_up, tab: 'customers',
    icon: User, bg: 'rgba(16,185,129,0.1)'
  })
  if (k.quotes?.pending > 0) items.push({
    label: '份报价待审批', value: k.quotes.pending, tab: 'quotes',
    icon: Document, bg: 'rgba(245,158,11,0.1)'
  })
  if (k.tasks?.pending > 0) items.push({
    label: '个任务待完成', value: k.tasks.pending, tab: 'projects',
    icon: List, bg: 'rgba(6,182,212,0.1)'
  })
  if (k.tasks?.reviewing > 0) items.push({
    label: '个任务待审核', value: k.tasks.reviewing, tab: 'projects',
    icon: DocumentChecked, bg: 'rgba(139,92,246,0.1)'
  })
  if (k.appointments?.upcoming > 0) items.push({
    label: '场待办预约', value: k.appointments.upcoming, tab: 'appointments',
    icon: Calendar, bg: 'rgba(249,115,22,0.1)'
  })
  if (!items.length) items.push({
    label: '暂无待办，状态良好',
    value: '✓',
    tab: '',
    icon: Finished,
    bg: 'rgba(16,185,129,0.1)'
  })
  return items
})

const loadMyOverview = async () => {
  overviewLoading.value = true
  try {
    const res = await getMyOverview()
    if (res.data?.code === 200) {
      myOverviewData.value = res.data.data
      nextTick(() => renderTrendChart())
    }
  } catch (e) {
    console.error('loadMyOverview error', e)
  } finally {
    overviewLoading.value = false
  }
}

const renderTrendChart = async () => {
  if (!myTrendChartRef.value) return
  const echarts = await import('echarts')
  if (trendChart) trendChart.dispose()
  const el = myTrendChartRef.value
  trendChart = echarts.init(el)
  const trend = myOverviewData.value?.monthly_trend || []
  const months = trend.map((t) => t.month)
  const leadsData = trend.map((t) => t.leads)
  const custData = trend.map((t) => t.customers)
  const quoteData = trend.map((t) => t.quotes)
  trendChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['线索', '客户', '报价'], bottom: 0, textStyle: { fontSize: 11 } },
    grid: { left: 40, right: 16, top: 10, bottom: 40 },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { fontSize: 10 } },
    series: [
      { name: '线索', type: 'bar', data: leadsData, itemStyle: { color: '#6366f1' } },
      { name: '客户', type: 'bar', data: custData, itemStyle: { color: '#10b981' } },
      { name: '报价', type: 'line', data: quoteData, smooth: true, itemStyle: { color: '#f59e0b' }, lineStyle: { width: 2 } },
    ],
  })
}

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

// 我的项目小组
const projectsLoading = ref(false)
const projectList = ref([])
const projectSearch = ref('')
const projectStatus = ref('')
const projectStatusOptions = [
  { value: '', label: '全部' },
  { value: 'planning', label: '规划中' },
  { value: 'active', label: '进行中' },
  { value: 'completed', label: '已完成' }
]
const filteredProjects = computed(() => {
  return projectList.value.filter((p) => {
    const text = projectSearch.value.trim().toLowerCase()
    const matchText = !text || (p.name || '').toLowerCase().includes(text) || (p.code || '').toLowerCase().includes(text)
    const matchStatus = !projectStatus.value || (p.status || '') === projectStatus.value
    return matchText && matchStatus
  })
})
const taskStatusTag = (status) => {
  const s = String(status || '').toLowerCase()
  if (['draft', 'published'].includes(s)) return 'info'
  if (['accepted', 'in_progress', 'submitted', 'rework'].includes(s)) return 'warning'
  if (['completed', 'done'].includes(s)) return 'success'
  if (['cancelled', 'rejected'].includes(s)) return 'danger'
  return 'info'
}
const taskStatusLabel = (status) => {
  const labels = {
    draft: '草稿', published: '待领取', accepted: '已接受', in_progress: '进行中',
    submitted: '已提交', rework: '返工', completed: '已完成', cancelled: '已取消'
  }
  return labels[status] || status || '-'
}
const toggleProjectDetail = async (proj) => {
  if (proj._expanded) {
    proj._expanded = false
    return
  }
  if (proj._members) {
    proj._expanded = true
    return
  }
  try {
    const detail = await request.get(`/project-teams/${proj.id}`)
    proj._members = detail.members || []
    proj._tasks = detail.tasks || []
    proj._expanded = true
  } catch (e) {
    ElMessage.error('加载项目详情失败')
  }
}
const loadProjects = async () => {
  projectsLoading.value = true
  try {
    const res = await request.get('/project-teams', { params: { pageSize: 100 } })
    const data = res || {}
    projectList.value = (data.items || []).map((p) => ({ ...p, _expanded: false }))
  } catch (e) {
    ElMessage.error('加载项目小组失败')
  } finally {
    projectsLoading.value = false
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

const loadPermissionProfile = async () => {
  try {
    permissionProfile.value = await request.get('/permissions/me')
  } catch (e) {
    permissionProfile.value = {
      user: localUser.value,
      permissions: [],
      visible_modules: [],
      projects: [],
      task_cards: []
    }
  } finally {
    permissionLoaded.value = true
  }
}

loadMyOverview()

const normalizeActiveKey = () => {
  if (!permissionLoaded.value) return
  if (!isAllowedKey(activeKey.value)) {
    activeKey.value = firstAllowedKey.value
  }
}

// 按 Tab 加载数据
const loadByKey = (key) => {
  if (!permissionLoaded.value || !isAllowedKey(key)) return
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
    case 'projects':
      loadProjects()
      break
    case 'team':
      loadTeam()
      break
  }
}

watch(activeKey, (val) => {
  if (!permissionLoaded.value) return
  if (!isAllowedKey(val)) {
    normalizeActiveKey()
    return
  }
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
  loadPermissionProfile().then(() => {
    normalizeActiveKey()
    loadByKey(activeKey.value)
  })
})

watch([permissionLoaded, allowedFlatItems], () => {
  normalizeActiveKey()
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

.overview-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ========== 个人数据驾驶舱样式 ========== */
.dash-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  margin-bottom: 20px;
}
.dash-hero-left { display: flex; gap: 18px; align-items: center; }
.dash-avatar {
  width: 64px; height: 64px; border-radius: 14px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.dash-hero-info { flex: 1; min-width: 0; }
.dash-hero-title { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
.dash-hero-title h2 { margin: 0; font-size: 24px; color: #fff; }
.dash-hero-desc { margin: 0; color: rgba(255,255,255,0.8); font-size: 14px; }
.dash-hero-meta { display: flex; gap: 16px; margin-top: 6px; font-size: 12px; color: rgba(255,255,255,0.6); }
.dash-hero-right { flex-shrink: 0; }
.dash-hero-right .el-button { color: #fff; border-color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); }

.dash-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}
.dash-kpi-card {
  padding: 18px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #eef0f5;
  position: relative;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.dash-kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}
.dash-kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--kpi-color);
}
.kpi-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.kpi-icon-box {
  width: 36px; height: 36px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.kpi-chip {
  font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 500;
}
.kpi-num {
  font-size: 28px; font-weight: 700; color: #172033; line-height: 1;
}
.kpi-name {
  margin-top: 6px; font-size: 13px; color: #7a8699;
}
.kpi-sub {
  margin-top: 8px; font-size: 12px; color: #98a2b3;
  display: flex; gap: 4px; align-items: center;
}

.dash-mid-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.dash-chart-card, .dash-todo-card, .dash-activity-card {
  background: #fff;
  border: 1px solid #eef0f5;
  border-radius: 10px;
  padding: 18px;
}
.dash-card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 14px; }
.dash-card-title { font-size: 16px; font-weight: 600; color: #1f2f46; }
.dash-card-sub { font-size: 12px; color: #98a2b3; }
.dash-chart-box { height: 240px; }

.dash-todo-list { display: flex; flex-direction: column; gap: 10px; }
.dash-todo-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 8px; background: var(--todo-bg, #f8f9fb);
  cursor: pointer; transition: background 0.15s;
}
.dash-todo-item:hover { background: #eef0f5; }
.dash-todo-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: rgba(255,255,255,0.6);
  display: flex; align-items: center; justify-content: center;
  color: #5a6a80; flex-shrink: 0;
}
.dash-todo-body { display: flex; flex-direction: column; }
.dash-todo-body strong { font-size: 18px; color: #172033; }
.dash-todo-body span { font-size: 12px; color: #7a8699; }

.dash-activity-card { margin-bottom: 20px; }
.dash-activity-list { display: flex; flex-direction: column; }
.dash-activity-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}
.dash-activity-item:last-child { border-bottom: none; }
.dash-activity-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.dash-activity-dot.lead { background: #6366f1; }
.dash-activity-dot.quote { background: #f59e0b; }
.dash-activity-dot.customer { background: #10b981; }
.dash-activity-content { flex: 1; min-width: 0; }
.dash-activity-title { font-size: 14px; font-weight: 500; color: #1f2f46; }
.dash-activity-desc { font-size: 12px; color: #7a8699; margin-top: 2px; }
.dash-activity-time { font-size: 12px; color: #98a2b3; flex-shrink: 0; }
.dash-empty { text-align: center; color: #98a2b3; padding: 24px 0; font-size: 13px; }

/* ========== 旧概览样式（保留兼容） ========== */
.employee-hero {
  display: flex;
  gap: 18px;
  align-items: center;
  padding: 22px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f8fbff 0%, #eef7ff 100%);
  border: 1px solid #dcecff;
}

.employee-avatar {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  background: #1677ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: 700;
  flex-shrink: 0;
}

.employee-main {
  flex: 1;
  min-width: 0;
}

.employee-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.employee-title-row h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2f46;
}

.employee-main p {
  margin: 0;
  color: #5f6f89;
  line-height: 1.7;
  max-width: 720px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.overview-card {
  padding: 18px;
  border: 1px solid #eef0f5;
  border-radius: 8px;
  background: #fff;
}

.overview-label {
  font-size: 13px;
  color: #7a8699;
}

.overview-value {
  margin-top: 8px;
  font-size: 30px;
  font-weight: 700;
  color: #172033;
  line-height: 1;
}

.overview-note {
  margin-top: 10px;
  font-size: 12px;
  color: #98a2b3;
}

.access-panel {
  border: 1px solid #eef0f5;
  border-radius: 8px;
  padding: 18px;
  background: #fff;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f46;
  margin-bottom: 14px;
}

.access-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.access-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eef0f5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.access-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 14px rgba(64, 158, 255, 0.12);
}

.access-icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.access-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.access-desc {
  margin-top: 2px;
  font-size: 12px;
  color: #8c8c8c;
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

.project-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.project-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.project-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid #f0f0f0;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-name .name-text {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
}

.project-code {
  font-size: 12px;
  color: #8c8c8c;
}

.project-card-body {
  padding: 14px 18px;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 12px;
  color: #8c8c8c;
}

.meta-value {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.project-objective {
  font-size: 13px;
  color: #595959;
  margin-top: 8px;
  line-height: 1.6;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.project-card-footer {
  padding: 0 18px 12px;
}

.project-detail {
  border-top: 1px solid #f0f0f0;
  padding: 16px 18px;
  background: #fafbfc;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-title {
  font-size: 13px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 10px;
}

.more-tasks {
  text-align: center;
  font-size: 12px;
  color: #8c8c8c;
  padding: 8px 0;
}

:deep(.el-pagination) {
  margin-top: 16px;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .workspace-body {
    flex-direction: column;
  }

  .workspace-sidebar {
    width: 100%;
    min-width: 0;
    max-height: 320px;
    border-right: 0;
    border-bottom: 1px solid #f0f0f0;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .dash-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dash-mid-grid {
    grid-template-columns: 1fr;
  }

  .employee-hero {
    align-items: flex-start;
  }
}
</style>
