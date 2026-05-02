import urllib.request
import json

def test(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            d = json.loads(r.read().decode('utf-8'))
            return d.get('data', {})
    except Exception as e:
        return {'error': str(e)}

base = 'http://localhost:5000/api/v3'

print('=== API测试 ===')
print('物料:', test(f'{base}/materials?page=1').get('total', 'ERR'))
print('分类:', len(test(f'{base}/materials/categories')))
print('客户:', test(f'{base}/customers?page=1').get('total', 'ERR'))
print('员工:', test(f'{base}/employees?page=1').get('total', 'ERR'))
print('合同:', test(f'{base}/contracts?page=1').get('total', 'ERR'))
print('楼盘:', test(f'{base}/buildings?page=1').get('total', 'ERR'))
print('报价:', test(f'{base}/quotes?page=1').get('total', 'ERR'))
print('方案:', test(f'{base}/schemes?page=1').get('total', 'ERR'))
