import urllib.request
import json

req = urllib.request.Request('http://localhost:5000/api/v3/materials/stats')
try:
    with urllib.request.urlopen(req, timeout=5) as response:
        data = response.read().decode('utf-8')
        obj = json.loads(data)
        print('Total:', obj['data']['total'])
        print('Categories:', len(obj['data']['by_category']))
        for cat in obj['data']['by_category'][:5]:
            print(f"  - {cat['name']}: {cat['count']}项")
except Exception as e:
    print('Error:', e)
