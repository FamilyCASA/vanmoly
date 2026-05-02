import urllib.request
import json

def test_url(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

base = 'http://localhost:5000'

# 无需认证的API
print('物料:', test_url(f'{base}/api/v3/materials?page=1')['data']['total'] if 'data' in test_url(f'{base}/api/v3/materials?page=1') else 'FAIL')
print('分类:', len(test_url(f'{base}/api/v3/materials/categories').get('data', [])))

# 健康检查
print('健康:', test_url(f'{base}/health'))
