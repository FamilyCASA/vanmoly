"""
迁移物料数据从 material.db 到 vanmoly_v3.db
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import sqlite3
from datetime import datetime

# 数据库路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
source_db = os.path.join(BASE_DIR, 'instance', 'material.db')
target_db = os.path.join(BASE_DIR, 'instance', 'vanmoly_v3.db')

def migrate_data():
    print("=" * 50)
    print("Material Data Migration")
    print("=" * 50)
    print(f"Source: {source_db}")
    print(f"Target: {target_db}")
    print()
    
    # 连接源数据库
    src_conn = sqlite3.connect(source_db)
    src_cursor = src_conn.cursor()
    
    # 连接目标数据库
    tgt_conn = sqlite3.connect(target_db)
    tgt_cursor = tgt_conn.cursor()
    
    try:
        # 1. 迁移分类
        print("Migrating categories...")
        src_cursor.execute("SELECT id, name, code, parent_id, level, icon, color, sort_order, is_enabled, is_deleted, created_at, updated_at FROM material_category WHERE is_deleted = 0")
        categories = src_cursor.fetchall()
        
        category_id_map = {}
        for cat in categories:
            (old_id, name, code, parent_id, level, icon, color, sort_order, 
             is_enabled, is_deleted, created_at, updated_at) = cat
            
            tgt_cursor.execute("""
                INSERT INTO material_category (name, code, parent_id, level, icon, color, sort_order, is_enabled, is_deleted, created_at, updated_at, tenant_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '0')
            """, (name, code, parent_id, level, icon, color, sort_order, is_enabled, is_deleted, created_at, updated_at))
            
            new_id = tgt_cursor.lastrowid
            category_id_map[old_id] = new_id
            
        tgt_conn.commit()
        print(f"  Migrated {len(categories)} categories")
        
        # 更新parent_id
        print("  Updating parent references...")
        for old_id, new_id in category_id_map.items():
            src_cursor.execute("SELECT parent_id FROM material_category WHERE id = ?", (old_id,))
            row = src_cursor.fetchone()
            if row and row[0] and row[0] in category_id_map:
                new_parent_id = category_id_map[row[0]]
                tgt_cursor.execute("UPDATE material_category SET parent_id = ? WHERE id = ?", (new_parent_id, new_id))
        tgt_conn.commit()
        
        # 2. 迁移SKU
        print("Migrating SKUs...")
        src_cursor.execute("""
            SELECT id, sku_code, name, category_id, brand, model, specification, material, origin,
                   main_image, images, cost_price, sale_price, market_price, unit, calc_type,
                   stock_quantity, stock_warning, customization_rules, has_variants, variant_options,
                   has_craft_parts, craft_parts, description, tags, status, is_deleted, created_at, updated_at
            FROM material_sku WHERE is_deleted = 0
        """)
        skus = src_cursor.fetchall()
        
        sku_count = 0
        for sku in skus:
            (old_id, sku_code, name, category_id, brand, model, specification, material, origin,
             main_image, images, cost_price, sale_price, market_price, unit, calc_type,
             stock_quantity, stock_warning, customization_rules, has_variants, variant_options,
             has_craft_parts, craft_parts, description, tags, status, is_deleted, created_at, updated_at) = sku
            
            # 转换category_id
            new_category_id = category_id_map.get(category_id) if category_id else None
            
            # 处理JSON字段
            if images:
                try:
                    import json
                    images = json.dumps(json.loads(images))
                except:
                    images = '[]'
            else:
                images = '[]'
                
            if customization_rules:
                try:
                    import json
                    customization_rules = json.dumps(json.loads(customization_rules))
                except:
                    customization_rules = '[]'
            else:
                customization_rules = '[]'
                
            if variant_options:
                try:
                    import json
                    variant_options = json.dumps(json.loads(variant_options))
                except:
                    variant_options = '[]'
            else:
                variant_options = '[]'
                
            if craft_parts:
                try:
                    import json
                    craft_parts = json.dumps(json.loads(craft_parts))
                except:
                    craft_parts = '[]'
            else:
                craft_parts = '[]'
                
            if tags:
                try:
                    import json
                    tags = json.dumps(json.loads(tags))
                except:
                    tags = '[]'
            else:
                tags = '[]'
            
            tgt_cursor.execute("""
                INSERT INTO material_sku (sku_code, name, category_id, brand, model, specification, material, origin,
                    main_image, images, cost_price, sale_price, market_price, unit, calc_type,
                    stock_quantity, stock_warning, customization_rules, has_variants, variant_options,
                    has_craft_parts, craft_parts, description, tags, status, is_deleted, created_at, updated_at, tenant_id, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '0', 1)
            """, (sku_code, name, new_category_id, brand, model, specification, material, origin,
                  main_image, images, cost_price, sale_price, market_price, unit, calc_type,
                  stock_quantity, stock_warning, customization_rules, has_variants, variant_options,
                  has_craft_parts, craft_parts, description, tags, status, is_deleted, created_at, updated_at))
            
            sku_count += 1
            
        tgt_conn.commit()
        print(f"  Migrated {sku_count} SKUs")
        
        # 3. 迁移变体
        print("Migrating variants...")
        src_cursor.execute("""
            SELECT v.id, v.sku_id, v.variant_code, v.variant_name, v.variant_values, v.image, 
                   v.price_adjustment, v.stock_quantity, v.is_deleted
            FROM material_variant v
            JOIN material_sku s ON v.sku_id = s.id
            WHERE v.is_deleted = 0 AND s.is_deleted = 0
        """)
        variants = src_cursor.fetchall()
        
        # 需要建立old_sku_id到new_sku_id的映射
        src_cursor.execute("SELECT id, sku_code FROM material_sku WHERE is_deleted = 0")
        sku_codes = {row[0]: row[1] for row in src_cursor.fetchall()}
        
        tgt_cursor.execute("SELECT id, sku_code FROM material_sku")
        new_sku_map = {row[1]: row[0] for row in tgt_cursor.fetchall()}
        
        variant_count = 0
        for var in variants:
            (old_id, old_sku_id, variant_code, variant_name, variant_values, image,
             price_adjustment, stock_quantity, is_deleted) = var
            
            sku_code = sku_codes.get(old_sku_id)
            if sku_code:
                new_sku_id = new_sku_map.get(sku_code)
                if new_sku_id:
                    if variant_values:
                        try:
                            import json
                            variant_values = json.dumps(json.loads(variant_values))
                        except:
                            variant_values = '{}'
                    else:
                        variant_values = '{}'
                    
                    tgt_cursor.execute("""
                        INSERT INTO material_variant (sku_id, variant_code, variant_name, variant_values, image, price_adjustment, stock_quantity, is_deleted)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (new_sku_id, variant_code, variant_name, variant_values, image, price_adjustment, stock_quantity, is_deleted))
                    variant_count += 1
        
        tgt_conn.commit()
        print(f"  Migrated {variant_count} variants")
        
        # 4. 迁移供应商
        print("Migrating suppliers...")
        src_cursor.execute("""
            SELECT id, name, code, contact_person, phone, email, address, status, is_deleted, created_at, updated_at
            FROM material_supplier WHERE is_deleted = 0
        """)
        suppliers = src_cursor.fetchall()
        
        for sup in suppliers:
            (old_id, name, code, contact_person, phone, email, address, status, is_deleted, created_at, updated_at) = sup
            
            tgt_cursor.execute("""
                INSERT INTO material_supplier (name, code, contact_person, phone, email, address, status, is_deleted, created_at, updated_at, tenant_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '0')
            """, (name, code, contact_person, phone, email, address, status, is_deleted, created_at, updated_at))
        
        tgt_conn.commit()
        print(f"  Migrated {len(suppliers)} suppliers")
        
        print()
        print("=" * 50)
        print("Migration Complete!")
        print("=" * 50)
        
        # 验证
        tgt_cursor.execute("SELECT COUNT(*) FROM material_category")
        print(f"Categories in target: {tgt_cursor.fetchone()[0]}")
        
        tgt_cursor.execute("SELECT COUNT(*) FROM material_sku")
        print(f"SKUs in target: {tgt_cursor.fetchone()[0]}")
        
        tgt_cursor.execute("SELECT COUNT(*) FROM material_variant")
        print(f"Variants in target: {tgt_cursor.fetchone()[0]}")
        
        tgt_cursor.execute("SELECT COUNT(*) FROM material_supplier")
        print(f"Suppliers in target: {tgt_cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        src_conn.close()
        tgt_conn.close()

if __name__ == '__main__':
    migrate_data()
