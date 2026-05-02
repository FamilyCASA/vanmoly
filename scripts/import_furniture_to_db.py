#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家具数据导入数据库脚本
将PDF提取的家具数据导入material.db
"""

import json
import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'instance', 'material.db')

def init_database():
    """确保数据库和表存在"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS material_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT DEFAULT '0',
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            parent_id INTEGER,
            level INTEGER DEFAULT 1,
            icon TEXT,
            color TEXT DEFAULT '#8B5A2B',
            sort_order INTEGER DEFAULT 0,
            is_enabled BOOLEAN DEFAULT 1,
            is_deleted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建SKU表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS material_sku (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT DEFAULT '0',
            sku_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category_id INTEGER,
            brand TEXT,
            model TEXT,
            specification TEXT,
            material TEXT,
            origin TEXT,
            main_image TEXT,
            images TEXT,
            cost_price REAL DEFAULT 0,
            sale_price REAL DEFAULT 0,
            market_price REAL,
            unit TEXT DEFAULT '件',
            calc_type TEXT DEFAULT 'quantity',
            stock_quantity INTEGER DEFAULT 0,
            stock_warning INTEGER DEFAULT 10,
            customization_rules TEXT,
            has_variants BOOLEAN DEFAULT 0,
            variant_options TEXT,
            has_craft_parts BOOLEAN DEFAULT 0,
            craft_parts TEXT,
            description TEXT,
            tags TEXT,
            status TEXT DEFAULT 'active',
            is_deleted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (category_id) REFERENCES material_category(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成")

def load_furniture_data():
    """加载家具数据"""
    json_file = os.path.join(os.path.dirname(__file__), 'furniture_structured.json')
    
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 加载了 {len(data)} 条家具数据")
    return data

def import_to_database(records):
    """导入数据到数据库"""
    print("\n" + "="*60)
    print("导入数据到数据库")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保分类存在
    categories = set()
    for r in records:
        cat = r.get('category_name', '成品家具')
        if cat:
            categories.add(cat)
    
    # 插入分类
    category_map = {}
    for cat_name in categories:
        cursor.execute('''
            INSERT OR IGNORE INTO material_category (name, code, level, tenant_id)
            VALUES (?, ?, 1, '0')
        ''', (cat_name, cat_name))
        
        cursor.execute('SELECT id FROM material_category WHERE name = ?', (cat_name,))
        result = cursor.fetchone()
        if result:
            category_map[cat_name] = result[0]
    
    print(f"✅ 分类处理完成: {len(categories)} 个")
    
    # 统计各品牌数量
    brand_stats = {}
    for r in records:
        brand = r.get('brand', '未知')
        brand_stats[brand] = brand_stats.get(brand, 0) + 1
    
    print(f"\n品牌分布:")
    for brand, count in sorted(brand_stats.items()):
        print(f"  - {brand}: {count}条")
    
    # 插入SKU
    inserted = 0
    skipped = 0
    errors = []
    
    for r in records:
        try:
            category_id = category_map.get(r.get('category_name', '成品家具'))
            
            cursor.execute('''
                INSERT OR IGNORE INTO material_sku (
                    sku_code, name, category_id, brand, model, specification,
                    material, origin, cost_price, sale_price, unit, calc_type,
                    description, status, tenant_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                r.get('sku_code', ''),
                r.get('name', ''),
                category_id,
                r.get('brand', ''),
                r.get('model', ''),
                r.get('specification', ''),
                r.get('material', ''),
                r.get('origin', ''),
                r.get('cost_price', 0),
                r.get('sale_price', 0),
                r.get('unit', '件'),
                r.get('calc_type', 'quantity'),
                r.get('description', ''),
                'active',
                '0'
            ))
            
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
                
            if inserted % 100 == 0:
                print(f"  已插入 {inserted} 条...")
                
        except Exception as e:
            errors.append(f"{r.get('sku_code')}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 导入完成!")
    print(f"   成功: {inserted} 条")
    print(f"   跳过: {skipped} 条")
    if errors:
        print(f"   错误: {len(errors)} 条")
        for err in errors[:5]:
            print(f"      {err}")

def show_statistics():
    """显示数据库统计"""
    print("\n" + "="*60)
    print("数据库统计")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总SKU数
    cursor.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted = 0")
    total_sku = cursor.fetchone()[0]
    
    # 分类统计
    cursor.execute('''
        SELECT c.name, COUNT(s.id) 
        FROM material_category c 
        LEFT JOIN material_sku s ON c.id = s.category_id AND s.is_deleted = 0
        GROUP BY c.id, c.name
        ORDER BY COUNT(s.id) DESC
    ''')
    cat_stats = cursor.fetchall()
    
    # 品牌统计
    cursor.execute('''
        SELECT brand, COUNT(*) 
        FROM material_sku 
        WHERE is_deleted = 0 AND brand != ''
        GROUP BY brand
        ORDER BY COUNT(*) DESC
    ''')
    brand_stats = cursor.fetchall()
    
    conn.close()
    
    print(f"\n总SKU数: {total_sku}")
    
    print(f"\n分类统计:")
    for cat, count in cat_stats:
        print(f"  - {cat}: {count}条")
    
    print(f"\n品牌统计 (前10):")
    for brand, count in brand_stats[:10]:
        print(f"  - {brand}: {count}条")

def main():
    """主函数"""
    print("🚀 家具数据导入数据库工具")
    print("="*60)
    
    # 初始化数据库
    init_database()
    
    # 加载数据
    records = load_furniture_data()
    
    if not records:
        print("⚠️ 没有数据需要导入")
        return
    
    # 导入数据库
    import_to_database(records)
    
    # 显示统计
    show_statistics()
    
    print("\n" + "="*60)
    print("🎉 全部完成!")
    print("="*60)

if __name__ == '__main__':
    main()
