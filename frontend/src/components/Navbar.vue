<template>
  <nav class="navbar" :class="{ 'scrolled': scrolled, 'transparent': isTransparent && !scrolled, 'scroll-away': props.stickyHide }">
    <div class="nav-container">
      <div class="nav-brand" @click="goHome">
        <div class="logo-mark">
          <span class="logo-icon">
            <img src="/images/logo.png" alt="帝标" style="height: 36px; width: auto; object-fit: contain;" />
          </span>
          <div class="logo-text">
            <span class="brand-divider">|</span>
            <span class="brand-name">设记家</span>
          </div>
        </div>
      </div>
      
      <div class="nav-menu">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' && !$route.hash }">首页</router-link>
        <a href="/#services" class="nav-link">全案服务</a>
        <a href="/#process" class="nav-link">全案流程</a>
        <a href="/#cases" class="nav-link">精选案例</a>
        <a href="/#about" class="nav-link">关于设记家</a>
        <a href="/#partner" class="nav-link">合作品牌</a>
        <a href="/#contact" class="nav-link">联系我们</a>
        <router-link to="/book" class="nav-link" :class="{ active: $route.path === '/book' }">预约中心</router-link>
        <router-link to="/cases" class="nav-link" :class="{ active: $route.path.startsWith('/cases') }">案例中心</router-link>
        <router-link to="/proposals" class="nav-link" :class="{ active: $route.path.startsWith('/proposals') || $route.path.startsWith('/slides') }">提案中心</router-link>
        <router-link to="/products" class="nav-link" :class="{ active: $route.path.startsWith('/products') }">产品中心</router-link>
        <button class="nav-link nav-link-button" :class="{ active: $route.path === '/user-center' }" @click="goToUserCenter">
          用户中心
        </button>
      </div>
      
      <!-- 移动端菜单按钮 -->
      <button class="menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
        <span :class="{ 'open': mobileMenuOpen }"></span>
      </button>
    </div>
    
    <!-- 移动端菜单 -->
    <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">
      <router-link to="/" @click="mobileMenuOpen = false">首页</router-link>
      <a href="/#services" @click="mobileMenuOpen = false">全案服务</a>
      <a href="/#process" @click="mobileMenuOpen = false">全案流程</a>
      <a href="/#cases" @click="mobileMenuOpen = false">精选案例</a>
      <a href="/#about" @click="mobileMenuOpen = false">关于设记家</a>
      <a href="/#partner" @click="mobileMenuOpen = false">合作品牌</a>
      <a href="/#contact" @click="mobileMenuOpen = false">联系我们</a>
      <router-link to="/book" @click="mobileMenuOpen = false">预约中心</router-link>
      <router-link to="/cases" @click="mobileMenuOpen = false">案例中心</router-link>
      <router-link to="/proposals" @click="mobileMenuOpen = false">提案中心</router-link>
      <router-link to="/products" @click="mobileMenuOpen = false">产品中心</router-link>
      <button class="mobile-link-button" @click="goToUserCenter">用户中心</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const scrolled = ref(false)
const mobileMenuOpen = ref(false)

const props = defineProps({
  // 沉浸式选品模式：筛选栏锁定时 Navbar 也跟随页面滚走
  stickyHide: {
    type: Boolean,
    default: false
  }
})

const isTransparent = computed(() => route.meta.hasHero === true)

const handleScroll = () => {
  // Hero section is min-height: 100vh - transparent until scrolled past hero
  scrolled.value = window.scrollY > (window.innerHeight > 0 ? window.innerHeight : 900)
}

const goHome = () => {
  router.push('/')
}

const goToUserCenter = () => {
  mobileMenuOpen.value = false
  if (localStorage.getItem('token')) {
    router.push({ path: '/admin/my-workspace', query: { openMine: '1' } })
    return
  }
  router.push('/user-center')
}

