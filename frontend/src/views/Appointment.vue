<template>
  <div class="appointment-page">
    <!-- 统一导航栏 -->
    <Navbar />

    <!-- 右侧 Sticky 预约按钮（滚动渐入） -->
    <transition name="sticky-btn-fade">
      <button
        v-if="showStickyBtn"
        class="sticky-book-btn"
        @click="scrollToForm"
      >
        <span class="sticky-book-icon">✏️</span>
        <span class="sticky-book-text">立即预约</span>
      </button>
    </transition>

    <!-- Hero区域 -->
    <section class="hero-section">
      <div class="hero-bg">
        <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1920" alt="预约量尺">
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-content">
        <h1>预约免费量尺</h1>
        <p class="hero-subtitle">专业设计师上门服务，量身定制您的理想家居</p>
        <div class="hero-features">
          <div class="feature">
            <el-icon :size="32"><Check /></el-icon>
            <span>免费上门</span>
          </div>
          <div class="feature">
            <el-icon :size="32"><Check /></el-icon>
            <span>专业测量</span>
          </div>
          <div class="feature">
            <el-icon :size="32"><Check /></el-icon>
            <span>方案设计</span>
          </div>
        </div>
        <button class="scroll-btn" @click="scrollToForm">
          <span>立即预约</span>
          <el-icon><ArrowDown /></el-icon>
        </button>
      </div>
    </section>

    <!-- 服务特色 -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">为什么选择我们</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="40"><User /></el-icon>
            </div>
            <h3>专业设计师</h3>
            <p>资深设计师一对一服务，根据您的生活习惯和审美偏好，量身定制专属方案</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="40"><FullScreen /></el-icon>
            </div>
            <h3>精准测量</h3>
            <p>专业测量工具，毫米级精度，确保每个尺寸都准确无误</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="40"><Document /></el-icon>
            </div>
            <h3>3D效果图</h3>
            <p>量尺后3-5天出具3D效果图，提前预览未来家的样子</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="40"><Lock /></el-icon>
            </div>
            <h3>品质保证</h3>
            <p>严选环保材料，10年质保承诺，让您安心入住</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 预约表单 -->
    <section class="form-section" id="booking-form">
      <div class="container">
        <div class="form-wrapper">
          <div class="form-header">
            <h2>填写预约信息</h2>
            <p>我们将在24小时内与您联系确认上门时间</p>
          </div>
          
          <el-form 
            ref="formRef"
            :model="form" 
            :rules="rules"
            label-position="top"
            class="booking-form"
          >
            <!-- 步骤指示器 -->
            <div class="step-indicator">
              <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                <div class="step-num">1</div>
                <span>基本信息</span>
              </div>
              <div class="step-line"></div>
              <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                <div class="step-num">2</div>
                <span>房屋信息</span>
              </div>
              <div class="step-line"></div>
              <div class="step" :class="{ active: currentStep >= 3 }">
                <div class="step-num">3</div>
                <span>预约时间</span>
              </div>
            </div>

            <!-- 步骤1: 基本信息 -->
            <div v-show="currentStep === 1" class="form-step">
              <el-row :gutter="24">
                <el-col :span="12" :xs="24">
                  <el-form-item label="您的姓名" prop="customer_name">
                    <el-input v-model="form.customer_name" placeholder="请输入您的姓名" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :span="12" :xs="24">
                  <el-form-item label="手机号码" prop="phone">
                    <el-input v-model="form.phone" placeholder="请输入手机号" size="large" maxlength="11" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="微信号（选填）">
                <el-input v-model="form.wechat" placeholder="方便我们添加您微信沟通" size="large" />
              </el-form-item>
            </div>

            <!-- 步骤2: 房屋信息 -->
            <div v-show="currentStep === 2" class="form-step">
              <el-form-item label="房屋地址" prop="house_address">
                <el-input v-model="form.house_address" placeholder="请输入详细地址，如：XX小区X栋X单元XXX" size="large" />
              </el-form-item>
              <el-row :gutter="24">
                <el-col :span="8" :xs="24">
                  <el-form-item label="户型">
                    <el-select v-model="form.house_type" placeholder="选择户型" size="large" style="width: 100%">
                      <el-option label="一室一厅" value="一室一厅" />
                      <el-option label="两室一厅" value="两室一厅" />
                      <el-option label="三室一厅" value="三室一厅" />
                      <el-option label="三室两厅" value="三室两厅" />
                      <el-option label="四室及以上" value="四室及以上" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8" :xs="24">
                  <el-form-item label="房屋面积">
                    <el-select v-model="form.area" placeholder="选择面积" size="large" style="width: 100%">
                      <el-option label="80㎡以下" value="80以下" />
                      <el-option label="80-100㎡" value="80-100" />
                      <el-option label="100-120㎡" value="100-120" />
                      <el-option label="120-150㎡" value="120-150" />
                      <el-option label="150㎡以上" value="150以上" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8" :xs="24">
                  <el-form-item label="装修预算">
                    <el-select v-model="form.budget" placeholder="选择预算" size="large" style="width: 100%">
                      <el-option label="15万以下" value="15万以下" />
                      <el-option label="15-20万" value="15-20万" />
                      <el-option label="20-30万" value="20-30万" />
                      <el-option label="30-50万" value="30-50万" />
                      <el-option label="50万以上" value="50万以上" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>

            <!-- 步骤3: 预约时间 -->
            <div v-show="currentStep === 3" class="form-step">
              <el-row :gutter="24">
                <el-col :span="12" :xs="24">
                  <el-form-item label="预约日期" prop="appointment_date">
                    <el-date-picker
                      v-model="form.appointment_date"
                      type="date"
                      placeholder="选择日期"
                      size="large"
                      style="width: 100%"
                      :disabled-date="disabledDate"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12" :xs="24">
                  <el-form-item label="预约时间" prop="appointment_time">
                    <el-time-select
                      v-model="form.appointment_time"
                      placeholder="选择时间"
                      size="large"
                      style="width: 100%"
                      start="09:00"
                      step="01:00"
                      end="18:00"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="备注说明">
                <el-input 
                  v-model="form.remark" 
                  type="textarea" 
                  :rows="3"
                  placeholder="请补充其他需求或注意事项，如：需要测量厨房和主卧..."
                />
              </el-form-item>
            </div>

            <!-- 按钮组 -->
            <div class="form-actions">
              <el-button 
                v-if="currentStep > 1" 
                size="large" 
                @click="prevStep"
              >
                上一步
              </el-button>
              <el-button 
                v-if="currentStep < 3" 
                type="primary" 
                size="large" 
                @click="nextStep"
              >
                下一步
              </el-button>
              <el-button 
                v-if="currentStep === 3" 
                type="primary" 
                size="large" 
                :loading="submitting"
                @click="handleSubmit"
              >
                {{ submitting ? '提交中...' : '提交预约' }}
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
    </section>

    <!-- 服务流程 -->
    <section class="process-section">
      <div class="container">
        <h2 class="section-title">服务流程</h2>
        <div class="process-timeline">
          <div class="timeline-item">
            <div class="timeline-icon">
              <span>01</span>
            </div>
            <div class="timeline-content">
              <h3>在线预约</h3>
              <p>填写预约表单，提交您的基本信息和房屋情况</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-icon">
              <span>02</span>
            </div>
            <div class="timeline-content">
              <h3>电话确认</h3>
              <p>客服将在24小时内致电确认上门时间和具体需求</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-icon">
              <span>03</span>
            </div>
            <div class="timeline-content">
              <h3>上门量尺</h3>
              <p>专业设计师携带工具上门，精准测量每个空间</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-icon">
              <span>04</span>
            </div>
            <div class="timeline-content">
              <h3>方案设计</h3>
              <p>3-5天内出具3D效果图和详细报价方案</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 统一页脚 -->
    <Footer />

    <!-- 成功弹窗 -->
    <el-dialog
      v-model="successDialogVisible"
      title="预约成功"
      width="420px"
      :show-close="false"
      :close-on-click-modal="false"
      center
      class="success-dialog"
    >
      <div class="success-content">
        <div class="success-icon">
          <el-icon :size="64" color="#10b981"><CircleCheck /></el-icon>
        </div>
        <h3>预约提交成功！</h3>
        <p>我们的客服将在24小时内与您联系确认</p>
        <div class="appointment-info">
          <span>预约编号</span>
          <strong>{{ appointmentId }}</strong>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" size="large" @click="handleSuccessClose" style="width: 100%">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, ArrowDown, User, FullScreen, Document, Lock, CircleCheck } from '@element-plus/icons-vue'
