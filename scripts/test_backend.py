"""测试后端API"""
import urllib.request
import json

def test_api():
    try:
        # 测试根路由
        req = urllib.request.Request('http://localhost:5000/api/v3/')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"API Root: {data}")
        
        # 测试物料列表
        req = urllib.request.Request('http://localhost:5000/api/v3/materials?page=1&page_size=5')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Materials: code={data.get('code')}, total={data.get('data', {}).get('total')}")
        
        # 测试分类
        req = urllib.request.Request('http://localhost:5000/api/v3/materials/categories')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Categories: code={data.get('code')}, count={len(data.get('data', []))}")
            
        print("\n✅ 后端服务运行正常!")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == '__main__':
    test_api()
