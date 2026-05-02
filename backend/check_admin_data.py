import requests
import json

base_url = 'http://localhost:9090/api/v3'
login_url = f'{base_url}/auth/login'

# 登录获取token
resp = requests.post(login_url, json={'username': 'admin', 'password': 'admin123'})
token = resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print('='*50)
print('Backend Admin Cards Data Check')
print('='*50)

# 1. 物料管理
print('\n[1] Materials:')
resp = requests.get(f'{base_url}/materials', headers=headers)
print(f'  /materials: {resp.status_code} - Total: {resp.json().get("total", 0)}')
resp = requests.get(f'{base_url}/materials/categories', headers=headers)
print(f'  /categories: {resp.status_code} - Count: {len(resp.json().get("data", []))}')

# 2. 客户管理
print('\n[2] Customers:')
resp = requests.get(f'{base_url}/customers', headers=headers)
print(f'  /customers: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 3. 员工管理
print('\n[3] Employees:')
resp = requests.get(f'{base_url}/employees', headers=headers)
print(f'  /employees: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 4. 合同管理
print('\n[4] Contracts:')
resp = requests.get(f'{base_url}/contracts', headers=headers)
print(f'  /contracts: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 5. 楼盘管理
print('\n[5] Buildings:')
resp = requests.get(f'{base_url}/buildings', headers=headers)
print(f'  /buildings: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 6. 报价管理
print('\n[6] Quotes:')
resp = requests.get(f'{base_url}/quotes', headers=headers)
print(f'  /quotes: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 7. 案例管理
print('\n[7] Cases:')
resp = requests.get(f'{base_url}/cases', headers=headers)
print(f'  /cases: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 8. 线索管理 (V2)
print('\n[8] Leads V2:')
resp = requests.get(f'{base_url}/leads-v2', headers=headers)
print(f'  /leads-v2: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 9. 供应商管理
print('\n[9] Suppliers:')
resp = requests.get(f'{base_url}/suppliers', headers=headers)
print(f'  /suppliers: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 10. 方案管理
print('\n[10] Schemes:')
resp = requests.get(f'{base_url}/schemes', headers=headers)
print(f'  /schemes: {resp.status_code} - Total: {resp.json().get("total", 0)}')

# 11. 服务流程
print('\n[11] Service Workflows:')
resp = requests.get(f'{base_url}/service-workflows', headers=headers)
print(f'  /service-workflows: {resp.status_code} - Total: {resp.json().get("total", 0)}')

print('\n' + '='*50)
print('Check Complete')
print('='*50)
