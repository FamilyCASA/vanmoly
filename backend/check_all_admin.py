import requests

base_url = 'http://localhost:9090/api/v3'

# 登录
resp = requests.post(f'{base_url}/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

print('='*60)
print('Backend Admin Cards Data Check (Final)')
print('='*60)

cards = [
    ('物料管理', '/materials', 'total'),
    ('物料分类', '/materials/categories', 'count'),
    ('客户管理', '/customers', 'total'),
    ('员工管理', '/employees', 'total'),
    ('合同管理', '/contracts', 'total'),
    ('楼盘管理', '/buildings', 'total'),
    ('报价管理', '/quotes', 'total'),
    ('案例管理', '/cases', 'total'),
    ('线索管理V2', '/leads', 'total'),
    ('供应商管理', '/materials/suppliers', 'count'),
    ('服务流程', '/workflows', 'total'),
]

for name, path, key in cards:
    try:
        resp = requests.get(f'{base_url}{path}', headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if key == 'count':
                if isinstance(data.get('data'), list):
                    count = len(data.get('data', []))
                else:
                    count = len(data.get('data', {}).get('items', []))
            else:
                count = data.get('data', {}).get('total', 0)
            status = '[OK]'
        else:
            count = f'HTTP {resp.status_code}'
            status = '[ERR]'
    except Exception as e:
        count = f'Error: {str(e)[:30]}'
        status = '[ERR]'
    
    print(f'{status} {name:12s} {path:30s} {count}')

print('='*60)
