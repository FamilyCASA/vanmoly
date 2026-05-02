import re

with open('app/routes/material_sku_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 @token_required 为 @jwt_required_v2
content = content.replace('@token_required', '@jwt_required_v2')
content = content.replace('@admin_required', '@jwt_required_v2')

# 替换函数签名：def xxx(current_user): → def xxx():
content = re.sub(r'def (\w+)\(current_user\):', r'def \1():', content)

# 替换函数签名：def xxx(current_user, → def xxx(
content = re.sub(r'def (\w+)\(current_user,', r'def \1(', content)

with open('app/routes/material_sku_routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
