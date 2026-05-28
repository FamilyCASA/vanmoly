import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check what patterns exist for mat row defaults
for kw in ['env_level', 'supply_chain', 'color_name', 'custom_name', 'custom_measure']:
    indices = []
    idx = 0
    while True:
        idx = c.find(kw, idx)
        if idx < 0:
            break
        line_start = c.rfind('\n', 0, idx) + 1
        line_end = c.find('\n', idx)
        line = c[line_start:line_end].strip()
        if len(line) < 150:
            indices.append(f"  offset {idx}: {line[:120]}")
        idx += len(kw)
    if indices:
        print(f"\n--- {kw} ({len(indices)} occurrences) ---")
        for i in indices[:5]:
            print(i)
