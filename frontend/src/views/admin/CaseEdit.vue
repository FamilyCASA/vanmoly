<template>
  <div class="case-edit">
    <!-- 顶部操作栏 -->
    <div class="header-bar">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>返回列表
        </el-button>
        <span class="divider">|</span>
        <h3>{{ isEdit ? '编辑案例' : '新建案例' }}</h3>
        <el-tag v-if="caseData.status" :type="getStatusType(caseData.status)" class="status-tag">
          {{ caseData.status }}
        </el-tag>
      </div>
      <div class="header-right">
        <el-button @click="handleSaveDraft" :loading="saving">保存草稿</el-button>
        <el-button type="primary" @click="handlePublish" :loading="publishing">
          {{ caseData.status === '已发布' ? '更新发布' : '立即发布' }}
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧标签页 -->
      <div class="left-panel">
        <el-tabs v-model="activeTab" type="border-card" class="edit-tabs">
          <!-- 基础信息 -->
          <el-tab-pane label="基础信息" name="basic">
            <el-form :model="caseData" label-position="top" class="edit-form">
              <el-row :gutter="24">
                <el-col :span="16">
                  <el-form-item label="案例标题" required>
                    <el-input v-model="caseData.title" placeholder="请输入案例标题" maxlength="100" show-word-limit />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="案例编号">
                    <el-input v-model="caseData.case_no" placeholder="自动生成" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="氛围标题" required>
                    <el-select v-model="caseData.atmosphere" style="width: 100%" placeholder="选择氛围">
                      <el-option label="温馨" value="温馨" />
                      <el-option label="清新" value="清新" />
                      <el-option label="简约" value="简约" />
                      <el-option label="浪漫" value="浪漫" />
                      <el-option label="雅致" value="雅致" />
                      <el-option label="沉稳" value="沉稳" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 配色方案 -->
              <el-row :gutter="24">
                <el-col :span="24">
                  <el-form-item label="配色方案">
                    <morandi-color-picker v-model="caseData.colors" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24" v-if="false">
                <el-col :span="8">
                  <el-form-item label="空间类型">
                    <el-select v-model="caseData.space_type" style="width: 100%" clearable placeholder="选择空间">
                      <el-option label="全案" value="全案" />
                      <el-option label="客厅" value="客厅" />
                      <el-option label="餐厅" value="餐厅" />
                      <el-option label="厨房" value="厨房" />
                      <el-option label="卧室" value="卧室" />
                      <el-option label="书房" value="书房" />
                      <el-option label="卫生间" value="卫生间" />
                      <el-option label="阳台" value="阳台" />
                      <el-option label="玄关" value="玄关" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="设计风格">
                    <el-select v-model="caseData.style" style="width: 100%" clearable filterable allow-create placeholder="搜索或选择风格">
                      <el-option label="现代简约" value="现代简约" />
                      <el-option label="北欧" value="北欧" />
                      <el-option label="日式" value="日式" />
                      <el-option label="新中式" value="新中式" />
                      <el-option label="轻奢" value="轻奢" />
                      <el-option label="法式" value="法式" />
                      <el-option label="美式" value="美式" />
                      <el-option label="工业风" value="工业风" />
                      <el-option label="侘寂风" value="侘寂风" />
                      <el-option label="奶油风" value="奶油风" />
                      <el-option label="中古风" value="中古风" />
                      <el-option label="极简主义" value="极简主义" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="所属楼盘" :required="caseData.is_real_case">
                    <el-select v-model="caseData.building_id" style="width: 100%" clearable filterable placeholder="真实案例请选择楼盘" @change="handleBuildingChange">
                      <el-option
                        v-for="item in buildingOptions"
                        :key="item.id"
                        :label="item.name"
                        :value="item.id"
                      />
                    </el-select>
                    <div v-if="caseData.is_real_case && !caseData.building_id" class="el-form-item__error" style="color: #e6a23c;">
                      真实案例必须选择楼盘，虚拟案例可不选
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="详细地址">
                    <el-input v-model="caseData.address" placeholder="选择楼盘后自动填充" :disabled="!caseData.is_real_case" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="客户名称">
                    <el-input v-model="caseData.customer_name" placeholder="请输入客户称呼" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="户型">
                    <el-select v-model="caseData.house_type" style="width: 100%" clearable filterable allow-create placeholder="选择户型">
                      <el-option label="一室一厅" value="一室一厅" />
                      <el-option label="一室两厅" value="一室两厅" />
                      <el-option label="两室一厅" value="两室一厅" />
                      <el-option label="两室两厅" value="两室两厅" />
                      <el-option label="三室一厅" value="三室一厅" />
                      <el-option label="三室两厅" value="三室两厅" />
                      <el-option label="三室两厅一卫" value="三室两厅一卫" />
                      <el-option label="三室两厅两卫" value="三室两厅两卫" />
                      <el-option label="四室一厅" value="四室一厅" />
                      <el-option label="四室两厅" value="四室两厅" />
                      <el-option label="四室两厅两卫" value="四室两厅两卫" />
                      <el-option label="四室三厅" value="四室三厅" />
                      <el-option label="五室两厅" value="五室两厅" />
                      <el-option label="五室三厅" value="五室三厅" />
                      <el-option label="别墅" value="别墅" />
                      <el-option label="公寓" value="公寓" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="面积（㎡）">
                    <el-input-number v-model="caseData.area" :min="0" :precision="2" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="预算区间">
                    <div style="display: flex; gap: 8px;">
                      <el-input v-model="caseData.budget_range" placeholder="如：25-35万" style="flex: 1;" />
                      <el-button @click="showQuoteTableDialog = true">引用报价表</el-button>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="全案规划师">
                    <el-select v-model="caseData.planner_id" style="width: 100%" clearable filterable placeholder="引用员工（可不选）">
                      <el-option
                        v-for="item in employeeOptions"
                        :key="item.id"
                        :label="item.title ? `${item.name} - ${item.title}` : item.name"
                        :value="item.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="全案设计师">
                    <el-select v-model="caseData.designer_id" style="width: 100%" clearable filterable placeholder="引用员工（可不选）">
                      <el-option
                        v-for="item in employeeOptions"
                        :key="item.id"
                        :label="item.title ? `${item.name} - ${item.title}` : item.name"
                        :value="item.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="客户经理">
                    <el-select v-model="caseData.responsible_id" style="width: 100%" clearable filterable placeholder="引用员工（可不选）">
                      <el-option
                        v-for="item in employeeOptions"
                        :key="item.id"
                        :label="item.title ? `${item.name} - ${item.title}` : item.name"
                        :value="item.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="标签">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
                      <el-check-tag :checked="caseData.is_top" @change="caseData.is_top = $event">置顶</el-check-tag>
                      <el-check-tag :checked="caseData.tags?.includes('热门')" @change="toggleTag('热门')">热门</el-check-tag>
                      <el-check-tag :checked="caseData.tags?.includes('店长推荐')" @change="toggleTag('店长推荐')">店长推荐</el-check-tag>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="发布控制">
                    <div style="display: flex; gap: 16px; align-items: center;">
                      <el-checkbox v-model="caseData.owner_authorized">业主授权</el-checkbox>
                      <el-checkbox v-model="caseData.is_public">公开发布</el-checkbox>
                      <el-checkbox v-model="caseData.is_real_case">真实案例</el-checkbox>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="案例简介">
                <el-input v-model="caseData.description" type="textarea" :rows="3" placeholder="请输入案例简介" />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 视觉素材 -->
          <el-tab-pane label="视觉素材" name="media">
            <div class="media-section">
              <h4>英雄主图 <span style="color: #999; font-size: 13px;">（最多5张，用于首页轮播展示）</span></h4>
              <div class="image-upload-grid">
                <div
                  v-for="(img, idx) in heroImageList"
                  :key="img.uid || idx"
                  class="uploaded-image-card"
                  @click="openImageDescDialog(heroImageList, idx, 'hero')"
                >
                  <img :src="img.url" alt="英雄图" />
                  <div class="img-card-overlay">
                    <span class="img-desc-badge" v-if="img.description">已填简介</span>
                    <span class="img-desc-badge empty" v-else>添加简介</span>
                    <el-icon class="img-delete-btn" @click.stop="handleHeroImageRemoveByIndex(idx)"><Close /></el-icon>
                  </div>
                </div>
                <div class="upload-trigger-card" v-if="heroImageList.length < 5" @click="triggerHeroUpload">
                  <el-icon><Plus /></el-icon>
                  <span>上传图片</span>
                </div>
              </div>
              <el-upload
                ref="heroUploadRef"
                :action="uploadUrl"
                :headers="uploadHeaders"
                list-type="text"
                :show-file-list="false"
                :on-success="handleHeroImageSuccess"
                :before-upload="beforeImageUpload"
                multiple
                :limit="5"
                :on-exceed="() => ElMessage.warning('最多上传5张英雄图')"
                style="display: none;"
              />
              <div class="upload-tip">建议尺寸 1200 x 800，最多5张，将用于案例首页轮播。点击上方图片可添加简介。</div>
            </div>

            <div class="media-section">
              <h4>封面图</h4>
              <ImageCropperUpload
                v-model="caseData.cover_image"
                placeholder="上传案例封面"
                :crop-enabled="true"
              />
              <div class="upload-tip">建议尺寸 1200 x 800，支持图片/视频链接</div>
            </div>

            <div class="media-section">
              <h4>效果图图集 <span style="color: #999; font-size: 13px;">（{{ mediaList.length }} 张）</span></h4>
              <div class="image-upload-grid">
                <div
                  v-for="(img, idx) in mediaList"
                  :key="img.uid || idx"
                  class="uploaded-image-card"
                  @click="openImageDescDialog(mediaList, idx, 'gallery')"
                >
                  <img :src="img.url" alt="效果图" />
                  <div class="img-card-overlay">
                    <span class="img-desc-badge" v-if="img.description">已填简介</span>
                    <span class="img-desc-badge empty" v-else>添加简介</span>
                    <el-icon class="img-delete-btn" @click.stop="handleMediaRemoveByIndex(idx)"><Close /></el-icon>
                  </div>
                </div>
                <div class="upload-trigger-card" @click="triggerGalleryUpload">
                  <el-icon><Plus /></el-icon>
                  <span>上传图片</span>
                </div>
              </div>
              <el-upload
                ref="galleryUploadRef"
                :action="uploadUrl"
                :headers="uploadHeaders"
                list-type="text"
                :show-file-list="false"
                :on-success="handleMediaSuccess"
                :before-upload="beforeImageUpload"
                multiple
                style="display: none;"
              />
            </div>

            <div class="media-section">
              <h4>VR 二维码</h4>
              <ImageCropperUpload
                v-model="caseData.vr_qrcode"
                placeholder="上传VR二维码图片"
                :crop-enabled="false"
              />
              <div class="upload-tip">建议正方形图片，180x180px以上</div>
            </div>

            <div class="media-section">
              <h4>360VR 链接</h4>
              <el-input v-model="caseData.vr_link" placeholder="请输入 VR 全景链接">
                <template #prefix>
                  <el-icon><View /></el-icon>
                </template>
              </el-input>
            </div>
          </el-tab-pane>

          <!-- 文案内容 -->
          <el-tab-pane label="文案内容" name="content">
            <el-form :model="caseData" label-position="top" class="edit-form">
              <el-form-item label="设计理念">
                <el-input v-model="caseData.design_concept" type="textarea" :rows="6" placeholder="描述设计理念..." />
              </el-form-item>

              <el-form-item label="全屋规划">
                <el-input v-model="caseData.whole_house_plan" type="textarea" :rows="6" placeholder="描述全屋空间规划..." />
              </el-form-item>

              <el-form-item label="客户需求">
                <el-input v-model="caseData.customer_requirements" type="textarea" :rows="4" placeholder="记录客户原始需求..." />
              </el-form-item>

              <el-form-item label="设计亮点">
                <el-input v-model="caseData.design_highlights" type="textarea" :rows="4" placeholder="描述设计亮点..." />
              </el-form-item>

              <el-form-item label="客户价值">
                <el-input v-model="caseData.customer_value" type="textarea" :rows="4" placeholder="描述为客户创造的价值..." />
              </el-form-item>

              <el-form-item label="收纳规划方案">
                <el-input v-model="caseData.storage_plan" type="textarea" :rows="4" placeholder="描述设记家精细化收纳规划，如玄关+厨房双收纳体系..." />
              </el-form-item>

              <el-form-item label="全案落地执行细节">
                <el-input v-model="caseData.execution_detail" type="textarea" :rows="4" placeholder="描述全案落地执行的特色与细节..." />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 报价配置 -->
          <el-tab-pane label="报价配置" name="price">
            <el-form :model="caseData" label-position="top" class="edit-form">
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="全案总价（元）">
                    <el-input-number v-model="caseData.total_price" :min="0" :precision="2" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="成交型预算（元）">
                    <el-input-number v-model="caseData.deal_budget" :min="0" :precision="2" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="套餐配置">
                    <el-select v-model="caseData.package_type" style="width: 100%" clearable>
                      <el-option label="全案A套餐" value="全案A" />
                      <el-option label="全案B套餐" value="全案B" />
                      <el-option label="全案S套餐" value="全案S" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="造价明细">
                <el-table :data="priceDetailList" border style="width: 100%">
                  <el-table-column prop="item" label="项目" width="150">
                    <template #default="{ row, $index }">
                      <el-input v-model="row.item" placeholder="项目名称" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="desc" label="说明">
                    <template #default="{ row }">
                      <el-input v-model="row.desc" placeholder="项目说明" />
                    </template>
                  </el-table-column>
                  <el-table-column prop="amount" label="金额" width="150">
                    <template #default="{ row }">
                      <el-input-number v-model="row.amount" :min="0" :precision="2" style="width: 100%" />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="80">
                    <template #default="{ $index }">
                      <el-button type="danger" link @click="removePriceItem($index)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-button type="primary" link @click="addPriceItem" style="margin-top: 12px">
                  <el-icon><Plus /></el-icon>添加明细
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 时间轴 -->
          <el-tab-pane label="时间轴" name="timeline">
            <div class="timeline-section">
              <el-button type="primary" @click="openAddTimelineDialog">
                <el-icon><Plus /></el-icon>添加节点
              </el-button>

              <el-timeline class="case-timeline">
                <el-timeline-item
                  v-for="(node, index) in timelineList"
                  :key="node.id || index"
                  :timestamp="formatDate(node.node_time)"
                  placement="top"
                >
                  <el-card>
                    <template #header>
                      <div class="timeline-header">
                        <span>{{ node.title }}</span>
                        <div class="timeline-actions">
                          <el-button type="primary" link @click="editTimelineNode(node)">编辑</el-button>
                          <el-button type="danger" link @click="deleteTimelineNode(node)">删除</el-button>
                        </div>
                      </div>
                    </template>
                    <p>{{ node.content }}</p>
                    <div v-if="node.media_urls" class="timeline-media">
                      <el-image
                        v-for="(url, idx) in parseMediaUrls(node.media_urls)"
                        :key="idx"
                        :src="url"
                        style="width: 100px; height: 80px; margin-right: 8px"
                        fit="cover"
                      />
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>

              <el-empty v-if="timelineList.length === 0" description="暂无时间轴节点" />
            </div>
          </el-tab-pane>

          <!-- 服务流程 -->
          <el-tab-pane label="服务流程" name="workflow">
            <div class="workflow-section">
              <!-- 未初始化状态 -->
              <div v-if="!workflowInitialized" class="workflow-empty">
                <el-empty description="该案例尚未关联服务流程">
                  <el-button type="primary" @click="handleInitWorkflow" :loading="workflowLoading">
                    初始化服务流程
                  </el-button>
                </el-empty>
                <div class="workflow-hint">
                  <p>初始化条件：案例已关联客户 + 已关联楼盘 + 存在全案服务流程</p>
                </div>
              </div>

              <!-- 已初始化状态 -->
              <div v-else>
                <!-- 授权开关 -->
                <div class="workflow-auth-bar">
                  <div class="auth-info">
                    <el-tag type="success" v-if="workflowData.is_real_case">真实案例</el-tag>
                    <el-tag type="info" v-else>虚拟方案</el-tag>
                    <span class="node-summary">
                      共 {{ workflowTimeline.length }} 个节点 ·
                      已完成 {{ workflowTimeline.filter(n => n.status === 'completed').length }} ·
                      进行中 {{ workflowTimeline.filter(n => n.status === 'ongoing').length }}
                    </span>
                  </div>
                  <div class="auth-toggle">
                    <span>公开展示服务流程</span>
                    <el-switch
                      v-model="workflowData.enable_public_workflow"
                      @change="handleTogglePublicWorkflow"
                      active-text="公开"
                      inactive-text="隐藏"
                    />
                  </div>
                </div>

                <!-- 进度条 -->
                <div class="workflow-progress">
                  <el-progress
                    :percentage="workflowProgress"
                    :stroke-width="12"
                    :color="workflowProgress === 100 ? '#67c23a' : '#e6a23c'"
                  />
                </div>

                <!-- 按阶段分组的时间轴 -->
                <div v-for="phase in phaseGroups" :key="phase.key" class="phase-group">
                  <div class="phase-header">
                    <span class="phase-icon">{{ phase.icon }}</span>
                    <span class="phase-name">{{ phase.label }}</span>
                    <span class="phase-count">{{ phase.nodes.length }} 个节点</span>
                    <span class="phase-progress">
                      {{ phase.nodes.filter(n => n.status === 'completed').length }}/{{ phase.nodes.length }}
                    </span>
                  </div>

                  <div class="phase-nodes">
                    <div
                      v-for="node in phase.nodes"
                      :key="node.id"
                      class="workflow-node"
                      :class="'status-' + node.status"
                    >
                      <div class="node-status-dot"></div>
                      <div class="node-content">
                        <div class="node-header">
                          <span class="node-name">{{ node.node_name }}</span>
                          <el-tag :type="nodeStatusType(node.status)" size="small">
                            {{ nodeStatusLabel(node.status) }}
                          </el-tag>
                        </div>
                        <div class="node-time" v-if="node.start_time || node.end_time">
                          <span v-if="node.start_time">开始: {{ formatDate(node.start_time) }}</span>
                          <span v-if="node.end_time">完成: {{ formatDate(node.end_time) }}</span>
                        </div>
                        <div class="node-notes" v-if="node.notes">{{ node.notes }}</div>

                        <!-- 照片区域 -->
                        <div class="node-photos" v-if="node.photos && node.photos.length">
                          <el-image
                            v-for="(url, idx) in node.photos"
                            :key="idx"
                            :src="addImagePrefix(url)"
                            :preview-src-list="node.photos.map(u => addImagePrefix(u))"
                            :initial-index="idx"
                            fit="cover"
                            style="width: 80px; height: 60px; margin-right: 6px; border-radius: 4px;"
                          />
                        </div>

                        <!-- 效果图区域 -->
                        <div class="node-renderings" v-if="node.renderings && node.renderings.length">
                          <span class="rendering-label">效果图：</span>
                          <el-image
                            v-for="(url, idx) in node.renderings"
                            :key="idx"
                            :src="addImagePrefix(url)"
                            :preview-src-list="node.renderings.map(u => addImagePrefix(u))"
                            :initial-index="idx"
                            fit="cover"
                            style="width: 80px; height: 60px; margin-right: 6px; border-radius: 4px;"
                          />
                        </div>

                        <!-- 操作按钮 -->
                        <div class="node-actions">
                          <el-dropdown trigger="click" @command="(cmd) => handleNodeCommand(cmd, node)">
                            <el-button size="small" type="primary" link>
                              操作 <el-icon><ArrowRight /></el-icon>
                            </el-button>
                            <template #dropdown>
                              <el-dropdown-menu>
                                <el-dropdown-item command="ongoing" :disabled="node.status === 'ongoing' || node.status === 'completed'">
                                  标记进行中
                                </el-dropdown-item>
                                <el-dropdown-item command="completed" :disabled="node.status === 'completed'">
                                  标记已完成
                                </el-dropdown-item>
                                <el-dropdown-item command="pending">
                                  重置为计划中
                                </el-dropdown-item>
                                <el-dropdown-item command="upload_photo" divided>
                                  上传施工照片
                                </el-dropdown-item>
                                <el-dropdown-item command="upload_rendering">
                                  上传效果图
                                </el-dropdown-item>
                                <el-dropdown-item command="edit_notes">
                                  编辑备注
                                </el-dropdown-item>
                                <el-dropdown-item command="toggle_public">
                                  {{ node.is_public ? '隐藏此节点' : '公开此节点' }}
                                </el-dropdown-item>
                              </el-dropdown-menu>
                            </template>
                          </el-dropdown>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 文件管理 -->
          <el-tab-pane label="文件管理" name="files">
            <div class="files-section">
              <h4>PDF 资料</h4>
              <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                :on-success="handleFileSuccess"
                :before-upload="beforePdfUpload"
                accept=".pdf"
              >
                <el-button type="primary">
                  <el-icon><Upload /></el-icon>上传 PDF
                </el-button>
              </el-upload>

              <el-table :data="fileList" style="margin-top: 16px" border>
                <el-table-column prop="file_name" label="文件名" />
                <el-table-column prop="file_type" label="类型" width="120">
                  <template #default="{ row }">
                    <el-tag v-if="row.has_watermark" type="warning">带水印</el-tag>
                    <el-tag v-else type="success">无水印</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="download_count" label="下载次数" width="100" />
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button type="primary" link @click="previewFile(row)">预览</el-button>
                    <el-button type="danger" link @click="deleteFile(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- 发布设置 -->
          <el-tab-pane label="发布设置" name="publish">
            <el-form :model="caseData" label-position="top" class="edit-form">
              <el-form-item label="发布方式">
                <el-radio-group v-model="publishMode">
                  <el-radio value="immediate">立即发布</el-radio>
                  <el-radio value="schedule">定时发布</el-radio>
                  <el-radio value="draft">保存为草稿</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="publishMode === 'schedule'" label="定时发布时间">
                <el-date-picker
                  v-model="caseData.scheduled_time"
                  type="datetime"
                  placeholder="选择发布时间"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="同步设置">
                <el-checkbox v-model="caseData.sync_xiaohongshu">同步至小红书</el-checkbox>
                <el-checkbox v-model="caseData.sync_mp">同步至公众号</el-checkbox>
              </el-form-item>

              <el-form-item label="订阅通知">
                <el-checkbox v-model="caseData.enable_subscription">开启案例订阅</el-checkbox>
                <el-checkbox v-model="caseData.enable_notify">微信更新通知</el-checkbox>
                <div class="form-tip">开启后，案例更新时会自动推送通知给订阅用户</div>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧预览 -->
      <div class="right-panel">
        <el-card class="preview-card">
          <template #header>
            <div class="preview-header">
              <span>实时预览</span>
              <el-button type="primary" link @click="openPreview">
                <el-icon><View /></el-icon>全屏预览
              </el-button>
            </div>
          </template>

          <div class="preview-content">
            <div class="preview-cover" :style="{ backgroundImage: `url(${caseData.cover_image || '/placeholder-case.jpg'})` }">
              <div class="preview-overlay">
                <h4>{{ caseData.title || '案例标题' }}</h4>
                <p>{{ caseData.location || '小区名称' }} · {{ caseData.area ? caseData.area + '㎡' : '面积' }}</p>
              </div>
            </div>

            <div class="preview-stats">
              <div class="stat-item">
                <div class="stat-value">{{ caseData.view_count || 0 }}</div>
                <div class="stat-label">浏览</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ caseData.like_count || 0 }}</div>
                <div class="stat-label">点赞</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ caseData.subscription_count || 0 }}</div>
                <div class="stat-label">订阅</div>
              </div>
            </div>

            <div class="preview-info">
              <div class="info-row">
                <span class="info-label">户型</span>
                <span class="info-value">{{ caseData.house_type || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">风格</span>
                <span class="info-value">{{ caseData.style || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">总价</span>
                <span class="info-value text-primary">{{ caseData.total_price ? '¥' + formatPrice(caseData.total_price) : '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">套餐</span>
                <span class="info-value">{{ caseData.package_type || '-' }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 时间轴节点弹窗 -->
    <el-dialog v-model="showTimelineDialog" :title="editingTimeline ? '编辑节点' : '添加节点'" width="600px">
      <el-form :model="timelineForm" label-position="top">
        <el-form-item label="时间节点" required>
          <el-date-picker v-model="timelineForm.node_time" type="datetime" style="width: 100%" />
        </el-form-item>
        <el-form-item label="节点标题" required>
          <el-select 
            v-model="timelineForm.title" 
            filterable 
            allow-create
            placeholder="选择或输入节点标题"
            style="width: 100%"
          >
            <el-option 
              v-for="node in workflowNodes" 
              :key="node.id" 
              :label="node.node_name" 
              :value="node.node_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容描述">
          <el-input v-model="timelineForm.content" type="textarea" :rows="4" placeholder="描述该节点的内容..." />
        </el-form-item>
        <el-form-item label="图片/视频">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            list-type="picture-card"
            :file-list="timelineMediaList"
            :on-success="handleTimelineMediaSuccess"
            :on-remove="handleTimelineMediaRemove"
            multiple
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTimelineDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTimelineNode" :loading="savingTimeline">保存</el-button>
      </template>
    </el-dialog>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" title="图片预览" width="70%" append-to-body>
      <img :src="previewUrl" style="width: 100%;" />
    </el-dialog>

    <!-- 图片简介编辑对话框 -->
    <el-dialog v-model="showImageDescDialog" title="编辑图片简介" width="520px">
      <div class="image-desc-editor">
        <div class="desc-preview-img" v-if="editingImageItem">
          <img :src="editingImageItem?.url" alt="预览" />
        </div>
        <el-input
          v-model="editingImageDescription"
          type="textarea"
          :rows="6"
          maxlength="500"
          show-word-limit
          placeholder="为这张图片添加简介（500字以内）...&#10;&#10;有简介的图片会在案例详情页以杂志风格展示，首字放大，底色自动吸取图片主色。"
        />
        <div class="desc-tips" v-if="editingImageDescription">
          <span class="tip-dot"></span> 已填写简介，该图片将在详情页以杂志风格展示
        </div>
      </div>
      <template #footer>
        <el-button @click="showImageDescDialog = false">取消</el-button>
        <el-button type="primary" @click="saveImageDescription">保存简介</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, View, Upload, ArrowRight, Close } from '@element-plus/icons-vue'
import ImageCropperUpload from '@/components/ImageCropperUpload.vue'
import MorandiColorPicker from '@/components/MorandiColorPicker.vue'
import {
  getCase, createCase, updateCase, publishCase,
  getTimeline, addTimeline, updateTimeline, deleteTimeline as deleteTimelineApi,
  getFiles, uploadFile, deleteFile as deleteFileApi,
  initWorkflow, getWorkflowTimeline, updateWorkflowNode,
  authorizeWorkflow, uploadWorkflowPhoto,
  getPinnedCases, getWorkflowNodes
} from '@/api/case'
import { getBuildings } from '@/api/building'
import { getEmployees } from '@/api/employee'

const route = useRoute()
const router = useRouter()

// 状态
const isEdit = computed(() => !!route.params.id)
const caseId = computed(() => route.params.id)
const activeTab = ref('basic')
const saving = ref(false)
const publishing = ref(false)
const publishMode = ref('immediate')

// 数据
const caseData = reactive({
  title: '',
  case_no: '',
  atmosphere: '',
  type: '实景',
  style: '',
  space_type: '',
  building_id: null,
  address: '',
  customer_name: '',
  house_type: '',
  area: null,
  budget_range: '',
  construction_phase: '',
  responsible_id: null,
  tags: [],
  description: '',
  cover_image: '',
  vr_link: '',
  vr_qrcode: '',
  planner_id: null,
  designer_id: null,
  storage_plan: '',
  execution_detail: '',
  design_concept: '',
  whole_house_plan: '',
  customer_requirements: '',
  design_highlights: '',
  customer_value: '',
  total_price: null,
  deal_budget: null,
  package_type: '',
  price_detail: '',
  owner_authorized: false,
  is_public: true,
  is_featured: false,
  is_top: false,
  top_position: null,
  scheduled_time: null,
  sync_xiaohongshu: false,
  sync_mp: false,
  enable_subscription: true,
  enable_notify: true,
  status: '草稿',
  colors: { main: null, auxiliary: null, accent: null, background: null }
})

// 选项数据
const buildingOptions = ref([])
const employeeOptions = ref([])

// 英雄主图列表
const heroImageList = ref([])

// 媒体列表
const mediaList = ref([])
const uploadUrl = '/api/v3/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 标签切换
const toggleTag = (tag) => {
  if (!caseData.tags) caseData.tags = []
  const idx = caseData.tags.indexOf(tag)
  if (idx > -1) {
    caseData.tags.splice(idx, 1)
  } else {
    caseData.tags.push(tag)
  }
}

// 楼盘选择自动填充地址
const handleBuildingChange = (buildingId) => {
  if (buildingId) {
    const building = buildingOptions.value.find(b => b.id === buildingId)
    if (building) {
      caseData.address = building.address || `${building.province || ''}${building.city || ''}${building.district || ''}${building.name || ''}`
    }
  } else {
    caseData.address = ''
  }
}

// 造价明细
const priceDetailList = ref([
  { item: '基础装修', desc: '水电、泥木、油漆等基础工程', amount: 0 },
  { item: '定制家具', desc: '橱柜、衣柜、鞋柜等定制产品', amount: 0 },
  { item: '活动家具', desc: '沙发、床、餐桌等活动家具', amount: 0 },
  { item: '软装配饰', desc: '窗帘、灯具、装饰品等', amount: 0 }
])

// 时间轴
const timelineList = ref([])
const showTimelineDialog = ref(false)
const editingTimeline = ref(null)
const savingTimeline = ref(false)
const workflowNodes = ref([])  // 流程节点模板列表
const timelineForm = reactive({
  node_time: null,
  title: '',
  content: '',
  media_urls: ''
})
const timelineMediaList = ref([])

// 文件列表
const fileList = ref([])

// ===== 服务流程 Workflow =====
const workflowInitialized = ref(false)
const workflowLoading = ref(false)
const workflowTimeline = ref([])
const workflowData = reactive({
  is_real_case: false,
  enable_public_workflow: false
})

const PHASE_MAP = {
  acquisition: { label: '获客阶段', icon: '🎯', key: 'acquisition' },
  conversion: { label: '转化阶段', icon: '🤝', key: 'conversion' },
  preparation: { label: '准备阶段', icon: '📋', key: 'preparation' },
  construction: { label: '施工阶段', icon: '🔨', key: 'construction' },
  follow_up: { label: '售后阶段', icon: '🛡', key: 'follow_up' }
}

const phaseGroups = computed(() => {
  const groups = {}
  for (const node of workflowTimeline.value) {
    if (!groups[node.phase]) groups[node.phase] = []
    groups[node.phase].push(node)
  }
  // Ordered by phase_order
  return Object.keys(PHASE_MAP)
    .filter(key => groups[key])
    .map(key => ({
      ...PHASE_MAP[key],
      nodes: groups[key] || []
    }))
})

const workflowProgress = computed(() => {
  if (!workflowTimeline.value.length) return 0
  const done = workflowTimeline.value.filter(n => n.status === 'completed').length
  return Math.round(done / workflowTimeline.value.length * 100)
})

const nodeStatusType = (status) => {
  return { pending: 'info', ongoing: 'warning', completed: 'success' }[status] || 'info'
}

const nodeStatusLabel = (status) => {
  return { pending: '计划中', ongoing: '进行中', completed: '已完成' }[status] || status
}

const addImagePrefix = (url) => {
  if (!url) return ''
  return url.startsWith('/') ? `/api/v3${url}` : url
}

const fetchWorkflowTimeline = async () => {
  if (!isEdit.value) return
  try {
    const res = await getWorkflowTimeline(caseId.value)
    workflowTimeline.value = res.timeline || []
    workflowData.is_real_case = res.is_real_case || false
    workflowData.enable_public_workflow = res.enable_public_workflow || false
    workflowInitialized.value = workflowTimeline.value.length > 0
  } catch (e) {
    console.error('获取服务流程失败:', e)
    workflowInitialized.value = false
  }
}

const handleInitWorkflow = async () => {
  workflowLoading.value = true
  try {
    const res = await initWorkflow(caseId.value)
    ElMessage.success(`已初始化 ${res.total_nodes || 0} 个流程节点`)
    await fetchWorkflowTimeline()
  } catch (e) {
    console.error('初始化失败:', e)
    ElMessage.error(e?.message || '初始化服务流程失败')
  } finally {
    workflowLoading.value = false
  }
}

const handleTogglePublicWorkflow = async (val) => {
  try {
    await authorizeWorkflow(caseId.value, { enable_public_workflow: val })
    ElMessage.success(val ? '已公开展示服务流程' : '已隐藏服务流程')
  } catch (e) {
    ElMessage.error('更新授权状态失败')
    workflowData.enable_public_workflow = !val
  }
}

const handleNodeCommand = async (cmd, node) => {
  if (cmd === 'pending' || cmd === 'ongoing' || cmd === 'completed') {
    try {
      await updateWorkflowNode(caseId.value, { timeline_id: node.id, status: cmd })
      node.status = cmd
      if (cmd === 'ongoing' && !node.start_time) node.start_time = new Date().toISOString()
      if (cmd === 'completed' && !node.end_time) node.end_time = new Date().toISOString()
      ElMessage.success('状态已更新')
    } catch (e) {
      ElMessage.error('更新状态失败')
    }
  } else if (cmd === 'upload_photo' || cmd === 'upload_rendering') {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = async () => {
      const file = input.files[0]
      if (!file) return
      const fd = new FormData()
      fd.append('file', file)
      fd.append('timeline_id', node.id)
      fd.append('type', cmd === 'upload_rendering' ? 'rendering' : 'photo')
      try {
        const res = await uploadWorkflowPhoto(caseId.value, fd)
        if (cmd === 'upload_rendering') {
          node.renderings = res.renderings || []
        } else {
          node.photos = res.photos || []
        }
        ElMessage.success('上传成功')
      } catch (e) {
        ElMessage.error('上传失败')
      }
    }
    input.click()
  } else if (cmd === 'edit_notes') {
    try {
      const { value } = await ElMessageBox.prompt('请输入备注内容', '编辑备注', {
        inputValue: node.notes || '',
        inputType: 'textarea'
      })
      await updateWorkflowNode(caseId.value, { timeline_id: node.id, notes: value })
      node.notes = value
      ElMessage.success('备注已更新')
    } catch {
      // cancelled
    }
  } else if (cmd === 'toggle_public') {
    try {
      await updateWorkflowNode(caseId.value, { timeline_id: node.id, is_public: !node.is_public })
      node.is_public = !node.is_public
      ElMessage.success(node.is_public ? '节点已公开' : '节点已隐藏')
    } catch (e) {
      ElMessage.error('更新失败')
    }
  }
}

// 获取案例详情
const fetchCaseDetail = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await getCase(caseId.value)
    const data = res
    
    // 填充数据
    Object.keys(caseData).forEach(key => {
      if (data[key] !== undefined) {
        caseData[key] = data[key]
      }
    })
    
    // 解析英雄主图
    if (data.hero_images) {
      try {
        const images = typeof data.hero_images === 'string' ? JSON.parse(data.hero_images) : data.hero_images
        heroImageList.value = images.map((url, i) => ({
          name: `hero_${i + 1}`,
          url: url.startsWith('/') ? `/api/v3${url}` : url,
          uid: Date.now() + i,
          description: ''
        }))
      } catch {
        heroImageList.value = []
      }
    }
    
    // 解析媒体列表（添加前缀）
    if (data.media) {
      mediaList.value = data.media.map((m, i) => ({
        name: m.description || `image_${i + 1}`,
        url: (m.url || '').startsWith('/') && !m.url.startsWith('/api') ? `/api/v3${m.url}` : m.url,
        uid: m.id || Date.now() + i,
        description: m.description || ''
      }))
    }
    
    // 解析配色方案
    caseData.colors = {
      main: data.main_colors ? (typeof data.main_colors === 'string' ? JSON.parse(data.main_colors) : data.main_colors) : null,
      auxiliary: data.auxiliary_colors ? (typeof data.auxiliary_colors === 'string' ? JSON.parse(data.auxiliary_colors) : data.auxiliary_colors) : null,
      accent: data.accent_colors ? (typeof data.accent_colors === 'string' ? JSON.parse(data.accent_colors) : data.accent_colors) : null,
      background: data.background_colors ? (typeof data.background_colors === 'string' ? JSON.parse(data.background_colors) : data.background_colors) : null
    }

    // 解析造价明细
    if (data.price_detail) {
      try {
        priceDetailList.value = JSON.parse(data.price_detail)
      } catch {
        // 解析失败使用默认
      }
    }
  } catch (error) {
    console.error('获取案例详情失败:', error)
    ElMessage.error('获取案例详情失败')
  }
}

// 获取时间轴
const fetchTimeline = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await getTimeline(caseId.value)
    timelineList.value = res || []
  } catch (error) {
    console.error('获取时间轴失败:', error)
  }
}

// 获取文件列表
const fetchFiles = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await getFiles(caseId.value)
    fileList.value = res || []
  } catch (error) {
    console.error('获取文件失败:', error)
  }
}

