# D&B 帝标|设记家系统版本记录

## v3.0.1 - 小程序基础版（2026-04-26 09:19）

### 版本说明
- **版本号**: v3.0.1
- **创建时间**: 2026-04-26 09:19 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 小程序模拟器+真机调试通过，手写签名功能正常

### 包含功能
| 模块 | 状态 | 说明 |
|:---|:---|:---|
| 后端服务 | ✅ | Flask + SQLAlchemy，端口 5000 |
| 前端管理后台 | ✅ | Vue3 + Element Plus，端口 3001 |
| 小程序 | ✅ | 原生微信小程序，基础功能完成 |
| - 首页 | ✅ | 菜单网格 + 后端状态检测 |
| - 手写签名 | ✅ | Canvas 签名 + 保存预览 |

### 关键文件清单
```
backend/
├── app.py                  # 主应用入口
├── run.py                  # 开发启动脚本
├── run_waitress.py         # 生产环境启动
├── config.py               # 数据库配置
├── app/models/             # 数据模型
├── app/routes/             # API 路由
└── instance/               # SQLite 数据库

frontend/
├── src/views/admin/        # 管理后台页面
└── src/components/         # 可复用组件

miniapp-native/             # 【当前稳定版本】
├── app.json                # 小程序配置
├── pages/
│   ├── index/              # 首页
│   └── signature/          # 签名页
└── project.config.json     # 项目配置
```

### 启动方式
1. **后端**: `python backend/run.py`
2. **前端**: `cd frontend && npm run dev`
3. **小程序**: 微信开发者工具打开 `miniapp-native` 目录

### 一键启动
双击运行: `D:\desktop\DESIGNARY-SYS-V3.0\启动小程序.bat`

### 已知限制
- 小程序使用旧版 Canvas API（兼容性好）
- TabBar 无图标（纯文字）
- 后端 HTTP 连接（开发环境）

### 回退方法
如需回退到此版本，直接恢复 `miniapp-native` 目录即可：
```bash
# 备份当前（如有修改）
ren miniapp-native miniapp-native-backup

# 恢复此版本（从备份）
ren miniapp-native-backup miniapp-native
```

---

## 历史版本

### v3.0.0 - 重构启动（2026-04-25）
- 技术栈: Flask + Vue3 + uni-app
- 状态: 已废弃（uni-app 编译复杂）

### v1.2.5 - 旧系统（2026-04-22）
- 技术栈: Flask + jQuery
- 位置: `D:\desktop\vanmoly-distilled`
- 状态: 维护中，功能完整

---

## v3.0.2 - SKU物料数据库建设（2026-04-26 11:05）

### 版本说明
- **版本号**: v3.0.2
- **创建时间**: 2026-04-26 11:05 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: SKU物料数据库建设完成，928条记录导入成功

### 数据来源
| 来源 | 记录数 | 价格类型 | 处理方式 |
|:---|:---|:---|:---|
| 后台报价数据 | 686 | 零售价 | 直接导入 |
| 鲁班材料-辅材 | 29 | 成本价 | 成本×1.5=零售价 |
| 鲁班材料-主材 | 17 | 成本价 | 成本×1.5=零售价 |
| 袁伟全案报价 | 196 | 成本价 | 成本×1.5=零售价 |
| **合计** | **928** | - | - |

### 数据库结构
- **数据库**: `backend/instance/material.db`
- **表**: `material_category` (12个分类), `material_sku` (928条SKU)
- **导入脚本**: `scripts/import_all_sku.py`

### 待处理
- 帝标供应链PDF文件（高晟eclectic、高晟大师系列）需转换为Excel后导入

---

## v3.0.3 - 一键启动脚本（2026-04-26 11:15）

### 版本说明
- **版本号**: v3.0.3
- **创建时间**: 2026-04-26 11:15 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 新增三个一键启动批处理脚本

### 新增脚本

| 脚本 | 功能 | 说明 |
|:---|:---|:---|
| `一键启动开发环境.bat` | 启动后端+前端+浏览器 | 管理后台开发调试 |
| `一键打开小程序开发.bat` | 启动后端+打开小程序工具 | 小程序开发调试 |
| `一键回退到旧版本.bat` | ⚠️ 危险操作，带二次确认 | 回退到v1.2.x |

### 脚本详情

#### 1. 一键启动开发环境
- 启动后端服务 (端口5000)
- 启动前端服务 (端口3001)
- 自动打开浏览器访问 http://localhost:3001

