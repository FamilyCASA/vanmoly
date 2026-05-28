import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find line numbers for CaseSpaceMaterial.to_dict
in_class = False
td_start_line = 0
for i, line in enumerate(lines, 1):
    if 'class CaseSpaceMaterial' in line:
        in_class = True
    if in_class and 'def to_dict' in line and td_start_line == 0:
        td_start_line = i

print(f"to_dict starts at line {td_start_line}")
# Print context around it
for i in range(max(1, td_start_line-2), min(len(lines), td_start_line+35)):
    print(f"L{i}: {lines[i-1].rstrip()}")
