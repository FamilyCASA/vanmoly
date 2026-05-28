import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find category material thead
import re
for m in re.finditer(r'<thead>.*?</thead>', c, re.DOTALL):
    block = m.group()
    # Skip if already has 17 columns (一级分类)
    if '一级分类' in block:
        continue
    if '序号' in block:
        print(f"offset {m.start()}: {block[:200]}")
