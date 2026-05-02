# D&B 帝标|设记家系统 V3.0 端口配置

## 统一端口规范（2026-04-27 更新）

| 服务 | 端口 | 用途 |
|:---|:---|:---|
| 后端 API | **8080** | Flask + Waitress 服务器 |
| 前端开发 | **5173** | Vite 开发服务器（默认） |

## 访问地址

- **前台页面**: http://localhost:5173
- **后台管理**: http://localhost:5173/admin
- **API 文档**: http://localhost:8080/api/v3/health

## 已修改的文件

### 后端启动脚本（全部统一为 8080）
- `backend/run.py` - 开发服务器
- `backend/run_waitress.py` - Waitress 生产服务器
- `backend/run_simple.py` - 简化版启动
- `backend/run_minimal.py` - 最小化启动
- `backend/run_stable.py` - 稳定版启动
- `backend/run_prod.py` - 生产环境
- `backend/run_production.py` - 生产环境（waitress）
- `backend/run_keepalive.py` - 保持活动模式
- `backend/run_api_server.py` - 轻量级 API 服务器
- `backend/run_api_server_v2.py` - 完整 API 服务器
- `backend/run_stable_server.py` - 稳定版 API 服务器

### 前端配置
- `frontend/vite.config.js` - Vite 服务器端口 + 代理目标

### 启动脚本
- `start-all-v3.0.5.bat` - 一键启动脚本

## 历史端口（已废弃）

- ~~5000~~ - 与 macOS AirPlay 冲突
- ~~8000~~ - 常见开发端口，易冲突
- ~~9090~~ - 临时使用，不稳定
- ~~3000/3001~~ - 旧前端端口

## 环境变量（可选）

如需自定义端口，可创建 `.env` 文件：

```bash
# 后端端口（默认 8080）
FLASK_PORT=8080

# 前端端口（默认 5173）
VITE_PORT=5173
```
