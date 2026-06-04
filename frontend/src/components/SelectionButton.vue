<template>
  <div 
    class="selection-button-wrapper"
    :class="{ 
      'has-items': totalCount > 0,
      'is-animating': isSwallowing,
      'is-pulsing': shouldPulse
    }"
  >
    <!-- 主按钮 -->
    <div 
      class="selection-button"
      @click="handleClick"
      @mouseenter="isHovered = true"
      @mouseleave="isHovered = false"
    >
      <!-- 背景光晕 -->
      <div class="button-glow" v-if="totalCount > 0"></div>
      
      <!-- 按钮主体 -->
      <div class="button-content">
        <!-- 乐高积木图标 -->
        <div class="lego-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 乐高积木主体 -->
            <rect x="3" y="8" width="18" height="12" rx="2" fill="currentColor" opacity="0.9"/>
            <!-- 凸粒（上面4个圆点） -->
            <circle cx="7" cy="5" r="2.5" fill="currentColor"/>
            <circle cx="12" cy="5" r="2.5" fill="currentColor"/>
            <circle cx="17" cy="5" r="2.5" fill="currentColor"/>
            <!-- 底部阴影线 -->
            <rect x="5" y="11" width="14" height="1.5" rx="0.75" fill="currentColor" opacity="0.3"/>
          </svg>
          
          <!-- 吞咽动画元素 -->
          <div class="swallow-effect" v-if="isSwallowing">
            <div class="swallow-particle" v-for="i in 6" :key="i" :style="getParticleStyle(i)"></div>
          </div>
        </div>
        
        <!-- 文字 -->
        <span class="button-text">我的选品单</span>
        
        <!-- 数量徽章 -->
        <transition name="badge-pop">
          <div v-if="totalCount > 0" class="count-badge" :key="badgeKey">
            <span class="count-number">{{ displayCount }}</span>
            <span class="count-plus" v-if="justAdded">+</span>
          </div>
        </transition>
      </div>
      
      <!-- 呼吸光效 -->
      <div class="pulse-ring" v-if="shouldPulse && !isHovered"></div>
      <div class="pulse-ring delay-1" v-if="shouldPulse && !isHovered"></div>
      <div class="pulse-ring delay-2" v-if="shouldPulse && !isHovered"></div>
    </div>
    
    <!-- 悬浮提示 -->
    <transition name="tooltip-fade">
      <div v-if="isHovered && totalCount > 0" class="selection-tooltip">
        <div class="tooltip-header">
          <span>选品清单</span>
          <span class="tooltip-total">¥{{ formatPrice(totalPrice) }}</span>
        </div>
        <div class="tooltip-preview" v-if="recentItems.length > 0">
          <div 
            v-for="item in recentItems" 
            :key="item.id"
            class="tooltip-item"
          >
            <img v-if="item.image" :src="item.image" :alt="item.name">
            <div v-else class="no-image"></div>
            <span class="item-name">{{ item.name }}</span>
            <span class="item-qty">x{{ item.quantity }}</span>
          </div>
        </div>
        <div class="tooltip-footer">
          点击查看完整清单 →
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnonymousSelection, onSwallow } from '@/composables/useAnonymousSelection'

const router = useRouter()
const { items, totalCount, totalPrice } = useAnonymousSelection()

// 状态
const isHovered = ref(false)
const isSwallowing = ref(false)
const justAdded = ref(false)
const badgeKey = ref(0)
const previousCount = ref(0)
const displayCount = ref(0)

// 是否显示呼吸动画
const shouldPulse = computed(() => {
  return totalCount.value > 0 && !isHovered.value && !isSwallowing.value
})

// 最近添加的3个物品（用于tooltip预览）
const recentItems = computed(() => {
  return items.value.slice(-3).reverse()
})

// 格式化价格
const formatPrice = (price) => {
  return price?.toLocaleString('zh-CN') || '0'
}

// 粒子动画样式
const getParticleStyle = (index) => {
  const angle = (index - 1) * 60
  const delay = (index - 1) * 0.05
  return {
    transform: `rotate(${angle}deg) translateY(-20px)`,
    animationDelay: `${delay}s`
  }
}

// 点击处理
const handleClick = () => {
  // 检查客户登录状态
  const customerToken = localStorage.getItem('customer_token')
  if (!customerToken) {
    // 未注册，跳转到客户注册页，并带上来源页面
    router.push('/register?redirect=' + encodeURIComponent('/selection-center'))
  } else {
    router.push('/selection-center')
  }
}

// 监听数量变化（仅处理减少的情况，增加由吞咽事件处理）
watch(totalCount, (newCount, oldCount) => {
  if (newCount < oldCount) {
    // 数量减少时直接更新
    displayCount.value = newCount
  }
  previousCount.value = newCount
}, { immediate: true })

