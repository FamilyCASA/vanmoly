import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find all occurrences of 'color_name' in case_routes
import re
for m in re.finditer(r".{0,60}color_name.{0,60}", c):
    line = m.group()
    print(f"offset {m.start()}: {line.strip()[:120]}")
