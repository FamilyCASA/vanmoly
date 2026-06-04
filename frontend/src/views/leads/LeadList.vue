<template>
  <div class="lead-list-page">
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-text">D&B 帝标|设记家</router-link>
      </div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/cases">案例展示</router-link>
        <router-link to="/book">预约量尺</router-link>
      </div>
    </nav>

    <div class="page-content">
      <div class="container">
        <h1>我的线索</h1>
        <p>功能开发中，敬请期待...</p>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 D&B 帝标|设记家全案落地服务系统 DEMO V.0.1</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.lead-list-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5%;
  height: 64px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.nav-brand .brand-text {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: #666;
  text-decoration: none;
  font-size: 15px;
}

.page-content {
  padding: 60px 5%;
  text-align: center;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.footer {
  background: #333;
  color: #999;
  padding: 24px 5%;
  text-align: center;
}
</style>
