<template>
  <div class="default-image" :style="{ width: size + 'px', height: height || size + 'px' }">
    <el-icon :size="iconSize"><Picture /></el-icon>
    <span v-if="text" class="text">{{ text }}</span>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: Number,
    default: 200
  },
  height: {
    type: Number,
    default: null
  },
  text: {
    type: String,
    default: ''
  }
})

const iconSize = computed(() => Math.min(props.size, props.height || props.size) * 0.3)
</script>

<style scoped>
.default-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  color: #c0c4cc;
}

.text {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
