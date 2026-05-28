# -*- coding: utf-8 -*-
"""精确替换箭头块（691-699）为三角形 - 简化版本"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 直接用索引替换
print('确认行691内容:')
print(repr(lines[690]))

# 新内容 - 必须保持相同的缩进
new_block = [
    '              <div v-if="idx < workflowPhases.length - 1" class="holo-arrow">\n',
    '                <div class="arrow-triangle"></div>\n',
    '              </div>\n',
]

# 替换 index 690-698 (共9行)
lines = lines[:690] + new_block + lines[699:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('[OK] Replaced lines 691-699')
print('[DONE]')