"""完整测试后端API"""
import urllib.request
import json

def test_api():
    base_url = 'http://localhost:5000'
    
    try:
        # 测试根路由
        req = urllib.request.Request(f'{base_url}/api/v3/')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"API Root: code={data.get('code')}")
        
        # 测试物料列表
        req = urllib.request.Request(f'{base_url}/api/v3/materials?page=1&page_size=5')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            total = data.get('data', {}).get('total', 0)
            items = data.get('data', {}).get('items', [])
            print(f"Materials: code={data.get('code')}, total={total}, items={len(items)}")
            if items:
                print(f"  First item: {items[0].get('sku_code')} - {items[0].get('name')}")
        
        # 测试分类
        req = urllib.request.Request(f'{base_url}/api/v3/materials/categories')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            cats = data.get('data', [])
            print(f"Categories: code={data.get('code')}, count={len(cats)}")
            if cats:
                print(f"  First category: {cats[0].get('name')}")
        
        # 测试统计
        req = urllib.request.Request(f'{base_url}/api/v3/materials/stats')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            stats = data.get('data', {})
            print(f"Stats: total={stats.get('total')}, active={stats.get('active')}, categories={stats.get('categories')}")
            
        print("\n[OK] API测试通过!")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    test_api()
