<template>
  <div class="navigation-editor">
    <div class="editor-header">
      <h4>{{ position === 'header' ? '顶部导航' : '底部导航' }}</h4>
      <el-button type="primary" @click="save">
        <el-icon><Check /></el-icon> 保存配置
      </el-button>
    </div>

    <div class="editor-content">
      <!-- 样式配置 -->
      <div class="style-config" v-if="position === 'header'">
        <h5>样式设置</h5>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="背景色">
              <el-color-picker v-model="form.style_config.bg_color" show-alpha />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="文字色">
              <el-color-picker v-model="form.style_config.text_color" show-alpha />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="激活色">
              <el-color-picker v-model="form.style_config.active_color" show-alpha />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 导航项列表 -->
      <div class="nav-items">
        <div class="items-header">
          <h5>导航项</h5>
          <el-button link type="primary" @click="addItem">
            <el-icon><Plus /></el-icon> 添加导航项
          </el-button>
        </div>

        <draggable 
          v-model="form.nav_items" 
          item-key="id"
          handle=".drag-handle"
          class="nav-list"
        >
          <template #item="{ element, index }">
            <div class="nav-item">
              <div class="item-main">
                <el-icon class="drag-handle"><Rank /></el-icon>
                
                <div class="item-fields">
                  <el-input 
                    v-model="element.label" 
                    placeholder="显示文字"
                    class="field-label"
                  />
                  <el-input 
                    v-model="element.link" 
                    placeholder="链接地址"
                    class="field-link"
                  />
                  <el-select v-model="element.type" class="field-type">
                    <el-option label="链接" value="link" />
                    <el-option label="按钮" value="button" />
                    <el-option label="下拉菜单" value="dropdown" />
                  </el-select>
                </div>

                <el-icon class="delete-btn" @click="removeItem(index)">
                  <Delete />
                </el-icon>
              </div>

              <!-- 下拉菜单子项 -->
              <div v-if="element.type === 'dropdown'" class="dropdown-items">
                <div 
                  v-for="(sub, subIndex) in element.items" 
                  :key="subIndex"
                  class="dropdown-item"
                >
                  <el-input v-model="sub.label" placeholder="子项文字" size="small" />
                  <el-input v-model="sub.link" placeholder="子项链接" size="small" />
                  <el-icon @click="removeSubItem(element, subIndex)"><Close /></el-icon>
                </div>
                <el-button link type="primary" size="small" @click="addSubItem(element)">
                  <el-icon><Plus /></el-icon> 添加子项
                </el-button>
              </div>
            </div>
          </template>
        </draggable>
      </div>
    </div>

    <!-- 预览 -->
    <div class="preview-section">
      <h5>预览</h5>
      <div 
        class="nav-preview"
        :class="position"
        :style="previewStyle"
      >
        <template v-for="item in form.nav_items" :key="item.id">
          <a 
            v-if="item.type === 'link'"
            :href="item.link"
            class="nav-link"
          >{{ item.label }}</a>
          
          <button 
            v-else-if="item.type === 'button'"
            class="nav-btn"
          >{{ item.label }}</button>
          
          <div v-else-if="item.type === 'dropdown'" class="nav-dropdown">
            <span>{{ item.label }}</span>
            <div class="dropdown-menu">
              <a v-for="sub in item.items" :key="sub.link" :href="sub.link">
                {{ sub.label }}
              </a>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Plus, Delete, Rank, Check, Close } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

const props = defineProps({
  position: {
    type: String,
    required: true
  },
  config: {
    type: Object,
    default: () => null
  }
})

const emit = defineEmits(['save'])

const form = reactive({
  nav_position: props.position,
  nav_items: [],
  style_config: {
    bg_color: 'transparent',
    text_color: '#FFFFFF',
    active_color: '#C4A77D'
  }
})

// 从父组件同步配置
watch(() => props.config, (newConfig) => {
  if (newConfig) {
    form.nav_items = newConfig.nav_items || []
    form.style_config = newConfig.style_config || form.style_config
  }
}, { immediate: true })

const previewStyle = computed(() => {
  if (props.position === 'header') {
    return {
      backgroundColor: form.style_config.bg_color,
      color: form.style_config.text_color
    }
  }
  return {}
})

const addItem = () => {
  form.nav_items.push({
    id: Date.now(),
    label: '新导航项',
    link: '/',
    type: 'link',
    items: []
  })
}

const removeItem = (index) => {
  form.nav_items.splice(index, 1)
}

const addSubItem = (parent) => {
  if (!parent.items) {
    parent.items = []
  }
  parent.items.push({
    label: '子项',
    link: '/'
  })
}

const removeSubItem = (parent, index) => {
  parent.items.splice(index, 1)
}

const save = () => {
  emit('save', {
    nav_position: props.position,
    nav_items: form.nav_items,
    style_config: form.style_config
  })
}
</script>

<style scoped>
.navigation-editor {
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.editor-header h4 {
  margin: 0;
  font-size: 18px;
}

.style-config {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.style-config h5 {
  margin: 0 0 16px;
  font-size: 14px;
  color: #666;
}

.nav-items {
  margin-bottom: 24px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.items-header h5 {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.item-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drag-handle {
  cursor: move;
  color: #999;
  font-size: 18px;
}

.item-fields {
  flex: 1;
  display: flex;
  gap: 12px;
}

.field-label {
  width: 150px;
}

.field-link {
  flex: 1;
}

.field-type {
  width: 120px;
}

.delete-btn {
  cursor: pointer;
  color: #f56c6c;
  font-size: 18px;
}

.dropdown-items {
  margin-top: 12px;
  padding-left: 30px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dropdown-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dropdown-item .el-input {
  flex: 1;
}

.dropdown-item .el-icon {
  cursor: pointer;
  color: #999;
}

.preview-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 24px;
}

.preview-section h5 {
  margin: 0 0 16px;
  font-size: 14px;
  color: #666;
}

.nav-preview {
  padding: 16px 24px;
  border-radius: 8px;
  display: flex;
  gap: 24px;
  align-items: center;
}

.nav-preview.header {
  background: #2c2420;
}

.nav-preview.footer {
  background: #f5f7fa;
  flex-wrap: wrap;
}

.nav-link {
  color: inherit;
  text-decoration: none;
  font-size: 14px;
}

.nav-btn {
  padding: 8px 16px;
  background: #8b7355;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.nav-dropdown {
  position: relative;
  cursor: pointer;
}

.nav-dropdown .dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 4px;
  padding: 8px 0;
  min-width: 150px;
  margin-top: 8px;
}

.nav-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-menu a {
  display: block;
  padding: 8px 16px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
}

.dropdown-menu a:hover {
  background: #f5f7fa;
}
</style>
