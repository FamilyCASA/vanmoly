<template>
  <div class="customer-register-page">
    <div class="register-container">
      <!-- 左侧欢迎区 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1>欢迎来到D&B 帝标|设记家</h1>
          <p class="welcome-subtitle">开启您的美好家居之旅</p>
          
          <div class="feature-list">
            <div class="feature-item">
              <el-icon :size="24" color="#8B5A2B"><Collection /></el-icon>
              <div>
                <h4>专属选品中心</h4>
                <p>保存您的心仪产品，随时查看对比</p>
              </div>
            </div>
            <div class="feature-item">
              <el-icon :size="24" color="#8B5A2B"><DocumentChecked /></el-icon>
              <div>
                <h4>智能方案推荐</h4>
                <p>根据您的选择，推荐最适合的套餐</p>
              </div>
            </div>
            <div class="feature-item">
              <el-icon :size="24" color="#8B5A2B"><Service /></el-icon>
              <div>
                <h4>一对一服务</h4>
                <p>专业顾问为您提供专属服务</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册区 -->
      <div class="register-section">
        <div class="register-box">
          <div class="register-header">
            <h2>创建您的账户</h2>
            <p class="register-subtitle">已有账户？<el-link type="primary" @click="goToLogin">立即登录</el-link></p>
          </div>

          <!-- 注册步骤 -->
          <el-steps :active="currentStep" finish-status="success" simple class="register-steps">
            <el-step title="填写信息" />
            <el-step title="完成注册" />
          </el-steps>

          <!-- 步骤1：填写信息 -->
          <div v-if="currentStep === 0" class="step-content">
            <el-form
              :model="registerForm"
              :rules="registerRules"
              ref="registerFormRef"
              label-position="top"
            >
              <el-form-item label="昵称" prop="nickname">
                <el-input
                  v-model="registerForm.nickname"
                  placeholder="请输入您的昵称"
                  size="large"
                  :prefix-icon="User"
                />
              </el-form-item>

              <el-form-item label="手机号" prop="phone">
                <el-input
                  v-model="registerForm.phone"
                  placeholder="请输入手机号码"
                  size="large"
                  maxlength="11"
                  :prefix-icon="Iphone"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请设置登录密码（至少6位）"
                  size="large"
                  show-password
                  :prefix-icon="Lock"
                />
                <div class="password-strength" v-if="registerForm.password">
                  <span>密码强度：</span>
                  <el-tag :type="passwordStrength.type" size="small">{{ passwordStrength.text }}</el-tag>
                </div>
              </el-form-item>

              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  size="large"
                  show-password
                  :prefix-icon="Lock"
                />
              </el-form-item>

              <el-form-item prop="agreement">
                <el-checkbox v-model="registerForm.agreement">
                  我已阅读并同意<el-link type="primary">《用户服务协议》</el-link>和<el-link type="primary">《隐私政策》</el-link>
                </el-checkbox>
              </el-form-item>

              <el-button
                type="primary"
                size="large"
                class="submit-btn"
                :loading="registering"
                @click="handleRegister"
              >
                立即注册
              </el-button>
            </el-form>

            <div class="divider">
              <span>或</span>
            </div>

            <div class="social-login">
              <el-button class="social-btn wechat" @click="registerWithWechat">
                <el-icon><ChatDotRound /></el-icon>
                微信一键注册
              </el-button>
            </div>
          </div>

          <!-- 步骤2：注册成功 -->
          <div v-if="currentStep === 1" class="step-content success-step">
            <el-result
              icon="success"
              title="注册成功！"
              :sub-title="`欢迎加入D&B 帝标|设记家，${registeredUser.nickname}`"
            >
              <template #extra>
                <div class="success-info">
                  <p>您的选品清单已保存到账户</p>
                  <p class="selection-count">共 {{ migratedCount }} 件商品</p>
                </div>
                <el-button type="primary" size="large" @click="goToSelectionCenter">
                  进入选品中心
                </el-button>
                <el-button size="large" @click="goToHome">先逛逛</el-button>
              </template>
            </el-result>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Iphone, Lock, Collection, DocumentChecked, Service, ChatDotRound
} from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAnonymousSelection } from '@/composables/useAnonymousSelection'

