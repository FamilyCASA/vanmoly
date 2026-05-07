<template>
  <div class="case-detail-v2">
    <!-- 固定导航栏（滚动后显示） -->
    <nav class="fixed-nav" :class="{ visible: showFixedNav }">
      <div class="nav-container">
        <div class="nav-left">
          <button class="back-btn" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <span class="nav-title">{{ caseDetail?.title || '案例详情' }}</span>
        </div>
        <div class="nav-right">
          <button class="nav-icon-btn" @click="handleLike">
            <el-icon><Star :class="{ active: isLiked }" /></el-icon>
          </button>
          <button class="nav-icon-btn" @click="handleShare">
            <el-icon><Share /></el-icon>
          </button>
        </div>
      </div>
    </nav>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-screen">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 案例内容 -->
    <div v-else-if="caseDetail" class="case-content">
      <!-- Hero 全屏区域 -->
      <section class="hero-section">
        <!-- 轮播英雄图 - Ken Burns 缩放 -->
        <div v-if="heroImages.length > 0" class="hero-carousel">
          <div
            v-for="(img, idx) in heroImages"
            :key="idx"
            class="hero-slide"
            :class="{ active: idx === currentHeroIndex, prev: idx === prevHeroIndex }"
          >
            <img :src="img.url" :alt="caseDetail.title" />
          </div>
          <div class="hero-gradient"></div>
          <!-- 轮播指示器 -->
          <div class="carousel-indicators" v-if="heroImages.length > 1">
            <span
              v-for="(img, idx) in heroImages"
              :key="idx"
              class="indicator"
              :class="{ active: idx === currentHeroIndex }"
              @click="goToHero(idx)"
            ></span>
          </div>
          <!-- 左右切换 -->
          <button v-if="heroImages.length > 1" class="carousel-arrow left" @click="prevHero">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <button v-if="heroImages.length > 1" class="carousel-arrow right" @click="nextHero">
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
        <!-- 单图降级 -->
        <div v-else class="hero-bg">
          <img :src="caseDetail.cover_image || '/placeholder-case.jpg'" :alt="caseDetail.title">
          <div class="hero-gradient"></div>
        </div>
        
        <div class="hero-content">
          <div class="back-float" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
          </div>
          
          <div class="hero-text">
            <div class="case-meta">
              <span v-if="caseDetail.is_featured" class="featured-badge">精选案例</span>
              <span class="location" v-if="caseDetail.location">
                <el-icon><Location /></el-icon>
                {{ caseDetail.location }}
              </span>
            </div>
            
            <h1 class="case-title">{{ caseDetail.title }}</h1>
            
            <p class="case-subtitle" v-if="caseDetail.subtitle || caseDetail.style">
              {{ caseDetail.subtitle || (caseDetail.style + ' · ' + (caseDetail.area || '') + '㎡') }}
            </p>
            
            <div class="case-tags">
              <span v-if="caseDetail.style" class="tag">{{ caseDetail.style }}</span>
              <span v-if="caseDetail.house_type" class="tag">{{ caseDetail.house_type }}</span>
              <span v-if="caseDetail.area" class="tag">{{ caseDetail.area }}㎡</span>
              <span v-if="caseDetail.package_type" class="tag highlight">{{ caseDetail.package_type }}</span>
              <span v-if="caseDetail.workflow_progress" class="tag workflow-tag">
                <span class="tag-dot" :class="getProgressClass(caseDetail.workflow_progress)"></span>
                {{ caseDetail.workflow_progress.current_phase || '进行中' }} · {{ caseDetail.workflow_progress.progress_pct }}%
              </span>
            </div>

            <!-- 预算金额 -->
            <div class="hero-budget" v-if="caseDetail.deal_budget || caseDetail.total_price || caseDetail.quote_info">
              <div class="budget-item" @click="openQuotePreview">
                <span class="budget-label">
                  <span v-if="caseDetail.is_real_case">真实案例</span>
                  <span v-else>参考造价</span>
                </span>
                <span class="budget-value">
                  <span class="budget-unit">¥</span>
                  {{ caseDetail.quote_info ? formatWan(caseDetail.quote_info.total_amount) : formatWan(caseDetail.deal_budget || caseDetail.total_price) }}
                </span>
                <span class="budget-arrow">
                  <el-icon><ArrowRight /></el-icon>
                </span>
              </div>
            </div>
          </div>
          
          <div class="scroll-hint" @click="scrollToContent">
            <span>向下滑动</span>
            <div class="scroll-arrow">
              <el-icon><ArrowDown /></el-icon>
            </div>
          </div>
        </div>
      </section>

      <!-- 项目概览 -->
      <section class="overview-section" ref="contentRef">
        <div class="container">
          <div class="overview-grid">
            <div class="overview-item">
              <span class="label">户型</span>
              <span class="value">{{ caseDetail.house_type || '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">面积</span>
              <span class="value">{{ caseDetail.area ? caseDetail.area + '㎡' : '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">风格</span>
              <span class="value">{{ caseDetail.style || '-' }}</span>
            </div>
            <div class="overview-item">
              <span class="label">工期</span>
              <span class="value">{{ caseDetail.duration || '90' }}天</span>
            </div>
            <div class="overview-item highlight" v-if="caseDetail.total_price">
              <span class="label">全案总价</span>
              <span class="value price">¥{{ formatPrice(caseDetail.total_price) }}</span>
            </div>
            <div class="overview-item budget" v-if="caseDetail.deal_budget || caseDetail.quote_info" @click="openQuotePreview">
              <span class="label">参考造价</span>
              <span class="value price clickable">
                <span v-if="caseDetail.quote_info">{{ formatWan(caseDetail.quote_info.total_amount) }}</span>
                <span v-else>{{ formatWan(caseDetail.deal_budget) }}</span>
                <el-icon><ArrowRight /></el-icon>
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 分类Tab导航 -->
      <section class="category-tabs-section" ref="contentRef">
        <div class="container">
          <div class="category-tabs">
            <button
              v-for="cat in categories"
              :key="cat.key"
              class="category-tab"
              :class="{ active: activeCategory === cat.key }"
              @click="activeCategory = cat.key"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>
      </section>

      <!-- 6阶段内容展示 -->
      <section class="phase-content-section">
        <div class="container">

          <!-- 户型分析 - 上图下文布局 -->
          <div v-if="activeCategory === 'layout'" class="phase-panel layout-analysis-stacked">
            <template v-if="phase1.layout_images?.length || phase1.layout_analysis">
              <div v-if="phase1.layout_images?.length" class="layout-image-stack">
                <div
                  v-for="(img, idx) in phase1.layout_images"
                  :key="idx"
                  class="layout-floorplan-card"
                  @click="openImagePreview(idx, phase1.layout_images)"
                >
                  <img :src="resolveImgUrl(img)" alt="户型图" />
                  <div class="img-overlay"><el-icon><ZoomIn /></el-icon></div>
                </div>
              </div>
              <div v-if="phase1.layout_analysis" class="layout-text-block">
                <h3 class="layout-title">原始户型</h3>
                <div class="layout-analysis-content rich-text" v-html="phase1.layout_analysis"></div>
              </div>
              <el-empty v-else-if="!phase1.layout_analysis" description="暂无户型分析内容" :image-size="80" />
            </template>
            <el-empty v-else description="暂无户型分析内容" />
          </div>

          <!-- 设计意境 -->
          <div v-if="activeCategory === 'mood'" class="phase-panel">
            <div v-if="resolveImgList(phase2.mood_images).length" class="phase-magazine-layout">
              <div
                v-for="(img, idx) in resolveImgList(phase2.mood_images)"
                :key="idx"
                class="magazine-card"
                :class="{ 'large': idx % 3 === 0 }"
                @click="openImagePreview(idx, resolveImgList(phase2.mood_images))"
              >
                <div class="mag-img-wrap">
                  <img :src="img" loading="lazy" />
                  <div class="mag-overlay"><el-icon><ZoomIn /></el-icon></div>
                </div>
                <div class="mag-caption" v-if="phase2.mood_text">
                  <p v-html="formatDropCap(phase2.mood_text)"></p>
                </div>
              </div>
            </div>
            <el-empty v-if="!resolveImgList(phase2.mood_images).length" description="暂无设计意境内容" />
          </div>


          <!-- 户型规划 - 上图下文布局 -->
          <div v-if="activeCategory === 'plan'" class="phase-panel plan-stacked">
            <div v-if="resolveImgUrl(phase3.plan_image)" class="plan-image-wrap" @click="openImagePreview(0, [resolveImgUrl(phase3.plan_image)])">
              <img :src="resolveImgUrl(phase3.plan_image)" />
              <div class="img-overlay"><el-icon><ZoomIn /></el-icon></div>
            </div>
            <div v-if="phase3.plan_text" class="plan-text-block">
              <h3 class="phase-heading">平面规划</h3>
              <div class="phase-body rich-text" v-html="phase3.plan_text"></div>
            </div>
            <el-empty v-if="!resolveImgUrl(phase3.plan_image) && !phase3.plan_text" description="暂无户型规划内容" />
          </div>

          <!-- 鸟瞰图展示 -->
          <div v-if="activeCategory === 'birdview'" class="phase-panel">
            <div v-if="resolveImgList(phase4.birdview_images).length" class="phase-birdview-stack">
              <div v-for="(img, idx) in resolveImgList(phase4.birdview_images)" :key="idx" class="phase-birdview-item" @click="openImagePreview(idx, resolveImgList(phase4.birdview_images))">
                <img :src="img" loading="lazy" />
                <div class="img-overlay"><el-icon><ZoomIn /></el-icon></div>
              </div>
            </div>
            <el-empty v-if="!resolveImgList(phase4.birdview_images).length" description="暂无鸟瞰图内容" />
          </div>

          <!-- 设计意向图 -->
          <div v-if="activeCategory === 'showcase'" class="phase-panel">
            <!-- 标题区 -->
            <div v-if="phase5.showcase_title1" class="showcase-header">
              <h3>{{ phase5.showcase_title1 }}</h3>
              <p v-if="phase5.showcase_title2" class="showcase-subtitle">{{ phase5.showcase_title2 }}</p>
            </div>
            <!-- 图片展示区 -->
            <div class="showcase-viewport">
              <div v-if="resolveImgList(phase5.showcase_images).length === 1" class="showcase-single" @click="openImagePreview(0, resolveImgList(phase5.showcase_images))">
                <img :src="resolveImgList(phase5.showcase_images)[0]" loading="lazy" />
              </div>
              <div v-else-if="resolveImgList(phase5.showcase_images).length > 1" class="showcase-scroll">
                <div v-for="(img, idx) in resolveImgList(phase5.showcase_images)" :key="idx" class="showcase-img-item" @click="openImagePreview(idx, resolveImgList(phase5.showcase_images))">
                  <img :src="img" loading="lazy" />
                </div>
              </div>
            </div>
            <!-- 底部文案 -->
            <div v-if="phase5.showcase_quote" class="showcase-quote">
              <blockquote>{{ phase5.showcase_quote }}</blockquote>
              <p v-if="phase5.showcase_quote_en" class="showcase-quote-en">{{ phase5.showcase_quote_en }}</p>
            </div>
            <el-empty v-if="!resolveImgList(phase5.showcase_images).length" description="暂无设计意向图内容" />
          </div>

          <!-- 空间效果图集 -->
          <div v-if="activeCategory === 'spaces'" class="phase-panel">
            <div v-if="spacesByName.length > 0" class="spaces-gallery">
              <div v-for="space in spacesByName" :key="space.name" class="space-group">
                <!-- 空间名称大字标题 -->
                <h3 class="space-name-title">{{ space.name }}</h3>
                <!-- 瀑布流杂志风格 -->
                <div class="spaces-masonry">
                  <div
                    v-for="(item, idx) in space.items"
                    :key="item.id || idx"
                    class="space-card"
                    @click="openImagePreview(0, space.items.map(i => resolveImgUrl(i)))"
                  >
                    <div class="space-img-wrap">
                      <img :src="resolveImgUrl(item)" loading="lazy" />
                      <div class="space-overlay">
                        <div class="space-overlay-content">
                          <p v-if="item.title" class="space-caption-title">{{ item.title }}</p>
                        </div>
                      </div>
                    </div>
                    <div v-if="item.description" class="space-desc-bar">
                      <p v-html="item.description"></p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-if="spacesByName.length === 0 && galleryList.length === 0" description="暂无空间效果图内容" />
            <!-- 兼容旧gallery -->
            <div v-if="spacesByName.length === 0 && galleryList.length > 0" class="gallery-fallback">
              <h3 class="space-name-title">图集</h3>
              <div class="spaces-masonry">
                <div v-for="(media, idx) in galleryList" :key="idx" class="space-card" @click="openImagePreview(idx)">
                  <div class="space-img-wrap">
                    <img :src="resolveImgUrl(media)" loading="lazy" />
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- VR 体验 -->
      <section class="vr-section" v-if="caseDetail.vr_link">
        <div class="container">
          <h2 class="section-title">360° 全景体验</h2>
          <div class="vr-card" @click="openVR">
            <img :src="caseDetail.cover_image" alt="VR预览">
            <div class="vr-overlay">
              <div class="vr-play-btn">
                <el-icon><VideoPlay /></el-icon>
              </div>
              <p>点击体验沉浸式 VR 全景</p>
            </div>
          </div>
        </div>
      </section>

     

      <!-- 施工进度（真实案例服务流程） -->
      <section class="workflow-progress-section" v-if="workflowProgress">
        <div class="container">
          <h2 class="section-title">施工进度</h2>
          
          <!-- 进度概览 -->
          <div class="progress-overview">
            <div class="progress-bar-wrapper">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: workflowProgress.progress_pct + '%' }"></div>
              </div>
              <span class="progress-percent">{{ workflowProgress.progress_pct }}%</span>
            </div>
            <p class="progress-current">
              当前阶段：<strong>{{ workflowProgress.current_phase || '待启动' }}</strong>
            </p>
          </div>
          
          <!-- 阶段进度条 -->
          <div class="phase-steps">
            <div
              v-for="(phase, idx) in workflowProgress.phases"
              :key="idx"
              class="phase-step"
              :class="phase.status"
            >
              <div class="phase-dot">
                <el-icon v-if="phase.status === 'completed'"><Check /></el-icon>
                <span v-else class="dot-inner"></span>
              </div>
              <div class="phase-line" v-if="idx < workflowProgress.phases.length - 1" :class="phase.status"></div>
              <div class="phase-info">
                <span class="phase-name">{{ phase.name }}</span>
                <span class="phase-detail">{{ phase.completed_nodes }}/{{ phase.total_nodes }}</span>
              </div>
            </div>
          </div>
          
          <!-- 工流时间轴（节点详情） -->
          <div class="workflow-nodes" v-if="workflowTimeline.length">
            <div class="nodes-by-phase" v-for="(nodes, phaseName) in groupedTimeline" :key="phaseName">
              <h4 class="phase-group-title">{{ phaseName }}</h4>
              <div class="node-list">
                <div
                  v-for="node in nodes"
                  :key="node.id"
                  class="workflow-node"
                  :class="node.status"
                >
                  <div class="node-status-dot"></div>
                  <div class="node-content">
                    <div class="node-header">
                      <span class="node-name">{{ node.node_name }}</span>
                      <span class="node-status-text">{{ getStatusText(node.status) }}</span>
                    </div>
                    <div class="node-photos" v-if="node.photos && node.photos.length">
                      <img
                        v-for="(url, idx) in node.photos.slice(0, 4)"
                        :key="idx"
                        :src="url"
                        @click="openImagePreview(0, node.photos)"
                      />
                    </div>
                    <div class="node-renderings" v-if="node.renderings && node.renderings.length">
                      <span class="rendering-label">效果图</span>
                      <img
                        v-for="(url, idx) in node.renderings.slice(0, 4)"
                        :key="idx"
                        :src="url"
                        @click="openImagePreview(0, node.renderings)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 施工时间轴（旧版） -->
      <section class="timeline-section" v-if="!workflowProgress && timelineList.length > 0">
        <div class="container">
          <h2 class="section-title">施工进程</h2>
          <div class="timeline">
            <div
              v-for="(node, index) in timelineList"
              :key="node.id || index"
              class="timeline-item"
              :class="{ active: index === 0 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-date">{{ formatDate(node.node_time) }}</span>
                <h4>{{ node.title }}</h4>
                <p>{{ node.content }}</p>
                <div v-if="node.media_urls" class="timeline-images">
                  <img
                    v-for="(url, idx) in parseMediaUrls(node.media_urls).slice(0, 3)"
                    :key="idx"
                    :src="url"
                    @click="openImagePreview(0, [url])"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 相关产品 -->
      <section class="products-section" v-if="relatedProducts.length > 0">
        <div class="container">
          <h2 class="section-title">使用产品</h2>
          <div class="products-grid">
            <div
              v-for="product in relatedProducts"
              :key="product.id"
              class="product-card"
              @click="goToProduct(product.id)"
            >
              <div class="product-image">
                <img :src="product.main_image || '/placeholder.png'" :alt="product.name">
              </div>
              <div class="product-info">
                <h4>{{ product.name }}</h4>
                <p class="product-brand">{{ product.brand }}</p>
                <span class="product-price">¥{{ product.sale_price }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部 CTA -->
      <section class="cta-section">
        <div class="container">
          <h2>喜欢这套设计？</h2>
          <p>预约设计师，获取专属方案</p>
          <div class="cta-buttons">
            <el-button type="primary" size="large" @click="showLeadForm = true">
              免费咨询
            </el-button>
            <el-button size="large" @click="handleSubscribe">
              <el-icon><Bell /></el-icon>
              {{ isSubscribed ? '已订阅' : '订阅更新' }}
            </el-button>
          </div>
        </div>
      </section>

      <!-- 更多案例（瀑布流） -->
      <section class="related-cases" v-if="relatedCases.length > 0">
        <div class="section-header">
          <h2 class="section-title">更多案例</h2>
          <p class="section-subtitle">同风格精选</p>
        </div>
        <div class="case-waterfall">
          <div
            v-for="caseItem in relatedCases"
            :key="caseItem.id"
            class="waterfall-card"
            @click="goToDetail(caseItem.id)"
          >
            <div class="wf-image-wrap">
              <img
                v-if="caseItem.cover_image"
                :src="caseItem.cover_image"
                :alt="caseItem.title"
                loading="lazy"
              >
              <div v-else class="wf-no-image" :style="{ background: getAtmosphereGradient(caseItem.atmosphere) }">
                <span>{{ caseItem.title }}</span>
              </div>
              <div class="wf-overlay">
                <div class="wf-atmosphere">{{ caseItem.atmosphere }}</div>
                <div class="wf-bottom">
                  <div class="wf-title">{{ caseItem.title }}</div>
                  <div class="wf-meta">
                    <span v-if="caseItem.house_type">{{ caseItem.house_type }}</span>
                    <span v-if="caseItem.area">{{ caseItem.area }}㎡</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部信息 -->
      <footer class="case-footer">
        <div class="container">
          <div class="footer-stats">
            <span><el-icon><View /></el-icon> {{ caseDetail.view_count || 0 }} 浏览</span>
            <span><el-icon><Star /></el-icon> {{ caseDetail.like_count || 0 }} 收藏</span>
            <span><el-icon><Bell /></el-icon> {{ caseDetail.subscription_count || 0 }} 订阅</span>
          </div>
          <p class="copyright">© D&B 帝标|设记家全案服务</p>
        </div>
      </footer>
    </div>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="imagePreview.visible"
      :url-list="imagePreview.list"
      :initial-index="imagePreview.index"
      @close="imagePreview.visible = false"
    />

    <!-- 报价详情弹窗 -->
    <el-dialog
      v-model="showQuoteDialog"
      title="造价分项报价"
      width="90%"
      max-width="700px"
      class="quote-dialog"
    >
      <div v-if="caseDetail?.quote_info" class="quote-detail-content">
        <div class="quote-total">
          <span class="quote-total-label">总造价</span>
          <span class="quote-total-value">¥{{ Number(caseDetail.quote_info.total_amount).toLocaleString() }} 元</span>
        </div>
        <div class="quote-breakdown" v-if="caseDetail.quote_info.items?.length">
          <div
            v-for="item in caseDetail.quote_info.items"
            :key="item.id || item.name"
            class="quote-item"
          >
            <span class="quote-item-name">{{ item.name || item.category }}</span>
            <span class="quote-item-amount">¥{{ Number(item.amount || 0).toLocaleString() }} 元</span>
          </div>
        </div>
        <el-empty v-else description="暂无报价明细" />
      </div>
    </el-dialog>


    <!-- 留资表单弹窗 -->
    <el-dialog
      v-model="showLeadForm"
      title="获取专属方案"
      width="90%"
      max-width="500px"
      class="lead-dialog"
    >
      <LeadForm
        :source-type="'case'"
        :source-id="caseDetail?.id"
        @success="onLeadSuccess"
      />
    </el-dialog>

    <!-- 订阅手机弹窗 -->
    <el-dialog
      v-model="showSubscribeDialog"
      title="订阅案例更新"
      width="90%"
      max-width="400px"
      class="subscribe-dialog"
    >
      <div class="subscribe-content">
        <p class="subscribe-tip">订阅「{{ caseDetail?.atmosphere || '该风格' }}」后，案例更新时将通过微信通知您</p>
        <el-input
          v-model="subscribePhone"
          placeholder="请输入手机号"
          type="tel"
          size="large"
          maxlength="11"
          @keyup.enter="doSubscribe"
        />
        <el-button
          type="primary"
          size="large"
          class="subscribe-btn"
          @click="doSubscribe"
          :disabled="!subscribePhone"
        >
          订阅「{{ caseDetail?.atmosphere || '该风格' }}」案例更新
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, ArrowDown, ArrowRight, Location, Star, Share,
  View, Bell, VideoPlay, ZoomIn, Check
} from '@element-plus/icons-vue'
import request from '@/api/request'
import LeadForm from '@/components/LeadForm.vue'

const route = useRoute()
const router = useRouter()

const goToDetail = (id) => {
  router.push(`/cases/${id}`)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const getAtmosphereGradient = (atm) => {
  const map = {
    '现代简约': 'linear-gradient(135deg,#667eea,#764ba2)',
    '新中式': 'linear-gradient(135deg,#f093fb,#f5576c)',
    '日式侧简': 'linear-gradient(135deg,#4facfe,#00f2fe)',
    '轻奔实用': 'linear-gradient(135deg,#43e97b,#38f9d7)',
    '法式奥山': 'linear-gradient(135deg,#fa709a,#fee140)',
    '工业风': 'linear-gradient(135deg,#a18cd1,#fbc2eb)',
    '山水居': 'linear-gradient(135deg,#ffecd2,#fcb69f)',
  }
  return map[atm] || 'linear-gradient(135deg,#8B5A2B,#D4A574)'
}

const loading = ref(false)
const caseDetail = ref(null)
const relatedCases = ref([])
const isLiked = ref(false)
const isSubscribed = ref(false)
const showLeadForm = ref(false)
const showSubscribeDialog = ref(false)
const subscribePhone = ref('')
const showFixedNav = ref(false)
const showQuoteDialog = ref(false)
const contentRef = ref(null)
const currentHeroIndex = ref(0)
const prevHeroIndex = ref(-1)
let heroCarouselTimer = null

// 轮播变化时记录上一张
watch(currentHeroIndex, (newIdx, oldIdx) => { prevHeroIndex.value = oldIdx })

// 图片预览
const imagePreview = ref({
  visible: false,
  list: [],
  index: 0
})

// 媒体列表 - 分离有描述和无描述的图片
const heroImages = computed(() => {
  const list = []
  if (caseDetail.value?.hero_images) {
    list.push(...caseDetail.value.hero_images.map(url => ({ url })))
  }
  return list
})

const galleryList = computed(() => {
  const list = []
  // 来自 case_media 表（含 description）
  if (caseDetail.value?.media) {
    list.push(...caseDetail.value.media.map(m => ({
      url: m.url,
      description: m.description || '',
      id: m.id
    })))
  }
  // 来自 gallery 字段
  if (caseDetail.value?.gallery) {
    caseDetail.value.gallery.forEach((url, i) => {
      // 避免与 media 重复
      if (!list.find(item => item.url === url)) {
        list.push({ url, description: '' })
      }
    })
  }
  return list
})

// 有描述的图片（杂志风格展示）
const describedImages = computed(() => {
  return galleryList.value.filter(m => m.description && m.description.trim())
})

// 无描述的图片（普通瀑布流）
const plainImages = computed(() => {
  return galleryList.value.filter(m => !m.description || !m.description.trim())
})

// 合并后的完整媒体列表（用于预览）
const mediaList = computed(() => {
  return [...heroImages.value, ...galleryList.value]
})

// 时间轴列表
const timelineList = computed(() => {
  return caseDetail.value?.timeline_nodes || []
})

// 工作流进度（真实案例）
const workflowProgress = computed(() => {
  return caseDetail.value?.workflow_progress || null
})

// 工作流时间轴节点
const workflowTimeline = computed(() => {
  return caseDetail.value?.workflow_timeline || []
})

// 按阶段分组的时间轴节点
const groupedTimeline = computed(() => {
  const groups = {}
  for (const node of workflowTimeline.value) {
    const phase = node.phase || '其他'
    if (!groups[phase]) groups[phase] = []
    groups[phase].push(node)
  }
  return groups
})

// 首字扩大3倍，杂志风格排版
const formatDropCap = (text) => {
  if (!text || text.length < 2) return text
  const firstChar = text.charAt(0)
  const rest = text.slice(1)
  return `<span class="drop-cap">${firstChar}</span>${rest}`
}

// 从图片提取主色（底色）
const extractColor = (event, item) => {
  const img = event.target
  if (!img) return
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  canvas.width = 50
  canvas.height = 50
  ctx.drawImage(img, 0, 0, 50, 50)
  try {
    const data = ctx.getImageData(25, 25, 1, 1).data
    const r = data[0], g = data[1], b = data[2]
    item.extractedColor = `rgb(${r},${g},${b})`
  } catch (e) {
    item.extractedColor = '#8B5A2B'
  }
}

// 在mediaList中查找图片索引
const findMediaIndex = (item) => {
  return galleryList.value.findIndex(m => m.url === item.url)
}

// 获取状态文本
const getStatusText = (status) => {
  const map = { pending: '待开始', ongoing: '进行中', completed: '已完成' }
  return map[status] || status
}

// 进度CSS类名
const getProgressClass = (wp) => {
  if (!wp) return ''
  if (wp.progress_pct >= 100) return 'completed'
  if (wp.progress_pct > 0) return 'ongoing'
  return 'pending'
}

// 相关产品
const relatedProducts = computed(() => {
  return caseDetail.value?.related_products || []
})

// 加载案例详情
const loadCaseDetail = async () => {
  loading.value = true
  try {
    const res = await request.get(`/public/cases/${route.params.id}`)
    caseDetail.value = res
    document.title = `${res.title} - D&B 帝标|设记家案例`
    checkSubscription()
    // 加载同风格相关案例
    loadRelatedCases(res.atmosphere, res.id)
  } catch (error) {
    ElMessage.error('加载案例详情失败')
  } finally {
    loading.value = false
  }
}

// 加载相关案例（同风格）
const loadRelatedCases = async (atmosphere, excludeId) => {
  try {
    const res = await request.get('/public/cases', {
      params: { atmosphere, page_size: 8, status: 'published' }
    })
    const list = res?.items || res || []
    relatedCases.value = list.filter(c => c.id !== excludeId).slice(0, 6)
  } catch (e) {
    // 静默失败
  }
}

// 检查订阅状态
const checkSubscription = async () => {
  try {
    const res = await request.get(`/public/cases/${route.params.id}/subscription-status`)
    isSubscribed.value = res?.is_subscribed || false
  } catch (e) {
    // 未登录时忽略错误
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 滚动到内容区
const scrollToContent = () => {
  contentRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// 处理滚动事件
const handleScroll = () => {
  const scrollY = window.scrollY
  showFixedNav.value = scrollY > window.innerHeight * 0.6
}

// 点赞
const handleLike = async () => {
  try {
    await request.post(`/cases/${caseDetail.value.id}/like`)
    isLiked.value = !isLiked.value
    caseDetail.value.like_count += isLiked.value ? 1 : -1
    ElMessage.success(isLiked.value ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 分享
const handleShare = () => {
  const shareData = {
    title: caseDetail.value.title,
    desc: caseDetail.value.design_concept?.slice(0, 50) + '...',
    link: window.location.href,
    imgUrl: caseDetail.value.cover_image
  }
  
  // 复制链接
  navigator.clipboard.writeText(window.location.href).then(() => {
    ElMessage.success('链接已复制，快去分享吧！')
  })
}

// 订阅
const handleSubscribe = async () => {
  if (!subscribePhone.value) {
    showSubscribeDialog.value = true
    return
  }
  // 输入手机号后直接订阅
  await doSubscribe()
}

const doSubscribe = async () => {
  try {
    const caseId = caseDetail.value.id
    if (isSubscribed.value) {
      await request.delete(`/cases/${caseId}/subscribe`)
      isSubscribed.value = false
      ElMessage.success('已取消订阅')
    } else {
      await request.post(`/cases/${caseId}/subscribe`, { phone: subscribePhone.value })
      isSubscribed.value = true
      ElMessage.success('订阅成功，案例更新将通过微信通知您')
    }
    showSubscribeDialog.value = false
    subscribePhone.value = ''
  } catch (error) {
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 打开报价预览
const openQuotePreview = () => {
  if (caseDetail.value?.is_real_case && caseDetail.value?.quote_id) {
    window.open(`/quotes/${caseDetail.value.quote_id}`, '_blank')
  } else if (caseDetail.value?.quote_info) {
    showQuoteDialog.value = true
  }
}

// 打开图片预览
const openImagePreview = (index, list = null) => {
  imagePreview.value.list = list || mediaList.value.map(m => m.url || m.file_url)
  imagePreview.value.index = index
  imagePreview.value.visible = true
}

// 打开 VR
const openVR = () => {
  if (caseDetail.value?.vr_link) {
    window.open(caseDetail.value.vr_link, '_blank')
  }
}

// 跳转到产品
const goToProduct = (id) => {
  router.push(`/products/${id}`)
}

// 留资成功
const onLeadSuccess = () => {
  showLeadForm.value = false
  ElMessage.success('提交成功，我们将尽快联系您')
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0'
  return parseFloat(price).toLocaleString('zh-CN')
}

// 格式化万元
const formatWan = (value) => {
  if (!value) return '-'
  const wan = Number(value) / 10000
  return wan >= 1 ? `${wan.toFixed(1)}万` : `${Number(value).toLocaleString()}元`
}

// 轮播控制
const goToHero = (idx) => {
  prevHeroIndex.value = currentHeroIndex.value
  currentHeroIndex.value = idx
}
const prevHero = () => goToHero((currentHeroIndex.value - 1 + heroImages.value.length) % heroImages.value.length)
const nextHero = () => goToHero((currentHeroIndex.value + 1) % heroImages.value.length)

// 分类Tab导航
const activeCategory = ref('mood')
const categories = [
  { key: 'mood', label: '设计意境' },
  { key: 'layout', label: '户型分析' },
  { key: 'plan', label: '户型规划' },
  { key: 'birdview', label: '鸟瞰图展示' },
  { key: 'showcase', label: '设计意向图' },
  { key: 'spaces', label: '空间效果图' },
]

// 安全解析JSON图片字段（空字符串/null返回空数组）
const parseImgField = (val) => {
  if (!val || val === '') return []
  if (Array.isArray(val)) return val
  try { const r = JSON.parse(val); return Array.isArray(r) ? r : [] } catch { return [] }
}

// 提取图片URL：对象 {url:'...'} → 字符串，字符串原样返回
const resolveImgUrl = (img) => {
  if (!img) return ''
  if (typeof img === 'string') return img
  if (img && img.url) return img.url
  if (img && img.image_url) return img.image_url
  if (img && img.rendering_url) return img.rendering_url
  return ''
}

// 解析图片字段并提取为纯URL字符串数组（兼容对象数组和字符串数组）
const resolveImgList = (arr) => {
  if (!arr || !Array.isArray(arr)) return []
  return arr.map(item => resolveImgUrl(item)).filter(u => u)
}
// 6阶段数据（来自后端phases字典或数组，过滤null）
const phases = computed(() => {
  const p = caseDetail.value?.phases
  if (!p) return []
  const arr = Array.isArray(p) ? p : Object.values(p)
  return arr.filter(Boolean).map(ph => ({
    ...ph,
    layout_images: parseImgField(ph.layout_images),
    mood_images: parseImgField(ph.mood_images),
    birdview_images: parseImgField(ph.birdview_images),
    showcase_images: parseImgField(ph.showcase_images),
  }))
})
const getPhase = (n) => phases.value.find(p => p.phase_number === n) || {}
const phase1 = computed(() => getPhase(1))
const phase2 = computed(() => getPhase(2))
const phase3 = computed(() => getPhase(3))
const phase4 = computed(() => getPhase(4))
const phase5 = computed(() => getPhase(5))
const phase6 = computed(() => getPhase(6))

// 空间效果图（来自后端spaces数组，按空间名分组）
const spaces = computed(() => caseDetail.value?.spaces || [])
const spacesByName = computed(() => {
  const groups = {}
  for (const s of spaces.value) {
    const name = s.space_name || '其他空间'
    if (!groups[name]) groups[name] = { name, items: [] }
    const items = s.renderings || []
    groups[name].items.push(...items)
  }
  return Object.values(groups).map(g => ({
    ...g,
    itemsWithDesc: g.items.filter(i => i.description || i.title),
    itemsNoDesc: g.items.filter(i => !i.description && !i.title),
  }))
})

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 解析媒体URL
const parseMediaUrls = (urls) => {
  if (!urls) return []
  if (typeof urls === 'string') {
    try {
      return JSON.parse(urls)
    } catch {
      return urls.split(',').map(u => u.trim())
    }
  }
  return urls
}

const startHeroCarousel = () => {
  if (heroCarouselTimer) clearInterval(heroCarouselTimer)
  if (heroImages.value.length > 1) {
    heroCarouselTimer = setInterval(() => {
      prevHeroIndex.value = currentHeroIndex.value
      currentHeroIndex.value = (currentHeroIndex.value + 1) % heroImages.value.length
    }, 4000)
  }
}

onMounted(() => {
  loadCaseDetail().then(() => {
    startHeroCarousel()
  })
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (heroCarouselTimer) clearInterval(heroCarouselTimer)
})
</script>

<style scoped>
.case-detail-v2 {
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
}

/* 固定导航栏 */
.fixed-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(20px);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}

.fixed-nav.visible {
  transform: translateY(0);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn,
.nav-icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.back-btn:hover,
.nav-icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-title {
  font-size: 16px;
  font-weight: 500;
}

.nav-right {
  display: flex;
  gap: 12px;
}

.nav-icon-btn .active {
  color: #ffd700;
}

/* Hero 轮播样式 */
.hero-carousel {
  position: absolute;
  inset: 0;
}
.hero-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 1.2s ease-in-out;
}
.hero-slide.active {
  opacity: 1;
  z-index: 1;
}
.hero-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: kenBurns 12s ease-in-out infinite alternate;
}
@keyframes kenBurns {
  from { transform: scale(1.0); }
  to { transform: scale(1.12); }
}
.carousel-indicators {
  position: absolute;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}
.carousel-indicators .indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  cursor: pointer;
  transition: all 0.3s;
}
.carousel-indicators .indicator.active {
  background: #fff;
  width: 24px;
  border-radius: 4px;
}
.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.4);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  backdrop-filter: blur(8px);
}
.carousel-arrow:hover { background: rgba(0,0,0,0.65); }
.carousel-arrow.left { left: 20px; }
.carousel-arrow.right { right: 20px; }
.carousel-arrow .el-icon { font-size: 20px; }

.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Hero 全屏区域 */
.hero-section {
  position: relative;
  height: 100vh;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}
.hero-carousel {
  position: absolute;
  inset: 0;
}
.hero-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 1.2s ease-in-out;
}
.hero-slide.active {
  opacity: 1;
  z-index: 1;
}
.hero-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: kenBurns 12s ease-in-out infinite alternate;
  animation-delay: inherit;
}
.hero-slide.active img {
  animation-name: kenBurns;
}
.hero-slide:not(.active) img {
  animation: none;
}
@keyframes kenBurns {
  from { transform: scale(1.0); }
  to { transform: scale(1.12); }
}
.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.4);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  backdrop-filter: blur(8px);
}
.carousel-arrow:hover { background: rgba(0,0,0,0.65); }
.carousel-arrow.left { left: 20px; }
.carousel-arrow.right { right: 20px; }
.carousel-arrow .el-icon { font-size: 20px; }


.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(10, 10, 10, 1) 0%,
    rgba(10, 10, 10, 0.7) 40%,
    rgba(10, 10, 10, 0.3) 70%,
    rgba(10, 10, 10, 0.1) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: 60px 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.back-float {
  position: absolute;
  top: 40px;
  left: 20px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 20px;
}

.back-float:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.hero-text {
  margin-bottom: 40px;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.featured-badge {
  padding: 6px 16px;
  background: linear-gradient(135deg, #8B5A2B 0%, #a67c52 100%);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.case-title {
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.case-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 24px;
  font-weight: 300;
}

.case-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.tag.highlight {
  background: rgba(139, 90, 43, 0.3);
  border-color: rgba(139, 90, 43, 0.5);
  color: #d4a574;
}

.tag.workflow-tag {
  background: rgba(230, 162, 60, 0.15);
  border-color: rgba(230, 162, 60, 0.3);
  color: #E6A23C;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.tag-dot.completed { background: #67C23A; }
.tag-dot.ongoing { background: #E6A23C; animation: pulse-dot 2s infinite; }
.tag-dot.pending { background: #999; }

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.scroll-arrow {
  font-size: 20px;
}

/* 项目概览 */
.overview-section {
  padding: 60px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 30px;
}

.overview-item {
  text-align: center;
}

.overview-item .label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.overview-item .value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #fff;
}

.overview-item .value.price {
  color: #d4a574;
  font-size: 28px;
}


.section-title {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 600;
  margin: 0 0 30px;
  text-align: center;
}

.concept-text {
  font-size: 18px;
  line-height: 2;
  color: rgba(255, 255, 255, 0.8);
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  font-weight: 300;
}

/* 分类Tab导航 */
.category-tabs-section {
  padding: 0;
  background: var(--bg-primary, #0d0d0d);
  position: sticky;
  top: 60px;
  z-index: 90;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.category-tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding: 0 0 4px;
  scrollbar-width: none;
}
.category-tabs::-webkit-scrollbar { display: none; }

.category-tab {
  flex-shrink: 0;
  padding: 10px 18px;
  border: none;
  background: transparent;
  color: rgba(255,255,255,0.45);
  font-size: 14px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.25s;
  font-family: inherit;
  white-space: nowrap;
}
.category-tab:hover {
  color: rgba(255,255,255,0.75);
  background: rgba(255,255,255,0.05);
}
.category-tab.active {
  color: #8B5A2B;
  background: rgba(139,90,43,0.12);
  font-weight: 600;
}

/* 6阶段内容区 */
.phase-content-section {
  padding: 60px 0;
}
.phase-panel {
  animation: fadeInUp 0.3s ease;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.phase-heading {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 16px;
}
.phase-body {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255,255,255,0.7);
}
/* 富文本内容样式重置 */
.phase-body.rich-text :deep(p) {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255,255,255,0.75);
}
.phase-body.rich-text :deep(strong) {
  color: #fff;
  font-weight: 600;
}
.phase-body.rich-text :deep(span) {
  color: inherit;
}
.phase-body.rich-text :deep(br) {
  display: block;
  content: '';
  margin-top: 4px;
}
.phase-text-block {
  margin-top: 32px;
}

/* ========== 户型分析：左文案 + 右图片（杂志风格）========== */
.layout-analysis-section {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.layout-left {
  flex: 1;
  min-width: 0;
}
.layout-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 20px;
  letter-spacing: 2px;
}
.layout-analysis-content {
  font-size: 14px;
  line-height: 2;
  color: rgba(255,255,255,0.8);
}
.layout-analysis-content :deep(p) {
  margin: 0 0 14px;
}
.layout-analysis-content :deep(strong) {
  color: #fff;
  font-weight: 600;
}
.layout-right {
  flex: 1.1;
  min-width: 0;
}
.layout-floorplan-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
}
.layout-floorplan-card img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.5s ease;
}
.layout-floorplan-card:hover img {
  transform: scale(1.03);
}
.layout-floorplan-card .img-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.layout-floorplan-card:hover .img-overlay {
  opacity: 1;
}

/* 响应式：移动端上下堆叠 */
@media (max-width: 768px) {
  .layout-analysis-section {
    flex-direction: column;
    gap: 24px;
  }
  .layout-right {
    order: -1; /* 图片在上 */
  }
}
.phase-images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.phase-img-card {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 4/3;
}
.phase-img-card img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s;
}
.phase-img-card:hover img { transform: scale(1.05); }
.img-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.25s;
}
.phase-img-card:hover .img-overlay { opacity: 1; }
.img-overlay .el-icon { font-size: 28px; color: #fff; }

/* 鸟瞰图展示：上下垂直排列，完整展示 */
.phase-birdview-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
}
.phase-birdview-item {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
}
.phase-birdview-item img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.4s;
}
.phase-birdview-item:hover img { transform: scale(1.02); }

/* 户型规划：上图下文，上下排列，宽对齐 */
.phase-plan-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}
.plan-image-wrap {
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
}
.plan-image-wrap img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.4s;
}
.plan-image-wrap:hover img {
  transform: scale(1.03);
}
.plan-text-block {
  width: 100%;
}
.phase-single-img {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
}
.phase-single-img img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s;
}
.phase-single-img:hover img { transform: scale(1.04); }

