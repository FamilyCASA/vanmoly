import re

with open('app/routes/material_sku_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换装饰器和函数签名
# @token_required\ndef xxx(current_user, ...): → @jwt_required_v2\ndef xxx(...):
content = re.sub(
    r'@token_required\n(def \w+)\(current_user,',
    r'@jwt_required_v2\n\1(',
    content
)

# 也替换 @admin_required
content = re.sub(
    r'@admin_required\n(def \w+)\(current_user,',
    r'@jwt_required_v2\n\1(',
    content
)

with open('app/routes/material_sku_routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
