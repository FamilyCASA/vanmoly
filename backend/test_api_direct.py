import requests

base_url = 'http://localhost:9090/api/v3'

# 1. 健康检查
print('1. Health Check:')
resp = requests.get('http://localhost:9090/')
print(f'   /: {resp.status_code} - {resp.json()}')

# 2. 登录
print('\n2. Login:')
resp = requests.post(f'{base_url}/auth/login', json={'username': 'admin', 'password': 'admin123'})
print(f'   Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    token = data['data']['token']
    print(f'   Token: {token[:20]}...')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. 测试各个API
    print('\n3. API Tests:')
    
    # 物料列表
    resp = requests.get(f'{base_url}/materials', headers=headers)
    print(f'   GET /materials: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'      Total: {data.get("total", 0)}')
        if data.get('items'):
            print(f'      First item: {data["items"][0].get("name", "N/A")}')
    else:
        print(f'      Error: {resp.text[:200]}')
    
    # 客户列表
    resp = requests.get(f'{base_url}/customers', headers=headers)
    print(f'   GET /customers: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'      Total: {data.get("total", 0)}')
    
    # 员工列表
    resp = requests.get(f'{base_url}/employees', headers=headers)
    print(f'   GET /employees: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'      Total: {data.get("total", 0)}')
    
    # 分类列表
    resp = requests.get(f'{base_url}/materials/categories', headers=headers)
    print(f'   GET /materials/categories: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'      Count: {len(data.get("data", []))}')
else:
    print(f'   Login failed: {resp.text}')
