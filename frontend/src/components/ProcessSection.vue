<template>
  <div class="process-section">
    <!-- Loading State -->
    <div v-if="loading" class="holo-loading">
      <div class="holo-loader"></div>
      <span>加载服务流程...</span>
    </div>

    <!-- Overview Mode: Phase Spheres -->
    <div v-else-if="!detailMode" class="holo-dome">
      <!-- Progress Bar -->
      <div class="process-progress-bar">
        <div class="progress-track">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercentage + '%', background: 'linear-gradient(90deg, #8B7355, #C4A77D)' }"
          ></div>
        </div>
        <div class="progress-labels">
          <span class="progress-text">服务进度</span>
          <span class="progress-percentage">{{ progressPercentage }}%</span>
        </div>
      </div>

      <!-- Phase Spheres -->
      <div class="holo-spheres">
        <div
          v-for="(phase, idx) in phases"
          :key="phase.code"
          class="holo-sphere-wrap"
          @click="enterPhase(phase)"
          @mouseenter="hoveredPhase = phase.code"
          @mouseleave="hoveredPhase = null"
        >
          <div 
            class="holo-sphere" 
            :class="{ 'sphere-active': hoveredPhase === phase.code }"
            :style="{ '--phase-color': phase.color || '#8B7355' }"
          >
            <div class="sphere-ring ring-outer"></div>
            <div class="sphere-ring ring-middle"></div>
            <div class="sphere-ring ring-inner"></div>
            <div class="sphere-core">
              <div class="sphere-phase-icon">{{ getPhaseIcon(phase.code) }}</div>
              <div class="sphere-phase-name">{{ phase.name }}</div>
              <div class="sphere-node-count">{{ phase.nodes?.length || 0 }}节点</div>
            </div>
            <!-- Hover Tooltip -->
            <div v-if="hoveredPhase === phase.code" class="sphere-tooltip">
              <div class="tooltip-title">{{ phase.name }}</div>
              <div class="tooltip-desc">{{ getPhaseDescription(phase.code) }}</div>
              <div class="tooltip-hint">点击进入查看详情 →</div>
            </div>
          </div>
          <!-- Arrow -->
          <div v-if="idx < phases.length - 1" class="holo-arrow">
            <div class="arrow-body">
              <div class="arrow-flow"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Interactive Hint -->
      <div class="interactive-hint">
        <span class="hint-icon">👆</span>
        <span class="hint-text">点击任意阶段球体，探索服务详情</span>
      </div>
    </div>

    <!-- Detail Mode: Phase Detail View -->
    <div v-else class="phase-detail-view">
      <!-- Back Button -->
      <div class="detail-header">
        <button class="back-btn" @click="exitPhase">
          <span class="back-arrow">←</span>
          <span>返回流程总览</span>
        </button>
        <div class="detail-phase-info">
          <span class="detail-phase-icon">{{ getPhaseIcon(selectedPhase?.code) }}</span>
          <h3 class="detail-phase-name">{{ selectedPhase?.name }}</h3>
          <span class="detail-node-count">{{ selectedPhase?.nodes?.length || 0 }}个服务节点</span>
        </div>
      </div>

      <!-- Node Cards Grid -->
      <div class="nodes-grid">
        <div 
          v-for="(node, nodeIdx) in selectedPhase?.nodes" 
          :key="node.code"
          class="node-card"
          :class="{ 'node-completed': completedNodes.has(node.code) }"
          @click="toggleNodeComplete(node.code)"
        >
          <div class="node-card-header">
            <span class="node-code-badge">{{ node.code }}</span>
            <button 
              class="node-info-btn" 
              @click.stop="showNodeDetail(node)"
              title="查看详情"
            >
              ℹ️
            </button>
          </div>
          <div class="node-card-body">
            <h4 class="node-card-title">{{ node.name }}</h4>
            <p class="node-card-desc">{{ getNodeDescription(node.code) }}</p>
          </div>
          <div class="node-card-footer">
            <span class="node-duration">⏱️ {{ getNodeDuration(node.code) }}</span>
            <span class="node-status">
              <span v-if="completedNodes.has(node.code)" class="status-done">✓ 已完成</span>
              <span v-else class="status-pending">待完成</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Node Detail Modal -->
    <div v-if="showingNodeDetail" class="node-detail-modal" @click.self="closeNodeDetail">
      <div class="modal-content">
        <button class="modal-close" @click="closeNodeDetail">✕</button>
        <div class="modal-header" :style="{ borderColor: selectedPhase?.color || '#8B7355' }">
          <span class="modal-node-code">{{ detailingNode?.code }}</span>
          <h3 class="modal-node-name">{{ detailingNode?.name }}</h3>
        </div>
        <div class="modal-body">
          <div class="modal-section">
            <h4>节点说明</h4>
            <p>{{ getNodeDescription(detailingNode?.code) }}</p>
          </div>
          <div class="modal-section">
            <h4>预计时长</h4>
            <p>{{ getNodeDuration(detailingNode?.code) }}</p>
          </div>
          <div class="modal-section">
            <h4>关键交付物</h4>
            <ul>
              <li v-for="(deliverable, di) in getNodeDeliverables(detailingNode?.code)" :key="di">
                {{ deliverable }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  phases: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// State
const detailMode = ref(false)
const selectedPhase = ref(null)
const hoveredPhase = ref(null)
const completedNodes = ref(new Set())
const showingNodeDetail = ref(false)
const detailingNode = ref(null)

// Computed
const progressPercentage = computed(() => {
  if (!props.phases || props.phases.length === 0) return 0
  const totalNodes = props.phases.reduce((sum, phase) => sum + (phase.nodes?.length || 0), 0)
  if (totalNodes === 0) return 0
  return Math.round((completedNodes.value.size / totalNodes) * 100)
})

// Methods
const getPhaseIcon = (code) => {
  const iconMap = {
    'PHASE_01': '🎯',
    'PHASE_02': '🎨',
    'PHASE_03': '🏗️',
    'PHASE_04': '🔧',
    'PHASE_05': '✨',
    'PHASE_06': '🎉'
  }
  return iconMap[code] || '📋'
}

const getPhaseDescription = (code) => {
  const descMap = {
    'PHASE_01': '深入了解您的需求，明确设计方向',
    'PHASE_02': '将想法变为可视化的设计方案',
    'PHASE_03': '精选环保材料，确保品质',
    'PHASE_04': '专业施工团队，精细工艺',
    'PHASE_05': '完善细节，追求完美',
    'PHASE_06': '交付您的梦想之家'
  }
  return descMap[code] || '专业服务阶段'
}

const getNodeDescription = (code) => {
  const descMap = {
    'N001': '深入了解您的生活习惯、喜好和需求',
    'N002': '实地测量房屋尺寸，记录现状',
    'N003': '根据需求和预算制定设计方案',
    'N004': '提供3D效果图，直观展示设计效果',
    'N005': '根据反馈调整方案，直到满意',
    'N006': '签订装修合同，明确双方权益'
  }
  return descMap[code] || '专业的服务节点，确保品质交付'
}

const getNodeDuration = (code) => {
  const durationMap = {
    'N001': '1-2天',
    'N002': '1天',
    'N003': '3-5天',
    'N004': '5-7天',
    'N005': '2-3天',
    'N006': '1天'
  }
  return durationMap[code] || '视具体情况而定'
}

const getNodeDeliverables = (code) => {
  const deliverablesMap = {
    'N001': ['需求分析表', '生活方式问卷'],
    'N002': ['房屋测量图', '现状照片集'],
    'N003': ['平面布置图', '材料清单', '预算报价'],
    'N004': ['3D效果图', 'VR全景图'],
    'N005': ['最终设计方案', '施工图纸'],
    'N006': ['装修合同', '施工时间表']
  }
  return deliverablesMap[code] || ['专业服务交付物']
}

const enterPhase = (phase) => {
  selectedPhase.value = phase
  detailMode.value = true
}

const exitPhase = () => {
  detailMode.value = false
  selectedPhase.value = null
}

const toggleNodeComplete = (nodeCode) => {
  const newSet = new Set(completedNodes.value)
  if (newSet.has(nodeCode)) {
    newSet.delete(nodeCode)
  } else {
    newSet.add(nodeCode)
  }
  completedNodes.value = newSet
}

const showNodeDetail = (node) => {
  detailingNode.value = node
  showingNodeDetail.value = true
}

const closeNodeDetail = () => {
  showingNodeDetail.value = false
  detailingNode.value = null
}
</script>

<style scoped>
.process-section {
  position: relative;
  z-index: 2;
}

/* Loading */
.holo-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.holo-loader {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(139, 115, 85, 0.3);
  border-top-color: #8B7355;
  border-radius: 50%;
  animation: holo-spin 1s linear infinite;
}

@keyframes holo-spin {
  to { transform: rotate(360deg); }
}

/* Progress Bar */
.process-progress-bar {
  max-width: 600px;
  margin: 0 auto 40px;
  padding: 0 20px;
}

.progress-track {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* Holo Dome */
.holo-dome {
  padding: 20px 0;
}

.holo-spheres {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
  padding: 20px 0;
}

.holo-sphere-wrap {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.holo-sphere {
  --phase-color: #8B7355;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s ease;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1), transparent 70%);
  box-shadow: 0 0 30px rgba(139, 115, 85, 0.2);
}

.holo-sphere:hover {
  transform: scale(1.08);
  box-shadow: 0 0 50px rgba(139, 115, 85, 0.4);
}

.sphere-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid var(--phase-color);
  opacity: 0.4;
  animation: sphere-pulse 3s ease-in-out infinite;
}

.sphere-ring.ring-outer {
  inset: -8px;
  opacity: 0.2;
}

.sphere-ring.ring-middle {
  inset: -4px;
  opacity: 0.3;
}

@keyframes sphere-pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

.sphere-core {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  z-index: 2;
  pointer-events: none;
}

.sphere-phase-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.sphere-phase-name {
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  text-align: center;
  line-height: 1.3;
}

.sphere-node-count {
  color: var(--phase-color);
  font-size: 11px;
  text-align: center;
  opacity: 0.9;
  line-height: 1.2;
}

/* Tooltip */
.sphere-tooltip {
  position: absolute;
  bottom: calc(100% + 16px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 15, 20, 0.95);
  border: 1px solid var(--phase-color, #8B7355);
  border-radius: 12px;
  padding: 16px;
  min-width: 200px;
  z-index: 10;
  pointer-events: none;
  backdrop-filter: blur(10px);
}

.tooltip-title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.tooltip-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.tooltip-hint {
  color: var(--phase-color, #8B7355);
  font-size: 12px;
  font-weight: 500;
}

/* Arrow */
.holo-arrow {
  position: absolute;
  right: -40px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 3;
  width: 36px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arrow-body {
  position: relative;
  width: 30px;
  height: 48px;
  overflow: hidden;
}

.arrow-flow {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right,
    transparent 0%,
    rgba(255, 255, 255, 0.95) 28%,
    rgba(255, 220, 150, 1) 48%,
    rgba(255, 255, 255, 0.95) 68%,
    transparent 100%
  );
  background-size: 70px 100%;
  animation: arrow-flow 1.0s linear infinite;
}

@keyframes arrow-flow {
  to { background-position: 70px 0; }
}

/* Interactive Hint */
.interactive-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  animation: hint-pulse 2s ease-in-out infinite;
}

.hint-icon {
  font-size: 20px;
}

@keyframes hint-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Detail View */
.phase-detail-view {
  padding: 20px 0;
}

.detail-header {
  margin-bottom: 40px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 24px;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.back-arrow {
  font-size: 18px;
}

.detail-phase-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-phase-icon {
  font-size: 48px;
}

.detail-phase-name {
  color: #fff;
  font-size: 32px;
  font-weight: 700;
}

.detail-node-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

/* Node Cards Grid */
.nodes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.node-card {
  background: rgba(30, 28, 26, 0.6);
  border: 1px solid rgba(139, 115, 85, 0.2);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.node-card:hover {
  transform: translateY(-4px);
  border-color: rgba(139, 115, 85, 0.4);
  box-shadow: 0 8px 24px rgba(139, 115, 85, 0.2);
}

.node-card.node-completed {
  border-color: rgba(34, 197, 94, 0.4);
  background: rgba(34, 197, 94, 0.05);
}

.node-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.node-code-badge {
  background: rgba(139, 115, 85, 0.3);
  color: #C4A77D;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.node-info-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.node-info-btn:hover {
  opacity: 1;
}

.node-card-body {
  margin-bottom: 16px;
}

.node-card-title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.node-card-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  line-height: 1.5;
}

.node-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.node-duration {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.node-status {
  font-size: 12px;
  font-weight: 500;
}

.status-done {
  color: #22c55e;
}

.status-pending {
  color: rgba(255, 255, 255, 0.4);
}

/* Node Detail Modal */
.node-detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #1e1c1a;
  border: 1px solid rgba(139, 115, 85, 0.3);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s;
  z-index: 10;
}

.modal-close:hover {
  color: #fff;
}

.modal-header {
  padding: 24px;
  border-bottom: 2px solid;
  background: rgba(139, 115, 85, 0.1);
}

.modal-node-code {
  display: inline-block;
  background: rgba(139, 115, 85, 0.3);
  color: #C4A77D;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
}

.modal-node-name {
  color: #fff;
  font-size: 24px;
  font-weight: 700;
}

.modal-body {
  padding: 24px;
}

.modal-section {
  margin-bottom: 24px;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.modal-section h4 {
  color: #C4A77D;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.modal-section p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  line-height: 1.6;
}

.modal-section ul {
  list-style: none;
  padding: 0;
}

.modal-section li {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  padding-left: 20px;
}

.modal-section li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #22c55e;
  font-weight: 700;
}

/* Responsive */
@media (max-width: 768px) {
  .holo-spheres {
    gap: 24px;
  }

  .holo-sphere {
    width: 100px;
    height: 100px;
  }

  .sphere-phase-icon {
    font-size: 20px;
  }

  .sphere-phase-name {
    font-size: 12px;
  }

  .nodes-grid {
    grid-template-columns: 1fr;
  }

  .detail-phase-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-phase-name {
    font-size: 24px;
  }
}
</style>
