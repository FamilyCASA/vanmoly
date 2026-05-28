# -*- coding: utf-8 -*-
"""简单安全的修复"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. 添加备用数据（在fetchWorkflowPhases前）
insert_data = '''const DEFAULT_WORKFLOW_PHASES = [
  { code: 'phase1', name: '需求沟通', color: '#8B7355', nodes: [
    { code: 'N1.1', name: '客户需求调研' }, { code: 'N1.2', name: '项目背景分析' }, { code: 'N1.3', name: '预算初步评估' }
  ]},
  { code: 'phase2', name: '方案设计', color: '#6B8E6B', nodes: [
    { code: 'N2.1', name: '设计方案制定' }, { code: 'N2.2', name: '效果图制作' }, { code: 'N2.3', name: '材料选型建议' }
  ]},
  { code: 'phase3', name: '合同签订', color: '#7B8BA3', nodes: [
    { code: 'N3.1', name: '预算明细确认' }, { code: 'N3.2', name: '合同条款议定' }, { code: 'N3.3', name: '首期款项支付' }
  ]},
  { code: 'phase4', name: '施工阶段', color: '#A08060', nodes: [
    { code: 'N4.1', name: '拆改工程' }, { code: 'N4.2', name: '水电改造' }, { code: 'N4.3', name: '泥瓦施工' },
    { code: 'N4.4', name: '木工制作' }, { code: 'N4.5', name: '油漆涂刷' }
  ]},
  { code: 'phase5', name: '竣工验收', color: '#9B7B5B', nodes: [
    { code: 'N5.1', name: '整体验收' }, { code: 'N5.2', name: '问题整改' }, { code: 'N5.3', name: '清洁交付' }
  ]},
  { code: 'phase6', name: '售后服务', color: '#5B8B7B', nodes: [
    { code: 'N6.1', name: '质保说明' }, { code: 'N6.2', name: '定期回访' }, { code: 'N6.3', name: '售后响应' }
  ]}
]

'''

new_lines = []
added_default = False
added_fallback = False

for i, line in enumerate(lines):
    # 在fetchWorkflowPhases前添加备用数据
    if not added_default and 'const fetchWorkflowPhases = async () => {' in line:
        new_lines.append(insert_data)
        added_default = True
        new_lines.append(line)
        continue
    
    # 修改if条件
    if not added_fallback and 'if (res && res.phases) {' in line:
        new_lines.append(line)
        # 跳过 { 和下一行，添加新逻辑
        next_line = lines[i+1]
        if 'workflowPhases.value = res.phases' in lines[i+1]:
            new_lines.append('        workflowPhases.value = res.phases\n')
            new_lines.append('      } else {\n')
            new_lines.append('        workflowPhases.value = DEFAULT_WORKFLOW_PHASES\n')
            # 跳过 } catch 之前的那行
            added_fallback = True
            continue
    elif not added_fallback and 'workflowPhases.value = res.phases' in line and 'const res' not in line:
        new_lines.append(line)
        # 查找并修改
        continue
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'[OK] Added DEFAULT_WORKFLOW_PHASES')
print('[DONE] Check and run build')