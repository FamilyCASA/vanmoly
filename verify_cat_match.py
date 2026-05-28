import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        # Get categories
        resp = client.get('/api/v3/materials/categories')
        import json
        data = json.loads(resp.data)
        cats = data.get('data', data) if isinstance(data, dict) else data
        print(f"Categories type: {type(cats)}, count: {len(cats) if isinstance(cats, list) else 'N/A'}")
        
        if isinstance(cats, list) and len(cats):
            for c in cats[:3]:
                name = c.get('name', '')
                cid = c.get('id', '')
                children = c.get('children', [])
                child_names = [ch.get('name','') for ch in (children or [])]
                print(f"\nL1: id={cid} name={name}")
                print(f"  L2 children ({len(children)}): {child_names}")
        
        # Check DB values
        import sqlite3
        db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
        db.row_factory = sqlite3.Row
        cur = db.execute("SELECT DISTINCT category_level1, category_level2 FROM case_space_materials WHERE case_id=37")
        rows = cur.fetchall()
        print(f"\n--- DB saved categories ---")
        for r in rows:
            print(f"  L1={r['category_level1']!r}, L2={r['category_level2']!r}")
        db.close()
