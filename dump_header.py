# -*- coding: utf-8 -*-
"""读取当前完整header模板和CSS"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 当前template header (line 1-210) ===')
for i in range(0, min(210, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')