// 获取选项
const fetchOptions = async () => {
  try {
    const [buildings, employees] = await Promise.all([
      getBuildings({ page_size: 100 }),
      getEmployees({ page_size: 100 })
    ])
    // 拦截器已解包 res.data，所以直接用 .items
    buildingOptions.value = buildings.items || buildings || []
    employeeOptions.value = employees.items || employees || []
    console.log('楼盘数据:', buildingOptions.value.length, '条')
    console.log('员工数据:', employeeOptions.value.length, '条')
  } catch (error) {
    console.error('获取选项失败:', error)
  }
}

// 保存草稿
const handleSaveDraft = async () => {
  saving.value = true
  try {
    const data = prepareSubmitData()
    data.status = '草稿'
    
    if (isEdit.value) {
      await updateCase(caseId.value, data)
    } else {
      const res = await createCase(data)
      // 创建成功后跳转到编辑页
      if (res?.id) {
        router.replace(`/admin/cases/edit/${res.id}`)
      }
    }
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 发布
const handlePublish = async () => {
  publishing.value = true
  try {
    const data = prepareSubmitData()
    
    if (isEdit.value) {
      await updateCase(caseId.value, data)
      await publishCase(caseId.value)
    } else {
      const res = await createCase(data)
      if (res?.id) {
        await publishCase(res.id)
        router.replace(`/admin/cases/edit/${res.id}`)
      }
    }
    
    ElMessage.success('发布成功')
    fetchCaseDetail()
  } catch (error) {
    console.error('发布失败:', error)
    ElMessage.error('发布失败')
  } finally {
    publishing.value = false
  }
}

// 准备提交数据
const prepareSubmitData = () => {
  // 剥离 /api/v3 前缀，存储相对路径
  const stripPrefix = (url) => {
    if (!url) return url
    return url.replace(/^\/api\/v3/, '')
  }
  const { colors, ...rest } = caseData
  return {
    ...rest,
    main_colors: colors.main ? JSON.stringify(colors.main) : null,
    auxiliary_colors: colors.auxiliary ? JSON.stringify(colors.auxiliary) : null,
    accent_colors: colors.accent ? JSON.stringify(colors.accent) : null,
    background_colors: colors.background ? JSON.stringify(colors.background) : null,
    hero_images: JSON.stringify(heroImageList.value.map(f => stripPrefix(f.url))),
    media: mediaList.value.map(f => ({
      url: stripPrefix(f.url),
      description: f.description || ''
    })),
    price_detail: JSON.stringify(priceDetailList.value),
    scheduled_time: publishMode.value === 'schedule' ? caseData.scheduled_time : null
  }
}

// 上传相关
const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

const beforePdfUpload = (file) => {
  const isPdf = file.type === 'application/pdf'
  const isLt20M = file.size / 1024 / 1024 < 20
  
  if (!isPdf) {
    ElMessage.error('只能上传 PDF 文件')
    return false
  }
  if (!isLt20M) {
    ElMessage.error('PDF 大小不能超过 20MB')
    return false
  }
  return true
}

const handleCoverSuccess = (res) => {
  // el-upload 的 on-success 不经过 axios 拦截器
  // res 是后端原始响应 {code: 200, data: {file_url: "/upload/xxx"}}
  const data = res.data || res
  const fileUrl = data.file_url || data.url
  if (fileUrl) {
    caseData.cover_image = fileUrl.startsWith('/') ? `/api/v3${fileUrl}` : fileUrl
  }
}

const handleHeroImageSuccess = (res, file) => {
  // el-upload 不走 axios 拦截器，res 是完整响应体 {code:200, data:{file_url:'...'}}
  const data = res.data || res
  const fileUrl = data.file_url || data.url
  if (fileUrl) {
    const fullUrl = fileUrl.startsWith('/') ? `/api/v3${fileUrl}` : fileUrl
    // 追加到 heroImageList
    heroImageList.value.push({
      name: `hero_${heroImageList.value.length + 1}`,
      url: fullUrl,
      uid: Date.now() + Math.random(),
      description: ''
    })
  }
}

const handleHeroImageRemove = (file, fileList) => {
  heroImageList.value = fileList
}

const handleMediaSuccess = (res, file) => {
  // el-upload 不走 axios 拦截器，res 是完整响应体 {code:200, data:{file_url:'...'}}
  const data = res.data || res
  const fileUrl = data.file_url || data.url
  if (fileUrl) {
    const fullUrl = fileUrl.startsWith('/') ? `/api/v3${fileUrl}` : fileUrl
    // 追加到 mediaList
    mediaList.value.push({
      name: `image_${mediaList.value.length + 1}`,
      url: fullUrl,
      uid: Date.now() + Math.random(),
      description: ''
    })
  }
}

const handleMediaRemove = (file, fileList) => {
  mediaList.value = fileList
}

// 图片预览
const previewVisible = ref(false)
const previewUrl = ref('')

// 图片简介编辑
const showImageDescDialog = ref(false)
const editingImageItem = ref(null)
const editingImageDescription = ref('')
const editingImageList = ref(null)
const editingImageIndex = ref(-1)
const editingImageType = ref('') // 'hero' or 'gallery'

// 打开图片简介编辑对话框
const openImageDescDialog = (list, index, type) => {
  editingImageList.value = list
  editingImageIndex.value = index
  editingImageType.value = type
  editingImageItem.value = list[index]
  editingImageDescription.value = list[index].description || ''
  showImageDescDialog.value = true
}

// 保存图片简介
const saveImageDescription = () => {
  if (!editingImageList.value || editingImageIndex.value < 0) return
  const item = editingImageList.value[editingImageIndex.value]
  item.description = editingImageDescription.value
  // 同时更新 name 用于提交时的 description 字段
  item.name = editingImageDescription.value || (editingImageType.value === 'hero' ? `hero_${editingImageIndex.value + 1}` : `image_${editingImageIndex.value + 1}`)
  showImageDescDialog.value = false
  ElMessage.success(editingImageDescription.value ? '简介已保存' : '已清除简介')
}

// 触发隐藏的上传组件
const heroUploadRef = ref(null)
const galleryUploadRef = ref(null)
const triggerHeroUpload = () => { heroUploadRef.value?.$el.querySelector('input')?.click() }
const triggerGalleryUpload = () => { galleryUploadRef.value?.$el.querySelector('input')?.click() }

// 按索引删除英雄图
const handleHeroImageRemoveByIndex = (index) => {
  heroImageList.value.splice(index, 1)
}

// 按索引删除效果图
const handleMediaRemoveByIndex = (index) => {
  mediaList.value.splice(index, 1)
}
const handlePreview = (file) => {
  previewUrl.value = file.url || (file.response?.data?.file_url ? `/api/v3${file.response.data.file_url}` : '')
  previewVisible.value = true
}

const handleFileSuccess = (res) => {
  fetchFiles()
  ElMessage.success('上传成功')
}

// 造价明细
const addPriceItem = () => {
  priceDetailList.value.push({ item: '', desc: '', amount: 0 })
}

const removePriceItem = (index) => {
  priceDetailList.value.splice(index, 1)
}

// 时间轴
const editTimelineNode = (node) => {
  editingTimeline.value = node
  timelineForm.node_time = node.node_time
  timelineForm.title = node.title
  timelineForm.content = node.content
  timelineForm.media_urls = node.media_urls
  
  // 解析媒体列表
  if (node.media_urls) {
    try {
      const urls = JSON.parse(node.media_urls)
      timelineMediaList.value = urls.map(url => ({ name: '图片', url }))
    } catch {
      timelineMediaList.value = []
    }
  }
  
  showTimelineDialog.value = true
}

// 打开添加节点对话框（初始化时间）
const openAddTimelineDialog = async () => {
  editingTimeline.value = null
  // 初始化为当前时间
  timelineForm.node_time = new Date()
  timelineForm.title = ''
  timelineForm.content = ''
  timelineForm.media_urls = ''
  timelineMediaList.value = []
  
  // 获取流程节点列表（如果还没有）
  if (workflowNodes.value.length === 0) {
    try {
      const res = await getWorkflowNodes()
      workflowNodes.value = res.items || []
    } catch (error) {
      console.error('获取节点列表失败:', error)
    }
  }
  
  showTimelineDialog.value = true
}

const saveTimelineNode = async () => {
  savingTimeline.value = true
  try {
    const data = {
      ...timelineForm,
      media_urls: JSON.stringify(timelineMediaList.value.map(f => f.url || f.response?.url))
    }
    
    if (editingTimeline.value) {
      await updateTimeline(editingTimeline.value.id, data)
    } else {
      await addTimeline(caseId.value, data)
    }
    
    ElMessage.success('保存成功')
    showTimelineDialog.value = false
    fetchTimeline()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingTimeline.value = false
  }
}

const deleteTimelineNode = async (node) => {
  try {
    await ElMessageBox.confirm('确定要删除该节点吗？', '确认删除', { type: 'warning' })
    await deleteTimelineApi(node.id)
    ElMessage.success('删除成功')
    fetchTimeline()
  } catch {
    // 取消
  }
}

const handleTimelineMediaSuccess = (res, file) => {
  // 时间轴媒体上传成功
}

const handleTimelineMediaRemove = (file, fileList) => {
  timelineMediaList.value = fileList
}

const parseMediaUrls = (urls) => {
  try {
    return JSON.parse(urls)
  } catch {
    return []
  }
}

// 文件管理
const previewFile = (file) => {
  window.open(file.file_url, '_blank')
}

const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm('确定要删除该文件吗？', '确认删除', { type: 'warning' })
    await deleteFileApi(file.id)
    ElMessage.success('删除成功')
    fetchFiles()
  } catch {
    // 取消
  }
}

