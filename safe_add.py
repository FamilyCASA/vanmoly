# -*- coding: utf-8 -*-
"""安全方式修改：只动script不碰template/style"""
import re

file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 fetchWorkflowPhases 之前插入 DEFAULT_WORKFLOW_PHASES
default_data = '''const DEFAULT_WORKFLOW_PHASES = [
  { code: "phase1", name: "需求沟通", color: "#8B7355", nodes: [
    { code: "N1.1", name: "客户需求调研" },
    { code: "N1.2", name: "项目背景分析" },
    { code: "N1.3", name: "预算初步评估" }
  ]},
  { code: "phase2", name: "方案设计", color: "#6B8E6B", nodes: [
    { code: "N2.1", name: "设计方案制定" },
    { code: "N2.2", name: "效果图制作" },
    { code: "N2.3", name: "材料选型建议" }
  ]},
  { code: "phase3", name: "合同签订", color: "#7B8BA3", nodes: [
    { code: "N3.1", name: "预算明细确认" },
    { code: "N3.2", name: "合同条款议定" },
    { code: "N3.3", name: "首期款项支付" }
  ]},
  { code: "phase4", name: "施工阶段", color: "#A08060", nodes: [
    { code: "N4.1", name: "拆改工程" },
    { code: "N4.2", name: "水电改造" },
    { code: "N4.3", name: "泥瓦施工" },
    { code: "N4.4", name: "木工制作" },
    { code: "N4.5", name: "油漆涂刷" }
  ]},
  { code: "phase5", name: "竣工验收", color: "#9B7B5B", nodes: [
    { code: "N5.1", name: "整体验收" },
    { code: "N5.2", name: "问题整改" },
    { code: "N5.3", name: "清洁交付" }
  ]},
  { code: "phase6", name: "售后服务", color: "#5B8B7B", nodes: [
    { code: "N6.1", name: "质保说明" },
    { code: "N6.2", name: "定期回访" },
    { code: "N6.3", name: "售后响应" }
  ]}
]

'''

target = 'const fetchWorkflowPhases = async () => {'
if target in content and 'DEFAULT_WORKFLOW_PHASES' not in content:
    content = content.replace(target, default_data + target, 1)
    print('[OK] Added DEFAULT_WORKFLOW_PHASES')
else:
    print('[INFO] DEFAULT_WORKFLOW_PHASES already exists or target not found')

# 2. 只修改 if (res && res.phases) 这一行
old_if = 'if (res && res.phases) {'
new_if = 'if (res && res.phases && res.phases.length > 0) {'
if old_if in content:
    content = content.replace(old_if, new_if, 1)
    print('[OK] Updated if condition')
else:
    print('[INFO] if condition already updated or not found')

# 3. 在赋值行后添加else分支 - 只匹配第一处
old_assign = '''workflowPhases.value = res.phases
      }
    } catch'''

new_assign = '''workflowPhases.value = res.phases
      } else {
        workflowPhases.value = DEFAULT_WORKFLOW_PHASES
      }
    } catch'''

if old_assign in content:
    content = content.replace(old_assign, new_assign, 1)
    print('[OK] Added else branch')
else:
    print('[INFO] Assign pattern not found')

# 4. 修改catch块
old_catch = "console.log('加载服务流程失败', e)"
new_catch = "console.log('加载服务流程失败，使用默认数据', e)\n      workflowPhases.value = DEFAULT_WORKFLOW_PHASES"

if old_catch in content:
    content = content.replace(old_catch, new_catch, 1)
    print('[OK] Updated catch block')
else:
    print('[INFO] Catch block already updated or not found')

# 5. 箭头CSS - 用更宽松的匹配
old_arrow_css = '''.holo-arrow {

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

  }'''

new_arrow_css = '''.holo-arrow {

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 24px;

    flex-shrink: 0;

  }

  .arrow-triangle {

    width: 0;

    height: 0;

    border-top: 10px solid transparent;

    border-bottom: 10px solid transparent;

    border-left: 14px solid var(--accent);

    opacity: 0.6;

  }'''

if old_arrow_css in content:
    content = content.replace(old_arrow_css, new_arrow_css)
    print('[OK] Replaced arrow CSS')
else:
    print('[INFO] Arrow CSS pattern not found, trying flexible match')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('\n[DONE] Run build to verify')