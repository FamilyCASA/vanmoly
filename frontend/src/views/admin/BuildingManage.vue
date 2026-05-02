<template>
  <div class="building-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>楼盘管理</h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新建楼盘
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">总楼盘</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card success">
          <div class="stat-value">{{ stats.cooperating || 0 }}</div>
          <div class="stat-label">合作中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card warning">
          <div class="stat-value">{{ stats.by_status?.contacting || 0 }}</div>
          <div class="stat-label">接洽中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.new_this_month || 0 }}</div>
          <div class="stat-label">本月新增</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="楼盘名称/地址" clearable />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="filterForm.city" placeholder="输入城市" clearable />
        </el-form-item>
        <el-form-item label="合作状态">
          <el-select v-model="filterForm.cooperation_status" placeholder="全部状态" clearable>
            <el-option v-for="s in options.cooperation_status" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="物业类型">
          <el-select v-model="filterForm.property_type" placeholder="全部类型" clearable>
            <el-option v-for="t in options.property_types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 楼盘列表 -->
    <el-card shadow="never">
      <el-table :data="buildings" v-loading="loading" stripe>
        <el-table-column label="楼盘名称" min-width="200">
          <template #default="{ row }">
            <div class="building-name">{{ row.name }}</div>
            <div class="building-address">{{ row.address }}</div>
          </template>
        </el-table-column>

        <el-table-column label="位置" width="150">
          <template #default="{ row }">
            {{ row.city }}{{ row.district ? ' · ' + row.district : '' }}
          </template>
        </el-table-column>

        <el-table-column label="开发商/物业" min-width="150">
          <template #default="{ row }">
            <div>{{ row.developer || '-' }}</div>
            <div class="property-company">{{ row.property_company || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="物业类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ propertyTypeLabel(row.property_type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="合作状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="cooperationType(row.cooperation_status)" size="small">
              {{ cooperationLabel(row.cooperation_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="联系人" width="150">
          <template #default="{ row }">
            <div>{{ row.contact_name || '-' }}</div>
            <div class="contact-phone">{{ row.contact_phone || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="openFollowDialog(row)">跟进</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 楼盘表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑楼盘' : '新建楼盘'"
      width="700px"
    >
      <el-form :model="form" label-width="100px">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-form-item label="楼盘名称" required>
              <el-input v-model="form.name" />
            </el-form-item>

            <el-form-item label="别名">
              <el-input v-model="form.alias" placeholder="如有多个名称" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="省">
                  <el-input v-model="form.province" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="市">
                  <el-input v-model="form.city" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="区/县">
                  <el-input v-model="form.district" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="详细地址">
              <el-input v-model="form.address" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="开发商">
                  <el-input v-model="form.developer" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="物业公司">
                  <el-input v-model="form.property_company" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="建成年份">
                  <el-input-number v-model="form.build_year" :min="1900" :max="2100" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="总户数">
                  <el-input-number v-model="form.total_houses" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="物业类型">
                  <el-select v-model="form.property_type" style="width: 100%">
                    <el-option v-for="t in options.property_types" :key="t.value" :label="t.label" :value="t.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="合作信息" name="cooperation">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="合作状态">
                  <el-select v-model="form.cooperation_status" style="width: 100%">
                    <el-option v-for="s in options.cooperation_status" :key="s.value" :label="s.label" :value="s.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="合作类型">
                  <el-select v-model="form.cooperation_type" style="width: 100%">
                    <el-option v-for="t in options.cooperation_types" :key="t.value" :label="t.label" :value="t.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="联系人">
                  <el-input v-model="form.contact_name" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="联系电话">
                  <el-input v-model="form.contact_phone" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="职位">
                  <el-input v-model="form.contact_position" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="合作开始">
                  <el-date-picker v-model="form.cooperation_start_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="合作结束">
                  <el-date-picker v-model="form.cooperation_end_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="合作条款">
              <el-input v-model="form.cooperation_terms" type="textarea" :rows="3" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 跟进对话框 -->
    <el-dialog v-model="followDialog.visible" title="楼盘跟进" width="600px">
      <el-form :model="followForm" label-width="100px">
        <el-form-item label="跟进类型">
          <el-select v-model="followForm.follow_type" style="width: 100%">
            <el-option v-for="t in options.follow_types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="联系人">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input v-model="followForm.contact_name" placeholder="姓名" />
            </el-col>
            <el-col :span="12">
              <el-input v-model="followForm.contact_phone" placeholder="电话" />
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item label="跟进内容">
          <el-input v-model="followForm.content" type="textarea" :rows="4" />
        </el-form-item>

        <el-form-item label="跟进结果">
          <el-select v-model="followForm.result" style="width: 100%">
            <el-option v-for="r in options.follow_results" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="下次跟进">
          <el-date-picker v-model="followForm.next_follow_at" type="datetime" style="width: 100%" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="followDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="addFollow" :loading="followDialog.loading">添加</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="60%">
      <div v-if="detailDrawer.building" class="building-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="楼盘名称">{{ detailDrawer.building.name }}</el-descriptions-item>
          <el-descriptions-item label="别名">{{ detailDrawer.building.alias || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ detailDrawer.building.address }}</el-descriptions-item>
          <el-descriptions-item label="开发商">{{ detailDrawer.building.developer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="物业公司">{{ detailDrawer.building.property_company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="合作状态">
            <el-tag :type="cooperationType(detailDrawer.building.cooperation_status)">
              {{ cooperationLabel(detailDrawer.building.cooperation_status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 跟进记录 -->
        <div class="section">
          <h4>跟进记录</h4>
          <el-timeline>
            <el-timeline-item
              v-for="f in detailDrawer.building.follows"
              :key="f.id"
              :timestamp="formatDateTime(f.created_at)"
            >
              <el-card size="small">
                <div class="follow-header">
                  <el-tag size="small">{{ followTypeLabel(f.follow_type) }}</el-tag>
                  <span class="operator">{{ f.operator_name }}</span>
                  <el-tag v-if="f.result" :type="followResultType(f.result)" size="small">
                    {{ followResultLabel(f.result) }}
                  </el-tag>
                </div>
                <div class="follow-content">{{ f.content }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="!detailDrawer.building.follows?.length" description="暂无跟进记录" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const buildings = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const activeTab = ref('basic')

const filterForm = reactive({
  keyword: '',
  city: '',
  cooperation_status: '',
  property_type: ''
})

const options = reactive({
  cooperation_status: [],
  cooperation_types: [],
  property_types: [],
  follow_types: [],
  follow_results: []
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  name: '',
  alias: '',
  province: '',
  city: '',
  district: '',
  address: '',
  developer: '',
  property_company: '',
  build_year: null,
  total_houses: null,
  property_type: '',
  cooperation_status: 'none',
  cooperation_type: '',
  contact_name: '',
  contact_phone: '',
  contact_position: '',
  cooperation_start_date: null,
  cooperation_end_date: null,
  cooperation_terms: ''
})

const followDialog = reactive({
  visible: false,
  loading: false,
  buildingId: null
})

const followForm = reactive({
  follow_type: 'visit',
  content: '',
  contact_name: '',
  contact_phone: '',
  result: '',
  next_follow_at: null
})

const detailDrawer = reactive({
  visible: false,
  title: '',
  building: null
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/buildings', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        city: filterForm.city,
        cooperation_status: filterForm.cooperation_status,
        property_type: filterForm.property_type
      }
    })
    buildings.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await request.get('/buildings/statistics')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadOptions = async () => {
  try {
    const res = await request.get('/buildings/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.city = ''
  filterForm.cooperation_status = ''
  filterForm.property_type = ''
  loadData()
}

// 表单操作
const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.visible = true
  activeTab.value = 'basic'
  Object.assign(form, {
    id: null,
    name: '',
    alias: '',
    province: '',
    city: '',
    district: '',
    address: '',
    developer: '',
    property_company: '',
    build_year: null,
    total_houses: null,
    property_type: '',
    cooperation_status: 'none',
    cooperation_type: '',
    contact_name: '',
    contact_phone: '',
    contact_position: '',
    cooperation_start_date: null,
    cooperation_end_date: null,
    cooperation_terms: ''
  })
}

const openEditDialog = (row) => {
  dialog.isEdit = true
  dialog.visible = true
  activeTab.value = 'basic'
  Object.assign(form, row)
}

const handleSubmit = async () => {
  if (!form.name) {
    ElMessage.warning('请输入楼盘名称')
    return
  }

  dialog.loading = true
  try {
    if (dialog.isEdit) {
      await request.put(`/buildings/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/buildings', form)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    dialog.loading = false
  }
}

// 跟进
const openFollowDialog = (row) => {
  followDialog.buildingId = row.id
  followDialog.visible = true
  followForm.contact_name = row.contact_name
  followForm.contact_phone = row.contact_phone
}

const addFollow = async () => {
  followDialog.loading = true
  try {
    await request.post(`/buildings/${followDialog.buildingId}/follows`, followForm)
    ElMessage.success('添加成功')
    followDialog.visible = false
    followForm.content = ''
    followForm.result = ''
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    followDialog.loading = false
  }
}

// 详情
const viewDetail = async (row) => {
  try {
    const res = await request.get(`/buildings/${row.id}`)
    detailDrawer.building = res
    detailDrawer.title = `楼盘详情 - ${row.name}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 辅助函数
const cooperationType = (status) => {
  const types = {
    none: 'info',
    contacting: 'warning',
    cooperating: 'success',
    ended: 'danger'
  }
  return types[status] || 'info'
}

const cooperationLabel = (status) => {
  const labels = {
    none: '未合作',
    contacting: '接洽中',
    cooperating: '合作中',
    ended: '已结束'
  }
  return labels[status] || status
}

const propertyTypeLabel = (type) => {
  const labels = {
    residential: '住宅',
    villa: '别墅',
    apartment: '公寓',
    commercial: '商业',
    mixed: '商住混合'
  }
  return labels[type] || type
}

const followTypeLabel = (type) => {
  const labels = {
    visit: '拜访',
    phone: '电话',
    meeting: '会议',
    event: '活动',
    other: '其他'
  }
  return labels[type] || type
}

const followResultLabel = (result) => {
  const labels = {
    interested: '有意向',
    considering: '考虑中',
    rejected: '拒绝',
    cooperated: '已合作',
    follow_up: '需跟进'
  }
  return labels[result] || result
}

const followResultType = (result) => {
  const types = {
    interested: 'success',
    considering: 'warning',
    rejected: 'danger',
    cooperated: 'success',
    follow_up: 'info'
  }
  return types[result] || 'info'
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
  loadStats()
  loadOptions()
})
</script>

<style scoped>
.building-manage {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #262626;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.stat-card.success .stat-value {
  color: #52c41a;
}

.stat-card.warning .stat-value {
  color: #faad14;
}

.filter-card {
  margin-bottom: 24px;
}

.building-name {
  font-weight: 500;
  color: #262626;
}

.building-address {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.property-company {
  font-size: 12px;
  color: #8c8c8c;
}

.contact-phone {
  font-size: 12px;
  color: #8c8c8c;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.building-detail {
  padding: 16px;
}

.section {
  margin-top: 32px;
}

.section h4 {
  margin-bottom: 16px;
  color: #262626;
  font-weight: 500;
}

.follow-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.follow-header .operator {
  font-size: 12px;
  color: #8c8c8c;
}

.follow-content {
  color: #595959;
  line-height: 1.6;
}
</style>