import { createAppointment } from '@/api/appointment'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const successDialogVisible = ref(false)
const appointmentId = ref('')
const currentStep = ref(1)
const showStickyBtn = ref(false)

const form = reactive({
  customer_name: '',
  phone: '',
  wechat: '',
  house_address: '',
  house_type: '',
  area: '',
  budget: '',
  appointment_date: null,
  appointment_time: '',
  remark: ''
})

const rules = {
  customer_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度2-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  house_address: [
    { required: true, message: '请输入房屋地址', trigger: 'blur' }
  ],
  appointment_date: [
    { required: true, message: '请选择预约日期', trigger: 'change' }
  ],
  appointment_time: [
    { required: true, message: '请选择预约时间', trigger: 'change' }
  ]
}

// 滚动到表单
const scrollToForm = () => {
  document.getElementById('booking-form').scrollIntoView({ behavior: 'smooth' })
}

// 滚动监听：控制 sticky 按钮显隐
const onScroll = () => {
  const heroHeight = window.innerHeight * 0.6
  const formEl = document.getElementById('booking-form')
  const formTop = formEl ? formEl.getBoundingClientRect().top : 9999
  showStickyBtn.value = window.scrollY > heroHeight && formTop > 200
}

// 下一步
const nextStep = async () => {
  let fieldsToValidate = []
  if (currentStep.value === 1) {
    fieldsToValidate = ['customer_name', 'phone']
  } else if (currentStep.value === 2) {
    fieldsToValidate = ['house_address']
  }
  
  if (fieldsToValidate.length > 0) {
    const valid = await formRef.value.validateField(fieldsToValidate).catch(() => false)
    if (!valid) return
  }
  
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      ...form,
      appointment_date: form.appointment_date
    }
    const res = await createAppointment(data)
    appointmentId.value = res.id
    successDialogVisible.value = true
  } catch (error) {
    console.error('预约失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleSuccessClose = () => {
  successDialogVisible.value = false
  router.push('/')
}

// 滚动监听
onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.appointment-page {
  padding-top: 0;
}

/* Hero区域 */
.hero-section {
  position: relative;
  z-index: 1;
  height: calc(100vh - 80px);
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.3) 40%,
    rgba(0, 0, 0, 0.1) 70%,
    transparent 100%
  );
  backdrop-filter: blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
  -webkit-mask: radial-gradient(ellipse at center, black 35%, transparent 85%);
  mask: radial-gradient(ellipse at center, black 35%, transparent 85%);
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: #fff;
  padding: 0 24px;
}

