import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. Fix create_material - add missing fields
old_create = """            has_craft_parts=data.get('has_craft_parts', False),
            craft_parts=data.get('craft_parts', []),
            description=data.get('description'),
            detail_content=data.get('detail_content'),
            tags=data.get('tags', []),
            status=data.get('status', 'active'),
            is_public=data.get('is_public', True),
            created_by=data.get('created_by')
        )"""

new_create = """            has_craft_parts=data.get('has_craft_parts', False),
            craft_parts=data.get('craft_parts', []),
            color_name=data.get('color_name', ''),
            env_level=data.get('env_level', '合格'),
            supply_chain=data.get('supply_chain', '直供'),
            description=data.get('description'),
            detail_content=data.get('detail_content'),
            tags=data.get('tags', []),
            status=data.get('status', 'active'),
            is_public=data.get('is_public', True),
            created_by=data.get('created_by')
        )"""

content = content.replace(old_create, new_create, 1)

# 2. Fix update_material - add missing fields  
old_update_start = content.find("def update_material(sku_id):")
if old_update_start > 0:
    # Find the sku field assignments in update_material
    old_update_fields = """            sku.has_craft_parts = data.get('has_craft_parts', sku.has_craft_parts)
            sku.craft_parts = data.get('craft_parts', sku.craft_parts)
            sku.description = data.get('description', sku.description)"""
    new_update_fields = """            sku.has_craft_parts = data.get('has_craft_parts', sku.has_craft_parts)
            sku.craft_parts = data.get('craft_parts', sku.craft_parts)
            sku.color_name = data.get('color_name', sku.color_name)
            sku.env_level = data.get('env_level', sku.env_level)
            sku.supply_chain = data.get('supply_chain', sku.supply_chain)
            sku.description = data.get('description', sku.description)"""
    content = content.replace(old_update_fields, new_update_fields, 1)

# 3. Add batch import endpoint after create_category
batch_import_code = '''

@material_bp.route('/materials/batch-import', methods=['POST'])
@jwt_required_v2
def batch_import_materials(current_user):
    """批量导入物料，自动创建不重复的L2分类"""
    data = request.get_json()
    if not data or 'items' not in data:
        return api_response(code=400, message='请提供物料列表(items)')
    
    items = data['items']
    if not items or not isinstance(items, list):
        return api_response(code=400, message='物料列表不能为空')
    
    # 加载所有现有分类（构建名称→ID映射）
    all_cats = MaterialCategory.query.filter_by(is_deleted=False).all()
    cat_name_map = {}  # "parent_id|name" → category object
    for c in all_cats:
        key = f"{c.parent_id or 0}|{c.name}"
        cat_name_map[key] = c
    # 也建立 L1 name → id 映射
    l1_name_map = {c.name: c for c in all_cats if c.level == 1 and not c.is_deleted}
    
    results = {'created': 0, 'skipped': 0, 'errors': [], 'new_categories': []}
    
    for idx, item in enumerate(items):
        try:
            l1_name = item.get('category_level1', '').strip()
            l2_name = item.get('category_level2', '').strip()
            
            if not l1_name:
                results['errors'].append(f'第{idx+1}行: 缺少一级分类')
                continue
            
            # 查找或创建 L1 分类
            l1_cat = l1_name_map.get(l1_name)
            if not l1_cat:
                l1_cat = MaterialCategory(
                    name=l1_name, level=1, sort_order=len(l1_name_map) + 1
                )
                db.session.add(l1_cat)
                db.session.flush()
                l1_name_map[l1_name] = l1_cat
                cat_name_map[f"0|{l1_name}"] = l1_cat
                results['new_categories'].append({'level': 1, 'name': l1_name, 'id': l1_cat.id})
            
            # 查找或创建 L2 分类
            category_id = l1_cat.id
            if l2_name:
                key = f"{l1_cat.id}|{l2_name}"
                l2_cat = cat_name_map.get(key)
                if not l2_cat:
                    # 查找现有最大sort_order
                    max_sort = db.session.query(db.func.max(MaterialCategory.sort_order)).filter_by(
                        parent_id=l1_cat.id, is_deleted=False
                    ).scalar() or 0
                    l2_cat = MaterialCategory(
                        name=l2_name, parent_id=l1_cat.id, level=2, sort_order=max_sort + 1
                    )
                    db.session.add(l2_cat)
                    db.session.flush()
                    cat_name_map[key] = l2_cat
                    results['new_categories'].append({'level': 2, 'name': l2_name, 'parent': l1_name, 'id': l2_cat.id})
                category_id = l2_cat.id
            
            # 检查SKU编码是否已存在
            sku_code = item.get('sku_code', '').strip()
            if sku_code:
                existing = MaterialSKU.query.filter_by(sku_code=sku_code).first()
                if existing:
                    results['skipped'] += 1
                    continue
            
            # 创建SKU
            sku = MaterialSKU(
                sku_code=sku_code or f"AUTO-{idx+1:05d}",
                name=item.get('name', '').strip(),
                category_id=category_id,
                brand=item.get('brand', ''),
                model=item.get('model', ''),
                specification=item.get('specification', ''),
                material=item.get('material', ''),
                origin=item.get('origin', ''),
                main_image=item.get('main_image', ''),
                color_name=item.get('color_name', ''),
                env_level=item.get('env_level', '合格'),
                supply_chain=item.get('supply_chain', '直供'),
                cost_price=float(item.get('cost_price', 0) or 0),
                sale_price=float(item.get('sale_price', 0) or 0),
                market_price=float(item.get('market_price', 0) or 0) if item.get('market_price') else None,
                unit=item.get('unit', '件'),
                calc_type=item.get('calc_type', 'quantity'),
                stock_quantity=int(item.get('stock_quantity', 0) or 0),
                description=item.get('description', ''),
                status=item.get('status', 'active'),
                is_public=item.get('is_public', True),
                created_by=current_user.id if current_user else None,
            )
            db.session.add(sku)
            results['created'] += 1
            
        except Exception as e:
            results['errors'].append(f'第{idx+1}行: {str(e)}')
            db.session.rollback()
            continue
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'批量导入失败: {str(e)}')
    
    return api_response(code=200, message=f'批量导入完成: 创建{results["created"]}条, 跳过{results["skipped"]}条, 新分类{len(results["new_categories"])}个',
                        data=results)
'''

# Insert after create_category function
anchor = """        return api_response(code=500, message=f'分类创建失败: {str(e)}')"""
# Find this in create_category
cat_create_end = content.find(anchor)
if cat_create_end > 0:
    insert_pos = cat_create_end + len(anchor)
    content = content[:insert_pos] + batch_import_code + content[insert_pos:]
    print("✅ 批量导入API已插入")
else:
    print("❌ 未找到create_category结尾锚点")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 后端路由更新完成:")
print("  - create_material: 补齐 color_name/env_level/supply_chain")
print("  - update_material: 补齐 color_name/env_level/supply_chain")
print("  - 新增 POST /materials/batch-import 批量导入API")