/* 设计意境 杂志风格 */
.phase-magazine-layout {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.phase-magazine-layout .magazine-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
.phase-magazine-layout .magazine-card.large {
  grid-column: span 2;
}
.phase-magazine-layout .mag-img-wrap {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4/3;
}
.phase-magazine-layout .magazine-card.large .mag-img-wrap {
  aspect-ratio: 16/9;
}
.phase-magazine-layout .mag-img-wrap img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.5s;
}
.phase-magazine-layout .magazine-card:hover img { transform: scale(1.05); }
.phase-magazine-layout .mag-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.25s;
}
.phase-magazine-layout .magazine-card:hover .mag-overlay { opacity: 1; }
.phase-magazine-layout .mag-caption {
  background: rgba(0,0,0,0.75);
  padding: 14px 16px;
}
.phase-magazine-layout .mag-caption .mag-text {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255,255,255,0.85);
}

/* 效果图首页 */
.showcase-header {
  text-align: center;
  margin-bottom: 28px;
}
.showcase-header h3 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 10px;
  letter-spacing: 0.06em;
}
.showcase-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.4);
  margin: 0;
  letter-spacing: 0.12em;
}

/* 设计意向图展示区 */
.showcase-viewport {
  width: 100%;
  height: 700px;
  overflow: hidden;
  border-radius: 12px;
  background: #0a0a0a;
}
.showcase-single {
  width: 100%;
  height: 700px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.showcase-single img {
  max-width: 100%;
  max-height: 700px;
  object-fit: contain;
}
.showcase-scroll {
  display: flex;
  height: 700px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  gap: 0;
  /* 隐藏滚动条但保留功能 */
  scrollbar-width: none;
}
.showcase-scroll::-webkit-scrollbar { display: none; }
.showcase-img-item {
  flex-shrink: 0;
  height: 700px;
  cursor: pointer;
  position: relative;
}
.showcase-img-item img {
  height: 100%;
  width: auto;
  display: block;
}
/* 底部文案引用 */
.showcase-quote {
  margin-top: 32px;
  padding: 20px 28px;
  border-left: 3px solid rgba(139,90,43,0.6);
  background: rgba(255,255,255,0.03);
  border-radius: 0 8px 8px 0;
}
.showcase-quote blockquote {
  font-size: 15px;
  color: rgba(255,255,255,0.75);
  margin: 0 0 8px;
  line-height: 1.8;
  font-style: italic;
}
.showcase-quote-en {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  margin: 0;
  font-style: italic;
  letter-spacing: 0.05em;
}

/* 空间效果图集 - 瀑布流杂志风格 */
.spaces-gallery { display: flex; flex-direction: column; gap: 48px; }

.space-name-title {
  font-size: 72px !important;
  font-weight: 700 !important;
  color: #8B5A2B !important;
  margin: 0 0 24px !important;
  padding-bottom: 0 !important;
  border: none !important;
  letter-spacing: -0.02em;
  line-height: 1;
  text-transform: uppercase;
  font-style: normal !important;
}

/* CSS 瀑布流：column-count 多列布局 */
.spaces-masonry {
  columns: 3 280px;
  column-gap: 16px;
}

.space-card {
  break-inside: avoid;
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
}

.space-img-wrap {
  position: relative;
  overflow: hidden;
}

.space-img-wrap img {
  width: 100%;
  display: block;
  transition: transform 0.6s ease;
}

.space-card:hover .space-img-wrap img {
  transform: scale(1.04);
}

/* 悬浮信息层 */
.space-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 60%);
  display: flex;
  align-items: flex-end;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.space-card:hover .space-overlay {
  opacity: 1;
}

