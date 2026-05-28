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
                name = c.get('name', '')
                children = c.get('children', [])
                child_names = [ch.get('name','') for ch in (children or [])]
                print(f"L1: {name} ({len(children)} children)")
                if '家具' in name or '固装' in name or any('家具' in cn or '固装' in cn or '投影' in cn or '柜门' in cn for cn in child_names):
                    print(f"  *** MATCH: {child_names}")
        
        # Also check material_sku categories directly from DB
        import sqlite3
        db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
        db.row_factory = sqlite3.Row
        cur = db.execute("SELECT DISTINCT category_level1, category_level2 FROM material_sku ORDER BY category_level1, category_level2")
        rows = cur.fetchall()
        print(f"\n--- material_sku DB categories ---")
        seen_l1 = set()
        for r in rows:
            l1 = r['category_level1'] or '(empty)'
            l2 = r['category_level2'] or '(empty)'
            if l1 not in seen_l1:
                print(f"L1: {l1}")
                seen_l1.add(l1)
            print(f"  L2: {l2}")
        db.close()