// 工具函数
const getStatusType = (status) => {
  const map = { '草稿': 'info', '已发布': 'success', '已下架': 'warning' }
  return map[status] || 'info'
}

const formatPrice = (price) => {
  if (!price) return '0'
  const num = parseFloat(price)
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const goBack = () => {
  router.back()
}

const openPreview = () => {
  window.open(`/cases/${caseId.value}`, '_blank')
}

onMounted(() => {
  fetchOptions()
  fetchCaseDetail()
  fetchTimeline()
  fetchFiles()
  fetchWorkflowTimeline()
})
</script>

<style scoped lang="scss">
.case-edit {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }

    .divider {
      color: #dcdfe6;
    }

    .status-tag {
      margin-left: 8px;
    }
  }

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

.left-panel {
  flex: 1;
  overflow: auto;

  .edit-tabs {
    height: 100%;

    :deep(.el-tabs__content) {
      padding: 24px;
      overflow: auto;
    }
  }

  .edit-form {
    max-width: 900px;
  }
}

.right-panel {
  width: 320px;
  flex-shrink: 0;

  .preview-card {
    height: 100%;

    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .preview-content {
      .preview-cover {
        height: 180px;
        background-size: cover;
        background-position: center;
        border-radius: 8px;
        position: relative;
        margin-bottom: 16px;

        .preview-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          padding: 16px;
          background: linear-gradient(transparent, rgba(0,0,0,0.7));
          color: #fff;
          border-radius: 0 0 8px 8px;

          h4 {
            margin: 0 0 4px 0;
            font-size: 16px;
          }

          p {
            margin: 0;
            font-size: 13px;
            opacity: 0.9;
          }
        }
      }

      .preview-stats {
        display: flex;
        justify-content: space-around;
        padding: 16px 0;
        border-bottom: 1px solid #e4e7ed;
        margin-bottom: 16px;

        .stat-item {
          text-align: center;

          .stat-value {
            font-size: 20px;
            font-weight: 600;
            color: #303133;
          }

          .stat-label {
            font-size: 12px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }

      .preview-info {
        .info-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #f0f0f0;

          &:last-child {
            border-bottom: none;
          }

          .info-label {
            color: #909399;
            font-size: 13px;
          }

          .info-value {
            color: #303133;
            font-size: 13px;

            &.text-primary {
              color: #8B5A2B;
              font-weight: 500;
            }
          }
        }
      }
    }
  }
}

