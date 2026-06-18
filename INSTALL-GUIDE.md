# VANMOLY-SYS 安装指南

> 适用于 macOS / Windows (WSL/Linux)

---

## 系统要求

| 项目 | 最低要求 |
|------|----------|
| 操作系统 | macOS 12+ / Windows 10+ (WSL) / Ubuntu 20.04+ |
| Python | 3.10+ |
| Node.js | 18+（推荐 20 LTS） |
| 内存 | 4GB+ |
| 磁盘 | 2GB+ |

---

## 第一步：克隆代码

```bash
# 在终端执行
git clone https://github.com/FamilyCASA/vanmoly.git
cd vanmoly
```

> ⚠️ 如果提示需要登录，直接在浏览器打开 https://github.com/FamilyCASA/vanmoly 下载 ZIP 也可以

---

## 第二步：安装后端依赖

### macOS / Linux (WSL)

```bash
cd vanmoly/backend

# 建议先创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows CMD

# 安装依赖
pip install -r requirements.txt
```

### Windows（非 WSL）

```bat
cd vanmoly\backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

---

## 第三步：安装前端依赖

```bash
# 新开一个终端窗口
cd vanmoly/frontend

npm install
```

> 如果 `npm install` 慢，可以切换淘宝镜像：
> ```bash
> npm config set registry https://registry.npmmirror.com
> npm install
> ```

---

## 第四步：初始化数据库

### 如果要使用空数据库（新系统）

```bash
cd vanmoly/backend

# 初始化所有数据库表
python init_databases_v2.py

# 创建管理员账号（默认 admin / van654321）
python create_admin.py
```

### 如果要从这台电脑迁移数据

1. 在原电脑导出数据库：
```bash
cd /Users/mac/VANMOLY-SYS/backend
sqlite3 vanmoly_v3.db ".dump" > vanmoly_v3.sql
sqlite3 quotes.db ".dump" > quotes.sql
sqlite3 app.db ".dump" > app.sql
```

2. 把这 3 个 `.sql` 文件拷贝到新电脑的 `backend/` 目录

3. 在新电脑导入：
```bash
cd vanmoly/backend
sqlite3 vanmoly_v3.db < vanmoly_v3.sql
sqlite3 quotes.db < quotes.sql
sqlite3 app.db < app.sql
```

---

## 第五步：启动系统

### 方式一：开发模式（推荐新手）

**终端窗口 1 - 启动后端：**
```bash
cd vanmoly/backend
python run.py
```
> 后端地址：http://localhost:8080

**终端窗口 2 - 启动前端：**
```bash
cd vanmoly/frontend
npm run dev
```
> 前端地址：http://localhost:5173

### 方式二：一键启动脚本

```bash
cd vanmoly
./start-system.sh
```

### 方式三：macOS App 一键启动

```bash
cd vanmoly
open VANMOLY-SYS.app
```

---

## 访问系统

打开浏览器，访问：

- **前端：** http://localhost:5173
- **默认账号：** `admin`
- **默认密码：** `van654321`

---

## 常见问题

### 1. 端口被占用

```bash
# 查找占用端口的进程
# macOS/Linux:
lsof -i :8080
lsof -i :5173

# Windows:
netstat -ano | findstr :8080

# 杀掉进程（把 PID 换成查到的进程号）
kill -9 PID   # macOS/Linux
taskkill /PID PID /F   # Windows
```

### 2. pip 安装报错

```bash
# 升级 pip
pip install --upgrade pip

# 再试
pip install -r requirements.txt
```

### 3. npm install 失败

```bash
# 清理缓存重装
cd vanmoly/frontend
rm -rf node_modules package-lock.json
npm install
```

### 4. 数据库初始化报错 "table already exists"

说明数据库已经存在，不需要重新初始化，直接启动即可。

### 5. Windows 下编码错误

```bat
chcp 65001
set PYTHONIOENCODING=utf-8
python run.py
```

### 6. 前端无法连接后端

检查后端是否正常运行 http://localhost:8080
确认前端 `.env` 或 `vite.config.js` 中 `VITE_API_BASE_URL` 为 `http://localhost:8080`

---

## 目录结构

```
vanmoly/
├── backend/                 # 后端（Flask）
│   ├── app/               # 应用代码
│   │   ├── routes/        # API 路由
│   │   ├── models/        # 数据模型
│   │   └── ...
│   ├── vanmoly_v3.db      # 主数据库（客户/合同/楼盘等）
│   ├── quotes.db          # 报价数据库
│   ├── app.db             # 应用配置数据库
│   ├── requirements.txt   # Python 依赖
│   ├── run.py             # 后端入口
│   └── upload/            # 上传文件目录
├── frontend/               # 前端（Vue 3 + Vite）
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API 请求
│   │   └── ...
│   ├── package.json       # Node 依赖
│   └── vite.config.js     # Vite 配置
└── start-system.sh         # 一键启动脚本
```

---

## 数据备份

定期备份数据库文件：
```bash
cd vanmoly/backend
cp vanmoly_v3.db ../backups/vanmoly_v3_$(date +%Y%m%d).db
cp quotes.db ../backups/quotes_$(date +%Y%m%d).db
```

---

## 联系支持

如有安装问题，请联系系统管理员。
