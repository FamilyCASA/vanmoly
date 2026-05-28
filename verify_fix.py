import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Check recalcMatRow
idx = content.find('const recalcMatRow')
print("=== recalcMatRow (计算后同步到custom_measure) ===")
print(content[idx:idx+600])

# Check el-select
idx2 = content.find('filter-method')
print("\n=== el-select (使用filter-method) ===")
print(content[max(0,idx2-50):idx2+200])

# Check onMatFilter
idx3 = content.find('const onMatFilter')
print("\n=== onMatFilter ===")
print(content[idx3:idx3+300])
