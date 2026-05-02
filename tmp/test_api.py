# -*- coding: utf-8 -*-
import requests

# Login
r = requests.post('http://localhost:8080/api/v3/auth/login', json={'identifier':'vanmoly','password':'Van9999'})
print('Login:', r.status_code, r.json())
token = r.json().get('data',{}).get('token')
if not token:
    print('No token!')
    exit()

headers = {'Authorization': f'Bearer {token}'}

# Test API
tests = [
    '/api/v3/cases',
    '/api/v3/dashboard/stats',
]

for path in tests:
    r = requests.get(f'http://localhost:8080{path}', headers=headers)
    print(f'{path}: {r.status_code}')