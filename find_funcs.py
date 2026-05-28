import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find onMatSearch function body
idx = content.find('const onMatSearch')
if idx >= 0:
    print("=== onMatSearch ===")
    print(content[idx:idx+600])

# Find getFilteredSKUs
idx2 = content.find('const getFilteredSKUs')
if idx2 >= 0:
    print("\n=== getFilteredSKUs ===")
    print(content[idx2:idx2+500])

# Find saveMaterialConfig (the actual function, not the button)
idx3 = content.find('const saveMaterialConfig')
if idx3 >= 0:
    print("\n=== saveMaterialConfig ===")
    print(content[idx3:idx3+1500])

# Find onMatSelect
idx4 = content.find('const onMatSelect')
if idx4 >= 0:
    print("\n=== onMatSelect ===")
    print(content[idx4:idx4+600])
