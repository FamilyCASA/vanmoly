<template>
  <div class="survey-edit">
    <!-- 顶部楼盘信息 -->
    <div class="survey-header">
      <el-page-header @back="goBack" :content="buildingName || '楼盘调查'" />
    </div>

    <div class="survey-body">
      <!-- 左侧导航 -->
      <aside class="survey-sidebar">
        <div
          v-for="group in groups"
          :key="group.key"
          :class="['sidebar-item', { active: activeGroup === group.key }]"
          @click="activeGroup = group.key"
        >
          <span class="sidebar-icon">{{ group.icon }}</span>
          <span class="sidebar-label">{{ group.label }}</span>
        </div>
      </aside>

      <!-- 右侧表单 -->
      <div class="survey-content">
        <!-- 项目概况 -->
        <div v-show="activeGroup === 'overview'" class="form-group">
          <h3 class="group-title">项目概况</h3>
          <el-form :model="form" label-width="100px" label-position="right">
            <el-form-item label="交付时间">
              <el-date-picker
                v-model="form.delivery_date"
                type="date"
                placeholder="选择交付日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="交付数量">
              <el-input-number
                v-model="form.delivery_count"
                :min="0"
                placeholder="交付套数"
                controls-position="right"
              />
              <span class="unit-label">套</span>
            </el-form-item>
            <el-form-item label="保底任务">
              <el-input v-model="form.base_task" placeholder="输入保底任务" />
            </el-form-item>
            <el-form-item label="物业类型">
              <el-select v-model="form.property_category" placeholder="选择物业类型" style="width: 100%">
                <el-option label="住宅" value="住宅" />
                <el-option label="商业" value="商业" />
                <el-option label="商住两用" value="商住两用" />
                <el-option label="别墅" value="别墅" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- 户型分析 -->
        <div v-show="activeGroup === 'unit'" class="form-group">
          <h3 class="group-title">户型分析</h3>
          <el-form :model="form" label-width="100px" label-position="right">
            <el-form-item label="户型面积">
              <el-input v-model="form.unit_area" placeholder="如：80-120" />
              <span class="unit-label">平米</span>
            </el-form-item>
            <el-form-item label="户型数量">
              <el-input-number
                v-model="form.unit_count"
                :min="0"
                placeholder="户型数量"
                controls-position="right"
              />
              <span class="unit-label">种</span>
            </el-form-item>
            <el-form-item label="主力户型">
              <el-input v-model="form.main_unit_type" placeholder="如：三室两厅" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 购房人群 -->
        <div v-show="activeGroup === 'crowd'" class="form-group">
          <h3 class="group-title">购房人群</h3>
          <el-form :model="form" label-width="100px" label-position="right">
            <el-form-item label="18岁以下">
              <el-input-number v-model="form.age_0_18" :min="0" :max="100" controls-position="right" />
              <span class="unit-label">%</span>
            </el-form-item>
            <el-form-item label="19-30岁">
              <el-input-number v-model="form.age_19_30" :min="0" :max="100" controls-position="right" />
              <span class="unit-label">%</span>
            </el-form-item>
            <el-form-item label="31-45岁">
              <el-input-number v-model="form.age_31_45" :min="0" :max="100" controls-position="right" />
              <span class="unit-label">%</span>
            </el-form-item>
            <el-form-item label="46-60岁">
              <el-input-number v-model="form.age_46_60" :min="0" :max="100" controls-position="right" />
              <span class="unit-label">%</span>
            </el-form-item>
            <el-form-item label="60岁以上">
              <el-input-number v-model="form.age_60_plus" :min="0" :max="100" controls-position="right" />
              <span class="unit-label">%</span>
            </el-form-item>

            <!-- 占比求和校验 -->
            <el-form-item label="">
              <div :class="['age-sum-bar', ageSumStatus]">
                <span class="age-sum-label">合计：{{ ageSum }}%</span>
                <span class="age-sum-hint">{{ ageSumHint }}</span>
                <el-progress
                  :percentage="Math.min(ageSum, 100)"
                  :color="ageSumStatus === 'ok' ? '#67c23a' : ageSumStatus === 'warn' ? '#e6a23c' : '#f56c6c'"
                  :stroke-width="8"
                  style="margin-top: 6px"
                />
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 配套设施 -->
        <div v-show="activeGroup === 'facility'" class="form-group">
          <h3 class="group-title">配套设施</h3>
          <el-form :model="form" label-width="100px" label-position="right">
            <el-form-item label="匹配商家">
              <el-input
                v-model="form.matching_shops"
                type="textarea"
                :rows="3"
                placeholder="多个商家用逗号分隔"
              />
            </el-form-item>
            <el-form-item label="地铁配套">
              <el-input v-model="form.metro_info" placeholder="如：地铁1号线XX站" />
            </el-form-item>
            <el-form-item label="公园配套">
              <el-input v-model="form.park_info" placeholder="如：XX公园" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 底部操作栏 -->
        <div class="form-footer">
          <div class="entry-info">
            <span>录入日期：{{ form.entry_date || today }}</span>
            <span style="margin-left: 20px">录入人：{{ form.entry_by || userName }}</span>
          </div>
          <div class="form-actions">
            <el-button @click="resetForm">重置</el-button>
            <el-button type="primary" @click="saveSurvey" :loading="saving">保存</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const buildingId = parseInt(route.params.id)

const buildingName = ref('')
const activeGroup = ref('overview')
const saving = ref(false)

