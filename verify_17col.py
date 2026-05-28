import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')
from app.models.case import CaseSpaceMaterial
m = CaseSpaceMaterial()
d = m.to_dict()
required = ['custom_name','category_level1','category_level2','material_name','spec','brand','material','color_name','width','depth','height','custom_measure','quantity','unit','unit_price','total_price']
for f in required:
    print(f"  {f}: {'✅' if f in d else '❌'}")
print(f"Total keys: {len(d)}")
