# -*- coding: utf-8 -*-
"""重写header为深色导航栏版本"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === 替换整个nav区域 (line 13-209, index 12-208) ===
# 旧: line 13 <nav ...> 到 line 209 </div> (mobile-menu关闭)
# 新: 深色导航栏

new_nav = '''    <nav class="navbar" :class="{ 'scrolled': scrolled }">

      <div class="nav-container">

        <div class="nav-brand" @click="scrollToTop">

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

          <a href="#" class="nav-link" @click.prevent="scrollToTop">首页</a>

          <a href="#services" class="nav-link">全案服务</a>

          <a href="#process" class="nav-link">全案流程</a>

          <a href="#cases" class="nav-link">精选案例</a>

          <a href="#about" class="nav-link">关于设记家</a>

          <a href="#brands" class="nav-link">合作品牌</a>

          <a href="#contact" class="nav-link">联系我们</a>

        </div>

        <div class="nav-actions">

          <router-link to="/service-center" class="btn-nav">服务中心</router-link>

          <router-link to="/cart" class="btn-nav">购物中心</router-link>

          <router-link to="/products" class="btn-nav">产品中心</router-link>

        </div>

        <button class="menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen">

          <span :class="{ 'open': mobileMenuOpen }"></span>

        </button>

      </div>

      <div class="mobile-menu" :class="{ 'open': mobileMenuOpen }">

        <a href="#" @click.prevent="scrollToTop; mobileMenuOpen = false">首页</a>

        <a href="#services" @click="mobileMenuOpen = false">全案服务</a>

        <a href="#process" @click="mobileMenuOpen = false">全案流程</a>

        <a href="#cases" @click="mobileMenuOpen = false">精选案例</a>

        <a href="#about" @click="mobileMenuOpen = false">关于设记家</a>

        <a href="#contact" @click="mobileMenuOpen = false">联系我们</a>

        <router-link to="/products" @click="mobileMenuOpen = false">产品中心</router-link>

      </div>

    </nav>


'''

# 替换 index 12 到 208 (line 13 到 209)
lines = lines[:12] + [new_nav] + lines[209:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'[OK] Header已替换为深色导航栏')
print(f'   旧: line 13-209 ({len(lines)-len(new_nav)-(12)+209} 行)')
print(f'   新: 深色主题 + 完整导航')
print('[DONE]')