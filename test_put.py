import urllib.request, json, urllib.error

# Login
login_data = json.dumps({'identifier': 'admin', 'password': 'van654321'}).encode()
login_req = urllib.request.Request(
    'http://localhost:8080/api/v3/auth/login',
    data=login_data,
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(login_req, timeout=5)
token = json.loads(resp.read().decode('utf-8')).get('data', {}).get('token', '')
print('Login OK')

# Simulate browser's exact form data (all fields potentially sent)
form_data = json.dumps({
    'name': '王学明',
    'phone': '13800138000',
    'email': 'test@test.com',
    'gender': None,
    'id_card': None,
    'birthday': None,
    'employee_no': 'VAN-001',
    'department_id': 1,
    'position_id': 1,
    'entry_date': '2015-02-03',
    'probation_end_date': None,
    'formal_date': None,
    'job_level': '15',
    'base_salary': None,
    'performance_ratio': None,
    'role': None,
    'status': None,
    'address': None,
    'emergency_contact': None,
    'emergency_phone': None,
    'remark': None,
    'avatar': None,
    'bio': None
}).encode()

req = urllib.request.Request(
    'http://localhost:8080/api/v3/employees/42',
    data=form_data,
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req, timeout=5)
    print('PUT OK:', resp.read().decode('utf-8')[:200])
except urllib.error.HTTPError as e:
    print('HTTPError', e.code)
    body = e.read().decode('utf-8')
    print('Body:', body[:500])
    # Also print Flask's server-side traceback
    try:
        body_json = json.loads(body)
        if 'data' in body_json and 'traceback' in str(body_json['data']):
            print('Traceback:', str(body_json['data'])[:1000])
    except:
        pass
except Exception as e:
    print('Error:', e)
