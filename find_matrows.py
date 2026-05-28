import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'matRows' in line and ('.value' in line or 'matRows.value' in line) and ('push' in line or '=' in line or '.map' in line or '.filter' in line):
        print(f"Line {i}: {line.rstrip()}")
