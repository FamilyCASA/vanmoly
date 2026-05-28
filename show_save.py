import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find save_space_materials_full function
idx = c.find('def save_space_materials_full')
end = c.find('\n@', idx + 10)
if end < 0: end = c.find('\ndef ', idx + 10)
block = c[idx:end]
print(block[:3000])
