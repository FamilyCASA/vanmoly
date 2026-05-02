# DESIGNARY-SYS-V3.0 系统审计报告

## 审计时间
2026-04-27 20:47 GMT+8

## 发现问题汇总

### 🔴 严重问题

#### 1. 员工登录失败
**症状**: LoginV2.vue 调用 `/auth/login` 返回 401
**根因**: 
- 前端 `LoginV2.vue` 使用 `request.post('/auth/login', {...})`
- 后端 `auth_routes.py` 只支持 MOCK_USERS（admin/admin123）
- `auth_routes_v2.py` 有完整登录逻辑但端点是 `/login`（不是 `/auth/login`）
- 蓝图注册可能有问题

**修复方案**:
- 统一使用 `auth_routes_v2.py` 的登录逻辑
- 确保蓝图正确注册 `/api/v3/auth/login`
- 创建默认员工账号用于测试

#### 2. 访客注册失败
**症状**: CustomerRegister.vue 调用 `/customer/register` 可能失败
**根因**:
- 前端使用 `request.post('/customer/register', ...)`
- 后端 `customer_routes_v2.py` 有 `/customer/register` 端点
- 但数据库 `Customer` 表的 `password_hash` 字段可能不存在

**修复方案**:
- 检查 Customer 模型是否有 password_hash 字段
- 检查 API 响应格式是否匹配前端期望

### 🟡 UI 风格问题

#### 3. 前台页面风格不统一
**现状**: 
- Home.vue: 自定义 CSS，风格尚可
- ProductList.vue: 现代简洁风格
- Login.vue: Element Plus 默认风格（紫色渐变）
- LoginV2.vue: 左右分栏，品牌色

**目标**: 统一为 apple.com.cn/mac 风格
**特征**:
- 大量留白
- 大字体、细字重
- 高质量产品图
- 微妙的动画
- 简洁的导航
- 深色/浅色交替区块

### 🟢 其他待检查项

#### 4. 页面完整性检查
- [ ] 所有路由是否可访问
- [ ] 404 页面处理
- [ ] 加载状态
- [ ] 错误处理

#### 5. API 连通性检查
- [ ] 前端 baseURL 配置
- [ ] CORS 设置
- [ ] 认证中间件

## 修复优先级

1. **P0**: 修复登录/注册（系统不可用）
2. **P1**: 统一 UI 风格（用户体验）
3. **P2**: 页面完整性优化

## 实施计划

### Phase 1: 修复认证系统
1. 检查蓝图注册
2. 统一登录 API 端点
3. 创建测试账号
4. 验证注册流程

### Phase 2: UI 风格统一
1. 参考 apple.com/mac 设计
2. 更新全局样式变量
3. 重写关键页面

### Phase 3: 全面测试
1. 所有页面路由测试
2. API 连通性测试
3. 移动端适配测试
