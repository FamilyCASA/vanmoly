path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find serviceTeam
import re
m = re.search(r'const serviceTeam = computed.*?(?=const \w+ = computed|\n// [A-Z])', content, re.DOTALL)
if m:
    print(m.group(0))
else:
    # try broader search
    idx = content.find('serviceTeam')
    if idx >= 0:
        print(content[idx:idx+600])
