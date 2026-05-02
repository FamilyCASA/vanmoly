import requests

base_url = 'http://localhost:9090/api/v3'

# 登录
resp = requests.post(f'{base_url}/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print('API Tests (Fixed):')
print()

# 物料列表
resp = requests.get(f'{base_url}/materials', headers=headers)
print(f'GET /materials: {resp.status_code}')
if resp.status_code == 200:
    result = resp.json()
    print(f'  Response code: {result.get("code")}')
    data = result.get('data', {})
    print(f'  Total: {data.get("total", 0)}')
    print(f'  Items count: {len(data.get("items", []))}')
    if data.get('items'):
        print(f'  First item: {data["items"][0].get("name", "N/A")}')
print()

# 客户列表
resp = requests.get(f'{base_url}/customers', headers=headers)
print(f'GET /customers: {resp.status_code}')
if resp.status_code == 200:
    result = resp.json()
    data = result.get('data', {})
    print(f'  Total: {data.get("total", 0)}')
print()

# 员工列表  
resp = requests.get(f'{base_url}/employees', headers=headers)
print(f'GET /employees: {resp.status_code}')
if resp.status_code == 200:
    result = resp.json()
    data = result.get('data', {})
    print(f'  Total: {data.get("total", 0)}')
print()

# 分类列表
resp = requests.get(f'{base_url}/materials/categories', headers=headers)
print(f'GET /materials/categories: {resp.status_code}')
if resp.status_code == 200:
    result = resp.json()
    data = result.get('data', [])
    print(f'  Count: {len(data)}')
