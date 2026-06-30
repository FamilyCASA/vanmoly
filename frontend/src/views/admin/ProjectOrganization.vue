<template>
  <div class="project-organization">
    <template v-if="mode === 'permissions'">
      <section class="project-hero permission-hero">
        <div>
          <p>PROJECT PERMISSION</p>
          <h2>项目权限矩阵</h2>
          <span>组织架构权限决定系统边界，项目权限决定每个项目内的职责边界。</span>
        </div>
        <el-select v-model="permissionProjectId" placeholder="选择项目组" clearable filterable @change="loadPermissionProject">
          <el-option v-for="item in projects" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </section>

      <div class="permission-layout">
        <el-card shadow="never" class="role-card">
          <template #header>项目角色模板</template>
          <div v-for="role in roleTemplates" :key="role.code" class="role-template">
            <div>
              <strong>{{ role.name }}</strong>
              <span>{{ role.description }}</span>
            </div>
            <div class="permission-chips">
              <el-tag v-for="key in role.permission_keys" :key="key" size="small" effect="plain">
                {{ permissionLabel(key) }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="matrix-card">
          <template #header>
            <div class="card-head">
              <span>权限策略</span>
              <el-button type="primary" :disabled="!permissionProjectId" @click="savePermissionPolicies">保存策略</el-button>
            </div>
          </template>
          <el-empty v-if="!permissionProjectId" description="请选择一个项目组配置权限" />
          <div v-else class="permission-groups">
            <div v-for="group in permissionGroups" :key="group.group" class="permission-group">
              <h3>{{ group.group }}</h3>
              <div v-for="item in group.items" :key="item.key" class="permission-row">
                <div class="permission-name">
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.key }}</span>
                </div>
                <el-select
                  v-model="policyMap[item.key].allowed_roles"
                  multiple
                  collapse-tags
                  placeholder="允许角色"
                >
                  <el-option v-for="role in roleTemplates" :key="role.code" :label="role.name" :value="role.code" />
                </el-select>
                <el-select
                  v-model="policyMap[item.key].allowed_employee_ids"
                  multiple
                  collapse-tags
                  filterable
                  placeholder="指定员工"
                >
                  <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
                </el-select>
                <el-switch v-model="policyMap[item.key].approval_required" active-text="需审核" />
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </template>

    <template v-else>
      <section class="project-hero">
        <div>
          <p>PROJECT ORGANIZATION</p>
          <h2>项目组织协同中心</h2>
          <span>以项目小组串联员工、客户、楼盘、任务、会议、成本与复盘。</span>
        </div>
        <div class="hero-actions">
          <el-button @click="loadProjects">刷新</el-button>
          <el-button type="primary" @click="openProjectDialog()">新建项目组</el-button>
        </div>
      </section>

      <div class="stat-grid">
        <div class="stat-card">
          <span>项目总数</span>
          <strong>{{ stats.total || 0 }}</strong>
        </div>
        <div class="stat-card">
          <span>进行中</span>
          <strong>{{ stats.active || 0 }}</strong>
        </div>
        <div class="stat-card">
          <span>筹备中</span>
          <strong>{{ stats.planning || 0 }}</strong>
        </div>
        <div class="stat-card warn">
          <span>待推进任务</span>
          <strong>{{ stats.pending_tasks || 0 }}</strong>
        </div>
      </div>

      <el-card class="toolbar-card" shadow="never">
        <el-form :inline="true" :model="filters">
          <el-form-item label="关键词">
            <el-input v-model="filters.keyword" placeholder="项目名称/编号/目标" clearable />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="filters.project_type" placeholder="全部类型" clearable>
              <el-option v-for="item in projectTypes" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部状态" clearable>
              <el-option v-for="item in projectStatuses" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadProjects">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card shadow="never" class="table-card">
        <el-table :data="projects" v-loading="loading" stripe>
          <el-table-column label="项目组" min-width="220">
            <template #default="{ row }">
              <div class="project-name">
                <strong>{{ row.name }}</strong>
                <span>{{ row.code || '未设置编号' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="130">
            <template #default="{ row }">{{ optionLabel(projectTypes, row.project_type) }}</template>
          </el-table-column>
          <el-table-column label="负责人" width="120">
            <template #default="{ row }">{{ row.owner_name || '-' }}</template>
          </el-table-column>
          <el-table-column label="进度" min-width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.progress || 0" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column label="预算/已用" width="150">
            <template #default="{ row }">¥{{ money(row.spent_amount) }} / ¥{{ money(row.budget) }}</template>
          </el-table-column>
          <el-table-column label="成员/任务" width="110">
            <template #default="{ row }">{{ row.member_count || 0 }}人 / {{ row.task_count || 0 }}项</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status)" size="small">{{ optionLabel(projectStatuses, row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetail(row)">详情</el-button>
              <el-button link type="primary" @click="openProjectDialog(row)">编辑</el-button>
              <el-button link type="primary" @click="openTaskDialog(row)">发任务</el-button>
              <el-button link type="primary" @click="openMeetingDialog(row)">会议</el-button>
              <el-button link type="danger" @click="archiveProject(row)">归档</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="loadProjects"
          />
        </div>
      </el-card>

      <el-drawer v-model="detailDrawer" size="78%" :title="selectedProject?.name || '项目详情'">
        <div v-if="selectedProject" class="project-detail">
          <div class="detail-overview">
            <div>
              <span>项目目标</span>
              <p>{{ selectedProject.objective || '暂未填写' }}</p>
            </div>
            <div>
              <span>项目范围</span>
              <p>{{ selectedProject.scope || '暂未填写' }}</p>
            </div>
            <div>
              <span>关联业务</span>
              <p>线索 {{ selectedProject.related_lead_id || '-' }} / 客户 {{ selectedProject.related_customer_id || '-' }} / 楼盘 {{ selectedProject.related_building_id || '-' }}</p>
            </div>
          </div>

          <el-tabs v-model="detailTab">
            <el-tab-pane label="成员分工" name="members">
              <div class="section-actions">
                <el-button type="primary" @click="openMemberDialog()">添加成员</el-button>
              </div>
              <el-table ref="memberTableRef" :data="selectedProject.members || []" stripe @row-click="toggleMemberExpand">
                <el-table-column type="expand">
                  <template #default="{ row }">
                    <div v-if="memberExpandLoading[row.employee_id]" style="padding: 16px; text-align: center; color: #909399">
                      <el-icon class="is-loading"><Loading /></el-icon> 加载兼任项目...
                    </div>
                    <div v-else-if="memberExpandData[row.employee_id]" style="padding: 12px 20px">
                      <div v-if="memberExpandData[row.employee_id].projects?.length" style="margin-bottom: 16px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #303133">兼任项目 ({{ memberExpandData[row.employee_id].projects.length }}个)</div>
                        <el-table :data="memberExpandData[row.employee_id].projects" size="small" style="max-width: 800px">
                          <el-table-column label="项目" min-width="180">
                            <template #default="{ row: p }">
                              <span>{{ p.project.name }}</span>
                              <el-tag v-if="p.member.is_leader" type="warning" size="small" style="margin-left: 4px">组长</el-tag>
                            </template>
                          </el-table-column>
                          <el-table-column label="角色" width="100">
                            <template #default="{ row: p }">{{ roleLabel(p.member.role_code) }}</template>
                          </el-table-column>
                          <el-table-column prop="member.responsibility" label="分工" show-overflow-tooltip />
                          <el-table-column label="进度" width="120">
                            <template #default="{ row: p }"><el-progress :percentage="p.project.progress || 0" :stroke-width="6" /></template>
                          </el-table-column>
                          <el-table-column label="状态" width="90">
                            <template #default="{ row: p }"><el-tag :type="statusTag(p.project.status)" size="small">{{ optionLabel(projectStatuses, p.project.status) }}</el-tag></template>
                          </el-table-column>
                        </el-table>
                      </div>
                      <div v-if="memberExpandData[row.employee_id].tasks?.length" style="margin-bottom: 12px">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #303133">待处理任务 ({{ memberExpandData[row.employee_id].tasks.length }}个)</div>
                        <el-table :data="memberExpandData[row.employee_id].tasks" size="small" style="max-width: 800px">
                          <el-table-column prop="title" label="任务" min-width="160" />
                          <el-table-column label="项目" width="140">
                            <template #default="{ row: t }">{{ getProjectNameById(t.project_id) }}</template>
                          </el-table-column>
                          <el-table-column prop="phase" label="节点" width="100" />
                          <el-table-column label="状态" width="90">
                            <template #default="{ row: t }"><el-tag size="small">{{ taskStatusLabel(t.status) }}</el-tag></template>
                          </el-table-column>
                          <el-table-column prop="due_date" label="截止" width="100" />
                        </el-table>
                      </div>
                      <div v-if="!memberExpandData[row.employee_id].projects?.length && !memberExpandData[row.employee_id].tasks?.length" style="color: #909399">
                        暂无兼任项目和待处理任务
                      </div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="employee_name" label="成员" width="120" />
                <el-table-column prop="department_name" label="部门" width="130" />
                <el-table-column prop="position_name" label="岗位" width="110" />
                <el-table-column label="项目角色" width="100">
                  <template #default="{ row }">
                    <span>{{ roleLabel(row.role_code) }}</span>
                    <el-tag v-if="row.is_leader" type="warning" size="small" style="margin-left: 4px">组长</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="responsibility" label="分工职责" min-width="160" show-overflow-tooltip />
                <el-table-column prop="workload" label="投入" width="80" />
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button link type="danger" @click.stop="removeMember(row)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="任务流程" name="tasks">
              <div class="section-actions">
                <el-button type="primary" @click="openTaskDialog(selectedProject)">发布任务</el-button>
                <el-button @click="openApplicationDialog(selectedProject)">主动任务申请</el-button>
              </div>
              <el-table :data="selectedProject.tasks || []" stripe>
                <el-table-column prop="title" label="任务" min-width="180" />
                <el-table-column prop="phase" label="流程节点" width="130" />
                <el-table-column prop="assignee_name" label="执行人" width="110" />
                <el-table-column label="状态" width="110">
                  <template #default="{ row }"><el-tag size="small">{{ taskStatusLabel(row.status) }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="due_date" label="截止" width="110" />
                <el-table-column label="流转" width="260">
                  <template #default="{ row }">
                    <el-button v-for="status in nextTaskStatuses(row.status)" :key="status" link type="primary" @click="transitionTask(row, status)">
                      {{ taskStatusLabel(status) }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="申请审核" name="applications">
              <el-table :data="selectedProject.applications || []" stripe>
                <el-table-column prop="employee_name" label="申请人" width="110" />
                <el-table-column prop="task_type" label="类型" width="130" />
                <el-table-column prop="reason" label="原因" show-overflow-tooltip />
                <el-table-column label="状态" width="100">
                  <template #default="{ row }"><el-tag size="small">{{ applicationStatusLabel(row.status) }}</el-tag></template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button v-if="row.status === 'pending'" link type="success" @click="reviewApplication(row, 'approved')">通过</el-button>
                    <el-button v-if="row.status === 'pending'" link type="danger" @click="reviewApplication(row, 'rejected')">驳回</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="会议纪要" name="meetings">
              <div class="section-actions">
                <el-button type="primary" @click="openMeetingDialog(selectedProject)">登记会议</el-button>
              </div>
              <el-table :data="selectedProject.meetings || []" stripe>
                <el-table-column prop="topic" label="主题" min-width="180" />
                <el-table-column prop="location" label="地点" width="120" />
                <el-table-column prop="start_time" label="时间" width="170" />
                <el-table-column prop="secretary_name" label="书记员" width="110" />
                <el-table-column prop="minutes" label="纪要" show-overflow-tooltip />
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="项目复盘" name="reviews">
              <div class="section-actions">
                <el-button type="primary" @click="openReviewDialog(selectedProject)">写复盘</el-button>
              </div>
              <el-table :data="selectedProject.reviews || []" stripe>
                <el-table-column prop="summary" label="复盘总结" min-width="220" show-overflow-tooltip />
                <el-table-column prop="budget_review" label="预算复盘" show-overflow-tooltip />
                <el-table-column prop="schedule_review" label="进度复盘" show-overflow-tooltip />
                <el-table-column prop="created_at" label="记录时间" width="170" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-drawer>

      <el-dialog v-model="projectDialog.visible" :title="projectForm.id ? '编辑项目组' : '新建项目组'" width="820px">
        <el-form :model="projectForm" label-width="100px">
          <el-row :gutter="16">
            <el-col :span="12"><el-form-item label="项目名称" required><el-input v-model="projectForm.name" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="项目编号"><el-input v-model="projectForm.code" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="项目类型">
                <el-select v-model="projectForm.project_type" style="width: 100%">
                  <el-option v-for="item in projectTypes" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="负责人">
                <el-select v-model="projectForm.owner_id" clearable filterable style="width: 100%" @change="onProjectOwnerChange">
                  <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="项目组成员">
                <el-select v-model="projectForm.member_ids" multiple filterable collapse-tags collapse-tags-tooltip style="width: 100%" placeholder="选择项目组成员">
                  <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" :disabled="item.id === projectForm.owner_id">
                    <span>{{ employeeOptionLabel(item) }}</span>
                    <el-tag v-if="item.id === projectForm.owner_id" type="success" size="small" style="margin-left: 6px">负责人</el-tag>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12"><el-form-item label="预算"><el-input-number v-model="projectForm.budget" :min="0" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="进度"><el-slider v-model="projectForm.progress" :min="0" :max="100" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="projectForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="projectForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="24"><el-form-item label="项目目标"><el-input v-model="projectForm.objective" type="textarea" :rows="3" /></el-form-item></el-col>
            <el-col :span="24"><el-form-item label="项目范围"><el-input v-model="projectForm.scope" type="textarea" :rows="3" /></el-form-item></el-col>
          </el-row>
        </el-form>
        <template #footer>
          <el-button @click="projectDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveProject">保存</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="memberDialog.visible" title="添加项目成员" width="560px">
        <el-form :model="memberForm" label-width="100px">
          <el-form-item label="成员" required>
            <el-select v-model="memberForm.employee_id" filterable style="width: 100%">
              <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目角色">
            <el-select v-model="memberForm.role_code" style="width: 100%">
              <el-option v-for="role in roleTemplates" :key="role.code" :label="role.name" :value="role.code" />
            </el-select>
          </el-form-item>
          <el-form-item label="分工职责"><el-input v-model="memberForm.responsibility" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="投入"><el-input v-model="memberForm.workload" placeholder="例如 50% / 每周3天" /></el-form-item>
          <el-form-item label="组长"><el-switch v-model="memberForm.is_leader" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="memberDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveMember">保存</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="taskDialog.visible" title="发布项目任务" width="680px">
        <el-form :model="taskForm" label-width="100px">
          <el-form-item label="任务标题" required><el-input v-model="taskForm.title" /></el-form-item>
          <el-form-item label="流程节点">
            <el-select v-model="taskForm.phase" clearable filterable style="width: 100%" placeholder="选择流程节点">
              <el-option-group v-for="group in workflowNodeGroups" :key="group.phase" :label="group.phase">
                <el-option v-for="node in group.nodes" :key="node.node_code" :label="node.node_name" :value="node.node_name">
                  <span>{{ node.node_code }}</span>
                  <span style="margin-left: 8px; color: #606266">{{ node.node_name }}</span>
                </el-option>
              </el-option-group>
            </el-select>
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="执行人">
                <el-select v-model="taskForm.assignee_id" clearable filterable style="width: 100%">
                  <el-option v-for="item in projectMemberOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id">
                    <span>{{ employeeOptionLabel(item) }}</span>
                    <el-tag v-if="item.is_leader" type="warning" size="small" style="margin-left: 6px">组长</el-tag>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="审核人">
                <el-select v-model="taskForm.reviewer_id" clearable filterable style="width: 100%">
                  <el-option v-for="item in adminEmployeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id">
                    <span>{{ employeeOptionLabel(item) }}</span>
                    <el-tag v-if="item.id === currentUserId" type="success" size="small" style="margin-left: 6px">自己</el-tag>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="截止日期"><el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
          <el-form-item label="任务说明"><el-input v-model="taskForm.description" type="textarea" :rows="4" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="taskDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveTask">发布</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="applicationDialog.visible" title="主动任务申请" width="620px">
        <el-form :model="applicationForm" label-width="100px">
          <el-form-item label="申请人" required>
            <el-select v-model="applicationForm.employee_id" filterable style="width: 100%">
              <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="任务类型"><el-input v-model="applicationForm.task_type" placeholder="例如：紧急外出测量" /></el-form-item>
          <el-form-item label="申请原因"><el-input v-model="applicationForm.reason" type="textarea" :rows="4" /></el-form-item>
          <el-row :gutter="16">
            <el-col :span="12"><el-form-item label="客户ID"><el-input-number v-model="applicationForm.related_customer_id" :min="1" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="楼盘ID"><el-input-number v-model="applicationForm.related_building_id" :min="1" style="width: 100%" /></el-form-item></el-col>
          </el-row>
        </el-form>
        <template #footer>
          <el-button @click="applicationDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveApplication">提交申请</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="meetingDialog.visible" title="登记项目会议" width="720px">
        <el-form :model="meetingForm" label-width="110px">
          <el-form-item label="会议主题" required><el-input v-model="meetingForm.topic" /></el-form-item>
          <el-form-item label="待解决问题"><el-input v-model="meetingForm.problems" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="参会人员">
            <el-select v-model="meetingForm.attendee_ids" multiple filterable style="width: 100%">
              <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="12"><el-form-item label="会议地点"><el-input v-model="meetingForm.location" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="持续分钟"><el-input-number v-model="meetingForm.duration_minutes" :min="15" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="开始时间"><el-date-picker v-model="meetingForm.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="书记员">
                <el-select v-model="meetingForm.secretary_id" clearable filterable style="width: 100%">
                  <el-option v-for="item in employeeOptions" :key="item.id" :label="employeeOptionLabel(item)" :value="item.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="准备文件"><el-input v-model="meetingForm.required_files" /></el-form-item>
          <el-form-item label="准备工具"><el-input v-model="meetingForm.required_tools" /></el-form-item>
          <el-form-item label="会议纪要"><el-input v-model="meetingForm.minutes" type="textarea" :rows="3" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="meetingDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveMeeting">保存会议</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="reviewDialog.visible" title="项目复盘" width="720px">
        <el-form :model="reviewForm" label-width="100px">
          <el-form-item label="复盘总结"><el-input v-model="reviewForm.summary" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="有效经验"><el-input v-model="reviewForm.wins" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="问题记录"><el-input v-model="reviewForm.problems" type="textarea" :rows="3" /></el-form-item>
          <el-form-item label="预算复盘"><el-input v-model="reviewForm.budget_review" type="textarea" :rows="2" /></el-form-item>
          <el-form-item label="进度复盘"><el-input v-model="reviewForm.schedule_review" type="textarea" :rows="2" /></el-form-item>
          <el-form-item label="改进动作"><el-input v-model="reviewForm.improvement_actions" type="textarea" :rows="3" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="reviewDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveReview">保存复盘</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import request from '@/utils/request'

const props = defineProps({
  mode: {
    type: String,
    default: 'projects'
  },
  employees: {
    type: Array,
    default: () => []
  }
})

const loading = ref(false)
const saving = ref(false)
const projects = ref([])
const employeeOptions = ref([])
const roleTemplates = ref([])
const permissionGroups = ref([])
const projectTypes = ref([])
const projectStatuses = ref([])
const taskStatusFlow = ref({})
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedProject = ref(null)
const detailDrawer = ref(false)
const detailTab = ref('members')
const permissionProjectId = ref(null)
const policyMap = reactive({})

const filters = reactive({
  keyword: '',
  status: '',
  project_type: ''
})

const projectDialog = reactive({ visible: false })
const memberDialog = reactive({ visible: false })
const taskDialog = reactive({ visible: false })
const applicationDialog = reactive({ visible: false })
const meetingDialog = reactive({ visible: false })
const reviewDialog = reactive({ visible: false })

const defaultProjectForm = () => ({
  id: null,
  name: '',
  code: '',
  project_type: 'customer_project',
  status: 'planning',
  priority: 'normal',
  objective: '',
  scope: '',
  budget: 0,
  spent_amount: 0,
  progress: 0,
  start_date: '',
  end_date: '',
  owner_id: null,
  member_ids: []
})

const defaultMemberForm = () => ({
  employee_id: null,
  role_code: 'member',
  responsibility: '',
  workload: '',
  is_leader: false,
  data_scope: 'project',
  permission_overrides: []
})

const defaultTaskForm = () => ({
  title: '',
  description: '',
  phase: '',
  status: 'published',
  priority: 'normal',
  assignee_id: null,
  reviewer_id: null,
  due_date: ''
})
const currentUserId = ref(null)
const workflowNodes = ref([])
const workflowNodeGroups = computed(() => {
  const groups = {}
  workflowNodes.value.forEach(node => {
    const phaseKey = node.phase || '其他'
    const phaseLabel = node.phase_label || phaseKey
    if (!groups[phaseKey]) {
      groups[phaseKey] = { phase: phaseLabel, nodes: [] }
    }
    groups[phaseKey].nodes.push(node)
  })
  return Object.values(groups).sort((a, b) => {
    const aOrder = a.nodes[0]?.phase_order || 0
    const bOrder = b.nodes[0]?.phase_order || 0
    return aOrder - bOrder
  })
})
const projectMemberOptions = computed(() => {
  if (!selectedProject.value?.members) return employeeOptions.value
  return selectedProject.value.members.map(m => ({
    id: m.employee_id,
    name: m.employee_name,
    department_name: m.department_name,
    position_name: m.position_name,
    is_leader: m.is_leader
  }))
})
const adminEmployeeOptions = computed(() => employeeOptions.value)
const onProjectOwnerChange = () => {
  if (projectForm.owner_id && !projectForm.member_ids.includes(projectForm.owner_id)) {
    projectForm.member_ids.push(projectForm.owner_id)
  }
}

const defaultApplicationForm = () => ({
  employee_id: null,
  task_type: '紧急外出测量',
  reason: '',
  related_customer_id: null,
  related_building_id: null
})

const defaultMeetingForm = () => ({
  topic: '',
  problems: '',
  attendee_ids: [],
  required_files: '',
  required_tools: '',
  location: '',
  duration_minutes: 60,
  start_time: '',
  secretary_id: null,
  minutes: '',
  decisions: ''
})

const defaultReviewForm = () => ({
  summary: '',
  wins: '',
  problems: '',
  budget_review: '',
  schedule_review: '',
  improvement_actions: ''
})

const projectForm = reactive(defaultProjectForm())
const memberForm = reactive(defaultMemberForm())
const taskForm = reactive(defaultTaskForm())
const applicationForm = reactive(defaultApplicationForm())
const meetingForm = reactive(defaultMeetingForm())
const reviewForm = reactive(defaultReviewForm())
const actionProjectId = ref(null)
const memberExpandData = reactive({})
const memberExpandLoading = reactive({})
const memberTableRef = ref(null)

const permissionItems = computed(() => permissionGroups.value.flatMap(group => group.items || []))

const syncEmployeeOptions = async () => {
  if (props.employees?.length) {
    employeeOptions.value = props.employees.map(item => ({
      id: item.id,
      name: item.name,
      department_name: item.department_name,
      position_name: item.position_name
    }))
    return
  }
  try {
    employeeOptions.value = await request.get('/project-teams/employee-options')
  } catch (error) {
    console.error('加载员工选项失败', error)
  }
}

const loadMeta = async () => {
  try {
    const [roles, permissions, nodesRes] = await Promise.all([
      request.get('/project-teams/roles'),
      request.get('/project-teams/permissions'),
      request.get('/workflows/nodes')
    ])
    roleTemplates.value = roles || []
    permissionGroups.value = permissions?.groups || []
    projectTypes.value = permissions?.project_types || []
    projectStatuses.value = permissions?.project_statuses || []
    taskStatusFlow.value = permissions?.task_status_flow || {}
    // 流程节点：API返回{phase: {info, nodes}}对象，拍平成数组
    const raw = nodesRes || {}
    const phaseNames = {}
    const allNodes = []
    Object.entries(raw).forEach(([phaseKey, group]) => {
      if (group?.info?.name) phaseNames[phaseKey] = group.info.name
      if (group?.nodes) {
        group.nodes.forEach(n => { allNodes.push(n) })
      }
    })
    workflowNodes.value = allNodes.filter(n => n.is_enabled !== false)
    // 将阶段中文名存入每个节点的 phase_label 字段
    workflowNodes.value.forEach(n => {
      n.phase_label = phaseNames[n.phase] || n.phase
    })
    resetPolicyMap([])
  } catch (error) {
    console.error('加载项目配置失败', error)
  }
}

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await request.get('/project-teams', {
      params: {
        page: page.value,
        pageSize: pageSize.value,
        keyword: filters.keyword,
        status: filters.status,
        project_type: filters.project_type
      }
    })
    projects.value = res.items || []
    total.value = res.total || 0
    stats.value = res.stats || {}
  } catch (error) {
    console.error('加载项目组织失败', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.project_type = ''
  page.value = 1
  loadProjects()
}

const loadDetail = async (projectId) => {
  selectedProject.value = await request.get(`/project-teams/${projectId}`)
  return selectedProject.value
}

const openDetail = async (row) => {
  await loadDetail(row.id)
  detailTab.value = 'members'
  detailDrawer.value = true
  // 清空展开状态
  Object.keys(memberExpandData).forEach(k => delete memberExpandData[k])
  Object.keys(memberExpandLoading).forEach(k => delete memberExpandLoading[k])
}

const toggleMemberExpand = async (row, column, event) => {
  // 仅在点击非操作列时触发展开
  if (column?.label === '操作') return
  const eid = row.employee_id
  if (!eid) return
  // 先切换展开状态
  memberTableRef.value?.toggleRowExpansion(row)
  // 如果尚未加载过数据，先加载
  if (!memberExpandData[eid] && !memberExpandLoading[eid]) {
    memberExpandLoading[eid] = true
    try {
      const res = await request.get(`/project-teams/employee/${eid}/summary`)
      memberExpandData[eid] = res || { projects: [], tasks: [] }
    } catch (error) {
      console.error('加载成员兼任信息失败', error)
      memberExpandData[eid] = { projects: [], tasks: [] }
    } finally {
      delete memberExpandLoading[eid]
    }
  }
}

const getProjectNameById = (pid) => {
  if (selectedProject.value?.id === pid) return selectedProject.value.name
  const found = projects.value.find(p => p.id === pid)
  return found?.name || `项目#${pid}`
}

const removeMember = async (row) => {
  if (!selectedProject.value) return
  try {
    await ElMessageBox.confirm(`确定将「${row.employee_name}」从项目组移除？`, '移除成员', { type: 'warning' })
    await request.delete(`/project-teams/${selectedProject.value.id}/members/${row.id}`)
    ElMessage.success('成员已移除')
    await loadDetail(selectedProject.value.id)
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') console.error('移除成员失败', error)
  }
}

const openProjectDialog = (row) => {
  Object.assign(projectForm, defaultProjectForm(), row || {})
  projectForm.member_ids = []
  if (row?.id) {
    loadDetail(row.id).then(detail => {
      projectForm.member_ids = (detail.members || []).map(m => m.employee_id)
    })
  }
  projectDialog.visible = true
}

const saveProject = async () => {
  if (!projectForm.name) {
    ElMessage.warning('请输入项目组名称')
    return
  }
  saving.value = true
  try {
    const payload = { ...projectForm }
    if (!payload.id) {
      payload.members = (payload.member_ids || []).map(eid => ({
        employee_id: eid,
        role_code: eid === payload.owner_id ? 'leader' : 'member',
        is_leader: eid === payload.owner_id,
        responsibility: eid === payload.owner_id ? '项目负责人' : ''
      }))
    }
    delete payload.member_ids
    if (projectForm.id) {
      await request.put(`/project-teams/${projectForm.id}`, payload)
    } else {
      await request.post('/project-teams', payload)
    }
    ElMessage.success('项目组已保存')
    projectDialog.visible = false
    loadProjects()
  } catch (error) {
    console.error('保存项目组失败', error)
  } finally {
    saving.value = false
  }
}

const archiveProject = async (row) => {
  try {
    await ElMessageBox.confirm('确定归档该项目组？归档后不会出现在日常项目列表中。', '归档项目组', { type: 'warning' })
    await request.delete(`/project-teams/${row.id}`)
    ElMessage.success('项目组已归档')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') console.error('归档失败', error)
  }
}

const openMemberDialog = () => {
  if (!selectedProject.value) return
  Object.assign(memberForm, defaultMemberForm())
  memberDialog.visible = true
}

const saveMember = async () => {
  if (!memberForm.employee_id || !selectedProject.value) {
    ElMessage.warning('请选择项目成员')
    return
  }
  saving.value = true
  try {
    await request.post(`/project-teams/${selectedProject.value.id}/members`, memberForm)
    ElMessage.success('成员已加入项目组')
    memberDialog.visible = false
    await loadDetail(selectedProject.value.id)
    loadProjects()
  } catch (error) {
    console.error('保存成员失败', error)
  } finally {
    saving.value = false
  }
}

const openTaskDialog = (project) => {
  actionProjectId.value = project?.id || selectedProject.value?.id
  if (!actionProjectId.value) return
  Object.assign(taskForm, defaultTaskForm())
  // 默认审核人为当前登录用户
  taskForm.reviewer_id = currentUserId.value
  // 默认执行人为项目组长
  if (selectedProject.value?.id === actionProjectId.value && selectedProject.value?.members) {
    const leader = selectedProject.value.members.find(m => m.is_leader)
    if (leader) taskForm.assignee_id = leader.employee_id
  } else if (project?.owner_id) {
    taskForm.assignee_id = project.owner_id
  }
  taskDialog.visible = true
}

const saveTask = async () => {
  if (!taskForm.title || !actionProjectId.value) {
    ElMessage.warning('请输入任务标题')
    return
  }
  saving.value = true
  try {
    await request.post(`/project-teams/${actionProjectId.value}/tasks`, taskForm)
    ElMessage.success('任务已发布')
    taskDialog.visible = false
    if (selectedProject.value?.id === actionProjectId.value) await loadDetail(actionProjectId.value)
    loadProjects()
  } catch (error) {
    console.error('发布任务失败', error)
  } finally {
    saving.value = false
  }
}

const transitionTask = async (task, status) => {
  if (!selectedProject.value) return
  await request.post(`/project-teams/${selectedProject.value.id}/tasks/${task.id}/transition`, { status })
  ElMessage.success('任务状态已更新')
  await loadDetail(selectedProject.value.id)
  loadProjects()
}

const openApplicationDialog = (project) => {
  actionProjectId.value = project?.id || selectedProject.value?.id
  if (!actionProjectId.value) return
  Object.assign(applicationForm, defaultApplicationForm())
  applicationDialog.visible = true
}

const saveApplication = async () => {
  if (!applicationForm.employee_id || !actionProjectId.value) {
    ElMessage.warning('请选择申请人')
    return
  }
  saving.value = true
  try {
    await request.post(`/project-teams/${actionProjectId.value}/applications`, applicationForm)
    ElMessage.success('任务申请已提交')
    applicationDialog.visible = false
    if (selectedProject.value?.id === actionProjectId.value) await loadDetail(actionProjectId.value)
  } catch (error) {
    console.error('提交申请失败', error)
  } finally {
    saving.value = false
  }
}

const reviewApplication = async (application, status) => {
  if (!selectedProject.value) return
  await request.put(`/project-teams/${selectedProject.value.id}/applications/${application.id}/review`, {
    status,
    create_task: status === 'approved',
    task_title: application.task_type
  })
  ElMessage.success(status === 'approved' ? '申请已通过并生成任务' : '申请已驳回')
  await loadDetail(selectedProject.value.id)
  loadProjects()
}

const openMeetingDialog = (project) => {
  actionProjectId.value = project?.id || selectedProject.value?.id
  if (!actionProjectId.value) return
  Object.assign(meetingForm, defaultMeetingForm())
  meetingDialog.visible = true
}

const saveMeeting = async () => {
  if (!meetingForm.topic || !actionProjectId.value) {
    ElMessage.warning('请输入会议主题')
    return
  }
  saving.value = true
  try {
    await request.post(`/project-teams/${actionProjectId.value}/meetings`, meetingForm)
    ElMessage.success('会议已保存')
    meetingDialog.visible = false
    if (selectedProject.value?.id === actionProjectId.value) await loadDetail(actionProjectId.value)
  } catch (error) {
    console.error('保存会议失败', error)
  } finally {
    saving.value = false
  }
}

const openReviewDialog = (project) => {
  actionProjectId.value = project?.id || selectedProject.value?.id
  if (!actionProjectId.value) return
  Object.assign(reviewForm, defaultReviewForm())
  reviewDialog.visible = true
}

const saveReview = async () => {
  if (!actionProjectId.value) return
  saving.value = true
  try {
    await request.post(`/project-teams/${actionProjectId.value}/reviews`, reviewForm)
    ElMessage.success('复盘已保存')
    reviewDialog.visible = false
    if (selectedProject.value?.id === actionProjectId.value) await loadDetail(actionProjectId.value)
  } catch (error) {
    console.error('保存复盘失败', error)
  } finally {
    saving.value = false
  }
}

const resetPolicyMap = (policies = []) => {
  Object.keys(policyMap).forEach(key => delete policyMap[key])
  permissionItems.value.forEach(item => {
    const saved = policies.find(policy => policy.permission_key === item.key)
    policyMap[item.key] = {
      permission_key: item.key,
      allowed_roles: saved?.allowed_roles || [],
      allowed_employee_ids: saved?.allowed_employee_ids || [],
      approval_required: !!saved?.approval_required
    }
  })
}

const loadPermissionProject = async () => {
  if (!permissionProjectId.value) {
    resetPolicyMap([])
    return
  }
  const project = await request.get(`/project-teams/${permissionProjectId.value}`)
  resetPolicyMap(project.permission_policies || [])
}

const savePermissionPolicies = async () => {
  if (!permissionProjectId.value) return
  const policies = Object.values(policyMap)
  await request.put(`/project-teams/${permissionProjectId.value}/permission-policies`, { policies })
  ElMessage.success('项目权限策略已保存')
}

const optionLabel = (options, value) => options.find(item => item.value === value)?.label || value || '-'
const roleLabel = (value) => roleTemplates.value.find(item => item.code === value)?.name || value || '-'
const permissionLabel = (key) => permissionItems.value.find(item => item.key === key)?.label || key
const employeeOptionLabel = (item) => `${item.name}${item.department_name ? ' / ' + item.department_name : ''}`
const money = (value) => Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })

const statusTag = (status) => ({
  planning: 'info',
  active: 'success',
  paused: 'warning',
  completed: 'primary',
  archived: ''
}[status] || '')

const taskStatusLabel = (status) => ({
  draft: '草稿',
  published: '待接收',
  accepted: '已接收',
  in_progress: '执行中',
  submitted: '待审核',
  approved: '已通过',
  rework: '需重做',
  archived: '已归档'
}[status] || status)

const applicationStatusLabel = (status) => ({
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回'
}[status] || status)

const nextTaskStatuses = (status) => taskStatusFlow.value?.[status] || []

onMounted(async () => {
  // 获取当前登录用户
  try {
    const me = await request.get('/auth/me')
    currentUserId.value = me?.id || me?.user_id || null
  } catch (e) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try { currentUserId.value = JSON.parse(userStr).id } catch {}
    }
  }
  await Promise.all([loadMeta(), syncEmployeeOptions()])
  await loadProjects()
})
</script>

