<template>
  <nav class="navbar" :class="{ 'scrolled': scrolled, 'transparent': isHome && !scrolled }">
    <div class="nav-container">
      <div class="nav-brand" @click="goHome">
        <div class="logo-mark">
          <span class="logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <rect x="4" y="12" width="14" height="20" rx="2" fill="currentColor" opacity="0.9"/>
              <rect x="22" y="8" width="14" height="24" rx="2" fill="currentColor" opacity="0.6"/>
            </svg>
          </span>
          <div class="logo-text">
            <span class="brand-name">D&B 帝标|设记家</span>
            <span class="brand-tag">DESIGNARY</span>
          </div>
        </div>
      </div>
      
      <div class="nav-menu">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">首页</router-link>
        <router-link to="/cases" class="nav-link" :class="{ active: $route.path.startsWith('/cases') }">案例</router-link>
        <router-link to="/products" class="nav-link" :class="{ active: $route.path.startsWith('/products') }">产品</router-link>
        <router-link to="/book" class="nav-link" :class="{ active: $route.path === '/book' }">预约</router-link>
      </div>
      
      <div class="nav-actions">
        <SelectionButton />
      </div>
      
      <!-- 移动端菜单按钮 -->
      <button class="menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
        <span :class="{ 'open': mobileMenuOpen }"></span>
      </button>
    </div>
    
    <!-- 移动端菜单 -->
    <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">
      <router-link to="/" @click="mobileMenuOpen = false">首页</router-link>
      <router-link to="/cases" @click="mobileMenuOpen = false">案例</router-link>
      <router-link to="/products" @click="mobileMenuOpen = false">产品</router-link>
      <a href="javascript:void(0)" @click="goToSelection">我的选品</a>
      <router-link to="/book" @click="mobileMenuOpen = false">预约量尺</router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import SelectionButton from '@/components/SelectionButton.vue'

const route = useRoute()
const router = useRouter()
const scrolled = ref(false)
const mobileMenuOpen = ref(false)

const isHome = computed(() => route.path === '/')

const handleScroll = () => {
  scrolled.value = window.scrollY > 50
}

const goHome = () => {
  router.push('/')
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
  background: #fff;
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}

.navbar.transparent {
  background: transparent;
  box-shadow: none;
}

.navbar.scrolled {
  background: #fff;
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
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
}

.logo-icon {
  width: 40px;
  height: 40px;
  color: #1a1a1a;
}

.navbar.transparent .logo-icon {
  color: #fff;
}

.navbar.scrolled .logo-icon {
  color: #1a1a1a;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 2px;
}

.navbar.transparent .brand-name {
  color: #fff;
}

.navbar.scrolled .brand-name {
  color: #1a1a1a;
}

.brand-tag {
  font-size: 10px;
  color: #999;
  letter-spacing: 3px;
}

.navbar.transparent .brand-tag {
  color: rgba(255,255,255,0.7);
}

.navbar.scrolled .brand-tag {
  color: #999;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 40px;
}

.nav-link {
  font-size: 15px;
  color: #666;
  text-decoration: none;
  transition: color 0.3s;
  position: relative;
}

.navbar.transparent .nav-link {
  color: rgba(255,255,255,0.8);
}

.navbar.scrolled .nav-link {
  color: #666;
}

.nav-link:hover,
.nav-link.active {
  color: #1a1a1a;
}

.navbar.transparent .nav-link:hover,
.navbar.transparent .nav-link.active {
  color: #fff;
}

.navbar.scrolled .nav-link:hover,
.navbar.scrolled .nav-link.active {
  color: #1a1a1a;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: currentColor;
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

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #1a1a1a;
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #333;
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
  background: #1a1a1a;
  position: absolute;
  left: 4px;
  transition: all 0.3s;
}

.navbar.transparent .menu-toggle span {
  background: #fff;
}

.navbar.scrolled .menu-toggle span {
  background: #1a1a1a;
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
  background: #1a1a1a;
}

.menu-toggle span.open::after {
  transform: rotate(-45deg);
  top: 0;
  background: #1a1a1a;
}

/* 移动端菜单 */
.mobile-menu {
  display: none;
  position: absolute;
  top: 80px;
  left: 0;
  right: 0;
  background: #fff;
  flex-direction: column;
  padding: 24px;
  gap: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
  color: #333;
  text-decoration: none;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
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
