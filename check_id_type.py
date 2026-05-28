import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        resp = client.get('/api/v3/materials/categories')
        import json
        data = json.loads(resp.data)
        cats = data.get('data', data) if isinstance(data, dict) else data
        
        if isinstance(cats, list):
            for c in cats:
                if c.get('name') == '固装家具':
                    print(f"L1: id={c['id']} (type={type(c['id']).__name__}), name={c['name']}")
                    for ch in (c.get('children') or []):
                        if ch.get('name') in ['投影报价', '柜门']:
                            print(f"  L2: id={ch['id']} (type={type(ch['id']).__name__}), name={ch['name']}")
                    break
