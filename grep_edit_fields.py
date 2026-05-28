path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ['规划师', '设计师', '客户经理']):
        start = max(0, i-5)
        end = min(len(lines), i+15)
        for j in range(start, end):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print('===')