.hero-content h1 {
  font-size: 52px;
  font-weight: 300;
  margin-bottom: 20px;
  letter-spacing: 8px;
}

.hero-subtitle {
  font-size: 24px;
  font-weight: 300;
  opacity: 0.9;
  margin-bottom: 48px;
  letter-spacing: 2px;
}

.hero-features {
  display: flex;
  justify-content: center;
  gap: 64px;
  margin-bottom: 64px;
}

.hero-features .feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.hero-features .feature span {
  font-size: 14px;
  letter-spacing: 2px;
}

.scroll-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.5);
  color: #fff;
  padding: 16px 40px;
  font-size: 14px;
  letter-spacing: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 auto;
  transition: all 0.3s;
}

.scroll-btn:hover {
  background: #fff;
  color: #1a1a1a;
  border-color: #fff;
}

/* 服务特色 */
.features-section {
  padding: 100px 60px;
  background: #fff;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 300;
  color: #1a1a1a;
  margin-bottom: 64px;
  letter-spacing: 8px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

.feature-card {
  text-align: center;
  padding: 40px 24px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
}

.feature-icon {
  width: 80px;
  height: 80px;
  background: #f8f8f8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #1a1a1a;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 400;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.feature-card p {
  font-size: 14px;
  color: #999;
  line-height: 1.8;
}

/* 表单区域 */
.form-section {
  padding: 100px 60px;
  background: #f8f8f8;
}

.form-wrapper {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 64px;
  box-shadow: 0 4px 40px rgba(0,0,0,0.06);
}

.form-header {
  text-align: center;
  margin-bottom: 48px;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 400;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.form-header p {
  color: #999;
  font-size: 14px;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-num {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #999;
  transition: all 0.3s;
}

.step.active .step-num {
  border-color: #1a1a1a;
  background: #1a1a1a;
  color: #fff;
}

.step.completed .step-num {
  border-color: #10b981;
  background: #10b981;
  color: #fff;
}

.step span {
  font-size: 13px;
  color: #999;
}

.step.active span {
  color: #1a1a1a;
}

.step-line {
  width: 80px;
  height: 2px;
  background: #ddd;
  margin: 0 16px;
  margin-bottom: 24px;
}

/* 表单 */
.booking-form :deep(.el-form-item__label) {
  font-size: 14px;
  color: #666;
  font-weight: 400;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.form-actions .el-button {
  min-width: 140px;
  height: 48px;
  font-size: 14px;
  letter-spacing: 2px;
}

.form-actions .el-button--primary {
  background: #1a1a1a;
  border-color: #1a1a1a;
}

.form-actions .el-button--primary:hover {
  background: #333;
  border-color: #333;
}

/* 服务流程 */
.process-section {
  padding: 100px 60px;
  background: #fff;
}

.process-timeline {
  display: flex;
  justify-content: space-between;
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
}

.process-timeline::before {
  content: '';
  position: absolute;
  top: 30px;
  left: 60px;
  right: 60px;
  height: 1px;
  background: #eee;
}

.timeline-item {
  text-align: center;
  flex: 1;
  position: relative;
}

.timeline-icon {
  width: 60px;
  height: 60px;
  background: #fff;
  border: 2px solid #1a1a1a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  position: relative;
  z-index: 1;
}

.timeline-icon span {
  font-size: 16px;
  font-weight: 500;
  color: #1a1a1a;
}

.timeline-content h3 {
  font-size: 18px;
  font-weight: 400;
  margin-bottom: 8px;
  color: #1a1a1a;
}

.timeline-content p {
  font-size: 14px;
  color: #999;
  max-width: 200px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 成功弹窗 */
.success-dialog :deep(.el-dialog__header) {
  display: none;
}

.success-dialog :deep(.el-dialog__body) {
  padding: 40px;
}

.success-content {
  text-align: center;
}

.success-icon {
  margin-bottom: 24px;
}

.success-content h3 {
  font-size: 24px;
  font-weight: 400;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.success-content p {
  color: #666;
  margin-bottom: 24px;
}

.appointment-info {
  background: #f8f8f8;
  padding: 16px 24px;
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
}

.appointment-info span {
  font-size: 12px;
  color: #999;
}

.appointment-info strong {
  font-size: 18px;
  color: #1a1a1a;
  letter-spacing: 2px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .process-timeline {
    flex-direction: column;
    gap: 32px;
  }
  
  .process-timeline::before {
    display: none;
  }
}

@media (max-width: 768px) {
  .appointment-page {
    padding-top: 64px;
  }
  
  .hero-section {
    height: calc(100vh - 64px);
    min-height: 500px;
  }
  
  .hero-content h1 {
    font-size: 36px;
  }
  
  .hero-features {
    flex-direction: column;
    gap: 24px;
  }
  
  .features-section,
  .form-section,
  .process-section {
    padding: 60px 24px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .form-wrapper {
    padding: 40px 24px;
  }
  
  .step-line {
    width: 40px;
  }
}

/* ====================================
   右侧 Sticky 预约按钮
   ==================================== */
.sticky-book-btn {
  position: fixed;
  right: 32px;
  bottom: 80px;
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #8B5A2B 0%, #A0714F 100%);
  color: #fff;
  border: none;
  border-radius: 50px;
  padding: 14px 24px;
  font-size: 14px;
  letter-spacing: 2px;
  font-weight: 400;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(139, 90, 43, 0.4);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  /* H5 特效：脉冲呼吸光晕 */
  animation: stickyPulse 3s ease-in-out infinite;
}

.sticky-book-btn:hover {
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 12px 40px rgba(139, 90, 43, 0.5);
  animation-play-state: paused;
}

.sticky-book-btn:active {
  transform: translateY(0) scale(0.97);
}

.sticky-book-icon {
  font-size: 18px;
  /* 微浮动动画 */
  display: inline-block;
  animation: iconBounce 2.5s ease-in-out infinite;
}

/* 按钮主体脉冲光晕 */
@keyframes stickyPulse {
  0%, 100% {
    box-shadow: 0 8px 32px rgba(139, 90, 43, 0.35),
                0 0 0 0 rgba(139, 90, 43, 0.15);
  }
  50% {
    box-shadow: 0 8px 32px rgba(139, 90, 43, 0.35),
                0 0 0 10px rgba(139, 90, 43, 0);
  }
}

/* 笔图标浮动 */
@keyframes iconBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 淡入淡出过渡 */
.sticky-btn-fade-enter-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.sticky-btn-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.sticky-btn-fade-enter-from,
.sticky-btn-fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 移动端隐藏 */
@media (max-width: 768px) {
  .sticky-book-btn {
    display: none;
  }
}
</style>
