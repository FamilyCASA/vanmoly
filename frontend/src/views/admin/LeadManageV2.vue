<template>
  <div class="lead-manage-v2">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>线索管理 V2.0</h2>
        <el-tag type="warning" effect="dark" v-if="todos.overdue > 0">
          逾期 {{ todos.overdue }} 条
        </el-tag>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>新建线索
        </el-button>
        <el-button @click="openSeaDialog">
          <el-icon><Watermelon /></el-icon>公海 ({{ seaCount }})
        </el-button>
        <el-button @click="openRankingDialog">
          <el-icon><Trophy /></el-icon>积分排行
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>下载模板
        </el-button>
        <el-button type="success" @click="openImportDialog">
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card" @click="setFilter('status', '')">
          <div class="stat-value">{{ stats.total_leads || 0 }}</div>
          <div class="stat-label">总线索</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card today" @click="setFilter('date', 'today')">
          <div class="stat-value">{{ stats.today_new || 0 }}</div>
          <div class="stat-label">今日新增</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card warning" @click="setFilter('is_overdue', 'true')">
          <div class="stat-value">{{ stats.total_overdue || 0 }}</div>
          <div class="stat-label">逾期跟进</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card info" @click="setFilter('is_in_sea', 'true')">
          <div class="stat-value">{{ stats.total_sea || 0 }}</div>
          <div class="stat-label">公海线索</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card success" @click="setFilter('status', '已交定金')">
          <div class="stat-value">{{ stats.deposit_count || 0 }}</div>
          <div class="stat-label">已交定金</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card primary" @click="setFilter('status', '已签约')">
          <div class="stat-value">{{ stats.contract_count || 0 }}</div>
          <div class="stat-label">已签约</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option v-for="s in filterOptions.statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="意向">
          <el-select v-model="filters.intention_level" placeholder="全部" clearable style="width: 100px">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="filters.conversion_level" placeholder="全部" clearable style="width: 100px">
            <el-option label="线索" value="线索" />
            <el-option label="客户" value="客户" />
            <el-option label="VIP" value="VIP" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filters.source" placeholder="全部来源" clearable style="width: 140px">
            <el-option v-for="src in filterOptions.sources" :key="src" :label="src" :value="src" />
          </el-select>
        </el-form-item>
        <el-form-item label="楼盘">
          <el-select v-model="filters.building_name" placeholder="全部楼盘" clearable filterable style="width: 150px">
            <el-option v-for="b in filterOptions.buildings" :key="b" :label="b" :value="b" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="姓名/电话/楼盘" clearable style="width: 180px">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 快捷筛选标签 -->
      <div class="quick-filters">
        <el-check-tag 
          v-for="tag in quickFilters" 
          :key="tag.key"
          :checked="activeQuickFilter === tag.key"
          @change="toggleQuickFilter(tag.key)"
          :type="tag.type"
        >
          {{ tag.label }}
        </el-check-tag>
      </div>
    </el-card>

    <!-- 批量操作栏 -->
    <div class="batch-bar" v-if="selectedLeads.length > 0">
      <span class="batch-text">已选择 {{ selectedLeads.length }} 条线索</span>
      <el-button type="primary" size="small" @click="openBatchAssign">批量分配</el-button>
      <el-button type="danger" size="small" @click="openBatchInvalid">标记无效</el-button>
      <el-button size="small" @click="clearSelection">取消选择</el-button>
    </div>

    <!-- 线索列表 -->
    <el-card>
      <el-table 
        :data="leads" 
        v-loading="loading" 
        stripe
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="线索信息" min-width="200">
          <template #default="{ row }">
            <div class="lead-info">
              <div class="lead-name">
                <span class="name">{{ row.name || '未命名' }}</span>
                <el-tag size="small" :type="getIntentionType(row.intention_level)">
                  {{ row.intention_level }}
                </el-tag>
                <el-tag size="small" :type="getLevelType(row.conversion_level)" effect="plain">
                  {{ row.conversion_level }}
                </el-tag>
              </div>
              <div class="lead-contact">
                <el-icon><Phone /></el-icon>{{ row.phone }}
                <span v-if="row.wechat" class="wechat">
                  <el-icon><ChatDotRound /></el-icon>{{ row.wechat }}
                </span>
              </div>
              <div class="lead-source">
                <el-tag size="small" effect="plain">{{ row.source }}</el-tag>
                <span class="time">{{ formatTime(row.created_at) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="楼盘/需求" min-width="180">
          <template #default="{ row }">
            <div class="building-info">
              <div v-if="row.building_name" class="building-name">
                <el-icon><OfficeBuilding /></el-icon>
                {{ row.building_name }}
              </div>
              <div v-else class="no-data">暂无楼盘信息</div>
              <div v-if="row.house_type || row.area" class="house-info">
                {{ row.house_type }} {{ row.area }}㎡
              </div>
              <div v-if="row.budget" class="budget">
                预算: {{ row.budget }}
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
            <div v-if="row.is_overdue" class="overdue-tag">
              <el-tag type="danger" size="small" effect="plain">逾期{{ row.overdue_days }}天</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="负责人" width="120">
          <template #default="{ row }">
            <div v-if="row.assigned_to">
              <el-avatar :size="24" :icon="UserFilled" />
              <span class="assignee">员工{{ row.assigned_to }}</span>
            </div>
            <el-tag v-else type="info" size="small">待分配</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="跟进" width="140">
          <template #default="{ row }">
            <div class="follow-info">
              <div>跟进 {{ row.follow_count }} 次</div>
              <div v-if="row.next_follow_at" class="next-follow">
                <el-icon><Clock /></el-icon>
                {{ formatDate(row.next_follow_at) }}
              </div>
              <div v-else class="no-follow">暂无跟进计划</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="积分" width="80" align="center">
          <template #default="{ row }">
            <div class="points">
              <el-icon><StarFilled /></el-icon>
              <span>{{ row.total_points || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openFollowDialog(row)">
              跟进
            </el-button>
            <el-button type="primary" link size="small" @click="openDetailDialog(row)">
              详情
            </el-button>
            <el-dropdown trigger="click">
              <el-button type="primary" link size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="openAssignDialog(row)">分配</el-dropdown-item>
                  <el-dropdown-item @click="openEditDialog(row)">编辑</el-dropdown-item>
                  <el-dropdown-item @click="handleUpgrade(row)" v-if="canUpgrade(row)">
                    升级为客户
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleInvalid(row)" type="danger">
                    标记无效
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑线索弹窗 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="isEdit ? '编辑线索' : '新建线索'" 
      width="700px"
      destroy-on-close
    >
      <el-form :model="editForm" label-width="100px" :rules="editRules" ref="editFormRef">
        <el-divider>基础信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="editForm.name" placeholder="客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="editForm.phone" placeholder="11位手机号" :disabled="isEdit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="微信号">
              <el-input v-model="editForm.wechat" placeholder="选填" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="editForm.gender">
                <el-radio-button value="男">男</el-radio-button>
                <el-radio-button value="女">女</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="来源渠道" prop="source">
              <el-select v-model="editForm.source" placeholder="选择来源" style="width: 100%">
                <el-option v-for="s in filterOptions.sources" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="意向等级">
              <el-select v-model="editForm.intention_level" placeholder="选择意向" style="width: 100%">
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>楼盘信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="楼盘名称">
              <el-input v-model="editForm.building_name" placeholder="如：万科城" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="详细地址">
              <el-input v-model="editForm.building_address" placeholder="如：成都市高新区xxx" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="户型">
              <el-select v-model="editForm.house_type" placeholder="选择" style="width: 100%">
                <el-option label="一室一厅" value="一室一厅" />
                <el-option label="两室一厅" value="两室一厅" />
                <el-option label="两室两厅" value="两室两厅" />
                <el-option label="三室一厅" value="三室一厅" />
                <el-option label="三室两厅" value="三室两厅" />
                <el-option label="四室两厅" value="四室两厅" />
                <el-option label="别墅" value="别墅" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="面积">
              <el-input-number v-model="editForm.area" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预算">
              <el-select v-model="editForm.budget" placeholder="选择" style="width: 100%">
                <el-option label="10万以下" value="10万以下" />
                <el-option label="10-20万" value="10-20万" />
                <el-option label="20-30万" value="20-30万" />
                <el-option label="30-50万" value="30-50万" />
                <el-option label="50-100万" value="50-100万" />
                <el-option label="100万以上" value="100万以上" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>需求信息</el-divider>
        <el-form-item label="装修类型">
          <el-radio-group v-model="editForm.decoration_type">
            <el-radio-button value="新房装修">新房装修</el-radio-button>
            <el-radio-button value="旧房翻新">旧房翻新</el-radio-button>
            <el-radio-button value="局部改造">局部改造</el-radio-button>
            <el-radio-button value="软装搭配">软装搭配</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="风格偏好">
          <el-checkbox-group v-model="editForm.style_preference">
            <el-checkbox value="现代简约">现代简约</el-checkbox>
            <el-checkbox value="北欧">北欧</el-checkbox>
            <el-checkbox value="新中式">新中式</el-checkbox>
            <el-checkbox value="轻奢">轻奢</el-checkbox>
            <el-checkbox value="美式">美式</el-checkbox>
            <el-checkbox value="日式">日式</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="详细需求">
          <el-input 
            v-model="editForm.detailed_needs" 
            type="textarea" 
            :rows="3"
            placeholder="记录客户的详细装修需求..."
          />
        </el-form-item>
        <el-form-item label="家庭结构">
          <el-input v-model="editForm.family_structure" placeholder="如：夫妻+1个孩子+父母" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 快速跟进弹窗 -->
    <el-dialog v-model="followDialogVisible" title="快速跟进" width="550px" destroy-on-close>
      <div v-if="currentLead" class="follow-lead-info">
        <el-descriptions :column="2" size="small" border>
          <el-descriptions-item label="姓名">{{ currentLead.name }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentLead.phone }}</el-descriptions-item>
          <el-descriptions-item label="楼盘">{{ currentLead.building_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="getStatusType(currentLead.status)">{{ currentLead.status }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <el-form :model="followForm" label-width="90px" class="follow-form">
        <el-form-item label="跟进方式">
          <el-radio-group v-model="followForm.follow_type">
            <el-radio-button value="电话">电话</el-radio-button>
            <el-radio-button value="微信">微信</el-radio-button>
            <el-radio-button value="到店">到店</el-radio-button>
            <el-radio-button value="其他">其他</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="跟进内容" required>
          <el-input 
            v-model="followForm.content" 
            type="textarea" 
            :rows="4"
            placeholder="记录跟进情况..."
          />
        </el-form-item>
        
        <el-form-item label="跟进结果">
          <el-select v-model="followForm.result" placeholder="选择结果" style="width: 100%">
            <el-option label="意向强烈" value="意向强烈" />
            <el-option label="意向一般" value="意向一般" />
            <el-option label="暂不考虑" value="暂不考虑" />
            <el-option label="需要再联系" value="需要再联系" />
            <el-option label="已预约到店" value="已预约到店" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预约到店">
          <el-switch v-model="followForm.is_visited" />
        </el-form-item>
        
        <el-form-item label="到店时间" v-if="followForm.is_visited">
          <el-date-picker
            v-model="followForm.visited_at"
            type="datetime"
            placeholder="选择到店时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
        
        <el-form-item label="下次跟进">
          <el-date-picker
            v-model="followForm.next_follow_at"
            type="datetime"
            placeholder="选择下次跟进时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="followDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFollow" :loading="submitting">
          提交跟进 (+{{ expectedPoints }}积分)
        </el-button>
      </template>
    </el-dialog>

    <!-- 线索详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="线索详情" width="800px">
      <div v-if="currentLead" v-loading="detailLoading">
        <!-- 顶部操作栏 -->
        <div class="detail-actions">
          <el-button-group>
            <el-button type="primary" @click="openFollowFromDetail">
              <el-icon><Phone /></el-icon>跟进
            </el-button>
            <el-button @click="openEditFromDetail">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button @click="openAssignFromDetail">
              <el-icon><User /></el-icon>分配
            </el-button>
          </el-button-group>
          
          <el-button-group>
            <el-button type="success" @click="handleMarkVisit" v-if="!currentLead.is_visited">
              标记到店
            </el-button>
            <el-button type="warning" @click="handleMarkDeposit" v-if="!currentLead.deposit_at">
              标记定金
            </el-button>
            <el-button type="danger" @click="handleMarkContract" v-if="!currentLead.contract_at">
              标记签约
            </el-button>
          </el-button-group>
        </div>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ currentLead.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="电话">{{ currentLead.phone }}</el-descriptions-item>
              <el-descriptions-item label="微信">{{ currentLead.wechat || '-' }}</el-descriptions-item>
              <el-descriptions-item label="性别">{{ currentLead.gender || '-' }}</el-descriptions-item>
              <el-descriptions-item label="来源">{{ currentLead.source }}</el-descriptions-item>
              <el-descriptions-item label="录入时间">{{ formatTime(currentLead.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="意向等级">
                <el-tag :type="getIntentionType(currentLead.intention_level)">{{ currentLead.intention_level }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="转化等级">
                <el-tag :type="getLevelType(currentLead.conversion_level)">{{ currentLead.conversion_level }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider>楼盘信息</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="楼盘">{{ currentLead.building_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="地址">{{ currentLead.building_address || '-' }}</el-descriptions-item>
              <el-descriptions-item label="户型">{{ currentLead.house_type || '-' }}</el-descriptions-item>
              <el-descriptions-item label="面积">{{ currentLead.area ? currentLead.area + '㎡' : '-' }}</el-descriptions-item>
              <el-descriptions-item label="预算">{{ currentLead.budget || '-' }}</el-descriptions-item>
              <el-descriptions-item label="交房时间">{{ currentLead.delivery_date || '-' }}</el-descriptions-item>
            </el-descriptions>
            
            <el-divider>需求信息</el-divider>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="装修类型">{{ currentLead.decoration_type || '-' }}</el-descriptions-item>
              <el-descriptions-item label="风格偏好">{{ currentLead.style_preference || '-' }}</el-descriptions-item>
              <el-descriptions-item label="详细需求">{{ currentLead.detailed_needs || '-' }}</el-descriptions-item>
              <el-descriptions-item label="家庭结构">{{ currentLead.family_structure || '-' }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="跟进记录" name="follows">
            <el-timeline v-if="currentLead.follows?.length">
              <el-timeline-item
                v-for="follow in currentLead.follows"
                :key="follow.id"
                :type="follow.follow_type === '到店' ? 'primary' : ''"
                :timestamp="formatTime(follow.created_at)"
              >
                <div class="follow-item">
                  <div class="follow-header">
                    <el-tag size="small">{{ follow.follow_type }}</el-tag>
                    <span class="follow-operator">{{ follow.operator_name || '系统' }}</span>
                  </div>
                  <p class="follow-content">{{ follow.content }}</p>
                  <div v-if="follow.result" class="follow-result">
                    结果: {{ follow.result }}
                  </div>
                  <div v-if="follow.next_follow_at" class="follow-next">
                    下次跟进: {{ formatTime(follow.next_follow_at) }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无跟进记录" />
          </el-tab-pane>
          
          <el-tab-pane label="积分记录" name="points">
            <el-table :data="currentLead.points" v-if="currentLead.points?.length" size="small">
              <el-table-column prop="point_type" label="类型" />
              <el-table-column prop="points" label="积分" width="80">
                <template #default="{ row }">
                  <span :class="row.points > 0 ? 'points-positive' : 'points-negative'">
                    {{ row.points > 0 ? '+' : '' }}{{ row.points }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" />
              <el-table-column prop="created_at" label="时间" width="160">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无积分记录" />
          </el-tab-pane>
          
          <el-tab-pane label="转化进度" name="progress">
            <el-steps :active="getProgressStep" finish-status="success">
              <el-step title="线索" description="录入系统" />
              <el-step title="跟进" description="首次联系" />
              <el-step title="到店" description="客户到店" />
              <el-step title="量房" description="上门量房" />
              <el-step title="方案" description="出设计方案" />
              <el-step title="定金" description="交定金" />
              <el-step title="签约" description="正式签约" />
            </el-steps>
            
            <div class="progress-info" v-if="currentLead.deposit_at">
              <el-alert
                :title="`已交定金 ¥${currentLead.deposit_amount}`"
                type="success"
                :closable="false"
              />
            </div>
            <div class="progress-info" v-if="currentLead.contract_at">
              <el-alert
                :title="`已签约 ${currentLead.contract_type} ¥${currentLead.contract_amount}`"
                type="success"
                :closable="false"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 分配弹窗 -->
    <el-dialog v-model="assignDialogVisible" title="分配线索" width="400px">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="当前负责人">
          <span v-if="currentLead?.assigned_to">员工{{ currentLead.assigned_to }}</span>
          <el-tag v-else type="info">待分配</el-tag>
        </el-form-item>
        <el-form-item label="分配给">
          <el-select v-model="assignForm.employee_id" placeholder="选择员工" style="width: 100%">
            <el-option 
              v-for="emp in employees" 
              :key="emp.id" 
              :label="emp.name" 
              :value="emp.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分配原因">
          <el-input v-model="assignForm.reason" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign" :loading="submitting">确认分配</el-button>
      </template>
    </el-dialog>

    <!-- 批量分配弹窗 -->
    <el-dialog v-model="batchAssignVisible" title="批量分配" width="400px">
      <p class="batch-info">已选择 {{ selectedLeads.length }} 条线索</p>
      <el-form :model="batchAssignForm" label-width="80px">
        <el-form-item label="分配给">
          <el-select v-model="batchAssignForm.employee_id" placeholder="选择员工" style="width: 100%">
            <el-option 
              v-for="emp in employees" 
              :key="emp.id" 
              :label="emp.name" 
              :value="emp.id" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchAssignVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchAssign" :loading="submitting">确认分配</el-button>
      </template>
    </el-dialog>

    <!-- 公海弹窗 -->
    <el-dialog v-model="seaDialogVisible" title="公海线索" width="900px">
      <el-table :data="seaLeads" v-loading="seaLoading" size="small">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="building_name" label="楼盘" min-width="150" />
        <el-table-column prop="source" label="来源" width="100" />
        <el-table-column prop="sea_at" label="入公海时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.sea_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="sea_reason" label="原因" width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="retrieveFromSea(row)">
              领取
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="sea-tips">
        <el-alert
          title="公海规则"
          type="info"
          :closable="false"
          description="48小时未跟进自动入公海 | 每人每日限领10条 | 领取后24小时保护期"
        />
      </div>
    </el-dialog>

    <!-- 积分排行榜弹窗 -->
    <el-dialog v-model="rankingDialogVisible" title="积分排行榜" width="700px">
      <el-tabs v-model="rankingPeriod">
        <el-tab-pane label="今日" name="today" />
        <el-tab-pane label="本周" name="week" />
        <el-tab-pane label="本月" name="month" />
        <el-tab-pane label="总榜" name="all" />
      </el-tabs>
      
      <el-table :data="rankingList" v-loading="rankingLoading" size="small">
        <el-table-column width="60" align="center">
          <template #default="{ $index }">
            <div class="rank-cell" :class="{ 'top3': $index < 3 }">
              {{ $index + 1 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="employee_name" label="员工" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="total_points" label="积分" width="100" align="center">
          <template #default="{ row }">
            <span class="points-highlight">{{ row.total_points }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="point_count" label="记录数" width="80" align="center" />
      </el-table>
    </el-dialog>
    <!-- 批量导入弹窗 -->
    <el-dialog v-model="importDialogVisible" title="批量导入线索" width="500px">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls,.csv"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls/csv 文件，请先下载模板填写数据
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Phone, ChatDotRound, OfficeBuilding,
  Clock, StarFilled, ArrowDown, UserFilled, Trophy,
  Edit, User, Download, Upload
} from '@element-plus/icons-vue'
import {
  getLeads, getLeadDetail, createLead, updateLead,
  addFollow, assignLead, batchAssignLeads, markInvalid,
  getSeaLeads, retrieveLeadFromSea, getPointsRanking,
  getLeadFilters, getLeadStats, getTodos
} from '@/api/lead_v2'
import { getEmployees } from '@/api/employee'

// ========== 数据状态 ==========
const loading = ref(false)
const importDialogVisible = ref(false)
const importing = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)
const leads = ref([])
const selectedLeads = ref([])
const stats = ref({})
const todos = ref({})
const seaCount = ref(0)
const employees = ref([])
const filterOptions = ref({
  sources: [],
  buildings: [],
  statuses: [],
  intention_levels: [],
  conversion_levels: []
})

const filters = reactive({
  status: '',
  intention_level: '',
  conversion_level: '',
  source: '',
  building_name: '',
  keyword: '',
  is_overdue: '',
  is_in_sea: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const activeQuickFilter = ref('')
const quickFilters = [
  { key: 'my', label: '我的线索', type: 'primary' },
  { key: 'today', label: '今日新增', type: 'success' },
  { key: 'overdue', label: '逾期跟进', type: 'danger' },
  { key: 'pending', label: '待分配', type: 'warning' },
  { key: 'high', label: '高意向', type: 'info' },
  { key: 'deposit', label: '已交定金', type: 'info' }
]

// ========== 弹窗状态 ==========
const editDialogVisible = ref(false)
const followDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const batchAssignVisible = ref(false)
const seaDialogVisible = ref(false)
const rankingDialogVisible = ref(false)

const isEdit = ref(false)
const submitting = ref(false)
const currentLead = ref(null)
const activeTab = ref('basic')
const detailLoading = ref(false)

// ========== 表单数据 ==========
const editForm = reactive({
  name: '',
  phone: '',
  wechat: '',
  gender: '',
  source: '',
  intention_level: '中',
  building_name: '',
  building_address: '',
  house_type: '',
  area: null,
  budget: '',
  decoration_type: '',
  style_preference: [],
  detailed_needs: '',
  family_structure: ''
})

const editRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  source: [{ required: true, message: '请选择来源', trigger: 'change' }]
}

const followForm = reactive({
  follow_type: '电话',
  content: '',
  result: '',
  next_follow_at: null,
  is_visited: false,
  visited_at: null
})

const assignForm = reactive({
  employee_id: null,
  reason: ''
})

const batchAssignForm = reactive({
  employee_id: null
})

// ========== 公海和排行榜 ==========
const seaLeads = ref([])
const seaLoading = ref(false)
const rankingList = ref([])
const rankingLoading = ref(false)
const rankingPeriod = ref('month')

// ========== 计算属性 ==========
const expectedPoints = computed(() => {
  let points = 1 // 基础跟进
  if (followForm.is_visited) points += 0.5
  return points
})

const getProgressStep = computed(() => {
  if (!currentLead.value) return 0
  const statusMap = {
    '待分配': 0,
    '已分配': 1,
    '跟进中': 1,
    '已到店': 2,
    '已量房': 3,
    '已出方案': 4,
    '已交定金': 5,
    '已签约': 6,
    '已成交': 7
  }
  return statusMap[currentLead.value.status] || 0
})

// ========== 方法 ==========
const fetchLeads = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    const res = await getLeads(params)
    leads.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取线索失败:', error)
    ElMessage.error('获取线索失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await getLeadStats()
    stats.value = res || {}
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const fetchTodos = async () => {
  try {
    const res = await getTodos()
    todos.value = res || {}
  } catch (error) {
    console.error('获取待办失败:', error)
  }
}

const fetchFilterOptions = async () => {
  try {
    const res = await getLeadFilters()
    filterOptions.value = res || {}
  } catch (error) {
    console.error('获取筛选选项失败:', error)
  }
}

const fetchEmployees = async () => {
  try {
    const res = await getEmployees()
    employees.value = res.items || []
  } catch (error) {
    console.error('获取员工失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchLeads()
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  activeQuickFilter.value = ''
  handleSearch()
}

const toggleQuickFilter = (key) => {
  if (activeQuickFilter.value === key) {
    activeQuickFilter.value = ''
    resetFilters()
    return
  }
  activeQuickFilter.value = key
  
  // 应用快捷筛选
  switch (key) {
    case 'my':
      filters.assigned_to = 'current_user' // 需要替换为实际用户ID
      break
    case 'today':
      // 今日新增
      break
    case 'overdue':
      filters.is_overdue = 'true'
      break
    case 'pending':
      filters.status = '待分配'
      break
    case 'high':
      filters.intention_level = '高'
      break
    case 'deposit':
      filters.status = '已交定金'
      break
  }
  handleSearch()
}

const setFilter = (key, value) => {
  filters[key] = value
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  fetchLeads()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchLeads()
}

const handleSelectionChange = (selection) => {
  selectedLeads.value = selection
}

const clearSelection = () => {
  selectedLeads.value = []
}

// ========== 新建/编辑 ==========
const openCreateDialog = () => {
  isEdit.value = false
  Object.keys(editForm).forEach(key => {
    editForm[key] = key === 'style_preference' ? [] : (key === 'intention_level' ? '中' : '')
  })
  editForm.area = null
  editDialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  Object.assign(editForm, row)
  editDialogVisible.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateLead(currentLead.value.id, editForm)
      ElMessage.success('更新成功')
    } else {
      await createLead(editForm)
      ElMessage.success('创建成功，积分+1')
    }
    editDialogVisible.value = false
    fetchLeads()
    fetchStats()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// ========== 跟进 ==========
const openFollowDialog = (row) => {
  currentLead.value = row
  followForm.follow_type = '电话'
  followForm.content = ''
  followForm.result = ''
  followForm.next_follow_at = null
  followForm.is_visited = false
  followForm.visited_at = null
  followDialogVisible.value = true
}

const submitFollow = async () => {
  if (!followForm.content.trim()) {
    ElMessage.warning('请输入跟进内容')
    return
  }
  
  submitting.value = true
  try {
    const res = await addFollow(currentLead.value.id, followForm)
    ElMessage.success(`跟进成功，获得${res.points_earned}积分`)
    followDialogVisible.value = false
    fetchLeads()
    fetchStats()
  } catch (error) {
    console.error('跟进失败:', error)
    ElMessage.error('跟进失败')
  } finally {
    submitting.value = false
  }
}

// ========== 详情 ==========
const openDetailDialog = async (row) => {
  detailLoading.value = true
  detailDialogVisible.value = true
  activeTab.value = 'basic'
  try {
    const res = await getLeadDetail(row.id, { include_follows: true, include_points: true })
    currentLead.value = res
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  } finally {
    detailLoading.value = false
  }
}

const openFollowFromDetail = () => {
  detailDialogVisible.value = false
  openFollowDialog(currentLead.value)
}

const openEditFromDetail = () => {
  detailDialogVisible.value = false
  openEditDialog(currentLead.value)
}

const openAssignFromDetail = () => {
  detailDialogVisible.value = false
  openAssignDialog(currentLead.value)
}

// ========== 分配 ==========
const openAssignDialog = (row) => {
  currentLead.value = row
  assignForm.employee_id = null
  assignForm.reason = ''
  assignDialogVisible.value = true
}

const submitAssign = async () => {
  if (!assignForm.employee_id) {
    ElMessage.warning('请选择员工')
    return
  }
  
  submitting.value = true
  try {
    await assignLead(currentLead.value.id, assignForm)
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    fetchLeads()
  } catch (error) {
    console.error('分配失败:', error)
    ElMessage.error('分配失败')
  } finally {
    submitting.value = false
  }
}

// ========== 批量操作 ==========
const openBatchAssign = () => {
  batchAssignForm.employee_id = null
  batchAssignVisible.value = true
}

const submitBatchAssign = async () => {
  if (!batchAssignForm.employee_id) {
    ElMessage.warning('请选择员工')
    return
  }
  
  submitting.value = true
  try {
    await batchAssignLeads({
      lead_ids: selectedLeads.value.map(l => l.id),
      employee_id: batchAssignForm.employee_id
    })
    ElMessage.success('批量分配成功')
    batchAssignVisible.value = false
    selectedLeads.value = []
    fetchLeads()
  } catch (error) {
    console.error('批量分配失败:', error)
    ElMessage.error('批量分配失败')
  } finally {
    submitting.value = false
  }
}

const openBatchInvalid = async () => {
  try {
    await ElMessageBox.confirm(
      `确定将选中的 ${selectedLeads.value.length} 条线索标记为无效？`,
      '确认操作',
      { type: 'warning' }
    )
    await batchAssignLeads({
      lead_ids: selectedLeads.value.map(l => l.id),
      reason: '批量标记无效'
    })
    ElMessage.success('操作成功')
    selectedLeads.value = []
    fetchLeads()
  } catch {
    // 取消操作
  }
}

// ========== 公海 ==========
const openSeaDialog = async () => {
  seaDialogVisible.value = true
  seaLoading.value = true
  try {
    const res = await getSeaLeads()
    seaLeads.value = res.items || []
  } catch (error) {
    console.error('获取公海失败:', error)
    ElMessage.error('获取公海失败')
  } finally {
    seaLoading.value = false
  }
}

const retrieveFromSea = async (row) => {
  try {
    await retrieveLeadFromSea(row.id)
    ElMessage.success('领取成功')
    seaLeads.value = seaLeads.value.filter(l => l.id !== row.id)
    fetchLeads()
    fetchStats()
  } catch (error) {
    console.error('领取失败:', error)
    ElMessage.error('领取失败')
  }
}

// ========== 排行榜 ==========
const openRankingDialog = async () => {
  rankingDialogVisible.value = true
  await fetchRanking()
}

const fetchRanking = async () => {
  rankingLoading.value = true
  try {
    const res = await getPointsRanking({ period: rankingPeriod.value })
    rankingList.value = res || []
  } catch (error) {
    console.error('获取排行榜失败:', error)
  } finally {
    rankingLoading.value = false
  }
}

watch(rankingPeriod, fetchRanking)

// ========== 其他操作 ==========
const canUpgrade = (row) => {
  return row.conversion_level === '线索' && row.building_name && row.building_address && row.detailed_needs
}

const handleUpgrade = async (row) => {
  try {
    await ElMessageBox.confirm('确定将该线索升级为客户？', '确认升级')
    // 调用升级API
    ElMessage.success('升级成功')
    fetchLeads()
  } catch {
    // 取消
  }
}

const handleInvalid = async (row) => {
  try {
    await ElMessageBox.confirm('确定将该线索标记为无效？', '确认操作', { type: 'warning' })
    await markInvalid(row.id, { reason: '手动标记无效' })
    ElMessage.success('操作成功')
    fetchLeads()
  } catch {
    // 取消
  }
}

const handleMarkVisit = async () => {
  // 标记到店
}

const handleMarkDeposit = async () => {
  // 标记定金
}

const handleMarkContract = async () => {
  // 标记签约
}


// ========== 批量导入 ==========
const openImportDialog = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/v3/leads/import-template', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (!response.ok) throw new Error('下载失败')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '线索导入模板.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  importing.value = true
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    const response = await fetch('/api/v3/leads/import-excel', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    const result = await response.json()
    
    if (result.code === 0 || result.created !== undefined) {
      ElMessage.success(`导入成功！新建 ${result.created || 0} 条，更新 ${result.updated || 0} 条，跳过 ${result.skipped || 0} 条`)
      importDialogVisible.value = false
      importFile.value = null
      fetchLeads()
      fetchStats()
    } else {
      ElMessage.error(result.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

// ========== 工具函数 ==========
const getStatusType = (status) => {
  const map = {
    '待分配': 'info',
    '已分配': 'info',
    '跟进中': 'primary',
    '已到店': 'success',
    '已量房': 'success',
    '已出方案': 'success',
    '已交定金': 'warning',
    '已签约': 'danger',
    '已成交': 'danger',
    '无效': 'info',
    '公海': 'info'
  }
  return map[status] || 'info'
}

const getIntentionType = (level) => {
  const map = { '高': 'danger', '中': 'warning', '低': 'info', '无效': 'info' }
  return map[level] || 'info'
}

const getLevelType = (level) => {
  const map = { '线索': 'info', '客户': 'primary', 'VIP': 'warning', 'SVIP': 'danger' }
  return map[level] || 'info'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// ========== 初始化 ==========
onMounted(() => {
  fetchLeads()
  fetchStats()
  fetchTodos()
  fetchFilterOptions()
  fetchEmployees()
})
</script>

<style scoped>
.lead-manage-v2 {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  text-align: center;
  margin-top: 4px;
}

.stat-card.today .stat-value { color: #67C23A; }
.stat-card.warning .stat-value { color: #E6A23C; }
.stat-card.info .stat-value { color: #409EFF; }
.stat-card.success .stat-value { color: #67C23A; }
.stat-card.primary .stat-value { color: #8B5A2B; }

.filter-card {
  margin-bottom: 20px;
}

.quick-filters {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #EBEEF5;
}

.quick-filters .el-check-tag {
  margin-right: 8px;
}

.batch-bar {
  background: #F5F7FA;
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.batch-text {
  font-size: 14px;
  color: #606266;
}

.lead-info .lead-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.lead-info .name {
  font-weight: 500;
  font-size: 14px;
}

.lead-info .lead-contact {
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.lead-info .wechat {
  color: #67C23A;
}

.lead-info .lead-source {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.building-info .building-name {
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 4px;
}

.building-info .no-data {
  color: #909399;
  font-size: 13px;
}

.building-info .house-info,
.building-info .budget {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.overdue-tag {
  margin-top: 4px;
}

.follow-info {
  font-size: 13px;
}

.follow-info .next-follow {
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.follow-info .no-follow {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.points {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #E6A23C;
  font-weight: 500;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.follow-lead-info {
  background: #F5F7FA;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.follow-form {
  margin-top: 16px;
}

.detail-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.follow-item {
  background: #F5F7FA;
  padding: 12px;
  border-radius: 4px;
}

.follow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.follow-operator {
  font-size: 12px;
  color: #909399;
}

.follow-content {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.follow-result,
.follow-next {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
}

.points-positive {
  color: #67C23A;
  font-weight: 500;
}

.points-negative {
  color: #F56C6C;
  font-weight: 500;
}

.progress-info {
  margin-top: 20px;
}

.rank-cell {
  width: 28px;
  height: 28px;
  line-height: 28px;
  border-radius: 50%;
  background: #EBEEF5;
  color: #606266;
  font-weight: 500;
  margin: 0 auto;
}

.rank-cell.top3 {
  background: #8B5A2B;
  color: white;
}

.points-highlight {
  color: #E6A23C;
  font-weight: 600;
  font-size: 16px;
}

.sea-tips {
  margin-top: 16px;
}

.batch-info {
  margin-bottom: 16px;
  color: #606266;
}
</style>
