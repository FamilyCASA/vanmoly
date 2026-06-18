<template>
  <div class="employee-manage">
    <el-tabs v-model="mainTab" class="main-tabs">
      <el-tab-pane label="员工管理" name="employees">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>员工管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新建员工
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-statistic title="总员工数" :value="stats.total" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="本月新增" :value="stats.new_this_month" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="在职员工" :value="stats.by_status?.active || 0" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="试用期" :value="stats.by_status?.probation || 0" />
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="姓名/电话/工号" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="filterForm.department_id" placeholder="全部部门" clearable>
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option v-for="s in options.status_list" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table :data="employees" v-loading="loading" stripe>
        <el-table-column label="员工" min-width="180">
          <template #default="{ row }">
            <div class="employee-info">
              <el-avatar :size="40" :src="row.avatar">
                {{ row.name?.charAt(0) }}
              </el-avatar>
              <div class="info-text">
                <div class="name">{{ row.name }}</div>
                <div class="no">{{ row.employee_no || '无工号' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="部门/岗位" min-width="150">
          <template #default="{ row }">
            <div>{{ row.department_name || '-' }}</div>
            <div class="position">{{ row.position_name || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="联系方式" min-width="150">
          <template #default="{ row }">
            <div>{{ row.phone || '-' }}</div>
            <div class="email">{{ row.email || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="entry_date" label="入职日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.entry_date) }}
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag effect="plain" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
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

      </el-tab-pane>

      <el-tab-pane label="组织架构" name="org">
        <el-tabs v-model="orgTab" class="org-sub-tabs">
          <el-tab-pane label="股东结构" name="shareholders">
            <div class="tab-content">
              <div class="section-header">
                <h3>股东信息管理</h3>
                <el-button type="primary" :icon="Plus" @click="openShareholderDialog()">新增股东</el-button>
              </div>
              <el-table :data="shareholderList" stripe v-loading="loadingShareholders">
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="phone" label="联系电话" width="130" />
                <el-table-column prop="role" label="角色" width="120">
                  <template #default="{ row }"><el-tag>{{ orgRoleLabel(row.role) }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="share_ratio" label="持股比例" width="100">
                  <template #default="{ row }">{{ ((row.share_ratio||0)*100).toFixed(2) }}%</template>
                </el-table-column>
                <el-table-column prop="investment_amount" label="投资金额" width="130">
                  <template #default="{ row }">¥{{ formatNum2(row.investment_amount) }}</template>
                </el-table-column>
                <el-table-column prop="investment_date" label="投资日期" width="120" />
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status==='active'?'success':'info'" size="small">
                      {{ row.status==='active'?'正常':'退出' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button text type="primary" @click="openShareholderDialog(row)">编辑</el-button>
                    <el-button text type="danger" @click="handleDeleteShareholder(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          <el-tab-pane label="部门管理" name="departments">
            <div class="tab-content">
              <div class="section-header">
                <h3>部门信息管理</h3>
                <el-button type="primary" :icon="Plus" @click="openDeptDialog()">新增部门</el-button>
              </div>
              <el-table :data="orgDepartmentList" stripe v-loading="loadingDepts">
                <el-table-column prop="name" label="部门名称" width="150" />
                <el-table-column prop="code" label="部门编码" width="120" />
                <el-table-column prop="manager_id" label="负责人ID" width="100" />
                <el-table-column prop="sort_order" label="排序" width="70" align="center" />
                <el-table-column prop="is_enabled" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.is_enabled?'success':'info'" size="small">
                      {{ row.is_enabled?'启用':'停用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button text type="primary" @click="openDeptDialog(row)">编辑</el-button>
                    <el-button text type="danger" @click="handleDeleteDept(row)">
                      {{ row.is_enabled?'停用':'启用' }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          <el-tab-pane label="岗位管理" name="positions">
            <div class="tab-content">
              <div class="section-header">
                <h3>岗位信息管理</h3>
                <el-button type="primary" :icon="Plus" @click="openPositionDialog()">新增岗位</el-button>
              </div>
              <el-table :data="orgPositionList" stripe v-loading="loadingPositions">
                <el-table-column prop="name" label="岗位名称" width="150" />
                <el-table-column prop="code" label="岗位编码" width="120" />
                <el-table-column prop="department_id" label="所属部门ID" width="110" />
                <el-table-column prop="level" label="岗位等级" width="100" />
                <el-table-column prop="sort_order" label="排序" width="70" align="center" />
                <el-table-column prop="is_active" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.is_active?'success':'info'" size="small">
                      {{ row.is_active?'启用':'停用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button text type="primary" @click="openPositionDialog(row)">编辑</el-button>
                    <el-button text type="danger" @click="handleDeletePosition(row)">
                      {{ row.is_active?'停用':'启用' }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          <el-tab-pane label="投资管理" name="investment">
            <div class="tab-content">
              <div class="section-header">
                <h3>股东与投资管理</h3>
                <el-button type="primary" :icon="Plus" @click="openShareholderDialog()">新增股东</el-button>
              </div>
              <el-table :data="shareholderList" stripe v-loading="loadingShareholders">
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="phone" label="联系电话" width="130" />
                <el-table-column prop="role" label="角色" width="120">
                  <template #default="{ row }"><el-tag>{{ orgRoleLabel(row.role) }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="share_ratio" label="持股比例" width="100">
                  <template #default="{ row }">{{ ((row.share_ratio||0)*100).toFixed(2) }}%</template>
                </el-table-column>
                <el-table-column prop="investment_amount" label="投资金额" width="130">
                  <template #default="{ row }">¥{{ formatNum2(row.investment_amount) }}</template>
                </el-table-column>
                <el-table-column prop="investment_date" label="投资日期" width="120" />
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status==='active'?'success':'info'" size="small">{{ row.status==='active'?'正常':'退出' }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button text type="primary" @click="openShareholderDialog(row)">编辑</el-button>
                    <el-button text type="danger" @click="handleDeleteShareholder(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          <el-tab-pane label="操作日志" name="audit-logs">
            <div class="tab-content">
              <div class="section-header">
                <h3>系统操作日志</h3>
              </div>
              <el-table :data="auditLogList" stripe v-loading="loadingAuditLogs">
                <el-table-column prop="id" label="ID" width="70" />
                <el-table-column prop="user_name" label="操作人" width="110" />
                <el-table-column prop="action" label="操作类型" width="120">
                  <template #default="{ row }">
                    <el-tag size="small" :type="auditActionType(row.action)">{{ auditActionLabel(row.action) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="target_type" label="目标类型" width="100" />
                <el-table-column prop="target_id" label="目标ID" width="80" />
                <el-table-column prop="ip_address" label="IP地址" width="130" />
                <el-table-column prop="created_at" label="操作时间" width="170" />
                <el-table-column prop="detail" label="详情" show-overflow-tooltip />
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
    </el-tabs>

    <!-- 员工表单对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑员工' : '新建员工'"
      width="800px"
    >
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="form.name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工号">
                  <el-input v-model="form.employee_no" placeholder="如：VM2024001" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号">
                  <el-input v-model="form.phone" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="form.email" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="性别">
                  <el-select v-model="form.gender" style="width: 100%">
                    <el-option label="男" value="男" />
                    <el-option label="女" value="女" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="入职日期">
                  <el-date-picker v-model="form.entry_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="部门">
                  <el-select v-model="form.department_id" style="width: 100%" clearable>
                    <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="岗位">
                  <el-select v-model="form.position_id" style="width: 100%" clearable>
                    <el-option v-for="p in positions" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="职级">
                  <el-input v-model="form.job_level" placeholder="如：P4/M2" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-select v-model="form.status" style="width: 100%">
                    <el-option v-for="s in options.status_list" :key="s.value" :label="s.label" :value="s.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="住址">
              <el-input v-model="form.address" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="工作信息" name="work">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="基本工资">
                  <el-input-number v-model="form.base_salary" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="绩效比例">
                  <el-input-number v-model="form.performance_ratio" :min="0" :max="1" :step="0.1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="角色">
                  <el-select v-model="form.role" style="width: 100%">
                    <el-option v-for="r in options.roles" :key="r.value" :label="r.label" :value="r.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="转正日期">
                  <el-date-picker v-model="form.formal_date" type="date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="3" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="紧急联系" name="emergency">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系人">
                  <el-input v-model="form.emergency_contact" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="form.emergency_phone" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="对外展示" name="showcase">
            <el-form-item label="职称/头衔">
              <el-input v-model="form.title" placeholder="如：全案规划师、资深设计师" maxlength="100" show-word-limit />
            </el-form-item>

            <el-form-item label="半身工作照">
              <el-upload
                class="showcase-photo-uploader"
                :action="uploadUrl"
                :headers="uploadHeaders"
                :show-file-list="false"
                :on-success="handleShowcasePhotoSuccess"
                accept="image/*"
              >
                <img v-if="form.showcase_photo" :src="form.showcase_photo" class="showcase-photo-preview" />
                <el-icon v-else class="showcase-photo-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">建议上传 375×500 像素的半身工作照</div>
            </el-form-item>

            <el-form-item label="个人简介">
              <el-input
                v-model="form.bio"
                type="textarea"
                :rows="8"
                maxlength="400"
                show-word-limit
                placeholder="请输入个人简介，最多400字。可包含：简历、头衔、主创案例等，用于建立信任背书。"
              />
              <div class="bio-tip">每行约50字，最多8行。建议填写：从业年限、擅长风格、代表案例等</div>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialog.loading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 员工详情抽屉 -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="60%">
      <div v-if="detailDrawer.employee" class="employee-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ detailDrawer.employee.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ detailDrawer.employee.employee_no }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ detailDrawer.employee.department_name }}</el-descriptions-item>
          <el-descriptions-item label="岗位">{{ detailDrawer.employee.position_name }}</el-descriptions-item>
          <el-descriptions-item label="入职日期">{{ formatDate(detailDrawer.employee.entry_date) }}</el-descriptions-item>
          <el-descriptions-item label="基本工资">{{ detailDrawer.employee.base_salary }}</el-descriptions-item>
        </el-descriptions>

        <!-- 合同列表 -->
        <div class="section">
          <h4>合同记录</h4>
          <el-table :data="detailDrawer.employee.contracts" size="small">
            <el-table-column prop="contract_no" label="合同编号" />
            <el-table-column prop="contract_type" label="类型" />
            <el-table-column prop="start_date" label="开始日期" />
            <el-table-column prop="end_date" label="结束日期" />
            <el-table-column prop="salary" label="薪资" />
          </el-table>
        </div>

        <!-- 业绩统计 -->
        <div class="section" v-if="detailDrawer.employee.performance">
          <h4>本月业绩</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-statistic title="目标业绩" :value="detailDrawer.employee.performance.target_amount" prefix="¥" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="实际业绩" :value="detailDrawer.employee.performance.actual_amount" prefix="¥" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="提成" :value="detailDrawer.employee.performance.commission" prefix="¥" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="完成率" :value="detailDrawer.employee.performance.completion_rate" suffix="%" />
            </el-col>
          </el-row>
        </div>
      </div>
    </el-drawer>
    <!-- 组织架构 - 股东弹窗 -->
    <el-dialog v-model="showShareholderDialog" :title="shareholderForm.id ? '编辑股东' : '新增股东'" width="600px">
      <el-form :model="shareholderForm" label-width="100px">
        <el-form-item label="股东姓名"><el-input v-model="shareholderForm.name" placeholder="输入股东姓名" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="shareholderForm.phone" placeholder="输入手机号" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="shareholderForm.role" placeholder="选择角色" style="width:100%">
            <el-option label="执行董事" value="executive_director" />
            <el-option label="经理" value="manager" />
            <el-option label="隐名投资人" value="silent_investor" />
          </el-select>
        </el-form-item>
        <el-form-item label="持股比例">
          <el-input-number v-model="shareholderForm.share_ratio" :min="0" :max="1" :step="0.01" :precision="4" />
          <span style="margin-left:8px;">{{ ((shareholderForm.share_ratio||0)*100).toFixed(2) }}%</span>
        </el-form-item>
        <el-form-item label="投资金额">
          <el-input-number v-model="shareholderForm.investment_amount" :min="0" :step="10000" style="width:200px" />
        </el-form-item>
        <el-form-item label="投资日期">
          <el-date-picker v-model="shareholderForm.investment_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="shareholderForm.status">
            <el-radio value="active">正常</el-radio>
            <el-radio value="exited">退出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shareholderForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShareholderDialog=false">取消</el-button>
        <el-button type="primary" @click="saveShareholder" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 组织架构 - 部门弹窗 -->
    <el-dialog v-model="showDeptDialog" :title="deptForm.id ? '编辑部门' : '新增部门'" width="500px">
      <el-form :model="deptForm" label-width="90px">
        <el-form-item label="部门名称" required><el-input v-model="deptForm.name" placeholder="输入部门名称" /></el-form-item>
        <el-form-item label="部门编码"><el-input v-model="deptForm.code" placeholder="如 DEPT-001" /></el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="deptForm.parent_id" placeholder="无（顶级部门）" clearable style="width:100%">
            <el-option v-for="d in orgDepartmentList.filter(x=>x.id!==deptForm.id)" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人ID"><el-input v-model="deptForm.manager_id" placeholder="负责人员工ID" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="deptForm.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="deptForm.is_enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeptDialog=false">取消</el-button>
        <el-button type="primary" @click="saveDept" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 组织架构 - 岗位弹窗 -->
    <el-dialog v-model="showPositionDialog" :title="positionForm.id ? '编辑岗位' : '新增岗位'" width="500px">
      <el-form :model="positionForm" label-width="90px">
        <el-form-item label="岗位名称" required><el-input v-model="positionForm.name" placeholder="输入岗位名称" /></el-form-item>
        <el-form-item label="岗位编码"><el-input v-model="positionForm.code" placeholder="如 POS-001" /></el-form-item>
        <el-form-item label="所属部门">
          <el-select v-model="positionForm.department_id" placeholder="选择部门" clearable style="width:100%">
            <el-option v-for="d in orgDepartmentList" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位等级"><el-input-number v-model="positionForm.level" :min="1" :max="10" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="positionForm.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="positionForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPositionDialog=false">取消</el-button>
        <el-button type="primary" @click="savePosition" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'
import financeAPI from '@/api/finance'

const loading = ref(false)
const employees = ref([])
const departments = ref([])
const positions = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const activeTab = ref('basic')

// 上传配置
const uploadUrl = '/api/v3/upload/image'
const uploadHeaders = {
  Authorization: 'Bearer ' + localStorage.getItem('token')
}

// 半身工作照上传成功回调
const handleShowcasePhotoSuccess = (response) => {
  // axios 拦截器解包后，response 是 { code, message, data: { file_url, ... }, timestamp }
  if (response && response.data && response.data.file_url) {
    form.showcase_photo = response.data.file_url
  } else {
    ElMessage.error('上传失败')
  }
}

const filterForm = reactive({
  keyword: '',
  department_id: null,
  status: ''
})

const options = reactive({
  status_list: [],
  roles: []
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false
})

const form = reactive({
  id: null,
  name: '',
  phone: '',
  email: '',
  gender: '',
  employee_no: '',
  department_id: null,
  position_id: null,
  entry_date: null,
  job_level: '',
  base_salary: 0,
  performance_ratio: 0,
  role: 'employee',
  status: 'active',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  formal_date: null,
  remark: '',
  title: '',
  bio: '',
  showcase_photo: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

const formRef = ref(null)

const detailDrawer = reactive({
  visible: false,
  title: '',
  employee: null
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/employees', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        department_id: filterForm.department_id,
        status: filterForm.status
      }
    })
    employees.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await request.get('/employees/statistics')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadDepartments = async () => {
  try {
    const res = await request.get('/employees/departments')
    departments.value = res
  } catch (error) {
    console.error('加载部门失败', error)
  }
}

const loadPositions = async () => {
  try {
    const res = await request.get('/employees/positions')
    positions.value = res || []
  } catch (error) {
    console.error('加载岗位失败', error)
  }
}

const loadOptions = async () => {
  try {
    const res = await request.get('/employees/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.department_id = null
  filterForm.status = ''
  loadData()
}

const openDialog = (row = null) => {
  dialog.isEdit = !!row
  dialog.visible = true
  activeTab.value = 'basic'

  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, {
      id: null,
      name: '',
      phone: '',
      email: '',
      gender: '',
      employee_no: '',
      department_id: null,
      position_id: null,
      entry_date: null,
      job_level: '',
      base_salary: 0,
      performance_ratio: 0,
      role: 'employee',
      status: 'active',
      address: '',
      emergency_contact: '',
      emergency_phone: '',
      formal_date: null,
      remark: ''
    })
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  dialog.loading = true
  try {
    if (dialog.isEdit) {
      await request.put(`/employees/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/employees', form)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    dialog.loading = false
  }
}

const handleDelete = async (row) => {
  try {
    await request.delete(`/employees/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const viewDetail = async (row) => {
  try {
    const res = await request.get(`/employees/${row.id}`)
    detailDrawer.employee = res
    detailDrawer.title = `员工详情 - ${row.name}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const statusType = (status) => {
  const types = { active: 'success', probation: 'warning', resigned: 'danger', leave: 'info' }
  return types[status] || 'info'
}

const statusLabel = (status) => {
  const labels = { active: '在职', probation: '试用期', resigned: '已离职', leave: '休假中' }
  return labels[status] || status
}

const roleLabel = (role) => {
  const labels = { admin: '管理员', manager: '店长', supervisor: '主管', employee: '员工' }
  return labels[role] || role
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}


// ===== 组织架构 =====
const mainTab = ref('employees')
const orgTab = ref('shareholders')
const loadingShareholders = ref(false)
const loadingDepts = ref(false)
const loadingPositions = ref(false)
const shareholderList = ref([])
const orgDepartmentList = ref([])
const orgPositionList = ref([])
const showShareholderDialog = ref(false)
const showDeptDialog = ref(false)
const showPositionDialog = ref(false)
const saving = ref(false)

const getDefaultShareholderForm = () => ({
  id: null, name: '', phone: '', role: '', share_ratio: 0,
  investment_amount: 0, investment_date: '', status: 'active', notes: ''
})
const getDefaultDeptForm = () => ({
  id: null, name: '', code: '', parent_id: null, manager_id: null,
  sort_order: 0, is_enabled: true
})
const getDefaultPositionForm = () => ({
  id: null, name: '', code: '', department_id: null, level: 1,
  sort_order: 0, is_active: true
})

const shareholderForm = ref(getDefaultShareholderForm())
const deptForm = ref(getDefaultDeptForm())
const positionForm = ref(getDefaultPositionForm())

const formatNum2 = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
const orgRoleLabel = (r) => ({
  'executive_director': '执行董事',
  'manager': '经理',
  'silent_investor': '隐名投资人'
}[r] || r)

const loadShareholders = async () => {
  loadingShareholders.value = true
  try {
    const d = await financeAPI.getShareholders()
    shareholderList.value = d.items || d || []
  } catch (e) { ElMessage.error('加载股东列表失败') }
  finally { loadingShareholders.value = false }
}
const openShareholderDialog = (row) => {
  shareholderForm.value = row ? { ...row } : getDefaultShareholderForm()
  showShareholderDialog.value = true
}
const saveShareholder = async () => {
  saving.value = true
  try {
    const d = { ...shareholderForm.value }
    if (d.investment_date instanceof Date) d.investment_date = d.investment_date.toISOString().split('T')[0]
    if (d.id) await financeAPI.updateShareholder(d.id, d)
    else await financeAPI.createShareholder(d)
    ElMessage.success('保存成功')
    showShareholderDialog.value = false
    loadShareholders()
  } catch (e) { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
const handleDeleteShareholder = (row) => {
  ElMessageBox.confirm('确定删除该股东？', '确认', { type: 'warning' })
    .then(async () => {
      await financeAPI.deleteShareholder(row.id)
      ElMessage.success('删除成功')
      loadShareholders()
    }).catch(() => {})
}

const loadOrgDepartments = async () => {
  loadingDepts.value = true
  try {
    const d = await request({ url: '/employees/departments' })
    orgDepartmentList.value = d.data || d || []
  } catch (e) { ElMessage.error('加载部门列表失败') }
  finally { loadingDepts.value = false }
}
const openDeptDialog = (row) => {
  deptForm.value = row ? { ...row } : getDefaultDeptForm()
  showDeptDialog.value = true
}
const saveDept = async () => {
  if (!deptForm.value.name) { ElMessage.warning('请输入部门名称'); return }
  saving.value = true
  try {
    const d = { ...deptForm.value }
    if (d.id) await request({ url: '/employees/departments/' + d.id, method: 'put', data: d })
    else await request({ url: '/employees/departments', method: 'post', data: d })
    ElMessage.success('保存成功')
    showDeptDialog.value = false
    loadOrgDepartments()
  } catch (e) { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
const handleDeleteDept = (row) => {
  const a = row.is_enabled ? '停用' : '启用'
  ElMessageBox.confirm('确定' + a + '该部门？', '确认', { type: 'warning' })
    .then(async () => {
      await request({ url: '/employees/departments/' + row.id, method: 'put', data: { is_enabled: !row.is_enabled } })
      ElMessage.success(a + '成功')
      loadOrgDepartments()
    }).catch(() => {})
}

const loadOrgPositions = async () => {
  loadingPositions.value = true
  try {
    const d = await request({ url: '/employees/positions' })
    orgPositionList.value = d.data || d || []
  } catch (e) { ElMessage.error('加载岗位列表失败') }
  finally { loadingPositions.value = false }
}
const openPositionDialog = (row) => {
  positionForm.value = row ? { ...row } : getDefaultPositionForm()
  showPositionDialog.value = true
}
const savePosition = async () => {
  if (!positionForm.value.name) { ElMessage.warning('请输入岗位名称'); return }
  saving.value = true
  try {
    const d = { ...positionForm.value }
    if (d.id) await request({ url: '/employees/positions/' + d.id, method: 'put', data: d })
    else await request({ url: '/employees/positions', method: 'post', data: d })
    ElMessage.success('保存成功')
    showPositionDialog.value = false
    loadOrgPositions()
  } catch (e) { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
const handleDeletePosition = (row) => {
  const a = row.is_active ? '停用' : '启用'
  ElMessageBox.confirm('确定' + a + '该岗位？', '确认', { type: 'warning' })
    .then(async () => {
      await request({ url: '/employees/positions/' + row.id, method: 'put', data: { is_active: !row.is_active } })
      ElMessage.success(a + '成功')
      loadOrgPositions()
    }).catch(() => {})
}

const loadingAuditLogs = ref(false)
const auditLogList = ref([])

const loadAuditLogs = async () => {
  loadingAuditLogs.value = true
  try {
    const d = await request({ url: '/finance/audit-logs' })
    auditLogList.value = d.data || d.items || d || []
  } catch (e) { ElMessage.error('加载操作日志失败') }
  finally { loadingAuditLogs.value = false }
}

const auditActionLabel = (a) => ({
  'create': '新增', 'update': '修改', 'delete': '删除',
  'login': '登录', 'logout': '登出',
  'approve': '审核', 'export': '导出'
}[a] || a)
const auditActionType = (a) => ({
  'create': 'success', 'update': 'warning', 'delete': 'danger',
  'login': 'info', 'logout': 'info',
  'approve': '', 'export': ''
}[a] || '')

onMounted(() => {
  loadData()
  loadStats()
  loadDepartments()
  loadPositions()
  loadOptions()
  // 组织架构数据
  loadShareholders()
  loadOrgDepartments()
  loadOrgPositions()
  loadAuditLogs()
})
</script>

<style scoped>
.employee-manage {
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

.filter-card {
  margin-bottom: 24px;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-text .name {
  font-weight: 500;
  color: #262626;
}

.info-text .no {
  font-size: 12px;
  color: #8c8c8c;
}

.position, .email {
  font-size: 12px;
  color: #8c8c8c;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.employee-detail {
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

/* 对外展示 - 半身工作照上传 */
.showcase-photo-uploader {
  width: 150px;
  height: 200px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  transition: border-color 0.3s;
}

.showcase-photo-uploader:hover {
  border-color: #409eff;
}

.showcase-photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.showcase-photo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-tip, .bio-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.5;
}

/* 组织架构 Tab */
.main-tabs { background: #fff; border-radius: 4px; }
.main-tabs .el-tabs__content { padding: 20px; }
.org-sub-tabs { background: #fafafa; padding: 16px; border-radius: 4px; }
.org-sub-tabs .tab-content { margin-top: 16px; }
.org-sub-tabs .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.org-sub-tabs .section-header h3 { margin: 0; font-size: 16px; color: #303133; }

</style>