#### 2. 一键打开小程序开发
- 启动后端服务 (端口5000)
- 尝试使用CLI打开微信开发者工具
- 如CLI不可用，打开项目目录供手动导入

#### 3. 一键回退到旧版本 ⚠️
- **必须输入"回退"二字确认**
- 自动停止V3.0服务
- 自动备份V3.0数据库到 backups/auto-backup-时间戳/
- 启动旧版本服务 (端口8000)

---

## v3.0.4 - PDF家具数据导入完成（2026-04-26 11:25）

### 版本说明
- **版本号**: v3.0.4
- **创建时间**: 2026-04-26 11:25 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 帝标供应链PDF家具数据提取并导入完成

### 数据来源完成
| 来源 | 记录数 | 价格策略 | 状态 |
|:---|:---|:---|:---|
| 后台报价数据 | 686 | 零售价 | ✅ 已导入 |
| 鲁班材料-辅材 | 29 | 成本价×1.5 | ✅ 已导入 |
| 鲁班材料-主材 | 17 | 成本价×1.5 | ✅ 已导入 |
| 袁伟全案报价 | 196 | 成本价×1.5 | ✅ 已导入 |
| **高晟eclectic** | **234** | **成本价×3** | ✅ **已导入** |
| **高晟大师系列** | **204** | **成本价×3** | ✅ **已导入** |
| **数据库总计** | **1366** | - | ✅ **完成** |

### 新增脚本
| 脚本 | 功能 |
|:---|:---|
| `scripts/extract_pdf_furniture.py` | PDF家具数据提取 |
| `scripts/import_furniture_to_db.py` | 家具数据导入数据库 |

### 数据库统计
```
总SKU数: 1366

分类TOP5:
  - 固装家具: 678条
  - 成品家具: 438条 (新增)
  - 主材: 82条
  - 综合项目: 32条
  - 基装: 28条

品牌TOP3:
  - 高晟eclectic: 234条
  - 高晟大师系列: 204条
  - 墓干山: 6条
```

---

---

## v3.0.5 - 客户自主选品方案（2026-04-26 14:00）

### 版本说明
- **版本号**: v3.0.5
- **创建时间**: 2026-04-26 14:00 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 客户可自主选品、搭配方案并提交

### 新增功能

#### 1. 产品展示中心（C端）
| 页面 | 功能 | 说明 |
|:---|:---|:---|
| 产品列表 | 浏览上架产品 | 分类筛选、价格展示 |
| 产品详情 | 查看产品信息 | 图片、规格、零售价 |
| 选品清单 | 管理已选产品 | 数量调整、删除、提交方案 |

#### 2. 客户方案系统
| 功能 | 说明 |
|:---|:---|
| 方案编辑 | 填写方案名称、风格、面积、阶段、备注 |
| 产品搭配 | 按分类组织已选产品，支持数量调整 |
| 方案提交 | 提交后生成方案编号，24小时内顾问联系 |
| 草稿保存 | 本地存储，可随时继续编辑 |

#### 3. 后端API
| 端点 | 功能 |
|:---|:---|
| `POST /api/v3/schemes` | 提交客户方案 |
| `GET /api/v3/schemes` | 获取方案列表（后台） |
| `GET /api/v3/schemes/<id>` | 获取方案详情 |
| `PUT /api/v3/schemes/<id>/status` | 更新方案状态 |

### 数据库表
```
customer_schemes    # 客户方案主表
scheme_items        # 方案明细表
```

### 用户体验流程
```
浏览产品 → 加入选品清单 → 编辑方案信息 → 提交方案
                ↓
         保存草稿（可选）
                ↓
         获得方案编号
                ↓
         等待顾问联系（24小时内）
```

---

## v3.0.6 - 客户选品与后台报价逻辑对齐（2026-04-26 14:00）

### 版本说明
- **版本号**: v3.0.6
- **创建时间**: 2026-04-26 14:00 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 客户选品逻辑与后台新建报价逻辑保持一致

### 数据模型对齐

| 字段 | 客户方案 (CustomerScheme) | 后台报价 (Quote) | 说明 |
|:---|:---|:---|:---|
| 编号 | scheme_no (SC前缀) | quote_no (BJ前缀) | 统一格式 |
| 分类汇总 | category_summary (JSON) | category_summary (JSON) | 完全一致 |
| 小计 | subtotal | subtotal | 计算方式一致 |
| 管理费 | management_fee + rate | management_fee + rate | 计算方式一致 |
| 税费 | tax + rate | tax + rate | 计算方式一致 |
| 总价 | total_amount | total_amount | 计算方式一致 |
| 状态 | draft/submitted/processing/quoted/confirmed/cancelled | draft/sent/confirmed/signed/expired | 略有差异 |

