import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check fallback dict has the new fields
for field in ["'material':", "'custom_name':", "'custom_measure':"]:
    count = c.count(field)
    print(f"{field} → {count} occurrences")

# Check save_space_materials_full has the new fields
idx = c.find('def save_space_materials_full')
if idx > 0:
    block = c[idx:idx+1500]
    for field in ['custom_name', 'material', 'custom_measure']:
        found = field in block
        print(f"  save_space_materials_full → {field}: {'✅' if found else '❌'}")
