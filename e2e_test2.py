import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        # Try different login field names
        login_res = client.post('/api/v3/auth/login', json={
            'account': 'admin',
            'password': 'admin123'
        })
        import json
        if login_res.status_code != 200:
            # Try another field
            login_res = client.post('/api/v3/auth/login', json={
                'username': 'admin',
                'password': 'admin123',
                'account': 'admin'
            })
        if login_res.status_code != 200:
            login_data = json.loads(login_res.data)
            print(f"Login failed: {login_data}")
            # Check available auth routes
            print("\nTrying direct DB approach instead...")
            
            # Direct test: use app context to create and read materials
            from app.models.case import CaseSpaceMaterial, db
            # Find a space
            from app.models.case import CaseSpaceRendering
            space = CaseSpaceRendering.query.filter_by(case_id=37).first()
            if not space:
                print("No spaces found for case 37")
                sys.exit(1)
            print(f"Space: id={space.id}, name={space.space_name}")
            
            # Delete old
            CaseSpaceMaterial.query.filter_by(space_id=space.id).delete()
            
            # Create with all fields
            m = CaseSpaceMaterial(
                space_id=space.id,
                case_id=37,
                space_name=space.space_name,
                sku_id=1,
                sku_code='SKU001',
                material_name='测试电视柜',
                material_image='',
                category_level1='固装家具',
                category_level2='柜体',
                brand='测试品牌',
                spec='1200*600mm',
                unit='个',
                quantity=2,
                unit_price=500,
                total_price=1000,
                env_level='E0',
                supply_chain='直供',
                color_name='白色',
                custom_name='客厅电视柜',
                custom_measure='2.64m²',
                material='板材',
                width=1200,
                depth=600,
                height=2200,
            )
            db.session.add(m)
            db.session.commit()
            
            # Read back
            saved = CaseSpaceMaterial.query.filter_by(space_id=space.id).first()
            d = saved.to_dict()
            print(f"\nRead back from DB:")
            for f in ['custom_name', 'category_level1', 'category_level2', 'custom_measure', 'width', 'depth', 'height', 'material', 'color_name']:
                val = d.get(f)
                status = '✅' if val not in [None, '', 0] else '❌'
                print(f"  {status} {f}: {val!r}")
