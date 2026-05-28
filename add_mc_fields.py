import sys; sys.stdout.reconfigure(encoding='utf-8')

# === 1. Add fields to CaseSpaceMaterial model ===
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Add 3 new columns before sort_order
old_sort = "    sort_order = db.Column(db.Integer, default=0, comment='排序')"
new_fields = """    # 自定义/材质
    custom_name = db.Column(db.String(200), comment='自定义商品名称')
    material = db.Column(db.String(100), comment='材质')
    custom_measure = db.Column(db.String(100), comment='定制计量值')

    sort_order = db.Column(db.Integer, default=0, comment='排序')"""

c = c.replace(old_sort, new_fields, 1)

# Add to to_dict
old_dict_end = "            'total_price': self.total_price,"
new_dict = """            'total_price': self.total_price,
            'custom_name': self.custom_name,
            'material': self.material,
            'custom_measure': self.custom_measure,"""

c = c.replace(old_dict_end, new_dict, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ CaseSpaceMaterial 模型已添加 custom_name/material/custom_measure")

# === 2. ALTER TABLE ===
import sqlite3
db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(case_space_materials)")
existing = {row[1] for row in cursor.fetchall()}

for col, col_type in [('custom_name', 'VARCHAR(200)'), ('material', 'VARCHAR(100)'), ('custom_measure', 'VARCHAR(100)')]:
    if col not in existing:
        cursor.execute(f"ALTER TABLE case_space_materials ADD COLUMN {col} {col_type}")
        print(f"  ✅ ALTER TABLE ADD {col}")
    else:
        print(f"  ⏭ {col} 已存在")

conn.commit()
conn.close()
print("✅ 数据库列已添加")

# === 3. Also add material field to MaterialSKU to_dict if missing ===
path2 = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\material_sku.py'
with open(path2, encoding='utf-8') as f:
    c2 = f.read()

# Check if material is in to_dict
if "'material'" not in c2[c2.find('def to_dict'):]:
    # Add material to to_dict
    c2 = c2.replace("'main_image': self.main_image,",
                     "'main_image': self.main_image,\n            'material': self.material,", 1)
    with open(path2, 'w', encoding='utf-8') as f:
        f.write(c2)
    print("✅ MaterialSKU.to_dict 添加 material 字段")
else:
    print("⏭ MaterialSKU.to_dict 已有 material 字段")

# === 4. Update backend route: save_space_materials_full ===
path3 = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path3, encoding='utf-8') as f:
    c3 = f.read()

# Find save_space_materials_full function and add new fields
idx = c3.find('def save_space_materials_full')
if idx > 0:
    # Find the section where fields are being set
    # Add custom_name, material, custom_measure to the create block
    old_create = "            m = CaseSpaceMaterial("
    # Find the create block
    create_idx = c3.find('m = CaseSpaceMaterial(', idx)
    if create_idx > 0:
        # Find the closing )
        paren_depth = 0
        end_create = create_idx
        for i in range(create_idx, min(create_idx + 2000, len(c3))):
            if c3[i] == '(':
                paren_depth += 1
            elif c3[i] == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    end_create = i + 1
                    break
        
        block = c3[create_idx:end_create]
        # Add fields if not present
        if 'custom_name' not in block:
            # Add before the closing )
            block_new = block.rstrip()
            if block_new.endswith(')'):
                block_new = block_new[:-1]
            # Add new fields from item data
            block_new += """,
                custom_name=item.get('custom_name', ''),
                material=item.get('material', ''),
                custom_measure=item.get('custom_measure', ''))"""
            c3 = c3[:create_idx] + block_new + c3[end_create:]
            print("✅ save_space_materials_full 添加 custom_name/material/custom_measure 创建逻辑")

# Find update_space_material and add new fields to update
idx2 = c3.find('def update_space_material')
if idx2 > 0:
    # Find the field assignments
    for field in ['custom_name', 'material', 'custom_measure']:
        if f"m.{field} =" not in c3[idx2:idx2+2000]:
            # Add after env_level
            old_env = "            m.env_level = data.get('env_level', m.env_level)"
            new_env = f"""            m.env_level = data.get('env_level', m.env_level)
            m.custom_name = data.get('custom_name', m.custom_name)
            m.material = data.get('material', m.material)
            m.custom_measure = data.get('custom_measure', m.custom_measure)"""
            # Only replace once in the update function area
            env_idx = c3.find(old_env, idx2)
            if env_idx > 0 and env_idx < idx2 + 2000:
                c3 = c3[:env_idx] + new_env + c3[env_idx + len(old_env):]
                print(f"✅ update_space_material 添加 {field} 更新逻辑")

with open(path3, 'w', encoding='utf-8') as f:
    f.write(c3)

# === 5. Update fallback SKU→dict mapping in get_slide_data ===
# When building dict from MaterialSKU, include material field
old_sku_dict = "'material_name': sku.material_name,"
new_sku_dict = """'material_name': sku.material_name,
                    'material': sku.material or '',"""
if old_sku_dict in c3 and "'material': sku.material" not in c3:
    c3 = c3.replace(old_sku_dict, new_sku_dict, 1)
    with open(path3, 'w', encoding='utf-8') as f:
        f.write(c3)
    print("✅ get_slide_data fallback dict 添加 material 字段")
else:
    # Already updated or different format
    with open(path3, 'w', encoding='utf-8') as f:
        f.write(c3)
    print("⏭ get_slide_data fallback dict 跳过（已存在或格式不同）")
