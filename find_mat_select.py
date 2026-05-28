import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find the material el-select
idx = content.find('el-select')
while idx >= 0:
    snippet = content[idx:idx+800]
    if 'material_id' in snippet:
        print("=== Material el-select ===")
        print(snippet)
        break
    idx = content.find('el-select', idx+10)
