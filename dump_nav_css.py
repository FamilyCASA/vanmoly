# -*- coding: utf-8 -*-
"""读取更多navbar CSS"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 从navbar开始，输出到mobile-menu结束
count = 0
started = False
for i in range(2413, min(2800, len(lines))):
    l = lines[i]
    print(f'{i+1}: {l.rstrip()}')
    count += 1
    if count > 200:
        break