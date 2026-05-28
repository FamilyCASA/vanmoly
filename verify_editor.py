import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check addMatRow
idx = c.find('const addMatRow')
if idx > 0:
    block = c[idx:idx+300]
    print("addMatRow:")
    print(block[:300])
    for field in ['custom_name', 'custom_measure']:
        found = field in block
        print(f"  {field}: {'✅' if found else '❌'}")

# Check save payload
idx = c.find('const saveMaterialConfig')
if idx > 0:
    block = c[idx:idx+600]
    print("\nsaveMaterialConfig payload:")
    for field in ['custom_name', 'custom_measure']:
        found = field in block
        print(f"  {field}: {'✅' if found else '❌'}")
