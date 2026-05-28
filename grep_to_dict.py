path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find to_dict method of CaseStudy
for i, line in enumerate(lines):
    if 'def to_dict' in line:
        for j in range(i, min(i+80, len(lines))):
            l = lines[j].rstrip()
            if any(k in l for k in ['planner', 'designer', 'responsible']):
                print(f"  {j+1}: {l}")
        break
