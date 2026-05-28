<template>
  <div class="customer-login-page">
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>登录查看您的选品清单</p>
        </div>

        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
          <el-form-item prop="phone">
            <el-input
              v-model="loginForm.phone"
              placeholder="请输入手机号"
              size="large"
              maxlength="11"
            >
              <template #prefix>
                <el-icon><Iphone /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
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

        <div class="register-link">
          还没有账号？<el-link type="primary" @click="goToRegister">立即注册</el-link>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog v-model="showForgotDialog" title="找回密码" width="400px">
      <el-form :model="forgotForm" label-width="80px">
        <el-form-item label="手机号">
          <el-input v-model="forgotForm.phone" placeholder="请输入注册手机号" maxlength="11" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotDialog = false">取消</el-button>
        <el-button type="primary" @click="handleForgot">发送验证码</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, Lock } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const route = useRoute()

const loginFormRef = ref(null)
const loginForm = reactive({
  phone: '',
  password: ''
})

const loginRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const loading = ref(false)
const rememberMe = ref(false)
const showForgotDialog = ref(false)
const forgotForm = reactive({ phone: '' })

const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await request.post('/customer/login', {
      phone: loginForm.phone,
      password: loginForm.password
    })

    if (res.data.code === 200) {
      const { token, user } = res.data.data
      localStorage.setItem('customer_token', token)
      localStorage.setItem('customer_user', JSON.stringify(user))
      
      ElMessage.success('登录成功')
      
      // 跳转到指定页面或选品中心
      const redirect = route.query.redirect || '/selection-center'
      router.push(redirect)
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}

const handleForgot = () => {
  ElMessage.info('验证码已发送（演示模式：123456）')
  showForgotDialog.value = false
}

const goToRegister = () => {
  router.push('/register?redirect=' + encodeURIComponent(route.query.redirect || '/selection-center'))
}
</script>

<style scoped>
.customer-login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #409EFF 0%, #6C63FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-box {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #0a0a1a;
  margin: 0 0 8px;
}

.login-header p {
  color: #999;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: #409EFF;
  border-color: #409EFF;
}

.login-btn:hover {
  background: #3a8ee6;
  border-color: #3a8ee6;
}

.register-link {
  text-align: center;
  color: #666;
  font-size: 14px;
}
</style>
