import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    from app.models.material_sku import MaterialSKU
    cols = [c.name for c in MaterialSKU.__table__.columns]
    print("MaterialSKU columns:", cols)
    has_wdh = all(f in cols for f in ['width', 'depth', 'height'])
    print(f"Has width/depth/height: {has_wdh}")
