import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用户状态
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    clearToken
  }
})

// 案例筛选状态
export const useCaseFilterStore = defineStore('caseFilter', () => {
  const filters = ref({
    type: '',
    style: '',
    space_type: '',
    budget_range: '',
    keyword: ''
  })

  const setFilter = (key, value) => {
    filters.value[key] = value
  }

  const resetFilters = () => {
    filters.value = {
      type: '',
      style: '',
      space_type: '',
      budget_range: '',
      keyword: ''
    }
  }

  return {
    filters,
    setFilter,
    resetFilters
  }
})
