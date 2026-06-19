<template>
  <div class="quote-rules-manage">
    <!-- 报价模板 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>报价模板</span>
          <el-button type="primary" size="small" @click="showTemplateDialog = true">
            <el-icon><Plus /></el-icon> 新建模板
          </el-button>
        </div>
      </template>
      <el-table :data="templates" v-loading="loadingTemplates" stripe>
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="template_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.template_type || '标准' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editTemplate(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteTemplate(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 计量规则 -->
    <el-card shadow="never" class="section-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>计量规则 <el-tag size="small" type="info">{{ measurementRules.length }}条</el-tag></span>
          <el-button type="primary" size="small" @click="openNewRule">
            <el-icon><Plus /></el-icon> 新建规则
          </el-button>
        </div>
      </template>
      <el-table :data="measurementRules" v-loading="loadingRules" stripe>
        <el-table-column prop="name" label="规则名称" width="160" />
        <el-table-column prop="calc_mode" label="计算模式" width="120">
          <template #default="{ row }">
            <el-tag :type="calcModeTag(row.calc_mode)" size="small">
              {{ calcModeName(row.calc_mode) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="formula" label="公式" width="200" show-overflow-tooltip />
        <el-table-column label="匹配条件" min-width="200">
          <template #default="{ row }">
            <div v-if="row.match_conditions && row.match_conditions.length">
              <el-tag v-for="(c, i) in row.match_conditions" :key="i" size="small" style="margin: 2px">
                {{ fieldLabel(c.field) }} {{ opLabel(c.op) }} {{ c.value }}
              </el-tag>
            </div>
            <span v-else style="color: #999">无条件（匹配所有）</span>
          </template>
        </el-table-column>
        <el-table-column prop="coefficient" label="系数" width="70" align="right">
          <template #default="{ row }">{{ row.coefficient != null && row.coefficient !== 1 ? row.coefficient : '-' }}</template>
        </el-table-column>
        <el-table-column prop="min_value" label="最小值" width="80" align="right">
          <template #default="{ row }">{{ row.min_value || '-' }}</template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" @change="toggleRule(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editRule(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 模板编辑对话框 -->
    <el-dialog v-model="showTemplateDialog" :title="editingTemplate ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="templateForm.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="templateForm.template_type" placeholder="选择类型" style="width: 100%">
            <el-option label="标准" value="标准" />
            <el-option label="定制" value="定制" />
            <el-option label="优惠" value="优惠" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" :rows="3" placeholder="模板说明" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="templateForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate" :loading="savingTemplate">保存</el-button>
      </template>
    </el-dialog>

    <!-- 规则编辑对话框 (v2 参数化) -->
    <el-dialog v-model="showRuleDialog" :title="editingRule ? '编辑规则' : '新建规则'" width="850px" top="5vh">
      <el-form :model="ruleForm" label-width="110px" class="rule-form">
        
        <!-- 基本信息 -->
        <el-divider content-position="left">📋 基本信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="规则名称" required>
              <el-input v-model="ruleForm.name" placeholder="如：长度计量" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="说明">
              <el-input v-model="ruleForm.description" placeholder="规则说明" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 匹配条件区 -->
        <el-divider content-position="left">📌 匹配条件（满足所有条件才生效）</el-divider>
        <div v-for="(cond, idx) in ruleForm.match_conditions" :key="idx" class="condition-row">
          <el-row :gutter="8" align="middle">
            <el-col :span="7">
              <el-select v-model="cond.field" placeholder="匹配字段" style="width: 100%">
                <el-option label="物料名称" value="name" />
                <el-option label="自定义名称" value="custom_name" />
                <el-option label="二级分类" value="category_level2" />
                <el-option label="单位分类" value="unit_category" />
                <el-option label="工艺名称" value="process_name" />
                <el-option label="单位" value="unit" />
              </el-select>
            </el-col>
            <el-col :span="5">
              <el-select v-model="cond.op" placeholder="匹配方式" style="width: 100%">
                <el-option label="包含" value="contains" />
                <el-option label="等于" value="equals" />
              </el-select>
            </el-col>
            <el-col :span="9">
              <el-input v-model="cond.value" placeholder="匹配值（多个用逗号分隔）" />
            </el-col>
            <el-col :span="3">
              <el-button type="danger" link @click="removeCondition(idx)" :disabled="ruleForm.match_conditions.length <= 1">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" link size="small" @click="addCondition" style="margin-top: 8px">
          <el-icon><Plus /></el-icon> 添加条件
        </el-button>
        <div v-if="ruleForm.match_conditions.length === 0" style="color: #909399; font-size: 13px; margin-top: 4px">
          💡 无条件 = 对所有物料生效
        </div>

        <!-- 计量值计算区 -->
        <el-divider content-position="left">🔢 计量值计算</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="计算模式">
              <el-select v-model="ruleForm.calc_mode" placeholder="选择模式" style="width: 100%">
                <el-option label="按长度 (max/1000)" value="length" />
                <el-option label="按面积 (w×h/1M)" value="area" />
                <el-option label="按体积 (w×d×h/1B)" value="volume" />
                <el-option label="按数量 (固定1)" value="quantity" />
                <el-option label="投影高度补足" value="adjust_height" />
                <el-option label="面积保底" value="adjust_min_area" />
                <el-option label="门套/垭口套" value="door_frame" />
                <el-option label="四方轮廓" value="four_sided" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="系数">
              <el-input-number v-model="ruleForm.coefficient" :min="0" :precision="3" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="最小值">
              <el-input-number v-model="ruleForm.min_value" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="计量单位">
              <el-input v-model="ruleForm.unit" placeholder="如：米、㎡" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="公式说明">
          <el-input v-model="ruleForm.formula" placeholder="如：宽 × 高 × 单价" />
        </el-form-item>

        <!-- 金额参数区 -->
        <el-divider content-position="left">💰 金额计算参数</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="工艺系数">
              <el-input-number v-model="ruleForm.process_coefficient_override" :precision="3" :step="0.1" :min="0"
                placeholder="留空=不覆盖" style="width: 100%" />
              <div class="field-hint">留空=用物料自身值；填0=强制归零</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工艺数量">
              <el-input-number v-model="ruleForm.process_qty_override" :precision="2" :step="1" :min="0"
                placeholder="留空=不覆盖" style="width: 100%" />
              <div class="field-hint">留空=用物料自身值</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工艺单价">
              <el-input-number v-model="ruleForm.process_price_override" :precision="2" :step="10" :min="0"
                placeholder="留空=不覆盖" style="width: 100%" />
              <div class="field-hint">留空=用物料自身值</div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="金额公式">
          <el-input v-model="ruleForm.amount_formula" placeholder="如：qty × mval × coef × price + pqty × pprice" />
        </el-form-item>

        <!-- 控制参数 -->
        <el-divider content-position="left">⚙️ 控制参数</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-input-number v-model="ruleForm.priority" :min="1" :max="999" style="width: 100%" />
              <div class="field-hint">数字越小越优先</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用状态">
              <el-switch v-model="ruleForm.is_enabled" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showRuleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="savingRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const templates = ref([])
const measurementRules = ref([])
const loadingTemplates = ref(false)
const loadingRules = ref(false)
const savingTemplate = ref(false)
const savingRule = ref(false)

const showTemplateDialog = ref(false)
const showRuleDialog = ref(false)
const editingTemplate = ref(null)
const editingRule = ref(null)

const templateForm = ref({
  name: '',
  template_type: '标准',
  description: '',
  is_active: true
})

const defaultRuleForm = () => ({
  name: '',
  description: '',
  calc_mode: 'length',
  match_conditions: [{ field: 'unit_category', op: 'equals', value: 'length' }],
  formula: '',
  unit: '',
  coefficient: 1,
  min_value: 0,
  process_coefficient_override: null,
  process_qty_override: null,
  process_price_override: null,
  amount_formula: '',
  priority: 100,
  is_enabled: true
})

const ruleForm = ref(defaultRuleForm())

// 计算模式
const calcModeMap = {
  length: '按长度',
  area: '按面积',
  volume: '按体积',
  quantity: '按数量',
  adjust_height: '投影补足',
  adjust_min_area: '面积保底',
  door_frame: '门套',
  four_sided: '四方'
}
const calcModeName = (m) => calcModeMap[m] || m
const calcModeTag = (m) => {
  const map = { length: 'primary', area: 'success', volume: 'warning', quantity: 'info',
    adjust_height: 'danger', adjust_min_area: 'danger', door_frame: 'primary', four_sided: 'success' }
  return map[m] || 'info'
}

// 字段/操作标签
const fieldLabel = (f) => {
  const m = { name: '物料名', custom_name: '自定义名', category_level2: '二级分类',
    unit_category: '单位分类', process_name: '工艺名', unit: '单位' }
  return m[f] || f
}
const opLabel = (o) => o === 'equals' ? '=' : '≈'

const addCondition = () => {
  ruleForm.value.match_conditions.push({ field: 'name', op: 'contains', value: '' })
}
const removeCondition = (idx) => {
  ruleForm.value.match_conditions.splice(idx, 1)
}

const openNewRule = () => {
  editingRule.value = null
  ruleForm.value = defaultRuleForm()
  showRuleDialog.value = true
}

const fetchTemplates = async () => {
  loadingTemplates.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v3/quotes/templates', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    templates.value = data.data || []
  } catch (err) {
    console.error('获取模板失败:', err)
  } finally {
    loadingTemplates.value = false
  }
}

const fetchRules = async () => {
  loadingRules.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v3/quotes/measurement-rules', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    measurementRules.value = data.data || []
  } catch (err) {
    console.error('获取规则失败:', err)
  } finally {
    loadingRules.value = false
  }
}

