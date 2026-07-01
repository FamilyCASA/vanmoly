# DESIGNARY 全案落地服务系统 V4.0

> **品牌**：DESIGNARY（帝标·设记家 / D&B）
> **仓库**：`git@github.com:FamilyCASA/vanmoly.git`
> **系统版本**：V4.0
> **最后更新**：2026-07-01

---

## 一、项目概述

### 1.1 品牌背景
- **品牌名**：DESIGNARY
- **曾用名**：帝标·设记家 → 梵木里/VANMOLY → DESIGNARY
- **主营业务**：全案落地装修服务、全屋定制、软装搭配、家具家居
- **服务模式**：多分店运营，多租户隔离架构

### 1.2 系统定位
WEB后台管理 + 客户前台（C端）+ 微信小程序三端融合的全案服务系统。覆盖从线索获客、客户跟进、方案选品、报价合同、施工服务到财务管理的全链路业务流程。

---

## 二、系统架构

### 2.1 技术栈

| 层 | 技术 | 端口 | 说明 |
|---|---|---|---|
| **前端** | Vue 3.4 + Element Plus 2.6 + Vite 5 + Pinia | 5173 | Composition API，history 模式路由 |
| **后端** | Flask 2.x + SQLAlchemy 2.x + Waitress | 8080 | 工厂模式 `create_app()`，JWT 认证 |
| **数据库** | SQLite（主库 `vanmoly_v3.db` + 分店独立库） | — | 单文件数据库，分店隔离 |
| **小程序** | 原生微信小程序 | — | 非uni-app/Taro |

