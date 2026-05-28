import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Full onMatSelect
idx = content.find('const onMatSelect')
print("=== onMatSelect (full) ===")
print(content[idx:idx+800])

# Find onMatSearch 
idx2 = content.find('const onMatSearch')
if idx2 >= 0:
    print("\n=== onMatSearch (full) ===")
    print(content[idx2:idx2+600])

# Find openMaterialConfig
idx3 = content.find('const openMaterialConfig')
if idx3 >= 0:
    print("\n=== openMaterialConfig ===")
    print(content[idx3:idx3+2000])
