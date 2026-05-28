import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')
from app.models.case import CaseSpaceMaterial
m = CaseSpaceMaterial()
d = m.to_dict()
for key in ['width', 'depth', 'height', 'custom_name', 'material', 'custom_measure', 'category_level1', 'category_level2']:
    print(f"  {key}: {key in d}")
print(f"Total keys: {len(d)}")
