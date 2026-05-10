<template>
  <div class="knowledge-index">
    <!-- 头部导航 -->
    <div class="knowledge-header">
      <div class="header-inner">
        <h1 class="logo">📖 设记家商学院</h1>
        <div class="header-actions">
          <template v-if="!isLoggedIn">
            <el-button @click="showAuthDialog = true; authMode = 'login'">登录</el-button>
            <el-button type="primary" @click="showAuthDialog = true; authMode = 'register'">注册</el-button>
          </template>
          <template v-else>
            <span class="user-name">👤 {{ currentUser?.name }}</span>
            <span class="user-star">⭐ {{ currentUser?.personal_star || 0 }} 星星</span>
            <el-button size="small" @click="logout">退出</el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="knowledge-body" v-if="!currentBase">
      <div class="section-title">选择知识库开始学习</div>
      <div class="base-grid">
        <div
          v-for="base in bases"
          :key="base.id"
          class="base-card"
          @click="enterBase(base)"
        >
          <div class="base-cover">
            <img v-if="base.cover_image" :src="resolveImg(base.cover_image)" />
            <div v-else class="base-cover-placeholder">📚</div>
          </div>
          <div class="base-info">
            <h3>{{ base.name }}</h3>
            <p>{{ base.description || '点击进入学习' }}</p>
            <div class="base-meta">
              <span>📂 {{ base.node_count || 0 }} 个章节</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && bases.length === 0" description="暂无知识库" />
    </div>

    <!-- 知识库详情 -->
    <div class="knowledge-detail" v-else>
      <div class="detail-header">
        <el-button link @click="currentBase = null">
          <el-icon><ArrowLeft /></el-icon> 返回知识库列表
        </el-button>
        <h2>📖 {{ currentBase.name }}</h2>
      </div>

      <!-- 树状结构 -->
      <div class="tree-list">
        <div
          v-for="node in treeData"
          :key="node.id"
          class="tree-item level-1"
        >
          <!-- 一级标题 -->
          <div class="tree-item-header" @click="toggleNode(node)">
            <div class="item-left">
              <el-icon class="toggle-icon"><component :is="node._open ? 'Minus' : 'Plus'" /></el-icon>
              <el-tag type="primary" size="small">一级</el-tag>
              <span class="item-name">{{ node.node_name }}</span>
            </div>
            <span class="item-views">{{ node.view_count || 0 }}次浏览</span>
          </div>

          <!-- 二级章节 -->
          <template v-if="node._open && node.children">
            <div
              v-for="child in node.children"
              :key="child.id"
              class="tree-item level-2"
            >
              <div class="tree-item-header" @click="toggleNode(child)">
                <div class="item-left">
                  <el-icon class="toggle-icon"><component :is="child._open ? 'Minus' : 'Plus'" /></el-icon>
                  <el-tag type="success" size="small">二级</el-tag>
                  <span class="item-name">{{ child.node_name }}</span>
                </div>
                <span class="item-views">{{ child.view_count || 0 }}次浏览</span>
              </div>

              <!-- 三级小节 -->
              <template v-if="child._open && child.children">
                <div
                  v-for="leaf in child.children"
                  :key="leaf.id"
                  class="tree-item level-3"
                >
                  <div class="tree-item-header leaf" @click="openContent(leaf)">
                    <div class="item-left">
                      <el-tag type="warning" size="small">三级</el-tag>
                      <span class="item-name">{{ leaf.node_name }}</span>
                      <el-tag v-if="leaf.video_url" type="info" size="small">含视频</el-tag>
                    </div>
                    <el-button size="small" type="primary" plain>开始学习 →</el-button>
                  </div>
                </div>
              </template>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 内容阅读弹窗 -->
    <el-dialog v-model="contentVisible" :title="currentContent?.node_name" width="820px"
      :fullscreen="contentFullscreen">
      <div class="content-viewer">
        <!-- 文案内容 -->
        <div class="content-html" v-html="currentContent?.content || '<p style=\'color:#999;text-align:center\'>暂无内容</p>'" />

        <!-- 视频 -->
        <div v-if="currentContent?.video_url" class="video-area">
          <div class="video-embed">
            <iframe
              v-if="getVideoEmbedUrl(currentContent.video_url)"
              :src="getVideoEmbedUrl(currentContent.video_url)"
              allowfullscreen
              frameborder="0"
            />
            <a v-else :href="currentContent.video_url" target="_blank" class="video-link">
              🔗 点击查看视频（外部链接）
            </a>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="content-footer">
          <span class="view-count">浏览 {{ currentContent?.view_count || 0 }} 次</span>
          <div class="footer-actions">
            <el-button @click="contentFullscreen = !contentFullscreen">
              {{ contentFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
            <el-button @click="contentVisible = false">关闭</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 注册/登录弹窗 -->
    <el-dialog v-model="showAuthDialog" :title="authMode === 'register' ? '注册账号' : '登录账号'" width="420px">
      <el-form :model="authForm" label-width="80px">
        <el-form-item label="姓名" v-if="authMode === 'register'">
          <el-input v-model="authForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="authForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="authForm.password" type="password" placeholder="请输入密码"
            @keyup.enter="doAuth" />
        </el-form-item>
        <el-form-item label="地区" v-if="authMode === 'register'">
          <el-input v-model="authForm.region" placeholder="如：四川成都" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="authMode = authMode === 'register' ? 'login' : 'register'">
          {{ authMode === 'register' ? '已有账号？登录' : '没有账号？注册' }}
        </el-button>
        <el-button type="primary" :loading="authLoading" @click="doAuth">
          {{ authMode === 'register' ? '注册' : '登录' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 解锁提示 -->
    <el-dialog v-model="showUnlockTip" title="解锁提示" width="400px">
      <p style="text-align:center;line-height:1.8">
        📚 当前章节需注册登录后解锁<br/>
        当前星星：<strong>⭐ {{ currentUser?.personal_star || 0 }}</strong><br/>
        解锁条件：累计 <strong>10</strong> 颗星星可解锁新章节
      </p>
      <template #footer>
        <el-button @click="showUnlockTip = false">继续浏览公开内容</el-button>
        <el-button type="primary" @click="showUnlockTip = false; showAuthDialog = true; authMode = 'register'">
          立即注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ArrowLeft, Plus, Minus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const bases = ref([])
const loading = ref(false)
const currentBase = ref(null)
const treeData = ref([])

// 登录状态
const isLoggedIn = ref(false)
const currentUser = ref(null)
const showAuthDialog = ref(false)
const authMode = ref('login')
const authLoading = ref(false)
const authForm = reactive({ name: '', phone: '', password: '', region: '' })

// 内容弹窗
const contentVisible = ref(false)
const contentFullscreen = ref(false)
const currentContent = ref(null)

// 解锁提示
const showUnlockTip = ref(false)

const VITE_API_BASE = import.meta.env.VITE_API_BASE || ''

onMounted(() => {
  checkLogin()
  loadBases()
})

function checkLogin() {
  const token = localStorage.getItem('front_token')
  const userStr = localStorage.getItem('front_user')
  if (token && userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
      isLoggedIn.value = true
    } catch {}
  }
}

function loadBases() {
  loading.value = true
  request.get('/knowledge/public/bases').then(res => {
    if (res.code === 200) bases.value = res.data
  }).finally(() => { loading.value = false })
}

function enterBase(base) {
  currentBase.value = base
  loadTree(base.id)
}

function loadTree(baseId) {
  request.get(`/knowledge/public/bases/${baseId}/tree`).then(res => {
    if (res.code === 200) {
      // 初始化展开状态
      treeData.value = res.data.map(n => ({ ...n, _open: false }))
    }
  })
}

function toggleNode(node) {
  node._open = !node._open
}

function openContent(node) {
  if (!isLoggedIn.value) {
    showUnlockTip.value = true
    return
  }
  // 记录浏览
  request.post(`/knowledge/nodes/${node.id}/view`)
  currentContent.value = node
  contentVisible.value = true
}

function getVideoEmbedUrl(url) {
  if (!url) return ''
  // 视频号
  if (url.includes('channels.weixin.qq.com')) return url
  // B站
  const bv = url.match(/bilibili\.com\/video\/(BV\w+)/)
  if (bv) return `//player.bilibili.com/player.html?bvid=${bv[1]}`
  // 抖音
  if (url.includes('douyin.com')) return url
  return ''
}

function resolveImg(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${VITE_API_BASE}${path.startsWith('/') ? '' : '/'}${path}`
}

function doAuth() {
  if (!authForm.phone || !authForm.password) {
    ElMessage.warning('请填写手机号和密码')
    return
  }
  if (authMode.value === 'register' && !authForm.name) {
    ElMessage.warning('请填写姓名')
    return
  }
  authLoading.value = true
  const endpoint = authMode.value === 'register' ? '/knowledge/auth/register' : '/knowledge/auth/login'
  request.post(endpoint, { ...authForm }).then(res => {
    if (res.code === 200) {
      if (authMode.value === 'register') {
        ElMessage.success('注册成功，请登录')
        authMode.value = 'login'
      } else {
        ElMessage.success('登录成功')
        localStorage.setItem('front_token', res.data.token || '1')
        localStorage.setItem('front_user', JSON.stringify(res.data.user))
        currentUser.value = res.data.user
        isLoggedIn.value = true
        showAuthDialog.value = false
      }
    }
  }).finally(() => { authLoading.value = false })
}

function logout() {
  localStorage.removeItem('front_token')
  localStorage.removeItem('front_user')
  isLoggedIn.value = false
  currentUser.value = null
  ElMessage.success('已退出')
}
</script>

<style scoped>
.knowledge-index {
  min-height: 100vh;
  background: #0a0a0f;
  color: #fff;
}

/* 头部 */
.knowledge-header {
  background: linear-gradient(135deg, #8B5A2B 0%, #5c3a1e 100%);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-name {
  font-size: 14px;
  color: #e8d5c4;
}
.user-star {
  font-size: 14px;
  color: #ffd700;
}

/* 主体 */
.knowledge-body {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
}
.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 32px;
  color: #e8d5c4;
  text-align: center;
}

/* 知识库卡片 */
.base-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}
.base-card {
  background: #16161e;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #2a2a3a;
  transition: all 0.3s;
}
.base-card:hover {
  transform: translateY(-4px);
  border-color: #8B5A2B;
  box-shadow: 0 8px 32px rgba(139, 90, 43, 0.3);
}
.base-cover {
  height: 160px;
  background: linear-gradient(135deg, #1e1e2e, #2a2a3a);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
}
.base-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.base-cover-placeholder {
  font-size: 64px;
}
.base-info {
  padding: 20px;
}
.base-info h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #e8d5c4;
}
.base-info p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #8c8c9c;
  line-height: 1.5;
}
.base-meta {
  font-size: 13px;
  color: #6c6c7c;
}

/* 详情页 */
.knowledge-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}
.detail-header {
  margin-bottom: 32px;
}
.detail-header h2 {
  margin: 16px 0 0;
  font-size: 28px;
  color: #e8d5c4;
}

/* 树状列表 */
.tree-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.tree-item {
  border-radius: 10px;
  overflow: hidden;
}
.tree-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.2s;
}
.tree-item.level-1 > .tree-item-header {
  background: #1e1e2e;
  border-left: 3px solid #8B5A2B;
}
.tree-item.level-2 > .tree-item-header {
  background: #18181f;
  margin-left: 20px;
  border-left: 3px solid #c4956a;
}
.tree-item.level-3 > .tree-item-header {
  background: #12121a;
  margin-left: 40px;
  border-left: 3px solid #d4a574;
}
.tree-item-header:hover {
  background: #2a2a3a;
}
.item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.toggle-icon {
  color: #8B5A2B;
  font-size: 16px;
}
.item-name {
  font-size: 15px;
  color: #e8d5c4;
}
.item-views {
  font-size: 12px;
  color: #5c5c6c;
}

/* 内容弹窗 */
.content-viewer {
  max-height: 70vh;
  overflow-y: auto;
  line-height: 1.9;
  font-size: 15px;
  color: #e0e0e0;
}
.content-html :deep(p) {
  margin-bottom: 16px;
}
.content-html :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
}
.video-area {
  margin-top: 24px;
}
.video-embed {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  border-radius: 8px;
  background: #000;
}
.video-embed iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.video-link {
  display: block;
  padding: 40px;
  text-align: center;
  color: #8B5A2B;
  font-size: 16px;
}
.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.view-count {
  font-size: 13px;
  color: #8c8c9c;
}
.footer-actions {
  display: flex;
  gap: 8px;
}
</style>
