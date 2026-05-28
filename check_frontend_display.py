import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find the material table - look for custom_measure display
idx = content.find('定制计量值')
if idx > 0:
    # Get context around it
    start = max(0, idx - 200)
    end = min(len(content), idx + 500)
    print("=== 定制计量值列附近代码 ===")
    print(content[start:end])

# Also find where custom_measure is used
print("\n=== custom_measure 使用情况 ===")
for i, line in enumerate(content.split('\n')):
    if 'custom_measure' in line or 'calcVal' in line:
        print(f"Line {i+1}: {line.strip()}")
