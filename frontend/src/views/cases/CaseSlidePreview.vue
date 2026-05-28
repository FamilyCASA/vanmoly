<template>
  <div
    class="slide-viewport"
    ref="viewportRef"
    v-loading="loading"
    @click="handleViewportClick"
    @dblclick="handleDblClick"
    @contextmenu.prevent="showContextMenu"
  >
    <!-- 导航按钮（放在视口层，不随缩放变化） -->
      <div class="slide-nav" @click.stop v-if="!loading && slideData">
        <button class="nav-btn prev" @click="prevSlide" :disabled="currentSlide === 0">
          <span>&#8592;</span>
        </button>
        <span class="slide-counter">{{ currentSlide + 1 }} / {{ totalSlides }}</span>
        <button class="nav-btn next" @click="nextSlide" :disabled="currentSlide === totalSlides - 1">
          <span>&#8594;</span>
        </button>
        <button class="nav-btn fullscreen" @click.stop="toggleFullscreen">&#x26F6;</button>
      </div>

    <!-- 幻灯片舞台（居中容器，支持画幅比例） -->
    <div class="slide-stage" :style="stageStyle" v-if="!loading && slideData">

            <!-- 封面 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('cover') }"
        v-if="slideIndex('cover') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('cover')"></div>
        <div class="slide-content cover-content magazine-cover">
          <div class="cover-left">
            <h1 class="cover-title">{{ slideConfig.cover_title || caseData.title || '案例标题' }}</h1>
            <p class="cover-subtitle">{{ slideConfig.cover_subtitle }}</p>
            <h2 class="cover-case-title">{{ caseData.title }}</h2>

            <p class="cover-atmosphere" v-if="caseData.atmosphere">{{ caseData.atmosphere }}</p>
            <div class="cover-colors-labeled" v-if="colorScheme.length">
              <div v-for="(item, idx) in colorScheme" :key="idx" class="color-label-item">
                <span class="color-dot" :style="{ background: item.color }"></span>
                <span class="color-name">{{ item.label }}</span>
              </div>
            </div>
          </div>
          <div class="cover-right">
            <div class="brand-name">{{ slideConfig.brand_name || 'DESIGNARY' }}</div>
            <div class="cover-style" v-if="caseData.style">
              <span class="style-tag">{{ caseData.style }}</span>
            </div>
            <div class="cover-scene-tags" v-if="caseData.scene_tags && caseData.scene_tags.length">
              <span class="scene-tag-item" v-for="(tag, idx) in caseData.scene_tags" :key="idx">{{ tag }}</span>
            </div>
            <div class="cover-meta-grid">
              <div class="meta-item" v-if="caseData.customer_name">
                <span class="meta-label">客户</span>
                <span class="meta-value">{{ caseData.customer_name }}</span>
              </div>
              <div class="meta-item" v-if="caseData.building_name">
                <span class="meta-label">楼盘</span>
                <span class="meta-value">{{ caseData.building_name }}</span>
              </div>
              <div class="meta-item" v-if="caseData.address">
                <span class="meta-label">地址</span>
                <span class="meta-value">{{ caseData.address }}</span>
              </div>
              <div class="meta-item" v-if="caseData.space_type">
                <span class="meta-label">户型</span>
                <span class="meta-value">{{ caseData.space_type }}</span>
              </div>
              <div class="meta-item" v-if="caseData.area">
                <span class="meta-label">面积</span>
                <span class="meta-value">{{ caseData.area }}m&sup2;</span>
              </div>
            </div>
          </div>
        </div>
      </div>

<!-- 关于我们 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('about') }"
        v-if="slideConfig.show_about && slideIndex('about') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('about')"></div>
        <div class="slide-content about-content">
          <div class="about-card">
<h2 class="about-title" v-html="aboutTitleWithRedEnglish"></h2>
            <p class="about-subtitle">{{ slideConfig.about_subtitle }}</p>
            <p class="about-text" v-html="aboutContentWithFirstWord"></p>
          </div>

        </div>
      </div>

      <!-- 团队介绍 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('team') }"
        v-if="slideConfig.show_team && slideIndex('team') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('team')"></div>
        <div class="slide-content team-content">
          <p class="team-label">SERVICE TEAM</p>
          <h2 class="team-title">服务团队</h2>
          <div class="team-cards">
            <div class="team-member-card" v-for="m in serviceTeam" :key="m?.id || m?.role">
              <div class="team-avatar-wrap">
                <img v-if="m?.showcase_photo" :src="m.showcase_photo" :alt="m.name" class="team-avatar-img" />
                <div v-else class="team-avatar-placeholder">{{ m?.name?.charAt(0) || '?' }}</div>
              </div>
              <div class="team-member-info">
                <span class="team-role-tag">{{ m.role }}</span>
                <h3 class="team-member-name">{{ m.name || '待指定' }}</h3>
                <p class="team-member-bio" v-if="m.bio">{{ m.bio }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 目录 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('toc') }"
        v-if="slideConfig.show_toc && slideIndex('toc') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('toc')"></div>
        <div class="slide-content toc-content">
          <p class="toc-label">CONTENTS</p>
          <h2 class="toc-title">目录</h2>
          <div class="toc-grid" :style="{ gridTemplateColumns: 'repeat(' + tocColumns + ', 1fr)' }">
            <div class="toc-card" v-for="(item, idx) in tocItems" :key="item.key" @click.stop="jumpToSlide(item.key)">
              <span class="toc-card-num">{{ String(idx + 1).padStart(2, '0') }}</span>
              <span class="toc-card-name">{{ item.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 户型分析（阶段1） -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('layout') }"
        v-if="phase1 && (phase1.layout_images?.length || phase1.layout_analysis) && slideIndex('layout') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('layout')"></div>
        <div class="layout-card">
          <div class="layout-text" v-if="phase1.layout_analysis">
            <h2 class="layout-title">户型分析</h2>
            <div class="layout-body" v-html="phase1.layout_analysis"></div>
          </div>
          <div class="layout-images" v-if="phase1.layout_images?.length">
            <div class="layout-img-item" v-for="(img, idx) in phase1.layout_images" :key="idx">
              <img :src="img.url" alt="户型分析" />
            </div>
          </div>
        </div>
      </div>

      <!-- 设计意境（阶段2） -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('mood') }"
        v-if="phase2 && (phase2.mood_images?.length || phase2.mood_text) && slideIndex('mood') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('mood')"></div>
        <div class="mood-card">
          <div class="mood-images" v-if="phase2.mood_images?.length">
            <div class="mood-img-item" v-for="(img, idx) in phase2.mood_images" :key="idx">
              <img :src="img.url" alt="设计意境" />
            </div>
          </div>
          <div class="mood-text" v-if="phase2.mood_text">
            <h2 class="mood-title">设计意境</h2>
            <div class="mood-body" v-html="phase2.mood_text"></div>
          </div>
        </div>
      </div>

      <!-- 平面规划（阶段3） -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('plan') }"
        v-if="phase3 && (phase3.plan_image || phase3.plan_text) && slideIndex('plan') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('plan')"></div>
        <div class="mood-card">
          <div class="mood-images" v-if="phase3.plan_image">
            <div class="mood-img-item">
              <img :src="phase3.plan_image" alt="平面规划" />
            </div>
          </div>
          <div class="mood-text" v-if="phase3.plan_text">
            <h2 class="mood-title">平面规划</h2>
            <div class="mood-body" v-html="phase3.plan_text"></div>
          </div>
        </div>
      </div>

      <!-- 鸟瞰展示（阶段4） -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('birdview') }"
        v-if="phase4 && phase4.birdview_images?.length && slideIndex('birdview') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('birdview')"></div>
        <h2 class="birdview-title">鸟瞰展示</h2>
        <div class="birdview-grid">
          <div class="birdview-img" v-for="(img, idx) in phase4.birdview_images" :key="idx">
            <img :src="img.url" alt="鸟瞰展示" />
          </div>
        </div>
      </div>

      <!-- 效果图展示首页（阶段5） -->
      <div
        class="slide showcase-slide"
        :class="{ active: currentSlide === slideIndex('showcase') }"
        v-if="phase5 && (phase5.showcase_images?.length || phase5.showcase_title1) && slideIndex('showcase') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('showcase')"></div>
        <div class="showcase-cover">
          <h2 class="showcase-cover-title">{{ phase5.showcase_title1 || '效果图展示' }}</h2>
          <p class="showcase-cover-subtitle" v-if="phase5?.showcase_title2">{{ phase5.showcase_title2 }}</p>
          <div class="showcase-cover-gallery" v-if="phase5.showcase_images?.length">
            <div class="showcase-cover-img" v-for="(img, imgIdx) in phase5.showcase_images" :key="imgIdx">
              <img :src="typeof img === 'string' ? img : img.url" alt="效果图" />
            </div>
          </div>
          <div class="showcase-cover-text" v-if="phase5.showcase_text_cn || phase5.showcase_text_en">
            <p class="showcase-cover-cn" v-if="phase5.showcase_text_cn" v-html="phase5.showcase_text_cn"></p>
            <p class="showcase-cover-en" v-if="phase5.showcase_text_en" v-html="phase5.showcase_text_en"></p>
          </div>
        </div>
      </div>