.space-overlay-content {
  padding: 16px 14px;
  width: 100%;
}

.space-caption-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin: 0;
  line-height: 1.4;
}

/* 简介文字常驻在图片下方 */
.space-desc-bar {
  background: #111;
  padding: 10px 12px;
}

.space-desc-bar p {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  margin: 0;
  line-height: 1.6;
}

.gallery-fallback {
  margin-top: 32px;
}

/* 兼容旧 gallery-item */
.gallery-masonry {
  columns: 3 280px;
  column-gap: 16px;
}
.gallery-item {
  break-inside: avoid;
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  aspect-ratio: 1;
}
.gallery-item.large { grid-column: span 2; grid-row: span 2; }
.gallery-item.wide { grid-column: span 2; }
.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}
.gallery-item:hover img { transform: scale(1.05); }
.item-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.gallery-item:hover .item-overlay { opacity: 1; }
.item-overlay .el-icon { font-size: 32px; color: #fff; }

/* VR 区域 */
.vr-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.vr-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 21/9;
}

.vr-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.vr-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  transition: background 0.3s;
}

.vr-card:hover .vr-overlay {
  background: rgba(0, 0, 0, 0.4);
}

.vr-play-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #8B5A2B;
  transition: transform 0.3s;
}

.vr-card:hover .vr-play-btn {
  transform: scale(1.1);
}