const editTemplate = (row) => {
  editingTemplate.value = row
  templateForm.value = { ...row }
  showTemplateDialog.value = true
}

const deleteTemplate = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该模板？', '提示', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v3/quotes/templates/${row.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (data.code === 200 || data.code === 2000) {
      ElMessage.success('删除成功')
      fetchTemplates()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (err) {
    if (err !== 'cancel') console.error(err)
  }
}

const saveTemplate = async () => {
  if (!templateForm.value.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  savingTemplate.value = true
  try {
    const token = localStorage.getItem('token')
    const url = editingTemplate.value
      ? `/api/v3/quotes/templates/${editingTemplate.value.id}`
      : '/api/v3/quotes/templates'
    const method = editingTemplate.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(templateForm.value)
    })
    const data = await res.json()
    if (data.code === 200 || data.code === 2000) {
      ElMessage.success('保存成功')
      showTemplateDialog.value = false
      editingTemplate.value = null
      fetchTemplates()
    } else {
      ElMessage.error(data.message || '保存失败')
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('保存失败')
  } finally {
    savingTemplate.value = false
  }
}

const editRule = (row) => {
  editingRule.value = row
  ruleForm.value = {
    name: row.name || '',
    description: row.description || '',
    calc_mode: row.calc_mode || row.rule_type || 'length',
    match_conditions: (row.match_conditions && row.match_conditions.length)
      ? row.match_conditions.map(c => ({ ...c }))
      : [{ field: 'unit_category', op: 'equals', value: 'length' }],
    formula: row.formula || '',
    unit: row.unit || '',
    coefficient: row.coefficient ?? 1,
    min_value: row.min_value ?? 0,
    process_coefficient_override: row.process_coefficient_override ?? null,
    process_qty_override: row.process_qty_override ?? null,
    process_price_override: row.process_price_override ?? null,
    amount_formula: row.amount_formula || '',
    priority: row.priority ?? 100,
    is_enabled: row.is_enabled ?? true
  }
  showRuleDialog.value = true
}

