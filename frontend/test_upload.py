import requests
import io

url = 'http://localhost:5173/api/v3/upload/image'
files = {'file': ('test.png', io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'fake png data'), 'image/png')}
resp = requests.post(url, files=files, timeout=10)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:500]}')