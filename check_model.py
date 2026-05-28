import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find CaseSpaceMaterial class
idx = c.find('class CaseSpaceMaterial')
if idx > 0:
    end = c.find('\nclass ', idx + 10)
    if end < 0:
        end = len(c)
    print(c[idx:end][:3000])
