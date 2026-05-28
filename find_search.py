import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Search for onMatSearch in all forms
import re
for m in re.finditer(r'onMatSearch', content):
    start = max(0, m.start()-50)
    end = min(len(content), m.end()+200)
    print(f"\n=== onMatSearch at {m.start()} ===")
    print(content[start:end])

# Also search for matSearching
print("\n\n=== matSearching ===")
for m in re.finditer(r'matSearching', content):
    start = max(0, m.start()-30)
    end = min(len(content), m.end()+100)
    print(f"\n--- at {m.start()} ---")
    print(content[start:end])
