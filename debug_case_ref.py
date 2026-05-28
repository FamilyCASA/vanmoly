import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check imports
import re
for m in re.finditer(r'from app\.models\.case import (.+)', c):
    print(f"Import: {m.group(1).strip()}")

# Check if Case or CaseStudy is used
print(f"\n'Case.query' count: {c.count('Case.query')}")
print(f"'CaseStudy.query' count: {c.count('CaseStudy.query')}")
print(f"'Case ' (as class ref) count: {c.count('Case ')[:10] if isinstance(c.count('Case '), int) else 'N/A'}")

# Find any reference to just "Case" as a model
for i, line in enumerate(c.split('\n'), 1):
    if 'Case.query' in line and 'CaseStudy' not in line:
        print(f"Line {i}: {line.strip()[:100]}")
