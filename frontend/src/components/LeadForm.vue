<template>
  <div class="lead-form">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <div class="form-row">
        <el-form-item label="您的姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
      </div>

      <div class="form-row">
        <el-form-item label="房屋面积" prop="area">
          <el-select v-model="form.area" placeholder="选择面积" style="width: 100%">
            <el-option label="80㎡以下" value="80以下" />
            <el-option label="80-100㎡" value="80-100" />
            <el-option label="100-120㎡" value="100-120" />
            <el-option label="120-150㎡" value="120-150" />
            <el-option label="150㎡以上" value="150以上" />
          </el-select>
        </el-form-item>

        <el-form-item label="装修预算" prop="budget">
          <el-select v-model="form.budget" placeholder="选择预算" style="width: 100%">
            <el-option label="15万以下" value="15万以下" />
            <el-option label="15-20万" value="15-20万" />
            <el-option label="20-30万" value="20-30万" />
            <el-option label="30-50万" value="30-50万" />
            <el-option label="50万以上" value="50万以上" />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="户型" prop="house_type">
        <el-radio-group v-model="form.house_type">
          <el-radio value="一室一厅">一室一厅</el-radio>
          <el-radio value="两室一厅">两室一厅</el-radio>
          <el-radio value="三室一厅">三室一厅</el-radio>
          <el-radio value="三室两厅">三室两厅</el-radio>
          <el-radio value="四室及以上">四室及以上</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="装修意向" prop="intention">
        <el-input
          v-model="form.intention"
          type="textarea"
          :rows="3"
          placeholder="请简单描述您的装修需求..."
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="handleSubmit"
          class="submit-btn"
        >
          {{ submitting ? '提交中...' : '立即获取方案' }}
        </el-button>
      </el-form-item>

      <p class="form-tip">* 提交后专业设计师将在24小时内与您联系</p>
    </el-form>

    <!-- 提交成功弹窗 -->
    <el-dialog
      v-model="successDialogVisible"
      title="提交成功"
      width="400px"
      :show-close="false"
      :close-on-click-modal="false"
      center
    >
      <div class="success-content">
        <el-icon class="success-icon" :size="60" color="#67c23a"><CircleCheck /></el-icon>
        <h3>感谢您的信任！</h3>
        <p>我们的设计师将在24小时内与您联系</p>
        <p class="sub-text">请保持手机畅通</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="successDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck } from '@element-plus/icons-vue'
import { createLead } from '@/api/lead'

const props = defineProps({
  source: {
    type: String,
    default: '网站留资'
  },
  sourceId: {
    type: Number,
    default: null
  }
})

const formRef = ref(null)
const submitting = ref(false)
const successDialogVisible = ref(false)

const form = reactive({
  name: '',
  phone: '',
  area: '',
  budget: '',
  house_type: '',
  intention: ''
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度2-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  area: [
    { required: true, message: '请选择房屋面积', trigger: 'change' }
  ],
  budget: [
    { required: true, message: '请选择装修预算', trigger: 'change' }
  ],
  house_type: [
    { required: true, message: '请选择户型', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      ...form,
      source: props.source,
      source_id: props.sourceId,
      source_page: window.location.pathname
    }
    await createLead(data)
    successDialogVisible.value = true
    // 重置表单
    formRef.value.resetFields()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.lead-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

:deep(.el-form-item__label) {
  color: #fff;
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.form-tip {
  text-align: center;
  color: rgba(255,255,255,0.7);
  font-size: 13px;
  margin-top: 8px;
}

/* 成功弹窗 */
.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  margin-bottom: 16px;
}

.success-content h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #333;
}

.success-content p {
  color: #666;
  margin-bottom: 4px;
}

.success-content .sub-text {
  color: #999;
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
