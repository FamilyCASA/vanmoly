$filePath = "D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue"
$content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)

# Find and replace the fetchWorkflowPhases function
$oldFunc = 'const fetchWorkflowPhases = async () => {
  try {
    const res = await request.get("/workflows/public/phases")
    if (res && res.phases) {
      workflowPhases.value = res.phases
    }
  } catch (e) {
    console.log("加载服务流程失败", e)
  } finally {
    workflowLoading.value = false
  }
}'

$newFunc = 'const fetchWorkflowPhases = async () => {
  try {
    const res = await request.get("/workflows/public/phases")
    console.log("流程数据返回:", res)
    if (res && Array.isArray(res)) {
      workflowPhases.value = res
    } else if (res && res.phases) {
      workflowPhases.value = res.phases
    } else if (res && res.data) {
      workflowPhases.value = Array.isArray(res.data) ? res.data : (res.data.phases || [])
    }
  } catch (e) {
    console.log("加载服务流程失败，使用默认数据", e)
    workflowPhases.value = [
      { code: "PHASE_01", name: "需求沟通", color: "#8B7355", nodes: [
        { code: "N001", name: "需求调研" }, { code: "N002", name: "现场量房" }
      ]},
      { code: "PHASE_02", name: "方案设计", color: "#C4A77D", nodes: [
        { code: "N003", name: "平面方案" }, { code: "N004", name: "效果图" }, { code: "N005", name: "方案确认" }
      ]},
      { code: "PHASE_03", name: "材料采购", color: "#A67C52", nodes: [
        { code: "N006", name: "主材选购" }, { code: "N007", name: "软装搭配" }
      ]},
      { code: "PHASE_04", name: "施工监理", color: "#6B8E7B", nodes: [
        { code: "N008", name: "拆改工程" }, { code: "N009", name: "水电工程" }, { code: "N010", name: "泥木工程" }
      ]},
      { code: "PHASE_05", name: "安装验收", color: "#9B8B7A", nodes: [
        { code: "N011", name: "定制安装" }, { code: "N012", name: "整体验收" }
      ]},
      { code: "PHASE_06", name: "交付售后", color: "#B5A595", nodes: [
        { code: "N013", name: "竣工交付" }, { code: "N014", name: "售后跟踪" }
      ]}
    ]
  } finally {
    workflowLoading.value = false
  }
}'

$content = $content.Replace($oldFunc, $newFunc)
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.Encoding]::UTF8)
Write-Host "Done"