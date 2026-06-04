<template>
  <router-view />
</template>

<script setup>
// 根组件 - 暗黑深空主题已通过 main.js 初始化
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary, #E8E8E8);
  background-color: var(--bg-base, #0a0a1a);
}

#app {
  min-height: 100vh;
}
</style>