### 明细表对齐 (SchemeItem vs QuoteItem)

| 字段 | SchemeItem | QuoteItem | 说明 |
|:---|:---|:---|:---|
| 空间 | room_name | room_name | 完全一致 |
| 三级分类 | category_level1/2/3 | category_level1/2/3 | 完全一致 |
| SKU信息 | sku_id, name, sku_code, spec, brand, unit | sku_id, name, sku_code, spec, brand, unit | 完全一致 |
| 价格 | quantity, unit_price, total_price | quantity, unit_price, total_price | 完全一致 |
| 图片 | main_image | image | 字段名不同 |
| 排序 | sort_order | sort_order | 完全一致 |

### API对齐

| 功能 | 客户方案端点 | 后台报价端点 |
|:---|:---|:---|
| 创建 | POST /api/v3/schemes | POST /api/v3/quotes |
| 列表 | GET /api/v3/schemes | GET /api/v3/quotes |
| 详情 | GET /api/v3/schemes/<id> | GET /api/v3/quotes/<id> |
| 更新状态 | PUT /api/v3/schemes/<id>/status | PUT /api/v3/quotes/<id> |
| 转换报价 | POST /api/v3/schemes/<id>/convert-to-quote | - |

### 前端功能更新

#### 1. 产品列表页 (ProductList.vue)
- 新增"加入选品"按钮
- 选择空间对话框（12个预设空间 + 自定义）
- 支持同一产品在不同空间分别添加
- 数量选择

#### 2. 选品清单页 (SelectionList.vue)
- 按空间分组展示
- 分类汇总面板（与后台报价一致）
- 费用明细（小计/管理费/税费/总价）
- 提交数据结构完全对齐后台报价

### 分类映射规则
```python
{
    '硬装主材': 'hard_material',
    '施工服务': 'construction',
    '安装服务': 'installation',
    '配送服务': 'delivery',
    '搬运服务': 'moving',
    '设计服务': 'design',
    '全屋定制': 'custom',
    '成品家具': 'furniture',
    '软装饰品': 'soft',
    '电气设备': 'equipment',
    '基装': 'construction',
    '主材': 'hard_material',
    '固装家具': 'custom',
    '活动家具': 'furniture'
}
```

### 一键转换功能
后台可将客户方案一键转换为正式报价单：
- 复制所有明细项
- 保留分类汇总
- 保留费用计算
- 自动关联方案与报价

---

---

## v3.0.7 - 后端路由修复（2026-04-26 16:15）

### 版本说明
- **版本号**: v3.0.7
- **创建时间**: 2026-04-26 16:15 (GMT+8)
- **状态**: ✅ 稳定运行
- **标记原因**: 修复scheme蓝图路由注册问题和数据库表结构问题

### 修复内容

#### 1. scheme蓝图路由注册修复
| 问题 | 原因 | 修复方案 |
|:---|:---|:---|
| 路由未正确注册 | scheme_bp使用空字符串路由`@scheme_bp.route('')`，与其他蓝图不一致 | 修改`__init__.py`，将url_prefix从`/api/v3`改为`/api/v3/schemes` |

**修复文件**: `backend/app/__init__.py`
```python
# 修复前
app.register_blueprint(scheme_bp, url_prefix='/api/v3')

# 修复后
app.register_blueprint(scheme_bp, url_prefix='/api/v3/schemes')
```

#### 2. 数据库模型修复
| 问题 | 原因 | 修复方案 |
|:---|:---|:---|
| SQLAlchemy上下文错误 | scheme模型使用独立db实例 | 改为使用主应用db实例 |
| employee表缺少id_card列 | 模型与数据库结构不一致 | 删除旧数据库，重新创建所有表 |

**修复文件**: `backend/app/models/scheme.py`
```python
# 修复前
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# 修复后
from app import db
```

#### 3. QUOTE_CATEGORIES类型修复
| 问题 | 原因 | 修复方案 |
|:---|:---|:---|
| AttributeError: 'list' object has no attribute 'items' | scheme_routes.py期望QUOTE_CATEGORIES是字典，但实际是列表 | 修改循环方式，使用元组解包 |

**修复文件**: `backend/app/routes/scheme_routes.py`
```python
# 修复前
for key, config in QUOTE_CATEGORIES.items():
    summary[key] = {'name': config['name'], 'amount': 0}

# 修复后
for key, name in QUOTE_CATEGORIES:
    summary[key] = {'name': name, 'amount': 0}
```

