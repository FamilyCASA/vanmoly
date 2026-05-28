# -*- coding: utf-8 -*-
"""直接替换文本内容"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# 检查当前状态
print('Checking current state...')
print('Has DEFAULT_WORKFLOW:', 'DEFAULT_WORKFLOW' in content)
print('Has fetchWorkflowPhases:', 'fetchWorkflowPhases' in content)
print('Has .holo-arrow:', '.holo-arrow' in content)

# 1. 添加备用数据 - 只在script区域内的fetchWorkflowPhases之前
if 'DEFAULT_WORKFLOW_PHASES' not in content:
    # 在 fetchWorkflowPhases 之前添加
    target = 'const fetchWorkflowPhases = async () => {'
    default_data = '''const DEFAULT_WORKFLOW_PHASES = [
  { code: 'phase1', name: '需求沟通', color: '#8B7355', nodes: [
    { code: 'N1.1', name: '客户需求调研' },
    { code: 'N1.2', name: '项目背景分析' },
    { code: 'N1.3', name: '预算初步评估' }
  ]},
  { code: 'phase2', name: '方案设计', color: '#6B8E6B', nodes: [
    { code: 'N2.1', name: '设计方案制定' },
    { code: 'N2.2', name: '效果图制作' },
    { code: 'N2.3', name: '材料选型建议' }
  ]},
  { code: 'phase3', name: '合同签订', color: '#7B8BA3', nodes: [
    { code: 'N3.1', name: '预算明细确认' },
    { code: 'N3.2', name: '合同条款议定' },
    { code: 'N3.3', name: '首期款项支付' }
  ]},
  { code: 'phase4', name: '施工阶段', color: '#A08060', nodes: [
    { code: 'N4.1', name: '拆改工程' },
    { code: 'N4.2', name: '水电改造' },
    { code: 'N4.3', name: '泥瓦施工' },
    { code: 'N4.4', name: '木工制作' },
    { code: 'N4.5', name: '油漆涂刷' }
  ]},
  { code: 'phase5', name: '竣工验收', color: '#9B7B5B', nodes: [
    { code: 'N5.1', name: '整体验收' },
    { code: 'N5.2', name: '问题整改' },
    { code: 'N5.3', name: '清洁交付' }
  ]},
  { code: 'phase6', name: '售后服务', color: '#5B8B7B', nodes: [
    { code: 'N6.1', name: '质保说明' },
    { code: 'N6.2', name: '定期回访' },
    { code: 'N6.3', name: '售后响应' }
  ]}
]

'''
    content = content.replace(target, default_data + target, 1)
    changes.append('Added DEFAULT_WORKFLOW_PHASES')
else:
    changes.append('DEFAULT_WORKFLOW_PHASES already exists')

# 2. 修改 fetchWorkflowPhases 的逻辑
# 找到 "} else {" 后面只有 "workflowPhases.value = res.phases" 的情况
old_pattern = '''if (res && res.phases) {
        workflowPhases.value = res.phases
      }
    } catch'''

new_pattern = '''if (res && res.phases && res.phases.length > 0) {
        workflowPhases.value = res.phases
      } else {
        workflowPhases.value = DEFAULT_WORKFLOW_PHASES
      }
    } catch'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    changes.append('Updated fallback logic')
else:
    changes.append('Logic pattern not found')

# 3. 修改catch块
old_catch = "console.log('加载服务流程失败', e)"
new_catch = "console.log('加载服务流程失败，使用默认数据', e)\n      workflowPhases.value = DEFAULT_WORKFLOW_PHASES"

if old_catch in content:
    content = content.replace(old_catch, new_catch, 1)
    changes.append('Added catch fallback')
else:
    changes.append('Catch not found')

# 4. 修改箭头CSS
old_arrow = '.holo-arrow {\n\n  position: absolute;\n\n  right: -40px;\n\n  top: 50%;\n\n  transform: translateY(-50%);\n\n  z-index: 3;\n\n  width: 36px;\n\n  height: 48px;\n\n  display: flex;\n\n  align-items: center;\n\n  justify-content: center;\n\n}'
new_arrow = '.holo-arrow {\n\n  position: relative;\n\n  display: flex;\n\n  align-items: center;\n\n  justify-content: center;\n\n  width: 24px;\n\n}\n\n  .arrow-triangle {\n\n  width: 0;\n\n  height: 0;\n\n  border-top: 10px solid transparent;\n\n  border-bottom: 10px solid transparent;\n\n  border-left: 14px solid var(--accent);\n\n  opacity: 0.6;\n\n}'

if old_arrow in content:
    content = content.replace(old_arrow, new_arrow)
    changes.append('Replaced arrow CSS')
else:
    changes.append('Arrow CSS not found with that pattern')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('\nChanges:')
for c in changes:
    print(f'  - {c}')
print('\n[DONE]')