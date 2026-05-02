"""
检查前端调用的API路径是否在后端有对应路由
"""
from app import create_app

# 前端调用的API路径列表
frontend_routes = [
    '/materials',
    '/materials/stats',
    '/materials/categories',
    '/materials/brands',
    '/materials/options',
    '/materials/suppliers',
    '/materials/supplier-stats',
    '/customers',
    '/customers/stats',
    '/customers/options',
    '/employees',
    '/employees/statistics',
    '/employees/options',
    '/employees/departments',
    '/employees/positions',
    '/contracts',
    '/contracts/statistics',
    '/contracts/options',
    '/quotes',
    '/quotes/statistics',
    '/quotes/options',
    '/quotes/templates',
    '/cases',
    '/leads',
    '/leads/stats',
    '/workflows',
    '/workflows/statistics',
    '/workflows/phases',
    '/workflows/nodes',
    '/buildings',
    '/buildings/statistics',
    '/buildings/options',
    '/appointments',
    '/appointments/stats',
    '/frontend/pages',
    '/frontend/themes',
    '/frontend/navigation/header',
    '/frontend/navigation/footer',
    '/frontend/components',
    '/frontend/resources',
    '/auth/users',
    '/auth/stores',
    '/hr/employees',
    '/hr/departments',
    '/hr/positions',
    '/dashboard/stats',
]

app = create_app()
with app.app_context():
    backend_routes = set()
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.endpoint:
            backend_routes.add(rule.rule)
    
    print("=" * 80)
    print("Frontend API Route Check")
    print("=" * 80)
    
    for route in frontend_routes:
        full_path = f'/api/v3{route}'
        if full_path in backend_routes:
            print(f"[OK] {route} -> {full_path}")
        else:
            found = False
            for br in backend_routes:
                if route in br and '/api/v3' in br:
                    print(f"[WARN] {route} -> maybe {br}")
                    found = True
                    break
            if not found:
                print(f"[MISSING] {route} -> no matching route")
