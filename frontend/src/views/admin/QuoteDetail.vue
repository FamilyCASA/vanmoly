<template>
  <div class="quote-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <span class="quote-no" style="cursor:pointer" title="点击复制报价单号" @click="copyQuoteNo">
            {{ quote.quote_no }} <el-icon><DocumentCopy /></el-icon>
          </span>
          <el-tag :type="statusType(quote.status)" size="small" style="margin-left: 8px">
            {{ statusLabel(quote.status) }}
          </el-tag>
        </template>
        <template #extra>
          <el-button-group>
            <el-button type="primary" @click="editQuote" v-if="quote.status === 'draft'">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button type="success" @click="handleExportPDF">
              <el-icon><Printer /></el-icon> 导出PDF
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button>
                更多操作 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="copy">复制报价</el-dropdown-item>
                  <el-dropdown-item command="convert" v-if="quote.status === 'accepted'">转订单</el-dropdown-item>
                  <el-dropdown-item command="export">导出PDF</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-button-group>
        </template>
      </el-page-header>
    </div>

    <!-- 基本信息 -->
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <div v-if="quote.status === 'draft'">
            <el-button v-if="!isEditingBasic" size="small" @click="startEditBasic">编辑</el-button>
            <template v-else>
              <el-button size="small" @click="cancelEditBasic">取消</el-button>
              <el-button type="primary" size="small" @click="saveBasicInfo" :loading="basicSaving">保存</el-button>
            </template>
          </div>
        </div>
      </template>
      <el-descriptions v-if="!isEditingBasic" :column="4" border>
        <el-descriptions-item label="客户姓名">{{ quote.customer_name || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ quote.customer_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户地址">{{ quote.customer_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报价日期">{{ formatDate(quote.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="项目地址">{{ quote.project_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="有效期至">{{ quote.valid_until ? formatDate(quote.valid_until) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="设计师">{{ quote.designer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="销售顾问">{{ quote.sales_name || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-form v-else :model="basicForm" label-width="100px" style="max-width:900px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户">
              <el-select v-model="basicForm.customer_id" filterable remote :remote-method="searchCustomers" placeholder="搜索客户姓名/电话" style="width:100%">
                <el-option v-for="c in customerOptions" :key="c.id" :label="c.name + ' ' + (c.phone||'')" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报价单号">
              <el-input v-model="basicForm.quote_no" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目地址">
              <el-input v-model="basicForm.project_address" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="basicForm.valid_until" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 服务团队 -->
    <el-card shadow="never" class="service-team-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>服务团队</span>
          <el-button
            v-if="quote.status === 'draft'"
            type="primary"
            size="small"
            @click="saveServiceTeam"
            :loading="savingServiceTeam"
          >保存</el-button>
        </div>
      </template>
      <el-row :gutter="16">
        <el-col :span="6" v-for="role in SERVICE_TEAM_ROLES" :key="role.value">
          <div class="team-role">
            <div class="role-label">{{ role.label }}</div>
            <el-select
              v-if="quote.status === 'draft'"
              v-model="serviceTeam[role.value]"
              filterable
              :placeholder="'选择' + role.label"
              style="width:100%"
              clearable
            >
              <el-option
                v-for="e in allEmployees"
                :key="e.id"
                :label="e.name"
                :value="e.id"
              />
            </el-select>
            <div v-else class="role-value">
              {{ getEmployeeName(serviceTeam[role.value]) || '未分配' }}
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 报价模板 -->
    <el-card shadow="never" class="template-card" v-loading="loadingTemplates">
      <template #header>
        <div class="card-header">
          <span>报价模板</span>
          <el-button type="primary" size="small" @click="applyTemplate" :disabled="!selectedTemplateId">应用</el-button>
        </div>
      </template>
      <div class="template-grid">
        <div
          v-for="tpl in templates"
          :key="tpl.id"
          class="template-item"
          :class="{ active: selectedTemplateId === tpl.id }"
          @click="selectedTemplateId = tpl.id"
        >
          <div class="template-preview">{{ tpl.template_type || '标准' }}</div>
          <div class="template-name">{{ tpl.name }}</div>
        </div>
        <el-empty v-if="!templates.length" description="暂无模板" :image-size="60" />
      </div>
    </el-card>

    <!-- 报价空间 -->
    <el-card shadow="never" class="spaces-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>报价空间 ({{ spaces.length }}个)</span>
          <el-button type="primary" size="small" @click="addSpace" v-if="quote.status === 'draft'">
            <el-icon><Plus /></el-icon> 添加空间
          </el-button>
        </div>
      </template>

      <!-- 新格式：空间实例 - 自定义水平Tab布局 -->
      <div v-if="!useLegacyView" class="spaces-container">
        <!-- 空间Tab栏 - 水平排列，自动换行 -->
        <div class="space-tabs">
          <div
            v-for="space in spaces"
            :key="space.id"
            class="space-tab"
            :class="{ active: activeSpaceId === space.id }"
            @click="switchSpace(space.id)"
          >
            <span class="tab-name">{{ space.space_name }}</span>
            <el-tag
              class="tab-count"
              :type="activeSpaceId === space.id ? 'primary' : 'info'"
              size="small"
              effect="plain"
            >
              {{ space.items?.length || 0 }}
            </el-tag>
            <el-dropdown
              v-if="quote.status === 'draft'"
              @command="(cmd) => handleSpaceCommand(cmd, space)"
              trigger="click"
              @click.stop
            >
              <el-icon class="tab-more"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">重命名</el-dropdown-item>
                  <el-dropdown-item command="copy">复制空间</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <!-- 添加空间按钮 -->
          <div
            class="space-tab add-space-tab"
            @click="addSpace"
            v-if="quote.status === 'draft'"
          >
            <el-icon><Plus /></el-icon>
            <span>添加空间</span>
          </div>
        </div>

        <!-- 当前激活空间的内容 -->
        <div v-if="activeSpace" class="space-content">
          <!-- 空间概览 -->
          <div class="space-overview">
            <el-row :gutter="16">
              <el-col :span="6">
                <el-statistic title="物料数量" :value="activeSpace.material_count || activeSpace.items?.length || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="物料成本" :value="activeSpace.material_cost || 0" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="工艺费用" :value="activeSpace.labor_cost || 0" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="小计" :value="activeSpace.total_price || 0" :precision="2" prefix="¥" />
              </el-col>
            </el-row>
          </div>

          <!-- 物料明细 -->
          <el-table :data="activeSpace.items" stripe style="margin-top: 16px" border size="small">
            <el-table-column type="index" width="45" label="#" />
            <el-table-column prop="custom_name" label="自定义名称" min-width="120">
              <template #default="{ row }">{{ row.custom_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="category_level1" label="第一类别" width="90">
              <template #default="{ row }">{{ row.category_level1 || '-' }}</template>
            </el-table-column>
            <el-table-column prop="category_level2" label="第二类别" width="90">
              <template #default="{ row }">{{ row.category_level2 || '-' }}</template>
            </el-table-column>
            <el-table-column prop="material_name" label="物料名称" min-width="120">
              <template #default="{ row }">{{ row.material_name || row.sku_name || row.name || '-' }}</template>
            </el-table-column>
            <el-table-column label="定制数据" width="140" align="center">
              <template #default="{ row }">
                <span v-if="row.custom_width || row.custom_depth || row.custom_height">
                  {{ row.custom_width || '-' }}×{{ row.custom_depth || '-' }}×{{ row.custom_height || '-' }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="measurement_value" label="计量值" width="70" align="right">
              <template #default="{ row }">{{ row.measurement_value || '-' }}</template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="55" align="center" />
            <el-table-column prop="quantity" label="数量" width="65" align="right" />
            <el-table-column label="单价" width="80" align="right">
              <template #default="{ row }">¥{{ row.unit_price }}</template>
            </el-table-column>
            <el-table-column prop="process_name" label="工艺名称" width="100">
              <template #default="{ row }">{{ row.process_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="process_coefficient" label="工艺系数" width="75" align="right">
              <template #default="{ row }">{{ row.process_coefficient != null && row.process_coefficient !== 1 ? row.process_coefficient : '-' }}</template>
            </el-table-column>
            <el-table-column prop="process_quantity" label="工艺数量" width="75" align="right">
              <template #default="{ row }">{{ row.process_quantity || '-' }}</template>
            </el-table-column>
            <el-table-column label="工艺金额" width="80" align="right">
              <template #default="{ row }">{{ row.process_amount ? '¥' + row.process_amount : '-' }}</template>
            </el-table-column>
            <el-table-column label="金额" width="100" align="right">
              <template #default="{ row }"><span class="amount">¥{{ row.total_price || row.row_total }}</span></template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" width="100">
              <template #default="{ row }">{{ row.remark || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right" v-if="quote.status === 'draft'">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editItem(activeSpace, row)">编辑</el-button>
                <el-button link type="success" size="small" @click="cloneItem(activeSpace, row)">克隆</el-button>
                <el-button link type="danger" size="small" @click="deleteItem(activeSpace, row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 添加物料按钮 -->
          <div class="add-item-area" v-if="quote.status === 'draft'">
            <el-button
              type="primary"
              @click="addItemToActiveSpace"
              class="add-item-btn"
            >
              <el-icon><Plus /></el-icon>
              添加物料到「{{ activeSpace.space_name }}」
            </el-button>
          </div>
        </div>

        <!-- 无激活空间 -->
        <el-empty v-if="!activeSpace" description="请选择一个空间" />
      </div>

      <!-- 旧格式：扁平物料按房间分组 -->
      <el-tabs v-else v-model="activeLegacyRoom" type="card">
        <el-tab-pane
          v-for="group in legacyGrouped"
          :key="group.room_name"
          :label="group.room_name"
          :name="group.room_name"
        >
          <div class="space-overview">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-statistic title="物料数量" :value="group.items.length" />
              </el-col>
              <el-col :span="8">
                <el-statistic title="房间小计" :value="group.total" :precision="2" prefix="¥" />
              </el-col>
              <el-col :span="8">
                <el-tag type="info">旧版报价格式</el-tag>
              </el-col>
            </el-row>
          </div>

          <el-table :data="group.items" stripe style="margin-top: 16px" border size="small">
            <el-table-column type="index" width="45" label="#" />
            <el-table-column prop="custom_name" label="自定义名称" min-width="120">
              <template #default="{ row }">{{ row.custom_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="category_level1" label="第一类别" width="90">
              <template #default="{ row }">{{ row.category_level1 || '-' }}</template>
            </el-table-column>
            <el-table-column prop="category_level2" label="第二类别" width="90">
              <template #default="{ row }">{{ row.category_level2 || '-' }}</template>
            </el-table-column>
            <el-table-column prop="material_name" label="物料名称" min-width="120">
              <template #default="{ row }">{{ row.material_name || row.sku_name || row.name || '-' }}</template>
            </el-table-column>
            <el-table-column label="定制数据" width="140" align="center">
              <template #default="{ row }">
                <span v-if="row.custom_width || row.custom_depth || row.custom_height">
                  {{ row.custom_width || '-' }}×{{ row.custom_depth || '-' }}×{{ row.custom_height || '-' }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="measurement_value" label="计量值" width="70" align="right">
              <template #default="{ row }">{{ row.measurement_value || '-' }}</template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="55" align="center" />
            <el-table-column prop="quantity" label="数量" width="65" align="right" />
            <el-table-column label="单价" width="80" align="right">
              <template #default="{ row }">¥{{ row.unit_price }}</template>
            </el-table-column>
            <el-table-column prop="process_name" label="工艺名称" width="100">
              <template #default="{ row }">{{ row.process_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="process_coefficient" label="工艺系数" width="75" align="right">
              <template #default="{ row }">{{ row.process_coefficient != null && row.process_coefficient !== 1 ? row.process_coefficient : '-' }}</template>
            </el-table-column>
            <el-table-column prop="process_quantity" label="工艺数量" width="75" align="right">
              <template #default="{ row }">{{ row.process_quantity || '-' }}</template>
            </el-table-column>
            <el-table-column label="工艺金额" width="80" align="right">
              <template #default="{ row }">{{ row.process_amount ? '¥' + row.process_amount : '-' }}</template>
            </el-table-column>
            <el-table-column label="金额" width="100" align="right">
              <template #default="{ row }"><span class="amount">¥{{ row.total_price || row.row_total }}</span></template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" width="100">
              <template #default="{ row }">{{ row.remark || '-' }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- 无任何数据 -->
      <el-empty v-if="!useLegacyView && spaces.length === 0" description="暂无报价明细" />
    </el-card>

    <!-- 费用汇总 -->
    <el-card shadow="never" class="summary-card">
      <template #header>
        <div class="card-header">
          <span>费用汇总</span>
        </div>
      </template>
      <el-row :gutter="32">
        <el-col :span="16">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="物料总额">
              ¥{{ formatMoney(quote.material_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="工艺费用">
              ¥{{ formatMoney(quote.craft_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="设计费用">
              ¥{{ formatMoney(quote.design_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="安装费用">
              ¥{{ formatMoney(quote.install_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="管理费率">
              {{ quote.manage_rate || 0 }}%
            </el-descriptions-item>
            <el-descriptions-item label="管理费">
              ¥{{ formatMoney(quote.manage_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="税额">
              ¥{{ formatMoney(quote.tax_amount) }}
            </el-descriptions-item>
            <el-descriptions-item label="优惠金额">
              <span class="discount">-¥{{ formatMoney(quote.discount_amount) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
        <el-col :span="8">
          <div class="total-box">
            <div class="total-label">报价总额</div>
            <div class="total-value">¥{{ formatMoney(quote.total_amount) }}</div>
            <div class="total-words">（大写：{{ moneyToChinese(quote.total_amount) }}）</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 备注信息 -->
    <el-card shadow="never" class="remark-card">
      <template #header>
        <div class="card-header">
          <span>备注信息</span>
        </div>
      </template>
      <el-input
        v-model="quote.remark"
        type="textarea"
        :rows="4"
        readonly
        placeholder="暂无备注"
      />
    </el-card>

    <!-- 签字区 -->
    <el-card shadow="never" class="sign-card">
      <template #header>
        <div class="card-header">
          <span>签字确认</span>
        </div>
      </template>
      <el-row :gutter="32">
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">客户签字</div>
            <div class="sign-value">{{ quote.customer_sign || '待签字' }}</div>
            <div class="sign-date" v-if="quote.customer_sign_date">
              {{ formatDate(quote.customer_sign_date) }}
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">设计师签字</div>
            <div class="sign-value">{{ quote.designer_sign || '待签字' }}</div>
            <div class="sign-date" v-if="quote.designer_sign_date">
              {{ formatDate(quote.designer_sign_date) }}
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="sign-box">
            <div class="sign-label">公司盖章</div>
            <div class="sign-value">{{ quote.company_seal ? '已盖章' : '待盖章' }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 编辑物料对话框 -->
    <el-dialog v-model="itemDialogVisible" :title="itemForm.id ? '编辑物料' : '新建物料'" width="680px">
      <el-form :model="itemForm" label-width="90px">
        <el-form-item label="自定义名称">
          <el-input v-model="itemForm.custom_name" placeholder="自定义显示名称（可选）" />
        </el-form-item>
        <el-form-item label="物料名称">
          <div style="display:flex;gap:8px;width:100%">
            <el-input v-model="itemForm.name" placeholder="输入物料名称" />
            <el-button @click="openMaterialPicker" type="info" plain>从库选择</el-button>
          </div>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="itemForm.quantity" :min="0.1" :precision="2" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="itemForm.unit" placeholder="项/m²/m/个" style="width:120px" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="itemForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-divider content-position="left">定制参数</el-divider>
        <el-form-item label="宽(cm)">
          <el-input-number v-model="itemForm.custom_width" :min="0" :precision="0" placeholder="定制宽度" />
        </el-form-item>
        <el-form-item label="深(cm)">
          <el-input-number v-model="itemForm.custom_depth" :min="0" :precision="0" placeholder="定制深度" />
        </el-form-item>
        <el-form-item label="高(cm)">
          <el-input-number v-model="itemForm.custom_height" :min="0" :precision="0" placeholder="定制高度" />
        </el-form-item>
        <el-form-item label="计量值">
          <el-input-number v-model="itemForm.measurement_value" :min="0" :precision="4" placeholder="自动/手动" />
        </el-form-item>
        <el-divider content-position="left">工艺信息</el-divider>
        <el-form-item label="工艺名称">
          <el-input v-model="itemForm.process_name" placeholder="例如：烤漆、覆膜" />
        </el-form-item>
        <el-form-item label="工艺系数">
          <el-input-number v-model="itemForm.process_coefficient" :min="0" :precision="3" placeholder="默认1" />
        </el-form-item>
        <el-form-item label="工艺数量">
          <el-input-number v-model="itemForm.process_quantity" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="工艺单价">
          <el-input-number v-model="itemForm.process_unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="工艺金额">
          <el-input-number v-model="itemForm.process_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-divider content-position="left">其他</el-divider>
        <el-form-item label="备注">
          <el-input v-model="itemForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>

    <!-- 物料选择器 -->
    <el-dialog v-model="skuPickerVisible" title="从物料库选择" width="700px" append-to-body>
      <div style="margin-bottom:12px">
        <el-input
          v-model="skuKeyword"
          placeholder="搜索物料名称/编码/品牌"
          clearable
          @keyup.enter="searchSku()"
          @clear="searchSku()"
          style="width:300px"
        >
          <template #append>
            <el-button @click="searchSku()" :loading="skuLoading">搜索</el-button>
          </template>
        </el-input>
      </div>
      <el-table :data="skuList" v-loading="skuLoading" max-height="400" highlight-current-row @row-click="selectSku">
        <el-table-column prop="sku_code" label="编码" width="100" />
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="sale_price" label="售价" width="80" align="right">
          <template #default="{ row }">{{ row.sale_price?.toFixed(2) || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click.stop="selectSku(row)">选择</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:12px;text-align:right">
        <el-pagination
          v-model:current-page="skuPage"
          :total="skuTotal"
          :page-size="20"
          layout="prev, pager, next"
          @current-change="searchSku"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, Printer, ArrowDown, Plus, DocumentCopy, MoreFilled
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const SERVICE_TEAM_ROLES = [
  { value: 'designer', label: '设计师' },
  { value: 'sales', label: '销售顾问' },
  { value: 'project_manager', label: '项目经理' },
  { value: 'construction_leader', label: '施工队长' }
]

const route = useRoute()
const router = useRouter()

// 报价ID
const quoteId = computed(() => route.params.id)

// 数据
const loading = ref(false)
const quote = ref({})
const spaces = ref([])
const activeSpaceId = ref('') // 当前激活的空间ID

// 基本信息编辑
const isEditingBasic = ref(false)
const basicSaving = ref(false)
const basicForm = reactive({
  customer_id: null,
  quote_no: '',
  project_address: '',
  valid_until: ''
})
const customerOptions = ref([])

// 服务团队（4个固定角色）
const serviceTeam = reactive({
  designer: null,
  sales: null,
  project_manager: null,
  construction_leader: null
})
const allEmployees = ref([])
const savingServiceTeam = ref(false)

// 报价模板
const templates = ref([])
const selectedTemplateId = ref(null)
const loadingTemplates = ref(false)

const loadTemplates = async () => {
  try {
    loadingTemplates.value = true
    const res = await request.get('/quotes/templates')
    templates.value = res.data?.data || res.data || []
    // 当前报价已选模板
    if (quote.value?.cover_template_id) {
      selectedTemplateId.value = quote.value.cover_template_id
    }
  } catch (e) {
    console.error('加载模板失败', e)
  } finally {
    loadingTemplates.value = false
  }
}

const applyTemplate = async () => {
  if (!selectedTemplateId.value) return
  try {
    await request.put(`/quotes/${quoteId.value}`, { cover_template_id: selectedTemplateId.value })
    ElMessage.success('模板已应用')
    quote.value.cover_template_id = selectedTemplateId.value
  } catch (e) {
    ElMessage.error('应用模板失败')
  }
}

// 当前激活的空间对象
const activeSpace = computed(() => {
  if (!activeSpaceId.value || !spaces.value.length) return null
  return spaces.value.find(s => String(s.id) === String(activeSpaceId.value))
})

// 状态映射
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  sent: { label: '已发送', type: 'warning' },
  accepted: { label: '已接受', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  expired: { label: '已过期', type: 'info' }
}

const statusLabel = (status) => statusMap[status]?.label || status
const statusType = (status) => statusMap[status]?.type || 'info'

// 格式化
const formatMoney = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 金额转中文大写
const moneyToChinese = (money) => {
  if (!money || money === 0) return '零元整'
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
  const decimalUnits = ['角', '分']
  
  const str = Math.abs(money).toFixed(2)
  const [integerPart, decimalPart] = str.split('.')
  
  let result = ''
  
  // 整数部分
  const intStr = integerPart.toString()
  for (let i = 0; i < intStr.length; i++) {
    const digit = parseInt(intStr[i])
    const unitIndex = intStr.length - 1 - i
    result += digits[digit] + units[unitIndex]
  }
  result = result.replace(/零+$/, '').replace(/零{2,}/g, '零')
  
  // 小数部分
  if (decimalPart && decimalPart !== '00') {
    for (let i = 0; i < decimalPart.length && i < 2; i++) {
      const digit = parseInt(decimalPart[i])
      if (digit !== 0) {
        result += digits[digit] + decimalUnits[i]
      }
    }
  }
  
  result += '元整'
  return result
}

// 旧报价扁平物料（按room_name分组）
const legacyItems = ref([])
const legacyGrouped = computed(() => {
  if (!legacyItems.value.length) return []
  const groups = {}
  for (const item of legacyItems.value) {
    const room = item.room_name || '未分类'
    if (!groups[room]) {
      groups[room] = { room_name: room, items: [], total: 0 }
    }
    groups[room].items.push(item)
    groups[room].total += Number(item.total_price || 0)
  }
  return Object.values(groups)
})
const useLegacyView = computed(() => spaces.value.length === 0 && legacyItems.value.length > 0)
const activeLegacyRoom = ref('')

// 加载数据
const loadQuote = async () => {
  loading.value = true
  try {
    const res = await request.get(`/quotes/${quoteId.value}`)
    quote.value = res || {}
    
    // 加载空间实例
    try {
      const spacesRes = await request.get(`/quotes/${quoteId.value}/space-instances`)
      spaces.value = Array.isArray(spacesRes) ? spacesRes : []
    } catch (e) {
      spaces.value = []
    }
    
    if (spaces.value.length > 0) {
      // 优先恢复上次激活的空间
      const savedSpaceId = localStorage.getItem('activeSpaceId')
      if (savedSpaceId && spaces.value.find(s => String(s.id) === String(savedSpaceId))) {
        activeSpaceId.value = String(savedSpaceId)
      } else {
        activeSpaceId.value = String(spaces.value[0].id)
      }
    } else {
      // 降级：使用报价自带的扁平items按room_name分组
      const flatItems = quote.value.items || []
      if (flatItems.length > 0) {
        legacyItems.value = flatItems
        const firstRoom = legacyGrouped.value[0]?.room_name
        if (firstRoom) activeLegacyRoom.value = firstRoom
      }
      loadServiceTeam()
    }
  } catch (error) {
    ElMessage.error('加载报价失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 基本信息编辑
const startEditBasic = () => {
  basicForm.customer_id = quote.value.customer_id || null
  basicForm.quote_no = quote.value.quote_no || ''
  basicForm.project_address = quote.value.project_address || ''
  basicForm.valid_until = quote.value.valid_until || ''
  isEditingBasic.value = true
}

const cancelEditBasic = () => {
  isEditingBasic.value = false
}

const saveBasicInfo = async () => {
  basicSaving.value = true
  try {
    await request.put(`/quotes/${quoteId.value}`, { ...basicForm })
    ElMessage.success('保存成功')
    isEditingBasic.value = false
    loadQuote()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    basicSaving.value = false
  }
}

const searchCustomers = async (query) => {
  if (!query) { customerOptions.value = []; return }
  try {
    const res = await request.get('/customers', { params: { keyword: query, page_size: 20 } })
    customerOptions.value = res.data || res || []
  } catch (e) { /* ignore */ }
}

// 服务团队
const loadAllEmployees = async () => {
  try {
    const res = await request.get('/quotes/options')
    allEmployees.value = res.data?.employees || []
  } catch (e) { /* ignore */ }
}

const loadServiceTeam = () => {
  const st = quote.value.service_team || []
  serviceTeam.designer = null
  serviceTeam.sales = null
  serviceTeam.project_manager = null
  serviceTeam.construction_leader = null
  st.forEach(item => {
    if (item.role && serviceTeam[item.role] !== undefined) {
      serviceTeam[item.role] = item.employee_id || null
    }
  })
}

const saveServiceTeam = async () => {
  savingServiceTeam.value = true
  try {
    const st = []
    SERVICE_TEAM_ROLES.forEach(r => {
      if (serviceTeam[r.value]) {
        const emp = allEmployees.value.find(e => e.id === serviceTeam[r.value])
        st.push({
          role: r.value,
          employee_id: serviceTeam[r.value],
          name: emp ? emp.name : ''
        })
      }
    })
    await request.put(`/quotes/${quoteId.value}`, { service_team: st })
    ElMessage.success('服务团队已保存')
    loadQuote()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    savingServiceTeam.value = false
  }
}

// 获取员工姓名
const getEmployeeName = (id) => {
  if (!id) return ''
  const emp = allEmployees.value.find(e => e.id === id)
  return emp ? emp.name : ''
}

// 返回
const goBack = () => {
  router.push('/admin/quotes')
}

// 编辑报价
const editQuote = () => {
  router.push(`/admin/quotes/${quoteId.value}/edit`)
}

// 导出PDF（携带token，fetch+blob触发下载）
const handleExportPDF = async () => {
  const id = quoteId.value
  try {
    // 从 localStorage 取 token（与 request.js 一致）
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token') || ''
    const resp = await fetch(`/api/v3/quotes/${id}/pdf`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!resp.ok) {
      ElMessage.error('下载失败，请先生成PDF')
      return
    }
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `报价单_${quote.value?.quote_no || id}_访客版.pdf`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('PDF 下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出PDF失败')
  }
}

// 下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'copy':
      copyQuote()
      break
    case 'convert':
      ElMessage.info('转订单功能开发中')
      break
    case 'export':
      handleExportPDF()
      break
    case 'delete':
      ElMessageBox.confirm('确定要删除该报价吗？', '提示', {
        type: 'warning'
      }).then(() => {
        ElMessage.success('删除成功')
        goBack()
      }).catch(() => {})
      break
  }
}

// 复制报价单号到剪贴板
const copyQuoteNo = () => {
  const no = quote.value?.quote_no
  if (!no) return
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(no).then(() => {
      ElMessage.success(`报价单号 ${no} 已复制`)
    }).catch(() => {
      ElMessage.error('复制失败，请手动复制')
    })
  } else {
    const ta = document.createElement('textarea')
    ta.value = no
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success(`报价单号 ${no} 已复制`)
  }
}

// 复制报价（跳转新建页面并预填）
const copyQuote = () => {
  router.push({ path: '/admin/quotes/from-case', query: { from: quoteId.value } })
}

// ========== 新增：空间管理方法 ==========

// 切换空间
const switchSpace = (spaceId) => {
  activeSpaceId.value = String(spaceId)
  localStorage.setItem('activeSpaceId', String(spaceId))
}

// 处理空间下拉菜单命令
const handleSpaceCommand = (command, space) => {
  switch (command) {
    case 'edit':
      editSpace(space)
      break
    case 'copy':
      copySpace(space)
      break
    case 'delete':
      deleteSpace(space)
      break
  }
}

// 编辑空间名称
const editSpace = async (space) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的空间名称', '编辑空间', {
      inputValue: space.space_name,
      inputPlaceholder: '请输入空间名称'
    })
    if (!value || !value.trim()) {
      ElMessage.warning('空间名称不能为空')
      return
    }
    await request.put(`/quotes/${quoteId.value}/space-instances/${space.id}`, {
      space_name: value.trim()
    })
    ElMessage.success('空间名称已更新')
    loadQuote()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 复制空间（包括物料）
const copySpace = async (space) => {
  try {
    await ElMessageBox.confirm('确定要复制该空间及其所有物料吗？', '提示', { type: 'warning' })
    ElMessage.info('复制空间功能开发中')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 删除空间
const deleteSpace = async (space) => {
  try {
    await ElMessageBox.confirm(`确定要删除空间「${space.space_name}」吗？`, '提示', { type: 'warning' })
    await request.delete(`/quotes/${quoteId.value}/space-instances/${space.id}`)
    ElMessage.success('空间已删除')
    
    // 如果删除的是当前激活的空间，切换到下一个
    if (String(space.id) === activeSpaceId.value) {
      const idx = spaces.value.findIndex(s => String(s.id) === String(space.id))
      const next = spaces.value[idx + 1] || spaces.value[idx - 1]
      if (next) {
        switchSpace(next.id)
      } else {
        activeSpaceId.value = ''
        localStorage.removeItem('activeSpaceId')
      }
    }
    
    loadQuote()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 添加物料到当前激活的空间
const addItemToActiveSpace = () => {
  if (!activeSpace.value) {
    ElMessage.warning('请先选择一个空间')
    return
  }
  
  // 打开物料选择对话框
  itemForm.id = null
  itemForm.space_id = activeSpace.value.id
  itemForm.sku_id = null
  itemForm.custom_name = ''
  itemForm.name = ''
  itemForm.quantity = 1
  itemForm.unit_price = 0
  itemForm.unit = ''
  itemForm.measurement_value = null
  itemForm.remark = ''
  itemForm.custom_width = null
  itemForm.custom_depth = null
  itemForm.custom_height = null
  itemForm.custom_result = ''
  itemForm.process_name = ''
  itemForm.process_coefficient = null
  itemForm.process_quantity = null
  itemForm.process_unit_price = null
  itemForm.process_amount = null
  itemForm.craft_type = ''
  itemForm.craft_price = 0
  itemForm.craft_quantity = null
  itemForm.craft_coefficient = null
  itemDialogVisible.value = true
}

// 添加空间
const addSpace = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入空间名称', '添加空间', {
      inputPlaceholder: '例如：客厅、卧室、厨房等'
    })
    if (!value || !value.trim()) {
      ElMessage.warning('空间名称不能为空')
      return
    }
    await request.post(`/quotes/${quoteId.value}/space-instances`, {
      space_name: value.trim()
    })
    ElMessage.success('空间添加成功')
    await loadQuote()
    
    // 自动激活新创建的空间
    const newSpace = spaces.value[spaces.value.length - 1]
    if (newSpace) {
      switchSpace(newSpace.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('添加失败')
    }
  }
}

// ========== 结束新增方法 ==========

// 编辑物料
const itemDialogVisible = ref(false)
const itemForm = reactive({
  id: null,
  space_id: null,
  sku_id: null,
  custom_name: '',
  name: '',
  quantity: 1,
  unit_price: 0,
  unit: '',
  measurement_value: null,
  remark: '',
  custom_width: null,
  custom_depth: null,
  custom_height: null,
  custom_result: '',
  process_name: '',
  process_coefficient: null,
  process_quantity: null,
  process_unit_price: null,
  process_amount: null,
  craft_type: '',
  craft_price: 0,
  craft_quantity: null,
  craft_coefficient: null
})

const editItem = (space, item) => {
  itemForm.id = item.id
  itemForm.space_id = space.id || null
  itemForm.sku_id = item.sku_id || null
  itemForm.custom_name = item.custom_name || ''
  itemForm.name = item.name || item.sku_name || item.material_name || ''
  itemForm.quantity = item.quantity
  itemForm.unit_price = item.unit_price
  itemForm.unit = item.unit || ''
  itemForm.measurement_value = item.measurement_value || null
  itemForm.remark = item.remark || ''
  itemForm.custom_width = item.custom_width || null
  itemForm.custom_depth = item.custom_depth || null
  itemForm.custom_height = item.custom_height || null
  itemForm.custom_result = item.custom_result || ''
  itemForm.process_name = item.process_name || ''
  itemForm.process_coefficient = item.process_coefficient || null
  itemForm.process_quantity = item.process_quantity || null
  itemForm.process_unit_price = item.process_unit_price || null
  itemForm.process_amount = item.process_amount || null
  itemForm.craft_type = item.craft_type || ''
  itemForm.craft_price = item.craft_price || 0
  itemForm.craft_quantity = item.craft_quantity || null
  itemForm.craft_coefficient = item.craft_coefficient || null
  itemDialogVisible.value = true
}

// 保存物料（支持新增和编辑）
const saveItem = async () => {
  try {
    if (itemForm.id) {
      // 编辑模式：旧格式（space_id=null）走直连路径，新格式走 space-instances 路径
      const path = itemForm.space_id == null
        ? `/quotes/${quoteId.value}/items/${itemForm.id}`
        : `/quotes/${quoteId.value}/space-instances/${itemForm.space_id}/items/${itemForm.id}`
      await request.put(path, itemForm)
      ElMessage.success('保存成功')
    } else {
      // 新增模式：POST（必须先有 space_id，新建 item 需要空间上下文）
      await request.post(
        `/quotes/${quoteId.value}/space-instances/${itemForm.space_id}/items`,
        itemForm
      )
      ElMessage.success('添加成功')
    }
    itemDialogVisible.value = false
    loadQuote()
  } catch (error) {
    ElMessage.error(itemForm.id ? '保存失败' : '添加失败')
  }
}

const deleteItem = async (space, item) => {
  try {
    await ElMessageBox.confirm('确定要删除该物料吗？', '提示', { type: 'warning' })
    // 旧格式（space 无 .id）走直连路径
    const path = space.id == null
      ? `/quotes/${quoteId.value}/items/${item.id}`
      : `/quotes/${quoteId.value}/space-instances/${space.id}/items/${item.id}`
    await request.delete(path)
    ElMessage.success('删除成功')
    loadQuote()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const cloneItem = async (space, item) => {
  try {
    await ElMessageBox.confirm('确认克隆该物料？', '提示', { type: 'info' })
    const payload = { ...item }
    delete payload.id
    const path = space.id
      ? `/quotes/${quoteId.value}/spaces/${space.id}/items`
      : `/quotes/${quoteId.value}/items`
    await request.post(path, payload)
    ElMessage.success('克隆成功')
    loadQuote()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.message || '克隆失败')
  }
}

// 物料选择器
const skuPickerVisible = ref(false)
const skuKeyword = ref('')
const skuList = ref([])
const skuLoading = ref(false)
const skuPage = ref(1)
const skuTotal = ref(0)

const searchSku = async (page = 1) => {
  try {
    skuLoading.value = true
    skuPage.value = page
    const res = await request.get('/materials', { params: { keyword: skuKeyword.value, page, page_size: 20 } })
    const data = res.data?.data || res.data
    skuList.value = data.items || data || []
    skuTotal.value = data.total || 0
  } catch (e) {
    console.error('搜索物料失败', e)
  } finally {
    skuLoading.value = false
  }
}

const openMaterialPicker = () => {
  skuPickerVisible.value = true
  skuKeyword.value = ''
  searchSku()
}

const selectSku = (sku) => {
  itemForm.sku_id = sku.id
  itemForm.name = sku.name
  itemForm.unit_price = sku.sale_price || 0
  if (sku.specification) itemForm.remark = sku.specification + (itemForm.remark ? '\n' + itemForm.remark : '')
  skuPickerVisible.value = false
  ElMessage.success(`已选择: ${sku.name}`)
}

onMounted(() => {
  loadQuote()
  loadAllEmployees()
  loadTemplates()
})
</script>

<style scoped>
.quote-detail {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.quote-no {
  font-size: 18px;
  font-weight: 600;
}

.info-card,
.spaces-card,
.summary-card,
.remark-card,
.sign-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-overview {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.amount {
  color: #409eff;
  font-weight: 600;
}

.summary-card .total-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.total-label {
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.total-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.total-words {
  font-size: 12px;
  opacity: 0.8;
}

.discount {
  color: #67c23a;
  font-weight: 600;
}

.sign-box {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  text-align: center;
}

.sign-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.sign-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.sign-date {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* ========== 新增：自定义空间Tab样式 ========== */
.spaces-container {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
}

.space-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  align-items: center;
}

.space-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
  font-size: 14px;
  color: #606266;
  user-select: none;
}

.space-tab:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.space-tab.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.space-tab .tab-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.space-tab .tab-count {
  margin-left: 4px;
}

.space-tab .tab-more {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.space-tab:hover .tab-more {
  opacity: 1;
}

.space-tab.add-space-tab {
  border-style: dashed;
  color: #909399;
  background: transparent;
}

.space-tab.add-space-tab:hover {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}

.space-content {
  padding: 20px;
  min-height: 200px;
}

.add-item-area {
  margin-top: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
  text-align: center;
}

.add-item-btn {
  width: 100%;
  max-width: 500px;
  height: 48px;
  font-size: 15px;
}

:deep(.el-descriptions__label) {
  width: 100px;
}

/* 服务团队卡片 */
.service-team-card .team-role {
  text-align: center;
  padding: 8px 4px;
}
.service-team-card .role-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}
.service-team-card .role-value {
  font-size: 14px;
  color: #303133;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-card .template-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.template-card .template-item {
  width: 120px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.template-card .template-item:hover {
  border-color: #409eff;
}
.template-card .template-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}
.template-card .template-preview {
  height: 60px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #909399;
}
.template-card .template-name {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
