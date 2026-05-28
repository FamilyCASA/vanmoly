path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find team template HTML
import re
m = re.search(r'<!-- 团队介绍 -->.*?</div>\s*</div>\s*</div>', content, re.DOTALL)
if m:
    print(m.group(0))
