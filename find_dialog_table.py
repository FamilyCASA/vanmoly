import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find the table template section (material dialog)
in_dialog = False
for i, line in enumerate(lines, 1):
    if 'materialDialogVisible' in line or 'material-dialog' in line.lower():
        in_dialog = True
    if in_dialog:
        print(f"L{i}: {line.rstrip()}")
        if i > 200 and 'materialDialogVisible' not in line and 'material-dialog' not in line.lower() and '<el-dialog' not in line and '</el-dialog>' not in line:
            # Keep printing a bit more
            pass
        if '</el-dialog>' in line:
            break