// 数字滚动动画
const animateNumber = (from, to) => {
  const duration = 400
  const startTime = performance.now()
  
  const update = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // 缓动函数
    const easeOut = 1 - Math.pow(1 - progress, 3)
    displayCount.value = Math.round(from + (to - from) * easeOut)
    
    if (progress < 1) {
      requestAnimationFrame(update)
    }
  }
  
  requestAnimationFrame(update)
}

onMounted(() => {
  displayCount.value = totalCount.value
  previousCount.value = totalCount.value
  
  // 监听吞咽事件
  const unsubscribe = onSwallow(() => {
    triggerSwallowAnimation()
  })
  
  onUnmounted(() => {
    unsubscribe()
  })
})

// 触发吞咽动画
const triggerSwallowAnimation = () => {
  isSwallowing.value = true
  justAdded.value = true
  badgeKey.value++
  
  // 数字滚动
  const newCount = totalCount.value
  animateNumber(displayCount.value, newCount)
  
  setTimeout(() => {
    isSwallowing.value = false
  }, 600)
  
  setTimeout(() => {
    justAdded.value = false
  }, 1500)
}
</script>

<style scoped>
.selection-button-wrapper {
  position: relative;
  display: inline-block;
}

/* 主按钮 */
.selection-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(26, 26, 46, 0.9);
  border: 1px solid #3a3a4e;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: visible;
}

.selection-button:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

/* 有物品时的样式 */
.has-items .selection-button {
  background: linear-gradient(135deg, #409EFF 0%, #6C63FF 100%);
  border-color: transparent;
  color: #fff;
}

.has-items .selection-button:hover {
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.3);
}

/* 背景光晕 */
.button-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, #409EFF 0%, #6C63FF 50%, #409EFF 100%);
  border-radius: 26px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.02); }
}

/* 按钮内容 */
.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

/* 乐高积木图标 */
.lego-icon {
  position: relative;
  width: 20px;
  height: 20px;
}

.lego-icon svg {
  width: 100%;
  height: 100%;
}

/* 吞咽动画 */
.swallow-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  pointer-events: none;
}

.swallow-particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #FFD700;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  margin: -3px 0 0 -3px;
  animation: swallow-in 0.6s ease-out forwards;
}

@keyframes swallow-in {
  0% {
    transform: rotate(var(--rotation, 0deg)) translateY(-20px) scale(1);
    opacity: 1;
  }
  50% {
    transform: rotate(var(--rotation, 0deg)) translateY(-10px) scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: rotate(var(--rotation, 0deg)) translateY(0) scale(0);
    opacity: 0;
  }
}

/* 按钮文字 */
.button-text {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  color: #E8E8E8;
}

/* 数量徽章 */
.count-badge {
  position: relative;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #0a0a1a;
  color: #409EFF;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.has-items .count-badge {
  background: #FFD700;
  color: #0a0a1a;
}

.count-plus {
  position: absolute;
  top: -8px;
  right: -4px;
  font-size: 10px;
  color: #52c41a;
  animation: plus-bounce 0.5s ease-out;
}

@keyframes plus-bounce {
  0% { transform: scale(0) translateY(10px); opacity: 0; }
  50% { transform: scale(1.3) translateY(-5px); opacity: 1; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* 徽章弹出动画 */
.badge-pop-enter-active {
  animation: badge-pop-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.badge-pop-leave-active {
  animation: badge-pop-out 0.3s ease-in;
}

@keyframes badge-pop-in {
  0% { transform: scale(0); opacity: 0; }
  70% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes badge-pop-out {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0); opacity: 0; }
}

/* 呼吸光环 */
.pulse-ring {
  position: absolute;
  inset: -4px;
  border: 2px solid #409EFF;
  border-radius: 28px;
  opacity: 0;
  animation: pulse-ring 2s ease-out infinite;
}

.pulse-ring.delay-1 {
  animation-delay: 0.4s;
}

.pulse-ring.delay-2 {
  animation-delay: 0.8s;
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

/* 悬浮提示 */
.selection-tooltip {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 280px;
  background: #1a1a2e;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  border: 1px solid #2a2a3e;
  padding: 16px;
  z-index: 1000;
  animation: tooltip-in 0.3s ease-out;
}

.selection-tooltip::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 40px;
  width: 12px;
  height: 12px;
  background: #1a1a2e;
  transform: rotate(45deg);
  border-radius: 2px;
}

@keyframes tooltip-in {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.3s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2a2a3e;
  font-weight: 500;
}

.tooltip-total {
  color: #f56c6c;
  font-weight: 600;
}

.tooltip-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.tooltip-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: #0a0a1a;
  border-radius: 8px;
}

.tooltip-item img,
.tooltip-item .no-image {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
  background: #e8e8e8;
}

.tooltip-item .item-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tooltip-item .item-qty {
  font-size: 12px;
  color: #A0A0B8;
}

.tooltip-footer {
  text-align: center;
  font-size: 13px;
  color: #409EFF;
  padding-top: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .button-text {
    display: none;
  }
  
  .selection-button {
    padding: 10px;
  }
  
  .selection-tooltip {
    width: 260px;
    right: -60px;
  }
}
</style>
