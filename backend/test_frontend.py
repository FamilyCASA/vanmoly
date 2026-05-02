import requests
import json

BASE_URL = 'http://localhost:8000/api/v3'

# 1. 登录获取token
login_res = requests.post(f'{BASE_URL}/auth/login', json={
    'identifier': 'vanmoly',
    'password': 'Van9999'
})
token = login_res.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

# 测试 dashboard/stats 返回格式
res = requests.get(f'{BASE_URL}/dashboard/stats', headers=headers)
data = res.json()

print("=== 后端返回的完整结构 ===")
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n=== 前端接收到的数据（经过request.js拦截器后） ===")
print("拦截器返回: response.data.data")
print(f"实际返回给前端的数据: {json.dumps(data.get('data'), indent=2, ensure_ascii=False)}")
