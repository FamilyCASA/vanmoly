# -*- coding: utf-8 -*-
"""安全修改流程显示 - 只改数据不碰模板"""

file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# 1. 在fetchWorkflowPhases前添加备用数据（只在script内添加）
if 'DEFAULT_WORKFLOW_PHASES' not in content:
    # 在fetchWorkflowPhases之前插入
    target = 'const fetchWorkflowPhases = async () => {'
    replacement = '''const DEFAULT_WORKFLOW_PHASES = [
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

''' + target
    
    content = content.replace(target, replacement)
    changes.append('Added DEFAULT_WORKFLOW_PHASES')
else:
    changes.append('DEFAULT_WORKFLOW_PHASES already exists')

# 2. 只修改fetchWorkflowPhases中的条件判断（在script区域内，不动template）
# 找到catch块前的if语句并扩展
old_logic = '''if (res && res.phases) {
        workflowPhases.value = res.phases
      }
    } catch'''

new_logic = '''if (res && res.phases && res.phases.length > 0) {
        workflowPhases.value = res.phases
      } else {
        workflowPhases.value = DEFAULT_WORKFLOW_PHASES
      }
    } catch'''

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    changes.append('Added fallback logic')
else:
    changes.append('Logic already updated or not found')

# 3. 修改catch块添加备用
old_catch = '''} catch (e) {
      console.log('加载服务流程失败', e)'''
new_catch = '''} catch (e) {
      console.log('加载服务流程失败，使用默认数据', e)
      workflowPhases.value = DEFAULT_WORKFLOW_PHASES'''

if old_catch in content:
    content = content.replace(old_catch, new_catch)
    changes.append('Added catch fallback')
else:
    changes.append('Catch block unchanged')

# 4. 替换箭头CSS（style区域内）
old_arrow = '''.holo-arrow {
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

new_arrow = '''.holo-arrow {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
  }

  .arrow-triangle {
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-left: 14px solid var(--accent);
    opacity: 0.6;
  }'''

if old_arrow in content:
    content = content.replace(old_arrow, new_arrow)
    changes.append('Replaced arrow CSS')
else:
    changes.append('Arrow CSS pattern not found')

# 5. 删除不需要的CSS
import re
old_body = '''.arrow-body {
    position: relative;
    width: 30px;
    height: 48px;
    overflow: hidden;
  }'''
old_flow = '''.arrow-flow {
    position: absolute;
    inset: 0;
    background: linear-gradient(to right,
      transparent 0%,
      rgba(255,255,255,0.95) 28%,
      rgba(255,220,150,1) 48%,
      rgba(255,255,255,0.95) 68%,
      transparent 100%
    );
    background-size: 70px 100%;
    animation: arrow-flow 1.0s linear infinite;
  }'''
old_before = '''.arrow-flow::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(to right,
      transparent,
      rgba(255,255,255,0.3),
      transparent
    );
    animation: arrow-flow 0.7s linear infinite reverse;
  }'''
old_after = '''.arrow-flow::after {
    content: '';
    position: absolute;
    right: -2px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-left: 14px solid var(--phase-color);
  }'''
old_keyframes = '''@keyframes arrow-flow {
    0% { left: -100%; }
    100% { left: 100%; }
  }'''

for css in [old_body, old_flow, old_before, old_after, old_keyframes]:
    if css in content:
        content = content.replace(css, '')
        changes.append(f'Removed {css[:30]}...')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Changes:')
for c in changes:
    print(f'  - {c}')
print('\n[DONE] Run build to verify')