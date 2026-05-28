import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find material select - search for el-select with filterable
for keyword in ['matRow', 'material', 'el-select', 'filterable', 'saveMaterialConfig']:
    idx = content.find(keyword)
    if idx >= 0:
        print(f"\n=== '{keyword}' at pos {idx} ===")
        print(content[max(0,idx-100):idx+300])
        print("---")