<style scoped>
.project-organization {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-hero {
  min-height: 148px;
  padding: 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #10213f 0%, #123f62 52%, #1f6f68 100%);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
}

.project-hero p {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 4px;
  color: rgba(255, 255, 255, 0.62);
}

.project-hero h2 {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.2;
}

.project-hero span {
  color: rgba(255, 255, 255, 0.78);
}

.permission-hero {
  background: linear-gradient(135deg, #18304b 0%, #285068 48%, #7b5d35 100%);
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-card {
  padding: 18px;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
  background: #fff;
}

.stat-card span {
  display: block;
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 10px;
}

.stat-card strong {
  font-size: 28px;
  color: #1f2937;
}

.stat-card.warn strong {
  color: #d97706;
}

.toolbar-card,
.table-card,
.role-card,
.matrix-card {
  border-radius: 8px;
}

.project-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name strong {
  color: #1f2937;
}

.project-name span,
.permission-name span,
.role-template span {
  color: #8a94a6;
  font-size: 12px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.project-detail {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-overview {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.detail-overview > div {
  padding: 16px;
  background: #f6f8fb;
  border: 1px solid #e7ebf2;
  border-radius: 8px;
}

.detail-overview span {
  display: block;
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 8px;
}

.detail-overview p {
  margin: 0;
  color: #1f2937;
  line-height: 1.7;
}

.section-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 12px;
}

.permission-layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
}

.role-template {
  padding: 14px 0;
  border-bottom: 1px solid #edf0f5;
}

.role-template:last-child {
  border-bottom: 0;
}

.role-template strong {
  display: block;
  margin-bottom: 6px;
}

.permission-chips {
  margin-top: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.permission-groups {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.permission-group h3 {
  margin: 0 0 10px;
  color: #1f2937;
  font-size: 15px;
}

.permission-row {
  display: grid;
  grid-template-columns: 160px 1fr 1fr 120px;
  gap: 12px;
  align-items: center;
  padding: 10px 0;
  border-top: 1px solid #edf0f5;
}

.permission-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

@media (max-width: 1200px) {
  .stat-grid,
  .detail-overview,
  .permission-layout {
    grid-template-columns: 1fr 1fr;
  }

  .permission-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .project-hero,
  .hero-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .stat-grid,
  .detail-overview,
  .permission-layout {
    grid-template-columns: 1fr;
  }
}
</style>
