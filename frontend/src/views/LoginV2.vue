<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <!-- <img src="/logo.png" alt="D&B 帝标|设记家" class="brand-logo" v-if="false"> -->
          <div class="brand-title">D&B 帝标|设记家</div>
          <div class="brand-subtitle">全案服务系统 V3.2</div>
          <div class="brand-desc">
            <p>专业 · 高效 · 温暖</p>
            <p>让每一次服务都成为美好回忆</p>
          </div>
        </div>
        <div class="brand-footer">
          © 2026 D&B 帝标|设记家 版权所有
        </div>
      </div>

      <!-- 右侧登录区 -->
      <div class="login-section">
        <div class="login-box">
          <h2 class="login-title">欢迎回来</h2>
          <p class="login-subtitle">请登录您的账号</p>

          <!-- 登录方式切换 -->
          <div class="login-tabs">
            <div 
              class="tab-item" 
              :class="{ active: loginMethod === 'password' }"
              @click="loginMethod = 'password'"
            >
              <el-icon><User /></el-icon>
              账号登录
            </div>
            <div 
              class="tab-item" 
              :class="{ active: loginMethod === 'wechat' }"
              @click="loginMethod = 'wechat'"
            >
              <el-icon><ChatDotRound /></el-icon>
              微信登录
            </div>
            <div 
              class="tab-item" 
              :class="{ active: loginMethod === 'qq' }"
              @click="loginMethod = 'qq'"
            >
              <el-icon><ChatSquare /></el-icon>
              QQ登录
            </div>
          </div>

          <!-- 账号密码登录 -->
          <div v-if="loginMethod === 'password'" class="login-form">
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
              <el-form-item prop="identifier">
                <el-input
                  v-model="loginForm.identifier"
                  placeholder="请输入昵称或手机号"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  @keyup.enter="handleLogin"
                />
              </el-form-item>
              <div class="form-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <el-link type="primary" @click="showForgotDialog = true">忘记密码？</el-link>
              </div>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form>

            <div class="default-password-tip" v-if="showDefaultTip">
              <el-alert
                title="默认密码提示"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  除超级管理员外，默认密码均为：<strong>van654321</strong>
                </template>
              </el-alert>
            </div>
          </div>

          <!-- 微信登录 -->
          <div v-if="loginMethod === 'wechat'" class="social-login">
            <div class="qr-placeholder">
              <div class="qr-code">
                <el-icon :size="80" color="#07c160"><ChatDotRound /></el-icon>
              </div>
              <p>请使用微信扫一扫登录</p>
              <p class="qr-tip">演示模式：点击模拟登录</p>
            </div>
            <el-button type="success" size="large" class="login-btn" @click="mockWechatLogin">
              模拟微信登录
            </el-button>
          </div>

          <!-- QQ登录 -->
          <div v-if="loginMethod === 'qq'" class="social-login">
            <div class="qr-placeholder">
              <div class="qr-code qq">
                <el-icon :size="80" color="#12b7f5"><ChatSquare /></el-icon>
              </div>
              <p>请使用QQ扫一扫登录</p>
              <p class="qr-tip">演示模式：点击模拟登录</p>
            </div>
            <el-button type="primary" size="large" class="login-btn" style="background: #12b7f5; border-color: #12b7f5;" @click="mockQQLogin">
              模拟QQ登录
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog
      v-model="showForgotDialog"
      title="找回密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-steps :active="forgotStep" simple finish-status="success">
        <el-step title="验证身份" />
        <el-step title="重置密码" />
        <el-step title="完成" />
      </el-steps>

      <!-- 步骤1：验证手机号 -->
      <div v-if="forgotStep === 0" class="forgot-step">
        <el-form :model="forgotForm" :rules="forgotRules" ref="forgotFormRef">
          <el-form-item prop="phone">
            <el-input
              v-model="forgotForm.phone"
              placeholder="请输入注册手机号"
              size="large"
            >
              <template #prefix>
                <el-icon><Iphone /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
        <el-button type="primary" size="large" class="full-width" :loading="sendingCode" @click="sendVerifyCode">
          获取验证码
        </el-button>
      </div>

      <!-- 步骤2：重置密码 -->
      <div v-if="forgotStep === 1" class="forgot-step">
        <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef">
          <el-form-item prop="code">
            <el-input
              v-model="resetForm.code"
              placeholder="请输入验证码"
              size="large"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="newPassword">
            <el-input
              v-model="resetForm.newPassword"
              type="password"
              placeholder="请输入新密码（至少6位）"
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="resetForm.confirmPassword"
              type="password"
              placeholder="请确认新密码"
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
        <el-button type="primary" size="large" class="full-width" :loading="resetting" @click="handleResetPassword">
          重置密码
        </el-button>
      </div>

      <!-- 步骤3：完成 -->
      <div v-if="forgotStep === 2" class="forgot-step success-step">
        <el-result
          icon="success"
          title="密码重置成功"
          sub-title="请使用新密码登录"
        >
          <template #extra>
            <el-button type="primary" @click="closeForgotDialog">去登录</el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>

    <!-- 首次登录修改密码弹窗 -->
    <el-dialog
      v-model="showChangePasswordDialog"
      title="首次登录 - 修改密码"
      width="400px"
      :close-on-click-modal="false"
      :show-close="false"
      :close-on-press-escape="false"
    >
      <el-alert
        title="安全提示"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #default>
          为了您的账号安全，首次登录需要修改初始密码
        </template>
      </el-alert>
      <el-form :model="changeForm" :rules="changeRules" ref="changeFormRef">
        <el-form-item prop="oldPassword">
          <el-input
            v-model="changeForm.oldPassword"
            type="password"
            placeholder="请输入当前密码（默认：van654321）"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item prop="newPassword">
          <el-input
            v-model="changeForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="changeForm.confirmPassword"
            type="password"
            placeholder="请确认新密码"
            size="large"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" size="large" :loading="changing" @click="handleChangePassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ChatDotRound, ChatSquare, Iphone, Key } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()

