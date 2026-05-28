path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find color-scheme in HTML
import re
for m in re.finditer(r'color.?scheme|colorScheme|color_list|color-block|color-dot|color-swatch', content, re.IGNORECASE):
    start = max(0, m.start()-80)
    end = min(len(content), m.end()+200)
    print(f"--- pos {m.start()} ---")
    print(content[start:end])
    print()
