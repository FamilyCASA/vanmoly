#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKU物料数据完整导入脚本
整合所有来源报价数据到数据库
"""

import pandas as pd
import json
import os
import sys
import re
import sqlite3
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'instance', 'vanmoly_v3.db')


def clean_price(price_val):
    """清理价格数据"""
    if pd.isna(price_val):
        return 0
    if isinstance(price_val, (int, float)):
        return float(price_val)
    price_str = str(price_val).strip()
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(price_str) if price_str else 0
    except:
        return 0


def parse_specification(name):
    """从产品名称解析规格参数"""
    spec_parts = []
    size_patterns = [
        r'(\d+[\d\s*×xX*\s]*\d*)\s*[m米㎡]',
        r'(\d{3,4}[\s*×xX*\s]*\d{3,4})',
    ]
    for pattern in size_patterns:
        match = re.search(pattern, name)
        if match:
            spec_parts.append(f"尺寸:{match.group(1)}")
            break
    thickness_match = re.search(r'(\d+)\s*[mM][mM]', name)
    if thickness_match:
        spec_parts.append(f"厚度:{thickness_match.group(1)}mm")
    return '; '.join(spec_parts) if spec_parts else ''


def import_backend_data():
    """导入后台报价数据（零售价）"""
    print("=" * 60)
    print("【1/4】导入后台报价数据（零售价）")
    print("=" * 60)
    
    file_path = r'D:\desktop\vanmoly-distilled\docs\后台报价数据\报价数据库.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return []
    
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"📊 读取到 {len(df)} 条记录")
    
    records = []
    for idx, row in df.iterrows():
        try:
            name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
            category = str(row.iloc[2]) if pd.notna(row.iloc[2]) else '未分类'
            sale_price = clean_price(row.iloc[14])
            cost_price = clean_price(row.iloc[12]) if pd.notna(row.iloc[12]) else sale_price * 0.6
            
            record = {
                'sku_code': str(row.iloc[0]) if pd.notna(row.iloc[0]) else f'BG-{idx+1:05d}',
                'name': name,
                'category_name': category if category != 'nan' else '未分类',
                'brand': str(row.iloc[6]) if pd.notna(row.iloc[6]) else '',
                'model': str(row.iloc[7]) if pd.notna(row.iloc[7]) else '',
                'specification': parse_specification(name),
                'material': str(row.iloc[4]) if pd.notna(row.iloc[4]) else '',
                'origin': str(row.iloc[17]) if pd.notna(row.iloc[17]) else '',
                'cost_price': round(cost_price, 2),
                'sale_price': round(sale_price, 2),
                'unit': str(row.iloc[15]) if pd.notna(row.iloc[15]) else '件',
                'calc_type': 'quantity',
                'description': str(row.iloc[16]) if pd.notna(row.iloc[16]) else '',
                'source': '后台报价数据',
            }
            records.append(record)
        except Exception as e:
            print(f"  ⚠️ 第 {idx+1} 行处理失败: {e}")
            continue
    
    print(f"✅ 成功解析 {len(records)} 条记录")
    return records


def import_luban_data():
    """导入鲁班材料数据（成本价×1.5=零售价）"""
    print("\n" + "=" * 60)
    print("【2/4】导入鲁班材料数据（成本价×1.5=零售价）")
    print("=" * 60)
    
    file_path = r'D:\desktop\报价标准数据库\鲁班材料.xlsx'
    
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在: {file_path}")
        return []
    
    # 读取Sheet1（辅材）
    df1 = pd.read_excel(file_path, sheet_name='Sheet1', header=1)
    # 读取Sheet2（主材）
    df2 = pd.read_excel(file_path, sheet_name='Sheet2', header=0)
    
    records = []
    
    # 处理辅材
    print(f"📋 辅材: {len(df1)} 条")
    for idx, row in df1.iterrows():
        try:
            if pd.isna(row.iloc[1]):
                continue
            name = str(row.iloc[1])
            spec = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''
            brand = str(row.iloc[5]) if pd.notna(row.iloc[5]) else ''
            origin = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ''
            desc = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''
            
            record = {
                'sku_code': f'LB-FC-{idx+1:03d}',
                'name': name,
                'category_name': '辅材',
                'brand': brand,
                'model': '',
                'specification': spec,
                'material': '',
                'origin': origin,
                'cost_price': 0,
                'sale_price': 0,
                'unit': '项',
                'calc_type': 'quantity',
                'description': desc,
                'source': '鲁班材料-辅材',
            }
            records.append(record)
        except Exception as e:
            continue
    
    # 处理主材
    print(f"📋 主材: {len(df2)} 条")
    for idx, row in df2.iterrows():
        try:
            if pd.isna(row.iloc[0]):
                continue
            name = str(row.iloc[0])
            
            record = {
                'sku_code': f'LB-ZC-{idx+1:03d}',
                'name': name,
                'category_name': '主材',
                'brand': '',
                'model': '',
                'specification': '',
                'material': '',
                'origin': '',
                'cost_price': 0,
                'sale_price': 0,
                'unit': '项',
                'calc_type': 'quantity',
                'description': '',
                'source': '鲁班材料-主材',
            }
            records.append(record)
        except Exception as e:
            continue
    
    print(f"✅ 成功解析 {len(records)} 条记录")
    return records


def import_yuanwei_data():
    """导入袁伟全案报价数据（成本价×1.5=零售价）"""
    print("\n" + "=" * 60)
    print("【3/4】导入袁伟全案报价数据（成本价×1.5=零售价）")
    print("=" * 60)
    
    file_path = r'D:\desktop\报价标准数据库\袁伟全案报价(1)(1).xlsx'
    
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在: {file_path}")
        return []
    
    df = pd.read_excel(file_path, sheet_name='袁伟报价', header=0)
    print(f"📊 读取到 {len(df)} 条记录")
    
    records = []
    for idx, row in df.iterrows():
        try:
            name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
            if name in ['全案服务项目', 'nan', '']:
                continue
            
            unit = str(row.iloc[1]) if pd.notna(row.iloc[1]) else '项'
            cost_price = clean_price(row.iloc[2])
            sale_price = round(cost_price * 1.5, 2) if cost_price > 0 else 0
            desc = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ''
            category = str(row.iloc[4]) if pd.notna(row.iloc[4]) else '施工项目'
            
            record = {
                'sku_code': f'YW-{idx+1:04d}',
                'name': name,
                'category_name': category,
                'brand': '',
                'model': '',
                'specification': '',
                'material': '',
                'origin': '',
                'cost_price': cost_price,
                'sale_price': sale_price,
                'unit': unit,
                'calc_type': 'quantity',
                'description': desc,
                'source': '袁伟全案报价',
            }
            records.append(record)
        except Exception as e:
            continue
    
    print(f"✅ 成功解析 {len(records)} 条记录")
    return records


def import_furniture_from_pdf():
    """导入成品家具数据（PDF需要手动转换）"""
    print("\n" + "=" * 60)
    print("【4/4】成品家具数据（PDF待处理）")
    print("=" * 60)
    
    files = [
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟eclectic批发报价.pdf', '高晟eclectic'),
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟大师系列批发价.pdf', '高晟大师系列'),
    ]
    
    for file_path, brand_name in files:
        if os.path.exists(file_path):
            print(f"📄 {brand_name}: {file_path}")
            print(f"   ⚠️ PDF文件需要转换为Excel后导入")
            print(f"   建议: 使用Adobe Acrobat或在线工具转换为Excel")
    
    return []


def init_database():
    """初始化数据库表"""
    print("\n" + "=" * 60)
    print("初始化数据库")
    print("=" * 60)
    
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
    print(f"✅ 数据库初始化完成: {DB_PATH}")


def insert_to_database(all_records):
    """插入数据到数据库"""
    print("\n" + "=" * 60)
    print("插入数据到数据库")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 统计分类
    categories = {}
    for r in all_records:
        cat = r.get('category_name', '未分类')
        if cat and cat != 'nan':
            categories[cat] = categories.get(cat, 0) + 1
    
    print(f"📊 发现 {len(categories)} 个分类")
    
    # 插入分类
    category_map = {}
    for cat_name in categories.keys():
        cursor.execute('''
            INSERT OR IGNORE INTO material_category (name, code, level, tenant_id)
            VALUES (?, ?, 1, '0')
        ''', (cat_name, cat_name))
        
        cursor.execute('SELECT id FROM material_category WHERE name = ?', (cat_name,))
        result = cursor.fetchone()
        if result:
            category_map[cat_name] = result[0]
    
    print(f"✅ 分类插入完成")
    
    # 插入SKU
    inserted = 0
    skipped = 0
    
    for r in all_records:
        try:
            category_id = category_map.get(r.get('category_name', '未分类'))
            
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
            print(f"  ⚠️ 插入失败 {r.get('sku_code')}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据插入完成: 成功 {inserted} 条, 跳过 {skipped} 条")


def main():
    """主函数"""
    print("[START] SKU物料数据完整导入工具")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    
    all_records = []
    
    # 1. 后台报价数据
    backend_records = import_backend_data()
    all_records.extend(backend_records)
    
    # 2. 鲁班材料
    luban_records = import_luban_data()
    all_records.extend(luban_records)
    
    # 3. 袁伟全案
    yuanwei_records = import_yuanwei_data()
    all_records.extend(yuanwei_records)
    
    # 4. 家具PDF（提示）
    import_furniture_from_pdf()
    
    print("\n" + "=" * 60)
    print(f"📊 总计: {len(all_records)} 条记录待导入")
    print("=" * 60)
    
    # 插入数据库
    insert_to_database(all_records)
    
    # 保存备份
    json_file = os.path.join(os.path.dirname(__file__), 'sku_imported.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 数据备份已保存: {json_file}")
    
    print("\n" + "=" * 60)
    print("[DONE] 导入完成!")
    print("=" * 60)
    print("\n提示:")
    print("- 成品家具PDF需要转换为Excel后手动导入")
    print("- 数据库位置: backend/instance/material.db")
    print("- 可在管理后台查看导入的物料数据")


if __name__ == '__main__':
    main()
