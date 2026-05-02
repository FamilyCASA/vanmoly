import urllib.request
import json
import urllib.parse

def test_api(method, path, data=None):
    url = f'http://localhost:5000{path}'
    try:
        if method == 'POST' and data:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), 
                                         headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)
        req.method = method
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

# 登录获取token
login_res = test_api('POST', '/api/v3/auth/login', {'username': 'admin', 'password': 'admin123'})
token = login_res.get('data', {}).get('token', '')
print(f"Login: token={'OK' if token else 'FAIL'}")

def authed_request(path):
    url = f'http://localhost:5000{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

# 测试各模块
apis = [
    ('物料列表', '/api/v3/materials?page=1&page_size=5'),
    ('物料分类', '/api/v3/materials/categories'),
    ('物料统计', '/api/v3/materials/stats'),
    ('客户列表', '/api/v3/customers?page=1&page_size=5'),
    ('员工列表', '/api/v3/employees?page=1&page_size=5'),
    ('合同列表', '/api/v3/contracts?page=1&page_size=5'),
    ('楼盘列表', '/api/v3/buildings?page=1&page_size=5'),
    ('报价列表', '/api/v3/quotes?page=1&page_size=5'),
    ('方案列表', '/api/v3/schemes?page=1&page_size=5'),
]

print("\nAPI测试结果:")
for name, path in apis:
    res = authed_request(path)
    if 'error' in res:
        print(f"  [FAIL] {name}: {res['error']}")
    else:
        data = res.get('data', {})
        if isinstance(data, list):
            print(f"  [OK] {name}: {len(data)}条")
        elif isinstance(data, dict):
            total = data.get('total', len(data.get('items', [])))
            print(f"  [OK] {name}: {total}条")
        else:
            print(f"  [OK] {name}: 返回数据")
