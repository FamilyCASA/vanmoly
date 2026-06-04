<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-grid">
        <div class="footer-brand">
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
          <p class="footer-desc">专注高端全屋定制，为您打造理想家居生活</p>
          <div class="footer-social">
            <a href="#" class="social-link" title="微信">
              <el-icon><ChatDotRound /></el-icon>
            </a>
            <a href="#" class="social-link" title="微博">
              <el-icon><Share /></el-icon>
            </a>
            <a href="#" class="social-link" title="小红书">
              <el-icon><Collection /></el-icon>
            </a>
          </div>
        </div>
        
        <div class="footer-links">
          <div class="footer-col">
            <h4>服务</h4>
            <router-link to="/book">预约量尺</router-link>
            <router-link to="/cases">案例展示</router-link>
            <router-link to="/products">产品中心</router-link>
          </div>
          <div class="footer-col">
            <h4>关于</h4>
            <router-link to="/">品牌故事</router-link>
            <router-link to="/">设计理念</router-link>
            <router-link to="/">联系我们</router-link>
          </div>
          <div class="footer-col">
            <h4>帝标总部</h4>
            <p>客服电话：400 6118 315</p>
            <p>地址：成都市新都区列维士路258号</p>
          </div>
          <div class="footer-col">
            <h4>设记家先锋店</h4>
            <p>服务热线：13881828767（贺女士）</p>
            <p>13219762086（曾女士）</p>
            <p>地址：成都市青羊区基准方中北区A座6-10</p>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2026 D&B 帝标|设记家 DESIGNARY. 蜀ICP备15030401号-3. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ChatDotRound, Share, Collection } from '@element-plus/icons-vue'
</script>

<style scoped>
.footer {
  padding: 80px 0 32px;
  background: var(--bg-base, #0a0a1a);
  color: var(--text-primary, #E8E8E8);
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 2fr;
  gap: 80px;
  margin-bottom: 64px;
}

.footer-brand .logo-mark {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.footer-brand .logo-icon {
  width: 40px;
  height: 40px;
  color: var(--text-title, #FFFFFF);
}

.footer-brand .logo-icon svg {
  width: 100%;
  height: 100%;
}

.footer-brand .logo-text {
  display: flex;
  flex-direction: column;
}

.footer-brand .brand-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-title, #FFFFFF);
  letter-spacing: 2px;
}

.footer-brand .brand-tag {
  font-size: 10px;
  color: var(--text-secondary, #A0A0B8);
  letter-spacing: 3px;
}

.footer-desc {
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
  margin-bottom: 24px;
  max-width: 280px;
  line-height: 1.6;
}

.footer-social {
  display: flex;
  gap: 12px;
}

.social-link {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary, #E8E8E8);
  font-size: 18px;
  transition: all 0.3s;
  text-decoration: none;
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-title, #FFFFFF);
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
}

.footer-col h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-title, #FFFFFF);
}

.footer-col a {
  display: block;
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
  text-decoration: none;
  margin-bottom: 12px;
  transition: color 0.3s;
}

.footer-col a:hover {
  color: var(--text-title, #FFFFFF);
}

.footer-col p {
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
  margin-bottom: 8px;
}

.footer-bottom {
  padding-top: 32px;
  border-top: 1px solid var(--border, #2a2a3e);
  text-align: center;
}

.footer-bottom p {
  font-size: 13px;
  color: var(--text-placeholder, #606080);
}

/* 响应式 */
@media (max-width: 992px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }
  
  .footer-links {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-col:nth-child(3),
  .footer-col:nth-child(4) {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 60px 0 24px;
  }
  
  .footer-container {
    padding: 0 20px;
  }
  
  .footer-links {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .footer-grid {
    margin-bottom: 48px;
  }
}
</style>
