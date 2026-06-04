# 帝标·设记家全案落地服务系统 V3.4.0 文档

> 品牌：帝标·设记家（D&B）
> 项目路径：`D:\desktop\VANMOLY-SYS-V3.0`
> 系统版本：V3.4.0
> 最后更新：2026-05-28

---

## 一、项目概述

### 1.1 品牌背景
- 品牌：帝标·设记家（D&B）
- 原品牌：梵木里/VANMOLY（2026年4月29日完成品牌重塑）
- 主营业务：全案落地装修服务、全屋定制、软装搭配
- 服务覆盖：多分店（独立数据库架构，多租户隔离）

### 1.2 系统定位
WEB后台管理 + 微信小程序 + 客户选品中心（Apple Mac风格）多端融合的全案服务系统，支持多租户（分店）隔离架构。

---

## 二、系统架构

### 2.1 技术栈总览
| 端       | 技术栈                                                                 | 端口  | 路径                                      |
|----------|------------------------------------------------------------------------|-------|-------------------------------------------|
| 前端     | Vue 3.4 + Element Plus 2.6 + Vite 5 + Pinia                           | 5173  | `D:\desktop\VANMOLY-SYS-V3.0\frontend\`  |
| 后端     | Flask + SQLAlchemy 2.x + Waitress（生产服务器）                        | 8080  | `D:\desktop\VANMOLY-SYS-V3.0\backend\`   |
| 数据库   | SQLite（主库：vanmoly_v3.db；分店独立库：store_xxx.db）                 | -     | `backend/instance/vanmoly_v3.db`          |
| 微信小程序 | 原生微信小程序（非uni-app/Taro）                                        | -     | `D:\desktop\VANMOLY-SYS-V3.0\miniapp-native\` |

### 2.2 架构图（文字描述）
```
用户端
├─ Web前端（Vue3 + Element Plus）→ Vite代理到后端8080
├─ 微信小程序（原生）→ 调用后端REST API
└─ 客户选品中心（Mac风格Web）→ 独立前端模块

后端服务（Flask）
├─ 认证模块（JWT，统一使用jwt_required_v2）
├─ 业务模块（报价/案例/客户/物料/员工/服务流程/幻灯片/特殊工艺）
├─ 数据层（SQLAlchemy ORM + SQLite）
└─ 多租户（分店独立数据库，主库管理分店元数据）

