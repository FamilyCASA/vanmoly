# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

# Login
login_data = json.dumps({'identifier': 'vanmoly', 'password': 'Van9999'}).encode()
req = urllib.request.Request('http://localhost:8080/api/v3/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
d = json.loads(resp.read())
token = d['data']['token']
print(f'Login OK, token: {token[:20]}...')

# Get case 36
req2 = urllib.request.Request('http://localhost:8080/api/v3/cases/36', headers={'Authorization': f'Bearer {token}'})
resp2 = urllib.request.urlopen(req2)
d2 = json.loads(resp2.read())
c = d2['data']
print(f'hero_images: {c.get("hero_images")}')
print(f'gallery: {c.get("gallery")}')
print(f'is_top: {c.get("is_top")}')
print(f'media count: {len(c.get("media", []))}')
print(f'cover_image: {c.get("cover_image")}')

# Test update is_top
update_data = json.dumps({'is_top': True}).encode()
req3 = urllib.request.Request('http://localhost:8080/api/v3/cases/36', data=update_data, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='PUT')
resp3 = urllib.request.urlopen(req3)
d3 = json.loads(resp3.read())
print(f'\nAfter update is_top=True: is_top={d3["data"].get("is_top")}')

# Revert
update_data2 = json.dumps({'is_top': False}).encode()
req4 = urllib.request.Request('http://localhost:8080/api/v3/cases/36', data=update_data2, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='PUT')
resp4 = urllib.request.urlopen(req4)
d4 = json.loads(resp4.read())
print(f'After revert is_top=False: is_top={d4["data"].get("is_top")}')
