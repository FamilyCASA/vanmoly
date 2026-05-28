path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find color scheme in template
import re
# Find colorScheme computed
m = re.search(r'const colorScheme = computed.*?(?=const \w+ = computed|\n// [A-Z]|\n$)', content, re.DOTALL)
if m:
    print("=== colorScheme computed ===")
    print(m.group(0)[:800])
    print()

# Find color-scheme in template HTML
idx = content.find('color-scheme')
if idx >= 0:
    print("=== color-scheme template ===")
    print(content[max(0,idx-100):idx+500])
