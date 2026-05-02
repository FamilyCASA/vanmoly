# -*- coding: utf-8 -*-
import requests

# Login first
r = requests.post('http://localhost:8080/api/v3/auth/login', json={'identifier':'vanmoly','password':'Van9999'})
print('Login:', r.status_code)
token = r.json().get('data',{}).get('token')
headers = {'Authorization': f'Bearer {token}'}

# Test atmosphere filter
r2 = requests.get('http://localhost:8080/api/v3/cases?atmosphere=温馨', headers=headers)
print('Cases with atmosphere=温馨:', r2.status_code)
data = r2.json()
items = data.get('data',{}).get('items',[])
print('Count:', len(items))
if items:
    print('First case atmosphere:', items[0].get('atmosphere'))
    print('First case title:', items[0].get('title'))

# Test list all
r3 = requests.get('http://localhost:8080/api/v3/cases', headers=headers)
all_cases = r3.json().get('data',{}).get('items',[])
print('\nTotal cases:', len(all_cases))
print('Atmospheres:', set([c.get('atmosphere') for c in all_cases if c.get('atmosphere')]))