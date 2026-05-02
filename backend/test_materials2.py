import requests

# 先登录获取新token
login_url = 'http://localhost:8080/api/v3/auth/login'
login_data = {'identifier': 'vanmoly', 'password': 'Van9999'}

response = requests.post(login_url, json=login_data)
result = response.json()
token = result['data']['token']

# 测试 brands 端点
url = 'http://localhost:8080/api/v3/materials/brands'
headers = {'Authorization': f'Bearer {token}'}

try:
    response = requests.get(url, headers=headers)
    print(f'Brands Status: {response.status_code}')
    print(f'Brands: {response.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
