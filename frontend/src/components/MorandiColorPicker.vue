<template>
  <div class="morandi-picker">
    <!-- 4个色点触发按钮 -->
    <div class="color-dots">
      <div class="color-dot-item" v-for="(slot, slotKey) in slots" :key="slotKey">
        <span class="slot-label">{{ slot.label }}</span>
        <div class="color-dot-wrapper">
          <div
            v-if="modelValue[slotKey]"
            class="color-swatch"
            :style="{ background: modelValue[slotKey].hex }"
            @click="openPicker(slotKey)"
          >
            <span class="swatch-name">{{ modelValue[slotKey].name || '' }}</span>
          </div>
          <div v-else class="color-dot-empty" @click="openPicker(slotKey)">+</div>
          <el-button
            v-if="modelValue[slotKey]"
            size="small"
            circle
            type="danger"
            class="clear-btn"
            @click.stop="clearColor(slotKey)"
          >x</el-button>
        </div>
      </div>
    </div>

    <!-- 色卡弹窗 -->
    <el-dialog
      :title="slots[activeSlot].label + ' - 选择配色'"
      v-model="dialogVisible"
      width="760px"
      :append-to-body="true"
    >
      <!-- 搜索栏：支持色号/潘通/HEX搜索 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索色名、潘通号或 #HEX"
          clearable
          prefix-icon="Search"
          size="default"
          style="max-width: 300px"
        />
      </div>

      <!-- 色系列表 -->
      <div class="palette-groups">
        <div
          v-for="group in filteredPaletteData"
          :key="group.key"
          class="palette-group"
        >
          <div class="group-header">
            <span class="group-dot" :style="{ background: group.colors[0]?.hex_value || '#ccc' }"></span>
            <span class="group-name">{{ group.name }}</span>
            <span class="group-count">{{ group.colors.length }}色</span>
          </div>
          <div class="color-grid">
            <div
              v-for="color in group.colors"
              :key="color.id"
              class="color-tile"
              :class="{ selected: color.hex_value === modelValue[activeSlot]?.hex }"
              :style="{ background: color.hex_value }"
              :title="color.name_cn + ' / ' + color.pantone_code"
              @click="selectColor(activeSlot, { hex: color.hex_value, name: color.name_cn, pantone: color.pantone_code, group: group.key })"
            >
              <span v-if="color.hex_value === modelValue[activeSlot]?.hex" class="check-mark">&#10003;</span>
              <span class="tile-name">{{ color.name_cn }}</span>
            </div>
          </div>
        </div>
        <div v-if="filteredPaletteData.length === 0" class="no-results">
          无匹配颜色，请尝试其他关键词
        </div>
      </div>

      <!-- 手动输入 HEX / 潘通号 -->
      <div class="manual-input">
        <el-divider>手动输入</el-divider>
        <div class="input-row">
          <el-input
            v-model="manualHex"
            placeholder="#RRGGBB"
            size="default"
            style="width: 140px"
            @change="applyManualHex"
          >
            <template #prefix>
              <div class="hex-preview" :style="{ background: manualHex }"></div>
            </template>
          </el-input>
          <el-input
            v-model="manualPantone"
            placeholder="Pantone 色号"
            size="default"
            style="width: 180px"
            @change="lookupPantone"
          >
            <template #prefix>
              <span style="font-size:12px;color:#999">PANTONE</span>
            </template>
          </el-input>
          <el-button type="primary" size="default" @click="applyManualInput" :disabled="!manualHex">
            应用
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import request from '@/utils/request'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      main: null,
      auxiliary: null,
      accent: null,
      background: null
    })
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const activeSlot = ref('main')
const paletteData = ref([])
const searchQuery = ref('')
const manualHex = ref('')
const manualPantone = ref('')

const slots = {
  main: { label: '主色' },
  auxiliary: { label: '辅助色' },
  accent: { label: '点缀色' },
  background: { label: '背景色' }
}

