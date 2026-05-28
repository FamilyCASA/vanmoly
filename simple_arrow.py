# -*- coding: utf-8 -*-
"""只改template中的箭头部分"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找 holo-arrow 那行
arrow_line = None
for i, l in enumerate(lines):
    if '<div v-if="idx < workflowPhases.length - 1" class="holo-arrow">' in l:
        arrow_line = i
        break

print(f'箭头起始行: {arrow_line+1}')
print('内容:')
for i in range(arrow_line, min(arrow_line+6, len(lines))):
    print(f'  {i+1}: {repr(lines[i])}')

# 替换：从holo-arrow开始，到第一个</div>结束（假设不超过5行）
new_block = [
    '              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">\n',
    '                <div class="arrow-triangle"></div>\n',
    '              </div>\n',
]

# 找到旧块的结束
end_line = arrow_line
for i in range(arrow_line, min(arrow_line+5, len(lines))):
    if '</div>' in lines[i]:
        end_line = i
        break

print(f'旧块结束行: {end_line+1}')

lines = lines[:arrow_line] + new_block + lines[end_line+1:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('[OK] Template arrow block replaced')