存储层
├─ 主库：vanmoly_v3.db（用户/订单/案例/物料/幻灯片配置等核心数据）
└─ 分店库：store_cd001.db等（各分店独立业务数据）
```

---

## 三、前后端功能模块清单

### 3.1 前端功能模块（Vue3）
| 模块名称               | 路径/组件名                  | 功能说明                                                                 |
|------------------------|-------------------------------|--------------------------------------------------------------------------|
| 登录页                 | LoginV2.vue                   | 员工/访客登录，identifier字段（非username）                               |
| 仪表盘                 | Dashboard.vue                 | 核心数据概览、快捷入口（13项）                                           |
| 报价管理               | QuoteManage.vue               | 报价单列表、新增/编辑/预览/复制、物料搜索框、增强字段（尺寸/工艺系数）     |
| 报价详情               | QuoteDetail.vue               | 报价详情查看、PDF导出（访客/客户版）、复制报价单号                         |
| 报价从案例生成         | QuoteFromCase.vue             | 四步向导：选客户→选案例→配空间→确认报价                                 |
| 案例管理               | CaseManage.vue、CaseList_NIO_Style.vue | 案例列表（蔚来风格五层架构）、氛围分类（温馨/清新等6类） |
| 案例详情               | CaseDetailV2.vue              | 案例详情、订阅（手机号+微信通知）                                         |
| 案例编辑               | CaseEdit.vue                  | 案例编辑、幻灯片配置（8页开关+风格选择+材质展示多选）                       |
| 幻灯片预览             | CaseSlidePreview.vue           | 1920×1080画布+transform scale自适应、团队页/目录页/效果图页/物料汇总页     |
| 客户管理               | CustomerManage.vue            | 客户列表、详情、跟进记录                                                 |
| 物料管理               | MaterialManageV2.vue          | 物料SKU管理、前台展示开关（is_public）、分类树状展示、筛选栏动态加载         |
| 特殊工艺管理           | CraftProcessManage.vue        | 特殊工艺数据库（全屋定制/硬装施工）、主图/施工图/实景图上传、富文本简介     |
| 产品中心               | ProductList.vue               | 前台产品展示、分类导航、关键词搜索、品牌/单位/环保等级筛选、选品抽屉        |
| 员工管理               | EmployeeManage.vue、HRManageV2.vue | 员工/部门/职位管理、权限分配                                           |
| 服务流程               | ServiceWorkflow.vue           | 58节点服务流程（6阶段：lead→contract→preparation→construction→finishing→after） |
| 分店管理               | StoreManage.vue               | 分店元数据管理、独立数据库配置（仅超管可访问）                           |
| 知识库管理             | KnowledgeManage.vue           | 知识库CRUD（jwt_required_v2统一认证，修复保存登出问题）                    |
| 小程序管理             | 原生小程序页面                | 首页/案例/留资/预约量尺/产品选品等                                       |

### 3.2 后端功能模块（Flask）
| 模块名称               | 路由文件                      | 核心功能                                                                 |
|------------------------|-------------------------------|--------------------------------------------------------------------------|
| 认证模块               | auth_routes_v2.py             | JWT生成/验证、jwt_required_v2装饰器、密码哈希                            |
| 报价模块               | quote_routes.py               | 报价CRUD、克隆/预览/PDF导出、空间配置、实时计价、物料关键词搜索            |
| 案例模块               | case_routes.py                | 案例CRUD、氛围分类、发布/下架、订阅、幻灯片配置API、材质展示候选/保存API    |
| 客户模块               | customer_routes.py            | 客户管理、跟进记录                                                       |
| 物料模块               | material_sku_routes.py        | SKU管理、前台配置、分类树、filter-options API、batch-import、is_public过滤 |
| 特殊工艺模块           | craft_routes.py               | 特殊工艺CRUD、图片上传、8个REST API端点                                   |
| 员工模块               | employee_routes.py、hr_routes_v2.py | 员工/部门/职位管理、绩效统计                                           |
| 服务流程模块           | service_workflow_routes.py    | 58节点流程管理、状态流转                                                 |
| 分店模块               | store_routes.py               | 分店管理、独立数据库迁移                                                 |
| 上传模块               | upload_routes.py              | 图片/文件上传、PDF生成与下载                                             |
| 线索模块               | lead_routes_v2.py            | 线索管理、公海规则、积分体系                                             |

### 3.3 数据模型（SQLAlchemy）
| 模型名称               | 对应表名               | 核心字段                                                                 |
|------------------------|------------------------|--------------------------------------------------------------------------|
| UserV2                 | users_v2               | id, identifier, password_hash, role, tenant_id                           |
| Quote                  | quote                  | id, customer_id, customer_name, customer_phone, status, total_price       |
| QuoteItem              | quote_item             | id, quote_id, sku_id, name, process_id, process_coefficient, process_unit_price |
| CaseStudy              | case_study             | id, title, atmosphere, status, cover_image, brand_name, tenant_id        |
| CaseSlideConfig        | case_slide_configs     | id, case_id, page_config(JSON), style, showcase_material_ids(JSON)        |
| SlideTemplate           | slide_templates        | id, name, style, page_config_template(JSON)                              |
| MaterialSKU            | material_sku           | id, name, category_id, is_public, brand, unit, env_level, main_image     |
| CraftProcess           | craft_process          | id, name, category, coefficient, unit_price, description, main_image      |
| Employee               | employees              | id, user_id, department_id, position_id, join_date                       |
| ServiceWorkflow        | service_workflow       | id, quote_id, current_node, status, service_type                        |
| Store                  | stores                 | id, name, tenant_id, db_path, db_status                                 |

---

## 四、全量API接口列表

### 4.1 认证相关
| 方法 | 路径                     | 功能                     | 权限       |
|------|--------------------------|--------------------------|------------|
| POST | /api/v3/auth/login       | 登录获取JWT              | 公开       |
| POST | /api/v3/auth/register    | 注册（仅超管/店长可操作）| 超管/店长  |

### 4.2 报价相关
| 方法 | 路径                                 | 功能                     | 权限       |
|------|--------------------------------------|--------------------------|------------|
| GET  | /api/v3/quotes                       | 报价列表                 | 员工       |
| POST | /api/v3/quotes                       | 创建报价                 | 员工       |
| GET  | /api/v3/quotes/{id}                  | 报价详情                 | 员工/客户  |
| PUT  | /api/v3/quotes/{id}                  | 更新报价                 | 员工       |
| DELETE| /api/v3/quotes/{id}                  | 删除报价                 | 超管       |
| GET  | /api/v3/quotes/{id}/pdf              | 导出访客版PDF            | 公开       |
| GET  | /api/v3/quotes/{id}/pdf-customer     | 导出客户版PDF            | 客户       |
| POST | /api/v3/quotes/from-case             | 从案例克隆报价           | 员工       |
| GET  | /api/v3/space-configs/by-case/{id}  | 案例空间配置             | 员工       |

### 4.3 案例相关
| 方法 | 路径                                 | 功能                     | 权限       |
|------|--------------------------------------|--------------------------|------------|
| GET  | /api/v3/cases                        | 案例列表（支持status/atmosphere/is_public筛选） | 公开/员工 |
| POST | /api/v3/cases                        | 创建案例                 | 员工       |
| GET  | /api/v3/cases/featured               | 精选案例                 | 公开       |
| GET  | /api/v3/cases/{id}                   | 案例详情                 | 公开/员工  |
| PUT  | /api/v3/cases/{id}                   | 更新案例                 | 员工       |
| PUT  | /api/v3/cases/{id}/publish           | 发布案例                 | 员工       |
| POST | /api/v3/public/cases/{id}/subscribe  | 订阅案例（手机号）       | 公开       |
| GET  | /api/v3/cases/{id}/showcase-candidates | 材质展示候选物料       | 员工       |
| POST | /api/v3/cases/{id}/showcase-materials | 保存材质展示配置       | 员工       |

### 4.4 物料相关
| 方法 | 路径                                 | 功能                     | 权限       |
|------|--------------------------------------|--------------------------|------------|
| GET  | /api/v3/materials                    | 物料SKU列表（支持is_public/keyword/brand/unit/env_level筛选） | 员工/公开 |
| POST | /api/v3/materials/batch-import       | 批量导入物料SKU          | 员工       |
| GET  | /api/v3/materials/filter-options     | 动态筛选选项（品牌/单位/环保等级）| 公开  |
| GET  | /api/v3/materials/public-config      | 前台展示配置             | 公开       |
| PUT  | /api/v3/materials/public-config      | 更新前台配置             | 员工       |
| GET  | /api/v3/materials/categories         | 分类树                   | 公开       |

### 4.5 特殊工艺相关
| 方法 | 路径                                 | 功能                     | 权限       |
|------|--------------------------------------|--------------------------|------------|
| GET  | /api/v3/craft-processes              | 工艺列表                 | 员工/公开  |
| POST | /api/v3/craft-processes              | 创建工艺                 | 员工       |
| GET  | /api/v3/craft-processes/{id}         | 工艺详情                 | 员工/公开  |
| PUT  | /api/v3/craft-processes/{id}         | 更新工艺                 | 员工       |
| DELETE| /api/v3/craft-processes/{id}         | 删除工艺                 | 员工       |
| POST | /api/v3/craft-processes/{id}/upload  | 上传工艺图片             | 员工       |

### 4.6 其他核心API
| 方法 | 路径                                 | 功能                     | 权限       |
|------|--------------------------------------|--------------------------|------------|
| GET  | /api/v3/employees                    | 员工列表                 | 超管/店长  |
| GET  | /api/v3/stores                       | 分店列表                 | 超管       |
| GET  | /api/v3/service-workflows            | 服务流程列表             | 员工       |
| POST | /api/v3/upload/image                 | 图片上传                 | 员工       |
| GET  | /api/v3/leads                        | 线索列表                 | 员工       |

---

## 五、技术栈详细说明

### 5.1 前端技术栈
- **框架**：Vue 3.4（Composition API）
- **UI组件库**：Element Plus 2.6
- **构建工具**：Vite 5（代理配置：`/api/v3` → `http://localhost:8080`）
- **状态管理**：Pinia
- **HTTP客户端**：Axios（拦截器已解包`{code, data, message}`，业务代码直接用`res.xxx`）
- **路由**：Vue Router 4（history模式，需Vite historyApiFallback）

