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
          <el-button type="primary" size="small" @click="showRuleDialog = true">
            <el-icon><Plus /></el-icon> 新建规则
          </el-button>
        </div>
      </template>
      <el-table :data="measurementRules" v-loading="loadingRules" stripe>
        <el-table-column prop="name" label="规则名称" width="180" />
        <el-table-column prop="rule_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="ruleTypeTag(row.rule_type)" size="small">
              {{ ruleTypeName(row.rule_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
        <el-table-column prop="formula" label="公式" width="200" show-overflow-tooltip />
        <el-table-column prop="is_enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" @change="toggleRule(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
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

    <!-- 规则编辑对话框 -->
    <el-dialog v-model="showRuleDialog" :title="editingRule ? '编辑规则' : '新建规则'" width="700px">
      <el-form :model="ruleForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="规则名称" required>
              <el-input v-model="ruleForm.name" placeholder="输入规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则类型" required>
              <el-select v-model="ruleForm.rule_type" placeholder="选择类型" style="width: 100%">
                <el-option label="按长度" value="length" />
                <el-option label="按面积" value="area" />
                <el-option label="按体积" value="volume" />
                <el-option label="投影面积" value="projection" />
                <el-option label="柜门" value="cabinet_door" />
                <el-option label="门套" value="door_frame" />
                <el-option label="垭口套" value="bay_frame" />
                <el-option label="四方" value="four_side" />
                <el-option label="赠送" value="gift" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="说明">
              <el-input v-model="ruleForm.description" placeholder="规则说明" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="计算公式">
              <el-input v-model="ruleForm.formula" placeholder="如: 宽 * 高 * 单价" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="ruleForm.unit" placeholder="计量单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="系数">
              <el-input-number v-model="ruleForm.coefficient" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最小值">
              <el-input-number v-model="ruleForm.min_value" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
import { Plus } from '@element-plus/icons-vue'

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

const ruleForm = ref({
  name: '',
  rule_type: 'area',
  description: '',
  formula: '',
  unit: '',
  coefficient: 1,
  min_value: 0,
  is_enabled: true
})

const ruleTypeMap = {
  length: '按长度',
  area: '按面积',
  volume: '按体积',
  projection: '投影面积',
  cabinet_door: '柜门',
  door_frame: '门套',
  bay_frame: '垭口套',
  four_side: '四方',
  gift: '赠送'
}

const ruleTypeTag = (type) => {
  const map = {
    length: 'primary',
    area: 'success',
    volume: 'warning',
    projection: 'info',
    cabinet_door: 'danger',
    door_frame: 'primary',
    bay_frame: 'warning',
    four_side: 'success',
    gift: 'info'
  }
  return map[type] || 'info'
}

const ruleTypeName = (type) => ruleTypeMap[type] || type

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
  ruleForm.value = { ...row }
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
  if (!ruleForm.value.name || !ruleForm.value.rule_type) {
    ElMessage.warning('请填写规则名称和类型')
    return
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
      body: JSON.stringify(ruleForm.value)
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
</style>