<!-- 空间效果图展示（智能分页） -->
      <template v-for="space in visibleSpaces" :key="'space_' + space.id">
        <!-- 空间标题页 -->
        <div
          v-if="slideIndex('space_title_' + space.id) >= 0"
          class="slide space-title-slide"
          :class="{ active: currentSlide === slideIndex('space_title_' + space.id) }"
          @click.stop="handleSlideClick"
        >
          <div class="slide-bg-img" :style="slideBgStyle('space_' + space.id)"></div>
          <div class="showcase-cover">
            <h2 class="showcase-cover-title">{{ space.space_name }}</h2>
          </div>
        </div>
        <!-- 空间效果图分页 -->
        <template v-for="(page, pIdx) in getSpaceGroupedPages(space)" :key="'sp_' + space.id + '_p' + pIdx">
          <div
            v-if="slideIndex('space_page_' + space.id + '_' + pIdx) >= 0"
            class="slide space-rendering-slide"
            :class="{ active: currentSlide === slideIndex('space_page_' + space.id + '_' + pIdx) }"
            @click.stop="handleSlideClick"
          >
            <div class="slide-bg-img" :style="slideBgStyle('space_' + space.id)"></div>
            <div class="showcase-page" :class="['showcase-page--' + page.type]">
              <!-- 文案在左侧 -->
              <template v-if="page.hasText && page.textSide === 'left'">
                <div class="showcase-page-text showcase-page-text--left">
                  <p class="showcase-page-cn" v-if="page.textCn" v-html="page.textCn"></p>
                  <p class="showcase-page-en" v-if="page.textEn" v-html="page.textEn"></p>
                </div>
              </template>
              <!-- 图片区域 -->
              <div class="showcase-page-images" :class="'showcase-page-images--' + page.type">
                <div class="showcase-page-img" v-for="(img, imgIdx) in page.images" :key="imgIdx">
                  <img :src="img.url" alt="效果图" />
                </div>
              </div>
              <!-- 文案在右侧 -->
              <template v-if="page.hasText && page.textSide === 'right'">
                <div class="showcase-page-text showcase-page-text--right">
                  <p class="showcase-page-cn" v-if="page.textCn" v-html="page.textCn"></p>
                  <p class="showcase-page-en" v-if="page.textEn" v-html="page.textEn"></p>
                </div>
              </template>
            </div>
          </div>
        </template>

        <!-- 空间物料配置页 -->
        <template v-for="(matPage, mIdx) in getSpaceMaterialPages(space.id)" :key="'smat_' + space.id + '_m' + mIdx">
          <div
            v-if="slideIndex('space_mat_' + space.id + '_' + mIdx) >= 0"
            class="slide space-material-slide"
            :class="{ active: currentSlide === slideIndex('space_mat_' + space.id + '_' + mIdx) }"
            @click.stop="handleSlideClick"
          >
            <div class="slide-bg-img" :style="slideBgStyle('space_' + space.id)"></div>
            <div class="slide-content space-material-content">
              <h2 class="slide-heading smat-heading">{{ space.space_name }} · 物料配置</h2>
              <table class="smat-table">
                <thead>
                  <tr>
                    <th class="smat-th-idx">#</th>
                    <th class="smat-th-custom">商品名称</th>
                    <th class="smat-th-name">物料名称</th>
                    <th class="smat-th-dim">尺寸</th>
                    <th class="smat-th-measure">计量</th>
                    <th class="smat-th-num">数量</th>
                    <th class="smat-th-price">单价</th>
                    <th class="smat-th-total">金额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(item, iIdx) in matPage"
                    :key="item.id || iIdx"
                    class="smat-row"
                    @click.stop="openMaterialDetail(item)"
                  >
                    <td class="smat-idx">{{ iIdx + 1 }}</td>
                    <td class="smat-custom">{{ item.custom_name || item.material_name || '' }}</td>
                    <td class="smat-name">{{ item.sku_name || item.material_name || '' }}</td>
                    <td class="smat-dim">{{ [item.width, item.depth, item.height].filter(Boolean).length ? [item.width, item.depth, item.height].filter(Boolean).join('×') : '' }}</td>
                    <td class="smat-measure">{{ item.custom_measure ? item.custom_measure + (item.unit || '') : '' }}</td>
                    <td class="smat-num">{{ item.quantity }}</td>
                    <td class="smat-num">¥{{ item.unit_price }}</td>
                    <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                  </tr>
                </tbody>
                <tfoot v-if="mIdx === getSpaceMaterialPages(space.id).length - 1">
                  <tr>
                    <td colspan="6"></td>
                    <td class="smat-foot-label">空间小计</td>
                    <td class="smat-price smat-total">¥{{ (spaceMaterialsMap[space.id] || []).reduce((s,m) => s + (parseFloat(m.total_price)||0), 0).toFixed(2) }}</td>
                  </tr>
                </tfoot>
              </table>
              <div class="smat-page-info" v-if="getSpaceMaterialPages(space.id).length > 1">
                {{ mIdx + 1 }} / {{ getSpaceMaterialPages(space.id).length }}
              </div>
            </div>
          </div>
        </template>
      </template>

      <!-- 分类物料配置页（无空间配置时按分类展示物料库数据） -->
      <template v-if="!hasSpaceMaterials && rawMaterials.length > 0">
        <template v-for="cat in categoryMaterialsMap.order" :key="'catmat_' + cat">
          <template v-for="(catPage, cpIdx) in getCategoryMaterialPages(cat)" :key="'catmat_' + cat + '_' + cpIdx">
            <div
              v-if="slideIndex('cat_mat_' + cat + '_' + cpIdx) >= 0"
              class="slide space-material-slide"
              :class="{ active: currentSlide === slideIndex('cat_mat_' + cat + '_' + cpIdx) }"
              @click.stop="handleSlideClick"
            >
              <div class="slide-bg-img" :style="slideBgStyle('space_1')"></div>
              <div class="slide-content space-material-content">
                <h2 class="slide-heading smat-heading">{{ cat }} · 物料配置</h2>
                <table class="smat-table">
                  <thead>
                    <tr>
                      <th class="smat-th-idx">#</th>
                      <th class="smat-th-custom">商品名称</th>
                      <th class="smat-th-name">物料名称</th>
                      <th class="smat-th-dim">尺寸</th>
                      <th class="smat-th-measure">计量</th>
                      <th class="smat-th-num">数量</th>
                      <th class="smat-th-price">单价</th>
                      <th class="smat-th-total">金额</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(item, iIdx) in catPage"
                      :key="item.id || iIdx"
                      class="smat-row"
                      @click.stop="openMaterialDetail(item)"
                    >
                      <td class="smat-idx">{{ iIdx + 1 }}</td>
                      <td class="smat-custom">{{ item.custom_name || item.material_name || '' }}</td>
                      <td class="smat-name">{{ item.sku_name || item.material_name || '' }}</td>
                      <td class="smat-dim">{{ [item.width, item.depth, item.height].filter(Boolean).length ? [item.width, item.depth, item.height].filter(Boolean).join('×') : '' }}</td>
                      <td class="smat-measure">{{ item.custom_measure ? item.custom_measure + (item.unit || '') : '' }}</td>
                      <td class="smat-num">{{ item.quantity }}</td>
                      <td class="smat-num">¥{{ item.unit_price }}</td>
                      <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                    </tr>
                  </tbody>
                </table>
                <div class="smat-page-info" v-if="getCategoryMaterialPages(cat).length > 1">
                  {{ cpIdx + 1 }} / {{ getCategoryMaterialPages(cat).length }}
                </div>
              </div>
            </div>
          </template>
        </template>
      </template>

      <!-- 物料详情弹窗 -->
      <el-dialog
        v-model="materialDetailVisible"
        :title="materialDetailItem?.custom_name || materialDetailItem?.material_name || '物料详情'"
        width="680px"
        top="5vh"
        destroy-on-close
        append-to-body
        class="material-detail-dialog"
      >
        <div class="md-layout" v-if="materialDetailItem">
          <div class="md-image-area">
            <img
              v-if="materialDetailItem.material_image"
              :src="materialDetailItem.material_image"
              :alt="materialDetailItem.material_name"
              class="md-main-img"
            />
            <div v-else class="md-no-img">
              <span>暂无图片</span>
            </div>
          </div>
          <div class="md-info-area">
            <h3 class="md-title">{{ materialDetailItem.custom_name || materialDetailItem.material_name || '-' }}</h3>
            <div class="md-divider"></div>
            <div class="md-props">
              <div class="md-prop">
                <span class="md-prop-label">型号</span>
                <span class="md-prop-value">{{ materialDetailItem.sku_code || '-' }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">规格</span>
                <span class="md-prop-value">{{ materialDetailItem.spec || '-' }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">品牌</span>
                <span class="md-prop-value">{{ materialDetailItem.brand || '-' }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">材料</span>
                <span class="md-prop-value">{{ [materialDetailItem.category_level1, materialDetailItem.category_level2, materialDetailItem.category_level3].filter(Boolean).join(' · ') || '-' }}</span>
              </div>
              <div class="md-prop" v-if="materialDetailItem.material">
                <span class="md-prop-label">材质</span>
                <span class="md-prop-value">{{ materialDetailItem.material }}</span>
              </div>
              <div class="md-prop" v-if="materialDetailItem.color_name">
                <span class="md-prop-label">花色</span>
                <span class="md-prop-value">{{ materialDetailItem.color_name }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">环保</span>
                <span class="md-prop-value">{{ materialDetailItem.env_level || '合格' }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">采购渠道</span>
                <span class="md-prop-value">{{ materialDetailItem.supply_chain || '直供' }}</span>
              </div>
              <div class="md-prop">
                <span class="md-prop-label">参考价格</span>
                <span class="md-prop-value md-price">¥{{ materialDetailItem.unit_price || 0 }} / {{ materialDetailItem.unit || '件' }}</span>
              </div>
            </div>
          </div>
        </div>
        <template #footer>
          <el-button @click="materialDetailVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      

      <!-- 材质展示 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('material') }"
        v-if="slideConfig.show_material && showcaseMaterials?.length && slideIndex('material') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('material')"></div>
        <div class="slide-content material-content">
          <h2 class="slide-heading">材质解析</h2>
          <div class="material-showcase-grid">
            <div class="showcase-card" v-for="(mat, idx) in showcaseMaterials" :key="idx">
              <div class="showcase-card-img">
                <img :src="mat.main_image" :alt="mat.sku_name" />
              </div>
              <div class="showcase-card-info">
                <div class="showcase-card-l1" v-if="mat.l1">{{ mat.l1 }}</div>
                <div class="showcase-card-name">{{ mat.sku_name }}</div>
                <div class="showcase-card-spec" v-if="mat.spec">{{ mat.spec }}</div>
                <div class="showcase-card-brand" v-if="mat.brand">{{ mat.brand }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 物料展示 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('product') }"
        v-if="slideConfig.show_product && (phase8?.product_gallery?.length || phase8?.product_list?.length) && slideIndex('product') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('product')"></div>
        <div class="slide-content product-content">
          <h2 class="slide-heading">物料清单</h2>
          <div class="product-gallery">
            <div class="product-item" v-for="(img, idx) in phase8" :key="idx">
              <img :src="img.url" alt="物料" />
            </div>
          </div>
          <div class="product-table" v-if="phase8?.product_list?.length">
            <table>
              <thead>
                <tr><th>物料</th><th>品牌</th><th>分类</th><th>数量</th><th>单价</th><th>小计</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in phase8.product_list" :key="item.sku_code || item.material_name">
                  <td>{{ item.material_name }}</td>
                  <td>{{ item.brand || '-' }}</td>
                  <td>{{ item.category || '-' }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>¥{{ item.unit_price }}</td>
                  <td class="price">¥{{ ((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 工法展示 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('process') }"
        v-if="slideConfig.show_process && phase9?.process_gallery?.length && slideIndex('process') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('process')"></div>
        <div class="slide-content process-content">
          <h2 class="slide-heading">工法解析</h2>
          <div class="process-gallery">
            <div class="process-item" v-for="(img, idx) in phase9.process_gallery" :key="idx">
              <img :src="img.url" alt="工法" />
            </div>
          </div>
          <div class="process-text" v-if="phase9.process_desc" v-html="phase9.process_desc"></div>
        </div>
      </div>

      <!-- 物料汇总 -->
      <div
        class="slide"
        :class="{ active: currentSlide === slideIndex('summary') }"
        v-if="slideConfig.show_summary && materialSummary?.length && slideIndex('summary') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('summary')"></div>
        <div class="slide-content summary-content">
          <h2 class="slide-heading smat-heading">物料汇总</h2>
          <div class="summary-cards">
            <div class="summary-card" v-for="group in materialSummary" :key="group.category">
              <div class="summary-cat">{{ group.category }}</div>
              <div class="summary-stats">
                <span class="summary-measure" v-if="group.measure_total">{{ group.measure_total.toFixed(2) }}{{ group.measure_unit || '㎡' }}</span>
                <span class="summary-total">合计 ¥{{ group.total.toFixed(2) }}</span>
              </div>
            </div>
          </div>
          <div class="summary-grand-total">
            <span>总计</span>
            <span class="grand-amount">¥{{ materialSummary.reduce((s, g) => s + (parseFloat(g.total)||0), 0).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- 封底 -->
      <div
        class="slide slide-back"
        :class="{ active: currentSlide === slideIndex('back') }"
        v-if="slideIndex('back') >= 0"
        @click.stop="handleSlideClick"
      >
        <div class="slide-bg-img" :style="slideBgStyle('back')"></div>
        <div class="slide-content back-content">
          <h2 class="back-title">感谢观看</h2>
          <p class="back-subtitle">D&B 帝标 · 设记家</p>
        </div>
      </div>
    </div>

    <!-- 键盘提示 -->
    <div class="keyboard-hint" v-if="!loading && slideData">
      ← → 切换 | 双击全屏 | 右键菜单 | 点击翻页
    </div>

    <!-- 右键菜单 -->
    <transition name="ctx-fade">
      <div
        v-if="ctxMenu.visible"
        class="slide-ctx-mask"
        @click="hideContextMenu"
      ></div>
    </transition>
    <transition name="ctx-pop">
      <div
        v-if="ctxMenu.visible"
        class="slide-ctx-menu"
        :style="{ left: ctxMenu.x + 'px', top: ctxMenu.y + 'px' }"
      >
        <div class="ctx-header">跳转至幻灯片</div>
        <div
          v-for="(page, idx) in slidePages"
          :key="page.key"
          class="ctx-item"
          :class="{ active: currentSlide === idx }"
          @click.stop="jumpToSlide(page.key); hideContextMenu();"
        >
          <span class="ctx-idx">{{ idx + 1 }}</span>
          <span class="ctx-name">{{ page.name }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const caseId = computed(() => parseInt(route.params.id))

const loading = ref(true)
const slideData = ref(null)
const caseData = reactive({})
const slideConfig = reactive({
  template_style: 'dark',
  primary_color: '#0365C0',
  aspect_ratio: '16:9',
  cover_title: '',
  cover_subtitle: '',
  cover_bg_image: '',
  inner_bg_image: '',
  back_bg_image: '',
  about_title: '',
  about_subtitle: '',
  about_content: '',
  about_image: '',
  show_about: true,
  show_team: true,
  show_toc: true,
  show_material: true,
  show_product: true,
  show_process: true,
  show_summary: true
})

const phases = ref({})
const spaces = ref([])
const materialSummary = ref([])
const rawMaterials = ref([])  // 原始物料列表（未聚合）
const showcaseMaterials = ref([])  // 材质展示选中物料

// 按空间分组的物料（用于幻灯片每空间后的物料页）
const spaceMaterialsMap = computed(() => {
  const map = {}
  rawMaterials.value.forEach(m => {
    const sid = m.space_id
    if (sid) {
      if (!map[sid]) map[sid] = []
      map[sid].push(m)
    }
  })
  return map
})

// 是否有空间级物料配置（space_id 不为空）
const hasSpaceMaterials = computed(() => rawMaterials.value.some(m => m.space_id))

// 按二级分类分组的物料（当无空间配置时，从物料库按分类展示）
const categoryMaterialsMap = computed(() => {
  const map = {}  // key: category_level2, value: material[]
  const order = []  // 保持分类出现顺序
  rawMaterials.value.forEach(m => {
    if (!m.space_id) {
      const cat = m.category_level2 || '未分类'
      if (!map[cat]) { map[cat] = []; order.push(cat) }
      map[cat].push(m)
    }
  })
  return { map, order }
})

// 获取某分类的物料分页
const getCategoryMaterialPages = (category) => {
  const items = categoryMaterialsMap.value.map[category] || []
  if (!items.length) return []
  const pageSize = 6
  const pages = []
  for (let i = 0; i < items.length; i += pageSize) {
    pages.push(items.slice(i, i + pageSize))
  }
  return pages
}

// 获取某空间的物料分页（每页最多15行）
const getSpaceMaterialPages = (spaceId) => {
  const items = spaceMaterialsMap.value[spaceId] || []
  if (!items.length) return []
  const pageSize = 6
  const pages = []
  for (let i = 0; i < items.length; i += pageSize) {
    pages.push(items.slice(i, i + pageSize))
  }
  return pages
}

// 物料详情弹窗
const materialDetailVisible = ref(false)
const materialDetailItem = ref(null)
const openMaterialDetail = (item) => {
  materialDetailItem.value = item
  materialDetailVisible.value = true
}
const pageAbout = ref({ title: '', content: '', highlights: [] })
const teamMembers = ref([])

const phase1 = computed(() => phases.value[1])
const phase2 = computed(() => phases.value[2])
const phase3 = computed(() => phases.value[3])
const phase4 = computed(() => phases.value[4])
const phase5 = computed(() => phases.value[5])

// 效果图分页逻辑：横版独占一页，竖版多张拼一页，横+竖可混排
const showcasePages = computed(() => {
  const images = phase5.value?.showcase_images || []
  const textCn = phase5.value?.showcase_text_cn || ''
  const textEn = phase5.value?.showcase_text_en || ''
  if (!images.length) return []

  // 判断图片方向（宽>高=横版，否则竖版）
  // 因为没有实际尺寸，用url中的线索或默认横版
  // 我们给每个image标记isWide（默认true，实际需要图片加载后判断）
  // 简化方案：先全部标记，分页时假设都未知，需要前端加载图片后才能判断
  // 更实际的方案：使用img.naturalWidth/naturalHeight，但这是异步的
  // 最终方案：用 Image() 预加载获取尺寸（在onMounted中处理）
  // 为了分页，我们用已缓存的图片尺寸
  return images.map((img, idx) => ({
    ...img,
    _idx: idx,
    _orientation: img._orientation || 'landscape' // 默认横版，异步更新
  }))
})

// 图片尺寸缓存
const imgOrientationCache = ref({}) // { url: 'landscape'|'portrait' }

// 预加载效果图获取尺寸
const preloadShowcaseImages = async () => {
  const images = phase5.value?.showcase_images || []
  for (const img of images) {
    if (!img.url || imgOrientationCache.value[img.url]) continue
    try {
      const orient = await new Promise((resolve) => {
        const i = new Image()
        i.onload = () => {
          resolve(i.naturalWidth >= i.naturalHeight ? 'landscape' : 'portrait')
        }
        i.onerror = () => resolve('landscape') // 加载失败默认横版
        i.src = img.url
      })
      imgOrientationCache.value[img.url] = orient
    } catch {
      imgOrientationCache.value[img.url] = 'landscape'
    }
  }
}

// 根据方向分页效果图
const showcaseGroupedPages = computed(() => {
  const images = phase5.value?.showcase_images || []
  const textCn = phase5.value?.showcase_text_cn || ''
  const textEn = phase5.value?.showcase_text_en || ''
  if (!images.length) return []

  const oriented = images.map((img, idx) => ({
    ...img,
    _idx: idx,
    _orientation: imgOrientationCache.value[img.url] || 'landscape',
    _hasText: !!(textCn || textEn)
  }))

  const pages = []
  let i = 0
  while (i < oriented.length) {
    const current = oriented[i]
    if (current._orientation === 'landscape') {
      // 横版独占一页
      pages.push({
        type: 'single-landscape',
        images: [current],
        textSide: Math.random() > 0.5 ? 'left' : 'right', // 随机文案位置
        textCn: textCn,
        textEn: textEn,
        hasText: !!(textCn || textEn)
      })
      i++
    } else {
      // 竖版：收集连续竖版，或者一竖一横
      const portraitGroup = [current]
      i++
      // 如果下一个是竖版，加入同一页
      while (i < oriented.length && oriented[i]._orientation === 'portrait' && portraitGroup.length < 3) {
        portraitGroup.push(oriented[i])
        i++
      }
      // 如果只有一个竖版且还有下一张是横版，可以合并
      if (portraitGroup.length === 1 && i < oriented.length && oriented[i]._orientation === 'landscape') {
        pages.push({
          type: 'mixed',
          images: [...portraitGroup, oriented[i]],
          textSide: Math.random() > 0.5 ? 'left' : 'right',
          textCn: textCn,
          textEn: textEn,
          hasText: !!(textCn || textEn)
        })
        i++
      } else if (portraitGroup.length === 1) {
        // 只有一张竖版，独占一页
        pages.push({
          type: 'single-portrait',
          images: portraitGroup,
          textSide: Math.random() > 0.5 ? 'left' : 'right',
          textCn: textCn,
          textEn: textEn,
          hasText: !!(textCn || textEn)
        })
      } else {
        // 多张竖版拼一页
        pages.push({
          type: 'multi-portrait',
          images: portraitGroup,
          textSide: Math.random() > 0.5 ? 'left' : 'right',
          textCn: textCn,
          textEn: textEn,
          hasText: !!(textCn || textEn)
        })
      }
    }
  }
    return pages
})

  // 空间图片方向缓存
  const spaceOrientationCache = ref({})

  // 预加载空间图片获取尺寸
  const preloadSpaceImages = () => {
    visibleSpaces.value.forEach(space => {
      if (!space.renderings?.length) return
      space.renderings.forEach(r => {
        const url = r.image_url
        if (!url || spaceOrientationCache.value[url]) return
        const img = new Image()
        img.onload = () => {
          spaceOrientationCache.value[url] = img.naturalWidth >= img.naturalHeight ? 'landscape' : 'portrait'
        }
        img.onerror = () => {
          spaceOrientationCache.value[url] = 'landscape'
        }
        img.src = url
      })
    })
  }

  // 获取某个空间的智能分页
  const getSpaceGroupedPages = (space) => {
    if (!space.renderings?.length) return []
    const images = space.renderings.filter(r => r.image_url).map(r => ({
      url: r.image_url,
      title: r.title || '',
      description: r.description || '',
      orientation: spaceOrientationCache.value[r.image_url] || 'landscape'
    }))
    
    const pages = []
    let i = 0
    while (i < images.length) {
      const img = images[i]
      
      if (img.orientation === 'landscape') {
        // 横版独占一页
        pages.push(makeSpacePage([img], 'single-landscape'))
        i += 1
      } else {
        // 竖版：收集连续的竖版图片，最多3张拼一页
        const portraitBatch = [img]
        let j = i + 1
        while (j < images.length && images[j].orientation === 'portrait' && portraitBatch.length < 3) {
          portraitBatch.push(images[j])
          j += 1
        }
        if (portraitBatch.length === 1) {
          // 只有1张竖版，独占一页
          pages.push(makeSpacePage(portraitBatch, 'single-portrait'))
        } else {
          // 多张竖版拼一页
          pages.push(makeSpacePage(portraitBatch, 'multi-portrait'))
        }
        i = j
      }
    }
    return pages
  }

  const makeSpacePage = (images, type) => {
    const hasText = images.some(img => img.description)
    const textImg = images.find(img => img.description)
    return {
      images,
      type,
      hasText,
      textSide: hasText ? (Math.random() > 0.5 ? 'left' : 'right') : null,
      textCn: textImg?.description || '',
      textEn: textImg?.title || ''
    }
  }

  const phase7 = computed(() => phases.value[7])
const phase8 = computed(() => phases.value[8])
const phase9 = computed(() => phases.value[9])

const currentSlide = ref(0)
const viewportRef = ref(null)

// 右键菜单状态
const ctxMenu = reactive({
  visible: false,
  x: 0,
  y: 0
})

// 画幅比例对应的 padding-bottom
// ===== 适合页面缩放 =====
const DESIGN_WIDTH = 1920
const DESIGN_HEIGHT = 1080
const slideScale = ref(1)

const aspectRatioMap = { '16:9': [16, 9], '21:9': [21, 9], '4:3': [4, 3] }
const aspectRatio = computed(() => {
  const r = aspectRatioMap[slideConfig.aspect_ratio] || [16, 9]
  return r
})

const designW = computed(() => {
  const r = aspectRatio.value
  // 以高度1080为基准，按比例算宽度
  return Math.round(DESIGN_HEIGHT * r[0] / r[1])
})
const designH = DESIGN_HEIGHT

const updateSlideScale = () => {
  const el = viewportRef.value
  if (!el) return
  const vw = el.clientWidth
  const vh = el.clientHeight
  if (!vw || !vh) return
  const scaleX = vw / designW.value
  const scaleY = vh / designH
  slideScale.value = Math.min(scaleX, scaleY)
}

// 舞台样式
const stageStyle = computed(() => ({
  width: designW.value + 'px',
  height: designH + 'px',
  transform: `translate(-50%, -50%) scale(${slideScale.value})`,
  transformOrigin: 'center center',
  position: 'absolute',
  top: '50%',
  left: '50%',
}))

// 幻灯片序列
const slidePages = computed(() => {
  const pages = []
  pages.push({ key: 'cover', name: '封面' })
  if (slideConfig.show_about) pages.push({ key: 'about', name: '关于我们' })
  if (slideConfig.show_team) pages.push({ key: 'team', name: '设计团队' })
  if (slideConfig.show_toc) pages.push({ key: 'toc', name: '目录' })
  if (phase1.value && (phase1.value.layout_images?.length || phase1.value.layout_analysis)) {
    pages.push({ key: 'layout', name: '户型分析' })
  }
  if (phase2.value && (phase2.value.mood_images?.length || phase2.value.mood_text)) {
    pages.push({ key: 'mood', name: '设计意境' })
  }
  if (phase3.value && (phase3.value.plan_image || phase3.value.plan_text)) {
    pages.push({ key: 'plan', name: '平面规划' })
  }
  if (phase4.value?.birdview_images?.length) {
    pages.push({ key: 'birdview', name: '鸟瞰展示' })
  }
  // 效果图展示：标题页（已恢复原设计）
  if (phase5.value && (phase5.value.showcase_images?.length || phase5.value.showcase_title1)) {
    pages.push({ key: 'showcase', name: phase5.value.showcase_title1 || '效果图展示' })
  }
  // 空间效果图：标题页 + 智能分页
  const vSpaces = visibleSpaces.value
  vSpaces.forEach(s => {
    pages.push({ key: 'space_title_' + s.id, name: s.space_name })
    const grouped = getSpaceGroupedPages(s)
    grouped.forEach((pg, idx) => {
      pages.push({ key: 'space_page_' + s.id + '_' + idx, name: s.space_name + ' ' + (idx + 1) })
    })
    // 空间物料配置页（每页最多30行）
    const matPages = getSpaceMaterialPages(s.id)
    matPages.forEach((pg, idx) => {
      const suffix = matPages.length > 1 ? ' 物料(' + (idx + 1) + '/' + matPages.length + ')' : ' 物料配置'
      pages.push({ key: 'space_mat_' + s.id + '_' + idx, name: s.space_name + suffix })
    })
  })
  // 无空间物料配置时，按二级分类分组展示物料库数据
  if (!hasSpaceMaterials.value && rawMaterials.value.length > 0) {
    const { order } = categoryMaterialsMap.value
    order.forEach(cat => {
      const catPages = getCategoryMaterialPages(cat)
      catPages.forEach((pg, idx) => {
        const suffix = catPages.length > 1 ? ' (' + (idx + 1) + '/' + catPages.length + ')' : ''
        pages.push({ key: 'cat_mat_' + cat + '_' + idx, name: cat + suffix })
      })
    })
  }
  // 物料配置表已改为每个空间后单独展示，不再需要全局页
  if (slideConfig.show_material && showcaseMaterials.value?.length) {
    pages.push({ key: 'material', name: '材质解析' })
  }
  if (slideConfig.show_product && (phase8.value?.product_gallery?.length || phase8.value?.product_list?.length)) {
    pages.push({ key: 'product', name: '物料清单' })
  }
  if (slideConfig.show_process && phase9.value?.process_gallery?.length) {
    pages.push({ key: 'process', name: '工法解析' })
  }
  if (slideConfig.show_summary && materialSummary.value?.length) {
    pages.push({ key: 'summary', name: '物料汇总' })
  }
  pages.push({ key: 'back', name: '感谢观看' })
    return pages
})

const totalSlides = computed(() => slidePages.value.length)

const slideIndex = (key) => slidePages.value.findIndex(p => p.key === key)

const visibleSpaces = computed(() => {
  if (!spaces.value) return []
  return spaces.value.filter(s => s.renderings?.some(r => r.image_url))
})

const tocItems = computed(() => {
  if (!slidePages.value) return []
  return slidePages.value.filter(p => {
    if (p.key === 'cover' || p.key === 'toc' || p.key === 'back') return false
    // 同一空间的子页不显示，只保留空间首页
    if (p.key.startsWith('space_page_')) return false
    // 物料配置子页也不显示在目录
    if (p.key.startsWith('space_mat_')) return false
    return true
  })
})

  // 目录列数：≤12→3列，13-20→4列，21-30→5列，>30→6列
  const tocColumns = computed(() => {
    const n = tocItems.value.length
    if (n <= 12) return 3
    if (n <= 20) return 4
    if (n <= 30) return 5
    return 6
  })



// 关于我们内容：首词放大（继承模板默认值）
const aboutContentWithFirstWord = computed(() => {
  const text = slideConfig.about_content || ''
  if (!text) return ''
  const firstSpace = text.indexOf(' ')
  if (firstSpace > 0) {
    return `<span class="first-word">${text.substring(0, firstSpace)}</span>${text.substring(firstSpace)}`
  }
  return `<span class="first-word">${text}</span>`
})

// 根据幻灯片类型获取背景图样式
const slideBgStyle = (type) => {
  let imgUrl = ''
  if (type === 'cover') {
    imgUrl = slideConfig.cover_bg_image || (caseData.hero_images?.[0])
  } else if (type === 'back') {
    imgUrl = slideConfig.back_bg_image || ''
  } else {
    imgUrl = slideConfig.inner_bg_image || slideConfig.cover_bg_image || (caseData.hero_images?.[0]) || ''
  }

  if (imgUrl) {
    return {
      backgroundImage: `url('${imgUrl}')`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }
  }
  const color = slideConfig.primary_color || '#0365C0'
  if (type === 'cover' || type === 'back') {
    return { background: `linear-gradient(135deg, ${color}, #0a3d6e)` }
  }
  return { background: 'transparent' }
}

// 价格格式化
const formatPrice = (val) => {
  if (!val) return '0'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

// ===== 视口高度自适应 =====
const updateViewportHeight = () => {
  const el = viewportRef.value
  if (!el) return
  if (document.fullscreenElement) {
    el.style.height = '100vh'
    el.style.maxHeight = '100vh'
  } else {
    // 扣除顶部导航栏高度（自动探测）
    const headerEl =
      document.querySelector('.el-header') ||
      document.querySelector('header') ||
      document.querySelector('[class*="header"]') ||
      document.querySelector('.navbar') ||
      document.querySelector('.sidebar')
    let offset = 0
    if (headerEl && headerEl !== el) {
      const rect = headerEl.getBoundingClientRect()
      offset = rect.height
    }
    // 保底 60px
    const headerH = offset || 60
    el.style.height = `calc(100vh - ${headerH}px)`
    el.style.maxHeight = `calc(100vh - ${headerH}px)`
  }
  // 更新缩放
  nextTick(updateSlideScale)
}

// ===== 导航 =====
const prevSlide = () => {
  if (currentSlide.value > 0) currentSlide.value--
}
const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) currentSlide.value++
}
const jumpToSlide = (key) => {
  const idx = slideIndex(key)
  if (idx >= 0) currentSlide.value = idx
}
const toggleFullscreen = () => {
  const el = viewportRef.value
  if (!el) return
  if (!document.fullscreenElement) {
    el.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

// 双击 → 全屏
const handleDblClick = (e) => {
  // 如果点击的是导航按钮，不触发全屏
  if (e.target.closest('.slide-nav')) return
  toggleFullscreen()
}

// 右键 → 显示菜单
const showContextMenu = (e) => {
  e.preventDefault()
  // 菜单位置，确保不超出视口
  const menuW = 220
  const menuH = Math.min(slidePages.value.length * 40 + 40, 500)
  let x = e.clientX
  let y = e.clientY
  if (x + menuW > window.innerWidth) x = window.innerWidth - menuW - 12
  if (y + menuH > window.innerHeight) y = window.innerHeight - menuH - 12
  ctxMenu.x = x
  ctxMenu.y = y
  ctxMenu.visible = true
}

const hideContextMenu = () => {
  ctxMenu.visible = false
}

// 点击幻灯片画面：自动翻页（末页返回提案列表）
const handleSlideClick = () => {
  if (currentSlide.value === totalSlides.value - 1) {
    router.push('/proposals')
  } else {
    nextSlide()
  }
}

// 点击视口（非导航区域、非菜单区域）也翻页
const handleViewportClick = (e) => {
  if (ctxMenu.visible) { hideContextMenu(); return }
  if (e.target.closest('.slide-nav')) return
  if (e.target.closest('.slide-ctx-menu')) return
  nextSlide()
}

// 键盘控制
const handleKeydown = (e) => {
  if (ctxMenu.visible) { hideContextMenu(); return }
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prevSlide()
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') nextSlide()
  if (e.key === 'f' || e.key === 'F') toggleFullscreen()
  if (e.key === 'Escape') {
    if (ctxMenu.visible) { hideContextMenu(); return }
    if (document.fullscreenElement) { document.exitFullscreen?.(); return }
    router.push('/proposals')
  }
  if (e.key === 'Home') currentSlide.value = 0
  if (e.key === 'End') currentSlide.value = totalSlides.value - 1
}

// 点击外部关闭菜单
const handleClickOutside = (e) => {
  if (ctxMenu.visible && !e.target.closest('.slide-ctx-menu')) {
    hideContextMenu()
  }
}

// 加载幻灯片数据
const loadSlideData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const baseUrl = '/api/v3'
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    let url = token ? `${baseUrl}/cases/${caseId.value}/slide-data` : `${baseUrl}/public/cases/${caseId.value}/slide-data`
    let res = await fetch(url, { headers })
    let json = await res.json()

    if (json.code !== 200 && token) {
      url = `${baseUrl}/public/cases/${caseId.value}/slide-data`
      res = await fetch(url)
      json = await res.json()
    }

    const data = json.data
    slideData.value = data

    if (data.case) {
      Object.keys(data.case).forEach(k => {
        if (data.case[k] !== undefined) caseData[k] = data.case[k]
      })
    }

    if (data.slide_config) {
      Object.keys(data.slide_config).forEach(k => {
        if (data.slide_config[k] !== undefined && k in slideConfig) slideConfig[k] = data.slide_config[k]
      })
    }

    phases.value = data.phases || {}
    spaces.value = data.spaces || []
    materialSummary.value = data.material_summary || []
    rawMaterials.value = data.materials || []
    showcaseMaterials.value = data.showcase_materials || []
    pageAbout.value = data.page_about || {}
    teamMembers.value = data.team_members || []

  } catch (e) {
    console.error('Load slide data error:', e)
  } finally {
    loading.value = false
    await nextTick()
    updateViewportHeight()
    updateSlideScale()
    // 预加载效果图尺寸
    preloadShowcaseImages()
    preloadSpaceImages()
  }
}

onMounted(() => {
  loadSlideData()
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', () => { updateViewportHeight(); updateSlideScale() })
  document.addEventListener('fullscreenchange', () => { updateViewportHeight(); updateSlideScale() })
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', updateViewportHeight)
  document.removeEventListener('fullscreenchange', updateViewportHeight)
})

// 服务团队：从案例基础信息取3人（规划师/设计师/客户经理），平等关系
const serviceTeam = computed(() => {
  const list = [
    { ...(caseData.planner || {}), role: '全案规划师' },
    { ...(caseData.designer || {}), role: '全案设计师' },
    { ...(caseData.responsible || {}), role: '客户经理' },
  ].filter(m => m.id)
  return list.length ? list : [
    { name: '待指定', role: '全案规划师' },
    { name: '待指定', role: '全案设计师' },
    { name: '待指定', role: '客户经理' },
  ]
})

// 关于我们标题 - 非中文字符（英文字母+符号）标红，中文保持黑色
const aboutTitleWithRedEnglish = computed(() => {
  const text = slideConfig.about_title || ''
  if (!text) return ''
  return text.replace(/[^\u4e00-\u9fa5]/g, (match) => `<span style="color:#FF0000">${match}</span>`)
})
// 配色方案（带标签）
const colorScheme = computed(() => {
  const scheme = []
  // 兼容两种格式：字符串数组 或 对象{hex, name, ...}
  const pickColor = (val) => {
    if (!val) return null
    if (typeof val === 'string') return val
    if (Array.isArray(val)) return val.length ? val[0] : null
    if (typeof val === 'object') return val.hex || val.color || null
    return null
  }
  const mc = pickColor(caseData.main_colors)
  if (mc) scheme.push({ label: '主色', color: mc })
  const ac = pickColor(caseData.auxiliary_colors)
  if (ac) scheme.push({ label: '辅助色', color: ac })
  const cc = pickColor(caseData.accent_colors)
  if (cc) scheme.push({ label: '点缀色', color: cc })
  const bc = pickColor(caseData.background_colors)
  if (bc) scheme.push({ label: '背景色', color: bc })
  return scheme
})

// 配色列表
const colorsList = computed(() => {
  const colors = []
  if (Array.isArray(caseData.main_colors)) colors.push(...caseData.main_colors)
  if (Array.isArray(caseData.auxiliary_colors)) colors.push(...caseData.auxiliary_colors)
  if (Array.isArray(caseData.accent_colors)) colors.push(...caseData.accent_colors)
  return [...new Set(colors)].slice(0, 5)
})

// 预算汇总
const totalBudget = computed(() => {
  if (materialSummary.value && materialSummary.value.length) {
    return materialSummary.value.reduce((sum, m) => sum + (parseFloat(m.total) || 0), 0)
  }
  return 0
})

// 预算显示
const budgetDisplay = computed(() => {
  if (!totalBudget.value) return '待定'
  const wan = totalBudget.value / 10000
  return wan.toFixed(1) + '万'
})

</script>

<style scoped>
/* === 视口：深空黑色，高度自适应 === */
.slide-viewport {
  width: 100%;
  height: calc(100vh - 60px);
  max-height: calc(100vh - 60px);
  overflow: hidden;
  position: relative;
  background: #0a0a0a;
  font-family: -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 全屏时由 JS 动态覆盖为 height:100vh */
}

:fullscreen .slide-viewport,
:-webkit-full-screen .slide-viewport {
  height: 100vh !important;
  max-height: 100vh !important;
}

/* === 舞台：固定设计画布 + 缩放适合页面 === */
.slide-stage {
  position: absolute;
  overflow: hidden;
  /* width/height/transform 由 stageStyle 动态设置 */
}

/* 非全屏时舞台受视口限制 — 已由 JS 缩放处理 */

/* 21:9 等比例已由 JS 动态计算 designW 处理 */

/* === 通用幻灯片 === */
.slide {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  overflow: hidden;
}
.slide.active {
  opacity: 1;
  pointer-events: auto;
}

/* 背景图层 */
.slide-bg-img {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
}

/* 内容层 */
.slide-content {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 50px 200px 0;
}

/* 暗色主题内容样式 */
.slide-heading {
  color: inherit;
  font-size: 26px;
  font-weight: 700;
  border-bottom: 2px solid var(--slide-primary, #0365C0);
  padding-bottom: 10px;
  margin-bottom: 20px;
}

/* === 导航栏 === */
.slide-nav {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 14px;
  z-index: 100;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(10px);
  padding: 7px 18px;
  border-radius: 30px;
  cursor: default;
  pointer-events: auto;
}

.nav-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.35);
  color: #fff;
  padding: 5px 11px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.2s;
}
.nav-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.2);
}
.nav-btn:disabled {
  opacity: 0.3;
  cursor: default;
}
.slide-counter {
  color: rgba(255,255,255,0.9);
  font-size: 13px;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

/* 键盘提示 */
.keyboard-hint {
  position: fixed;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255,255,255,0.3);
  font-size: 11px;
  z-index: 99;
  pointer-events: none;
}

/* === 封面 === */
.cover-content {
  text-align: center;
  padding: 8%;
  justify-content: center;
}
.cover-title {
  font-size: clamp(28px, 4vw, 52px);
  font-weight: 800;
  margin-bottom: 14px;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.cover-subtitle {
  color: #C9A96E;
  font-size: 32px;
  font-weight: 300;
  font-style: italic;
  opacity: 0.9;
  margin: 0;
}

.cover-case-title {
  font-size: 48px;
  font-weight: 700;
  color: #ffffff;
  font-family: "Microsoft YaHei", "SimHei", sans-serif;
  margin-top: 8px;
  margin-bottom: 0;
  letter-spacing: 2px;
}

.cover-scene-tags {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.scene-tag-item {
  display: inline-block;
  font-size: 28px;
  color: #C9A96E;
  border: 1px solid rgba(201, 169, 110, 0.6);
  padding: 4px 20px;
  margin-right: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  letter-spacing: 2px;
}
.cover-meta {
  display: flex;
  gap: 14px;
  justify-content: center;
  font-size: clamp(12px, 1.5vw, 15px);
  flex-wrap: wrap;
}
.cover-meta span {
  padding: 3px 12px;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 20px;
  background: rgba(255,255,255,0.08);
}

/* === 关于我们 === */
.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 0 5%;
  gap: 20px;
}
.about-title {
  color: #1a1a1a !important;
  font-size: 56px;
  font-weight: 800;
  letter-spacing: 6px;
  line-height: 1.2;
}
.about-subtitle {
  color: inherit;
  font-size: 28px;
  font-weight: 400;
  line-height: 1.5;
}
.about-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: 1200px;
  width: 100%;
  padding-top: 20px;
}
.about-text {
  font-size: 28px;
  line-height: 1.8;
  opacity: 0.8;
  text-align: left;
}
.first-word {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}
.about-stats { display: flex; gap: 48px; justify-content: center; }
.stat-item { text-align: center; }
.stat-value { font-size: clamp(18px, 2.5vw, 26px); font-weight: 700; color: var(--slide-primary, #0365C0); }
.stat-label { font-size: 13px; opacity: 0.6; }

/* === 团队 === */
.team-content { text-align: center; padding: 0 0 3%; }
.team-label { font-size: 12px; letter-spacing: 4px; color: #999; text-transform: uppercase; margin-bottom: 8px; }
.team-title { font-size: 32px; font-weight: 700; color: #1a1a1a; margin-bottom: 32px; }
.team-cards { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; max-width: 1400px; margin: 0 auto; }
.team-member-card {
  flex: 1; min-width: 280px; max-width: 380px;
  display: flex; flex-direction: column; align-items: center;
  transition: transform 0.3s ease;
}
.team-member-card:hover {
  transform: translateY(-4px);
}
.team-avatar-wrap {
  width: 375px; height: 500px;
  aspect-ratio: 3/4;
  overflow: hidden;
  margin-bottom: 20px;
  border: 10px solid #ffffff;
  box-shadow: 0 4px 20px rgba(0,0,0,0.10);
  background: #f5f0eb;
}
.team-avatar-img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
.team-avatar-placeholder {
  width: 100%; height: 100%;
  background: linear-gradient(180deg, #e8e0d4 0%, #d4ccc0 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 80px; font-weight: 700; color: #5a4a3a;
  letter-spacing: 4px;
}
.team-member-info { text-align: center; margin-top: 16px; }
.team-role-tag {
  display: inline-block;
  font-size: 11px; letter-spacing: 2px; color: #8B7355;
  padding: 2px 12px;
  border: 1px solid #d4c4a8;
  border-radius: 20px;
  margin-bottom: 6px;
}
.team-member-name { font-size: 22px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px 0; letter-spacing: 2px; }
.team-member-bio {
  font-size: 13px; color: #777; line-height: 1.8;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  max-width: 300px;
  margin: 0 auto;
}

/* === 目录 === */
.toc-content { position: relative; padding-top: 50px; padding-left: 200px; padding-right: 200px; }
.toc-label { font-size: 11px; letter-spacing: 4px; color: #999; text-transform: uppercase; margin-bottom: 8px; }
.toc-title { font-size: 32px; font-weight: 700; color: #1a1a1a; margin-bottom: 40px; }
.toc-grid { display: grid; column-gap: 30px; row-gap: 18px; padding: 0 0 80px; }
.toc-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.toc-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.14);
}
.toc-card-num {
  font-size: 36px;
  font-weight: 800;
  color: #C9A96E;
  line-height: 1;
  min-width: 52px;
}
.toc-card-name {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 1px;
}
.toc-card-arrow {
  font-size: 18px;
  color: #C9A96E;
  transition: transform 0.2s ease;
}
.toc-card:hover .toc-card-arrow {
  transform: translateX(4px);
}

/* === 户型分析 === */
.layout-card {
  position: absolute;
  top: 80px;
  left: 80px;
  right: 80px;
  bottom: 80px;
  display: flex;
  gap: 0;
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
}
.layout-text {
  flex: 0 0 38%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 36px 48px 48px;
}
.layout-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 20px 0;
  letter-spacing: 2px;
}
.layout-body {
  font-size: 16px !important;
  line-height: 1.7 !important;
  color: #333;
  overflow: visible;
}
.layout-body * {
  line-height: 1.7 !important;
}
.layout-images {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
  gap: 16px;
}
.layout-img-item {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.layout-img-item img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

/* === 设计意境卡片（图片左+文案右） === */
.mood-card {
  position: absolute;
  top: 80px;
  left: 80px;
  right: 80px;
  bottom: 80px;
  display: flex;
  gap: 0;
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
}
.mood-images {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
  gap: 16px;
}
.mood-img-item {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mood-img-item img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}
.mood-text {
  flex: 0 0 38%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 48px 48px 36px;
}
.mood-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 20px 0;
  letter-spacing: 2px;
}
.mood-body {
  font-size: 16px !important;
  line-height: 1.7 !important;
  color: #333;
  overflow: visible;
}
.mood-body * {
  line-height: 1.7 !important;
}

/* === 鸟瞰展示（标题居中+双图最大化垂直居中） === */
.birdview-title {
  position: absolute;
  top: 50px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  z-index: 2;
}
.birdview-grid {
  position: absolute;
  top: 110px;
  left: 60px;
  right: 60px;
  bottom: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
}
.birdview-img {
  flex: 1;
  max-width: 50%;
  height: 100%;
  overflow: hidden;
  border-radius: 8px;
}
.birdview-img img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

/* === 通用阶段内容 === */
.phase-content { max-width: 1000px; margin: 0 auto; padding: 0 0 4%; }
.phase-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.phase-gallery-item img { width: 100%; height: auto; object-fit: contain; border-radius: 6px; }
.phase-text { font-size: 14px; line-height: 1.8; opacity: 0.75; }
/* === 效果图展示首页（居中、不裁切、英文文案） === */
.showcase-cover {
  position: absolute;
  top: 60px;
  left: 80px;
  right: 80px;
  bottom: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.showcase-cover-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  text-align: center;
  margin-bottom: 6px;
}
.showcase-cover-subtitle {
  font-size: 19px;
  color: #555;
  text-align: center;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
}
.showcase-cover-gallery {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  width: 100%;
  flex-wrap: nowrap;
}
.showcase-cover-img {
  flex: 1 1 0;
  min-width: 0;
  max-height: 400px;
}
.showcase-cover-img img {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 4px;
}
.showcase-cover-text {
  width: 100%;
  max-width: 900px;
  margin-top: 28px;
  text-align: left;
  padding-left: 8px;
  border-left: 2px solid #c9a96e;
  padding-left: 16px;
}
.showcase-cover-cn {
  font-size: 15px;
  line-height: 1.8 !important;
  color: #2a2a2a;
  margin-bottom: 10px;
  letter-spacing: 0.3px;
}
.showcase-cover-en {
  font-size: 13px;
  line-height: 1.7 !important;
  color: #999;
  font-style: italic;
  letter-spacing: 0.2px;
}

/* ===== 效果图分页布局 ===== */
.showcase-page {
  position: absolute;
  top: 40px;
  left: 60px;
  right: 60px;
  bottom: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.showcase-page-images {
  display: flex;
  justify-content: center;
  align-items: center;
}

.showcase-page-img img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}

/* 横版独占 */
.showcase-page--single-landscape .showcase-page-images {
  flex: 1;
  height: 85%;
}

.showcase-page--single-landscape .showcase-page-img {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 单竖版 */
.showcase-page--single-portrait .showcase-page-images {
  flex: 0 0 42%;
  height: 85%;
}

.showcase-page--single-portrait .showcase-page-img {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 多竖版拼一页 */
.showcase-page--multi-portrait .showcase-page-images {
  flex: 1;
  gap: 12px;
  height: 85%;
  align-items: stretch;
}

.showcase-page--multi-portrait .showcase-page-img {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 混排（竖+横） */
.showcase-page--mixed .showcase-page-images {
  flex: 1;
  gap: 16px;
  height: 85%;
}

.showcase-page--mixed .showcase-page-img {
  height: 85%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.showcase-page--mixed .showcase-page-img:first-child {
  flex: 0 0 35%;
}

.showcase-page--mixed .showcase-page-img:last-child {
  flex: 1;
}

/* 效果图文案 */
.showcase-page-text {
  flex: 0 0 350px;
  padding: 20px 16px;
}

.showcase-page-text--left {
  border-left: 2px solid #c9a96e;
}

.showcase-page-text--right {
  border-left: 2px solid #c9a96e;
  text-align: left;
}

.showcase-page-cn {
  font-size: 18px;
  line-height: 1.8;
  color: #2a2a2a;
  margin-bottom: 10px;
  letter-spacing: 0.3px;
}

.showcase-page-en {
  font-size: 15px;
  line-height: 1.7;
  color: #999;
  font-style: italic;
  letter-spacing: 0.2px;
}

/* ===== 物料配置表（精简 9 列 + 白底玻璃态） ===== */

.smat-th-idx { width: 36px; text-align: center; }
.smat-th-custom { width: 150px; text-align: left; }
.smat-th-name { text-align: left; }
.smat-th-dim { width: 130px; text-align: center; }
.smat-th-measure { width: 90px; text-align: center; }
.smat-th-num { width: 60px; text-align: center; }
.smat-th-price { width: 90px; text-align: center; }
.smat-th-total { width: 100px; text-align: center; }

.smat-idx { text-align: center; color: #999; font-size: 18px; }
.smat-custom { font-size: 18px; font-weight: 500; color: #333; }
.smat-dim { text-align: center; font-size: 18px; color: #888; font-variant-numeric: tabular-nums; }
.smat-measure { font-size: 18px; color: #666; text-align: center; font-variant-numeric: tabular-nums; }

.material-config-content {
  padding: 30px 50px !important;
  overflow-y: auto !important;
  color: #333 !important;
}

/* === 空间物料配置页 === */
.space-material-content { padding: 3% 5%; max-width: 1400px; margin: auto; color: #333; }
.smat-heading {
  font-size: 22px !important; font-weight: 700; color: #5a4520 !important;
  margin-bottom: 18px !important; padding-bottom: 10px;
  border-bottom: 1px solid rgba(201,169,110,0.3);
  letter-spacing: 1px;
}
.smat-heading::after {
  content: '' !important; display: block; width: 40px; height: 2px;
  background: #c9a96e; margin-top: 10px;
}
.smat-table {
  width: 100%; border-collapse: collapse; font-size: 18px;
  background: rgba(255,255,255,0.78); backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 12px; overflow: hidden;
  border: 1px solid rgba(201,169,110,0.15);
  box-shadow: 0 2px 16px rgba(0,0,0,0.06);
}
.smat-table thead {
  background: rgba(201,169,110,0.08);
}
.smat-table th {
  padding: 14px 12px; text-align: center; font-weight: 600;
  color: #6b5530; border-bottom: 2px solid rgba(201,169,110,0.2);
  font-size: 22px; letter-spacing: 0.5px; text-transform: uppercase;
}
.smat-th-custom, .smat-th-name { text-align: left !important; }
.smat-table td {
  padding: 12px 12px; border-bottom: 1px solid rgba(0,0,0,0.04); color: #444;
}
.smat-row { cursor: pointer; transition: background 0.2s; }
.smat-row:hover { background: rgba(201,169,110,0.06); }
.smat-name { font-weight: 400; color: #777; font-size: 18px; max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.smat-num { text-align: center; font-variant-numeric: tabular-nums; color: #555; }
.smat-price { font-weight: 600; color: #a07d3a; }
.smat-total { font-size: 18px; font-weight: 700; }
.smat-foot-label { text-align: right; font-weight: 600; color: #888; font-size: 18px; }
.smat-table tfoot td {
  padding: 12px 10px; border-top: 1px solid rgba(201,169,110,0.2); color: #666;
}
.smat-page-info {
  text-align: center; font-size: 12px; color: #aaa; margin-top: 14px;
}

/* === 物料详情弹窗 === */
.material-detail-dialog :deep(.el-dialog__body) { padding: 0; }
.md-layout { display: flex; gap: 0; }
.md-image-area {
  width: 300px; min-height: 380px; background: #f9f6f3;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.md-main-img {
  max-width: 100%; max-height: 380px; object-fit: contain; padding: 16px;
}
.md-no-img {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  color: #c0b4a8; font-size: 14px;
}
.md-info-area { flex: 1; padding: 28px 32px; }
.md-title {
  font-size: 20px; font-weight: 700; color: #1a1a1a; margin: 0 0 12px 0;
}
.md-divider { width: 40px; height: 3px; background: #722F37; margin-bottom: 20px; border-radius: 2px; }
.md-props { display: flex; flex-direction: column; gap: 14px; }
.md-prop { display: flex; align-items: baseline; }
.md-prop-label {
  width: 80px; flex-shrink: 0; font-size: 13px; color: #999; font-weight: 500;
}
.md-prop-value { font-size: 14px; color: #333; font-weight: 400; }
.md-price { color: #722F37; font-weight: 600; font-size: 16px; }

.mc-heading {
  font-size: 24px !important;
  font-weight: 700;
  color: #722F37;
  margin-bottom: 20px !important;
  padding-bottom: 10px;
  border-bottom: 2px solid #722F37;
}

.mc-tables {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mc-group-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.mc-group-space {
  color: #722F37;
  font-weight: 700;
}

.mc-group-cat {
  color: #888;
  font-size: 13px;
  padding: 2px 8px;
  background: #f5f0eb;
  border-radius: 3px;
}

.mc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.mc-table thead {
  background: #f5f0eb;
}

.mc-table th {
  padding: 8px 10px;
  text-align: center;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #e8e0d6;
  font-size: 12px;
}

.mc-table td {
  padding: 7px 10px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.mc-table tbody tr:hover {
  background: #fdf8f4;
}

.mc-name {
  font-weight: 500;
  color: #1a1a1a;
}

.mc-num {
  text-align: center;
}

.mc-price {
  font-weight: 600;
  color: #722F37;
}

.mc-total {
  font-size: 14px;
  font-weight: 700;
}

.mc-table tfoot td {
  padding: 10px;
  font-weight: 600;
  border-top: 2px solid #e8e0d6;
  color: #555;
}

/* === 空间展示 === */
.space-content { padding: 0 0 4%; max-width: 1600px; margin: auto; }
.showcase-slide .phase-content { max-width: none; margin: 0; padding: 100px 60px; }
.showcase-slide .phase-gallery { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.showcase-slide .phase-text { font-size: 15px; line-height: 1.8; opacity: 0.8; }
.space-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  max-height: 72vh;
  overflow-y: auto;
}
.space-item img { width: 100%; height: 220px; object-fit: cover; border-radius: 6px; }
.space-item-info { padding: 6px 0; }
.space-item-title { font-size: 14px; font-weight: 600; }
.space-item-desc { font-size: 13px; opacity: 0.6; }

/* === 材质 === */
.material-content { max-width: 1600px; margin: 0 auto; padding: 3% 4%; }
.material-showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}
.showcase-card {
  background: rgba(255,255,255,0.08);
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.showcase-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.25);
}
.showcase-card-img {
  width: 100%;
  aspect-ratio: 1 / 2;
  overflow: hidden;
}
.showcase-card-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.showcase-card-info {
  padding: 10px 14px 14px;
}
.showcase-card-l1 {
  font-size: 11px;
  color: #C9A96E;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.showcase-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #eee;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.showcase-card-spec {
  font-size: 12px;
  color: #aaa;
  margin-bottom: 2px;
}
.showcase-card-brand {
  font-size: 11px;
  color: #888;
}

/* === 物料 === */
.product-content { max-width: 1200px; margin: 0 auto; padding: 4% 5%; }
.product-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}
.product-item img { width: 100%; height: 160px; object-fit: cover; border-radius: 5px; }
.product-table { overflow-x: auto; }
.product-table table { width: 100%; border-collapse: collapse; font-size: 13px; }
.product-table th { padding: 7px 10px; background: rgba(255,255,255,0.1); text-align: left; font-weight: 600; }
.product-table td { padding: 7px 10px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.product-table .price { font-weight: 600; color: #e6a23c; }

/* === 物料汇总 === */
.summary-content { max-width: 1200px; margin: 0 auto; padding: 4% 5%; }
.summary-cards {
  display: flex; flex-direction: column; gap: 12px;
  overflow-y: auto; max-height: 68vh;
  padding-right: 8px;
}
.summary-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px;
  background: rgba(255,255,255,0.78); backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(201,169,110,0.15);
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transition: background 0.2s;
}
.summary-card:hover { background: rgba(255,255,255,0.88); }
.summary-cat { font-size: 20px; font-weight: 600; color: #5a4520; }
.summary-stats { display: flex; align-items: center; gap: 20px; }
.summary-measure { font-size: 16px; color: #666; font-variant-numeric: tabular-nums; }
.summary-total { font-size: 18px; font-weight: 700; color: #a07d3a; font-variant-numeric: tabular-nums; }
.summary-grand-total {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 20px; padding: 18px 24px;
  background: rgba(201,169,110,0.1); backdrop-filter: blur(16px);
  border-radius: 12px;
  border: 1px solid rgba(201,169,110,0.2);
}
.summary-grand-total span:first-child { font-size: 20px; font-weight: 700; color: #5a4520; }
.grand-amount { font-size: 24px; font-weight: 800; color: #8b6914; font-variant-numeric: tabular-nums; }

/* === 封底 === */
.back-content { text-align: center; padding: 200px 8% 8%; justify-content: center; }
.back-title { font-size: clamp(28px, 4vw, 46px); font-weight: 800; margin-bottom: 10px; }
.back-subtitle { font-size: clamp(14px, 2vw, 20px); opacity: 0.75; }

/* ======= 右键菜单 ======= */
.slide-ctx-mask {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0,0,0,0.25);
}
.slide-ctx-menu {
  position: fixed;
  z-index: 10001;
  background: rgba(20,20,30,0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  padding: 6px 0;
  min-width: 200px;
  max-height: 55vh;
  overflow-y: auto;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
}
.ctx-header {
  padding: 8px 16px 6px;
  font-size: 11px;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 4px;
}
.ctx-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 16px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 13px;
  color: rgba(255,255,255,0.8);
}
.ctx-item:hover {
  background: rgba(255,255,255,0.1);
}
.ctx-item.active {
  background: rgba(3,101,192,0.25);
  color: #fff;
}
.ctx-idx {
  display: inline-block;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  text-align: center;
  line-height: 22px;
  font-size: 11px;
  flex-shrink: 0;
}
.ctx-item.active .ctx-idx {
  background: var(--slide-primary, #0365C0);
  color: #fff;
}
.ctx-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 菜单动画 */
.ctx-fade-enter-active, .ctx-fade-leave-active { transition: opacity 0.2s; }
.ctx-fade-enter-from, .ctx-fade-leave-to { opacity: 0; }
.ctx-pop-enter-active { transition: all 0.2s cubic-bezier(0.16,1,0.3,1); }
.ctx-pop-leave-active { transition: all 0.15s ease-in; }
.ctx-pop-enter-from { opacity: 0; transform: scale(0.95) translateY(-4px); }
.ctx-pop-leave-to { opacity: 0; transform: scale(0.97); }


/* === 文字配色：封面/封底白，内页黑 === */
.cover-content,
.back-content {
  color: #ffffff !important;
}
.cover-content .cover-title,
.cover-content .cover-atmosphere,
.cover-content .cover-budget,
.cover-content .cover-style,
.cover-content .cover-meta-grid,
.cover-content .cover-description,
.cover-content .cover-colors,
.back-content .back-title,
.back-content .back-subtitle {
  color: #ffffff !important;
}

.cover-content .cover-subtitle {
  color: #C9A96E !important;
}

.phase-content,
.space-content,
.process-content { max-width: 1000px; margin: 0 auto; padding: 4% 5%; }
.process-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}
.process-item img { width: 100%; height: 160px; object-fit: cover; border-radius: 5px; }
.process-text { font-size: 14px; line-height: 1.8; opacity: 0.7; }

.material-content,
.material-config-content,
.product-content,
.process-content,
.summary-content,
.about-content,
.team-content,
.toc-content {
  color: #1a1a1a !important;
}



/* === 封面杂志风两列布局 === */
.magazine-cover {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 60px 80px;
  box-sizing: border-box;
  height: 100%;
  gap: 60px;
}
.cover-left {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  gap: 24px;
  text-align: left;
}
.cover-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-radius: 16px;
  padding: 32px 36px;
  text-align: right;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.cover-title {
  font-size: 64px;
  font-weight: 700;
  line-height: 1.1;
  color: #C9A96E;
  text-shadow: 0 2px 20px rgba(0,0,0,0.5);
  letter-spacing: -1px;
  margin-bottom: 8px;
}
.cover-subtitle {
  font-size: 32px;
  font-weight: 400;
  color: #C9A96E;
  opacity: 0.9;
  font-style: italic;
  margin-top: 0;
  text-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.cover-budget {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.budget-label {
  font-size: 18px;
  font-weight: 400;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 2px;
}
.budget-value {
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -1px;
}
.cover-style {
  display: flex;
  align-items: center;
}
.style-tag {
  display: inline-block;
  padding: 6px 18px;
  border: 1px solid currentColor;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 1px;
  opacity: 0.9;
}
.cover-colors {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.color-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.4);
  flex-shrink: 0;
}
.cover-meta-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 16px;
}
.meta-label {
  font-weight: 600;
  opacity: 0.7;
  min-width: 52px;
  font-size: 14px;
  letter-spacing: 1px;
  text-transform: uppercase;
  flex-shrink: 0;
}
.meta-value {
  font-weight: 400;
  font-size: 16px;
}
.cover-description {
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.8;
  font-style: normal;
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 16px;
}
.cover-description p {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}


.brand-name {
  font-size: 64px;
  font-weight: 700;
  line-height: 1.1;
  color: #ffffff;
  letter-spacing: -1px;
  margin-bottom: 4px;
}
.cover-atmosphere {
  font-size: 32px;
  font-weight: 300;
  opacity: 0.9;
  font-style: italic;
  margin-top: 8px;
}
.cover-colors-labeled {
  display: flex;
  flex-direction: row;
  gap: 20px;
  margin-top: 16px;
}
.color-label-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.color-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.4);
  flex-shrink: 0;
}
.color-name {
  font-size: 12px;
  opacity: 0.85;
  letter-spacing: 1px;
  white-space: nowrap;
}

</style>
