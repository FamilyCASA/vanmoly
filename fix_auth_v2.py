import re

# Fix hr_routes_v2.py
with open(r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\hr_routes_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
content = content.replace('from app.utils.auth import jwt_required, get_current_user_id', 'from app.routes.auth_routes_v2 import jwt_required_v2')
content = content.replace('@jwt_required', '@jwt_required_v2')
content = content.replace('get_current_user_id()', 'request.current_user.get("id")')

with open(r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\hr_routes_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('hr_routes_v2.py fixed')

# Fix lead_routes_v2.py
with open(r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\lead_routes_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
content = content.replace('from app.utils.auth import jwt_required, get_current_user_id', 'from app.routes.auth_routes_v2 import jwt_required_v2')
content = content.replace('@jwt_required', '@jwt_required_v2')
content = content.replace('get_current_user_id()', 'request.current_user.get("id")')

with open(r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\lead_routes_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('lead_routes_v2.py fixed')