### 5.2 后端技术栈
- **框架**：Flask 2.x（工厂模式`create_app()`）
- **ORM**：SQLAlchemy 2.x（模型与数据库表需保持同步）
- **认证**：JWT（jwt_required_v2装饰器，传递`current_user`字典）
- **生产服务器**：Waitress（端口8080，修改后需重启后端）
- **数据库**：SQLite 3（单文件数据库，分店独立库）

### 5.3 微信小程序
- **框架**：原生微信小程序（非uni-app/Taro）
- **核心页面**：首页/案例列表/案例详情/留资表单/预约量尺/产品选品/报价预览
- **要求**：每页必须设留资入口，商业转化优先

---

## 六、开发注意事项（含历史踩坑经验）

### 6.1 编码规范（铁律）
1. **Windows Python文件写入必须指定`encoding='utf-8'`**，禁止混合UTF-8和GBK写入，否则会导致中文乱码、SyntaxError。
2. **Markdown/JSON/JS/Vue等文本文件写入必须用`qclaw-text-file`技能的`write_file.py`脚本**，禁止直接用内置write工具写目标文件，避免跨平台编码问题。
3. **PowerShell脚本**：`.bat`/`.cmd`含中文时用GBK编码，`.ps1`用UTF-8 with BOM。

### 6.2 前端开发规范
1. **Axios拦截器规则**：`request.js`已解包响应（成功时返回`res.data`），业务代码必须直接用`res.xxx`（如`res.items`、`res.total`），禁止用`res.data.xxx`（会导致undefined）。
2. **路由守卫**：未登录跳转`/login`，登录后跳转`/admin/dashboard`，用`createWebHistory`而非hash模式。
3. **el-upload上传**：不经过Axios拦截器，需手动添加`uploadHeaders`携带Bearer Token，避免401。
4. **CSS优先级**：`!important`比`inherit`更可靠，不易被覆盖；UI元素不可见时优先检查CSS（颜色对比度、opacity、z-index、overflow:hidden）。

