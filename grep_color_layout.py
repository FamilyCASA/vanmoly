path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find cover-colors-labeled template
idx = content.find('cover-colors-labeled')
if idx >= 0:
    print("=== HTML ===")
    print(content[max(0,idx-50):idx+600])
    print()

# Find CSS for color-label-item, color-dot, color-name
for cls in ['cover-colors-labeled', 'color-label-item', 'color-dot', 'color-name']:
    i = content.find('.' + cls)
    if i >= 0:
        print(f"=== .{cls} CSS ===")
        # find the rule block
        end = content.find('\n}', i)
        print(content[i:end+2])
        print()