.vr-overlay p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}


.highlights-content {
  max-width: 800px;
  margin: 0 auto;
}

.highlights-content p {
  font-size: 16px;
  line-height: 2;
  color: rgba(255, 255, 255, 0.8);
}

/* 时间轴 */
.timeline-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 施工进度（真实案例工作流） */
.workflow-progress-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-overview {
  max-width: 600px;
  margin: 0 auto 40px;
  text-align: center;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8B5A2B, #d4a574);
  border-radius: 4px;
  transition: width 0.6s ease;
}

.progress-percent {
  font-size: 24px;
  font-weight: 700;
  color: #d4a574;
  min-width: 60px;
}

.progress-current {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.progress-current strong {
  color: #fff;
}

/* 阶段进度条 */
.phase-steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  margin-bottom: 60px;
  padding: 0 20px;
  overflow-x: auto;
}

.phase-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 100px;
  max-width: 180px;
}

.phase-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  z-index: 1;
  background: rgba(255, 255, 255, 0.1);
  color: #999;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.phase-step.completed .phase-dot {
  background: #8B5A2B;
  border-color: #8B5A2B;
  color: #fff;
}

.phase-step.ongoing .phase-dot {
  background: transparent;
  border-color: #E6A23C;
  color: #E6A23C;
}

