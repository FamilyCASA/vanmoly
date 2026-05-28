import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Reduce td padding for 17 columns
old = "  padding: 8px 12px; border-bottom: 1px solid #f0f0f0; color: #333;\n}"
new = "  padding: 5px 5px; border-bottom: 1px solid #f0f0f0; color: #333;\n}"
c = c.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done: td padding reduced")