### 2.2 架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                         用户端                                     │
├──────────────┬──────────────────┬────────────────────────────────┤
│ Web后台管理   │  客户前台(C端)     │  微信小程序                     │
│ (Vue3+EP)    │  (Vue3 Mac风格)   │  (原生小程序)                   │
│ :5173        │  :5173            │                                │
└──────┬───────┴────────┬─────────┴────────────┬───────────────────┘
       │                 │                      │
       └────────┬────────┴──────────────────────┘
                │  REST API (/api/v3/*)
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Flask 后端服务 (:8080)                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │ 认证模块  │ │ 报价模块 │ │ 案例模块 │ │ 客户模块 │ │ 财务模块 │    │
│  │ JWT v2   │ │ PDF/HTML│ │ 筛选向导 │ │ 全量关联 │ │ 10张表  │    │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │ 权限模块  │ │ 项目组织 │ │ 知识库   │ │ 服务流程 │ │ 供应链   │    │
│  │ 隐式继承 │ │ 团队/任务 │ │ 三级分类 │ │ 58节点  │ │ 登记管理 │    │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │ 物料SKU  │ │ 特殊工艺 │ │ 楼盘管理 │ │ 合同管理 │ │ Dashboard│   │
│  │ 动态加载 │ │ 工艺系数 │ │ 楼盘调查 │ │ 模板管理 │ │ 数据驾驶舱│   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                           │
│  │ 方案管理  │ │ 预约量尺 │ │ 上传服务 │                           │
│  │ 客户选品  │ │ 前台留资 │ │ 图片/PDF │                           │
│  └─────────┘ └─────────┘ └─────────┘                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      数据层 (SQLite)                              │
│  主库 vanmoly_v3.db：用户/客户/报价/合同/案例/物料/财务/权限...     │
│  分店库 store_xxx.db：各分店独立业务数据                           │
│  物料库 material.db：SKU全字段动态加载                            │
│  报价库 quotes.db：报价单/空间/物料项/计量规则                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、功能模块清单

### 3.1 后台管理端（/admin）

| 模块 | 前端组件 | 后端路由 | 功能说明 |
|---|---|---|---|
| **数据驾驶舱** | `Dashboard.vue` | `dashboard_routes.py` | KPI卡片、7个统计端点、16个快捷入口、ECharts趋势图、待办提醒 |
| **我的工作台** | `MyWorkspace.vue` | `dashboard_routes.py` | 个人概览(`my-overview`接口)、我的客户(展开行全量信息)、我的项目小组、待办 |
| **线索管理** | `LeadManageV2.vue` | `lead_routes_v2.py` | 线索CRUD、公海规则、积分体系、状态流转 |
| **客户管理** | `CustomerManage.vue` `CustomerDetail.vue` | `customer_routes.py` | 客户CRUD、跟进记录、批量关联(报价/合同/案例/方案/预约/财务/项目组) |
| **案例管理** | `CaseManage.vue` `CaseEdit.vue` | `case_routes.py` | 案例CRUD、筛选向导(`CaseFilterWizard`)、氛围分类、幻灯片配置、订阅通知 |
| **选品/方案管理** | `SchemeManage.vue` | `scheme_routes.py` | 客户自主选品方案、方案转报价 |
| **报价管理** | `QuoteManage.vue` `QuoteDetail.vue` | `quote_routes.py` | 报价CRUD、空间实例模型、计量规则引擎(9条预设规则)、PDF导出(客户版/参考版)、HTML预览、模板管理 |
| **合同管理** | `ContractManage.vue` | `contract_routes.py` | 合同CRUD、14条模板、WeasyPrint PDF导出 |
| **服务流程** | `ServiceWorkflow.vue` | `service_workflow_routes.py` | 58节点6阶段(lead→contract→preparation→construction→finishing→after)、节点记录 |
| **预约管理** | `AppointmentManage.vue` | `appointment_routes.py` | 预约量尺、状态流转(待确认→已确认→已完成/已取消) |
| **财务管理** | `FinanceLayout.vue` + 13个子页面 | `finance_routes.py` | 流水CRUD、应收应付(分期支持)、报销审批、投资管理、股东/企业章程、操作日志、财务分析、5级角色权限 |
| **权限矩阵** | `PermissionCenter.vue` | `permission_routes.py` | 隐式权限继承(基于职位名匹配47个岗位)、显式分配、多选批量授权、审计日志 |
| **项目组织** | `ProjectOrganization.vue` | `project_team_routes.py` | 项目组CRUD、成员管理、任务分配、会议记录、评审、权限策略 |
| **组织架构** | `OrgStructureManage.vue` `HRManageV2.vue` | `hr_routes_v2.py` | 部门/岗位CRUD、员工管理(Tab整合) |
| **物料SKU** | `MaterialManageV2.vue` | `material_sku_routes.py` | SKU全字段动态加载、分类树、前台展示开关、批量导入 |
| **特殊工艺** | `CraftProcessManage.vue` | `craft_routes.py` | 工艺CRUD、图片上传、工艺系数 |
| **供应链登记** | `SupplierManage.vue` | — | 供应商登记管理 |
| **楼盘管理** | `BuildingManage.vue` `BuildingSurveyEdit.vue` | `building_routes.py` `building_survey_routes.py` | 楼盘CRUD、Excel导入、楼盘调查 |
| **知识库** | `KnowledgeManage.vue` `CategoryManage.vue` | `knowledge_routes.py` | 4个知识库、187个节点、三级分类树、18篇门店管理操作指南 |
| **系统设置** | `SettingsLayout.vue` | `frontend_config_routes.py` | 前端配置、文件管理、用户管理(`UserManageV2.vue`)、幻灯片模板 |

### 3.2 客户前台（C端）

| 页面 | 路由 | 功能说明 |
|---|---|---|
| 首页 | `/` | 品牌展示、毛玻璃英雄区、案例轮播(10s) |
| 案例列表 | `/cases` | 筛选向导、网格分页、卡片纯图+标签 |
| 案例详情 | `/cases/:id` | 毛玻璃英雄区、VR链接、配色方案、空间配置 |
| 产品列表 | `/products` | 分类导航、关键词搜索、品牌/环保等级筛选 |
| 产品详情 | `/products/:id` | 产品详情展示 |
| 选品中心 | `/selection-center` | 客户自主选品 |
| 提案列表 | `/proposals` | 方案预览 |
| 知识库 | `/knowledge` | 三视图切换、三级分类导航 |
| 预约量尺 | `/book` | 前台留资预约 |
| 线索表单 | `/leads` | 客户留资 |
| 登录/注册 | `/customer/login` `/register` | 客户认证 |
| 用户中心 | `/user-center` | 客户个人中心 |

### 3.3 微信小程序

原生微信小程序，核心页面：首页/案例列表/案例详情/留资表单/预约量尺/产品选品/报价预览。

---

## 四、数据模型

### 4.1 核心业务模型

| 模型 | 表名 | 说明 |
|---|---|---|
| `UserV2` | `users_v2` | 用户认证（identifier + SHA256哈希） |
| `Employee` | `employees` | 员工（关联UserV2） |
| `Customer` | `customer` | 客户（含楼盘/户型/面积/预算/来源/跟进） |
| `Lead` | `leads` | 线索（公海/积分） |
| `Quote` / `QuoteItem` | `quote` / `quote_item` | 报价单/物料项（空间实例模型） |
| `QuoteSpaceTemplate` | `quote_space_templates` | 空间模板 |
| `MeasurementRule` | `measurement_rule` | 计量规则（9条预设） |
| `QuoteTemplate` | `quote_template` | 报价模板 |
| `CustomerScheme` / `SchemeItem` | `customer_schemes` / `scheme_items` | 客户选品方案 |
| `CaseStudy` | `case_study` | 案例（含幻灯片配置） |
| `Contract` | `contract` | 合同 |
| `Appointment` | `appointment` | 预约量尺 |
| `ServiceWorkflow` | `service_workflow` | 58节点服务流程 |
| `ProjectTeam` / `ProjectTeamMember` / `ProjectTask` | `project_team` / ... | 项目组织 |

### 4.2 财务模型（10张表）

| 模型 | 表名 | 说明 |
|---|---|---|
| `FinanceTransaction` | `finance_transaction` | 收支流水 |
| `FinanceReceivable` | `finance_receivable` | 应收款（支持分期） |
| `FinancePayable` | `finance_payable` | 应付款 |
| `FinancePaymentPlan` | `finance_payment_plan` | 付款计划 |
| `FinanceReimbursement` | `finance_reimbursement` | 报销单 |
| `FinanceCategory` | `finance_category` | 财务分类 |
| `FinanceShareholder` | `finance_shareholder` | 股东 |
| `FinanceCharter` | `finance_charter` | 企业章程 |
| `FinanceRole` / `FinanceMember` | `finance_role` / `finance_member` | 财务角色/成员 |
| `FinanceAuditLog` | `finance_audit_log` | 操作日志 |

### 4.3 权限模型

| 模型 | 表名 | 说明 |
|---|---|---|
| `PermissionAssignment` | `permission_assignments` | 权限分配（支持多选批量） |
| `PermissionAuditLog` | `permission_audit_logs` | 权限审计日志 |

权限体系：**隐式继承**（基于 `Position.name` 匹配47个职位自动获得权限） + **显式分配**（权限中心手动授权）。

### 4.4 知识库模型

| 模型 | 表名 | 说明 |
|---|---|---|
| `KnowledgeBase` | `knowledge_base` | 知识库（4个） |
| `KnowledgeCategory` | `knowledge_category` | 三级分类（5→19→46） |
| `KnowledgeNode` | `knowledge_node` | 知识节点（187个） |
| `KnowledgeArticle` | `knowledge_article` | 文章 |
| `KnowledgeShare` | `knowledge_share` | 分享记录 |

---

## 五、API 接口概览

所有 API 统一前缀 `/api/v3`，认证使用 `jwt_required_v2`（Bearer Token）。

| 模块 | 蓝图 | 核心端点 |
|---|---|---|
| 认证 | `auth_v2_bp` | `POST /auth/login`, `GET /auth/me` |
| Dashboard | `dashboard_bp` | `GET /dashboard/stats`, `GET /dashboard/my-overview` |
| 客户 | `customer_bp` | `GET /customers` (批量关联), `POST /customers`, `GET /customers/:id` |
| 线索 | `lead_v2_bp` | `GET /leads`, `POST /leads` |
| 报价 | `quote_bp` | `GET /quotes`, `POST /quotes`, `GET /quotes/:id/pdf`, `GET /quotes/:id/preview` |
| 案例 | `case_bp` | `GET /cases`, `POST /cases`, `GET /cases/:id/showcase-candidates` |
| 方案 | `scheme_bp` | `GET /schemes`, `POST /schemes` |
| 合同 | `contract_bp` | `GET /contracts`, `POST /contracts` |
| 物料 | `material_sku_bp` | `GET /materials`, `GET /materials/filter-options`, `POST /materials/batch-import` |
| 工艺 | `craft_bp` | `GET /crafts/all`, `POST /crafts` |
| 财务 | `finance_bp` | `GET /finance/transactions`, `POST /finance/transactions`, `GET /finance/receivables`, `POST /finance/reimbursements` |
| 权限 | `permission_bp` | `GET /permissions/assignments`, `POST /permissions/assignments` |
| 项目 | `project_team_bp` | `GET /project-teams`, `POST /project-teams` |
| 服务流程 | `service_workflow_bp` | `GET /workflows`, `POST /workflows` |
| 知识库 | `knowledge_bp` | `GET /knowledge/bases`, `GET /knowledge/categories` |
| 楼盘 | `building_bp` | `GET /buildings` |
| 预约 | `appointment_bp` | `GET /appointments`, `POST /appointments` |
| 员工/HR | `hr_v2_bp` | `GET /hr/employees`, `GET /hr/departments`, `GET /hr/positions` |
| 上传 | `upload_bp` | `POST /upload/image` |
| 前端配置 | `frontend_config_bp` | `GET /frontend/config` |

---

## 六、报价系统

### 6.1 金额公式

```
物料项金额 = 数量 × 计量值 × 工艺系数 × 单价 + 工艺数量 × 工艺单价
```

### 6.2 计量规则引擎（9条预设）

| 规则 | 说明 |
|---|---|
| 长度 | 按长度计算 |
| 面积 | 按面积计算 |
| 体积 | 按体积计算 |
| 数量 | 按数量计算 |
| 投影高度补足 | 不足高度补足 |
| 柜门保底面积 | 保底面积计算 |
| 门套垭口套 | 门窗套计算 |
| 四方轮廓 | 四方轮廓计算 |
| 赠送工艺归零 | VIP4+赠送工艺归零 |

### 6.3 PDF导出

- **结构**：封面(16:9) → 分类汇总(左右双栏) → 物料详单(按空间分组) → 报价原则页
- **版本**：客户版(11列) / 参考版(12列)
- **费用汇总**：设计费/安装费自动统计二级分类关键词汇总
- **HTML预览**：独立Jinja2模板，样式与PDF对齐

---

## 七、权限体系

### 7.1 隐式权限继承

基于 `Position.name` 匹配47个职位，自动获得对应权限组：

- 系统角色：超管/店长 → 全部权限
- 业务角色：设计师/报价员/审核员 → 对应业务模块权限
- 财务角色：5级体系（出纳/会计/财务主管/财务总监/CFO）
- 项目角色：项目组长/项目成员 → 项目相关权限

### 7.2 权限检查顺序

```
has_permission(employee, perm):
  1. 系统角色检查（超管/店长直接通过）
  2. 隐式来源检查（职位/部门负责人/项目组长/项目成员）
  3. 显式分配检查（PermissionAssignment 表）
```

### 7.3 权限装饰器

- `@require_permission('permission_name')` — 路由级权限控制
- `@jwt_required_v2` — JWT认证
- `can_grant_permission()` — 授权权限检查

---

## 八、快速启动

### 8.1 环境要求

- Python 3.10+
- Node.js 18+
- SQLite 3

### 8.2 后端启动

```bash
cd backend
pip install -r requirements.txt
python3 run.py
# 验证：http://localhost:8080/api/v3/auth/login
```

### 8.3 前端启动

```bash
cd frontend
npm install
npx vite --host 0.0.0.0
# 访问：http://localhost:5173
```

### 8.4 登录凭据

- 管理员：`admin` / `van654321`
- 测试员工：`emp_42` / `van654321`

---

## 九、开发规范

### 9.1 前端规范

1. **Axios拦截器**：`request.js` 已解包 `{code, data, message}`，业务代码直接用 `res.xxx`
2. **路由**：`createWebHistory` 模式，Vite 需配置 `historyApiFallback`
3. **上传**：`el-upload` 不经过Axios拦截器，需手动添加 `uploadHeaders` 携带Bearer Token
4. **Vite Proxy**：必须使用 `127.0.0.1` 而非 `localhost`（IPv6冲突）
5. **中文搜索**：需 `encodeURIComponent` 编码（waitress WSGI限制）

### 9.2 后端规范

1. **认证**：统一使用 `jwt_required_v2`，禁止旧版 `token_required`
2. **蓝图**：所有蓝图 `url_prefix='/api/v3'`
3. **current_user**：JWT返回字典而非对象，用 `.get('key')` 访问
4. **数据库**：SQLite不支持跨库外键，跨库操作使用原生SQL
5. **密码**：SHA256哈希存储

### 9.3 常见问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 登录后401 | 旧版token_required密钥不同 | 迁移到jwt_required_v2 |
| 422 Token失效 | SECRET_KEY不一致 | 重启后端，重新登录 |
| 中文搜索500 | waitress不处理非ASCII URL | 前端 `encodeURIComponent` |
| Vite代理500 | IPv6/IPv4冲突 | proxy target用 `127.0.0.1` |
| Vue响应式失效 | reactive嵌套对象 | 提取为独立 `ref` |
| parent_id 500 | 前端传null | 统一默认值为整数 `0` |
| 端口8080被占 | 旧进程未退出 | `lsof -ti:8080 \| xargs kill -9` |

---

## 十、版本历史

| 版本 | 时间 | 核心更新 |
|---|---|---|
| V3.0 | 2026-04 | 品牌重塑、认证统一、HR管理、分店管理 |
| V3.1 | 2026-05-02 | 合同管理、WeasyPrint PDF、楼盘Excel导入 |
| V3.2 | 2026-05-10 | 服务流程可视化、楼盘调查、案例管理升级 |
| V3.3 | 2026-05-22 | 幻灯片模板系统、特殊工艺数据库 |
| V3.4 | 2026-05-28 | 物料筛选动态化、产品中心优化、is_public修复 |
| V3.5 | 2026-06-07 | 报价系统V3.0重构：空间实例模型、计量规则引擎、物料动态加载 |
| V3.6 | 2026-06-14 | PDF重写：16:9横向、分类汇总双栏、HTML预览、认证系统V2 |
| V3.7 | 2026-06-16 | 财务管理模块（10张表/30+API）、个人工作台 |
| V3.8 | 2026-06-22 | 知识库系统（4库187节点/三级分类）、供应链登记、报价规则引擎v2 |
| V4.0 | 2026-06-28~07-01 | 隐式权限体系、数据驾驶舱、毛玻璃视觉效果、案例筛选向导、客户列表全量信息展示 |

---

## 十一、Git 仓库

- **远程仓库**：`git@github.com:FamilyCASA/vanmoly.git`
- **默认分支**：`master`
- **提交规范**：前缀 `feat:` / `fix:` / `chore:` / `docs:` / `perf:`

---

*最后更新：2026-07-01 22:14 GMT+8*
