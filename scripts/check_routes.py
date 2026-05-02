"""检查运行中的服务路由"""
import urllib.request
import json

def check_routes():
    try:
        # 直接测试物料列表
        req = urllib.request.Request('http://localhost:5000/api/v3/materials?page=1&page_size=5')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_routes()