const groups = [
  { key: 'overview', icon: '📋', label: '项目概况' },
  { key: 'unit', icon: '📐', label: '户型分析' },
  { key: 'crowd', icon: '👥', label: '购房人群' },
  { key: 'facility', icon: '🏪', label: '配套设施' }
]

const today = new Date().toISOString().split('T')[0]
const userName = ref('')

const form = ref({
  delivery_date: '',
  delivery_count: null,
  base_task: '',
  property_category: '',
  unit_area: '',
  unit_count: null,
  main_unit_type: '',
  age_0_18: null,
  age_19_30: null,
  age_31_45: null,
  age_46_60: null,
  age_60_plus: null,
  matching_shops: '',
  metro_info: '',
  park_info: '',
  entry_date: today,
  entry_by: ''
})

// 购房人群占比求和
const ageSum = computed(() => {
  const fields = ['age_0_18', 'age_19_30', 'age_31_45', 'age_46_60', 'age_60_plus']
  return fields.reduce((sum, f) => sum + (form.value[f] || 0), 0)
})

const ageSumStatus = computed(() => {
  if (ageSum.value === 0) return 'empty'
  if (Math.abs(ageSum.value - 100) <= 5) return 'ok'
  if (Math.abs(ageSum.value - 100) <= 10) return 'warn'
  return 'error'
})

const ageSumHint = computed(() => {
  if (ageSum.value === 0) return '请填写购房人群占比'
  if (Math.abs(ageSum.value - 100) <= 5) return '符合要求'
  if (ageSum.value < 95) return '占比较低，请检查'
  return '占比过高，请修正'
})

// 获取当前用户
async function fetchCurrentUser() {
  try {
    const res = await request.get('/auth/me')
    userName.value = res.username || res.name || res.data?.username || ''
    form.value.entry_by = userName.value
  } catch (e) {
    // ignore
  }
}

// 获取楼盘名称
async function fetchBuildingInfo() {
  try {
    const res = await request.get(`/buildings/${buildingId}`)
    buildingName.value = res.name || res.data?.name || `楼盘 #${buildingId}`
  } catch (e) {
    buildingName.value = `楼盘 #${buildingId}`
  }
}

// 加载已有调查数据
async function fetchSurvey() {
  try {
    const res = await request.get(`/building-surveys/${buildingId}`)
    const data = res.data || res
    if (data) {
      Object.keys(form.value).forEach(key => {
        if (data[key] !== undefined && data[key] !== null) {
          form.value[key] = data[key]
        }
      })
    }
  } catch (e) {
    // 404 = 尚未录入，正常
  }
}

// 保存
async function saveSurvey() {
  // 前端占比校验
  if (ageSum.value > 0 && Math.abs(ageSum.value - 100) > 5) {
    ElMessage.warning(`购房人群占比合计 ${ageSum}%，偏差超过5%，请检查修正`)
    return
  }

  saving.value = true
  try {
    const payload = { ...form.value, building_id: buildingId }
    // 清理null值
    Object.keys(payload).forEach(k => {
      if (payload[k] === null || payload[k] === undefined) {
        delete payload[k]
      }
    })

    // 判断新建还是更新
    try {
      await request.get(`/building-surveys/${buildingId}`)
      // 已存在 → PUT
      await request.put(`/building-surveys/${buildingId}`, payload)
      ElMessage.success('更新成功')
    } catch (e) {
      if (e.response?.status === 404) {
        // 不存在 → POST
        await request.post('/building-surveys', payload)
        ElMessage.success('保存成功')
      } else {
        throw e
      }
    }
  } catch (e) {
    const msg = e.response?.data?.msg || e.message || '保存失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

function resetForm() {
  form.value = {
    delivery_date: '',
    delivery_count: null,
    base_task: '',
    property_category: '',
    unit_area: '',
    unit_count: null,
    main_unit_type: '',
    age_0_18: null,
    age_19_30: null,
    age_31_45: null,
    age_46_60: null,
    age_60_plus: null,
    matching_shops: '',
    metro_info: '',
    park_info: '',
    entry_date: today,
    entry_by: userName.value
  }
  ElMessage.info('已重置表单')
}

function goBack() {
  router.push('/admin/buildings')
}

onMounted(() => {
  fetchCurrentUser()
  fetchBuildingInfo()
  fetchSurvey()
})
</script>

<style scoped>
.survey-edit {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.survey-header {
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.survey-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧导航 */
.survey-sidebar {
  width: 160px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  padding: 16px 0;
  flex-shrink: 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
  font-size: 14px;
  border-left: 3px solid transparent;
}

.sidebar-item:hover {
  background: #f5f7fa;
  color: #303133;
}

.sidebar-item.active {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
  font-weight: 500;
}

.sidebar-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 右侧内容 */
.survey-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  position: relative;
}

.form-group {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.group-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.unit-label {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

/* 占比求和 */
.age-sum-bar {
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 14px;
  width: 100%;
}

.age-sum-bar.empty {
  background: #f4f4f5;
  color: #909399;
}

.age-sum-bar.ok {
  background: #f0f9eb;
  color: #67c23a;
}

.age-sum-bar.warn {
  background: #fdf6ec;
  color: #e6a23c;
}

.age-sum-bar.error {
  background: #fef0f0;
  color: #f56c6c;
}

.age-sum-label {
  font-weight: 600;
  margin-right: 12px;
}

.age-sum-hint {
  font-size: 13px;
}

/* 底部操作栏 */
.form-footer {
  margin-top: 24px;
  background: #fff;
  border-radius: 8px;
  padding: 16px 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.entry-info {
  color: #909399;
  font-size: 13px;
}

.form-actions {
  display: flex;
  gap: 12px;
}
</style>
