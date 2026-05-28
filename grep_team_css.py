path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find team-related CSS
for i, line in enumerate(lines):
    if '.team-' in line or '.slide-heading' in line:
        for j in range(i, min(i+20, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print('===')
