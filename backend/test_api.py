import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8080/api/v3'
login = requests.post(f'{BASE}/auth/login', json={'identifier': 'vanmoly', 'password': 'Van9999'}, timeout=10)
token = login.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}

paths = [
    '/auth/me',
    '/stats/overview',
    '/stats/funnel',
    '/stats/channels',
    '/leads/todos',
    '/leads/filters',
    '/leads/sea',
    '/points/ranking',
    '/points/my',
]

for path in paths:
    r = requests.get(BASE + path, headers=headers, timeout=5)
    if r.status_code != 200:
        data = r.json()
        msg = data.get('message', '')
        print(f'{path}: [{r.status_code}] {msg}')
    else:
        print(f'{path}: [200] OK')
