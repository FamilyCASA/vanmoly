# -*- coding: utf-8 -*-
"""删除旧的arrow-body和arrow-flow CSS块"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到所有需要删除的块的行范围
to_delete = set()

# 找 .arrow-body 块
for i, l in enumerate(lines):
    if '.arrow-body {' in l or '.arrow-flow {' in l or '.arrow-flow::before {' in l or '.arrow-flow::after {' in l:
        depth = 0
        for j in range(i, len(lines)):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth == 0:
                to_delete.update(range(i, j+1))
                print(f'删除块: line {i+1} - {j+1}')
                break

# 删除行
lines = [l for i, l in enumerate(lines) if i not in to_delete]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'[OK] 删除了 {len(to_delete)} 行旧CSS')
print('[DONE]')