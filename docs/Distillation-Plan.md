# D&B 帝标|设记家 DEMO V.0.1 功能蒸馏计划

**来源系统**: D:\desktop\vanmoly-distilled (V1.2.3)  
**目标系统**: D:\desktop\DESIGNARY-SYS-V3.0 (V3.0)  
**日期**: 2026-04-26

---

## 一、蒸馏模块清单

| 模块 | 旧系统路径 | 优先级 | 状态 |
|------|-----------|--------|------|
| **客户管理** | core/customer/ | P0 | 待蒸馏 |
| **物料管理** | business/quote/sku_api.py | P0 | 待蒸馏 |
| **员工管理** | business/employee/ | P0 | 待蒸馏 |
| **合同管理** | core/common/contract_*.py | P1 | 待蒸馏 |
| **楼盘管理** | business/building/ | P1 | 待蒸馏 |

---

## 二、客户管理模块蒸馏

### 2.1 数据模型映射

| 旧系统 (Customer) | 新系统 (Customer) | 处理方式 |
|------------------|------------------|---------|
| id | id | 保留 |
| name | name | 保留 |
| phone | phone | 保留 |
| gender | gender | 保留 |
| age_range | - | 移除 |
| avatar | - | 移除 |
| email | email | 保留 |
| wechat | wechat | 保留 |
| address | address | 保留 |
| province/city/district | province/city/district | 保留 |
| building_name | building_name | 保留 |
| source | source | 保留 |
| budget | budget | 保留 |
| house_type | house_type | 保留 |
| house_area | house_area | 保留 |
| requirements | requirements | 保留 |
| style_preference | style_preference | 保留 |
| customer_type | customer_type | 保留 |
| status | status | 保留 |
| priority | priority | 保留 |
| owner_id | owner_id | 保留 |
| owner_name | - | 移除（通过join获取） |
| follow_count | follow_count | 保留 |
| last_follow | last_follow | 保留 |
| next_follow | next_follow | 保留 |
| remark | remark | 保留 |
| is_deleted | is_deleted | 保留 |
| tenant_id | tenant_id | 保留 |
| created_at/updated_at | created_at/updated_at | 保留 |

### 2.2 API 端点规划

```
GET    /api/v3/customers              # 客户列表（筛选/分页/搜索）
GET    /api/v3/customers/{id}         # 客户详情
POST   /api/v3/customers              # 创建客户
PUT    /api/v3/customers/{id}         # 更新客户
DELETE /api/v3/customers/{id}         # 删除客户（软删除）
POST   /api/v3/customers/{id}/follow  # 添加跟进记录
GET    /api/v3/customers/stats        # 客户统计
GET    /api/v3/customers/sources      # 来源列表
```

---

## 三、物料管理模块蒸馏

### 3.1 数据模型映射

旧系统的 SKU 数据存储在 `instance/sku.db` 的 `metadata` 表中。

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| id | id | 保留 |
| category | category | 保留 |
| prod_property | property | 产品属性 |
| prod_series | series | 产品系列 |
| material | material | 材质 |
| pattern | pattern | 花色 |
| brand | brand | 品牌 |
| model | model | 型号 |
| specification | specification | 规格 |
| cost | cost_price | 成本价 |
| retail_price | sale_price | 销售价 |
| unit | unit | 单位 |
| calc_type | calc_type | 计算类型 |
| name | name | 名称 |
| remark | remark | 备注 |
| design | design_fee | 设计费 |
| install | install_fee | 安装费 |
| delivery | delivery_fee | 配送费 |
| reference_image | image_url | 参考图 |
| tags | tags | 标签(JSON) |
| customization_rules | customization_rules | 定制规则(JSON) |

### 3.2 API 端点规划

```
GET    /api/v3/materials              # 物料列表（筛选/分页/搜索）
GET    /api/v3/materials/{id}         # 物料详情
POST   /api/v3/materials              # 创建物料
PUT    /api/v3/materials/{id}         # 更新物料
DELETE /api/v3/materials/{id}         # 删除物料
GET    /api/v3/materials/categories   # 分类列表
POST   /api/v3/materials/import       # 批量导入
```

---

## 四、员工管理模块蒸馏

### 4.1 数据模型增强

V3.0 已有基础 Employee 模型，需要增强：

