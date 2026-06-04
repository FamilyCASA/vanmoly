# VANMOLY-SYS-V3.0 Git 版本管理教程

## 一、基础命令

```powershell
# 添加文件到暂存区（添加全部文件用 git add .）
git add <文件名>

# 提交暂存区到本地仓库
git commit -m "提交说明"

# 查看仓库状态
git status

# 查看提交历史
git log
```

---

## 二、远程仓库配置

| Remote | 地址 | 用途 |
|--------|------|------|
| `local` | `file:///D:/vanmoly-local.git` | 本地备份，秒级推送，无网络依赖 |
| `origin` | `git@github.com:AmethystTim/VANMOLY.git` | GitHub 远程仓库 |

---

## 三、推送代码

```powershell
# 推送到本地备份（秒级完成，无网络问题）
git push local master

# 推送到 GitHub（需要网络）
git push origin master

# 两个都推
git push local master; git push origin master
```

---

## 四、日常提交流程

```powershell
# 1. 添加修改的文件
git add .

# 2. 提交
git commit -m "你的修改说明"

# 3. 推送到本地备份
git push local master

# 4. 网络好时，推送到 GitHub
git push origin master
```

---

## 五、同步与恢复

```powershell
# 从远程仓库同步到本地
git pull origin master

# 从本地备份恢复整个项目
git clone file:///D:/vanmoly-local.git

# 从 GitHub 恢复整个项目
git clone https://github.com/AmethystTim/VANMOLY.git

# 从 GitHub 浅克隆（只拉取最新代码，不含历史）
git clone --depth=1 https://github.com/AmethystTim/VANMOLY.git
```

---

## 六、推送失败时

如果推送到 GitHub 失败，先在终端中粘贴代理命令（从 Clash for Windows 复制，一般选 PowerShell 格式），然后重试：

```powershell
# 增大 HTTP buffer（处理大仓库推送超时）
git config --global http.postBuffer 1048576000

# 重新推送
git push origin master
```

---

## 七、常用操作速查

| 操作 | 命令 |
|------|------|
| 查看状态 | `git status` |
| 查看历史 | `git log --oneline` |
| 撤销暂存 | `git restore --staged <文件>` |
| 丢弃修改 | `git restore <文件>` |
| 查看差异 | `git diff` |
| 切换分支 | `git checkout <分支名>` |
| 创建分支 | `git checkout -b <新分支名>` |
