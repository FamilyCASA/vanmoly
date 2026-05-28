import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        # Test public API
        resp = client.get('/api/v3/public/cases/37/slide-data')
        print(f"Public API Status: {resp.status_code}")
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
                for k in ['width','depth','height','material','custom_name','custom_measure','category_level1','category_level2','color_name']:
                    print(f"  {k}: {m.get(k)}")
        else:
            print(f"Error: {resp.data[:500].decode('utf-8', errors='replace')}")
