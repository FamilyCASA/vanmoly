"""测试API"""
import sys
sys.path.insert(0, 'D:\\desktop\\DESIGNARY-SYS-V3.0\\backend')

from app import create_app
from config import config

app = create_app(config['development'])

# 测试一个简单请求
with app.test_client() as client:
    # 测试根路由
    resp = client.get('/')
    print(f'Root: {resp.status_code} - {resp.get_json()}')
    
    # 测试API根
    resp = client.get('/api/v3/')
    print(f'API Root: {resp.status_code} - {resp.get_json()}')
    
    # 先登录获取token
    login_data = {'username': 'admin', 'password': 'admin123'}
    resp = client.post('/api/v3/auth/login', json=login_data)
    login_result = resp.get_json()
    print(f'Login: {resp.status_code}')
    
    if resp.status_code == 200 and login_result.get('code') == 200:
        print(f'  Login data: {login_result.get("data", {}).keys()}')
        token = login_result['data'].get('access_token') or login_result['data'].get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # 测试物料列表
        resp = client.get('/api/v3/materials?page=1&per_page=5', headers=headers)
        data = resp.get_json()
        print(f'Materials: {resp.status_code} - code: {data.get("code")}')
        if data.get('code') == 200:
            print(f'  Total: {data.get("data", {}).get("total")}')
            print(f'  Items: {len(data.get("data", {}).get("items", []))}')
        
        # 测试分类列表
        resp = client.get('/api/v3/materials/categories', headers=headers)
        data = resp.get_json()
        print(f'Categories: {resp.status_code} - code: {data.get("code")}')
        if data.get('code') == 200:
            items = data.get('data', [])
            print(f'  Count: {len(items)}')
            if items:
                print(f'  First: {items[0].get("name")}')
    else:
        print(f'Login failed: {login_result}')
