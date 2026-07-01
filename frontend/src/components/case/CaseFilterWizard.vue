<template>
  <div class="filter-wizard">
    <!-- 步骤指示器 -->
    <div class="wizard-steps" v-if="currentStep < 4">
      <div class="step-indicator">
        <span class="step-dot" :class="{ active: currentStep >= 1, current: currentStep === 1 }">1</span>
        <span class="step-line" :class="{ active: currentStep >= 2 }"></span>
        <span class="step-dot" :class="{ active: currentStep >= 2, current: currentStep === 2 }">2</span>
        <span class="step-line" :class="{ active: currentStep >= 3 }"></span>
        <span class="step-dot" :class="{ active: currentStep >= 3, current: currentStep === 3 }">3</span>
      </div>
      <div class="step-labels">
        <span :class="{ active: currentStep === 1 }">选择阶段</span>
        <span :class="{ active: currentStep === 2 }">预算范围</span>
        <span :class="{ active: currentStep === 3 }">风格偏好</span>
      </div>
    </div>

    <!-- 步骤 1: 服务阶段 -->
    <div v-if="currentStep === 1" class="wizard-step">
      <h3 class="step-title">您目前处于哪个阶段？</h3>
      <p class="step-desc">选择您当前的服务阶段，我们将为您推荐相关案例</p>
      
      <div class="stage-options">
        <div
          v-for="stage in stages"
          :key="stage.value"
          class="stage-card"
          :class="{ selected: selectedStage === stage.value }"
          @click="selectStage(stage.value)"
        >
          <div class="stage-icon">{{ stage.icon }}</div>
          <div class="stage-info">
            <span class="stage-name">{{ stage.label }}</span>
            <span class="stage-desc">{{ stage.desc }}</span>
          </div>
          <div class="stage-count" v-if="stage.count">{{ stage.count }}个案例</div>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn-skip" @click="skipToResults">跳过向导，查看全部</button>
        <button class="btn-next" :disabled="!selectedStage" @click="goToStep(2)">
          下一步 <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
    </div>

    <!-- 步骤 2: 预算范围 -->
    <div v-if="currentStep === 2" class="wizard-step">
      <h3 class="step-title">您的预算范围是？</h3>
      <p class="step-desc">选择预算区间，精准匹配适合您的案例</p>
      
      <div class="budget-options">
        <button
          v-for="budget in budgets"
          :key="budget.value"
          class="budget-btn"
          :class="{ selected: selectedBudget === budget.value }"
          @click="selectBudget(budget.value)"
        >
          <span class="budget-label">{{ budget.label }}</span>
          <span class="budget-count" v-if="budget.count">{{ budget.count }}个</span>
        </button>
      </div>

      <div class="step-actions">
        <button class="btn-back" @click="goToStep(1)">
          <el-icon><ArrowLeft /></el-icon> 上一步
        </button>
        <button class="btn-next" @click="goToStep(3)">
          下一步 <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
    </div>

    <!-- 步骤 3: 风格偏好 -->
    <div v-if="currentStep === 3" class="wizard-step">
      <h3 class="step-title">您偏好哪种风格？</h3>
      <p class="step-desc">选择您喜欢的空间氛围，发现心仪案例</p>
      
      <div class="style-options">
        <div
          v-for="style in styles"
          :key="style.value"
          class="style-card"
          :class="{ selected: selectedStyle === style.value }"
          @click="selectStyle(style.value)"
          :style="{ background: style.gradient }"
        >
          <span class="style-name">{{ style.label }}</span>
          <span class="style-count" v-if="style.count">{{ style.count }}个</span>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn-back" @click="goToStep(2)">
          <el-icon><ArrowLeft /></el-icon> 上一步
        </button>
        <button class="btn-primary" @click="finishWizard">
          查看匹配结果
        </button>
      </div>
    </div>

    <!-- 结果展示 + 筛选摘要 -->
    <div v-if="currentStep === 4" class="wizard-results">
      <div class="filter-summary">
        <span class="summary-title">筛选条件</span>
        <div class="summary-tags">
          <span class="tag" v-if="selectedStage">
            {{ getStageLabel(selectedStage) }}
            <el-icon @click="clearFilter('stage')"><Close /></el-icon>
          </span>
          <span class="tag" v-if="selectedBudget">
            {{ getBudgetLabel(selectedBudget) }}
            <el-icon @click="clearFilter('budget')"><Close /></el-icon>
          </span>
          <span class="tag" v-if="selectedStyle">
            {{ getStyleLabel(selectedStyle) }}
            <el-icon @click="clearFilter('style')"><Close /></el-icon>
          </span>
          <button class="btn-reset" @click="resetWizard">重新筛选</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowRight, ArrowLeft, Close } from '@element-plus/icons-vue'

