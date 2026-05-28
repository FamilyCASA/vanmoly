path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find loadSlideData function
for i, line in enumerate(lines):
    if 'loadSlideData' in line and ('async' in line or 'function' in line or 'const' in line):
        for j in range(i, min(i+80, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break