### 6.3 后端开发规范
1. **认证装饰器**：所有需要登录的路由必须用`jwt_required_v2`，禁止用旧版`token_required`（双轨密钥不同导致401）；路由函数必须加`current_user`参数。
2. **蓝图注册**：所有蓝图必须指定`url_prefix='/api/v3'`，避免前端路径不匹配。
3. **SQLAlchemy模型**：必须与数据库表结构同步，修改模型后需同步迁移数据库；Flask-SQLAlchemy 3.x无`db.text`属性，用`sqlalchemy.text`。
4. **`func.case()`兼容**：新版SQLAlchemy用`elsevalue=`替代`else_`参数，避免语法错误。

### 6.4 历史踩坑经验
| 问题现象                     | 根因                                                     | 解决方案                                                                 |
|------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------|
| 登录后跳转404                 | 用了`createWebHashHistory`导致路径拼接错误                | 改用`createWebHistory` + Vite historyApiFallback                         |
| 已登录仍返回401               | 双轨认证系统（token_required vs jwt_required_v2）密钥不同 | 全面迁移到jwt_required_v2，路由函数加current_user参数                     |
| 报价详情空白                 | customer_name/phone冗余字段未填充                         | ALTER TABLE添加列，回填历史数据                                           |
| 案例筛选status无效            | 前端传`published`但数据库存`已发布`                      | 后端添加STATUS_MAP映射，同时支持中英文筛选                                |
| PDF导出找不到文件             | 后端只返回success无文件路径                               | 新增`/api/v3/quotes/{id}/pdf`端点，返回文件路径，前端用fetch+blob下载    |
| 旧报价空间Tab空白             | 旧报价用扁平items，无space_instances数据                 | 前端做降级展示，无space-instances时直接渲染items列表                       |
| 知识库保存后跳转到登录页     | `knowledge_routes.py`自定义`jwt_required_v2`与全局不一致 | 统一从`auth_routes_v2`导入`jwt_required_v2`                             |
| 幻灯片预览团队页无数据       | API端点路径错误、MaterialCategory导入作用域问题           | 修正端点路径、将MaterialCategory导入移到函数顶部                          |
| 产品中心is_public过滤无效    | 前端`fetchProducts()`未传`is_public=true`               | params添加`is_public: true`                                              |

