path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find team-related fields in CaseStudy
for i, line in enumerate(lines):
    if 'class CaseStudy' in line:
        for j in range(i, min(i+200, len(lines))):
            l = lines[j].rstrip()
            if any(k in l.lower() for k in ['team', 'designer', 'responsible', 'member', '员工', '人员', '服务']):
                print(f"  {j+1}: {l}")
        break