.phase-step.ongoing .dot-inner {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #E6A23C;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.phase-line {
  position: absolute;
  top: 18px;
  left: calc(50% + 18px);
  right: calc(-50% + 18px);
  height: 2px;
  background: rgba(255, 255, 255, 0.15);
}

.phase-line.completed {
  background: #8B5A2B;
}

.phase-info {
  margin-top: 12px;
  text-align: center;
}

.phase-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.phase-detail {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* 工作流节点详情 */
.workflow-nodes {
  max-width: 800px;
  margin: 0 auto;
}

.phase-group-title {
  font-size: 18px;
  font-weight: 600;
  color: #d4a574;
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(139, 90, 43, 0.3);
}

.workflow-node {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  position: relative;
}

.workflow-node:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 36px;
  bottom: -16px;
  width: 2px;
  background: rgba(255, 255, 255, 0.08);
}

.node-status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.workflow-node.pending .node-status-dot {
  background: rgba(255, 255, 255, 0.2);
}

.workflow-node.ongoing .node-status-dot {
  background: #E6A23C;
  box-shadow: 0 0 0 4px rgba(230, 162, 60, 0.2);
}

.workflow-node.completed .node-status-dot {
  background: #67C23A;
}

.node-content {
  flex: 1;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.node-name {
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.node-status-text {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.workflow-node.pending .node-status-text {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.4);
}

.workflow-node.ongoing .node-status-text {
  background: rgba(230, 162, 60, 0.15);
  color: #E6A23C;
}

.workflow-node.completed .node-status-text {
  background: rgba(103, 194, 58, 0.15);
  color: #67C23A;
}

.node-photos,
.node-renderings {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.node-photos img,
.node-renderings img {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
}

.node-photos img:hover,
.node-renderings img:hover {
  transform: scale(1.08);
}

.rendering-label {
  display: none;
}

.timeline {
  max-width: 800px;
  margin: 0 auto;
}

.timeline-item {
  display: flex;
  gap: 24px;
  padding: 24px 0;
  position: relative;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 48px;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  margin-top: 6px;
}

.timeline-item.active .timeline-dot {
  background: #8B5A2B;
  box-shadow: 0 0 0 4px rgba(139, 90, 43, 0.3);
}

.timeline-content {
  flex: 1;
}

.timeline-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.timeline-content h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 8px 0;
}

.timeline-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin: 0;
}

.timeline-images {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.timeline-images img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
}

/* 相关产品 */
.products-section {
  padding: 80px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.product-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, background 0.3s;
}

.product-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
}

