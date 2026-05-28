$filePath = "D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue"
$content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)

# Find the process section start and end
$startMarker = '<section id="process" class="process holo-dome-section">'
$casesMarker = '<!-- Cases Section -->'

$startIdx = $content.IndexOf($startMarker)
$casesIdx = $content.IndexOf($casesMarker)

if ($startIdx -ge 0 -and $casesIdx -gt $startIdx) {
    $newSection = @'
    <section id="process" class="process holo-dome-section">
      <div class="section-container">
        <div class="section-header light">
          <span class="section-label">Our Process</span>
          <h2 class="section-title">全案落地服务流程</h2>
          <p class="section-desc">6大阶段，54个标准节点，品质全程可追溯</p>
        </div>

        <div v-if="workflowLoading" class="holo-loading">
          <div class="holo-loader"></div>
          <span>加载服务流程...</span>
        </div>

        <div v-else class="holo-dome">
          <!-- Progress Bar -->
          <div class="process-progress-bar">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: workflowProgress + '%' }"></div>
            </div>
            <div class="progress-labels">
              <span class="progress-text">服务进度</span>
              <span class="progress-percentage">{{ workflowProgress }}%</span>
            </div>
          </div>

          <!-- Phase Spheres -->
          <div class="holo-spheres">
            <div
              v-for="(phase, idx) in workflowPhases"
              :key="phase.code"
              class="holo-sphere-wrap"
              @click="togglePhase(phase.code)"
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
                  <div class="tooltip-hint">点击查看服务节点 →</div>
                </div>
              </div>
              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">
                <div class="arrow-body">
                  <div class="arrow-flow"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Node Detail Panel -->
          <div v-if="selectedPhase" class="phase-detail-view">
            <div class="detail-header">
              <button class="back-btn" @click="selectedPhase = null">
                <span class="back-arrow">←</span>
                <span>返回流程总览</span>
              </button>
              <div class="detail-phase-info">
                <span class="detail-phase-icon">{{ getPhaseIcon(selectedPhase.code) }}</span>
                <h3 class="detail-phase-name">{{ selectedPhase.name }}</h3>
                <span class="detail-node-count">{{ selectedPhase.nodes?.length || 0 }}个服务节点</span>
              </div>
            </div>
            <div class="nodes-grid">
              <div 
                v-for="(node, ni) in selectedPhase.nodes" 
                :key="ni"
                class="node-card"
                :class="{ 'node-completed': completedNodes.has(node.code) }"
                @click="toggleNodeComplete(node.code)"
              >
                <div class="node-card-header">
                  <span class="node-code-badge">{{ node.code }}</span>
                  <button class="node-info-btn" @click.stop="showNodeDetail(node)" title="查看详情">
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
        </div>
      </div>
    </section>

'@
    $content = $content.Substring(0, $startIdx) + $newSection + $content.Substring($casesIdx)
    [System.IO.File]::WriteAllText($filePath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "Process section updated successfully"
} else {
    Write-Host "Could not find section markers"
}