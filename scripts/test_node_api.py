import urllib.request
import json

def test(url):
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

base = 'http://localhost:8000/api/v3'

print('=== D&B 帝标|设记家API测试 ===')
print()

# 根路由
print('1. 根路由:')
resp = test(f'{base}/')
print(f"   版本: {resp.get('data', {}).get('version', 'ERR')}")
print(f"   模块: {', '.join(resp.get('data', {}).get('modules', []))}")
print()

# 物料
print('2. 物料模块:')
resp = test(f'{base}/materials?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print(f"   返回: {len(data.get('items', []))} 条")

resp = test(f'{base}/materials/categories')
print(f"   分类: {len(resp.get('data', []))} 个")

resp = test(f'{base}/materials/stats')
data = resp.get('data', {})
print(f"   统计: 物料{data.get('total', 0)} / 分类{data.get('categories', 0)}")
print()

# 客户
print('3. 客户模块:')
resp = test(f'{base}/customers?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

# 员工
print('4. 员工模块:')
resp = test(f'{base}/employees?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

# 合同
print('5. 合同模块:')
resp = test(f'{base}/contracts?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

# 楼盘
print('6. 楼盘模块:')
resp = test(f'{base}/buildings?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

# 报价
print('7. 报价模块:')
resp = test(f'{base}/quotes?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

# 方案
print('8. 方案模块:')
resp = test(f'{base}/schemes?page=1')
data = resp.get('data', {})
print(f"   总数: {data.get('total', 'ERR')}")
print()

print('=== 测试完成 ===')