// 过滤色卡
const filteredPaletteData = computed(() => {
  if (!searchQuery.value) return paletteData.value
  const q = searchQuery.value.toLowerCase().trim()
  return paletteData.value
    .map(group => {
      const filtered = group.colors.filter(c =>
        (c.name_cn && c.name_cn.includes(q)) ||
        (c.pantone_code && c.pantone_code.toLowerCase().includes(q)) ||
        (c.hex_value && c.hex_value.toLowerCase().includes(q))
      )
      if (filtered.length === 0) return null
      return { ...group, colors: filtered }
    })
    .filter(Boolean)
})

const openPicker = (slotKey) => {
  activeSlot.value = slotKey
  searchQuery.value = ''
  manualHex.value = props.modelValue[slotKey]?.hex || ''
  manualPantone.value = props.modelValue[slotKey]?.pantone || ''
  dialogVisible.value = true
}

const clearColor = (slotKey) => {
  const updated = { ...props.modelValue, [slotKey]: null }
  emit('update:modelValue', updated)
}

const selectColor = (slotKey, colorData) => {
  const updated = { ...props.modelValue, [slotKey]: colorData }
  emit('update:modelValue', updated)
  manualHex.value = colorData.hex
  manualPantone.value = colorData.pantone || ''
}

// 手动输入HEX
const applyManualHex = () => {
  let hex = manualHex.value.trim()
  if (!hex.startsWith('#')) hex = '#' + hex
  if (!/^#[0-9A-Fa-f]{6}$/.test(hex)) return
  const updated = {
    ...props.modelValue,
    [activeSlot.value]: {
      hex: hex,
      name: manualPantone.value || hex,
      pantone: manualPantone.value || '',
      group: 'custom'
    }
  }
  emit('update:modelValue', updated)
}

// 查询潘通色映射
const lookupPantone = async () => {
  const code = manualPantone.value.trim()
  if (!code) return
  try {
    const res = await request.get('/pantone-lookup', { params: { code } })
    const data = res.data || res
    if (data && data.hex_value) {
      manualHex.value = data.hex_value
    }
  } catch (e) {
    // 潘通查询失败不影响使用
    console.warn('Pantone lookup failed:', e)
  }
}

// 应用手动输入
const applyManualInput = () => {
  applyManualHex()
}

// 加载色卡数据
const loadPalette = async () => {
  try {
    const res = await request.get('/morandi-palette')
    const data = res.data || res || []
    paletteData.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('loadPalette error:', e)
    paletteData.value = []
  }
}

onMounted(() => {
  loadPalette()
})
</script>

<style scoped>
.color-dots {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.color-dot-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.slot-label {
  font-size: 12px;
  color: #888;
  letter-spacing: 1px;
}
.color-dot-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
}
.color-swatch {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #ddd, 0 2px 6px rgba(0,0,0,0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s;
}
.color-swatch:hover {
  transform: scale(1.1);
}
.swatch-name {
  font-size: 9px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  max-width: 30px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.color-dot-empty {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px dashed #ccc;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 20px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.color-dot-empty:hover {
  border-color: #8B5A2B;
}
.clear-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  padding: 0;
  font-size: 10px;
  min-height: 0 !important;
  line-height: 18px;
}

/* Dialog */
.search-bar {
  margin-bottom: 16px;
}
.palette-groups {
  max-height: 400px;
  overflow-y: auto;
}
.palette-group {
  margin-bottom: 20px;
}
.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.group-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.1);
}
.group-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}
.group-count {
  font-size: 11px;
  color: #999;
}
.color-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.color-tile {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s, border-color 0.2s;
  position: relative;
}
.color-tile:hover {
  transform: scale(1.12);
  border-color: #333;
  z-index: 1;
}
.color-tile.selected {
  border-color: #333;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px #333;
}
.check-mark {
  color: #fff;
  font-size: 20px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}
.tile-name {
  font-size: 8px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  margin-top: 2px;
  max-width: 44px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.no-results {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}

/* Manual Input */
.manual-input {
  margin-top: 16px;
}
.input-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.hex-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
}
</style>