import sys, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find cover-style
idx = content.find('cover-style')
while idx >= 0:
    print(f"--- pos {idx} ---")
    print(repr(content[max(0,idx-20):idx+150]))
    print()
    idx = content.find('cover-style', idx+1)
