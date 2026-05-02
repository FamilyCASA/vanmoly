"""
批量修复路由文件中的认证导入
将旧的 token_required 替换为 jwt_required_v2
"""
import os
import re

# 需要修复的文件列表
files_to_fix = [
    'app/routes/building_routes.py',
    'app/routes/contract_routes.py',
    'app/routes/customer_routes.py',
    'app/routes/employee_routes.py',
    'app/routes/frontend_config_routes.py',
    'app/routes/quote_routes.py',
    'app/routes/scheme_routes.py',
    'app/routes/service_workflow_routes.py',
]

base_dir = os.path.dirname(os.path.abspath(__file__))

for filepath in files_to_fix:
    full_path = os.path.join(base_dir, filepath)
    
    if not os.path.exists(full_path):
        print(f"[SKIP] File not found: {filepath}")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含旧的导入
    if 'from app.routes.auth_routes import' not in content:
        print(f"[SKIP] No old import found: {filepath}")
        continue
    
    # 替换导入语句
    content = re.sub(
        r'from app\.routes\.auth_routes import\s+[^\n]+',
        'from app.routes.auth_routes_v2 import jwt_required_v2',
        content
    )
    
    # 替换装饰器 @token_required -> @jwt_required_v2
    content = content.replace('@token_required', '@jwt_required_v2')
    
    # 替换装饰器 @admin_required -> @jwt_required_v2 (admin功能后续单独处理)
    content = content.replace('@admin_required', '@jwt_required_v2')
    
    # 移除装饰器参数中的 current_user
    content = re.sub(r'@jwt_required_v2\s*\n\s*def\s+(\w+)\s*\(\s*current_user\s*,\s*', 
                     r'@jwt_required_v2\n    def \1(', 
                     content)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[FIXED] {filepath}")

print("\nDone! Please restart the backend server.")
