import sys, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8')

# 测试 /api/v3/auth/login (v2 login)
login_data = json.dumps({'identifier': 'admin', 'password': 'van654321'}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8080/api/v3/auth/login',
    data=login_data,
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    d = json.loads(resp.read())
    print('login OK')
    token = d.get('data', {}).get('token') or d.get('token', '')
    print('token:', token[:40] + '...' if token else 'NONE')
    
    # 测试 /api/v3/employees/positions
    req2 = urllib.request.Request(
        'http://localhost:8080/api/v3/employees/positions',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    resp2 = urllib.request.urlopen(req2, timeout=10)
    d2 = json.loads(resp2.read())
    print('positions code:', d2.get('code'))
    print('positions count:', len(d2.get('data', [])))
    print('positions first:', d2.get('data', [{}])[0] if d2.get('data') else 'EMPTY')
except Exception as e:
    print('ERROR:', e)
    if hasattr(e, 'read'):
        print('body:', e.read().decode('utf-8'))