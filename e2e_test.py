import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    with app.test_client() as client:
        # 1. Login to get JWT
        login_res = client.post('/api/v3/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        print(f"Login: {login_res.status_code}")
        if login_res.status_code != 200:
            print(f"Login error: {login_res.data[:300].decode('utf-8', errors='replace')}")
            sys.exit(1)
        
        import json
        login_data = json.loads(login_res.data)
        token = login_data.get('data', {}).get('access_token') or login_data.get('data', {}).get('token')
        if not token:
            # Try nested
            print(f"Login response keys: {list(login_data.get('data', {}).keys())}")
            sys.exit(1)
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Find a space for case 37
        spaces_res = client.get('/api/v3/cases/37/spaces', headers=headers)
        print(f"Spaces: {spaces_res.status_code}")
        spaces_data = json.loads(spaces_res.data)
        spaces = spaces_data.get('data', [])
        if spaces:
            space_id = spaces[0]['id']
            space_name = spaces[0].get('space_name', '')
            print(f"Using space: id={space_id}, name={space_name}")
        else:
            print("No spaces found!")
            sys.exit(1)
        
        # 3. Save material config with all fields
        save_res = client.put(f'/api/v3/spaces/{space_id}/full', 
            headers=headers,
            json={
                'configs': [{
                    'name': '测试电视柜',
                    'material_id': 1,
                    'sku_code': 'SKU001',
                    'brand': '测试品牌',
                    'material': '板材',
                    'spec': '1200*600mm',
                    'width': 1200,
                    'depth': 600,
                    'height': 2200,
                    'quantity': 2,
                    'price': 500,
                    'amount': 1000,
                    'unit': '个',
                    'main_image': '',
                    'env_level': 'E0',
                    'supply_chain': '直供',
                    'color_name': '白色',
                    'custom_name': '客厅电视柜',
                    'custom_measure': '2.64m²',
                    'category_level1': '固装家具',
                    'category_level2': '柜体'
                }]
            }
        )
        print(f"\nSave: {save_res.status_code}")
        save_data = json.loads(save_res.data)
        print(f"Save msg: {save_data.get('message', '')}")
        
        # 4. Read back and verify all fields
        read_res = client.get(f'/api/v3/spaces/{space_id}/materials', headers=headers)
        print(f"\nRead back: {read_res.status_code}")
        read_data = json.loads(read_res.data)
        items = read_data.get('data', [])
        if items:
            m = items[0]
            fields_to_check = ['custom_name', 'category_level1', 'category_level2', 'custom_measure', 'width', 'depth', 'height', 'material', 'color_name', 'env_level']
            print("\nField verification:")
            for f in fields_to_check:
                val = m.get(f)
                status = '✅' if val not in [None, '', 0] else '❌'
                print(f"  {status} {f}: {val!r}")
        else:
            print("No items returned!")
