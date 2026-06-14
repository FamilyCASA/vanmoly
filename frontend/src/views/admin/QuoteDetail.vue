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
            <el-button type="primary" @click="saveAll" :loading="savingAll" v-if="quote.status === 'draft'">
              <el-icon><DocumentChecked /></el-icon> 保存
            </el-button>
            <el-button type="success" @click="submitForReview" v-if="quote.status === 'draft'">
              <el-icon><Check /></el-icon> 提交审核
            </el-button>
            <el-button type="warning" @click="saveAsTemplate">
              <el-icon><DocumentCopy /></el-icon> 另存为模板
            </el-button>
            <el-button type="info" @click="showHtmlPreview">
              <el-icon><View /></el-icon> 预览
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button>
                更多操作 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-item command="copy">复制报价</el-dropdown-item>
                <el-dropdown-item command="convert" v-if="quote.status === 'accepted'">转订单</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </template>
            </el-dropdown>
          </el-button-group>
        </template>
      </el-page-header>
    </div>

    <!-- 基本信息 + 服务团队（合并，可直接编辑） -->
    <!-- 基本信息卡片（美化版） -->
    <div class="info-section">
      <!-- 客户信息区 -->
      <div class="info-grid">
        <div class="info-field">
          <label class="field-label">客户</label>
          <el-select 
            v-if="quote.status === 'draft'"
            v-model="quoteInfo.customer_id" 
            filterable 
            remote 
            :remote-method="searchCustomers" 
            placeholder="搜索客户姓名/电话"
            size="default"
            @change="onCustomerChange"
          >
            <el-option v-for="c in customerOptions" :key="c.id" :label="c.name + ' ' + (c.phone||'')" :value="c.id" />
          </el-select>
          <div v-else class="field-value-static">{{ quote.customer_name || '未设置' }}</div>
        </div>
        <div class="info-field">
          <label class="field-label">联系电话</label>
          <div class="field-value-static">{{ quoteInfo.customer_phone || quote.customer_phone || '-' }}</div>
        </div>
        <div class="info-field">
          <label class="field-label">楼盘</label>
          <div class="field-value-static">{{ quoteInfo.building_name || quote.building_name || '-' }}</div>
        </div>
        <div class="info-field">
          <label class="field-label">户型</label>
          <div class="field-value-static">{{ quoteInfo.house_type || quote.house_type || '-' }}</div>
        </div>
        <div class="info-field field-wide">
          <label class="field-label">项目地址</label>
          <el-input 
            v-if="quote.status === 'draft'"
            v-model="quoteInfo.project_address" 
            placeholder="项目地址"
            size="default"
          />
          <div v-else class="field-value-static">{{ quote.project_address || '-' }}</div>
        </div>
        <div class="info-field">
          <label class="field-label">报价有效期</label>
          <el-date-picker 
            v-if="quote.status === 'draft'"
            v-model="quoteInfo.valid_until" 
            type="date" 
            value-format="YYYY-MM-DD"
            size="default"
            placeholder="选择有效期"
          />
          <div v-else class="field-value-static">{{ quote.expire_date ? formatDate(quote.expire_date) : (quote.valid_until ? formatDate(quote.valid_until) : '-') }}</div>
        </div>
        <div class="info-field">
          <label class="field-label">报价日期</label>
          <div class="field-value-static">{{ formatDate(quote.created_at) }}</div>
        </div>
      </div>

      <!-- 服务团队区 -->
      <div class="team-section">
        <div class="section-title">服务团队</div>
        <div class="team-grid">
          <div class="team-item" v-for="role in QUOTE_TEAM_ROLES" :key="role.value">
            <div class="team-role-name">{{ role.label }}</div>
            <el-select
              v-if="quote.status === 'draft' && role.value !== 'auditor'"
              v-model="serviceTeam[role.value]"
              filterable
              size="small"
              clearable
              placeholder="选择人员"
            >
              <el-option v-for="e in allEmployees" :key="e.id" :label="e.name" :value="e.id" />
            </el-select>
            <el-select
              v-else-if="quote.status === 'draft' && role.value === 'auditor'"
              v-model="serviceTeam[role.value]"
              disabled
              size="small"
              placeholder="提交后自动填充"
            >
              <el-option v-for="e in allEmployees" :key="e.id" :label="e.name" :value="e.id" />
            </el-select>
            <div v-else class="team-member-name">{{ getEmployeeName(serviceTeam[role.value]) || '未分配' }}</div>
          </div>
        </div>
      </div>
    </div>

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
          <div class="fee-summary-table">
            <!-- 自动统计（只读） -->
            <div class="fee-row">
              <span class="fee-label">物料总额</span>
              <span class="fee-value readonly">¥{{ formatMoney(quote.material_amount) }}</span>
              <span class="fee-label">工艺费用</span>
              <span class="fee-value readonly">¥{{ formatMoney(quote.craft_amount) }}</span>
            </div>
            <!-- 手动输入 -->
            <div class="fee-row">
              <span class="fee-label">管理费率</span>
              <el-input-number
                v-model="quote.manage_rate"
                :precision="1" :step="0.5" :min="0" :max="100" size="small"
                controls-position="right" @change="onMgmtRateChange" />
              <span style="color:#999;font-size:13px;">%</span>
              <span class="fee-label">管理费</span>
              <el-input-number
                v-model="quote.manage_amount"
                :precision="2" :step="100" :min="0" size="small"
                controls-position="right" @change="onFeeChange" />
            </div>
            <div class="fee-row">
              <span class="fee-label">税额</span>
              <el-input-number
                v-model="quote.tax_amount"
                :precision="2" :step="100" :min="0" size="small"
                controls-position="right" @change="onFeeChange" />
              <span class="fee-label">优惠比例</span>
              <el-input-number
                v-model="quote.discount_rate"
                :precision="1" :step="0.5" :min="0" :max="100" size="small"
                controls-position="right" @change="onDiscountRateChange" />
              <span style="color:#999;font-size:13px;">%</span>
            </div>
          </div>
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



    <!-- HTML预览对话框 -->
    <el-dialog v-model="htmlPreviewVisible" title="报价单预览" width="90%" top="3vh" :fullscreen="false">
      <iframe :src="htmlPreviewUrl" style="width:100%;height:80vh;border:1px solid #eee;border-radius:4px;"></iframe>
      <template #footer>
        <el-button @click="htmlPreviewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExportPDF">下载 PDF</el-button>
      </template>
    </el-dialog>

    <!-- 编辑物料对话框 -->
    <el-dialog v-model="itemDialogVisible" :title="itemForm.id ? '编辑物料' : '新建物料'" width="680px">
      <el-form :model="itemForm" label-width="90px">
        <!-- SKU来源标识 -->
        <el-form-item v-if="itemForm.sku_id" label="物料库">
          <el-tag type="success" size="small">已关联 SKU #{{ itemForm.sku_id }}</el-tag>
          <span v-if="itemForm.calc_type" style="margin-left:8px;color:#909399;font-size:12px">计量类型: {{ itemForm.calc_type }}</span>
        </el-form-item>
        <el-form-item label="自定义名称">
          <el-input v-model="itemForm.custom_name" placeholder="自定义显示名称（可选）" />
        </el-form-item>
        <el-form-item label="物料名称">
          <div style="display:flex;gap:8px;width:100%">
            <el-input v-model="itemForm.name" placeholder="输入物料名称" />
            <el-button @click="openMaterialPicker" type="info" plain>从库选择</el-button>
          </div>
        </el-form-item>
        <el-form-item label="分类">
          <div style="display:flex;gap:8px">
            <el-input v-model="itemForm.category_level1" placeholder="一级分类" style="width:140px" />
            <el-input v-model="itemForm.category_level2" placeholder="二级分类" style="width:140px" />
          </div>
        </el-form-item>
        <el-form-item label="品牌/材质">
          <div style="display:flex;gap:8px">
            <el-input v-model="itemForm.brand" placeholder="品牌" style="width:140px" />
            <el-input v-model="itemForm.material" placeholder="材质" style="width:140px" />
          </div>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="itemForm.quantity" :min="0.1" :precision="2" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="itemForm.unit" placeholder="项/m²/m/个" style="width:120px" @change="calcMeasurementValue" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="itemForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-divider content-position="left">定制参数</el-divider>
        <el-form-item label="宽(mm)">
          <el-input-number v-model="itemForm.custom_width" :min="0" :precision="0" placeholder="定制宽度" @change="calcMeasurementValue" />
        </el-form-item>
        <el-form-item label="深(mm)">
          <el-input-number v-model="itemForm.custom_depth" :min="0" :precision="0" placeholder="定制深度" @change="calcMeasurementValue" />
        </el-form-item>
        <el-form-item label="高(mm)">
          <el-input-number v-model="itemForm.custom_height" :min="0" :precision="0" placeholder="定制高度" @change="calcMeasurementValue" />
        </el-form-item>
        <el-form-item label="计量值">
          <span style="font-size:16px;font-weight:600;color:#303133">{{ measurementCache }}</span>
          <span style="margin-left: 8px; color: #909399; font-size: 12px">{{ itemForm.unit || '' }}</span>
        </el-form-item>
        <el-divider content-position="left">工艺信息</el-divider>
        <el-form-item label="工艺名称">
          <el-select
            v-model="itemForm.process_name"
            filterable
            placeholder="选择或搜索工艺（如：烤漆、覆膜）"
            style="width: 100%"
            :loading="craftLoading"
            @change="onCraftSelected"
          >
            <el-option
              v-for="c in craftOptions"
              :key="c.id"
              :label="c.name + (c.category ? ' [' + c.category + ']' : '')"
              :value="c.name"
            >
              <span>{{ c.name }}</span>
              <span style="color:#999;font-size:12px;float:right">{{ c.category || '' }} · 系数{{ c.coefficient }}</span>
            </el-option>
          </el-select>
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
    <el-dialog v-model="skuPickerVisible" title="从物料库选择" width="1100px" append-to-body>
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
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="100" show-overflow-tooltip />
        <el-table-column prop="material" label="材质" width="80" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column prop="calc_type" label="计量" width="70">
          <template #default="{ row }">{{ row.calc_type || '-' }}</template>
        </el-table-column>
        <el-table-column prop="sale_price" label="售价" width="80" align="right">
          <template #default="{ row }">¥{{ row.sale_price?.toFixed(2) || '-' }}</template>
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

    <!-- 计量规则管理对话框 -->
    <el-dialog v-model="showRulesEditor" title="计量规则管理" width="900px" destroy-on-close>
      <el-table :data="measurementRules" stripe border size="small" max-height="500">
        <el-table-column type="index" width="40" label="#" />
        <el-table-column prop="name" label="规则名称" width="120" />
        <el-table-column prop="rule_type" label="规则类型" width="100">
          <template #default="{ row }">{{ ruleTypeName(row.rule_type) }}</template>
        </el-table-column>
        <el-table-column label="匹配条件" width="180">
          <template #default="{ row }">
            <span>{{ matchFieldLabel(row.match_field) }}: {{ row.match_value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="70" align="center" />
        <el-table-column label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" size="small" @change="toggleRule(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editRule(row)">编辑</el-button>
            <el-button link type="warning" size="small" @click="moveRule(row, -1)">↑</el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 12px; text-align: right;">
        <el-button type="primary" @click="addNewRule">添加规则</el-button>
      </div>
    </el-dialog>

    <!-- 规则编辑对话框 -->
    <el-dialog v-model="showRuleForm" :title="editingRule.id ? '编辑规则' : '新建规则'" width="600px" append-to-body destroy-on-close>
      <el-form :model="editingRule" label-width="100px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="editingRule.name" placeholder="例：门套计量" />
        </el-form-item>
        <el-form-item label="规则类型" required>
          <el-select v-model="editingRule.rule_type" placeholder="选择规则类型">
            <el-option label="长度计量" value="length" />
            <el-option label="面积计量" value="area" />
            <el-option label="体积计量" value="volume" />
            <el-option label="固定值" value="fixed_override" />
            <el-option label="高度补足" value="adjust_height" />
            <el-option label="面积保底" value="adjust_min_area" />
            <el-option label="门套/垭口套" value="door_frame" />
            <el-option label="四方轮廓" value="four_sided" />
            <el-option label="赠送归零" value="process_free" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配字段">
          <el-select v-model="editingRule.match_field">
            <el-option label="单位(unit)" value="unit" />
            <el-option label="二级分类(category_level2)" value="category_level2" />
            <el-option label="自定义名称(custom_name)" value="custom_name" />
            <el-option label="物料名称(name)" value="name" />
            <el-option label="工艺名称(process_name)" value="process_name" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配值" required>
          <el-input v-model="editingRule.match_value" placeholder="关键词或匹配值，多个用逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editingRule.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="editingRule.priority" :min="1" :max="999" />
          <span style="margin-left:8px;color:#999">数值越小越优先</span>
        </el-form-item>
        <el-form-item v-if="editingRule.rule_type === 'fixed_override'" label="固定值">
          <el-input-number v-model="editingRule.rule_params.value" :min="0" :precision="4" />
        </el-form-item>
        <el-form-item v-if="editingRule.rule_type === 'adjust_height'" label="高度阈值">
          <div v-for="(t, idx) in editingRule.rule_params.thresholds" :key="idx" style="display:flex;gap:8px;margin-bottom:6px;align-items:center">
            <span>高度 &lt; </span>
            <el-input-number v-model="t.min" :min="0" size="small" />
            <span>→ 调为</span>
            <el-input-number v-model="t.adjust_to" :min="0" size="small" />
            <el-button link type="danger" size="small" @click="editingRule.rule_params.thresholds.splice(idx, 1)">删</el-button>
          </div>
          <el-button size="small" @click="(editingRule.rule_params.thresholds || (editingRule.rule_params.thresholds = [])).push({min:0, adjust_to:1000})">添加阈值</el-button>
        </el-form-item>
        <el-form-item v-if="editingRule.rule_type === 'adjust_min_area'" label="最小面积">
          <el-input-number v-model="editingRule.rule_params.min_value" :min="0" :precision="4" />
          <span style="margin-left:8px">㎡</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRuleForm = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, Printer, ArrowDown, Plus, DocumentCopy, MoreFilled, Check, DocumentChecked
} from '@element-plus/icons-vue'
import request from '@/utils/request'

// 服务团队角色（报价单用）
const QUOTE_TEAM_ROLES = [
  { value: 'quoter', label: '报价员' },
  { value: 'auditor', label: '审核员' },
  { value: 'designer', label: '全案设计师' },
  { value: 'planner', label: '全案规划师' },
  { value: 'project_manager', label: '项目经理' }
]

// 兼容旧代码
const SERVICE_TEAM_ROLES = QUOTE_TEAM_ROLES

const route = useRoute()
const router = useRouter()

// 报价ID
const quoteId = computed(() => route.params.id)

// 数据
const loading = ref(false)
const quote = ref({})
const spaces = ref([])
const activeSpaceId = ref('') // 当前激活的空间ID

// 基本信息 + 服务团队（合并编辑）
const savingQuoteInfo = ref(false)
const quoteInfo = reactive({
  customer_id: null,
  customer_phone: '',
  customer_address: '',
  building_name: '',
  house_type: '',
  project_address: '',
  valid_until: ''
})
// 服务团队单独用 ref 确保响应式
const serviceTeam = ref({
  quoter: null,
  auditor: null,
  designer: null,
  planner: null,
  project_manager: null
})
const customerOptions = ref([])
const allEmployees = ref([])

// 兼容旧代码
const isEditingBasic = ref(false)
const basicSaving = ref(false)
const basicForm = reactive({
  customer_id: null,
  quote_no: '',
  project_address: '',
  valid_until: ''
})
const savingServiceTeam = ref(false)

// 报价模板
const templates = ref([])
const selectedTemplateId = ref(null)
const loadingTemplates = ref(false)

const loadTemplates = async () => {
  try {
    loadingTemplates.value = true
    const res = await request.get('/quotes/templates')
    // 拦截器已解包，res 直接是数组或 {items:[...]}
    templates.value = Array.isArray(res) ? res : (res?.items || [])
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

// ========== 计量规则 ==========
const measurementRules = ref([])
const showRulesEditor = ref(false)
const showRuleForm = ref(false)
const editingRule = reactive({
  id: null, name: '', description: '', match_type: 'keyword_category',
  match_value: '', match_field: 'unit', rule_type: 'length',
  rule_params: {}, priority: 100, is_enabled: true, sort_order: 0
})

const ruleTypeName = (type) => {
  const map = {
    length: '长度', area: '面积', volume: '体积', fixed_override: '固定值',
    adjust_height: '高度补足', adjust_min_area: '面积保底',
    door_frame: '门套/垭口套', four_sided: '四方轮廓', process_free: '赠送归零'
  }
  return map[type] || type
}

const ruleTypeTag = (type) => {
  const map = {
    length: '', area: '', volume: '', fixed_override: 'info',
    adjust_height: 'warning', adjust_min_area: 'warning',
    door_frame: 'success', four_sided: 'success', process_free: 'danger'
  }
  return map[type] || 'info'
}

const matchFieldLabel = (field) => {
  const map = {
    unit: '单位', category_level2: '二级分类', custom_name: '自定义名称',
    name: '物料名称', process_name: '工艺名称'
  }
  return map[field] || field
}

const loadMeasurementRules = async () => {
  try {
    const res = await request.get('/quotes/measurement-rules')
    // 拦截器已解包
    measurementRules.value = Array.isArray(res) ? res : (res?.items || [])
    if (!measurementRules.value.length) {
      await request.post('/quotes/measurement-rules/init')
      const res2 = await request.get('/quotes/measurement-rules')
      measurementRules.value = Array.isArray(res2) ? res2 : (res2?.items || [])
    }
  } catch (e) {
    console.error('加载计量规则失败', e)
  }
}

const toggleRule = async (rule) => {
  try {
    await request.put(`/quotes/measurement-rules/${rule.id}`, { is_enabled: rule.is_enabled })
  } catch (e) {
    rule.is_enabled = !rule.is_enabled
    ElMessage.error('更新失败')
  }
}

const editRule = (rule) => {
  Object.assign(editingRule, {
    id: rule.id, name: rule.name, description: rule.description,
    match_type: rule.match_type, match_value: rule.match_value,
    match_field: rule.match_field, rule_type: rule.rule_type,
    rule_params: JSON.parse(JSON.stringify(rule.rule_params || {})),
    priority: rule.priority, is_enabled: rule.is_enabled, sort_order: rule.sort_order
  })
  showRuleForm.value = true
}

const addNewRule = () => {
  Object.assign(editingRule, {
    id: null, name: '', description: '', match_type: 'keyword_category',
    match_value: '', match_field: 'unit', rule_type: 'length',
    rule_params: {}, priority: 100, is_enabled: true, sort_order: 0
  })
  showRuleForm.value = true
}

const saveRule = async () => {
  if (!editingRule.name || !editingRule.match_value) {
    ElMessage.warning('请填写规则名称和匹配值')
    return
  }
  try {
    const payload = {
      name: editingRule.name, description: editingRule.description,
      match_type: editingRule.match_type, match_value: editingRule.match_value,
      match_field: editingRule.match_field, rule_type: editingRule.rule_type,
      rule_params: editingRule.rule_params, priority: editingRule.priority,
      sort_order: editingRule.sort_order, is_enabled: editingRule.is_enabled
    }
    if (editingRule.id) {
      await request.put(`/quotes/measurement-rules/${editingRule.id}`, payload)
    } else {
      await request.post('/quotes/measurement-rules', payload)
    }
    ElMessage.success(editingRule.id ? '规则已更新' : '规则已创建')
    showRuleForm.value = false
    await loadMeasurementRules()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm(`确定删除规则「${rule.name}」？`, '确认', { type: 'warning' })
    await request.delete(`/quotes/measurement-rules/${rule.id}`)
    ElMessage.success('已删除')
    await loadMeasurementRules()
  } catch (e) { /* canceled */ }
}

const moveRule = async (rule, direction) => {
  const idx = measurementRules.value.findIndex(r => r.id === rule.id)
  const swapIdx = idx + direction
  if (swapIdx < 0 || swapIdx >= measurementRules.value.length) return
  const other = measurementRules.value[swapIdx]
  const tmpPri = rule.priority
  try {
    await request.put(`/quotes/measurement-rules/${rule.id}`, { priority: other.priority })
    await request.put(`/quotes/measurement-rules/${other.id}`, { priority: tmpPri })
    await loadMeasurementRules()
  } catch (e) {
    ElMessage.error('调整失败')
  }
}

const recalculateAll = async () => {
  try {
    await request.post(`/quotes/${quoteId.value}/recalculate`)
    ElMessage.success('重新计算完成')
    await loadQuote()
  } catch (e) {
    ElMessage.error('重算失败')
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

// ── 费用汇总编辑逻辑 ──
const onFeeChange = async () => {
  // 重新计算总价：物料+工艺 + 管理费 + 税额 - 优惠金额
  const subtotal = parseFloat(quote.value.material_amount || 0) + parseFloat(quote.value.craft_amount || 0)
  const mgmt = parseFloat(quote.value.manage_amount || 0)
  const tax = parseFloat(quote.value.tax_amount || 0)
  // 优惠金额 = (subtotal + mgmt) × discount_rate%
  const discountRate = parseFloat(quote.value.discount_rate || 0)
  const discount = Math.round((subtotal + mgmt) * discountRate / 100 * 100) / 100
  quote.value.discount_amount = discount
  quote.value.total_amount = Math.round(subtotal + mgmt + tax - discount)
}

const onMgmtRateChange = () => {
  // 按费率自动计算管理费（基于物料+工艺总额）
  const subtotal = parseFloat(quote.value.material_amount || 0) + parseFloat(quote.value.craft_amount || 0)
  const rate = parseFloat(quote.value.manage_rate || 0)
  if (rate > 0) {
    quote.value.manage_amount = Math.round(subtotal * rate / 100 * 100) / 100
  }
  onFeeChange()
}

const onDiscountRateChange = () => {
  // 按优惠比例自动计算优惠金额，再重算总价
  onFeeChange()
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
      // 拦截器已解包，spacesRes 可能是 {instances:[...]} 或直接是数组
      spaces.value = Array.isArray(spacesRes) ? spacesRes : (spacesRes?.instances || spacesRes?.items || [])
      
      // 加载每个空间的物料列表，并计算统计数据
      for (const space of spaces.value) {
        try {
          const itemsRes = await request.get(`/quotes/${quoteId.value}/space-instances/${space.id}/items`)
          const items = Array.isArray(itemsRes) ? itemsRes : (itemsRes?.items || itemsRes?.data || [])
          space.items = [...items]
          const itemIds = items.map(i => i.id)
          console.log(`[loadQuote] 空间 ${space.id} 加载了 ${items.length} 个物料，ID列表:`, itemIds)
          
          // 动态计算空间统计数据（如果API返回为空）
          if (!space.material_cost && items.length > 0) {
            let materialCost = 0
            let laborCost = 0
            for (const it of items) {
              const qty = parseFloat(it.quantity || 1)
              const mv = parseFloat(it.measurement_value || 1)
              const up = parseFloat(it.unit_price || 0)
              const coeff = parseFloat(it.process_coefficient || it.craft_coefficient || 1)
              const baseAmount = qty * mv * up  // 不含工艺的基础金额
              materialCost += baseAmount
              // 工艺费用 = 基础金额×(系数-1) + 工艺数量×工艺单价
              if (coeff > 1) {
                laborCost += baseAmount * (coeff - 1)
              }
              const pq = parseFloat(it.process_quantity || it.craft_quantity || 0)
              const pup = parseFloat(it.process_unit_price || 0)
              if (pq > 0 && pup > 0) {
                laborCost += pq * pup
              }
            }
            space.material_cost = Math.round(materialCost * 100) / 100
            space.labor_cost = Math.round(laborCost * 100) / 100
            space.total_price = Math.round((materialCost + laborCost) * 100) / 100
            space.material_count = items.length
            console.log(`[loadQuote] 空间 ${space.space_name} 动态计算: mc=${space.material_cost}, lc=${space.labor_cost}, tp=${space.total_price}`)
          }
        } catch (e) {
          console.warn(`加载空间 ${space.id} 物料失败:`, e)
          space.items = []
        }
      }
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
    }
    
    // 初始化 quoteInfo
    initQuoteInfo()
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
  basicForm.valid_until = quote.value.expire_date || quote.value.valid_until || ''
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
  if (!query || !query.trim()) { customerOptions.value = []; return }
  try {
    const encodedQuery = encodeURIComponent(query.trim())
    const res = await request.get(`/customers?keyword=${encodedQuery}&page_size=20`)
    customerOptions.value = Array.isArray(res) ? res : (res?.items || res?.data || [])
  } catch (e) {
    console.error('[searchCustomers] 错误:', e)
    ElMessage.error('客户搜索失败')
  }
}

// 客户选择变化 - 自动填充客户信息
const onCustomerChange = (customerId) => {
  const customer = customerOptions.value.find(c => c.id === customerId)
  if (customer) {
    quoteInfo.customer_phone = customer.phone || ''
    quoteInfo.customer_address = customer.address || ''
    quoteInfo.building_name = customer.building_name || ''
    quoteInfo.house_type = customer.house_type || ''
    // 如果项目地址为空，默认使用客户地址
    if (!quoteInfo.project_address) {
      quoteInfo.project_address = customer.address || ''
    }
  }
}

// 初始化 quoteInfo 从 quote 数据
const initQuoteInfo = () => {
  quoteInfo.customer_id = quote.value.customer_id || null
  quoteInfo.customer_phone = quote.value.customer_phone || ''
  quoteInfo.customer_address = quote.value.customer_address || ''
  quoteInfo.building_name = quote.value.building_name || ''
  quoteInfo.house_type = quote.value.house_type || ''
  quoteInfo.project_address = quote.value.project_address || ''
  // 后端返回 expire_date，前端显示用 valid_until（日期字符串）
  quoteInfo.valid_until = quote.value.expire_date || quote.value.valid_until || ''
  
  // 将当前客户加入选项列表，确保el-select能正确显示名称
  if (quote.value.customer_id && quote.value.customer_name) {
    const exists = customerOptions.value.find(c => c.id === quote.value.customer_id)
    if (!exists) {
      customerOptions.value.push({
        id: quote.value.customer_id,
        name: quote.value.customer_name,
        phone: quote.value.customer_phone
      })
    }
  }
  
  // 初始化服务团队
  let st = quote.value.service_team || []
  // 确保 st 是数组
  if (!Array.isArray(st)) {
    console.warn('[initQuoteInfo] service_team 不是数组:', st)
    st = []
  }
  serviceTeam.value = {
    quoter: null,
    auditor: null,
    designer: null,
    planner: null,
    project_manager: null
  }
  st.forEach(item => {
    if (item && item.role && serviceTeam.value[item.role] !== undefined) {
      serviceTeam.value[item.role] = item.employee_id || null
    }
  })
}

// 保存报价基本信息 + 服务团队
const saveQuoteInfo = async () => {
  savingQuoteInfo.value = true
  try {
    // 构建 service_team 数组
    const st = []
    QUOTE_TEAM_ROLES.forEach(r => {
      if (serviceTeam.value[r.value]) {
        st.push({
          role: r.value,
          employee_id: serviceTeam.value[r.value]
        })
      }
    })
    
    const payload = {
      customer_id: quoteInfo.customer_id,
      customer_phone: quoteInfo.customer_phone,
      customer_name: customerOptions.value.find(c => c.id === quoteInfo.customer_id)?.name || '',
      building_name: quoteInfo.building_name,
      house_type: quoteInfo.house_type,
      project_address: quoteInfo.project_address,
      valid_until: quoteInfo.valid_until,
      service_team: st
    }
    
    await request.put(`/quotes/${quoteId.value}`, payload)
    ElMessage.success('保存成功')
    loadQuote()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    savingQuoteInfo.value = false
  }
}

// 保存所有信息（基本信息 + 物料表）
const savingAll = ref(false)
const saveAll = async () => {
  savingAll.value = true
  try {
    // 1. 保存基本信息
    const st = []
    QUOTE_TEAM_ROLES.forEach(r => {
      if (serviceTeam.value[r.value]) {
        st.push({
          role: r.value,
          employee_id: serviceTeam.value[r.value]
        })
      }
    })
    
    const basicPayload = {
      customer_id: quoteInfo.customer_id,
      customer_phone: quoteInfo.customer_phone,
      customer_name: customerOptions.value.find(c => c.id === quoteInfo.customer_id)?.name || '',
      building_name: quoteInfo.building_name,
      house_type: quoteInfo.house_type,
      project_address: quoteInfo.project_address,
      valid_until: quoteInfo.valid_until,
      service_team: st,
      // 费用汇总字段
      design_amount: parseFloat(quote.value.design_amount || 0),
      install_amount: parseFloat(quote.value.install_amount || 0),
      manage_rate: parseFloat(quote.value.manage_rate || 0),
      manage_amount: parseFloat(quote.value.manage_amount || 0),
      tax_amount: parseFloat(quote.value.tax_amount || 0),
      tax_rate: parseFloat(quote.value.tax_rate || 0),
      discount_rate: parseFloat(quote.value.discount_rate || 0),
      discount_amount: parseFloat(quote.value.discount_amount || 0),
    }
    await request.put(`/quotes/${quoteId.value}`, basicPayload)
    
    // 2. 保存物料表（遍历所有空间实例，保存每个空间的物料）
    for (const space of spaces.value) {
      const items = space.items || []
      for (const item of items) {
        if (item.id) {
          // 更新现有物料
          await request.put(`/quotes/${quoteId.value}/space-instances/${space.id}/items/${item.id}`, {
            quantity: item.quantity,
            unit_price: item.unit_price,
            custom_width: item.custom_width,
            custom_depth: item.custom_depth,
            custom_height: item.custom_height,
            custom_result: item.custom_result,
            process_name: item.process_name,
            process_quantity: item.process_quantity,
            process_unit_price: item.process_unit_price,
            remark: item.remark
          })
        }
      }
    }
    
    ElMessage.success('保存成功')
    loadQuote()
  } catch (e) {
    console.error('[saveAll] 保存失败:', e)
    console.error('[saveAll] 错误详情:', e.response?.data || e.message)
    ElMessage.error(e.response?.data?.message || e.message || '保存失败')
  } finally {
    savingAll.value = false
  }
}

// 服务团队
const loadAllEmployees = async () => {
  try {
    console.log('[loadAllEmployees] 开始加载...')
    const res = await request.get('/quotes/options')
    console.log('[loadAllEmployees] API返回:', res)
    // 拦截器已解包到 data 层
    allEmployees.value = res?.employees || res?.data?.employees || []
    console.log('[loadAllEmployees] 员工数量:', allEmployees.value.length)
    if (allEmployees.value.length === 0) {
      console.warn('[loadAllEmployees] 警告: 员工列表为空!')
    }
  } catch (e) { 
    console.error('[loadAllEmployees] 错误:', e)
    ElMessage.error('加载员工列表失败: ' + (e.message || '未知错误'))
  }
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

// 提交审核
const submitForReview = async () => {
  try {
    await ElMessageBox.confirm('确定要提交该报价进行审核吗？提交后报价将进入待审核状态，部分字段将不可编辑。', '确认提交审核', {
      confirmButtonText: '确定提交',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.post(`/quotes/${quoteId.value}/submit`)
    ElMessage.success('报价已提交审核')
    loadQuote()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('[submitForReview] 错误:', e)
      ElMessage.error('提交审核失败: ' + (e.response?.data?.message || e.message || '未知错误'))
    }
  }
}

// 另存为模板
const saveAsTemplate = async () => {
  try {
    const { value: templateName } = await ElMessageBox.prompt('请输入模板名称', '另存为模板', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：标准三室两厅套餐',
      inputValidator: (val) => {
        if (!val || val.trim() === '') return '模板名称不能为空'
        if (val.trim().length > 50) return '模板名称不能超过50个字符'
        return true
      }
    })
    
    if (!templateName) return
    
    // 构建模板数据：去掉客户敏感信息，保留户型等基本信息
    const templateData = {
      name: templateName.trim(),
      // 保留户型信息，去掉客户名称、电话等敏感信息
      building_name: quote.value.building_name || null,
      house_type: quote.value.house_type || null,
      house_area: quote.value.house_area || null,
      project_address: null, // 清空具体地址
      // 完整保留空间和物料信息
      spaces: spaces.value.map(space => ({
        space_name: space.space_name,
        space_type: space.space_type,
        items: (space.items || []).map(item => ({
          sku_id: item.sku_id,
          custom_name: item.custom_name,
          material: item.material,
          calc_type: item.calc_type,
          quantity: item.quantity,
          unit_price: item.unit_price,
          craft_name: item.craft_name,
          craft_coefficient: item.craft_coefficient,
          craft_quantity: item.craft_quantity,
          craft_unit_price: item.craft_unit_price,
          custom_width: item.custom_width,
          custom_depth: item.custom_depth,
          custom_height: item.custom_height,
          measurement_value: item.measurement_value,
          category_level1: item.category_level1,
          category_level2: item.category_level2
        }))
      }))
    }
    
    await request.post('/quotes/templates/from-quote', {
      quote_id: quoteId.value,
      template_data: templateData
    })
    ElMessage.success('模板保存成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error('[saveAsTemplate] 错误:', e)
      ElMessage.error('保存模板失败: ' + (e.response?.data?.message || e.message || '未知错误'))
    }
  }
}

// 编辑报价
const editQuote = () => {
  router.push(`/admin/quotes/${quoteId.value}/edit`)
}

// HTML预览（不生成PDF文件）
const htmlPreviewVisible = ref(false)
const htmlPreviewUrl = ref('')
const showHtmlPreview = async () => {
  const id = quoteId.value
  const token = localStorage.getItem('token') || localStorage.getItem('auth_token') || ''
  htmlPreviewUrl.value = `/api/v3/quotes/${id}/html-preview?token=${token}`
  htmlPreviewVisible.value = true
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
  itemForm.brand = ''
  itemForm.spec = ''
  itemForm.material = ''
  itemForm.image = ''
  itemForm.category_level1 = ''
  itemForm.category_level2 = ''
  itemForm.calc_type = ''
  itemForm.measurement_value = 1
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
  itemForm.craft_parts = []
  itemForm.customization_rules = []
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
  brand: '',
  spec: '',
  material: '',
  image: '',
  category_level1: '',
  category_level2: '',
  calc_type: '',
  measurement_value: 1,
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
  craft_coefficient: null,
  craft_parts: [],
  customization_rules: []
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
  itemForm.brand = item.brand || ''
  itemForm.spec = item.spec || ''
  itemForm.material = item.material || ''
  itemForm.image = item.image || ''
  itemForm.category_level1 = item.category_level1 || ''
  itemForm.category_level2 = item.category_level2 || ''
  itemForm.calc_type = item.calc_type || ''
  itemForm.measurement_value = item.measurement_value || 1
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
  // 打开弹窗后立即计算计量值（有定制参数时显示真实值）
  setTimeout(() => calcMeasurementValue(), 100)
}

// 计量值：调用后端规则引擎实时计算
const measurementCache = ref(1)
const calcLoading = ref(false)
let calcDebounce = null

const calcMeasurementValue = async () => {
  calcLoading.value = true
  const w = Number(itemForm.custom_width || itemForm.width || 0)
  const d = Number(itemForm.custom_depth || itemForm.depth || 0)
  const h = Number(itemForm.custom_height || itemForm.height || 0)
  
  console.log('[计量计算] 参数:', { w, d, h, unit: itemForm.unit, name: itemForm.name?.substring(0,20) })
  
  // 无尺寸参数时返回默认1
  if (!w && !d && !h) { measurementCache.value = 1; calcLoading.value = false; return 1 }
  
  try {
    const res = await request.post('/quotes/measurement-calc', {
      unit: itemForm.unit || '',
      width: itemForm.custom_width || itemForm.width || null,
      depth: itemForm.custom_depth || itemForm.depth || null,
      height: itemForm.custom_height || itemForm.height || null,
      category_level2: itemForm.category_level2 || '',
      material_name: itemForm.name || '',
      process_name: itemForm.process_name || ''
    })
    console.log('[计量计算] API响应:', res)
    // 注意：request.js 响应拦截器已解包一层（return res.data），所以 res 直接就是后端的 data 字段
    const val = res?.measurement_value ?? 1
    measurementCache.value = val
    calcLoading.value = false
    return val
  } catch (e) {
    console.warn('[计量计算] API调用失败，使用本地降级', e)
    // 降级：本地简单计算
    const unit = (itemForm.unit || '').toLowerCase()
    let val = 1
    if (['㎡','m²'].some(u => unit.includes(u))) {
      const dims = [w,d,h].filter(v=>v>0).sort((a,b)=>b-a)
      val = dims.length >= 2 ? (dims[0]*dims[1])/1000000 : (dims[0]||0)/1000
    } else if (['m³'].some(u => unit.includes(u))) {
      val = (w*d*h)/1000000000
    } else {
      val = Math.max(w,d,h)/1000 || 1
    }
    measurementCache.value = Math.round(val*10000)/10000
    return measurementCache.value
  } finally {
    calcLoading.value = false
  }
}

// ========== watch: 定制参数变化时自动同步计量值（防抖）==========
watch(
  () => [itemForm.custom_width, itemForm.custom_depth, itemForm.custom_height, itemForm.unit, itemForm.name, itemForm.process_name, itemForm.category_level2],
  () => {
    if (calcDebounce) clearTimeout(calcDebounce)
    calcDebounce = setTimeout(() => {
      calcMeasurementValue()
    }, 200)
  },
  { deep: true }
)

// ========== watch: 工艺金额自动计算 ==========
watch(
  () => [itemForm.process_coefficient, itemForm.process_unit_price, itemForm.process_quantity],
  () => {
    const coef = Number(itemForm.process_coefficient || 0)
    const price = Number(itemForm.process_unit_price || 0)
    const qty = Number(itemForm.process_quantity || 1)
    itemForm.process_amount = Math.round(coef * price * qty * 100) / 100
  },
  { deep: true }
)

// 保存物料（支持新增和编辑）
const saveItem = async () => {
  try {
    console.log('[saveItem] 开始保存，itemForm:', itemForm)
    await calcMeasurementValue()
    itemForm.measurement_value = measurementCache.value
    console.log('[saveItem] 计量值:', measurementCache.value)
    
    // 构建纯净的 payload，避免 reactive 代理对象的问题
    const payload = {
      sku_id: itemForm.sku_id,
      custom_name: itemForm.custom_name,
      name: itemForm.name,
      quantity: itemForm.quantity,
      unit_price: itemForm.unit_price,
      unit: itemForm.unit,
      brand: itemForm.brand,
      spec: itemForm.spec,
      material: itemForm.material,
      image: itemForm.image,
      category_level1: itemForm.category_level1,
      category_level2: itemForm.category_level2,
      calc_type: itemForm.calc_type,
      measurement_value: itemForm.measurement_value,
      remark: itemForm.remark,
      custom_width: itemForm.custom_width,
      custom_depth: itemForm.custom_depth,
      custom_height: itemForm.custom_height,
      custom_result: itemForm.custom_result,
      process_name: itemForm.process_name,
      process_coefficient: itemForm.process_coefficient,
      process_quantity: itemForm.process_quantity,
      process_unit_price: itemForm.process_unit_price,
      process_amount: itemForm.process_amount,
      craft_type: itemForm.craft_type,
      craft_price: itemForm.craft_price,
      craft_quantity: itemForm.craft_quantity,
      craft_coefficient: itemForm.craft_coefficient
    }
    
    if (itemForm.id) {
      // 编辑模式
      const path = itemForm.space_id == null
        ? `/quotes/${quoteId.value}/items/${itemForm.id}`
        : `/quotes/${quoteId.value}/space-instances/${itemForm.space_id}/items/${itemForm.id}`
      console.log('[saveItem] 编辑模式，PUT:', path)
      const res = await request.put(path, payload)
      console.log('[saveItem] 编辑成功:', res)
      ElMessage.success('保存成功')
    } else {
      // 新增模式
      const path = `/quotes/${quoteId.value}/space-instances/${itemForm.space_id}/items`
      console.log('[saveItem] 新增模式，POST:', path, '数据:', payload)
      const res = await request.post(path, payload)
      console.log('[saveItem] 添加成功:', res)
      ElMessage.success('添加成功')
    }
    itemDialogVisible.value = false
    console.log('[saveItem] 调用 loadQuote() 刷新列表')
    await loadQuote()
    console.log('[saveItem] 列表刷新完成')
  } catch (error) {
    console.error('[saveItem] 保存失败:', error)
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

// ========== 工艺选择器数据 ==========
const craftOptions = ref([])  // 工艺下拉选项 {id, name, category, coefficient, unit_price, unit}
const craftLoading = ref(false)

// 加载工艺列表（用于工艺名称下拉选择）
const loadCraftOptions = async () => {
  try {
    craftLoading.value = true
    const res = await request.get('/crafts/all')
    craftOptions.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('加载工艺失败', e)
  } finally {
    craftLoading.value = false
  }
}

// 选择工艺时自动填充系数、单价等
const onCraftSelected = (craftName) => {
  if (!craftName) return
  const craft = craftOptions.value.find(c => c.name === craftName)
  if (!craft) return
  itemForm.process_coefficient = craft.coefficient || 1
  itemForm.process_unit_price = craft.unit_price || 0
  itemForm.process_name = craft.name
  // 工艺金额 = 系数 × 单价 × 数量（watch 中自动计算）
}

const searchSku = async (page = 1) => {
  try {
    skuLoading.value = true
    skuPage.value = page
    const res = await request.get('/materials', { params: { keyword: skuKeyword.value, page, page_size: 20 } })
    // 拦截器已解包 res.data，res 直接是 {items, total, page, page_size}
    skuList.value = res.items || []
    skuTotal.value = res.total || 0
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
  // 从物料库动态加载所有字段，不硬编码
  itemForm.sku_id = sku.id
  itemForm.name = sku.name
  itemForm.unit_price = sku.sale_price || 0
  itemForm.unit = sku.unit || ''
  itemForm.brand = sku.brand || ''
  itemForm.spec = sku.specification || sku.spec || ''
  itemForm.material = sku.material || ''
  itemForm.image = sku.main_image || (sku.images && sku.images[0]) || ''

  // 分类路径（后端已返回 L1/L2）
  if (sku.category_level1) {
    itemForm.category_level1 = sku.category_level1
  }
  if (sku.category_level2) {
    itemForm.category_level2 = sku.category_level2
  } else if (sku.category_name) {
    itemForm.category_level1 = sku.category_name
  }

  // 计量类型：从 SKU 的 calc_type 决定计量规则
  itemForm.calc_type = sku.calc_type || ''

  // 工艺系数：SKU 默认工艺系数
  if (sku.craft_coefficient != null && itemForm.process_coefficient == null) {
    itemForm.process_coefficient = sku.craft_coefficient
  }

  // 工艺部件：如果 SKU 有工艺部件数据
  if (sku.craft_parts && sku.craft_parts.length > 0) {
    itemForm.craft_parts = sku.craft_parts
  }

  // 定制规则：SKU 预定义的定制参数规则
  if (sku.customization_rules && sku.customization_rules.length > 0) {
    itemForm.customization_rules = sku.customization_rules
  }

  // 备注拼接规格
  if (sku.specification) {
    itemForm.remark = sku.specification + (itemForm.remark ? '\n' + itemForm.remark : '')
  }

  skuPickerVisible.value = false
  ElMessage.success(`已选择: ${sku.name}（¥${sku.sale_price}/${sku.unit}）`)
}

onMounted(() => {
  loadQuote()
  loadAllEmployees()
  loadTemplates()
  loadMeasurementRules()
  loadCraftOptions()  // 加载工艺选项
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

/* 费用汇总编辑表格 */
.fee-summary-table {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}
.fee-row {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}
.fee-row:last-child {
  border-bottom: none;
}
.fee-label {
  width: 80px;
  padding: 12px 16px;
  background: #fafafa;
  color: #606266;
  font-size: 14px;
  flex-shrink: 0;
  border-right: 1px solid #ebeef5;
}
.fee-value {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  color: #303133;
}
.fee-value.readonly {
  color: #909399;
  font-weight: 500;
}
.fee-row .el-input-number {
  flex: 1;
  margin-right: 4px;
}

/* ========== 基本信息样式（美化版） ========== */
.info-section {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 24px 28px;
  margin-bottom: 16px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px 32px;
}

.info-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-wide {
  grid-column: span 2;
}

.field-label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.field-value-static {
  font-size: 14px;
  color: #303133;
  background: #f5f7fa;
  padding: 6px 12px;
  border-radius: 4px;
  min-height: 34px;
  display: flex;
  align-items: center;
  line-height: 1.4;
}

/* 服务团队区 */
.team-section {
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  font-size: 15px;
  color: #606266;
  font-weight: 600;
  margin-bottom: 18px;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 15px;
  background: linear-gradient(180deg, #409eff, #67c23a);
  border-radius: 2px;
}

.team-grid {
  display: flex;
  gap: 12px;
}

.team-item {
  flex: 1;
  min-width: 0;
  text-align: center;
  padding: 14px 10px;
  background: #fafbfc;
  border: 1px solid #e9ecf0;
  border-radius: 6px;
  transition: all 0.25s;
}

.team-item:hover {
  border-color: #c0c4cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.team-role-name {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-member-name {
  font-size: 14px;
  color: #303133;
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 3px;
  margin-top: -2px;
}

/* 旧样式保留兼容（已废弃，待清理） */
.info-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  line-height: 32px;
}

/* ========== 自定义空间Tab样式 ==========*/
.spaces-container {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
}

.space-tabs {
  display: flex;
  flex-direction: row;
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
  background: #67c23a !important;
  border-color: #67c23a !important;
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.4);
  transform: scale(1.02);
}

.space-tab:not(.active) {
  background: #f5f7fa;
  border-color: #dcdfe6;
  color: #606266;
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


.rules-card .rules-list {
  max-height: 240px;
  overflow-y: auto;
}
.rules-card .rule-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}
.rules-card .rule-item:last-child {
  border-bottom: none;
}
.rules-card .rule-tag {
  flex-shrink: 0;
}
.rules-card .rule-name {
  font-weight: 500;
  min-width: 80px;
}
.rules-card .rule-desc {
  flex: 1;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
