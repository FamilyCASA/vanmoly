import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'onCat1Change' in line or 'onCat2Change' in line or 'l1Categories' in line or 'getL2Categor' in line:
        print(f"Line {i}: {line.rstrip()}")
