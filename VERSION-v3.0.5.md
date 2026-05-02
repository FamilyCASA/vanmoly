# D&B 帝标|设记家全安落地服务系统 DEMO V.0.1.5

**版本号**: 3.0.5  
**发布日期**: 2026-04-26  
**更新内容**: 统一前端导航栏和页脚，修复 Element Plus 警告

## 版本特性

### 前端改进
- ✅ 统一导航栏组件 (Navbar.vue)
- ✅ 统一页脚组件 (Footer.vue)
- ✅ 案例页面重构 (梵几风格)
- ✅ 产品中心重构 (MADE.com 风格)
- ✅ 预约页面重构 (TMF 风格)
- ✅ 修复 el-radio label → value 警告

### 后端改进
- ✅ 添加 echarts 依赖
- ✅ waitress 生产服务器稳定运行

## 文件清单

### 新增组件
- `frontend/src/components/Navbar.vue`
- `frontend/src/components/Footer.vue`

### 更新页面
- `frontend/src/views/cases/CaseList.vue`
- `frontend/src/views/products/ProductList.vue`
- `frontend/src/views/Appointment.vue`

### 修复文件
- `frontend/src/views/admin/Dashboard.vue`
- `frontend/src/components/LeadForm.vue`
- `frontend/src/views/admin/AppointmentManage.vue`
- `frontend/src/views/admin/CaseManage.vue`
- `frontend/src/views/admin/LeadManage.vue`
- `frontend/src/views/admin/ServiceWorkflow.vue`
- `frontend/src/views/admin/SupplierManage.vue`

## 启动方式

运行 `start-all-v3.0.5.bat` 一键启动：
1. 自动备份当前版本到 `vanmoly-backup-v3.0.5`
2. 启动后端服务 (端口 5000)
3. 启动前端开发服务器 (端口 3000)
4. 自动打开浏览器

## 访问地址

- 前台首页: http://localhost:3000
- 后台管理: http://localhost:3000/admin
- 后端API: http://localhost:5000

## 回退方式

运行 `revert-v3.0.5.bat` 可回退到此版本。
