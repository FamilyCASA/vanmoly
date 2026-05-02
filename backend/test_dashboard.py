import requests
import json

BASE_URL = 'http://localhost:8000/api/v3'

# 1. 登录获取token
login_res = requests.post(f'{BASE_URL}/auth/login', json={
    'identifier': 'vanmoly',
    'password': 'Van9999'
})
print(f"Login status: {login_res.status_code}")
if login_res.status_code != 200:
    print(f"Login failed: {login_res.text}")
    exit(1)

token = login_res.json()['data']['token']
print(f"Token obtained: {token[:20]}...")

headers = {'Authorization': f'Bearer {token}'}

# 2. 测试 dashboard/stats
print("\n--- Testing /dashboard/stats ---")
res = requests.get(f'{BASE_URL}/dashboard/stats', headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Response structure: {list(data.keys())}")
    print(f"Code: {data.get('code')}")
    print(f"Data keys: {list(data.get('data', {}).keys())}")
    print(f"Overview: {data.get('data', {}).get('overview', {})}")
    print(f"Todo: {data.get('data', {}).get('todo', {})}")
else:
    print(f"Error: {res.text[:200]}")

# 3. 测试 dashboard/trends
print("\n--- Testing /dashboard/trends ---")
res = requests.get(f'{BASE_URL}/dashboard/trends?period=week', headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Response structure: {list(data.keys())}")
    print(f"Data keys: {list(data.get('data', {}).keys())}")

# 4. 测试 dashboard/contract-distribution
print("\n--- Testing /dashboard/contract-distribution ---")
res = requests.get(f'{BASE_URL}/dashboard/contract-distribution', headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Response structure: {list(data.keys())}")

# 5. 测试 dashboard/recent-activities
print("\n--- Testing /dashboard/recent-activities ---")
res = requests.get(f'{BASE_URL}/dashboard/recent-activities?limit=5', headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Response structure: {list(data.keys())}")
    print(f"Activities count: {len(data.get('data', []))}")