### 验证结果
```bash
# 路由注册验证
flask routes | findstr scheme
/api/v3/schemes POST,OPTIONS
/api/v3/schemes GET,OPTIONS
/api/v3/schemes/<int:id> GET,OPTIONS
/api/v3/schemes/<int:id> DELETE,OPTIONS
/api/v3/schemes/<int:id>/convert-to-quote POST,OPTIONS
/api/v3/schemes/<int:id>/status PUT,OPTIONS

# API测试验证
POST /api/v3/schemes
Response: 200 OK
{
  "code": 200,
  "data": {
    "id": 1,
    "scheme_no": "SC202604260001",
    "total_amount": 1000,
    "total_quantity": 1
  },
  "message": "方案提交成功"
}
```

### 服务状态
- **后端服务**: http://127.0.0.1:5000 (运行中)
- **前端服务**: http://localhost:3000 (运行中)
- **数据库**: SQLite (已重建，表结构最新)

---

*最后更新: 2026-04-26 16:15*
---

## v3.0.8 - 系统设置独立页面 + 我的面板（2026-05-06 08:08）

### 版本说明
- **版本号**: v3.0.8
- **创建时间**: 2026-05-06 08:08 (GMT+8)
- **状态**: ✅ 开发完成
- **标记原因**: 管理后台系统设置从 Drawer 改为独立页面，右上角新增"我的"面板

### 改造内容

#### 1. 系统设置独立页面
将原来 AdminLayout 内的 Drawer 弹窗改为独立路由 `/admin/settings`，左右分栏布局：

| 组件 | 文件 | 说明 |
|:---|:---|:---|
| 设置布局 | `SettingsLayout.vue` | 左侧 280px 功能卡片导航，右侧动态编辑区 |
| 流程模板管理 | `WorkflowTemplateManage.vue` | 已独立抽取，供 SettingsLayout 调用 |
| 物料分类管理 | `CategoryManage.vue` | 从 AdminLayout Drawer 提取，独立组件 |

**系统设置 7 个模块**（均集成到 `/admin/settings`）：
1. 流程模板管理（Connection 图标 / 蓝）
2. 物料分类管理（Folder 图标 / 绿）
3. 员工管理（User 图标 / 橙）
4. 分店管理（Shop 图标 / 紫）
5. 物料管理（Box 图标 / 青）
6. 文件管理（FolderOpened 图标 / 红）
7. 前端配置（Monitor 图标 / 靛）

#### 2. AdminLayout 侧边栏精简
- 移除 5 个独立菜单项（员工管理 / 分店管理 / 物料管理 / 文件管理 / 前端配置）
- 统一从 `/admin/settings` 进入
- router/index.js 移除对应 6 个独立路由

#### 3. 右上角"我的"面板
- 删除原有用户下拉菜单（个人中心 / 退出登录）
- 只保留"我的"按钮，点击打开右侧 Drawer
- Drawer 内容：
  - 用户卡片（头像 + 姓名 + 岗位）
  - 我的积分（余额卡片 + 详情弹窗 + 排行榜弹窗）
  - 我的业务网格（8个快捷入口：团队/楼盘/合同/报价/审核/线索/客户/服务流程）
  - 安全设置：修改登录密码弹窗
  - 退出登录按钮（移至抽屉底部）

#### 4. API 路径重复 bug 修复
- 问题：`request.js` baseURL 为 `/api/v3`，但 AdminLayout.vue 调用写了完整 `/api/employee/...`，拼出来变成 `/api/v3/api/employee/...`
- 修复：去掉 AdminLayout.vue 中 6 处多余的 `/api/` 前缀

### 文件变更清单

| 操作 | 文件 |
|:---|:---|
| 新建 | `frontend/src/views/admin/SettingsLayout.vue` |
| 新建 | `frontend/src/views/admin/CategoryManage.vue` |
| 修改 | `frontend/src/views/admin/AdminLayout.vue` |
| 修改 | `frontend/src/router/index.js` |

### 后端待实现接口（目前返回 404）

| 端点 | 功能 |
|:---|:---|
| GET `/api/v3/employee/me/points` | 积分余额 |
| GET `/api/v3/employee/me/points/detail` | 积分明细 |
| GET `/api/v3/employee/points/rank` | 积分排行 |
| GET `/api/v3/employee/me/team` | 我的团队 |
| POST `/api/v3/auth/change-password` | 修改密码 |

### 备份
- 自动备份目录：`D:\desktop\VANMOLY-SYS-V3.0\backups\`

---

*最后更新: 2026-05-06 08:36*