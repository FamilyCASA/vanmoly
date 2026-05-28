import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find the material config table template (el-table columns)
# Search for color_name column
idx = c.find('color_name')
occurrences = []
while idx > 0:
    line_start = c.rfind('\n', 0, idx) + 1
    line_end = c.find('\n', idx)
    line = c[line_start:line_end].strip()
    if len(line) < 200:
        occurrences.append(f"  line ~{c[:idx].count(chr(10))+1}: {line[:150]}")
    idx = c.find('color_name', idx + 10)

print(f"color_name found {len(occurrences)} times:")
for o in occurrences[:8]:
    print(o)