.media-section {
  margin-bottom: 32px;

  h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 500;
  }

  // 图片上传网格（自定义卡片式）
  .image-upload-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;

    .uploaded-image-card {
      width: 160px;
      height: 120px;
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      cursor: pointer;
      border: 2px solid transparent;
      transition: all 0.25s ease;

      &:hover {
        border-color: #8B5A2B;
        box-shadow: 0 4px 16px rgba(139, 90, 43, 0.2);

        .img-card-overlay {
          opacity: 1;
        }
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .img-card-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(transparent 50%, rgba(0,0,0,0.7));
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        padding: 8px;
        opacity: 0;
        transition: opacity 0.25s;

        .img-desc-badge {
          background: rgba(255,255,255,0.9);
          color: #333;
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 10px;
          backdrop-filter: blur(4px);

          &.empty {
            background: #8B5A2B;
            color: #fff;
          }
        }

        .img-delete-btn {
          color: #fff;
          font-size: 16px;
          cursor: pointer;
          padding: 4px;
          border-radius: 50%;
          background: rgba(255,60,60,0.85);

          &:hover {
            background: #ff4444;
          }
        }
      }
    }

    .upload-trigger-card {
      width: 160px;
      height: 120px;
      border: 2px dashed #d0d0d0;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      color: #999;
      transition: all 0.25s;
      gap: 6px;

      &:hover {
        border-color: #8B5A2B;
        color: #8B5A2B;
        background: rgba(139,90,43,0.04);
      }

      .el-icon {
        font-size: 28px;
      }

      span {
        font-size: 12px;
      }
    }
  }

  .cover-uploader {
    :deep(.el-upload) {
      border: 1px dashed #d9d9d9;
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: border-color 0.3s;
      width: 300px;
      height: 200px;

      &:hover {
        border-color: #8B5A2B;
      }
    }

    .cover-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .upload-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #8c939d;

      .el-icon {
        font-size: 28px;
        margin-bottom: 8px;
      }

      .upload-tip {
        font-size: 12px;
        margin-top: 8px;
      }
    }
  }
}

