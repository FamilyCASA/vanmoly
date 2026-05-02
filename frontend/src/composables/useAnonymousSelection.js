/**
 * 匿名选品 Composable - 全局单例模式
 * 基于 localStorage + cookie 实现匿名用户选品记录
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'vanmoly_anonymous_selection'
const COOKIE_KEY = 'vanmoly_visitor_id'

// ===== 全局状态（单例） =====
const globalVisitorId = ref('')
const globalSelectionData = ref({ items: [], spaces: [] })
const isInitialized = ref(false)

// 全局事件总线，用于触发吞咽动画
const swallowCallbacks = []

export const onSwallow = (callback) => {
  swallowCallbacks.push(callback)
  return () => {
    const index = swallowCallbacks.indexOf(callback)
    if (index > -1) swallowCallbacks.splice(index, 1)
  }
}

export const triggerSwallow = () => {
  swallowCallbacks.forEach(cb => cb())
}

// 生成访客ID
const generateVisitorId = () => {
  return 'v_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 获取或创建访客ID
const getVisitorId = () => {
  let visitorId = localStorage.getItem(COOKIE_KEY)
  if (!visitorId) {
    visitorId = generateVisitorId()
    localStorage.setItem(COOKIE_KEY, visitorId)
  }
  return visitorId
}

// 获取选品数据
const getSelectionData = () => {
  const data = localStorage.getItem(STORAGE_KEY)
  if (data) {
    try {
      return JSON.parse(data)
    } catch (e) {
      return { items: [], spaces: [] }
    }
  }
  return { items: [], spaces: [] }
}

// 保存选品数据
const saveSelectionData = (data) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export function useAnonymousSelection() {
  // 使用全局状态
  const visitorId = globalVisitorId
  const selectionData = globalSelectionData
  
  // 初始化（只执行一次）
  onMounted(() => {
    if (!isInitialized.value) {
      visitorId.value = getVisitorId()
      selectionData.value = getSelectionData()
      isInitialized.value = true
      
      // 监听 storage 事件（跨标签页同步）
      window.addEventListener('storage', handleStorageChange)
    }
  })
  
  onUnmounted(() => {
    window.removeEventListener('storage', handleStorageChange)
  })
  
  // 处理 storage 变化（跨标签页同步）
  const handleStorageChange = (e) => {
    if (e.key === STORAGE_KEY) {
      selectionData.value = getSelectionData()
    }
  }
  
  // 选品列表
  const items = computed(() => selectionData.value.items || [])
  
  // 空间列表
  const spaces = computed(() => selectionData.value.spaces || [])
  
  // 选品总数
  const totalCount = computed(() => items.value.length)
  
  // 选品总价
  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => {
      const price = item.price || 0
      const quantity = item.quantity || 1
      return sum + (price * quantity)
    }, 0)
  })
  
  // 按空间分组
  const itemsBySpace = computed(() => {
    const grouped = {}
    items.value.forEach(item => {
      const spaceName = item.space_name || '未分类'
      if (!grouped[spaceName]) {
        grouped[spaceName] = []
      }
      grouped[spaceName].push(item)
    })
    return grouped
  })
  
  // 添加选品
  const addItem = (item) => {
    const data = getSelectionData()
    
    // 检查是否已存在
    const existingIndex = data.items.findIndex(i => 
      i.id === item.id && i.type === item.type
    )
    
    if (existingIndex >= 0) {
      // 更新数量
      data.items[existingIndex].quantity = (data.items[existingIndex].quantity || 1) + 1
    } else {
      // 添加新项
      data.items.push({
        ...item,
        quantity: 1,
        added_at: new Date().toISOString()
      })
    }
    
    saveSelectionData(data)
    
    // 重要：创建新对象触发 Vue 响应式更新
    selectionData.value = { ...data, items: [...data.items] }
    
    // 触发吞咽动画
    triggerSwallow()
    
    return true
  }
  
  // 更新数量
  const updateQuantity = (itemId, type, quantity) => {
    const data = getSelectionData()
    const index = data.items.findIndex(i => i.id === itemId && i.type === type)
    
    if (index >= 0) {
      if (quantity <= 0) {
        data.items.splice(index, 1)
      } else {
        data.items[index].quantity = quantity
      }
      saveSelectionData(data)
      // 创建新对象触发响应式更新
      selectionData.value = { ...data, items: [...data.items] }
      return true
    }
    return false
  }
  
  // 删除选品
  const removeItem = (itemId, type) => {
    const data = getSelectionData()
    data.items = data.items.filter(i => !(i.id === itemId && i.type === type))
    saveSelectionData(data)
    // 创建新对象触发响应式更新
    selectionData.value = { ...data, items: [...data.items] }
  }
  
  // 清空选品
  const clearAll = () => {
    const emptyData = { items: [], spaces: [] }
    saveSelectionData(emptyData)
    selectionData.value = { ...emptyData }
  }
  
  // 迁移到登录用户（注册/登录后调用）
  const migrateToUser = async (api) => {
    const data = getSelectionData()
    if (data.items.length === 0) return { migrated: false }
    
    try {
      // 调用API将匿名选品迁移到用户账号
      const res = await api.post('/selection/migrate', {
        visitor_id: visitorId.value,
        items: data.items
      })
      
      if (res.data.code === 200) {
        // 清空本地数据
        clearAll()
        return { migrated: true, count: data.items.length }
      }
    } catch (error) {
      console.error('迁移选品失败:', error)
    }
    
    return { migrated: false }
  }
  
  // 检查是否有选品
  const hasItems = computed(() => items.value.length > 0)
  
  return {
    visitorId,
    items,
    spaces,
    totalCount,
    totalPrice,
    itemsBySpace,
    hasItems,
    addItem,
    updateQuantity,
    removeItem,
    clearAll,
    migrateToUser
  }
}
