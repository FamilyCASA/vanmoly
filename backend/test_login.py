import requests
import json

# 测试登录API
url = 'http://localhost:8080/api/v3/auth/login'
data = {'identifier': 'vanmoly', 'password': 'Van9999'}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=data, headers=headers, timeout=5)
    print(f'Status: {response.status_code}')
    result = response.json()
    print(f'Code: {result.get("code")}')
    print(f'Message: {result.get("message")}')
    if result.get('data'):
        print(f'Token: {result["data"]["token"][:50]}...')
        print(f'User: {result["data"]["user"]["username"]}')
        print(f'Role: {result["data"]["user"]["role"]}')
except Exception as e:
    print(f'Error: {e}')
