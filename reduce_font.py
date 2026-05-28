import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Reduce table font size for 17 columns
old = ".smat-table {\n  width: 100%; border-collapse: collapse; font-size: 13px;"
new = ".smat-table {\n  width: 100%; border-collapse: collapse; font-size: 11px;"
c = c.replace(old, new, 1)

# Also reduce th font
old_th = ".smat-table th {"
idx = c.find(old_th)
if idx > 0:
    block = c[idx:idx+200]
    print(f"Current th CSS: {block[:150]}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done: font reduced to 11px")
