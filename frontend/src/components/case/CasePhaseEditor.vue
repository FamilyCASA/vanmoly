<template>
  <div class="case-phase-editor">
    <el-collapse v-model="activePhase" accordion>
      <!-- 阶段1：户型分析 -->
      <el-collapse-item title="阶段1：户型分析" name="1">
        <PhaseLayoutEditor 
          v-model="phasesData[1]" 
          @update:modelValue="onPhaseUpdate(1, $event)"
        />
      </el-collapse-item>
      
      <!-- 阶段2：设计意境 -->
      <el-collapse-item title="阶段2：设计意境" name="2">
        <PhaseMoodEditor 
          v-model="phasesData[2]"
          @update:modelValue="onPhaseUpdate(2, $event)"
        />
      </el-collapse-item>
      
      <!-- 阶段3：平面规划 -->
      <el-collapse-item title="阶段3：平面优化与规划" name="3">
        <PhasePlanEditor 
          v-model="phasesData[3]"
          @update:modelValue="onPhaseUpdate(3, $event)"
        />
      </el-collapse-item>
      
      <!-- 阶段4：鸟瞰展示 -->
      <el-collapse-item title="阶段4：鸟瞰展示" name="4">
        <PhaseBirdviewEditor 
          v-model="phasesData[4]"
          @update:modelValue="onPhaseUpdate(4, $event)"
        />
      </el-collapse-item>
      
      <!-- 阶段5：效果图首页 -->
      <el-collapse-item title="阶段5：效果图展示首页" name="5">
        <PhaseShowcaseEditor 
          v-model="phasesData[5]"
          @update:modelValue="onPhaseUpdate(5, $event)"
        />
      </el-collapse-item>
      
      <!-- 阶段6：空间效果图 -->
      <el-collapse-item title="阶段6：空间效果图" name="6">
        <PhaseSpaceRenderingsEditor 
          :case-id="caseId"
          :quote-id="quoteId"
        />
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import PhaseLayoutEditor from './phases/PhaseLayoutEditor.vue'
import PhaseMoodEditor from './phases/PhaseMoodEditor.vue'
import PhasePlanEditor from './phases/PhasePlanEditor.vue'
import PhaseBirdviewEditor from './phases/PhaseBirdviewEditor.vue'
import PhaseShowcaseEditor from './phases/PhaseShowcaseEditor.vue'
import PhaseSpaceRenderingsEditor from './phases/PhaseSpaceRenderingsEditor.vue'

const props = defineProps({
  caseId: {
    type: Number,
    required: true
  },
  quoteId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update'])

// 当前展开的阶段
const activePhase = ref('1')

// 阶段数据
const phasesData = ref({
  1: null,
  2: null,
  3: null,
  4: null,
  5: null,
  6: null
})

// 加载阶段数据
const loadPhases = async () => {
  try {
    const res = await request.get(`/cases/${props.caseId}/phases`)
    if (res) {
      // 合并返回的数据
      for (let i = 1; i <= 6; i++) {
        if (res[i]) {
          phasesData.value[i] = res[i]
        }
      }
    }
  } catch (e) {
    console.error('Load phases failed:', e)
  }
}

// 阶段更新
const onPhaseUpdate = async (phaseNum, data) => {
  try {
    await request.put(`/cases/${props.caseId}/phases/${phaseNum}`, data)
    ElMessage.success(`阶段${phaseNum}已保存`)
    emit('update', { phaseNum, data })
  } catch (e) {
    ElMessage.error(`保存失败: ${e.message || e}`)
  }
}

onMounted(() => {
  if (props.caseId) {
    loadPhases()
  }
})

// 监听caseId变化
watch(() => props.caseId, (newId) => {
  if (newId) {
    loadPhases()
  }
})
</script>

<style scoped>
.case-phase-editor {
  width: 100%;
}

:deep(.el-collapse-item__header) {
  font-size: 15px;
  font-weight: 500;
  background-color: #f5f7fa;
  padding-left: 16px;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}
</style>
