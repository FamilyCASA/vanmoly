# D&B 帝标|设记家全安落地服务系统 DEMO V.0.1

> 从「内部管理工具」升级为「品牌展示 + 获客转化 + 服务管理」一体化平台

## 项目结构

```
DESIGNARY-SYS-V3.0/
├── backend/                    # Flask 后端服务
│   ├── app/
│   │   ├── __init__.py         # 应用工厂
│   │   ├── models/             # 数据模型
│   │   │   ├── case.py         # 案例模型
│   │   │   ├── lead.py         # 线索模型
│   │   │   ├── appointment.py  # 预约模型
│   │   │   ├── coupon.py       # 优惠券模型
│   │   │   ├── material.py     # 物料模型
│   │   │   ├── article.py      # 文章模型
│   │   │   └── employee.py     # 员工模型
│   │   └── routes/             # API路由
│   │       ├── case_routes.py      # 案例API
│   │       ├── lead_routes.py      # 留资API
│   │       ├── appointment_routes.py
│   │       ├── coupon_routes.py
│   │       ├── material_routes.py
│   │       ├── article_routes.py
│   │       └── dashboard_routes.py
│   ├── config.py               # 配置文件
│   ├── run.py                  # 启动入口
│   └── requirements.txt        # 依赖清单
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/                # API封装
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面视图
│   │   ├── router/             # 路由配置
│   │   ├── store/              # 状态管理
│   │   └── utils/              # 工具函数
│   ├── package.json
│   └── vite.config.js
├── miniapp/                    # 微信小程序
├── database/                   # 数据库脚本
│   └── schema_v3.0.sql
└── docs/                       # 项目文档
    ├── V3.0-Development-Guide.md
    └── Implementation-Progress.md
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端服务将在 http://localhost:5000 启动

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 http://localhost:3000 启动

## 核心功能

### Phase 1 - 核心获客能力（已完成）

- [x] 案例展示中心
  - [x] 案例列表（筛选/搜索/分页）
  - [x] 案例详情（图片画廊/留资入口）
  - [x] 精选案例展示
  
- [x] 留资引导系统
  - [x] 留资表单组件
  - [x] 线索管理API
  - [x] 跟进记录功能

- [x] 预约量尺（基础页面）

### Phase 2 - 增强体验（待开发）

- [ ] 优惠券系统
- [ ] 销售物料中心
- [ ] 数据看板增强

### Phase 3 - 品牌沉淀（待开发）

- [ ] 文章/动态系统
- [ ] 微信小程序
- [ ] 高级功能（视频/360全景）

## API 文档

详见 `docs/V3.0-Development-Guide.md`

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端 | Flask | 2.3+ |
| 后端 | SQLAlchemy | 2.0+ |
| 后端 | SQLite | 3.x |
| 前端 | Vue | 3.4+ |
| 前端 | Element Plus | 2.6+ |
| 前端 | Pinia | 2.1+ |

## 开发规范

- 后端遵循 PEP 8 规范
- 前端使用 Composition API
- Git 提交使用规范格式: `type(scope): subject`

## 许可证

MIT