.product-image {
  aspect-ratio: 1;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-info {
  padding: 16px;
}

.product-info h4 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-brand {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 8px;
}

.product-price {
  font-size: 16px;
  font-weight: 600;
  color: #d4a574;
}

/* CTA 区域 */
.cta-section {
  padding: 100px 0;
  text-align: center;
  background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
}

.cta-section h2 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 12px;
}

.cta-section p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 32px;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.cta-buttons .el-button--primary {
  background: #8B5A2B;
  border-color: #8B5A2B;
  padding: 16px 40px;
  font-size: 16px;
}

.cta-buttons .el-button--primary:hover {
  background: #a67c52;
  border-color: #a67c52;
}

/* 底部 */
.case-footer {
  padding: 40px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.footer-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-stats span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.copyright {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

/* 加载状态 */
.loading-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* 响应式 */
@media (max-width: 768px) {
  .gallery-masonry {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .gallery-item.large,
  .gallery-item.wide {
    grid-column: span 2;
    grid-row: span 1;
  }
  
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hero-content {
    padding: 40px 16px 30px;
  }
  
  .case-title {
    font-size: 28px;
  }
  
  .back-float {
    top: 20px;
    left: 16px;
    width: 40px;
    height: 40px;
  }
}

/* 订阅弹窗 */
.subscribe-content {
  padding: 20px 10px;
}

.subscribe-tip {
  margin-bottom: 20px;
  color: #666;
  text-align: center;
}

.subscribe-btn {
  width: 100%;
  margin-top: 20px;
}

/* 杂志风格画廊 */
.magazine-gallery {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.magazine-card {
  background: var(--img-color, #8B5A2B);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.magazine-card:hover {
  transform: translateY(-4px);
}

.mag-img-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
}

.mag-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.magazine-card:hover .mag-overlay {
  opacity: 1;
}

.mag-overlay .el-icon {
  font-size: 32px;
  color: #fff;
}

.mag-caption {
  padding: 12px;
  background: var(--img-color, #8B5A2B);
  color: #fff;
  font-size: 14px;
  line-height: 1.6;
}

.mag-text {
  margin: 0;
}

.mag-text :deep(.drop-cap) {
  float: left;
  font-size: 3em;
  line-height: 1;
  margin-right: 0.1em;
  color: #fff;
}

/* ── 更多案例瀑布流 ── */
.related-cases {
  padding: 60px 0 0;
  background: #f0ede8;
}

.related-cases .section-header {
  padding: 0 60px 32px;
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.related-cases .section-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: 2px;
  margin: 0;
}

.related-cases .section-subtitle {
  font-size: 14px;
  color: #999;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin: 0;
}

/* 共用瀑布流样式 */
.case-waterfall {
  columns: 3;
  column-gap: 6px;
  padding: 0 60px 80px;
}

@media (max-width: 1200px) {
  .case-waterfall { columns: 2; padding: 0 24px 60px; }
  .related-cases .section-header { padding: 0 24px 24px; }
}
@media (max-width: 640px) {
  .case-waterfall { columns: 1; padding: 0 12px 40px; }
  .related-cases .section-header { padding: 0 12px 20px; }
}

.waterfall-card {
  break-inside: avoid;
  margin-bottom: 6px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  display: block;
}

.wf-image-wrap {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.wf-image-wrap img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.waterfall-card:hover .wf-image-wrap img {
  transform: scale(1.04);
}

.wf-no-image {
  width: 100%;
  aspect-ratio: 3/4;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.7);
  font-size: 16px;
  letter-spacing: 2px;
}

.wf-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(
    to bottom,
    rgba(0,0,0,0.45) 0%,
    transparent 35%,
    transparent 50%,
    rgba(0,0,0,0.72) 100%
  );
  transition: background 0.4s ease;
}

.waterfall-card:hover .wf-overlay {
  background: linear-gradient(
    to bottom,
    rgba(0,0,0,0.55) 0%,
    transparent 30%,
    transparent 45%,
    rgba(0,0,0,0.85) 100%
  );
}

.wf-atmosphere {
  align-self: flex-start;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.92);
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.3);
  padding: 5px 12px;
  border-radius: 2px;
}

.wf-bottom {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.wf-title {
  font-size: clamp(22px, 3.5vw, 38px);
  font-weight: 700;
  color: #fff;
  line-height: 1.15;
  letter-spacing: 1px;
  text-shadow: 0 2px 12px rgba(0,0,0,0.5);
  word-break: break-all;
}

.wf-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.wf-meta span {
  font-size: 12px;
  color: rgba(255,255,255,0.8);
  letter-spacing: 1px;
  background: rgba(255,255,255,0.12);
  padding: 3px 8px;
  border-radius: 2px;
}
</style>

