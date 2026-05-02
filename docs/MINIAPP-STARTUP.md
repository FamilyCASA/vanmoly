# 微信小程序模拟器启动指南

## 方式一：HBuilder X 模拟器（推荐）

### 1. 安装 HBuilder X
- 下载地址：https://www.dcloud.io/hbuilderx.html
- 安装并启动

### 2. 打开项目
1. 点击菜单 `文件` → `打开目录`
2. 选择 `D:\desktop\DESIGNARY-SYS-V3.0\miniapp`
3. 等待项目加载完成

### 3. 运行到微信开发者工具
1. 确保已安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 在 HBuilder X 中点击菜单 `运行` → `运行到小程序模拟器` → `微信开发者工具`
3. 首次运行需要配置微信开发者工具路径

### 4. 配置微信开发者工具
1. 打开微信开发者工具
2. 点击 `设置` → `安全设置`
3. 开启 `服务端口`
4. 返回 HBuilder X 重新运行

---

## 方式二：直接使用微信开发者工具

### 1. 打开微信开发者工具
1. 启动微信开发者工具
2. 点击 `+` 号创建新项目
3. 选择项目目录：`D:\desktop\DESIGNARY-SYS-V3.0\miniapp`
4. AppID 填写：`wx1234567890abcdef`（测试号）
5. 点击确定

### 2. 配置后端 API 地址
如果后端不在本机，需要修改 `miniapp/pages/index/index.vue` 中的请求地址：

```javascript
// 修改为你的后端地址
url: 'http://192.168.8.84:5000/api/v3/cases'
```

---

## 方式三：uni-app CLI 命令行

### 1. 安装依赖
```bash
cd D:\desktop\DESIGNARY-SYS-V3.0\miniapp
npm install -g @dcloudio/uni-app-cli
```

### 2. 运行到微信小程序
```bash
npm run dev:mp-weixin
```

### 3. 在微信开发者工具中导入
1. 打开微信开发者工具
2. 选择 `导入项目`
3. 选择 `D:\desktop\DESIGNARY-SYS-V3.0\miniapp\dist\dev\mp-weixin`

---

## 常见问题

### 1. 请求后端 API 失败
- 确保后端服务已启动：`http://localhost:5000`
- 在微信开发者工具中开启「不校验合法域名」
- 设置 → 项目设置 → 勾选「不校验合法域名、web-view...」

### 2. 真机调试
- 点击微信开发者工具中的「真机调试」
- 扫描二维码在手机上预览

### 3. 模拟器白屏
- 检查 manifest.json 配置
- 清除缓存重新编译

---

## 手写签名功能测试

### 在 Web 端测试
1. 访问 `http://localhost:3001/admin/quotes`
2. 创建报价 → 第5步「签字确认」
3. 点击签名区域，使用 Canvas 手写签名

### 在小程序端测试
1. 启动小程序模拟器
2. 需要在小程序中配置 WebView 页面跳转
3. 或使用小程序原生签名页面：`pages/signature/index`

---

## 目录结构

```
miniapp/
├── manifest.json          # 应用配置
├── pages.json             # 页面路由
├── main.js                # 入口文件
├── App.vue                # 根组件
├── uni.scss               # 全局样式变量
├── pages/                 # 页面
│   ├── index/             # 首页
│   ├── case/              # 案例
│   ├── lead/              # 留资
│   ├── appointment/       # 预约
│   └── signature/         # 手写签名
└── static/                # 静态资源
    ├── banner/            # Banner图
    └── tabbar/            # Tab图标
```

---

## 下一步

1. 完善小程序页面（案例列表、案例详情、留资表单、预约量尺）
2. 配置后端 API 域名
3. 申请正式微信小程序 AppID
4. 发布上线
