# -*- coding: utf-8 -*-
"""精确替换箭头块（691-699）为三角形"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 确认箭头块位置
target = '              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">'
if lines[690].rstrip() != target.lstrip():
    print(f'[X] Line 691 mismatch: {repr(lines[690])}')
    exit()

print(f'确认: lines 691-699 (index 690-698)')
print('旧内容:')
for i in range(690, 699):
    print(f'  {i+1}: {repr(lines[i])}')

# 新内容
new_block = [
    '              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">\n',
    '                <div class="arrow-triangle"></div>\n',
    '              </div>\n',
]

# 替换 691-699 (index 690-698)
lines = lines[:690] + new_block + lines[699:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('[OK] Replaced lines 691-699')
print('[DONE]')