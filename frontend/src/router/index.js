import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', hasHero: true }
  },
  {
    path: '/cases',
    name: 'CaseList',
    component: () => import('@/views/cases/CaseList.vue'),
    meta: { title: '案例展示', hasHero: true }
  },
  {
    path: '/cases/:id',
    name: 'CaseDetail',
    component: () => import('@/views/cases/CaseDetailV2.vue'),
    meta: { title: '案例详情' }
  },
  {
    path: '/my-subscriptions',
    name: 'MySubscriptions',
    component: () => import('@/views/cases/MySubscriptions.vue'),
    meta: { title: '我的订阅' }
  },
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('@/views/products/ProductList.vue'),
    meta: { title: '产品中心', hasHero: true }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/views/products/ProductDetailV2.vue'),
    meta: { title: '产品详情' }
  },
  {
    path: '/proposals',
    name: 'ProposalList',
    component: () => import('@/views/proposals/ProposalList.vue'),
    meta: { title: '提案中心', hasHero: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeIndex',
    component: () => import('@/views/knowledge/KnowledgeIndex.vue'),
    meta: { title: '商学院知识库' }
  },
  {
    path: '/leads',
    name: 'LeadList',
    component: () => import('@/views/leads/LeadList.vue'),
    meta: { title: '线索管理', requiresAuth: true }
  },
  {
    path: '/book',
    name: 'Appointment',
    component: () => import('@/views/Appointment.vue'),
    meta: { title: '预约量尺', hasHero: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginV2.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/customer/login',
    name: 'CustomerLogin',
    component: () => import('@/views/CustomerLogin.vue'),
    meta: { title: '客户登录', public: true }
  },
  {
    path: '/register',
    name: 'CustomerRegister',
    component: () => import('@/views/CustomerRegister.vue'),
    meta: { title: '客户注册', public: true }
  },
  {
    path: '/user-center',
    name: 'UserCenter',
    component: () => import('@/views/UserCenter.vue'),
    meta: { title: '用户中心', public: true, hasHero: true }
  },
  {
    path: '/selection-center',
    name: 'SelectionCenter',
    component: () => import('@/views/SelectionCenter.vue'),
    meta: { title: '我的选品中心', requiresAuth: true, isCustomerAuth: true }
  },
  {
    path: '/demo/selection-button',
    name: 'SelectionButtonDemo',
    component: () => import('@/views/demo/SelectionButtonDemo.vue'),
    meta: { title: '选品按钮演示', public: true }
  },
  {
    path: '/demo/debug-selection',
    name: 'DebugSelection',
    component: () => import('@/views/demo/DebugSelection.vue'),
    meta: { title: '选品调试', public: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { title: '管理后台', requiresAuth: true },
    children: [
      {
        path: 'cases',
        name: 'AdminCases',
        component: () => import('@/views/admin/CaseManage.vue'),
        meta: { title: '案例管理' }
      },
      {
        path: 'cases/create',
        name: 'AdminCaseCreate',
        component: () => import('@/views/admin/CaseEdit.vue'),
        meta: { title: '新建案例' }
      },
      {
        path: 'cases/edit/:id',
        name: 'AdminCaseEdit',
        component: () => import('@/views/admin/CaseEdit.vue'),
        meta: { title: '编辑案例' }
      },
      {
        path: 'case-leads',
        name: 'AdminCaseLeads',
        component: () => import('@/views/admin/CaseLeadManage.vue'),
        meta: { title: '客资管理' }
      },
      {
        path: 'leads',
        name: 'AdminLeads',
        component: () => import('@/views/admin/LeadManageV2.vue'),
        meta: { title: '线索管理 V2.0' }
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据看板' }
      },
      {
        path: 'appointments',
        name: 'AdminAppointments',
        component: () => import('@/views/admin/AppointmentManage.vue'),
        meta: { title: '预约管理' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/SettingsLayout.vue'),
        meta: { title: '系统设置' }
      },

      {
        path: 'knowledge',
        name: 'AdminKnowledge',
        component: () => import('@/views/admin/KnowledgeManage.vue'),
        meta: { title: '知识库管理' }
      },
      {
        path: 'customers',
        name: 'AdminCustomers',
        component: () => import('@/views/admin/CustomerManage.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'customers/:id',
        name: 'AdminCustomerDetail',
        component: () => import('@/views/admin/CustomerDetail.vue'),
        meta: { title: '客户详情' }
      },
      {
        path: 'workflow',
        name: 'AdminWorkflow',
        component: () => import('@/views/admin/ServiceWorkflow.vue'),
        meta: { title: '服务流程' }
      },
      {
        path: 'contracts',
        name: 'AdminContracts',
        component: () => import('@/views/admin/ContractManage.vue'),
        meta: { title: '合同管理' }
      },
      {
        path: 'buildings',
        name: 'AdminBuildings',
        component: () => import('@/views/admin/BuildingManage.vue'),
        meta: { title: '楼盘管理' }
      },
      {
        path: 'buildings/survey/:id',
        name: 'BuildingSurveyEdit',
        component: () => import('@/views/admin/BuildingSurveyEdit.vue'),
        meta: { title: '楼盘调查' }
      },
      {
        path: 'quotes',
        name: 'AdminQuotes',
        component: () => import('@/views/admin/QuoteManage.vue'),
        meta: { title: '报价管理' }
      },
      {
        path: 'quotes/from-case',
        name: 'QuoteFromCase',
        component: () => import('@/views/admin/QuoteFromCase.vue'),
        meta: { title: '从案例创建报价' }
      },
      {
        path: 'quotes/:id',
        name: 'QuoteDetail',
        component: () => import('@/views/admin/QuoteDetail.vue'),
        meta: { title: '报价预览' }
      },
      {
        path: 'quote-templates',
        name: 'QuoteTemplateSettings',
        component: () => import('@/views/admin/QuoteTemplateSettings.vue'),
        meta: { title: '模板管理' }
      },
      {
        path: 'schemes',
        name: 'AdminSchemes',
        component: () => import('@/views/admin/SchemeManage.vue'),
        meta: { title: '方案管理' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManageV2.vue'),
        meta: { title: '用户权限' }
      },
      // 组织架构管理
      {
        path: 'org-structure',
        name: 'AdminOrgStructure',
        component: () => import('@/views/admin/OrgStructureManage.vue'),
        meta: { title: '组织架构' }
      },
      // 个人工作台（独立页面，非财务管理子模块）
      {
        path: 'my-workspace',
        name: 'MyWorkspace',
        component: () => import('@/views/admin/MyWorkspace.vue'),
        meta: { title: '我的工作台' }
      },
      // 财务管理（嵌入 AdminLayout，Tab 切换子模块）
      {
        path: 'finance',
        name: 'AdminFinance',
        component: () => import('@/views/finance/FinanceLayout.vue'),
        meta: { title: '财务管理' }
      },
      // 权限矩阵
      {
        path: 'permission-center',
        name: 'PermissionCenter',
        component: () => import('@/views/admin/PermissionCenter.vue'),
        meta: { title: '权限矩阵' }
      },
      // 项目组织协同
      {
        path: 'project-organization',
        name: 'ProjectOrganization',
        component: () => import('@/views/admin/ProjectOrganization.vue'),
        meta: { title: '项目组织' }
      },
      // 用户中心
      {
        path: 'user-center',
        name: 'UserCenter',
        component: () => import('@/views/UserCenter.vue'),
        meta: { title: '用户中心' }
      }
    ]
  },
  // 旧 /finance/* 重定向
  {
    path: '/finance/:pathMatch(.*)*',
    redirect: '/admin/finance'
  },
  {
    path: '/slides/:id',
    name: 'CaseSlidePreview',
    component: () => import('@/views/cases/CaseSlidePreview.vue'),
    meta: { title: '案例幻灯片', public: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - D&B 帝标|设记家 DEMO V.0.1` : 'D&B 帝标|设记家 - 全案服务系统 V3.0'
  
  // 检查是否需要登录（包括父路由和子路由）
  const token = localStorage.getItem('token')
  const customerToken = localStorage.getItem('customer_token')
  
  // 递归检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  // 客户专属页面：未注册引导注册，已注册可直达
  if (to.meta.isCustomerAuth && !customerToken) {
    next({ path: '/user-center', query: { redirect: to.fullPath }, replace: true })
    return
  }

  if (requiresAuth && !to.meta.isCustomerAuth && !token) {
    // 需要员工登录但未登录，跳转到统一用户中心
    next({ path: '/user-center', query: { redirect: to.fullPath }, replace: true })
    return
  }

  if (to.path === '/login' && token) {
    // 已登录但访问登录页，跳转到个人工作台并打开“我的”
    next({ path: '/admin/my-workspace', query: { openMine: '1' }, replace: true })
    return
  }
  
  next()
})

export default router
