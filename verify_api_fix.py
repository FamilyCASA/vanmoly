import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        resp = client.get('/api/v3/cases/37/slide-data')
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            import json
            data = json.loads(resp.data)
            inner = data.get('data', data)
            case = inner.get('case', {})
            print(f"Case title: {case.get('title', 'N/A')}")
            materials = inner.get('materials', [])
            print(f"Materials count: {len(materials)}")
            if materials:
                m = materials[0]
                print(f"First material keys: {list(m.keys())[:10]}")
                print(f"  width={m.get('width')}, depth={m.get('depth')}, height={m.get('height')}")
        else:
            print(f"Error: {resp.data[:500].decode('utf-8', errors='replace')}")
