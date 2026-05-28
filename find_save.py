import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Get full el-select for material
idx = content.find('remote-method')
if idx >= 0:
    print("=== el-select 物料搜索 ===")
    print(content[max(0,idx-300):idx+500])

# Find onMatSearch function
idx2 = content.find('onMatSearch')
if idx2 >= 0:
    print("\n=== onMatSearch 函数 ===")
    print(content[idx2:idx2+800])

# Find saveMaterialConfig function  
idx3 = content.find('function saveMaterialConfig')
if idx3 < 0:
    idx3 = content.find('saveMaterialConfig')
if idx3 >= 0:
    print("\n=== saveMaterialConfig 函数 ===")
    print(content[idx3:idx3+1500])