const router = useRouter()
const route = useRoute()
const { items, totalCount, migrateToUser } = useAnonymousSelection()

// 注册步骤
const currentStep = ref(0)
const registering = ref(false)
const registeredUser = ref({})
const migratedCount = ref(0)

// 注册表单
const registerFormRef = ref(null)
const registerForm = reactive({
  nickname: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agreement: false,
  source: 'website',  // 注册来源
  channel: 'DESIGNARY网站自然流量'  // 线索渠道
})

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = registerForm.password
  if (!pwd) return { type: 'info', text: '未输入' }
  
  let score = 0
  if (pwd.length >= 6) score++
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z0-9]/.test(pwd)) score++
  
  if (score <= 2) return { type: 'danger', text: '弱' }
  if (score <= 4) return { type: 'warning', text: '中' }
  return { type: 'success', text: '强' }
})

// 验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreement = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请同意用户协议'))
  } else {
    callback()
  }
}

const registerRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度2-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式错误', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreement: [
    { validator: validateAgreement, trigger: 'change' }
  ]
}

// 注册处理
const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return

  registering.value = true
  try {
    // 准备注册数据
    const registerData = {
      nickname: registerForm.nickname,
      phone: registerForm.phone,
      password: registerForm.password,
      source: registerForm.source,
      channel: registerForm.channel,
      // 如果有匿名选品，一并提交
      anonymous_items: items.value
    }

    const res = await request.post('/customer/register', registerData)
    
    if (res.data.code === 200) {
      const { token, user } = res.data.data
      
      // 保存登录状态
      localStorage.setItem('customer_token', token)
      localStorage.setItem('customer_user', JSON.stringify(user))
      
      registeredUser.value = user
      migratedCount.value = totalCount.value
      
      // 清空匿名选品
      localStorage.removeItem('vanmoly_anonymous_selection')
      
      // 进入下一步
      currentStep.value = 1
      
      ElMessage.success('注册成功！')
    } else {
      ElMessage.error(res.data.message || '注册失败')
    }
  } catch (error) {
    const msg = error.response?.data?.message || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    registering.value = false
  }
}

// 微信注册
const registerWithWechat = () => {
  ElMessage.info('微信注册功能开发中')
}

// 跳转
const goToLogin = () => {
  router.push('/customer/login?redirect=' + encodeURIComponent(route.query.redirect || '/selection-center'))
}

const goToSelectionCenter = () => {
  router.push('/selection-center')
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.customer-register-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.register-container {
  display: flex;
  min-height: 100vh;
}

/* 左侧欢迎区 */
.welcome-section {
  flex: 1;
  background: linear-gradient(135deg, #8B5A2B 0%, #A67B5B 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.welcome-content h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
}

.welcome-subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin-bottom: 60px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-item h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px;
}

.feature-item p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

/* 右侧注册区 */
.register-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #fff;
}

.register-box {
  width: 100%;
  max-width: 420px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.register-subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.register-steps {
  margin-bottom: 32px;
}

.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

.password-strength {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: #8B5A2B;
  border-color: #8B5A2B;
  margin-top: 8px;
}

.submit-btn:hover {
  background: #6B4423;
  border-color: #6B4423;
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #999;
  font-size: 14px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e8e8e8;
}

.divider span {
  padding: 0 16px;
}

.social-login {
  display: flex;
  justify-content: center;
}

.social-btn {
  width: 100%;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.social-btn.wechat {
  background: #07c160;
  color: #fff;
  border-color: #07c160;
}

.social-btn.wechat:hover {
  background: #06ad56;
  border-color: #06ad56;
}

/* 成功步骤 */
.success-step {
  text-align: center;
}

.success-info {
  margin: 20px 0;
  padding: 16px;
  background: #f6ffed;
  border-radius: 8px;
}

.success-info p {
  margin: 4px 0;
  color: #666;
}

.selection-count {
  font-size: 18px;
  font-weight: 600;
  color: #52c41a;
}

/* 响应式 */
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
  }
  
  .welcome-section {
    padding: 40px 24px;
    min-height: auto;
  }
  
  .welcome-content h1 {
    font-size: 28px;
  }
  
  .feature-list {
    gap: 20px;
  }
  
  .register-section {
    padding: 40px 24px;
  }
}
</style>