// 登录方式
const loginMethod = ref('password')
const loading = ref(false)
const rememberMe = ref(false)
const showDefaultTip = ref(true)

// 登录表单
const loginFormRef = ref(null)
const loginForm = reactive({
  identifier: '',
  password: ''
})

const loginRules = {
  identifier: [
    { required: true, message: '请输入昵称或手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

// 忘记密码
const showForgotDialog = ref(false)
const forgotStep = ref(0)
const sendingCode = ref(false)
const resetting = ref(false)

const forgotFormRef = ref(null)
const forgotForm = reactive({
  phone: ''
})

const forgotRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }
  ]
}

const resetFormRef = ref(null)
const resetForm = reactive({
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const resetRules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 修改密码
const showChangePasswordDialog = ref(false)
const changing = ref(false)
const tempToken = ref('')

const changeFormRef = ref(null)
const changeForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const changeRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== changeForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 登录处理
const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    console.log('登录请求:', { identifier: loginForm.identifier, password: '***' })
    const res = await request.post('/auth/login', {
      identifier: loginForm.identifier,
      password: loginForm.password
    })
    console.log('登录响应:', res)
    console.log('res.code:', res.code)
    console.log('res.data:', res.data)
    console.log('res.token:', res.token)
    console.log('是否有token:', !!(res.data?.token || res.token))

    // 兼容两种响应格式
    const responseData = res.data || res
    const token = responseData.token || res.token
    const user = responseData.user || res.user
    const must_change_password = responseData.must_change_password || res.must_change_password

    if (res.code === 200 || token) {
      // 保存token
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      
      if (must_change_password) {
        // 首次登录需要修改密码
        tempToken.value = token
        showChangePasswordDialog.value = true
      } else {
        ElMessage.success('登录成功')
        router.push('/admin/dashboard')
      }
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    console.error('登录错误:', error)
    const msg = error.response?.data?.message || error.message || '登录失败，请检查账号密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

// 模拟微信登录
const mockWechatLogin = async () => {
  loading.value = true
  try {
    const res = await request.post('/auth/login/wechat', { code: 'mock_wx_code' })
    if (res.data.code === 200) {
      const { token, user } = res.data.data
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('微信登录成功')
      router.push('/admin/dashboard')
    } else if (res.data.code === 404 && res.data.need_bind) {
      ElMessage.warning('该微信未绑定账号，请先使用账号密码登录后绑定')
      loginMethod.value = 'password'
    }
  } catch (error) {
    ElMessage.error('微信登录失败')
  } finally {
    loading.value = false
  }
}

// 模拟QQ登录
const mockQQLogin = async () => {
  loading.value = true
  try {
    const res = await request.post('/auth/login/qq', { code: 'mock_qq_code' })
    if (res.data.code === 200) {
      const { token, user } = res.data.data
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('QQ登录成功')
      router.push('/admin/dashboard')
    } else if (res.data.code === 404 && res.data.need_bind) {
      ElMessage.warning('该QQ未绑定账号，请先使用账号密码登录后绑定')
      loginMethod.value = 'password'
    }
  } catch (error) {
    ElMessage.error('QQ登录失败')
  } finally {
    loading.value = false
  }
}

// 发送验证码
const sendVerifyCode = async () => {
  const valid = await forgotFormRef.value?.validate().catch(() => false)
  if (!valid) return

  sendingCode.value = true
  try {
    const res = await request.post('/auth/password/reset-request', {
      phone: forgotForm.phone
    })
    if (res.data.code === 200) {
      ElMessage.success('验证码已发送（演示模式：123456）')
      forgotStep.value = 1
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    sendingCode.value = false
  }
}

// 重置密码
const handleResetPassword = async () => {
  const valid = await resetFormRef.value?.validate().catch(() => false)
  if (!valid) return

  resetting.value = true
  try {
    const res = await request.post('/auth/password/reset', {
      token: 'mock_reset_token',
      code: resetForm.code,
      new_password: resetForm.newPassword
    })
    if (res.data.code === 200) {
      ElMessage.success('密码重置成功')
      forgotStep.value = 2
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('重置失败')
  } finally {
    resetting.value = false
  }
}

// 修改密码（首次登录）
const handleChangePassword = async () => {
  const valid = await changeFormRef.value?.validate().catch(() => false)
  if (!valid) return

  changing.value = true
  try {
    const res = await request.post('/auth/password/change', {
      old_password: changeForm.oldPassword,
      new_password: changeForm.newPassword
    }, {
      headers: { 'Authorization': `Bearer ${tempToken.value}` }
    })
    if (res.data.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      showChangePasswordDialog.value = false
      // 清除token，要求重新登录
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      loginForm.password = ''
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('修改失败')
  } finally {
    changing.value = false
  }
}

const closeForgotDialog = () => {
  showForgotDialog.value = false
  forgotStep.value = 0
  forgotForm.phone = ''
  resetForm.code = ''
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
}

onMounted(() => {
  // 检查是否已登录
  const token = localStorage.getItem('token')
  if (token) {
    router.push('/admin/dashboard')
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: #f5f7fa;
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: auto;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  min-height: 600px;
}

/* 左侧品牌区 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #8B5A2B 0%, #A67B5B 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px;
  position: relative;
}

.brand-content {
  text-align: center;
}

.brand-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 8px;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 40px;
  letter-spacing: 2px;
}

.brand-desc {
  font-size: 14px;
  opacity: 0.8;
  line-height: 2;
}

.brand-footer {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  opacity: 0.6;
}

/* 右侧登录区 */
.login-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px;
  background: #fff;
}

.login-box {
  width: 100%;
  max-width: 360px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  text-align: center;
}

.login-subtitle {
  font-size: 14px;
  color: #999;
  margin-bottom: 32px;
  text-align: center;
}

/* 登录方式切换 */
.login-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: #f5f7fa;
  padding: 4px;
  border-radius: 8px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #8B5A2B;
}

.tab-item.active {
  background: #fff;
  color: #8B5A2B;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 登录表单 */
.login-form {
  margin-top: 8px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: #8B5A2B;
  border-color: #8B5A2B;
}

.login-btn:hover {
  background: #6B4423;
  border-color: #6B4423;
}

.default-password-tip {
  margin-top: 20px;
}

/* 社交登录 */
.social-login {
  text-align: center;
  padding: 20px 0;
}

.qr-placeholder {
  margin-bottom: 24px;
}

.qr-code {
  width: 180px;
  height: 180px;
  margin: 0 auto 16px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
}

.qr-code.qq {
  background: #f0f9ff;
  border-color: #bae7ff;
}

.qr-placeholder p {
  color: #666;
  font-size: 14px;
  margin: 4px 0;
}

.qr-tip {
  color: #999;
  font-size: 12px;
}

/* 忘记密码弹窗 */
.forgot-step {
  padding: 24px 0;
}

.full-width {
  width: 100%;
}

.success-step {
  padding: 40px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    margin: 0;
    border-radius: 0;
    min-height: 100vh;
  }
  
  .brand-section {
    padding: 40px 24px;
    min-height: 200px;
  }
  
  .brand-title {
    font-size: 32px;
  }
  
  .login-section {
    padding: 40px 24px;
  }
}
</style>
