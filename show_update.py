import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

idx = c.find('def update_space_material')
if idx > 0:
    block = c[idx:idx+1500]
    print(block[:1500])
