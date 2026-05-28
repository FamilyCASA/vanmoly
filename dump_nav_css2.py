# -*- coding: utf-8 -*-
"""继续读取navbar CSS到nav-link等"""
file_path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\Home.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2614, min(2850, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')