import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find all table elements and their context
import re
for m in re.finditer(r'<th[^>]*>.*?</th>', c, re.DOTALL):
    text = m.group()
    if '序号' in text or '自定义' in text or 'custom_name' in text:
        print(f"offset {m.start()}: {text[:80]}")
