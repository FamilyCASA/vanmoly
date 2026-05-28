import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find existing smat-dim style, add if missing
if '.smat-dim' not in c:
    # Add after smat-measure
    old_css = ".smat-measure {"
    new_css = """.smat-dim { text-align: center; font-size: 10px; color: #aaa; }
.smat-measure {"""
    c = c.replace(old_css, new_css, 1)
    print("Added .smat-dim CSS")
else:
    print(".smat-dim already exists")

# Also make the overall table font smaller for 17 columns
old_table_css = ".smat-table {"
if ".smat-table {" in c:
    idx = c.find(".smat-table {")
    block = c[idx:idx+300]
    print(f"Current smat-table CSS: {block[:200]}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