| 新增字段 | 来源 | 说明 |
|---------|------|------|
| gender | 旧系统 | 性别 |
| avatar | 旧系统 | 头像 |
| hire_date | 旧系统 | 入职日期 |
| employee_no | 旧系统 | 工号 |
| user_id | 旧系统 | 关联用户ID |
| remark | 旧系统 | 备注 |

### 4.2 API 端点规划

```
GET    /api/v3/employees              # 员工列表
GET    /api/v3/employees/{id}         # 员工详情
POST   /api/v3/employees              # 创建员工
PUT    /api/v3/employees/{id}         # 更新员工
DELETE /api/v3/employees/{id}         # 删除员工
GET    /api/v3/employees/positions    # 岗位列表
GET    /api/v3/employees/departments  # 部门列表
GET    /api/v3/employees/{id}/profile # 员工档案（聚合数据）
```

---

## 五、合同管理模块蒸馏

### 5.1 数据模型映射

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| id | id | 保留 |
| contract_no | contract_no | 合同编号 |
| contract_type | contract_type | 合同类型 |
| contract_name | contract_name | 合同名称 |
| status | status | 状态 |
| party_a_name | customer_name | 客户名称 |
| party_a_contact | customer_contact | 客户联系人 |
| party_a_phone | customer_phone | 客户电话 |
| total_amount | total_amount | 合同金额 |
| service_items | service_items | 服务项目(JSON) |
| signed_date | signed_date | 签署日期 |
| created_at/updated_at | created_at/updated_at | 时间戳 |

### 5.2 API 端点规划

```
GET    /api/v3/contracts              # 合同列表
GET    /api/v3/contracts/{id}         # 合同详情
POST   /api/v3/contracts              # 创建合同
PUT    /api/v3/contracts/{id}         # 更新合同
DELETE /api/v3/contracts/{id}         # 删除合同
GET    /api/v3/contracts/templates    # 合同模板
POST   /api/v3/contracts/{id}/sign    # 签署合同
```

---

## 六、实施步骤

### Phase 1: 核心模块 (P0)

1. **客户管理模块**
   - [ ] 创建 customer.py 模型
   - [ ] 创建 customer_routes.py API
   - [ ] 创建 CustomerManage.vue 管理页面
   - [ ] 数据迁移脚本

2. **物料管理模块**
   - [ ] 增强 material.py 模型
   - [ ] 创建 material_routes.py API
   - [ ] 创建 MaterialManage.vue 管理页面
   - [ ] 数据导入脚本

3. **员工管理模块**
   - [ ] 增强 employee.py 模型
   - [ ] 增强 employee_routes.py API
   - [ ] 创建 EmployeeManage.vue 管理页面

### Phase 2: 扩展模块 (P1)

4. **合同管理模块**
   - [ ] 创建 contract.py 模型
   - [ ] 创建 contract_routes.py API
   - [ ] 创建 ContractManage.vue 管理页面

5. **楼盘管理模块**
   - [ ] 创建 building.py 模型
   - [ ] 创建 building_routes.py API
   - [ ] 创建 BuildingManage.vue 管理页面

---

## 七、数据迁移策略

### 7.1 客户数据迁移

```python
# 从旧系统 customer.db 读取
# 写入新系统 instance/v3.db
# 映射字段并处理差异
```

### 7.2 物料数据迁移

```python
# 从旧系统 sku.db metadata 表读取
# 写入新系统 instance/v3.db
# 转换 calc_type 等字段
```

### 7.3 员工数据迁移

```python
# 从旧系统 auth.db employees 表读取
# 写入新系统 instance/v3.db
# 保留原有数据，增强字段设默认值
```

---

## 八、前端页面规划

### 8.1 管理后台菜单结构

```
管理后台
├── 数据看板 (Dashboard)
├── 内容管理
│   ├── 案例管理 (CaseManage)
│   ├── 文章管理 (ArticleManage)
│   └── 物料管理 (MaterialManage) ⭐新增
├── 客户管理
│   ├── 客户列表 (CustomerManage) ⭐新增
│   ├── 线索管理 (LeadManage)
│   └── 预约管理 (AppointmentManage)
├── 业务管理
│   ├── 合同管理 (ContractManage) ⭐新增
│   ├── 楼盘管理 (BuildingManage) ⭐新增
│   └── 优惠券管理 (CouponManage)
├── 系统设置
│   ├── 员工管理 (EmployeeManage) ⭐新增
│   ├── 文件管理 (FileManage)
│   └── 前端配置 (FrontendConfig)
```

---

**开始时间**: 2026-04-26  
**预计完成**: 2026-04-27
