path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all class names
for i, line in enumerate(lines):
    if 'class ' in line and 'Model' in line:
        print(f"  {i+1}: {line.rstrip()}")

print("---")

# Check for db.Table (association tables)
for i, line in enumerate(lines):
    if 'db.Table' in line:
        print(f"  {i+1}: {line.rstrip()}")
