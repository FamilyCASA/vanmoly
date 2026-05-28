<template>
  <div class="login-page">
    <div class="login-box">
      <h2>D&B 帝标|设记家 V3.3.0</h2>
      <p>全案服务管理系统</p>
      
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <p class="tip">默认账号: admin / admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const res = await login(form)
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #0a0a1a 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #1a1a2e;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.login-box h2 {
  text-align: center;
  margin-bottom: 8px;
  color: #E8E8E8;
}

.login-box p {
  text-align: center;
  color: #A0A0B8;
  margin-bottom: 32px;
}

.tip {
  margin-top: 16px;
  font-size: 12px;
  color: #A0A0B8;
}

/* 暗黑模式 - 表单元素覆盖 */
:deep(.el-input__wrapper) {
  background-color: #0a0a1a !important;
  border: 1px solid #2a2a3e;
}
:deep(.el-input__inner) {
  color: #E8E8E8 !important;
}
:deep(.el-input__inner::placeholder) {
  color: #606080 !important;
}
:deep(.el-form-item__label) {
  color: #A0A0B8;
}
:deep(.el-button--primary) {
  background-color: #409EFF;
  border-color: #409EFF;
}
</style>
