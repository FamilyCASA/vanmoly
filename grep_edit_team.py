path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find team-related sections
for i, line in enumerate(lines):
    l = line.rstrip()
    if any(k in l for k in ['服务团队', '人员名单', 'team_member', 'teamMember', '团队成员']):
        start = max(0, i-3)
        end = min(len(lines), i+10)
        for j in range(start, end):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print('---')
