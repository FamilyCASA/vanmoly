<template>
  <div class="user-center-page">
    <Navbar />

    <main class="user-center-main">
      <section class="intro-panel">
        <div class="eyebrow">USER CENTER</div>
        <h1>用户中心</h1>
        <p>同一个入口从低权限到高权限识别身份。访客保留前台权限，员工进入个人后台，管理员再进入管理后台。</p>

        <div class="permission-row">
          <div class="permission-item">
            <el-icon><UserFilled /></el-icon>
            <span>员工任务</span>
          </div>
          <div class="permission-item">
            <el-icon><Document /></el-icon>
            <span>案例报价表</span>
          </div>
          <div class="permission-item">
            <el-icon><ShoppingCart /></el-icon>
            <span>采购清单</span>
          </div>
        </div>
      </section>

      <section class="account-panel">
        <div v-if="customerLoggedIn" class="visitor-card">
          <div class="visitor-header">
            <div>
              <span class="status-pill">访客账号</span>
              <h2>{{ customerUser.nickname || customerUser.name || '网站访客' }}</h2>
              <p>{{ customerUser.phone || '已登录前台用户中心' }}</p>
            </div>
            <el-button text type="danger" @click="logoutCustomer">退出</el-button>
          </div>

          <div class="visitor-actions">
            <button class="action-card" @click="router.push('/cases')">
              <el-icon><Document /></el-icon>
              <span>查看案例报价表</span>
            </button>
            <button class="action-card" @click="router.push('/selection-center')">
              <el-icon><ShoppingCart /></el-icon>
              <span>查看我的采购清单</span>
            </button>
            <button class="action-card" @click="router.push('/products')">
              <el-icon><Goods /></el-icon>
              <span>继续选品</span>
            </button>
          </div>
        </div>

        <template v-else>
          <div class="panel-header">
            <h2>{{ activeMode === 'login' ? '登录账号' : '注册访客账号' }}</h2>
            <p>{{ activeMode === 'login' ? '系统先识别访客账号，再识别员工与管理员账号' : '注册后可保存选品清单并查看前台报价信息' }}</p>
          </div>

          <el-segmented
            v-model="activeMode"
            :options="[
              { label: '登录', value: 'login' },
              { label: '访客注册', value: 'register' }
            ]"
            class="mode-switch"
          />

          <el-form
            v-if="activeMode === 'login'"
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="account-form"
          >
            <el-form-item prop="identifier">
              <el-input
                v-model="loginForm.identifier"
                size="large"
                placeholder="手机号 / 员工账号"
                clearable
              >
                <template #prefix><el-icon><User /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                size="large"
                type="password"
                placeholder="请输入密码"
                show-password
                @keyup.enter="handleUnifiedLogin"
              >
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleUnifiedLogin">
              登录并自动识别权限
            </el-button>
            <p class="form-note">系统按访客、员工、管理员的顺序判断权限；员工和管理员登录后进入后台“我的”界面。</p>
          </el-form>

          <el-form
            v-else
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="account-form"
          >
            <el-form-item prop="nickname">
              <el-input v-model="registerForm.nickname" size="large" placeholder="昵称">
                <template #prefix><el-icon><User /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="phone">
              <el-input v-model="registerForm.phone" size="large" placeholder="手机号" maxlength="11">
                <template #prefix><el-icon><Iphone /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="registerForm.password" size="large" type="password" placeholder="设置密码" show-password>
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                size="large"
                type="password"
                placeholder="确认密码"
                show-password
                @keyup.enter="handleVisitorRegister"
              >
                <template #prefix><el-icon><Lock /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-checkbox v-model="registerForm.agreement" class="agreement">
              我同意注册为网站访客账号，仅使用前台用户权限
            </el-checkbox>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleVisitorRegister">
              注册并进入用户中心
            </el-button>
          </el-form>
        </template>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import {
  Document, Goods, Iphone, Lock, ShoppingCart, User, UserFilled
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const route = useRoute()
const activeMode = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const customerUser = ref(readCustomerUser())
const customerToken = ref(localStorage.getItem('customer_token') || '')

const authClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v3',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

const phonePattern = /^1[3-9]\d{9}$/

const loginForm = reactive({
  identifier: '',
  password: ''
})

const registerForm = reactive({
  nickname: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const customerLoggedIn = computed(() => Boolean(customerToken.value))

const loginRules = {
  identifier: [{ required: true, message: '请输入员工账号或手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const validateConfirmPassword = (_rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== registerForm.password) callback(new Error('两次密码不一致'))
  else callback()
}

const registerRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: phonePattern, message: '手机号格式错误', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

function readCustomerUser() {
  try {
    return JSON.parse(localStorage.getItem('customer_user') || '{}')
  } catch {
    return {}
  }
}

function unwrapResponse(response) {
  const body = response?.data || {}
  return body.data || body
}

function saveStaffSession(payload) {
  localStorage.setItem('token', payload.token)
  localStorage.setItem('user', JSON.stringify(payload.user || {}))
  localStorage.removeItem('customer_token')
  localStorage.removeItem('customer_user')
}

function saveCustomerSession(payload) {
  localStorage.setItem('customer_token', payload.token)
  localStorage.setItem('customer_user', JSON.stringify(payload.user || {}))
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  customerToken.value = payload.token
  customerUser.value = payload.user || {}
}

async function tryStaffLogin() {
  const response = await authClient.post('/auth/login', {
    identifier: loginForm.identifier.trim(),
    password: loginForm.password
  })
  const data = unwrapResponse(response)
  return data?.token ? data : null
}

async function tryCustomerLogin() {
  if (!phonePattern.test(loginForm.identifier.trim())) return null
  const response = await authClient.post('/customer/login', {
    phone: loginForm.identifier.trim(),
    password: loginForm.password
  })
  const data = unwrapResponse(response)
  return data?.token ? data : null
}

const handleUnifiedLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    try {
      const customer = await tryCustomerLogin()
      if (customer?.token) {
        saveCustomerSession(customer)
        ElMessage.success('访客登录成功')
        const redirect = route.query.redirect
        if (redirect && String(redirect).startsWith('/selection-center')) {
          router.replace(String(redirect))
        }
        return
      }
    } catch {}

    try {
      const staff = await tryStaffLogin()
      if (staff?.token) {
        saveStaffSession(staff)
        ElMessage.success('员工登录成功')
        router.replace({ path: '/admin/my-workspace', query: { openMine: '1' } })
        return
      }
    } catch {}

    ElMessage.error('账号或密码不正确，请确认后重试')
  } finally {
    loading.value = false
  }
}

const handleVisitorRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!registerForm.agreement) {
    ElMessage.warning('请先同意访客账号权限说明')
    return
  }

  loading.value = true
  try {
    const response = await authClient.post('/customer/register', {
      nickname: registerForm.nickname.trim(),
      phone: registerForm.phone.trim(),
      password: registerForm.password,
      source: '用户中心',
      channel: 'website',
      anonymous_items: JSON.parse(localStorage.getItem('vanmoly_anonymous_selection') || '[]')
    })
    const data = unwrapResponse(response)
    if (data?.token) {
      saveCustomerSession(data)
      localStorage.removeItem('vanmoly_anonymous_selection')
      ElMessage.success('注册成功')
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const logoutCustomer = () => {
  localStorage.removeItem('customer_token')
  localStorage.removeItem('customer_user')
  customerToken.value = ''
  customerUser.value = {}
  activeMode.value = 'login'
}

onMounted(() => {
  if (localStorage.getItem('token')) {
    router.replace({ path: '/admin/my-workspace', query: { openMine: '1' } })
    return
  }
  customerToken.value = localStorage.getItem('customer_token') || ''
  customerUser.value = readCustomerUser()
})
</script>

<style scoped>
.user-center-page {
  min-height: 100vh;
  background:
    linear-gradient(120deg, rgba(9, 16, 31, 0.92), rgba(26, 21, 37, 0.88)),
    url('/uploads/cases/%E7%AE%80%E7%BA%A6_10.jpg') center/cover;
  color: #fff;
}

.user-center-main {
  width: min(1180px, calc(100% - 40px));
  min-height: 100vh;
  margin: 0 auto;
  padding: 150px 0 72px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  gap: 56px;
  align-items: center;
}

.intro-panel h1 {
  font-size: 56px;
  line-height: 1.08;
  margin: 16px 0 18px;
  letter-spacing: 0;
}

.intro-panel p {
  max-width: 620px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 18px;
  line-height: 1.9;
}

.eyebrow {
  color: #d8aa62;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 4px;
}

.permission-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 34px;
}

.permission-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.88);
}

.account-panel {
  padding: 28px;
  border-radius: 8px;
  background: rgba(8, 13, 25, 0.84);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.36);
  backdrop-filter: blur(14px);
}

.panel-header h2,
.visitor-header h2 {
  margin: 0 0 8px;
  font-size: 26px;
}

.panel-header p,
.visitor-header p,
.form-note {
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.7;
}

.mode-switch {
  width: 100%;
  margin: 22px 0;
}

.account-form :deep(.el-input__wrapper) {
  min-height: 46px;
  background: rgba(255, 255, 255, 0.96);
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
  min-height: 46px;
}

.form-note {
  margin-top: 14px;
  font-size: 13px;
}

.agreement {
  margin: 2px 0 14px;
  color: rgba(255, 255, 255, 0.74);
}

.visitor-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.status-pill {
  display: inline-flex;
  margin-bottom: 12px;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.18);
  color: #83c3ff;
  font-size: 12px;
}

.visitor-actions {
  display: grid;
  gap: 12px;
  margin-top: 28px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-card:hover {
  border-color: rgba(64, 158, 255, 0.58);
  background: rgba(64, 158, 255, 0.18);
}

@media (max-width: 900px) {
  .user-center-main {
    grid-template-columns: 1fr;
    padding-top: 118px;
    gap: 30px;
  }

  .intro-panel h1 {
    font-size: 40px;
  }
}
</style>
