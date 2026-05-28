import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find l1Categories computed
for i, line in enumerate(lines, 1):
    if 'l1Categories' in line and ('computed' in lines[max(0,i-5):i] or 'const l1' in line or 'l1Categories' in line):
        print(f"L{i}: {line.rstrip()}")
