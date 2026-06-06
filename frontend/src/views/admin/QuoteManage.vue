<template>
  <div class="quote-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>报价管理</h2>
      <div>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 手动新建
        </el-button>
      </div>
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
          <div class="stat-value">¥{{ formatMoney(stats.total_amount) }}</div>
          <div class="stat-label">报价总额</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="报价编号" clearable />
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

    <!-- 报价列表 -->
    <el-card shadow="never">
      <el-table :data="quotes" v-loading="loading" stripe>
        <el-table-column prop="quote_no" label="报价编号" width="140" />

        <el-table-column label="客户" min-width="150">
          <template #default="{ row }">
            <div class="customer-name">{{ row.customer_name }}</div>
            <div class="customer-phone">{{ row.customer_phone }}</div>
          </template>
        </el-table-column>

        <el-table-column label="总价" width="150">
          <template #default="{ row }">
            <div class="amount">¥{{ formatMoney(row.total_amount) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="creator_name" label="创建人" width="100" />

        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="editQuote(row)" v-if="row.status === 'draft'">编辑</el-button>
            <el-button link type="success" @click="previewQuote(row)">预览</el-button>
            <el-button link type="warning" @click="submitQuote(row)" v-if="row.status === 'draft'">提交</el-button>
            <el-button link type="success" @click="approveQuote(row)" v-if="row.status === 'pending'">通过</el-button>
            <el-button link type="danger" @click="rejectQuote(row)" v-if="row.status === 'pending'">驳回</el-button>
            <el-button link type="danger" @click="deleteQuote(row)">删除</el-button>
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

    <!-- 新建/编辑报价对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑报价' : '新建报价'"
      width="95%"
      :fullscreen="dialog.fullscreen"
      class="quote-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <span>{{ dialog.isEdit ? '编辑报价' : '新建报价' }}</span>
          <el-button link @click="dialog.fullscreen = !dialog.fullscreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </div>
      </template>

      <el-steps :active="activeStep" finish-status="success" class="quote-steps">
        <el-step title="物料详单" />
        <el-step title="封面设计" />
        <el-step title="服务团队" />
        <el-step title="分类汇总" />
        <el-step title="预览报价" />
      </el-steps>

      <!-- 步骤2: 封面设计 -->
      <div v-show="activeStep === 1" class="step-content">
        <el-row :gutter="24">
          <el-col :span="8">
            <el-card title="封面配置">
              <el-form :model="form.cover_config" label-width="100px">
                <el-form-item label="选择模板">
                  <div class="template-grid">
                    <div
                      v-for="t in templates"
                      :key="t.id"
                      class="template-item"
                      :class="{ active: form.cover_config.template_id === t.id }"
                      @click="selectTemplate(t)"
                    >
                      <div class="template-preview" :style="getTemplateStyle(t)">
                        <span>{{ t.name }}</span>
                      </div>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item label="主色调">
                  <el-color-picker v-model="form.cover_config.primary_color" show-alpha />
                </el-form-item>

                <el-form-item label="背景图片">
                  <el-upload
                    class="cover-uploader"
                    action="/api/v3/upload/image"
                    :show-file-list="false"
                    :headers="uploadHeaders"
                    :on-success="handleCoverUpload"
                    :on-error="handleUploadError"
                  >
                    <img v-if="form.cover_config.background_image" :src="form.cover_config.background_image" class="cover-image" />
                    <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
                  </el-upload>
                </el-form-item>

                <el-form-item label="Logo">
                  <el-upload
                    class="logo-uploader"
                    action="/api/v3/upload/image"
                    :show-file-list="false"
                    :headers="uploadHeaders"
                    :on-success="handleLogoUpload"
                    :on-error="handleUploadError"
                  >
                    <img v-if="form.cover_config.logo" :src="form.cover_config.logo" class="logo-image" />
                    <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
                  </el-upload>
                </el-form-item>

                <el-form-item label="水印文字">
                  <el-input v-model="form.cover_config.watermark" placeholder="D&B 帝标|设记家全案服务" />
                </el-form-item>

                <el-form-item label="门店名称">
                  <el-input v-model="form.cover_config.store_name" placeholder="D&B 帝标|设记家·全案落地服务中心" />
                </el-form-item>

                <el-form-item label="显示设置">
                  <el-checkbox v-model="form.cover_config.show_customer_info">显示客户信息</el-checkbox>
                  <el-checkbox v-model="form.cover_config.show_store_name">显示门店名称</el-checkbox>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <el-col :span="16">
            <el-card title="封面预览">
              <div class="cover-preview" :style="getCoverPreviewStyle()">
                <div class="cover-watermark" v-if="form.cover_config.watermark">
                  {{ form.cover_config.watermark }}
                </div>
                <div class="cover-content">
                  <img v-if="form.cover_config.logo" :src="form.cover_config.logo" class="cover-logo" />
                  <h1 class="cover-title">全案服务报价单</h1>
                  <div class="cover-subtitle" v-if="form.cover_config.store_name">
                    {{ form.cover_config.store_name }}
                  </div>
                  <div class="cover-info" v-if="form.cover_config.show_customer_info && selectedCustomer">
                    <div class="info-item">
                      <span class="label">客户姓名：</span>
                      <span class="value">{{ selectedCustomer.name }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">联系电话：</span>
                      <span class="value">{{ selectedCustomer.phone }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">房屋地址：</span>
                      <span class="value">{{ selectedCustomer.address || '-' }}</span>
                    </div>
                  </div>
                  <div class="cover-quote-no">{{ form.quote_no || 'BJ202604260001' }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 步骤3: 服务团队 -->
      <div v-show="activeStep === 2" class="step-content">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>服务团队配置</span>
              <el-button type="primary" size="small" @click="addTeamMember">
                <el-icon><Plus /></el-icon> 添加成员
              </el-button>
            </div>
          </template>

          <el-table :data="form.service_team" border>
            <el-table-column label="岗位" width="180">
              <template #default="{ row, $index }">
                <el-select v-model="row.role" @change="onRoleChange($index)">
                  <el-option
                    v-for="r in options.service_roles"
                    :key="r.value"
                    :label="r.label"
                    :value="r.value"
                  />
                </el-select>
              </template>
            </el-table-column>

            <el-table-column label="姓名" width="150">
              <template #default="{ row, $index }">
                <el-select-v2
                  v-model="row.employee_id"
                  :options="employeeOptions"
                  placeholder="选择员工"
                  @change="onEmployeeChange($index, $event)"
                />
              </template>
            </el-table-column>

            <el-table-column label="联系电话" width="150">
              <template #default="{ row }">
                <el-input v-model="row.phone" placeholder="联系电话" />
              </template>
            </el-table-column>

            <el-table-column label="操作" width="100">
              <template #default="{ $index }">
                <el-button type="danger" link @click="removeTeamMember($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="team-preview" v-if="form.service_team.length > 0">
            <h4>团队预览</h4>
            <el-row :gutter="16">
              <el-col :span="6" v-for="member in form.service_team" :key="member.role">
                <div class="team-member-card">
                  <div class="role">{{ member.role_name }}</div>
                  <div class="name">{{ member.name }}</div>
                  <div class="phone">{{ member.phone }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>

      <!-- 步骤4: 分类汇总 -->
      <div v-show="activeStep === 3" class="step-content">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>分类汇总</span>
            </div>
          </template>

          <el-row :gutter="16">
            <el-col :span="12" v-for="cat in categoryList" :key="cat.key">
              <el-card class="category-card" shadow="hover">
                <div class="category-header">
                  <span class="category-name">{{ cat.label }}</span>
                  <span class="category-amount">¥{{ formatMoney(getCategoryAmount(cat.key)) }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-divider />

          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="小计">
                <el-input-number v-model="form.subtotal" :min="0" :precision="2" disabled :controls="false" style="width:100px" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="管理费率 %">
                <el-input-number v-model="form.management_fee_rate" :min="0" :max="100" :precision="2" :controls="false" style="width:100px" @change="calculateTotal" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="管理费">
                <el-input-number v-model="form.management_fee" :min="0" :precision="2" disabled :controls="false" style="width:100px" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="税率 %">
                <el-input-number v-model="form.tax_rate" :min="0" :max="100" :precision="2" :controls="false" style="width:100px" @change="calculateTotal" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="税费">
                <el-input-number v-model="form.tax" :min="0" :precision="2" disabled :controls="false" style="width:100px" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="总价">
                <div class="total-amount">¥{{ formatMoney(form.total_amount) }}</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 步骤1: 物料详单 -->
      <div v-show="activeStep === 0" class="step-content">
        <!-- 空间分组卡片 -->
        <div v-for="(space, spaceIdx) in form.spaces" :key="space.id" class="space-card">
          <el-card>
            <template #header>
              <div class="space-header">
                <div class="space-title">
                  <el-input v-model="space.room_name" placeholder="空间名称（如：主卧）" style="width:120px" />
                </div>
                <div class="space-actions">
                  <span class="space-total">本空间合计: ¥{{ formatMoney(calculateSpaceTotal(space)) }}</span>
                  <el-button type="danger" link size="small" @click="removeSpace(spaceIdx)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>

            <el-table :data="space.children" border row-key="id" size="small" class="material-detail-table">
                          <!-- 序号列 -->
              <el-table-column label="序号" width="50" align="center">
                <template #default="{ $index }">{{ $index + 1 }}</template>
              </el-table-column>

              <!-- 商品名称列 -->
              <el-table-column label="商品名称" width="120">
                <template #default="{ row }">
                  <el-input v-model="row.product_name" size="small" placeholder="商品名称" />
                </template>
              </el-table-column>

              <!-- 物料筛选列 -->
              <el-table-column label="选物料" width="200" class-name="material-picker-col">
                <template #default="{ row, $index }">
                  <div class="material-picker-cell" @click="openPickerForRow(spaceIdx, $index)">
                    <template v-if="row.sku_id || row.name">
                      <el-icon color="#67C23A"><Box /></el-icon>
                      <span class="picker-cell-text">{{ row.name }}</span>
                    </template>
                    <template v-else>
                      <el-icon color="#c0c4cc"><Plus /></el-icon>
                      <span class="picker-cell-placeholder">点击选择</span>
                    </template>
                  </div>
                </template>
              </el-table-column>


              <el-table-column label="长(mm)" width="100">
                <template #default="{ row }"><el-input-number v-model="row.width" :min="0" size="small" :controls="false" style="width:100px" @change="autoCalculateMeasurement(row)" /></template>
              </el-table-column>
              <el-table-column label="深(mm)" width="100">
                <template #default="{ row }"><el-input-number v-model="row.depth" :min="0" size="small" :controls="false" style="width:100px" @change="autoCalculateMeasurement(row)" /></template>
              </el-table-column>
              <el-table-column label="高(mm)" width="100">
                <template #default="{ row }"><el-input-number v-model="row.height" :min="0" size="small" :controls="false" style="width:100px" @change="autoCalculateMeasurement(row)" /></template>
              </el-table-column>
              <el-table-column label="计量值" width="70" align="right">
                <template #default="{ row }"><span style="font-size:13px;">{{ row.measurement_value != null ? row.measurement_value.toFixed(2) : '-' }}</span></template>
              </el-table-column>

              <!-- 核心列（始终显示） -->
              <el-table-column label="数量" width="100" align="center">
                <template #default="{ row }">
                  <el-input-number v-model="row.quantity" :min="0" :precision="2" size="small" :controls="false" style="width:100px" @change="calculateTotal" />
                </template>
              </el-table-column>
              <el-table-column label="单价" width="80" align="right">
                <template #default="{ row }"><span style="font-size:13px;">{{ row.unit_price != null ? row.unit_price.toFixed(2) : '-' }}</span></template>
              </el-table-column>
              <el-table-column label="单位" width="60" align="center">
                <template #default="{ row }"><span style="font-size:13px;">{{ row.unit || '-' }}</span></template>
              </el-table-column>
              <el-table-column label="特殊工艺" width="90">
                <template #default="{ row }"><el-select v-model="row.craft_type" style="background-color: #faf3e0; border-radius: 2px;" size="small" placeholder="工艺" clearable filterable @visible-change="(v) => v && loadCraftOptions(row.category_level1)" @change="(val) => { if(val) { const opt = craftOptions.find(c => c.label === val); row.craft_unit = opt ? opt.unit : '项'; row.craft_coefficient = opt ? opt.coefficient : 1; row.craft_price = opt ? opt.unit_price : 0; } else { row.craft_unit = ''; row.craft_coefficient = 1; row.craft_price = 0; } calculateTotal() }"><el-option v-for="c in craftOptions" :key="c.label" :label="c.label" :value="c.label" /></el-select></template>
              </el-table-column>

              <el-table-column label="工艺数量" width="100" align="center">
                <template #default="{ row }"><el-input-number v-model="row.craft_quantity" :min="0" :precision="2" size="small" :controls="false" style="width:100px" @change="calculateTotal" /></template>
              </el-table-column>
              <el-table-column label="工艺系数" width="70" align="center">
                <template #default="{ row }"><span style="font-size:13px; background-color: #faf3e0; border-radius: 2px; padding: 2px 4px;">{{ row.craft_coefficient ?? 1 }}</span></template>
              </el-table-column>
              <el-table-column label="工艺单位" width="70" align="center">
                <template #default="{ row }"><span style="font-size:13px; background-color: #faf3e0; border-radius: 2px; padding: 2px 4px;">{{ row.craft_unit || '-' }}</span></template>
              </el-table-column>
              <el-table-column label="工艺价" width="80" align="right">
                <template #default="{ row }"><span style="font-size:13px; background-color: #faf3e0; border-radius: 2px; padding: 2px 4px;">{{ row.craft_price != null ? row.craft_price.toFixed(2) : '-' }}</span></template>
              </el-table-column>
              <el-table-column label="增项金额" width="80" align="right">
                <template #default="{ row }">
                  <span class="process-amount" style="background-color: #faf3e0; border-radius: 2px; padding: 2px 4px;">¥{{ formatMoney(row.process_amount || 0) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="小计金额" width="90" align="right" class-name="amount-col">
                <template #default="{ row }"><span class="item-total" style="background-color: #faf3e0; border-radius: 2px; padding: 2px 4px;">¥{{ formatMoney(row.total_price) }}</span></template>
              </el-table-column>
              <el-table-column label="备注" min-width="80">
                <template #default="{ row }"><span style="font-size:13px;">{{ row.remark || '-' }}</span></template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ $index }">
                  <el-button type="primary" link size="small" @click="cloneRow(spaceIdx, $index)" title="克隆">
                    <el-icon><DocumentCopy /></el-icon>
                  </el-button>
                  <el-button type="danger" link size="small" @click="space.children.splice($index, 1); calculateTotal()" title="删除">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <!-- 添加空间按钮 -->
        <el-button type="primary" @click="addSpace" style="margin: 12px 0">
          <el-icon><Plus /></el-icon> 添加空间
        </el-button>

        <!-- 物料备选框 -->
        <el-card class="material-picker-card">
          <template #header>
            <div class="card-header">
              <span>📦 物料备选</span>
              <el-input v-model="materialSearchKeyword" placeholder="搜索物料" clearable style="width:200px" @keyup.enter="searchMaterials" @clear="searchMaterials">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </div>
          </template>

          <el-tabs v-model="activeCategoryTab" @tab-change="onCategoryTabChange" type="card">
            <el-tab-pane v-for="cat in categoryTree" :key="cat.id" :label="cat.name" :name="cat.id" />
          </el-tabs>

          <div class="sub-category-bar">
            <el-select v-model="activeSubCategory" placeholder="全部二级分类" clearable style="width:160px; margin-right: 8px" @change="onSubCategoryChange">
              <el-option v-for="sub in currentSubCategories" :key="sub.id" :label="sub.name" :value="sub.id" />
            </el-select>
            <el-input
              v-model="materialSearchKeyword"
              placeholder="搜索物料名称/品牌/规格"
              clearable
              style="width: 200px; margin-right: 8px"
              @keyup.enter="searchMaterials"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="searchMaterials" :loading="materialSearchLoading">
              <el-icon><Search /></el-icon> 搜索
            </el-button>
          </div>

          <div v-loading="materialSearchLoading" class="material-grid">
            <div v-for="m in materialSearchResults" :key="m.id" class="material-card" @click="addMaterialToQuote(m)">
              <div class="material-card-img">
                <img v-if="m.images?.[0] || m.image" :src="m.images?.[0] || m.image" />
                <el-icon v-else :size="32" color="#c0c4cc"><Box /></el-icon>
              </div>
              <div class="material-card-info">
                <div class="material-card-name" :title="m.name">{{ m.name }}</div>
                <div class="material-card-meta">
                  <span v-if="m.brand">{{ m.brand }}</span>
                  <span v-if="m.spec || m.specification">{{ m.spec || m.specification }}</span>
                </div>
                <div class="material-card-price">¥{{ m.sale_price || m.base_price || 0 }}</div>
              </div>
            </div>
            <el-empty v-if="!materialSearchLoading && materialSearchResults.length === 0" :description="materialSearchKeyword ? '未找到匹配物料，请尝试其他关键词' : '暂无物料'" />
          </div>
        </el-card>
      </div> -->
            <div v-show="activeStep === 4" class="step-content">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>报价预览</span>
              <el-button type="primary" size="small" @click="generateQuotePreview">
                <el-icon><View /></el-icon> 生成预览
              </el-button>
            </div>
          </template>
          <div v-if="quotePreviewUrl" class="preview-container">
            <iframe :src="quotePreviewUrl" class="preview-iframe" />
          </div>
          <el-empty v-else description='点击「生成预览」查看报价单' />
        </el-card>

        <el-row :gutter="24" style="margin-top: 16px;">
          <el-col :span="24">
            <el-card title="报价汇总">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="客户">{{ form.customer_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ form.customer_phone || '-' }}</el-descriptions-item>
                <el-descriptions-item label="项目地址">{{ form.project_address || '-' }}</el-descriptions-item>
                <el-descriptions-item label="方案名称">{{ form.quote_name || '-' }}</el-descriptions-item>
              </el-descriptions>
              <el-divider />
              <div class="quote-summary-total">
                <span class="total-label">报价总额</span>
                <span class="total-price">¥{{ formatMoney(form.total_amount) }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

<template #footer>
        <div class="dialog-footer">
          <el-button v-if="activeStep > 0" @click="activeStep--">上一步</el-button>
          <el-button v-if="activeStep < 4" type="primary" @click="activeStep++">下一步</el-button>
          <el-button v-if="activeStep === 4" type="success" @click="saveQuote" :loading="dialog.loading">
            保存报价
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入物料对话框 -->
    <el-dialog v-model="showImportDialog" title="从物料库导入" width="800px">
      <MaterialSelector @select="onMaterialSelect" />
    </el-dialog>

    <!-- 签名对话框 -->
    <el-dialog v-model="signatureDialog.visible" :title="signatureDialog.title" width="500px" :close-on-click-modal="false">
      <SignaturePad
        ref="signaturePadRef"
        :title="signatureDialog.title"
        @save="onSignatureSave"
      />
    </el-dialog>


  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, FullScreen, Download, Delete, Edit, Stamp, DocumentCopy, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import MaterialSelector from '@/components/MaterialSelector.vue'
import SignaturePad from '@/components/SignaturePad.vue'

const loading = ref(false)
const quotes = ref([])
const stats = ref({})
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const activeStep = ref(0)
const isExportPdf = ref(false)  // PDF导出时为true，控制引用参数列显示
const showImportDialog = ref(false)

// 物料分类树（从后端动态加载）
const categoryTree = ref([])  // [{id, name, code, children:[{id, name, code}]}]
const activeCategoryTab = ref(null)  // 当前选中的一级分类id
const activeSubCategory = ref(null)  // 当前选中的二级分类id
const materialSearchKeyword = ref('')
const materialSearchResults = ref([])
const materialSearchLoading = ref(false)
const pickerTargetIndex = ref(null)  // 当前正在选择物料的行索引
const pickerSpaceIdx = ref(null)      // 当前正在选择物料的空间索引

// 工艺选项
// 工艺选项（从数据库"特殊工艺"二级分类动态加载）
const craftOptions = ref([])

// 加载工艺选项（特殊工艺分类）- 支持按一级分类过滤
const loadCraftOptions = async (parentId = null) => {
  try {
    const params = parentId ? { parent_id: parentId } : {}
    const res = await request.get('/materials/material-categories/processes', { params })
    if (res.data && res.data.code === 200) {
      craftOptions.value = (res.data.data || []).map(item => ({
        label: item.name,
        coefficient: item.coefficient || 1,
        unit: item.unit || '项',
        unit_price: item.unit_price || 0,
        id: item.id
      }))
    }
  } catch (e) {
    console.warn('加载工艺选项失败', e)
  }
}

// 加载分类树
const loadCategoryTree = async () => {
  try {
    const res = await request.get('/materials/categories')
    const tree = Array.isArray(res) ? res : (res.data || [])
    categoryTree.value = tree
    if (tree.length > 0 && !activeCategoryTab.value) {
      activeCategoryTab.value = tree[0].id
    }
  } catch (e) {
    console.error('加载分类树失败', e)
  }
}

// 当前一级分类下的二级分类列表
const currentSubCategories = computed(() => {
  const parent = categoryTree.value.find(c => c.id === activeCategoryTab.value)
  return parent?.children || []
})

// 搜索物料（大类+二级分类+模糊搜索）
const searchMaterials = async () => {
  materialSearchLoading.value = true
  try {
    const params = { page: 1, page_size: 50 }
    if (materialSearchKeyword.value.trim()) {
      params.keyword = materialSearchKeyword.value.trim()
    }
    // 按二级分类搜索
    if (activeSubCategory.value) {
      params.category_id = activeSubCategory.value
    } else if (activeCategoryTab.value) {
      // 一级分类：搜索其下所有二级分类的物料
      const parent = categoryTree.value.find(c => c.id === activeCategoryTab.value)
      if (parent?.children?.length) {
        params.category_ids = parent.children.map(c => c.id).join(',')
      } else {
        params.category_id = activeCategoryTab.value
      }
    }
    const res = await request.get('/materials', { params })
    materialSearchResults.value = res.items || res.data?.items || []
  } catch (e) {
    console.error('搜索物料失败', e)
    materialSearchResults.value = []
  } finally {
    materialSearchLoading.value = false
  }
}

// 点击物料卡片直接添加到报价
const addMaterialToQuote = (m) => {
  const rowData = {
    id: genId(),
    sku_id: m.id,
    name: m.name,
    spec: m.spec || m.specification || '',
    material_attr: m.material_attr || m.attr || '',
    material: m.material || '',
    color: m.color || '',
    brand: m.brand || '',
    model: m.model || '',
    grade: m.grade || '',
    origin: m.origin || '',
    unit: m.unit || '项',
    quantity: 1,
    unit_price: m.sale_price || m.base_price || 0,
    total_price: m.sale_price || m.base_price || 0,
    image: m.images?.[0] || m.image || m.reference_image || '',
    product_name: '',
    category_level1: activeCategoryTab.value,
    category_level2: activeSubCategory.value || '',
    category_level3: '',
    item_type: 'product',
    remark: '',
    width: null,
    depth: null,
    height: null,
    measurement_value: 1,
    craft_type: '',
    craft_quantity: 1,
    craft_unit: '项',
    craft_coefficient: 1,
    craft_price: 0
  }
  
  // 空间分组模式
  if (pickerSpaceIdx.value !== null && form.spaces[pickerSpaceIdx.value]) {
    const space = form.spaces[pickerSpaceIdx.value]
    if (pickerTargetIndex.value !== null && pickerTargetIndex.value < space.children.length) {
      // 填充到目标行
      const target = space.children[pickerTargetIndex.value]
      Object.assign(target, rowData)
      ElMessage.success(`已填充: ${m.name}`)
    } else {
      // 追加到空间
      space.children.push(rowData)
      ElMessage.success(`已添加到 ${space.room_name || '空间'}: ${m.name}`)
    }
    pickerSpaceIdx.value = null
    pickerTargetIndex.value = null
    calculateTotal()
    return
  }
  
  // 兼容旧模式（扁平 items）
  if (pickerTargetIndex.value !== null && pickerTargetIndex.value < form.items.length) {
    const target = form.items[pickerTargetIndex.value]
    Object.assign(target, rowData, { room_name: target.room_name })
    ElMessage.success(`已填充: ${m.name}`)
    pickerTargetIndex.value = null
  } else if (form.spaces.length > 0) {
    // 没有指定空间时，添加到第一个空间
    const targetSpace = form.spaces[0]
    targetSpace.children.push(rowData)
    ElMessage.success(`已添加到 ${targetSpace.room_name || '空间'}: ${m.name}`)
  } else {
    rowData.room_name = '客厅'
    form.items.push(rowData)
    ElMessage.success(`已添加: ${m.name}`)
  }
  calculateTotal()
}

// 点击行的物料筛选单元格，打开备选框并标记当前行
const openPickerForRow = (spaceIdx, childIdx) => {
  pickerSpaceIdx.value = spaceIdx
  pickerTargetIndex.value = childIdx
  // 滚动到备选框区域
  const el = document.querySelector('.material-picker-card')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}


// 工艺增项计算

// 切换一级分类Tab时自动搜索
const onCategoryTabChange = (tabId) => {
  activeCategoryTab.value = tabId
  activeSubCategory.value = null
  searchMaterials()
}

// 切换二级分类时自动搜索
const onSubCategoryChange = () => {
  searchMaterials()
}

const filterForm = reactive({
  keyword: '',
  status: ''
})

const options = reactive({
  status_list: [],
  service_roles: [],
  rooms: [
    '\u5ba2\u5385',   // Living Room
    '\u9910\u5385',   // Dining Room
    '\u4e3b\u536b',   // Master Bedroom
    '\u6b21\u536b',   // Guest Bedroom
    '\u513f\u7ae5\u623f',   // Kids\' Room
    '\u8001\u4eba\u623f',   // Senior Bedroom
    '\u4e66\u623f/\u5de5\u4f5c\u95f4',  // Study
    '\u4e2d\u53a8',   // Chinese Kitchen
    '\u897f\u53a8',   // Western Kitchen
    '\u5f00\u653e\u5f0f\u53a8\u623f',  // Open Kitchen
    '\u4e3b\u536b',   // Master Bathroom  (no newline, same as Master Bedroom label)
    '\u5ba2\u536b',   // Guest Bathroom
    '\u516c\u536b\uff08\u516c\u5bd3\uff09', // Common Bathroom
    '\u5e72\u6e7f\u5206\u79bb\u536b\u751f\u95f4',  // Wet-Dry Bathroom
    '\u7384\u5173',   // Foyer
    '\u5165\u6237\u82b1\u56ed',  // Entry Garden
    '\u751f\u6d3b\u9633\u53f0',  // Service Balcony
    '\u4f11\u95f2\u9633\u53f0',  // Leisure Balcony
    '\u89c2\u666f\u9633\u53f0',  // View Balcony
    '\u8fc7\u9053/\u8d70\u5eca',  // Corridor
    '\u6b65\u5165\u5f0f\u8863\u5e3d\u95f4',  // Walk-in Closet
    '\u5d4c\u5165\u5f0f\u8863\u5e3d\u95f4',  // Built-in Closet
    '\u50a8\u85cf\u5ba4/\u6742\u7269\u95f4',  // Storage Room
    '\u9601\u697c',   // Attic
    '\u5730\u4e0b\u5ba4',   // Basement
    '\u5f71\u97f3\u5ba4/\u5bb6\u5ead\u5f71\u9662',  // Home Theater
    '\u5065\u8eab\u5ba4/\u7470\u4f53\u8ba1\u5ba4',  // Home Gym
    '\u8336\u5ba4/\u68cb\u724c\u5ba4',  // Tea Room
    '\u7434\u623f/\u753b\u5ba4',  // Art Studio
    '\u4fdd\u59c6\u623f',   // Nanny\'s Room
    '\u513f\u7ae5\u6d3b\u52a8\u533a',  // Kids Play Area
    '\u8001\u4eba\u62a4\u7406\u95f4',  // Elderly Care Room
    '\u5ba0\u7269\u623f',   // Pet Room
    '\u9633\u5149\u623f',   // Sunroom
    '\u5165\u6237\u82b1\u5385',  // Entry Hall Garden
    '\u7a7a\u4e2d\u82b1\u56ed',  // Sky Garden
    '\u9152\u58e2',   // Wine Cellar
    '\u96ea\u852c\u623f',   // Cigar Room
    '\u51a5\u60f3\u5ba4',   // Meditation Room
    '\u79c1\u4eba\u4f1a\u6240',  // Private Clubhouse
    '\u8bbe\u5907\u95f4',   // Equipment Room
  ],
  employees: []
})

const templates = ref([])
const customers = ref([])
const selectedCustomer = ref(null)

const dialog = reactive({
  visible: false,
  isEdit: false,
  loading: false,
  fullscreen: false
})

const form = reactive({
  id: null,
  quote_no: '',
  customer_id: null,
  cover_config: {
    template_id: null,
    template_type: 'modern',
    primary_color: '#8B4513',
    background_image: '',
    logo: '',
    watermark: 'D&B 帝标|设记家全案服务',
    store_name: 'D&B 帝标|设记家·全案落地服务中心',
    show_customer_info: true,
    show_store_name: true
  },
  service_team: [],
  category_summary: {},
  subtotal: 0,
  management_fee: 0,
  management_fee_rate: 5,
  tax: 0,
  tax_rate: 6,
  total_amount: 0,
  items: [],
  spaces: [],  // 空间分组结构 [{id, room_name, product_name, category_id, children:[]}]
  signature_customer: '',
  signature_planner: '',
  signature_manager: '',
  signature_seal: ''
})

// 签名对话框
const signatureDialog = reactive({
  visible: false,
  title: '',
  type: ''
})

const signaturePadRef = ref(null)

// 分类列表（从分类树派生）
const categoryList = computed(() => {
  return categoryTree.value.map(c => ({
    key: c.code,
    id: c.id,
    label: c.name,
    enabled: true
  }))
})

// 分类选项（级联选择器用，带二级分类）
const categoryOptions = computed(() => {
  return categoryTree.value.map(cat => ({
    value: cat.id,
    label: cat.name,
    children: (cat.children || []).map(sub => ({
      value: sub.id,
      label: sub.name
    }))
  }))
})

// 员工选项
const employeeOptions = computed(() => {
  return options.employees.map(e => ({
    value: e.id,
    label: `${e.name} (${e.phone})`
  }))
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await request.get('/quotes', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: filterForm.keyword,
        status: filterForm.status
      }
    })
    quotes.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await request.get('/quotes/statistics')
    stats.value = res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadOptions = async () => {
  try {
    const res = await request.get('/quotes/options')
    Object.assign(options, res)
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const loadTemplates = async () => {
  try {
    const res = await request.get('/quotes/templates')
    templates.value = res
  } catch (error) {
    console.error('加载模板失败', error)
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  loadData()
}

// 创建报价
const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.visible = true
  activeStep.value = 0

  // 加载工艺选项（从数据库特殊工艺分类）
  loadCraftOptions()

  // 重置表单
  Object.assign(form, {
    id: null,
    quote_no: '',
    customer_id: null,
    cover_config: {
      template_id: null,
      template_type: 'modern',
      primary_color: '#8B4513',
      background_image: '',
      logo: '',
      watermark: 'D&B 帝标|设记家全案服务',
      store_name: 'D&B 帝标|设记家·全案落地服务中心',
      show_customer_info: true,
      show_store_name: true
    },
    service_team: [],
    category_summary: {},
    subtotal: 0,
    management_fee: 0,
    management_fee_rate: 5,
    tax: 0,
    tax_rate: 6,
    total_amount: 0,
    items: [],
    signature_customer: '',
    signature_planner: '',
    signature_manager: '',
    signature_seal: ''
  })

  // 初始化分类汇总
  categoryList.value.forEach(cat => {
    form.category_summary[cat.key] = { name: cat.label, amount: 0 }
  })
}

// 封面相关
const selectTemplate = (template) => {
  form.cover_config.template_id = template.id
  form.cover_config.template_type = template.template_type
  if (template.style_config?.primary_color) {
    form.cover_config.primary_color = template.style_config.primary_color
  }
}

const getTemplateStyle = (template) => {
  const color = template.style_config?.primary_color || '#8B4513'
  return {
    background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
    color: '#fff'
  }
}

const getCoverPreviewStyle = () => {
  const config = form.cover_config
  const style = {
    background: config.primary_color || '#8B4513'
  }
  if (config.background_image) {
    style.backgroundImage = `url(${config.background_image})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  }
  return style
}

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
})

const handleCoverUpload = (res) => {
  // axios拦截器已将res解包为{data}，所以res本身就包含file_url
  const url = res.file_url || res.url || res.data?.file_url || res.data?.url
  if (url) {
    form.cover_config.background_image = url
    ElMessage.success('背景图片上传成功')
  } else {
    ElMessage.error('上传响应格式异常')
    console.error('Upload response:', res)
  }
}

const handleLogoUpload = (res) => {
  const url = res.file_url || res.url || res.data?.file_url || res.data?.url
  if (url) {
    form.cover_config.logo = url
    ElMessage.success('Logo上传成功')
  } else {
    ElMessage.error('上传响应格式异常')
    console.error('Upload response:', res)
  }
}

const handleUploadError = (error) => {
  ElMessage.error('上传失败：' + (error?.message || '未知错误'))
  console.error('Upload error:', error)
}

// 团队相关
const addTeamMember = () => {
  form.service_team.push({
    role: '',
    role_name: '',
    employee_id: null,
    name: '',
    phone: ''
  })
}

const removeTeamMember = (index) => {
  form.service_team.splice(index, 1)
}

const onRoleChange = (index) => {
  const member = form.service_team[index]
  const role = options.service_roles.find(r => r.value === member.role)
  if (role) {
    member.role_name = role.label
  }
}

const onEmployeeChange = (index, employeeId) => {
  const member = form.service_team[index]
  const employee = options.employees.find(e => e.id === employeeId)
  if (employee) {
    member.name = employee.name
    member.phone = employee.phone
  }
}

// 分类汇总（实时从 spaces 计算）
const getCategoryAmount = (categoryKey) => {
  let total = 0
  form.spaces.forEach(space => {
    (space.children || []).forEach(item => {
      if (item.category_level1 === categoryKey) {
        total += (item.total_price || 0)
      }
    })
  })
  return total
}

const calculateTotal = () => {
  // 优先计算 spaces 分组模式
  if (form.spaces.length > 0) {
    let subtotal = 0
    form.spaces.forEach(space => {
      space.children.forEach(item => {
        // 增项金额 = 工艺数量 × 工艺价
        item.process_amount = (item.craft_quantity || 0) * (item.craft_price || 0)
        // 小计金额 = 单价 × 计量值 × 数量 × 工艺系数 + 增项金额
        const itemTotal = (item.unit_price || 0) * (item.measurement_value || 1) * (item.quantity || 0) * (item.craft_coefficient || 1) + (item.process_amount || 0)
        item.total_price = itemTotal
        item.row_total = itemTotal // 兼容 V3.2 字段
        subtotal += itemTotal
      })
    })
    form.subtotal = subtotal
  } else {
    // 兼容旧模式：从 category_summary 计算
    let subtotal = 0
    Object.values(form.category_summary).forEach(cat => {
      subtotal += (cat.amount || 0)
    })
    form.subtotal = subtotal
  }

  // 计算管理费
  form.management_fee = form.subtotal * (form.management_fee_rate / 100)

  // 计算税费
  form.tax = (form.subtotal + form.management_fee) * (form.tax_rate / 100)

  // 计算总价
  form.total_amount = form.subtotal + form.management_fee + form.tax
}


// 物料项相关 - 获取分类数组（用于级联选择器）
const getItemCategory = (row) => {
  const result = []
  if (row.category_level1) result.push(row.category_level1)
  if (row.category_level2) result.push(row.category_level2)
  if (row.category_level3) result.push(row.category_level3)
  return result
}

// 物料项相关 - 设置分类数组（用于级联选择器）
const setItemCategory = (row, val) => {
  row.category_level1 = val[0] || ''
  row.category_level2 = val[1] || ''
  row.category_level3 = val[2] || ''
}

const addItem = () => {
  form.items.push({
    room_name: '客厅',
    category_level1: 'hard_material',
    category_level2: '',
    category_level3: '',
    item_type: 'product',
    name: '',
    spec: '',
    brand: '',
    unit: '件',
    quantity: 1,
    unit_price: 0,
    total_price: 0,
    craft_type: '',
    craft_price: 0,
    image: '',
    remark: '',
    // V3.2 增强字段
    width: null,
    depth: null,
    height: null,
    measurement_value: 1,
    craft_quantity: 1,
    craft_unit: '项',
    craft_coefficient: 1,
  })
}

// 克隆行：复制当前行数据，product_name 加“(副本)”后缀
const cloneRow = (spaceIdx, rowIdx) => {
  const space = form.spaces[spaceIdx]
  if (!space || !space.children[rowIdx]) return
  const original = space.children[rowIdx]
  const cloned = { ...original, id: genId() }
  if (cloned.product_name) {
    cloned.product_name = cloned.product_name + '(副本)'
  }
  space.children.splice(rowIdx + 1, 0, cloned)
  calculateTotal()
  ElMessage.success('已克隆行')
}

// 根据单位自动计算计量值（长/深/高 单位：mm）
const autoCalculateMeasurement = (item) => {
  const w = Number(item.width) || 0
  const d = Number(item.depth) || 0
  const h = Number(item.height) || 0
  const unit = (item.unit || '').toLowerCase()
  if (!w && !d && !h) {
    item.measurement_value = 1
    return
  }
  // m3 / 立方米 / m³ → (长*深*高) / 1,000,000,000
  if (['m3', '立方米', 'm³'].includes(unit)) {
    item.measurement_value = (w * d * h) / 1000000000
  }
  // m2 / 平米 / 平方米 / ㎡ → MAX(长*深, 深*高, 长*高) / 1,000,000
  else if (['m2', '平米', '平方米', '㎡'].includes(unit)) {
    item.measurement_value = Math.max(w * d, d * h, w * h) / 1000000
  }
  // m / 米 / 延米 → MAX(长, 深, 高) / 1,000
  else if (['m', '米', '延米'].includes(unit)) {
    item.measurement_value = Math.max(w, d, h) / 1000
  }
  // 其他单位不自动计算，保持原值
  item.measurement_value = Number(item.measurement_value.toFixed(4))
  calculateTotal()
}

const removeItem = (index) => {
  form.items.splice(index, 1)
}

// === 空间分组方法 ===
const genId = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6)

const addSpace = () => {
  form.spaces.push({
    id: genId(),
    room_name: '',
    product_name: '',
    category_id: null,
    children: []
  })
}

const removeSpace = (index) => {
  form.spaces.splice(index, 1)
  calculateTotal()
}

const calculateSpaceTotal = (space) => {
  return (space.children || []).reduce((sum, item) => sum + (item.total_price || 0), 0)
}

const addMaterialToSpace = (space, m) => {
  const rowData = {
    id: genId(),
    sku_id: m.id,
    name: m.name,
    spec: m.spec || m.specification || '',
    material_attr: m.material_attr || m.attr || '',
    material: m.material || '',
    color: m.color || '',
    brand: m.brand || '',
    model: m.model || '',
    grade: m.grade || '',
    origin: m.origin || '',
    unit: m.unit || '项',
    quantity: 1,
    unit_price: m.sale_price || m.base_price || 0,
    total_price: m.sale_price || m.base_price || 0,
    image: m.images?.[0] || m.image || m.reference_image || '',
    product_name: '',
    category_level1: activeCategoryTab.value,
    category_level2: activeSubCategory.value || '',
    category_level3: '',
    item_type: 'product',
    remark: '',
    width: null,
    depth: null,
    height: null,
    measurement_value: 1,
    craft_type: '',
    craft_quantity: 1,
    craft_unit: '项',
    craft_coefficient: 1,
    craft_price: 0
  }
  space.children.push(rowData)
  calculateTotal()
  ElMessage.success(`已添加: ${m.name}`)
}

const calculateItemTotal = (item) => {
  item.total_price = (item.quantity || 0) * (item.unit_price || 0)
}

const onMaterialSelect = (materials) => {
  // 修复Bug：物料应添加到 form.spaces[].children 而不是 form.items
  // 优先使用 pickerSpaceIdx，如果未设置则使用第一个空间
  let targetSpace = null
  
  if (pickerSpaceIdx.value !== null && form.spaces[pickerSpaceIdx.value]) {
    targetSpace = form.spaces[pickerSpaceIdx.value]
  } else if (form.spaces.length > 0) {
    // 如果没有选择空间但有空间存在，使用第一个空间
    targetSpace = form.spaces[0]
    pickerSpaceIdx.value = 0
  } else {
    // 没有空间则创建一个默认空间
    addSpace()
    targetSpace = form.spaces[0]
    pickerSpaceIdx.value = 0
  }
  
  // 确保 children 数组存在
  if (!targetSpace.children) {
    targetSpace.children = []
  }
  
  materials.forEach(m => {
    // 构建物料行数据，匹配 children 结构
    const rowData = {
      id: genId(),
      sku_id: m.id,
      sku_code: m.sku_code || '',
      name: m.name,
      material_name: m.name,  // 兼容字段
      custom_name: '',        // 自定义商品名称
      spec: m.spec || m.specification || '',
      material_attr: m.material_attr || m.attr || '',
      material: m.material || '',
      color: m.color || '',
      brand: m.brand || '',
      unit: m.unit || '项',
      quantity: 1,
      unit_price: m.sale_price || m.base_price || 0,
      total_price: m.sale_price || m.base_price || 0,
      // 定制参数
      custom_width: null,
      custom_depth: null,
      custom_height: null,
      custom_result: null,
      // 工艺增项
      process_id: null,
      process_name: '',
      process_coefficient: 1,
      process_quantity: 0,
      process_unit: '',
      process_unit_price: 0,
      process_amount: 0,
      // 工艺字段
      craft_type: m.craft_type || '',
      craft_quantity: 1,
      craft_unit: m.craft_unit || '项',
      craft_coefficient: 1,
      craft_price: 0,
      // 图片
      image: m.images?.[0] || m.image || m.reference_image || '',
      material_image: m.images?.[0] || '',
      category_level1: m.category_level1 || 'hard_material',
      category_level2: '',
      remark: '',
      room_name: targetSpace.room_name || '客厅'
    }
    // 添加到正确空间的 children 数组
    targetSpace.children.push(rowData)
  })
  
  // 重新计算总价
  calculateTotal()
  showImportDialog.value = false
  
  // 提示用户
  ElMessage.success(`已添加 ${materials.length} 个物料到 ${targetSpace.room_name || '空间'}`)
}

// 签名相关
const openSignatureDialog = (type) => {
  signatureDialog.type = type
  const titles = {
    customer: '客户签名',
    planner: '规划师签名',
    manager: '店长签名'
  }
  signatureDialog.title = titles[type] || '签名'
  signatureDialog.visible = true
}

const onSignatureSave = (signatureData) => {
  const type = signatureDialog.type
  if (type === 'customer') {
    form.signature_customer = signatureData
  } else if (type === 'planner') {
    form.signature_planner = signatureData
  } else if (type === 'manager') {
    form.signature_manager = signatureData
  }
  signatureDialog.visible = false
}

// 报价预览
const quotePreviewUrl = ref('')

const generateQuotePreview = () => {
  const f = form
  const total = calculateTotal()
  const spacesHtml = f.spaces && f.spaces.length > 0
    ? f.spaces.map((s, i) => `
      <tr>
        <td colspan="6" style="background:#8B5A2B;color:#fff;padding:8px;font-weight:bold;">
          ${i+1}、${s.name || '空间' + (i+1)}
        </td>
      </tr>
      ${(s.children || []).map(item => `
        <tr>
          <td>${item.material_name || '-'}</td>
          <td>${item.brand || '-'}</td>
          <td>${item.spec || '-'}</td>
          <td>${item.unit || '-'}</td>
          <td style="text-align:right;">¥${item.unit_price || 0}</td>
          <td style="text-align:right;">¥${((item.unit_price || 0) * (item.quantity || 0)).toFixed(2)}</td>
        </tr>
      `).join('')}
    `).join('')
    : '<tr><td colspan="6" style="text-align:center;color:#999;">暂无物料</td></tr>'

  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>报价预览 - ${f.quote_name || '报价单'}</title>
<style>
body { font-family: Arial, sans-serif; padding: 40px; color: #333; }
.header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #8B5A2B; padding-bottom: 20px; }
.total { font-size: 24px; color: #8B5A2B; font-weight: bold; margin: 20px 0; text-align: right; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #8B5A2B; color: #fff; }
</style>
</head>
<body>
<div class="header">
<h1 style="color:#8B5A2B;">${f.quote_name || '装修报价单'}</h1>
<p><strong>客户：</strong>${f.customer_name || '-'} &nbsp; <strong>电话：</strong>${f.customer_phone || '-'}</p>
<p><strong>地址：</strong>${f.project_address || '-'}</p>
</div>
<div class="total">报价总额：¥${(total || 0).toFixed(2)}</div>
<table>
<tr><th>物料名称</th><th>品牌</th><th>规格</th><th>单位</th><th>单价</th><th>小计</th></tr>
${spacesHtml}
</table>
</body>
</html>`

  const blob = new Blob([html], { type: 'text/html' })
  quotePreviewUrl.value = URL.createObjectURL(blob)
}

// 保存报价
const saveQuote = async () => {
  // 同步分类汇总金额到 category_summary（后端需要）
  categoryList.value.forEach(cat => {
    if (form.category_summary[cat.key]) {
      form.category_summary[cat.key].amount = getCategoryAmount(cat.key)
    }
  })
  dialog.loading = true
  try {
    if (dialog.isEdit) {
      await request.put(`/quotes/${form.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/quotes', form)
      ElMessage.success('创建成功')
    }
    dialog.visible = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    dialog.loading = false
  }
}

// 其他操作
const router = useRouter()

const viewDetail = (row) => {
  router.push(`/admin/quotes/${row.id}`)
}

const editQuote = (row) => {
  // 编辑报价 - 跳转到详情页，后续改造表单支持编辑模式
  router.push(`/admin/quotes/${row.id}`)
}

const previewQuote = async (row) => {
  try {
    ElMessage.info('正在生成PDF预览...')
    isExportPdf.value = true
    const token = localStorage.getItem('token')
    // 生成紧凑版预览（show_ref=false），按需展开引用参数列
    const response = await fetch(`/api/v3/quotes/${row.id}/pdf-preview?show_ref=true`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('PDF生成失败')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `报价单_${row.quote_no}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('PDF预览生成成功')
  } catch (error) {
    ElMessage.error('PDF预览失败：' + (error.message || '未知错误'))
  } finally {
    isExportPdf.value = false
  }
}

const deleteQuote = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该报价吗？', '提示', { type: 'warning' })
    await request.delete(`/quotes/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

// 辅助函数
const statusType = (status) => {
  const types = {
    draft: 'info',
    sent: 'warning',
    confirmed: 'success',
    signed: 'success',
    expired: 'danger'
  }
  return types[status] || 'info'
}

const statusLabel = (status) => {
  const labels = {
    draft: '草稿',
    sent: '已发送',
    confirmed: '已确认',
    signed: '已签署',
    expired: '已过期'
  }
  return labels[status] || status
}

const formatMoney = (amount) => {
  if (!amount) return '0'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

// 报价状态映射
const getStatusType = (status) => {
  const map = { 'draft': 'info', 'pending': 'warning', 'approved': 'success', 'rejected': 'danger' }
  return map[status] || 'info'
}
const getStatusText = (status) => {
  const map = { 'draft': '草稿', 'pending': '待审核', 'approved': '已通过', 'rejected': '已驳回' }
  return map[status] || status
}
const submitQuote = async (row) => {
  try {
    await request.post(`/quotes/${row.id}/submit`)
    ElMessage.success('提交成功')
    fetchQuotes()
  } catch (e) { ElMessage.error('提交失败') }
}
const approveQuote = async (row) => {
  try {
    await request.post(`/quotes/${row.id}/approve`)
    ElMessage.success('审核通过')
    fetchQuotes()
  } catch (e) { ElMessage.error('审核失败') }
}
const rejectQuote = async (row) => {
  const reason = prompt("请输入驳回原因:")
  if (!reason) return
  try {
    await request.post(`/quotes/${row.id}/reject`, { reason })
    ElMessage.success('已驳回')
    fetchQuotes()
  } catch (e) { ElMessage.error('驳回失败') }
}

onMounted(() => {
  loadData()
  loadStats()
  loadOptions()
  loadTemplates()
  loadCategoryTree()

  // 初始化分类汇总
  categoryList.value.forEach(cat => {
    form.category_summary[cat.key] = { name: cat.label, amount: 0 }
  })
})
</script>

<style scoped>
.quote-manage {
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
  font-size: 24px;
  font-weight: bold;
  color: #262626;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.stat-card.total .stat-value {
  color: #52c41a;
}

.filter-card {
  margin-bottom: 24px;
}

.customer-name {
  font-weight: 500;
  color: #262626;
}

.customer-phone {
  font-size: 12px;
  color: #8c8c8c;
}

.amount {
  font-weight: 500;
  color: #f5222d;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 对话框样式 */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quote-steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 模板选择 */
.template-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.template-item {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.template-item.active {
  border-color: #409eff;
}

.template-preview {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

/* 封面上传 */
.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 120px;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  width: 120px;
  height: 120px;
}

.logo-uploader:hover {
  border-color: #409eff;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
}

/* 封面预览 */
.cover-preview {
  min-height: 500px;
  border-radius: 12px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  overflow: hidden;
}

.cover-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-30deg);
  font-size: 48px;
  opacity: 0.1;
  white-space: nowrap;
  pointer-events: none;
}

.cover-content {
  text-align: center;
  z-index: 1;
}

.cover-logo {
  max-width: 120px;
  max-height: 60px;
  margin-bottom: 20px;
}

.cover-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.cover-subtitle {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.cover-info {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  padding: 24px 40px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  width: 80px;
  opacity: 0.8;
}

.info-item .value {
  font-weight: 500;
}

.cover-quote-no {
  font-size: 14px;
  opacity: 0.7;
  letter-spacing: 2px;
}

/* 团队预览 */
.team-preview {
  margin-top: 30px;
}

.team-preview h4 {
  margin-bottom: 16px;
}

.team-member-card {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 16px;
}

.team-member-card .role {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.team-member-card .name {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.team-member-card .phone {
  font-size: 12px;
  color: #8c8c8c;
}

/* 分类卡片 */
.category-card {
  margin-bottom: 16px;
}

.category-card .category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-card .category-name {
  font-weight: 500;
}

.total-amount {
  font-size: 24px;
  font-weight: bold;
  color: #f5222d;
}

/* 物料项 */
.item-total {
  font-weight: 500;
  color: #f5222d;
}

/* 签名上传 */
.signature-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  width: 200px;
  height: 100px;
}

.signature-uploader:hover {
  border-color: #409eff;
}

.signature-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
}

.signature-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
}

.signature-placeholder span {
  font-size: 12px;
  margin-top: 8px;
}

/* 签名显示 */
.signature-wrapper {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  width: 200px;
  height: 100px;
  cursor: pointer;
  overflow: hidden;
}

.signature-wrapper:hover {
  border-color: #409eff;
}

.signature-display {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
}

.signature-add {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  background: #fafafa;
}

.signature-add span {
  font-size: 12px;
  margin-top: 8px;
}

/* 报价汇总 */
.quote-summary {
  padding: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.summary-row.total {
  font-size: 18px;
  font-weight: bold;
}

.summary-row .total-price {
  color: #f5222d;
  font-size: 24px;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.dialog-footer .selected-tip {
  flex: 1;
  color: #666;
}

/* 筛选表单 */
.filter-form {
  margin-bottom: 16px;
}

/* ========== material detail table (Excel style) ========== */
.material-detail-table { font-size: 13px; }
.material-detail-table th { background-color: #f5f7fa !important; color: #303133; font-weight: 600; font-size: 12px; padding: 6px 4px !important; }
.material-detail-table td { padding: 4px 4px !important; vertical-align: middle; }

/* material picker column - green clickable cell */
.material-picker-col .cell { padding: 0 !important; }
.material-picker-cell {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 10px; cursor: pointer; border-radius: 4px;
  transition: all 0.2s ease; min-height: 32px;
  background-color: #f0f9eb; border: 1px solid #e1f3d8;
  width: 100%; box-sizing: border-box;
}
.material-picker-cell:hover { background-color: #e1f3d8; border-color: #67C23A; box-shadow: 0 0 0 2px rgba(103,194,58,0.15); }
.material-picker-cell.active { background-color: #67C23A; border-color: #529b2e; box-shadow: 0 0 0 2px rgba(103,194,58,0.3); }
.material-picker-cell.active .picker-cell-text,
.material-picker-cell.active .picker-cell-placeholder { color: #fff; }
.picker-cell-text { color: #303133; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.picker-cell-placeholder { color: #909399; font-size: 12px; }

/* amount column - red */
.amount-col .item-total { color: #F56C6C; font-weight: 600; font-size: 13px; }

/* material picker card */
.material-picker-card { margin-top: 16px; border: 2px solid #E6A23C; }
.material-picker-card :deep(.el-card__header) { background-color: #fdf6ec; border-bottom: 1px solid #E6A23C; }

.material-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px; max-height: 300px; overflow-y: auto; padding: 8px 0;
}
.material-card {
  border: 1px solid #ebeef5; border-radius: 8px; padding: 10px; cursor: pointer;
  transition: all 0.2s; display: flex; flex-direction: column;
  align-items: center; gap: 6px;
}
.material-card:hover { border-color: #409EFF; box-shadow: 0 2px 10px rgba(64,158,255,0.15); transform: translateY(-1px); }
.material-card-img { width: 60px; height: 60px; border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.material-card-img img { width: 100%; height: 100%; object-fit: cover; }
.material-card-info { text-align: center; width: 100%; }
.material-card-name { font-size: 12px; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.3; }
.material-card-meta { font-size: 11px; color: #909399; display: flex; justify-content: center; gap: 6px; }
.material-card-price { color: #F56C6C; font-size: 13px; font-weight: 600; }
.sub-category-bar { display: flex; gap: 10px; align-items: center; margin: 10px 0; }

/* 空间分组卡片 */
.space-card { margin-bottom: 16px; }
.space-header { display: flex; justify-content: space-between; align-items: center; }
.space-title { display: flex; align-items: center; }
.space-actions { display: flex; align-items: center; gap: 12px; }
.space-total { font-size: 14px; color: #F56C6C; font-weight: 600; }
</style>