.timeline-section {
  .case-timeline {
    margin-top: 24px;

    .timeline-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .timeline-actions {
        display: flex;
        gap: 8px;
      }
    }

    .timeline-media {
      margin-top: 12px;
    }
  }
}

.files-section {
  h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 500;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* ===== 服务流程 Workflow ===== */
.workflow-section {
  max-width: 900px;
}

.workflow-empty {
  text-align: center;
  padding: 60px 0;
}

.workflow-hint {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
}

.workflow-auth-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;

  .auth-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .node-summary {
      font-size: 13px;
      color: #606266;
    }
  }

  .auth-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
}

.workflow-progress {
  margin-bottom: 24px;
}

.phase-group {
  margin-bottom: 32px;

  .phase-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e4e7ed;

    .phase-icon {
      font-size: 20px;
    }

    .phase-name {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .phase-count {
      font-size: 12px;
      color: #909399;
    }

    .phase-progress {
      font-size: 12px;
      color: #67c23a;
      font-weight: 500;
    }
  }
}

.phase-nodes {
  padding-left: 12px;
}

.workflow-node {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f2f3f5;

  &:last-child {
    border-bottom: none;
  }

  .node-status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-top: 6px;
    flex-shrink: 0;
  }

  &.status-pending .node-status-dot {
    background: #c0c4cc;
  }

  &.status-ongoing .node-status-dot {
    background: #e6a23c;
    box-shadow: 0 0 6px rgba(230, 162, 60, 0.4);
  }

  &.status-completed .node-status-dot {
    background: #67c23a;
  }

  .node-content {
    flex: 1;

    .node-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;

      .node-name {
        font-size: 14px;
        font-weight: 500;
      }
    }

    .node-time {
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;

      span {
        margin-right: 16px;
      }
    }

    .node-notes {
      font-size: 13px;
      color: #606266;
      margin-bottom: 8px;
      padding: 6px 10px;
      background: #f5f7fa;
      border-radius: 4px;
    }

    .node-photos, .node-renderings {
      display: flex;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }

    .rendering-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;
    }

    .node-actions {
      margin-top: 4px;
    }
  }
}

// 图片简介编辑器
.image-desc-editor {
  .desc-preview-img {
    width: 100%;
    height: 180px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 16px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .desc-tips {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 10px 14px;
    background: #f6f1e9;
    border-radius: 8px;
    font-size: 13px;
    color: #8B5A2B;

    .tip-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #8B5A2B;
      flex-shrink: 0;
    }
  }
}
</style>
