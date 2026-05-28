import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find the backend dict mapping for SKU fallback data
idx = c.find("category_level1")
while idx > 0:
    line_start = c.rfind('\n', 0, idx) + 1
    line_end = c.find('\n', idx)
    print(f"{c[line_start:line_end].strip()[:150]}")
    idx = c.find("category_level1", idx + 10)

print("\n--- custom_name / custom_unit / material_name fields ---")
for kw in ['custom_name', 'custom_unit', 'custom_measure', 'material_name', 'material_type', 'quantity']:
    idx2 = c.find(kw)
    count = 0
    while idx2 > 0 and count < 3:
        line_start = c.rfind('\n', 0, idx2) + 1
        line_end = c.find('\n', idx2)
        print(f"  [{kw}] {c[line_start:line_end].strip()[:120]}")
        idx2 = c.find(kw, idx2 + 10)
        count += 1
