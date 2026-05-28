import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\MaterialManageV2.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find all API calls
import re
calls = re.findall(r"request\.(get|post|put|delete)\(['\"`]([^'\"`]+)", content)
for method, url in calls:
    print(f"  {method.upper():6s} {url}")