---

## 七、版本迭代路线图

### 7.1 版本历史
| 版本   | 时间       | 核心更新                                                                 |
|--------|------------|--------------------------------------------------------------------------|
| V3.0.0 | 2026-04   | 品牌重塑（梵木里→帝标·设记家）、认证统一、HR账号管理、分店管理             |
| V3.1.0 | 2026-05-02 | 合同管理、14条全功能合同模板、WeasyPrint PDF导出、楼盘Excel导入、AI填表    |
| V3.2.0 | 2026-05-10 | HoloDome服务流程可视化、首页动态化、楼盘调查系统、案例管理升级             |
| V3.3.0 | 2026-05-22 | 幻灯片模板系统（SlideTemplate模型、6个CRUD路由、前端管理页）                |
| V3.4.0 | 2026-05-28 | 特殊工艺数据库、物料管理筛选栏动态化、产品中心搜索/筛选、is_public修复      |

### 7.2 未来规划（V3.5+）
| 阶段 | 时间规划 | 核心内容                                                                 |
|------|----------|--------------------------------------------------------------------------|
| V3.5 | 2026-06 | 报价对接特殊工艺数据库、幻灯片PhaseMaterialEditor可视化点选、产品中心分页优化 |
| V3.6 | 2026-07 | 物料前台分类页、选品中心Mac风格适配、微信小程序核心功能                     |
| V3.7 | 2026-08 | 多租户完善（分店独立库迁移工具、跨店数据同步、租户权限细化）                |

---

## 八、快速启动

### 8.1 后端启动
```bash
# 用管理员权限运行
D:\desktop\VANMOLY-SYS-V3.0\start_be_v5.bat
# 验证：http://localhost:8080/api/v3/auth/login
```

### 8.2 前端启动
```bash
cd D:\desktop\VANMOLY-SYS-V3.0\frontend
npm run dev
# 访问：http://localhost:5173
```

### 8.3 登录凭据
- 超级管理员：`vanmoly` / `Van9999`
- 测试用户：`test` / `van654321`
- 访客：无需登录，可访问公开案例/物料接口

---

## 九、备份与恢复

### 9.1 备份路径
- 项目完整备份：`D:\desktop\VANMOLY-SYS-V3.0_backup_latest`
- 数据库备份：`backend/instance/vanmoly_v3_backup_latest.db`

### 9.2 恢复步骤
1. 复制备份项目到目标路径
2. 安装依赖：`pip install -r backend/requirements.txt`、`npm install`（前端）
3. 启动后端和前端

---

## 十、Git 仓库

- 远程仓库：`https://github.com/AmethystTim/VANMOLY.git`
- 默认分支：`master`
- 提交规范：英文/中文均可，建议前缀：`feat:` / `fix:` / `chore:` / `docs:`

---

*最后更新：2026-05-28 08:43 GMT+8*
