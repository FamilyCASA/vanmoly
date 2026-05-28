import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find material config UI
for kw in ['物料配置', 'matConfig', 'mat-config', 'addMat', 'el-input', 'v-model.*material']:
    import re
    matches = list(re.finditer(kw, c))
    if matches:
        print(f"\n--- '{kw}' ({len(matches)} matches) ---")
        for m in matches[:3]:
            start = max(0, m.start() - 40)
            end = min(len(c), m.end() + 80)
            print(f"  ...{c[start:end]}...")
    else:
        print(f"\nNOT found: '{kw}'")