const props = defineProps({
  stages: {
    type: Array,
    default: () => []
  },
  budgets: {
    type: Array,
    default: () => []
  },
  styles: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['filter-change', 'skip', 'reset'])

const currentStep = ref(1)
const selectedStage = ref('')
const selectedBudget = ref('')
const selectedStyle = ref('')

const selectStage = (value) => {
  selectedStage.value = value
}

const selectBudget = (value) => {
  selectedBudget.value = value
}

const selectStyle = (value) => {
  selectedStyle.value = value
}

const goToStep = (step) => {
  currentStep.value = step
}

const finishWizard = () => {
  currentStep.value = 4
  emitFilterChange()
}

const skipToResults = () => {
  currentStep.value = 4
  emit('skip')
}

const resetWizard = () => {
  currentStep.value = 1
  selectedStage.value = ''
  selectedBudget.value = ''
  selectedStyle.value = ''
  emit('reset')
}

const clearFilter = (type) => {
  if (type === 'stage') selectedStage.value = ''
  if (type === 'budget') selectedBudget.value = ''
  if (type === 'style') selectedStyle.value = ''
  emitFilterChange()
}

const emitFilterChange = () => {
  emit('filter-change', {
    stage: selectedStage.value,
    budget: selectedBudget.value,
    style: selectedStyle.value
  })
}

const getStageLabel = (value) => {
  const stage = props.stages.find(s => s.value === value)
  return stage?.label || value
}

const getBudgetLabel = (value) => {
  const budget = props.budgets.find(b => b.value === value)
  return budget?.label || value
}

const getStyleLabel = (value) => {
  const style = props.styles.find(s => s.value === value)
  return style?.label || value
}

watch([selectedStage, selectedBudget, selectedStyle], emitFilterChange, { deep: true })
</script>

<style scoped>
.filter-wizard {
  background: var(--bg-surface, #1a1a2e);
  border-radius: 12px;
  padding: 24px 32px;
  margin: 20px 24px;
  border: 1px solid var(--border, #2a2a3e);
}

/* 步骤指示器 */
.wizard-steps {
  margin-bottom: 32px;
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.step-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-elevated, #2a2a3e);
  color: var(--text-secondary, #A0A0B8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step-dot.active {
  background: var(--primary, #409EFF);
  color: #fff;
}

.step-dot.current {
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.step-line {
  width: 60px;
  height: 2px;
  background: var(--bg-elevated, #2a2a3e);
  transition: all 0.3s ease;
}

.step-line.active {
  background: var(--primary, #409EFF);
}

.step-labels {
  display: flex;
  justify-content: center;
  gap: 48px;
  font-size: 12px;
  color: var(--text-secondary, #A0A0B8);
}

.step-labels span.active {
  color: var(--primary, #409EFF);
  font-weight: 500;
}

/* 步骤内容 */
.wizard-step {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-title, #FFFFFF);
  margin: 0 0 8px;
  text-align: center;
}

.step-desc {
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
  margin: 0 0 24px;
  text-align: center;
}

/* 阶段选项 */
.stage-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stage-card {
  background: var(--bg-elevated, #2a2a3e);
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
}

.stage-card:hover {
  border-color: rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.stage-card.selected {
  border-color: var(--primary, #409EFF);
  background: rgba(64, 158, 255, 0.1);
}

.stage-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.stage-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stage-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-title, #FFFFFF);
}

.stage-desc {
  font-size: 12px;
  color: var(--text-secondary, #A0A0B8);
}

.stage-count {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 11px;
  color: var(--primary, #409EFF);
  background: rgba(64, 158, 255, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
}

/* 预算选项 */
.budget-options {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.budget-btn {
  background: var(--bg-elevated, #2a2a3e);
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 100px;
}

.budget-btn:hover {
  border-color: rgba(64, 158, 255, 0.3);
}

.budget-btn.selected {
  border-color: var(--primary, #409EFF);
  background: rgba(64, 158, 255, 0.1);
}

.budget-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-title, #FFFFFF);
}

.budget-count {
  font-size: 12px;
  color: var(--text-secondary, #A0A0B8);
}

/* 风格选项 */
.style-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.style-card {
  border: 3px solid transparent;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
}

.style-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.style-card.selected {
  border-color: var(--primary, #409EFF);
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
}

.style-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.style-card:last-child .style-name {
  color: #fff;
  text-shadow: none;
}

.style-count {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.5);
}

.style-card:last-child .style-count {
  color: rgba(255, 255, 255, 0.7);
}

/* 按钮 */
.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--border, #2a2a3e);
}

.btn-skip {
  background: transparent;
  border: none;
  color: var(--text-secondary, #A0A0B8);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  transition: color 0.3s;
}

.btn-skip:hover {
  color: var(--text-title, #FFFFFF);
}

.btn-back {
  background: var(--bg-elevated, #2a2a3e);
  border: none;
  color: var(--text-title, #FFFFFF);
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: var(--bg-hover, #3a3a4e);
}

.btn-next, .btn-primary {
  background: var(--primary, #409EFF);
  border: none;
  color: #fff;
  font-size: 14px;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.btn-next:hover, .btn-primary:hover {
  background: var(--primary-dark, #2a6cb0);
}

.btn-next:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 结果摘要 */
.wizard-results {
  animation: fadeIn 0.3s ease;
}

.filter-summary {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.summary-title {
  font-size: 14px;
  color: var(--text-secondary, #A0A0B8);
}

.summary-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: rgba(64, 158, 255, 0.15);
  color: var(--primary, #409EFF);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag .el-icon {
  cursor: pointer;
  font-size: 12px;
}

.btn-reset {
  background: transparent;
  border: 1px solid var(--border, #2a2a3e);
  color: var(--text-secondary, #A0A0B8);
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-reset:hover {
  border-color: var(--primary, #409EFF);
  color: var(--primary, #409EFF);
}

/* 响应式 */
@media (max-width: 768px) {
  .filter-wizard {
    padding: 20px;
    margin: 16px;
  }

  .stage-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .style-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .budget-options {
    gap: 8px;
  }

  .budget-btn {
    padding: 12px 16px;
    min-width: 80px;
  }

  .step-labels {
    gap: 24px;
  }
}
</style>
