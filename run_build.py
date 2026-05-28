# -*- coding: utf-8 -*-
"""运行build并捕获错误"""
import subprocess, os
os.chdir(r'D:\desktop\VANMOLY-SYS-V3.0\frontend')
result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True, encoding='utf-8', timeout=120)
print('=== STDERR (last 2000 chars) ===')
print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
print('\n=== EXIT CODE ===')
print(result.returncode)