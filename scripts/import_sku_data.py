#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKU物料数据导入脚本
整合多来源报价数据到数据库
"""

import pandas as pd
import json
import os
import sys
import re
from datetime import datetime

# 数据库字段映射
DB_FIELDS = {
    'sku_code': 'SKU编码',
    'name': '产品名称',
    'category_id': '分类ID',
    'brand': '品牌',
    'model': '型号',
    'specification': '规格参数',
    'material': '材质',
    'origin': '产地',
    'cost_price': '成本价',
    'sale_price': '销售价',
    'unit': '单位',
    'calc_type': '计价方式',
    'description': '描述',
    'tags': '标签',
}


def clean_price(price_val):
    """清理价格数据"""
    if pd.isna(price_val):
        return 0
    if isinstance(price_val, (int, float)):
        return float(price_val)
    # 处理字符串价格
    price_str = str(price_val).strip()
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(price_str) if price_str else 0
    except:
        return 0


def parse_specification(name):
    """从产品名称解析规格参数"""
    spec_parts = []
    
    # 提取尺寸 (如 1.8m, 1800*2000, 1800mm等)
    size_patterns = [
        r'(\d+[\d\s*×xX*\s]*\d*)\s*[m米㎡]',
        r'(\d{3,4}[\s*×xX*\s]*\d{3,4})',
    ]
    for pattern in size_patterns:
        match = re.search(pattern, name)
        if match:
            spec_parts.append(f"尺寸:{match.group(1)}")
            break
    
    # 提取厚度
    thickness_match = re.search(r'(\d+)\s*[mM][mM]', name)
    if thickness_match:
        spec_parts.append(f"厚度:{thickness_match.group(1)}mm")
    
    return '; '.join(spec_parts) if spec_parts else name


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
            # 解析产品名称
            name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
            category = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''
            
            # 价格（零售价）
            sale_price = clean_price(row.iloc[14])  # 销售价格列
            
            # 成本价（如果有）
            cost_price = clean_price(row.iloc[12]) if pd.notna(row.iloc[12]) else sale_price * 0.6
            
            record = {
                'sku_code': str(row.iloc[0]) if pd.notna(row.iloc[0]) else f'BG-{idx+1:05d}',
                'name': name,
                'category_name': category,
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
                'price_type': 'retail',
            }
            records.append(record)
        except Exception as e:
            print(f"  ⚠️ 第 {idx+1} 行处理失败: {e}")
            continue
    
    print(f"✅ 成功解析 {len(records)} 条记录")
    return records


def import_furniture_data():
    """导入成品家具数据（帝标供应链 - 成本价，零售价3倍）"""
    print("\n" + "=" * 60)
    print("【2/4】导入成品家具数据（成本价×3=零售价）")
    print("=" * 60)
    
    files = [
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟eclectic批发报价.pdf', '高晟eclectic'),
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟大师系列批发价.pdf', '高晟大师系列'),
    ]
    
    records = []
    for file_path, brand_name in files:
        if not os.path.exists(file_path):
            print(f"⚠️ 跳过不存在文件: {file_path}")
            continue
        
        print(f"📄 处理: {brand_name}")
        # PDF处理需要额外库，这里先标记
        print(f"  ⏳ PDF解析待实现，文件: {os.path.basename(file_path)}")
    
    print(f"✅ 家具数据导入完成（PDF需手动处理或提供Excel版本）")
    return records


def import_construction_data():
    """导入硬装施工与材料数据（成本价×1.5=零售价）"""
    print("\n" + "=" * 60)
    print("【3/4】导入硬装施工与材料数据（成本价×1.5=零售价）")
    print("=" * 60)
    
    files = [
        (r'D:\desktop\报价标准数据库\鲁班材料.xlsx', '鲁班材料'),
        (r'D:\desktop\报价标准数据库\袁伟全案报价(1)(1).xlsx', '袁伟全案'),
    ]
    
    records = []
    for file_path, source_name in files:
        if not os.path.exists(file_path):
            print(f"⚠️ 跳过不存在文件: {file_path}")
            continue
        
        print(f"📄 处理: {source_name}")
        try:
            xl = pd.ExcelFile(file_path)
            print(f"  Sheets: {xl.sheet_names}")
            
            # 读取第一个sheet
            df = pd.read_excel(file_path, sheet_name=0)
            print(f"  行数: {len(df)}")
            print(f"  列名: {list(df.columns)[:5]}...")
            
            # 这里需要根据实际列名映射
            # 暂时记录结构待后续处理
            records.append({
                'source': source_name,
                'file': file_path,
                'sheets': xl.sheet_names,
                'rows': len(df),
                'columns': list(df.columns),
            })
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
    
    return records


def generate_import_sql(records):
    """生成SQL导入语句"""
    print("\n" + "=" * 60)
    print("【4/4】生成导入SQL")
    print("=" * 60)
    
    if not records:
        print("⚠️ 没有数据需要导入")
        return
    
    # 分类统计
    categories = {}
    for r in records:
        cat = r.get('category_name', '未分类')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"📊 数据统计:")
    print(f"  总记录数: {len(records)}")
    print(f"  分类数: {len(categories)}")
    print(f"\n  分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"    - {cat}: {count}条")
    
    # 生成SQL文件
    sql_file = os.path.join(os.path.dirname(__file__), 'sku_import.sql')
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- SKU物料数据导入脚本\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- 注意: 先确保material_category表中有对应分类\n\n")
        
        f.write("BEGIN TRANSACTION;\n\n")
        
        # 插入分类（如果不存在）
        f.write("-- 插入分类\n")
        for cat in sorted(categories.keys()):
            if cat and cat != 'nan':
                f.write(f"INSERT OR IGNORE INTO material_category (name, code, level) VALUES ('{cat}', '{cat}', 1);\n")
        
        f.write("\n-- 插入SKU数据\n")
        for r in records[:100]:  # 先导出前100条作为示例
            f.write(f"""INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    '{r.get('sku_code', '')}',
    '{r.get('name', '').replace("'", "''")}',
    (SELECT id FROM material_category WHERE name = '{r.get('category_name', '')}'),
    '{r.get('brand', '')}',
    '{r.get('model', '')}',
    '{r.get('specification', '').replace("'", "''")}',
    '{r.get('material', '')}',
    {r.get('cost_price', 0)},
    {r.get('sale_price', 0)},
    '{r.get('unit', '件')}',
    '{r.get('calc_type', 'quantity')}',
    '{r.get('description', '').replace("'", "''")}',
    'active',
    datetime('now')
);\n""")
        
        f.write("\nCOMMIT;\n")
    
    print(f"\n✅ SQL文件已生成: {sql_file}")
    
    # 同时生成JSON备份
    json_file = os.path.join(os.path.dirname(__file__), 'sku_data_backup.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON备份已生成: {json_file}")


def main():
    """主函数"""
    print("🚀 SKU物料数据导入工具")
    print("=" * 60)
    
    all_records = []
    
    # 1. 导入后台报价数据
    backend_records = import_backend_data()
    all_records.extend(backend_records)
    
    # 2. 导入成品家具数据
    furniture_records = import_furniture_data()
    all_records.extend(furniture_records)
    
    # 3. 导入硬装数据
    construction_records = import_construction_data()
    
    # 4. 生成SQL
    generate_import_sql(all_records)
    
    print("\n" + "=" * 60)
    print("🎉 处理完成!")
    print("=" * 60)
    print("\n下一步:")
    print("1. 检查生成的SQL文件")
    print("2. 在数据库中执行SQL导入")
    print("3. 对于PDF文件，建议转换为Excel后手动处理")


if __name__ == '__main__':
    main()
