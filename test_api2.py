import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:8080/api/v3/public/cases/37/slide-data'
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    body = e.read().decode('utf-8')
    print(body[:1000])
except Exception as e:
    print(f"Error: {e}")
