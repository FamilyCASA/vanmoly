<template>
  <div class="contract-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>合同管理</h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新建合同
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="(count, status) in stats.by_status" :key="status">
        <el-card class="stat-card" :class="status">
          <div class="stat-value">{{ count }}</div>
          <div class="stat-label">{{ statusLabel(status) }}</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card total">
          <div class="stat-value">&yen;{{ formatMoney(stats.total_amount) }}</div>
          <div class="stat-label">合同总额</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="合同编号/标题" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option v-for="s in options.status_list" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.contract_type" placeholder="全部类型" clearable>
            <el-option v-for="t in options.contract_types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 合同列表 -->
    <el-card shadow="never">
      <el-table :data="contracts" v-loading="loading" stripe>
        <el-table-column prop="contract_no" label="合同编号" width="160" />
        <el-table-column label="客户" min-width="120">
          <template #default="{ row }">
            <div class="customer-name">{{ row.customer_name }}</div>
          </template>
        </el-table-column>
        <el-table-column label="合同标题" min-width="180">
          <template #default="{ row }">
            <div class="contract-title">{{ row.title }}</div>
            <div class="contract-type">{{ typeLabel(row.contract_type) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="150">
          <template #default="{ row }">
            <div class="amount">&yen;{{ formatMoney(row.total_amount) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="签署状态" width="120" align="center">
          <template #default="{ row }">
            <div class="sign-status">
              <el-tag v-if="row.signed_by_customer" type="success" size="small">客签</el-tag>
              <el-tag v-else type="info" size="small">客未签</el-tag>
            </div>
            <div class="sign-status">
              <el-tag v-if="row.signed_by_company" type="success" size="small">司签</el-tag>
              <el-tag v-else type="info" size="small">司未签</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signed_date" label="签署日期" width="120">
          <template #default="{ row }">{{ formatDate(row.signed_date) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button link type="primary">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="submit" v-if="row.status === 'draft'">提交签署</el-dropdown-item>
                  <el-dropdown-item command="sign_customer" v-if="row.status === 'pending' && !row.signed_by_customer">客户签署</el-dropdown-item>
                  <el-dropdown-item command="sign_company" v-if="row.status === 'pending' && !row.signed_by_company">公司签署</el-dropdown-item>
                  <el-dropdown-item command="execute" v-if="row.status === 'signed'">开始执行</el-dropdown-item>
                  <el-dropdown-item command="complete" v-if="row.status === 'executing'">完成合同</el-dropdown-item>
                  <el-dropdown-item command="cancel" divided>取消合同</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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

    <!-- ========== 新建/编辑合同对话框 ========== -->
    <el-dialog v-model="createDialog.visible" :title="createDialog.isEdit ? '编辑合同' : '新建合同'" width="960px" top="2vh" :close-on-click-modal="false">
      <el-form :model="createForm" label-width="120px" class="contract-form">
        <el-tabs v-model="createDialog.activeTab" type="border-card">

          <!-- Tab 1: 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="合同编号">
                  <el-input v-model="createForm.contract_no" placeholder="自动生成，可手动修改" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="签订地点">
                  <el-input v-model="createForm.variables.sign_place" placeholder="如：成都市" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="签订日期">
                  <el-date-picker v-model="createForm.variables.sign_date" type="date" placeholder="选择签订日期" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="合同类型" required>
                  <el-select v-model="createForm.contract_type" style="width:100%">
                    <el-option v-for="t in options.contract_types" :key="t.value" :label="t.label" :value="t.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="合同标题">
              <el-input v-model="createForm.title" placeholder="如：设记家全案家居全案落地服务合同" />
            </el-form-item>
          </el-tab-pane>

          <!-- Tab 2: 甲方信息 -->
          <el-tab-pane label="甲方信息" name="partyA">
            <el-form-item label="选择客户" required>
              <el-select-v2
                v-model="createForm.customer_id"
                :options="customerOptions"
                placeholder="搜索客户（自动填充甲方信息）"
                filterable
                clearable
                style="width: 100%"
                @change="onCustomerSelect"
              />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="甲方姓名">
                  <el-input v-model="createForm.variables.party_a_name" placeholder="姓名/名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="证件号码">
                  <el-input v-model="createForm.variables.party_a_id_card" placeholder="身份证号/统一社会信用代码" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="createForm.variables.party_a_phone" placeholder="甲方电话" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="房屋面积">
                  <el-input v-model="createForm.variables.party_a_area" placeholder="建筑面积">
                    <template #append>㎡</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="通讯地址">
              <el-input v-model="createForm.variables.party_a_address" placeholder="甲方住所/通讯地址" />
            </el-form-item>
          </el-tab-pane>

          <!-- Tab 3: 乙方信息 -->
          <el-tab-pane label="乙方信息" name="partyB">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司名称">
                  <el-input v-model="createForm.variables.party_b_company" placeholder="如：成都帝标家居有限公司" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="信用代码">
                  <el-input v-model="createForm.variables.party_b_credit_code" placeholder="统一社会信用代码" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="法定代表人">
                  <el-input v-model="createForm.variables.party_b_legal_person" placeholder="法定代表人" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公司电话">
                  <el-input v-model="createForm.variables.party_b_phone" placeholder="乙方联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="注册地址">
              <el-input v-model="createForm.variables.party_b_address" placeholder="乙方注册地址" />
            </el-form-item>

            <el-divider content-position="left">项目负责人信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="全案规划师">
                  <el-input v-model="createForm.variables.planner_name" placeholder="规划师姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="规划师电话">
                  <el-input v-model="createForm.variables.planner_phone" placeholder="规划师联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="全案设计师">
                  <el-input v-model="createForm.variables.designer_name" placeholder="设计师姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="设计师电话">
                  <el-input v-model="createForm.variables.designer_phone" placeholder="设计师联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="项目经理">
                  <el-input v-model="createForm.variables.pm_name" placeholder="项目经理姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目经理电话">
                  <el-input v-model="createForm.variables.pm_phone" placeholder="项目经理联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="工程监理">
                  <el-input v-model="createForm.variables.supervisor_name" placeholder="监理姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="监理电话">
                  <el-input v-model="createForm.variables.supervisor_phone" placeholder="监理联系电话" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- Tab 4: 装修信息 -->
          <el-tab-pane label="装修信息" name="construction">
            <el-form-item label="项目地址" required>
              <el-row :gutter="8" style="width:100%">
                <el-col :span="4">
                  <el-input v-model="createForm.variables.project_city" placeholder="市" />
                </el-col>
                <el-col :span="4">
                  <el-input v-model="createForm.variables.project_district" placeholder="区" />
                </el-col>
                <el-col :span="4">
                  <el-input v-model="createForm.variables.project_road" placeholder="路" />
                </el-col>
                <el-col :span="4">
                  <el-input v-model="createForm.variables.project_community" placeholder="小区" />
                </el-col>
                <el-col :span="2">
                  <el-input v-model="createForm.variables.project_building" placeholder="栋" />
                </el-col>
                <el-col :span="2">
                  <el-input v-model="createForm.variables.project_unit" placeholder="单元" />
                </el-col>
                <el-col :span="2">
                  <el-input v-model="createForm.variables.project_floor" placeholder="楼层" />
                </el-col>
                <el-col :span="2">
                  <el-input v-model="createForm.variables.project_room" placeholder="室号" />
                </el-col>
              </el-row>
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="建筑面积">
                  <el-input v-model="createForm.variables.construction_area" placeholder="面积">
                    <template #append>㎡</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="效果图数量">
                  <el-input v-model="createForm.variables.rendering_count" placeholder="张">
                    <template #append>张</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="承包方式">
                  <el-select v-model="createForm.variables.contract_method" style="width:100%" placeholder="选择承包方式">
                    <el-option label="设计+家具+软装" value="method1" />
                    <el-option label="设计+基础装修+主材+家具+软装" value="method2" />
                    <el-option label="设计+基础装修+家具+软装" value="method3" />
                    <el-option label="设计+主材+家具+软装" value="method4" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="工期天数">
                  <el-input v-model="createForm.variables.construction_days" placeholder="总日历工作日">
                    <template #append">天</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="开工日期">
                  <el-date-picker v-model="createForm.start_date" type="date" placeholder="开工日期" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="竣工日期">
                  <el-date-picker v-model="createForm.end_date" type="date" placeholder="竣工日期" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- Tab 5: 费用与付款 -->
          <el-tab-pane label="费用与付款" name="payment">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="合同总金额" required>
                  <el-input-number v-model="createForm.total_amount" :min="0" :precision="2" style="width:100%" @change="recalcAllPayments" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="金额大写">
                  <el-input v-model="amountInWords" readonly placeholder="自动生成" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="增项金额">
                  <el-input-number v-model="createForm.variables.extra_amount" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="设计费">
                  <el-input-number v-model="createForm.design_fee" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="施工费">
                  <el-input-number v-model="createForm.construction_fee" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="材料费">
                  <el-input-number v-model="createForm.material_fee" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="软装费">
                  <el-input-number v-model="createForm.soft_fee" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">收款信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="收款人姓名">
                  <el-input v-model="createForm.variables.payee_name" placeholder="收款人" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="收款人身份证">
                  <el-input v-model="createForm.variables.payee_id_card" placeholder="身份证号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="开户银行">
                  <el-input v-model="createForm.variables.bank_name" placeholder="开户银行" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="银行账号">
                  <el-input v-model="createForm.variables.bank_account" placeholder="银行账号" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">付款节点</el-divider>
            <div class="payment-schedule">
              <div v-for="(item, index) in createForm.payment_schedule" :key="index" class="payment-item">
                <el-row :gutter="8" align="middle">
                  <el-col :span="3">
                    <el-input v-model="item.phase_name" placeholder="阶段名称" />
                  </el-col>
                  <el-col :span="3">
                    <el-input v-model="item.node_desc" placeholder="节点说明" />
                  </el-col>
                  <el-col :span="3">
                    <el-input-number v-model="item.percentage" :min="0" :max="100" placeholder="占比%" style="width:100%" @change="recalcPaymentAmount(item)" />
                  </el-col>
                  <el-col :span="4">
                    <el-input-number v-model="item.amount" :min="0" :precision="2" placeholder="金额" style="width:100%" />
                  </el-col>
                  <el-col :span="5">
                    <el-date-picker v-model="item.planned_date" type="date" placeholder="计划日期" style="width:100%" />
                  </el-col>
                  <el-col :span="4">
                    <el-select v-model="item.phase" placeholder="阶段类型" style="width:100%">
                      <el-option v-for="p in options.payment_phases" :key="p.value" :label="p.label" :value="p.value" />
                    </el-select>
                  </el-col>
                  <el-col :span="2">
                    <el-button type="danger" link @click="removePayment(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" link @click="addPayment">
                <el-icon><Plus /></el-icon> 添加付款节点
              </el-button>
            </div>

            <el-divider content-position="left">报价表附件</el-divider>
            <el-form-item label="选择报价表">
              <el-select v-model="selectedQuoteId" placeholder="选择已有报价表作为附件" clearable style="width:100%" @change="onQuoteSelect">
                <el-option v-for="q in quoteList" :key="q.id" :label="q.quote_no + ' - ' + q.customer_name + ' (¥' + formatMoney(q.total_amount) + ')'" :value="q.id" />
              </el-select>
            </el-form-item>
            <div v-if="createForm.attachments && createForm.attachments.length" class="attachment-preview">
              <el-tag v-for="(att, idx) in createForm.attachments" :key="idx" closable @close="removeAttachment(idx)">
                {{ att.name }}
              </el-tag>
            </div>
          </el-tab-pane>

          <!-- Tab 6: 保修与违约 -->
          <el-tab-pane label="保修与违约" name="warranty">
            <el-divider content-position="left">保修期限</el-divider>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="基础装修">
                  <el-input v-model="createForm.variables.warranty_base" placeholder="年">
                    <template #append>年</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="防水防渗漏">
                  <el-input v-model="createForm.variables.warranty_waterproof" placeholder="年">
                    <template #append>年</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="定制家具">
                  <el-input v-model="createForm.variables.warranty_custom" placeholder="年">
                    <template #append>年</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="成品家具">
                  <el-input v-model="createForm.variables.warranty_finished" placeholder="年">
                    <template #append>年</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">违约条款</el-divider>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="违约金比例">
                  <el-input v-model="createForm.variables.breach_penalty_rate" placeholder="如5">
                    <template #append>%</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="逾期费率">
                  <el-input v-model="createForm.variables.overdue_rate" placeholder="如0.05">
                    <template #append">%/日</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="减项阈值">
                  <el-input v-model="createForm.variables.reduction_threshold" placeholder="项数" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="减项费率">
                  <el-input v-model="createForm.variables.reduction_fee_rate" placeholder="如10">
                    <template #append>%</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="远程费率">
                  <el-input v-model="createForm.variables.remote_rate" placeholder="如3">
                    <template #append>%</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="建渣清运费">
                  <el-input v-model="createForm.variables.debris_fee" placeholder="元" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="钥匙数量">
                  <el-input v-model="createForm.variables.key_count" placeholder="把" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="钥匙保管人">
                  <el-input v-model="createForm.variables.key_keeper" placeholder="保管人" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">争议解决</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="解决方式">
                  <el-select v-model="createForm.variables.dispute_method" style="width:100%">
                    <el-option label="仲裁" value="arbitration" />
                    <el-option label="诉讼" value="litigation" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="管辖法院/仲裁委">
                  <el-input v-model="createForm.variables.jurisdiction" placeholder="如：成都市青羊区人民法院" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <!-- Tab 7: 附加条款与签章 -->
          <el-tab-pane label="附加条款" name="extra">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="合同份数">
                  <el-input v-model="createForm.variables.contract_copies" placeholder="如：2" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="甲方执">
                  <el-input v-model="createForm.variables.party_a_copies" placeholder="份">
                    <template #append>份</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="乙方执">
                  <el-input v-model="createForm.variables.party_b_copies" placeholder="份">
                    <template #append>份</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">附加条款（最多5条）</el-divider>
            <el-form-item v-for="i in 5" :key="i" :label="'条款' + i">
              <el-input v-model="createForm.variables['extra_clause_' + i]" :placeholder="'附加条款内容 ' + i" type="textarea" :rows="2" />
            </el-form-item>

            <el-divider content-position="left">备注</el-divider>
            <el-form-item label="备注">
              <el-input v-model="createForm.remark" type="textarea" :rows="3" placeholder="合同其他备注说明" />
            </el-form-item>

            <el-divider content-position="left">签章信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="甲方签署日期">
                  <el-date-picker v-model="createForm.variables.party_a_sign_date" type="date" placeholder="甲方签署日期" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="乙方签署日期">
                  <el-date-picker v-model="createForm.variables.party_b_sign_date" type="date" placeholder="乙方签署日期" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="createDialog.visible = false">取消</el-button>
        <el-button @click="previewContract">预览</el-button>
        <el-button @click="saveDraft" :loading="createDialog.loading">保存草稿</el-button>
        <el-button type="warning" @click="submitForReview" :loading="createDialog.loading">提交审核</el-button>
        <el-button type="success" @click="exportPDF" :loading="createDialog.loading">导出PDF</el-button>
      </template>
    </el-dialog>

    <!-- ========== 全文预览弹窗 ========== -->
    <el-dialog v-model="previewFullDialog.visible" title="合同全文预览" width="65%" :close-on-click-modal="false">
      <div v-if="previewFullDialog.html" style="text-align:right;margin-bottom:8px;">
        <el-button type="primary" size="small" @click="() => { const w = window.open('', '_blank'); w.document.write(previewFullDialog.html); w.document.close(); w.print() }">打印</el-button>
      </div>
      <iframe v-if="previewFullDialog.html" :srcdoc="previewFullDialog.html" style="width:100%;height:70vh;border:none;" />
    </el-dialog>

    <!-- ========== 合同详情抽屉 ========== -->
    <el-drawer v-model="detailDrawer.visible" :title="detailDrawer.title" size="70%">
      <div v-if="detailDrawer.contract" class="contract-detail">
        <!-- 操作按钮 -->
        <div class="detail-actions" style="margin-bottom:12px;display:flex;gap:8px;">
          <el-button type="primary" size="small" @click="previewFullText">全文预览</el-button>
          <el-button size="small" @click="exportContractPdf">导出PDF</el-button>
        </div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="合同编号">{{ detailDrawer.contract.contract_no }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detailDrawer.contract.customer?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailDrawer.contract.status)">{{ statusLabel(detailDrawer.contract.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="合同金额">&yen;{{ formatMoney(detailDrawer.contract.total_amount) }}</el-descriptions-item>
          <el-descriptions-item label="设计费">&yen;{{ formatMoney(detailDrawer.contract.design_fee) }}</el-descriptions-item>
          <el-descriptions-item label="施工费">&yen;{{ formatMoney(detailDrawer.contract.construction_fee) }}</el-descriptions-item>
          <el-descriptions-item label="材料费">&yen;{{ formatMoney(detailDrawer.contract.material_fee) }}</el-descriptions-item>
          <el-descriptions-item label="软装费">&yen;{{ formatMoney(detailDrawer.contract.soft_fee) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 甲方信息 -->
        <div class="section" v-if="detailDrawer.contract.variables">
          <h4>甲方信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="甲方姓名">{{ detailDrawer.contract.variables.party_a_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="证件号码">{{ detailDrawer.contract.variables.party_a_id_card || '-' }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ detailDrawer.contract.variables.party_a_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="房屋面积">{{ detailDrawer.contract.variables.party_a_area ? detailDrawer.contract.variables.party_a_area + ' ㎡' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="通讯地址" :span="2">{{ detailDrawer.contract.variables.party_a_address || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 乙方信息 -->
        <div class="section" v-if="detailDrawer.contract.variables">
          <h4>乙方信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="公司名称">{{ detailDrawer.contract.variables.party_b_company || '-' }}</el-descriptions-item>
            <el-descriptions-item label="信用代码">{{ detailDrawer.contract.variables.party_b_credit_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="法定代表人">{{ detailDrawer.contract.variables.party_b_legal_person || '-' }}</el-descriptions-item>
            <el-descriptions-item label="公司电话">{{ detailDrawer.contract.variables.party_b_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="注册地址" :span="2">{{ detailDrawer.contract.variables.party_b_address || '-' }}</el-descriptions-item>
          </el-descriptions>
          <el-descriptions :column="2" border size="small" style="margin-top:8px" title="项目负责人">
            <el-descriptions-item label="全案规划师">{{ detailDrawer.contract.variables.planner_name || '-' }} {{ detailDrawer.contract.variables.planner_phone ? '(' + detailDrawer.contract.variables.planner_phone + ')' : '' }}</el-descriptions-item>
            <el-descriptions-item label="全案设计师">{{ detailDrawer.contract.variables.designer_name || '-' }} {{ detailDrawer.contract.variables.designer_phone ? '(' + detailDrawer.contract.variables.designer_phone + ')' : '' }}</el-descriptions-item>
            <el-descriptions-item label="项目经理">{{ detailDrawer.contract.variables.pm_name || '-' }} {{ detailDrawer.contract.variables.pm_phone ? '(' + detailDrawer.contract.variables.pm_phone + ')' : '' }}</el-descriptions-item>
            <el-descriptions-item label="工程监理">{{ detailDrawer.contract.variables.supervisor_name || '-' }} {{ detailDrawer.contract.variables.supervisor_phone ? '(' + detailDrawer.contract.variables.supervisor_phone + ')' : '' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 装修信息 -->
        <div class="section" v-if="detailDrawer.contract.variables">
          <h4>装修信息</h4>
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="项目地址" :span="3">
              {{ buildProjectAddress(detailDrawer.contract.variables) }}
            </el-descriptions-item>
            <el-descriptions-item label="建筑面积">{{ detailDrawer.contract.variables.construction_area ? detailDrawer.contract.variables.construction_area + ' ㎡' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="承包方式">{{ contractMethodLabel(detailDrawer.contract.variables.contract_method) }}</el-descriptions-item>
            <el-descriptions-item label="工期">{{ detailDrawer.contract.variables.construction_days ? detailDrawer.contract.variables.construction_days + ' 天' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="开工日期">{{ formatDate(detailDrawer.contract.start_date) }}</el-descriptions-item>
            <el-descriptions-item label="竣工日期">{{ formatDate(detailDrawer.contract.end_date) }}</el-descriptions-item>
            <el-descriptions-item label="效果图">{{ detailDrawer.contract.variables.rendering_count ? detailDrawer.contract.variables.rendering_count + ' 张' : '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 付款计划 -->
        <div class="section">
          <h4>付款计划</h4>
          <el-table :data="detailDrawer.contract.payments" size="small" border>
            <el-table-column prop="phase" label="阶段" width="120">
              <template #default="{ row }">{{ phaseLabel(row.phase) }}</template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" width="100">
              <template #default="{ row }">{{ row.percentage }}%</template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="150">
              <template #default="{ row }">&yen;{{ formatMoney(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="planned_date" label="计划日期" width="120">
              <template #default="{ row }">{{ formatDate(row.planned_date) }}</template>
            </el-table-column>
            <el-table-column prop="actual_date" label="实际日期" width="120">
              <template #default="{ row }">{{ formatDate(row.actual_date) || '-' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'paid' ? 'success' : 'info'" size="small">{{ row.status === 'paid' ? '已付' : '待付' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" type="primary" size="small" @click="openPayDialog(row)">收款</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 保修信息 -->
        <div class="section" v-if="detailDrawer.contract.variables">
          <h4>保修与违约</h4>
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="基础装修">{{ detailDrawer.contract.variables.warranty_base ? detailDrawer.contract.variables.warranty_base + ' 年' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="防水防渗漏">{{ detailDrawer.contract.variables.warranty_waterproof ? detailDrawer.contract.variables.warranty_waterproof + ' 年' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="定制家具">{{ detailDrawer.contract.variables.warranty_custom ? detailDrawer.contract.variables.warranty_custom + ' 年' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="成品家具">{{ detailDrawer.contract.variables.warranty_finished ? detailDrawer.contract.variables.warranty_finished + ' 年' : '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-drawer>

    <!-- ========== 收款对话框 ========== -->
    <el-dialog v-model="payDialog.visible" title="记录收款" width="500px">
      <el-form :model="payForm" label-width="100px">
        <el-form-item label="付款阶段"><span>{{ phaseLabel(payForm.phase) }}</span></el-form-item>
        <el-form-item label="金额"><span>&yen;{{ formatMoney(payForm.amount) }}</span></el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="payForm.payment_method" style="width:100%">
            <el-option label="现金" value="cash" />
            <el-option label="银行转账" value="transfer" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信支付" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="交易流水">
          <el-input v-model="payForm.transaction_no" />
        </el-form-item>
        <el-form-item label="付款日期">
          <el-date-picker v-model="payForm.actual_date" type="date" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="recordPayment" :loading="payDialog.loading">确认收款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const contracts = ref([])
const stats = ref({ by_status: {}, total_amount: 0 })
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filterForm = reactive({ keyword: '', status: '', contract_type: '' })
const options = reactive({ contract_types: [], status_list: [], payment_phases: [] })
const customerOptions = ref([])
const quoteList = ref([])
const selectedQuoteId = ref(null)

const createDialog = reactive({ visible: false, loading: false, isEdit: false, activeTab: 'basic' })
const detailDrawer = reactive({ visible: false, title: '', contract: null })
const payDialog = reactive({ visible: false, loading: false })

// 创建表单 - 包含合同范文所有字段
const createForm = reactive({
  customer_id: null,
  contract_type: 'all_in',
  title: '',
  contract_no: '',
  total_amount: 0,
  design_fee: 0,
  construction_fee: 0,
  material_fee: 0,
  soft_fee: 0,
  payment_schedule: [],
  start_date: null,
  end_date: null,
  remark: '',
  // 所有范文扩展字段存入 variables JSON
  variables: {
    sign_place: '',
    sign_date: null,
    // 甲方
    party_a_name: '',
    party_a_id_card: '',
    party_a_address: '',
    party_a_phone: '',
    party_a_area: '',
    // 乙方
    party_b_company: '',
    party_b_credit_code: '',
    party_b_address: '',
    party_b_legal_person: '',
    party_b_phone: '',
    // 乙方负责人
    planner_name: '',
    planner_phone: '',
    designer_name: '',
    designer_phone: '',
    pm_name: '',
    pm_phone: '',
    supervisor_name: '',
    supervisor_phone: '',
    // 装修信息
    project_city: '',
    project_district: '',
    project_road: '',
    project_community: '',
    project_building: '',
    project_unit: '',
    project_floor: '',
    project_room: '',
    construction_area: '',
    rendering_count: '',
    contract_method: '',
    construction_days: '',
    // 收款信息
    payee_name: '',
    payee_id_card: '',
    bank_name: '',
    bank_account: '',
    // 增项
    extra_amount: 0,
    // 保修
    warranty_base: '',
    warranty_waterproof: '',
    warranty_custom: '',
    warranty_finished: '',
    // 违约
    breach_penalty_rate: '',
    overdue_rate: '',
    reduction_threshold: '',
    reduction_fee_rate: '',
    remote_rate: '',
    debris_fee: '',
    key_count: '',
    key_keeper: '',
    // 争议
    dispute_method: '',
    jurisdiction: '',
    // 附加
    contract_copies: '',
    party_a_copies: '',
    party_b_copies: '',
    extra_clause_1: '',
    extra_clause_2: '',
    extra_clause_3: '',
    extra_clause_4: '',
    extra_clause_5: '',
    // 签章
    party_a_sign_date: null,
    party_b_sign_date: null,
  },
  attachments: []
})

const payForm = reactive({
  payment_id: null,
  phase: '',
  amount: 0,
  payment_method: 'transfer',
  transaction_no: '',
  actual_date: null
})

// 金额大写
const amountInWords = computed(() => {
  return numberToChinese(createForm.total_amount)
})

// 金额转大写
function numberToChinese(n) {
  if (!n || n === 0) return ''
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['', '拾', '佰', '仟']
  const bigUnits = ['', '万', '亿']
  const decUnits = ['角', '分']

  const num = Math.abs(n)
  const intPart = Math.floor(num)
  const decPart = Math.round((num - intPart) * 100)

  let result = ''
  if (intPart === 0) {
    result = ''
  } else {
    const intStr = intPart.toString()
    const len = intStr.length
    let zeroFlag = false
    for (let i = 0; i < len; i++) {
      const d = parseInt(intStr[i])
      const pos = len - 1 - i
      const bigUnitIdx = Math.floor(pos / 4)
      const unitIdx = pos % 4

      if (d === 0) {
        zeroFlag = true
        if (unitIdx === 0 && bigUnitIdx > 0) {
          result += bigUnits[bigUnitIdx]
        }
      } else {
        if (zeroFlag) { result += '零'; zeroFlag = false }
        result += digits[d] + units[unitIdx]
        if (unitIdx === 0 && bigUnitIdx > 0) {
          result += bigUnits[bigUnitIdx]
        }
      }
    }
    result += '元'
  }

  if (decPart === 0) {
    result += '整'
  } else {
    const jiao = Math.floor(decPart / 10)
    const fen = decPart % 10
    if (jiao > 0) result += digits[jiao] + decUnits[0]
    else if (intPart > 0) result += '零'
    if (fen > 0) result += digits[fen] + decUnits[1]
  }

  return result
}

// 客户选择时自动填充甲方信息
const onCustomerSelect = async (customerId) => {
  if (!customerId) return
  try {
    const res = await request.get(`/customers/${customerId}`)
    const c = res
    createForm.variables.party_a_name = c.name || ''
    createForm.variables.party_a_phone = c.phone || ''
    createForm.variables.party_a_address = c.address || ''
    createForm.variables.party_a_id_card = c.id_card || ''
    createForm.variables.party_a_area = c.house_area || ''
    // 加载该客户的报价表
    loadQuotes(customerId)
  } catch (e) {
    console.error('加载客户详情失败', e)
  }
}

// 加载客户相关报价表
const loadQuotes = async (customerId) => {
  if (!customerId) {
    quoteList.value = []
    return
  }
  try {
    const res = await request.get(`/quotes`, { params: { customer_id: customerId, page_size: 100 } })
    quoteList.value = res.items || []
  } catch (e) {
    console.error('加载报价表失败', e)
  }
}

// 选择报价表作为附件
const onQuoteSelect = (quoteId) => {
  if (!quoteId) return
  const quote = quoteList.value.find(q => q.id === quoteId)
  if (!quote) return
  // 添加到附件列表
  if (!createForm.attachments) createForm.attachments = []
  // 避免重复添加
  if (createForm.attachments.some(a => a.quote_id === quoteId)) {
    ElMessage.warning('该报价表已添加')
    return
  }
  createForm.attachments.push({
    name: `报价单-${quote.quote_no}`,
    type: 'quote',
    quote_id: quote.id,
    url: quote.pdf_path || ''
  })
  selectedQuoteId.value = null // 重置选择
  ElMessage.success('报价表已添加为附件')
}

// 删除附件
const removeAttachment = (index) => {
  createForm.attachments.splice(index, 1)
}

// 重建项目地址
const buildProjectAddress = (v) => {
  if (!v) return '-'
  const parts = [v.project_city, v.project_district, v.project_road, v.project_community,
    v.project_building ? v.project_building + '栋' : '',
    v.project_unit ? v.project_unit + '单元' : '',
    v.project_floor ? v.project_floor + '楼' : '',
    v.project_room ? v.project_room + '室' : ''
  ].filter(Boolean)
  return parts.length > 0 ? parts.join('') : '-'
}

// 承包方式标签
const contractMethodLabel = (method) => {
  const map = {
    method1: '设计+家具+软装',
    method2: '设计+基础装修+主材+家具+软装',
    method3: '设计+基础装修+家具+软装',
    method4: '设计+主材+家具+软装',
  }
  return map[method] || method || '-'
}

// ====== 数据加载 ======
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/contracts', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status,
        contract_type: filterForm.contract_type
      }
    })
    contracts.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await request.get('/contracts/statistics')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadOptions = async () => {
  try {
    const res = await request.get('/contracts/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const loadCustomers = async () => {
  try {
    const res = await request.get('/customers', { params: { page_size: 1000 } })
    customerOptions.value = res.items.map(c => ({
      value: c.id,
      label: `${c.name} (${c.phone})`
    }))
  } catch (error) {
    console.error('加载客户失败', error)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  filterForm.contract_type = ''
  loadData()
}

// ====== 创建合同 ======
const openCreateDialog = () => {
  createDialog.visible = true
  createDialog.isEdit = false
  createDialog.activeTab = 'basic'
  // 重置表单
  createForm.customer_id = null
  createForm.contract_type = 'all_in'
  createForm.title = ''
  createForm.contract_no = ''
  createForm.total_amount = 0
  createForm.design_fee = 0
  createForm.construction_fee = 0
  createForm.material_fee = 0
  createForm.soft_fee = 0
  createForm.payment_schedule = []
  createForm.start_date = null
  createForm.end_date = null
  createForm.remark = ''
  // 重置 variables
  Object.keys(createForm.variables).forEach(k => {
    if (typeof createForm.variables[k] === 'number') createForm.variables[k] = 0
    else createForm.variables[k] = null
  })
  createForm.variables.extra_amount = 0
  loadCustomers()
}

const addPayment = () => {
  createForm.payment_schedule.push({
    phase: '',
    phase_name: `第${createForm.payment_schedule.length + 1}期`,
    node_desc: '',
    percentage: 0,
    amount: 0,
    planned_date: null
  })
}

const removePayment = (index) => {
  createForm.payment_schedule.splice(index, 1)
}

const recalcPaymentAmount = (item) => {
  if (createForm.total_amount > 0 && item.percentage > 0) {
    item.amount = Math.round(createForm.total_amount * item.percentage / 100 * 100) / 100
  }
}

const recalcAllPayments = () => {
  if (createForm.total_amount > 0 && createForm.payment_schedule.length > 0) {
    createForm.payment_schedule.forEach(item => {
      if (item.percentage > 0) {
        item.amount = Math.round(createForm.total_amount * item.percentage / 100 * 100) / 100
      }
    })
  }
}

watch(() => createForm.total_amount, () => recalcAllPayments())

// ====== 合同操作 ======
const previewContract = async () => {
  if (!createForm.customer_id) { ElMessage.warning('请先选择客户'); return }
  createDialog.loading = true
  try {
    const res = await request.post('/contracts/preview', createForm)
    detailDrawer.contract = res
    detailDrawer.title = `合同预览 - ${res.contract_no || '预览'}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '预览失败')
  } finally {
    createDialog.loading = false
  }
}

const saveDraft = async () => {
  if (!createForm.customer_id) { ElMessage.warning('请选择客户'); return }
  createDialog.loading = true
  try {
    await request.post('/contracts', { ...createForm, status: 'draft' })
    ElMessage.success('草稿保存成功')
    createDialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    createDialog.loading = false
  }
}

// ====== 全文预览 ======
const previewFullDialog = ref({ visible: false, html: '', loading: false })
const previewFullText = async () => {
  if (!detailDrawer.contract?.id) { ElMessage.warning('请先打开合同详情'); return }
  previewFullDialog.loading = true
  try {
    const res = await request.get(`/contracts/${detailDrawer.contract.id}/preview-full`)
    previewFullDialog.html = res.html
    previewFullDialog.visible = true
  } catch (error) {
    console.error('预览加载失败', error)
    ElMessage.error(error.response?.data?.message || '加载预览失败，请重试')
  } finally {
    previewFullDialog.loading = false
  }
}

const exportContractPdf = async () => {
  if (!detailDrawer.contract?.id) return
  // 调 preview-full 端点，生成完整HTML，直接用 iframe 打印
  const res = await request.get(`/contracts/${detailDrawer.contract.id}/preview-full`)
  const printWin = window.open('', '_blank')
  if (printWin) {
    printWin.document.write(res.html)
    printWin.document.close()
    printWin.onload = () => printWin.print()
  }
}

const submitForReview = async () => {
  if (!createForm.customer_id) { ElMessage.warning('请选择客户'); return }
  createDialog.loading = true
  try {
    await request.post('/contracts', { ...createForm, status: 'pending_review' })
    ElMessage.success('已提交审核')
    createDialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '提交失败')
  } finally {
    createDialog.loading = false
  }
}

const exportPDF = async () => {
  if (!createForm.customer_id) { ElMessage.warning('请先选择客户'); return }
  createDialog.loading = true
  try {
    const res = await request.post('/contracts/export-pdf', createForm)
    if (res.html) {
      const blob = new Blob([res.html], { type: 'text/html;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', res.filename || `合同_${createForm.title || 'draft'}.html`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功，请用浏览器打开后打印为PDF')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '导出失败')
  } finally {
    createDialog.loading = false
  }
}

// ====== 详情 ======
const viewDetail = async (row) => {
  try {
    const res = await request.get(`/contracts/${row.id}`)
    detailDrawer.contract = res
    detailDrawer.title = `合同详情 - ${res.contract_no}`
    detailDrawer.visible = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// ====== 更多操作 ======
const handleCommand = async (command, row) => {
  const actions = {
    submit: () => doAction(row.id, 'submit', '提交'),
    sign_customer: () => doSign(row.id, 'customer'),
    sign_company: () => doSign(row.id, 'company'),
    execute: () => doAction(row.id, 'execute', '开始执行'),
    complete: () => doAction(row.id, 'complete', '完成'),
    cancel: () => doCancel(row.id)
  }
  if (actions[command]) actions[command]()
}

const doAction = async (id, action, label) => {
  try {
    await ElMessageBox.confirm(`确定要${label}吗？`, '提示', { type: 'warning' })
    await request.post(`/contracts/${id}/${action}`)
    ElMessage.success('操作成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const doSign = async (id, signer) => {
  try {
    await request.post(`/contracts/${id}/sign`, { signer })
    ElMessage.success('签署成功')
    loadData()
  } catch (error) {
    ElMessage.error('签署失败')
  }
}

const doCancel = async (id) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入取消原因', '取消合同', {
      confirmButtonText: '确认', cancelButtonText: '取消', inputType: 'textarea'
    })
    await request.post(`/contracts/${id}/cancel`, { reason: value })
    ElMessage.success('已取消')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('取消失败')
  }
}

// ====== 收款 ======
const openPayDialog = (row) => {
  payForm.payment_id = row.id
  payForm.phase = row.phase
  payForm.amount = row.amount
  payForm.payment_method = 'transfer'
  payForm.transaction_no = ''
  payForm.actual_date = new Date()
  payDialog.visible = true
}

const recordPayment = async () => {
  payDialog.loading = true
  try {
    await request.post(`/contracts/${detailDrawer.contract.id}/payments/${payForm.payment_id}/pay`, payForm)
    ElMessage.success('收款记录成功')
    payDialog.visible = false
    viewDetail({ id: detailDrawer.contract.id })
    loadStats()
  } catch (error) {
    ElMessage.error('记录失败')
  } finally {
    payDialog.loading = false
  }
}

// ====== 辅助函数 ======
const statusType = (status) => {
  const types = { draft: 'info', pending: 'warning', signed: 'success', executing: 'primary', completed: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

const statusLabel = (status) => {
  const labels = { draft: '草稿', pending: '待签署', signed: '已签署', executing: '执行中', completed: '已完成', cancelled: '已取消' }
  return labels[status] || status
}

const typeLabel = (type) => {
  const labels = { design: '设计合同', construction: '施工合同', all_in: '全案合同', soft: '软装合同', custom: '定制合同' }
  return labels[type] || type
}

const phaseLabel = (phase) => {
  const labels = { deposit: '定金', first: '首付款', progress: '进度款', final: '尾款', quality: '质保金' }
  return labels[phase] || phase
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
  loadStats()
  loadOptions()
})
</script>

<style scoped>
.contract-manage { padding: 24px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-header h2 { margin: 0; }

.stats-row { margin-bottom: 24px; }

.stat-card { text-align: center; }
.stat-card .stat-value { font-size: 24px; font-weight: bold; color: #262626; }
.stat-card .stat-label { font-size: 12px; color: #8c8c8c; margin-top: 4px; }
.stat-card.total .stat-value { color: #52c41a; }

.filter-card { margin-bottom: 24px; }

.customer-name { font-weight: 500; color: #262626; }
.contract-title { font-weight: 500; color: #262626; }
.contract-type { font-size: 12px; color: #8c8c8c; margin-top: 4px; }
.amount { font-weight: 500; color: #f5222d; margin-bottom: 4px; }
.sign-status { margin-bottom: 4px; }

.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }

.payment-schedule {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.payment-item { width: 100%; }

.contract-detail { padding: 16px; }
.contract-detail .section { margin-top: 24px; }
.contract-detail .section h4 { margin-bottom: 12px; color: #262626; font-weight: 500; border-left: 3px solid #409eff; padding-left: 8px; }

.contract-form :deep(.el-tabs__content) { padding: 16px; }
</style>