const deleteRule = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该规则？', '提示', { type: 'warning' })
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v3/quotes/measurement-rules/${row.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    if (data.code === 200 || data.code === 2000) {
      ElMessage.success('删除成功')
      fetchRules()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (err) {
    if (err !== 'cancel') console.error(err)
  }
}

const saveRule = async () => {
  if (!ruleForm.value.name) {
    ElMessage.warning('请填写规则名称')
    return
  }
  // 过滤掉空条件
  const cleanConditions = (ruleForm.value.match_conditions || []).filter(c => c.value && c.value.trim())
  
  const payload = {
    ...ruleForm.value,
    match_conditions: cleanConditions,
    // null 表示不覆盖
    process_coefficient_override: ruleForm.value.process_coefficient_override ?? null,
    process_qty_override: ruleForm.value.process_qty_override ?? null,
    process_price_override: ruleForm.value.process_price_override ?? null,
  }
  
  savingRule.value = true
  try {
    const token = localStorage.getItem('token')
    const url = editingRule.value
      ? `/api/v3/quotes/measurement-rules/${editingRule.value.id}`
      : '/api/v3/quotes/measurement-rules'
    const method = editingRule.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.code === 200 || data.code === 2000) {
      ElMessage.success('保存成功')
      showRuleDialog.value = false
      editingRule.value = null
      fetchRules()
    } else {
      ElMessage.error(data.message || '保存失败')
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('保存失败')
  } finally {
    savingRule.value = false
  }
}

const toggleRule = async (row) => {
  try {
    const token = localStorage.getItem('token')
    await fetch(`/api/v3/quotes/measurement-rules/${row.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_enabled: row.is_enabled })
    })
    ElMessage.success(row.is_enabled ? '已启用' : '已禁用')
  } catch (err) {
    console.error(err)
    row.is_enabled = !row.is_enabled
  }
}

onMounted(() => {
  fetchTemplates()
  fetchRules()
})
</script>

<style scoped>
.quote-rules-manage {
  padding: 0;
}

.section-card {
  border: 1px solid #f0f0f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rule-form :deep(.el-divider__text) {
  font-weight: 600;
  font-size: 14px;
}

.condition-row {
  margin-bottom: 8px;
}

.field-hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}
</style>
