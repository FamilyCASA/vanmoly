<template>
  <div class="knowledge-index">
    <!-- 头部导航 -->
    <div class="knowledge-header">
      <div class="header-inner">
        <h1 class="logo">📖 设记家商学院</h1>
        <div class="header-actions">
          <div class="search-box">
            <el-input v-model="searchQuery" placeholder="搜索文章..." clearable @keyup.enter="doSearch">
              <template #prefix><el-icon><Search /></el-icon></template>
              <template #append>
                <el-button @click="doSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
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

    <!-- 搜索结果页 -->
    <div v-if="searchResults !== null" class="knowledge-body">
      <div class="detail-header">
        <el-button link @click="exitSearch">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <h2>搜索结果：{{ searchQuery }}</h2>
      </div>
      <div class="article-list" v-if="searchResults.length">
        <div v-for="article in searchResults" :key="article.id" class="article-item" @click="readArticle(article)">
          <div class="article-item-cover" v-if="article.cover_image">
            <img :src="resolveImg(article.cover_image)" />
          </div>
          <div class="article-item-info">
            <h3>{{ article.title }}</h3>
            <p>{{ article.summary || '暂无摘要' }}</p>
            <div class="article-item-meta">
              <span>👤 {{ article.author || '佚名' }}</span>
              <span>👁️ {{ article.view_count || 0 }}</span>
              <span>👍 {{ article.like_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="未找到相关文章" />
    </div>

    <!-- 知识库列表页 -->
    <div v-else-if="!currentBase" class="knowledge-body">
      <!-- 分类导航 -->
      <div class="category-nav">
        <div
          v-for="cat in categories"
          :key="cat.id || 'all'"
          class="cat-nav-item"
          :class="{ active: activeCategory === (cat.id || null) }"
          @click="filterByCategory(cat.id || null)"
        >
          {{ cat.name }}
          <span class="cat-count">{{ cat.base_count || 0 }}</span>
        </div>
      </div>

      <div class="section-title">选择知识库开始学习</div>
      <div class="base-grid" v-loading="loading">
        <div
          v-for="base in filteredBases"
          :key="base.id"
          class="base-card"
          :style="{ '--theme-color': base.theme_color || '#8B5A2B' }"
          @click="enterBase(base)"
        >
          <div class="base-cover">
            <img v-if="base.cover_image" :src="resolveImg(base.cover_image)" />
            <div v-else class="base-cover-placeholder">{{ base.icon || '📚' }}</div>
          </div>
          <div class="base-info">
            <div class="base-info-header">
              <h3>{{ base.name }}</h3>
              <el-tag
                v-if="base.category_name"
                size="small"
                :style="{ backgroundColor: base.theme_color || '#8B5A2B', color: '#fff', border: 'none' }"
              >{{ base.category_name }}</el-tag>
            </div>
            <p>{{ base.description || '点击进入学习' }}</p>
            <div class="base-meta">
              <span>📂 {{ base.node_count || 0 }} 章节</span>
              <span>📄 {{ base.article_count || 0 }} 文章</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && filteredBases.length === 0" description="暂无知识库" />
    </div>

    <!-- 知识库详情页 -->
    <div v-else-if="!currentArticle" class="knowledge-detail">
      <div class="detail-header">
        <el-button link @click="backToBases">
          <el-icon><ArrowLeft /></el-icon> 返回知识库列表
        </el-button>
        <h2 :style="{ color: currentBase.theme_color || '#e8d5c4' }">
          {{ currentBase.icon || '📖' }} {{ currentBase.name }}
        </h2>
        <p v-if="currentBase.description" class="detail-desc">{{ currentBase.description }}</p>
      </div>

      <!-- 视图切换 -->
      <div class="view-switch">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="tree">📁 目录树</el-radio-button>
          <el-radio-button value="list">📄 文章列表</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 目录树视图 -->
      <div v-if="viewMode === 'tree'" class="tree-list">
        <div v-for="node in treeData" :key="node.id" class="tree-item level-1">
          <div class="tree-item-header" @click="toggleNode(node)">
            <div class="item-left">
              <el-icon class="toggle-icon"><component :is="node._open ? 'Minus' : 'Plus'" /></el-icon>
              <el-tag type="primary" size="small">一级</el-tag>
              <span class="item-name">{{ node.node_name }}</span>
              <span v-if="node.article_count" class="item-count">📄 {{ node.article_count }}</span>
            </div>
            <span class="item-views">{{ node.view_count || 0 }}次浏览</span>
          </div>
          <template v-if="node._open && node.children">
            <div v-for="child in node.children" :key="child.id" class="tree-item level-2">
              <div class="tree-item-header" @click="toggleNode(child)">
                <div class="item-left">
                  <el-icon class="toggle-icon"><component :is="child._open ? 'Minus' : 'Plus'" /></el-icon>
                  <el-tag type="success" size="small">二级</el-tag>
                  <span class="item-name">{{ child.node_name }}</span>
                  <span v-if="child.article_count" class="item-count">📄 {{ child.article_count }}</span>
                </div>
                <span class="item-views">{{ child.view_count || 0 }}次浏览</span>
              </div>
              <template v-if="child._open && child.children">
                <div v-for="leaf in child.children" :key="leaf.id" class="tree-item level-3">
                  <div class="tree-item-header leaf" @click="openNodeContent(leaf)">
                    <div class="item-left">
                      <el-tag type="warning" size="small">三级</el-tag>
                      <span class="item-name">{{ leaf.node_name }}</span>
                      <el-tag v-if="leaf.video_url" type="info" size="small">含视频</el-tag>
                      <span v-if="leaf.article_count" class="item-count">📄 {{ leaf.article_count }}</span>
                    </div>
                    <el-button size="small" type="primary" plain>开始学习 →</el-button>
                  </div>
                </div>
              </template>
            </div>
          </template>
        </div>
      </div>

      <!-- 文章列表视图 -->
      <div v-else class="article-list">
        <div v-for="article in baseArticles" :key="article.id" class="article-item" @click="readArticle(article)">
          <div class="article-item-cover" v-if="article.cover_image">
            <img :src="resolveImg(article.cover_image)" />
          </div>
          <div class="article-item-info">
            <h3>{{ article.title }}</h3>
            <p>{{ article.summary || '暂无摘要' }}</p>
            <div class="article-item-meta">
              <span>👤 {{ article.author || '佚名' }}</span>
              <span>👁️ {{ article.view_count || 0 }}</span>
              <span>👍 {{ article.like_count || 0 }}</span>
              <span v-if="article.node_name">📂 {{ article.node_name }}</span>
            </div>
          </div>
        </div>
        <el-empty v-if="baseArticles.length === 0" description="暂无文章" />
      </div>
    </div>

    <!-- 文章阅读页 -->
    <div v-else class="article-reader">
      <div class="reader-header">
        <el-button link @click="backToBase">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <div class="reader-actions">
          <el-button size="small" @click="toggleReaderFullscreen">
            {{ readerFullscreen ? '退出全屏' : '全屏' }}
          </el-button>
          <el-button size="small" type="primary" plain @click="likeArticle(currentArticle)">
            👍 {{ currentArticle.like_count || 0 }}
          </el-button>
        </div>
      </div>

      <div class="reader-body">
        <h1 class="article-title">{{ currentArticle.title }}</h1>
        <div class="article-meta">
          <span>👤 {{ currentArticle.author || '佚名' }}</span>
          <span>👁️ {{ currentArticle.view_count || 0 }} 浏览</span>
          <span>👍 {{ currentArticle.like_count || 0 }} 点赞</span>
          <span v-if="currentArticle.updated_at">🕐 {{ currentArticle.updated_at }}</span>
        </div>
        <div class="article-tags" v-if="currentArticle.tags">
          <el-tag v-for="tag in (currentArticle.tags || '').split(',').filter(t => t.trim())" :key="tag" size="small" effect="plain">{{ tag.trim() }}</el-tag>
        </div>
        <div class="article-cover" v-if="currentArticle.cover_image">
          <img :src="resolveImg(currentArticle.cover_image)" />
        </div>
        <div class="article-content" v-html="currentArticle.content || '<p style=\'color:#999;text-align:center\'>暂无内容</p>'"></div>

        <div v-if="currentArticle.video_url" class="video-area">
          <div class="video-embed">
            <iframe
              v-if="getVideoEmbedUrl(currentArticle.video_url)"
              :src="getVideoEmbedUrl(currentArticle.video_url)"
              allowfullscreen
              frameborder="0"
            />
            <a v-else :href="currentArticle.video_url" target="_blank" class="video-link">
              🔗 点击查看视频（外部链接）
            </a>
          </div>
        </div>

        <div class="article-footer">
          <el-button type="primary" size="large" @click="likeArticle(currentArticle)">
            👍 点赞 ({{ currentArticle.like_count || 0 }})
          </el-button>
        </div>
      </div>
    </div>

    <!-- 节点内容弹窗（目录树模式下点击叶子节点） -->
    <el-dialog v-model="nodeContentVisible" :title="currentNode?.node_name" width="820px"
      :fullscreen="nodeContentFullscreen">
      <div class="content-viewer">
        <div class="content-html" v-html="currentNode?.content || '<p style=\'color:#999;text-align:center\'>暂无内容</p>'" />
        <div v-if="currentNode?.video_url" class="video-area">
          <div class="video-embed">
            <iframe
              v-if="getVideoEmbedUrl(currentNode.video_url)"
              :src="getVideoEmbedUrl(currentNode.video_url)"
              allowfullscreen
              frameborder="0"
            />
            <a v-else :href="currentNode.video_url" target="_blank" class="video-link">
              🔗 点击查看视频（外部链接）
            </a>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="content-footer">
          <span class="view-count">浏览 {{ currentNode?.view_count || 0 }} 次</span>
          <div class="footer-actions">
            <el-button @click="nodeContentFullscreen = !nodeContentFullscreen">
              {{ nodeContentFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
            <el-button @click="nodeContentVisible = false">关闭</el-button>
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
          <el-input v-model="authForm.password" type="password" placeholder="请输入密码" @keyup.enter="doAuth" />
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
import { ArrowLeft, Plus, Minus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// ==================== 状态 ====================
const bases = ref([])
const categories = ref([])
const loading = ref(false)
const activeCategory = ref(null)
const currentBase = ref(null)
const currentArticle = ref(null)
const treeData = ref([])
const baseArticles = ref([])
const viewMode = ref('tree')

// 搜索
const searchQuery = ref('')
const searchResults = ref(null)

// 登录状态
const isLoggedIn = ref(false)
const currentUser = ref(null)
const showAuthDialog = ref(false)
const authMode = ref('login')
const authLoading = ref(false)
const authForm = reactive({ name: '', phone: '', password: '', region: '' })

// 节点内容弹窗
const nodeContentVisible = ref(false)
const nodeContentFullscreen = ref(false)
const currentNode = ref(null)

// 全屏阅读
const readerFullscreen = ref(false)

const VITE_API_BASE = import.meta.env.VITE_API_BASE || ''

onMounted(() => {
  checkLogin()
  loadBases()
  loadCategories()
})

// ==================== 登录 ====================
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

function logout() {
  localStorage.removeItem('front_token')
  localStorage.removeItem('front_user')
  isLoggedIn.value = false
  currentUser.value = null
  ElMessage.success('已退出')
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
    if (res && res.token) {
      if (authMode.value === 'register') {
        ElMessage.success('注册成功，请登录')
        authMode.value = 'login'
      } else {
        ElMessage.success('登录成功')
        localStorage.setItem('front_token', res.token)
        localStorage.setItem('front_user', JSON.stringify(res.user || res))
        currentUser.value = res.user || res
        isLoggedIn.value = true
        showAuthDialog.value = false
      }
    } else {
      ElMessage.error('操作失败')
    }
  }).finally(() => { authLoading.value = false })
}

// ==================== 分类 ====================
function loadCategories() {
  request.get('/knowledge/categories').then(res => {
    if (Array.isArray(res)) {
      categories.value = [{ id: null, name: '全部', base_count: 0 }, ...res]
    } else {
      categories.value = [{ id: null, name: '全部', base_count: 0 }]
    }
  })
}

function filterByCategory(catId) {
  activeCategory.value = catId
}

const filteredBases = computed(() => {
  if (!activeCategory.value) return bases.value
  return bases.value.filter(b => b.category_id === activeCategory.value)
})

// ==================== 知识库 ====================
function loadBases() {
  loading.value = true
  request.get('/knowledge/bases').then(res => {
    if (res && res.items) bases.value = res.items
    else if (Array.isArray(res)) bases.value = res
    else bases.value = []
  }).finally(() => { loading.value = false })
}

function enterBase(base) {
  currentBase.value = base
  currentArticle.value = null
  viewMode.value = 'tree'
  loadTree(base.id)
  loadBaseArticles(base.id)
}

function backToBases() {
  currentBase.value = null
  currentArticle.value = null
}

// ==================== 树状结构 ====================
function loadTree(baseId) {
  request.get(`/knowledge/bases/${baseId}/tree`).then(res => {
    if (Array.isArray(res)) {
      treeData.value = res.map(n => ({ ...n, _open: false }))
    } else {
      treeData.value = []
    }
  })
}

function toggleNode(node) {
  node._open = !node._open
}

function openNodeContent(node) {
  if (!isLoggedIn.value) {
    showUnlockTip.value = true
    return
  }
  request.post(`/knowledge/nodes/${node.id}/view`).catch(() => {})
  currentNode.value = node
  nodeContentVisible.value = true
}

// ==================== 文章 ====================
function loadBaseArticles(baseId) {
  request.get('/knowledge/articles', { params: { base_id: baseId, page: 1, pageSize: 100 } }).then(res => {
    if (res && res.items) baseArticles.value = res.items
    else if (Array.isArray(res)) baseArticles.value = res
    else baseArticles.value = []
  })
}

function readArticle(article) {
  if (!isLoggedIn.value && article.status !== 'published') {
    showUnlockTip.value = true
    return
  }
  request.post(`/knowledge/articles/${article.id}/view`).catch(() => {})
  if (!article.content) {
    request.get(`/knowledge/articles/${article.id}`).then(res => {
      if (res) {
        currentArticle.value = { ...article, ...res }
      } else {
        currentArticle.value = article
      }
    })
  } else {
    currentArticle.value = article
  }
}

function backToBase() {
  currentArticle.value = null
}

function likeArticle(article) {
  if (!isLoggedIn.value) {
    showUnlockTip.value = true
    return
  }
  request.post(`/knowledge/articles/${article.id}/like`).then(res => {
    if (res) {
      article.like_count = (article.like_count || 0) + 1
      ElMessage.success('点赞成功')
    }
  })
}

// ==================== 搜索 ====================
function doSearch() {
  if (!searchQuery.value.trim()) return
  loading.value = true
  request.get('/knowledge/search', { params: { q: searchQuery.value } }).then(res => {
    if (Array.isArray(res)) searchResults.value = res
    else if (res && res.items) searchResults.value = res.items
    else searchResults.value = []
  }).finally(() => { loading.value = false })
}

function exitSearch() {
  searchResults.value = null
  searchQuery.value = ''
}

// ==================== 全屏阅读 ====================
function toggleReaderFullscreen() {
  readerFullscreen.value = !readerFullscreen.value
  document.body.classList.toggle('reader-fullscreen', readerFullscreen.value)
}

// ==================== 工具函数 ====================
function getVideoEmbedUrl(url) {
  if (!url) return ''
  if (url.includes('channels.weixin.qq.com')) return url
  const bv = url.match(/bilibili\.com\/video\/(BV\w+)/)
  if (bv) return `//player.bilibili.com/player.html?bvid=${bv[1]}`
  if (url.includes('douyin.com')) return url
  return ''
}

function resolveImg(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${VITE_API_BASE}${path.startsWith('/') ? '' : '/'}${path}`
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.logo {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-box {
  width: 280px;
}
.search-box :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.15);
  box-shadow: none;
  border: 1px solid rgba(255,255,255,0.2);
}
.search-box :deep(.el-input__inner) {
  color: #fff;
}
.search-box :deep(.el-input__inner::placeholder) {
  color: rgba(255,255,255,0.5);
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* 分类导航 */
.category-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
  justify-content: center;
}
.cat-nav-item {
  padding: 8px 20px;
  border-radius: 20px;
  background: #16161e;
  border: 1px solid #2a2a3a;
  color: #8c8c9c;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.cat-nav-item:hover {
  border-color: #8B5A2B;
  color: #e8d5c4;
}
.cat-nav-item.active {
  background: linear-gradient(135deg, #8B5A2B, #5c3a1e);
  border-color: #8B5A2B;
  color: #fff;
}
.cat-count {
  font-size: 12px;
  opacity: 0.7;
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}
.base-card {
  background: #16161e;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #2a2a3a;
  transition: all 0.3s;
  border-top: 3px solid var(--theme-color, #8B5A2B);
}
.base-card:hover {
  transform: translateY(-4px);
  border-color: var(--theme-color, #8B5A2B);
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
.base-info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.base-info h3 {
  margin: 0;
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
  display: flex;
  gap: 16px;
}

/* 详情页 */
.knowledge-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}
.detail-header {
  margin-bottom: 24px;
}
.detail-header h2 {
  margin: 16px 0 8px;
  font-size: 28px;
  color: #e8d5c4;
}
.detail-desc {
  font-size: 14px;
  color: #8c8c9c;
  margin: 0;
}
.view-switch {
  margin-bottom: 24px;
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
.tree-item-header.leaf:hover {
  background: #2a2a3a;
}
.item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.toggle-icon {
  color: #8B5A2B;
  font-size: 16px;
}
.item-name {
  font-size: 15px;
  color: #e8d5c4;
}
.item-count {
  font-size: 12px;
  color: #409EFF;
}
.item-views {
  font-size: 12px;
  color: #5c5c6c;
}

/* 文章列表 */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.article-item {
  display: flex;
  gap: 16px;
  background: #16161e;
  border: 1px solid #2a2a3a;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}
.article-item:hover {
  border-color: #8B5A2B;
  transform: translateX(4px);
}
.article-item-cover {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}
.article-item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.article-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.article-item-info h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #e8d5c4;
}
.article-item-info p {
  margin: 0 0 8px;
  font-size: 13px;
  color: #8c8c9c;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.article-item-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #6c6c7c;
}

/* 文章阅读页 */
.article-reader {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.reader-actions {
  display: flex;
  gap: 8px;
}
.reader-body {
  background: #16161e;
  border-radius: 12px;
  padding: 40px;
  border: 1px solid #2a2a3a;
}
.article-title {
  font-size: 28px;
  color: #e8d5c4;
  margin: 0 0 16px;
  line-height: 1.4;
}
.article-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #8c8c9c;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.article-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.article-tags :deep(.el-tag) {
  background: rgba(139, 90, 43, 0.2);
  border-color: rgba(139, 90, 43, 0.3);
  color: #c4956a;
}
.article-cover {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
}
.article-cover img {
  width: 100%;
  border-radius: 12px;
}
.article-content {
  line-height: 1.9;
  font-size: 16px;
  color: #e0e0e0;
}
.article-content :deep(p) {
  margin-bottom: 16px;
}
.article-content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 12px 0;
}
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  color: #e8d5c4;
  margin: 24px 0 12px;
}
.article-content :deep(pre) {
  background: #0a0a0f;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
.article-content :deep(blockquote) {
  border-left: 4px solid #8B5A2B;
  padding-left: 16px;
  margin: 12px 0;
  color: #a0a0b0;
}
.article-content :deep(a) {
  color: #c4956a;
}
.article-footer {
  margin-top: 40px;
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #2a2a3a;
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

/* 全屏阅读 */
:global(body.reader-fullscreen) .article-reader {
  max-width: none;
  padding: 0;
}
:global(body.reader-fullscreen) .reader-body {
  border-radius: 0;
  border: none;
  min-height: 100vh;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-inner {
    flex-direction: column;
    gap: 12px;
  }
  .search-box {
    width: 100%;
  }
  .base-grid {
    grid-template-columns: 1fr;
  }
  .reader-body {
    padding: 20px;
  }
  .article-title {
    font-size: 22px;
  }
}
</style>
