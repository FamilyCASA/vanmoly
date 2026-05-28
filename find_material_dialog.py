import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find material dialog table section
in_dialog = False
for i, line in enumerate(lines, 1):
    if 'materialDialogVisible' in line and ('<el-dialog' in line or 'v-model' in line):
        in_dialog = True
    if in_dialog:
        print(f"Line {i}: {line.rstrip()}")
    if in_dialog and '</el-dialog>' in line:
        break
