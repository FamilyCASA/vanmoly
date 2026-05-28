import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find the material select in the matRows table - look for the select after cat2
idx = content.find('onCat2Change')
if idx >= 0:
    print("=== onCat2Change 上下文 ===")
    print(content[max(0,idx-200):idx+600])
