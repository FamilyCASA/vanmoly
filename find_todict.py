import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find to_dict for CaseSpaceMaterial
idx = content.find('def to_dict')
count = 0
search_start = 0
while True:
    idx = content.find('def to_dict', search_start)
    if idx < 0: break
    count += 1
    # Get surrounding class context
    class_start = content.rfind('class ', max(0, idx-2000), idx)
    print(f"\n=== to_dict #{count} at {idx} (class at {class_start}) ===")
    print(content[max(0,class_start):idx+800])
    print("---")
    search_start = idx + 10
