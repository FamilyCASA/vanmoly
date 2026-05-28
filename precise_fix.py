# -*- coding: utf-8 -*-
"""精确修改fetchWorkflowPhases"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到fetchWorkflowPhases的行号
func_line = None
for i, line in enumerate(lines):
    if 'const fetchWorkflowPhases = async () => {' in line:
        func_line = i
        break

if func_line is None:
    print('[X] Could not find fetchWorkflowPhases')
    exit()

print(f'Found fetchWorkflowPhases at line {func_line+1}')

# 在函数之前插入DEFAULT_WORKFLOW_PHASES
default_data = [
    '\n',
    'const DEFAULT_WORKFLOW_PHASES = [\n',
    '  { code: "phase1", name: "需求沟通", color: "#8B7355", nodes: [\n',
    '    { code: "N1.1", name: "客户需求调研" },\n',
    '    { code: "N1.2", name: "项目背景分析" },\n',
    '    { code: "N1.3", name: "预算初步评估" }\n',
    '  ]},\n',
    '  { code: "phase2", name: "方案设计", color: "#6B8E6B", nodes: [\n',
    '    { code: "N2.1", name: "设计方案制定" },\n',
    '    { code: "N2.2", name: "效果图制作" },\n',
    '    { code: "N2.3", name: "材料选型建议" }\n',
    '  ]},\n',
    '  { code: "phase3", name: "合同签订", color: "#7B8BA3", nodes: [\n',
    '    { code: "N3.1", name: "预算明细确认" },\n',
    '    { code: "N3.2", name: "合同条款议定" },\n',
    '    { code: "N3.3", name: "首期款项支付" }\n',
    '  ]},\n',
    '  { code: "phase4", name: "施工阶段", color: "#A08060", nodes: [\n',
    '    { code: "N4.1", name: "拆改工程" },\n',
    '    { code: "N4.2", name: "水电改造" },\n',
    '    { code: "N4.3", name: "泥瓦施工" },\n',
    '    { code: "N4.4", name: "木工制作" },\n',
    '    { code: "N4.5", name: "油漆涂刷" }\n',
    '  ]},\n',
    '  { code: "phase5", name: "竣工验收", color: "#9B7B5B", nodes: [\n',
    '    { code: "N5.1", name: "整体验收" },\n',
    '    { code: "N5.2", name: "问题整改" },\n',
    '    { code: "N5.3", name: "清洁交付" }\n',
    '  ]},\n',
    '  { code: "phase6", name: "售后服务", color: "#5B8B7B", nodes: [\n',
    '    { code: "N6.1", name: "质保说明" },\n',
    '    { code: "N6.2", name: "定期回访" },\n',
    '    { code: "N6.3", name: "售后响应" }\n',
    '  ]}\n',
    ']\n',
    '\n',
]

# 在func_line位置插入
lines = lines[:func_line] + default_data + lines[func_line:]

# 现在重新找到if语句的位置（因为行号已改变）
if_line = None
for i, line in enumerate(lines):
    if 'if (res && res.phases) {' in line:
        if_line = i
        break

print(f'Found if statement at line {if_line+1}')

# 修改if语句后面的内容
# if (res && res.phases) {
#       workflowPhases.value = res.phases
#     }
#   } catch

# 找到workflowPhases.value那行的下一行（即 } 关闭if）
assign_line = None
close_if_line = None
for i in range(if_line, min(if_line+10, len(lines))):
    if 'workflowPhases.value = res.phases' in lines[i]:
        assign_line = i
    if assign_line is not None and '}' in lines[i] and 'catch' not in lines[i]:
        close_if_line = i
        break

print(f'Found assignment at {assign_line+1}, close at {close_if_line+1}')

# 替换第2113行（关闭if的那行）为 else + DEFAULT_WORKFLOW_PHASES
# 原来的 } catch 前面需要加 } else { 和 DEFAULT_WORKFLOW_PHASES }
# 在assign_line后面插入else分支
new_content = lines[:assign_line+1] + ['      } else {\n', '        workflowPhases.value = DEFAULT_WORKFLOW_PHASES\n', '      }\n'] + lines[close_if_line+1:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print('[OK] Added DEFAULT_WORKFLOW_PHASES and fallback logic')
print('[DONE]')