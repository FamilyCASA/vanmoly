import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Reduce th padding and font for 17 columns
old = "  padding: 9px 12px; text-align: center; font-weight: 600; color: #666;\n  border-bottom: 2px solid #e8e0d6; font-size: 12px;"
new = "  padding: 6px 6px; text-align: center; font-weight: 600; color: #666;\n  border-bottom: 2px solid #e8e0d6; font-size: 10px;"
c = c.replace(old, new, 1)

# Reduce td padding too
old_td = ".smat-table td {"
idx = c.find(old_td)
if idx > 0:
    block = c[idx:idx+200]
    print(f"Current td CSS: {block[:150]}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done: th padding/font reduced")
