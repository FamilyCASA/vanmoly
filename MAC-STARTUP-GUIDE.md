# 帝标·设记家全案服务系统 V3.4.0
## Mac 系统启动指南

> 项目路径: `/Users/mac/Desktop/VANMOLY-SYS-V3.0`
> 最后更新: 2026-05-31

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
cd /Users/mac/Desktop/VANMOLY-SYS-V3.0
bash start-system.sh
```

启动后自动打开浏览器访问: **http://localhost:5173**

### 方式二：手动启动

**1. 启动后端 (端口 8080)**
```bash
cd /Users/mac/Desktop/VANMOLY-SYS-V3.0/backend
python3 run.py
```

**2. 启动前端 (端口 5173)**
```bash
cd /Users/mac/Desktop/VANMOLY-SYS-V3.0/frontend
npm run dev
```

---

## 🛑 停止服务

### 一键停止
```bash
cd /Users/mac/Desktop/VANMOLY-SYS-V3.0
bash stop-system.sh
```

### 手动停止
```bash
# 停止后端
lsof -ti:8080 | xargs kill -9

# 停止前端
lsof -ti:5173 | xargs kill -9
```

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端界面** | http://localhost:5173 | Vue 3 + Element Plus |
| **后端 API** | http://localhost:8080 | Flask + SQLAlchemy |
| **后端日志** | `logs/backend.log` | 实时查看: `tail -f logs/backend.log` |
| **前端日志** | `logs/frontend.log` | 实时查看: `tail -f logs/frontend.log` |

---

## 🔧 环境要求

✅ **已安装依赖:**
- Python 3.11.5
- Node.js v22.16.0
- npm 10.9.8

✅ **已安装 Python 包:**
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Waitress 2.1.2
- 其他依赖见 `backend/requirements.txt`

✅ **已安装前端依赖:**
- Vue 3.4
- Element Plus 2.6
- Vite 5.4
- 其他依赖见 `frontend/package.json`

---

## ❓ 常见问题

### 1. 前端报错: `Unsafe attempt to load URL http://localhost/`
**原因:** 前端配置错误，试图访问端口 80 而不是 8080

**解决:**
```bash
# 检查前端配置
cat /Users/mac/Desktop/VANMOLY-SYS-V3.0/frontend/.env
# 应该包含: VITE_API_BASE_URL=/api/v3

# 重启前端
bash stop-system.sh
bash start-system.sh
```

### 2. 后端启动失败
**检查日志:**
```bash
tail -f /Users/mac/Desktop/VANMOLY-SYS-V3.0/logs/backend.log
```

**常见原因:**
- 端口 8080 被占用 → 运行 `lsof -ti:8080 | xargs kill -9`
- Python 依赖缺失 → 运行 `pip3 install -r backend/requirements.txt`

### 3. 前端启动失败
**检查日志:**
```bash
tail -f /Users/mac/Desktop/VANMOLY-SYS-V3.0/logs/frontend.log
```

**常见原因:**
- 端口 5173 被占用 → 运行 `lsof -ti:5173 | xargs kill -9`
- node_modules 缺失 → 运行 `cd frontend && npm install`

---

## 📂 项目结构

```
VANMOLY-SYS-V3.0/
├── backend/              # Flask 后端 (端口 8080)
│   ├── app/             # 应用主目录
│   ├── instance/        # 数据库文件
│   ├── requirements.txt # Python 依赖
│   └── run.py          # 启动入口
├── frontend/            # Vue 3 前端 (端口 5173)
│   ├── src/            # 源代码
│   ├── package.json    # Node.js 依赖
│   ├── vite.config.js # Vite 配置 (代理到 8080)
│   └── .env           # 环境变量
├── miniapp-native/      # 微信小程序
├── start-system.sh      # ⭐ Mac 启动脚本 (新版)
├── stop-system.sh       # ⭐ Mac 停止脚本 (新版)
└── logs/               # 日志目录
    ├── backend.log
    └── frontend.log
```

---

## 🔄 从 Windows 迁移

如果你从 Windows 迁移过来:
- ❌ 删除 `start-all-v3.0.5.bat` (不兼容 Mac)
- ✅ 使用 `start-system.sh` (Mac 版本)
- ✅ 使用 `stop-system.sh` (Mac 版本)

---

## 📞 技术支持

如遇问题，请检查:
1. 端口 8080 和 5173 是否被占用
2. Python 和 Node.js 版本是否符合要求
3. 依赖是否完整安装
4. 查看 `logs/` 目录中的日志文件

---

**系统版本:** V3.4.0  
**最后测试:** 2026-05-31 on macOS 25.3.0  
**作者:** D&B 帝标|设记家技术团队