// 跳转到选品中心（检查登录状态，已注册可直达，未注册引导注册）
const goToSelection = () => {
  mobileMenuOpen.value = false
  const customerToken = localStorage.getItem('customer_token')
  if (!customerToken) {
    router.push('/register?redirect=' + encodeURIComponent('/selection-center'))
  } else {
    router.push('/selection-center')
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.3s ease;
  background: var(--bg-surface, #1a1a2e);
  box-shadow: var(--shadow, 0 2px 20px rgba(0,0,0,0.6));
}

.navbar.transparent {
  background: transparent;
  box-shadow: none;
}

.navbar.scrolled {
  background: var(--bg-elevated, #111111);
  box-shadow: var(--shadow, 0 2px 20px rgba(0,0,0,0.8));
}

/* 沉浸式选品：筛选栏锁定时，Navbar 跟随页面滚走 */
.navbar.scroll-away {
  transition: transform 0.4s ease, opacity 0.4s ease;
  transform: translateY(-100%);
  opacity: 0;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  cursor: pointer;
}

.logo-mark {
  display: flex;
  align-items: center;
  gap: 12px;

  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  padding: 4px 14px 4px 8px;}

/* white/scrolled background */
.navbar.scrolled .logo-mark,
.navbar:not(.transparent) .logo-mark {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.logo-icon {
  display: flex;
  align-items: center;
}

.logo-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  padding: 4px 12px 4px 8px;
  border-radius: 4px;
  gap: 8px;
}



.brand-divider {
  color: rgba(255, 255, 255, 0.4);
  font-size: 18px;
  font-weight: 300;
}
.brand-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-title, #FFFFFF);
  letter-spacing: 2px;
  line-height: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
}

/* brand text stays white in all states */

.brand-tag {
  font-size: 10px;
  color: var(--text-secondary, #A0A0B8);
  letter-spacing: 3px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 40px;
}

.nav-link {
  font-size: 15px;
  color: var(--text-secondary, #A0A0B8);
  text-decoration: none;
  transition: color 0.3s;
  position: relative;
}

.nav-link-button {
  border: 1px solid rgba(64, 158, 255, 0.35);
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  padding: 8px 14px;
  font-family: inherit;
}

.nav-link-button::after {
  display: none;
}

.nav-link-button:hover,
.nav-link-button.active {
  color: #fff;
  background: rgba(64, 158, 255, 0.28);
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-title, #FFFFFF);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--primary, #409EFF);
  transition: width 0.3s;
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: rgba(30, 28, 26, 0.08);
  color: var(--text-primary, #E8E8E8);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary, #409EFF);
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: var(--primary-dark, #2a6cb0);
  transform: translateY(-2px);
}

/* 移动端菜单按钮 */
.menu-toggle {
  display: none;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
}

.menu-toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--text-primary, #E8E8E8);
  position: absolute;
  left: 4px;
  transition: all 0.3s;
}

.menu-toggle span::before,
.menu-toggle span::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background: inherit;
  left: 0;
  transition: all 0.3s;
}

.menu-toggle span::before {
  top: -7px;
}

.menu-toggle span::after {
  top: 7px;
}

.menu-toggle span.open {
  background: transparent;
}

.menu-toggle span.open::before {
  transform: rotate(45deg);
  top: 0;
  background: var(--text-primary, #E8E8E8);
}

.menu-toggle span.open::after {
  transform: rotate(-45deg);
  top: 0;
  background: var(--text-primary, #E8E8E8);
}

/* 移动端菜单 */
.mobile-menu {
  display: none;
  position: absolute;
  top: 80px;
  left: 0;
  right: 0;
  background: var(--bg-surface, #1a1a2e);
  flex-direction: column;
  padding: 24px;
  gap: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
  transform: translateY(-100%);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}

.mobile-menu.open {
  transform: translateY(0);
  opacity: 1;
  visibility: visible;
}

.mobile-menu a {
  font-size: 16px;
  color: var(--text-primary, #E8E8E8);
  text-decoration: none;
  padding: 12px 0;
  border-bottom: 1px solid var(--border, #2a2a3e);
}

.mobile-link-button {
  width: 100%;
  text-align: left;
  border: 0;
  border-bottom: 1px solid var(--border, #2a2a3e);
  background: transparent;
  color: var(--text-primary, #E8E8E8);
  font: inherit;
  font-size: 16px;
  padding: 12px 0;
  cursor: pointer;
}

.mobile-menu .btn-primary {
  margin-top: 8px;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 992px) {
  .nav-menu,
  .nav-actions {
    display: none;
  }
  
  .menu-toggle {
    display: block;
  }
  
  .mobile-menu {
    display: flex;
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 20px;
    height: 64px;
  }
  
  .mobile-menu {
    top: 64px;
  }
}
</style>
