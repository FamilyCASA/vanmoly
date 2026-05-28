import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        resp = client.get('/api/v3/public/cases/37/slide-data')
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            import json
            data = json.loads(resp.data)
            inner = data.get('data', data)
            materials = inner.get('materials', [])
            print(f"Materials count: {len(materials)}")
            if materials:
                m = materials[0]
                print(f"\nFirst material:")
                for f in ['custom_name', 'category_level1', 'category_level2', 'custom_measure', 'width', 'depth', 'height', 'material', 'color_name', 'material_name']:
                    val = m.get(f)
                    status = '✅' if val not in [None, '', 0] else '❌'
                    print(f"  {status} {f}: {val!r}")
        else:
            print(f"Error: {resp.data[:300].decode('utf-8', errors='replace')}")
