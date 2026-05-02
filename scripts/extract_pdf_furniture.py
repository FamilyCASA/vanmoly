#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF家具报价数据提取脚本
从帝标供应链PDF中提取家具数据并转换为Excel
"""

import pdfplumber
import pandas as pd
import os
import re
import json
from datetime import datetime


def clean_price(price_str):
    """清理价格字符串"""
    if not price_str:
        return 0
    price_str = str(price_str).strip()
    # 提取数字
    match = re.search(r'[\d,]+\.?\d*', price_str)
    if match:
        return float(match.group().replace(',', ''))
    return 0


def extract_furniture_from_pdf(pdf_path, brand_name):
    """从PDF提取家具数据"""
    print(f"\n{'='*60}")
    print(f"处理: {brand_name}")
    print(f"文件: {pdf_path}")
    print('='*60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return []
    
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📄 总页数: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\n  处理第 {page_num} 页...")
            
            # 提取表格
            tables = page.extract_tables()
            
            if tables:
                for table_idx, table in enumerate(tables):
                    print(f"    发现表格 {table_idx+1}, 行数: {len(table)}")
                    
                    # 分析表格结构
                    if len(table) > 1:
                        # 尝试识别表头
                        header = table[0]
                        print(f"    表头: {header}")
                        
                        # 遍历数据行
                        for row_idx, row in enumerate(table[1:], 1):
                            try:
                                # 清理数据
                                row = [str(cell).strip() if cell else '' for cell in row]
                                
                                # 过滤空行
                                if not any(row):
                                    continue
                                
                                # 尝试提取关键字段
                                record = {
                                    'page': page_num,
                                    'table': table_idx + 1,
                                    'row': row_idx,
                                    'raw_data': row,
                                    'brand': brand_name,
                                    'source_file': os.path.basename(pdf_path),
                                }
                                
                                # 智能字段映射
                                for i, cell in enumerate(row):
                                    cell_lower = cell.lower()
                                    
                                    # 产品名称
                                    if any(kw in cell_lower for kw in ['型号', '产品', '名称', '款号']):
                                        record['name'] = cell
                                    # 价格
                                    elif any(kw in cell_lower for kw in ['价格', '批发', '单价', '金额']):
                                        record['price'] = clean_price(cell)
                                    # 规格
                                    elif any(kw in cell_lower for kw in ['规格', '尺寸', 'cm', 'mm']):
                                        record['specification'] = cell
                                    # 材质
                                    elif any(kw in cell_lower for kw in ['材质', '面料', '材料']):
                                        record['material'] = cell
                                
                                records.append(record)
                                
                            except Exception as e:
                                print(f"      ⚠️ 行处理失败: {e}")
                                continue
            else:
                # 没有表格，尝试提取文本
                text = page.extract_text()
                if text:
                    print(f"    无表格，提取文本 ({len(text)} 字符)")
                    # 这里可以添加文本解析逻辑
    
    print(f"\n✅ 共提取 {len(records)} 条记录")
    return records


def analyze_and_structure(records):
    """分析并结构化数据"""
    print(f"\n{'='*60}")
    print("数据结构化分析")
    print('='*60)
    
    if not records:
        print("⚠️ 没有数据需要处理")
        return []
    
    structured_records = []
    
    for r in records:
        raw = r.get('raw_data', [])
        
        # 尝试从原始数据中提取信息
        # 假设常见的列顺序: 序号 | 型号/名称 | 规格 | 材质 | 价格 | 备注
        
        name = ''
        spec = ''
        material = ''
        cost_price = 0
        
        # 遍历原始数据列
        for i, cell in enumerate(raw):
            cell_str = str(cell).strip()
            
            # 跳过序号列
            if i == 0 and cell_str.isdigit():
                continue
            
            # 识别价格（包含数字和常见价格标记）
            if re.search(r'\d+\.?\d*', cell_str) and any(kw in cell_str for kw in ['元', '￥', '$', '价格']):
                cost_price = clean_price(cell_str)
            # 识别规格（包含尺寸单位）
            elif any(unit in cell_str for unit in ['cm', 'mm', 'm', 'CM', 'MM', 'M', '×', 'x', '*']):
                spec = cell_str
            # 识别材质
            elif any(kw in cell_str for kw in ['皮', '布', '木', '金属', '玻璃', '大理石']):
                material = cell_str
            # 产品名称（较长的文本，不含数字）
            elif len(cell_str) > 2 and not cell_str.replace('.', '').isdigit():
                if not name:
                    name = cell_str
        
        # 如果没有提取到名称，使用第一个非空文本
        if not name:
            for cell in raw[1:]:
                if cell and len(str(cell)) > 2:
                    name = str(cell)
                    break
        
        # 生成SKU编码
        sku_code = f"{r['brand'][:2].upper()}-{r['page']:02d}{r['table']:02d}{r['row']:03d}"
        
        structured = {
            'sku_code': sku_code,
            'name': name or '未命名产品',
            'category_name': '成品家具',
            'brand': r['brand'],
            'model': '',
            'specification': spec,
            'material': material,
            'origin': '',
            'cost_price': cost_price,
            'sale_price': round(cost_price * 3, 2) if cost_price > 0 else 0,  # 成本×3
            'unit': '件',
            'calc_type': 'quantity',
            'description': f"来源: {r['source_file']} 第{r['page']}页",
            'source': r['brand'],
            'raw_data': '|'.join(raw),  # 保留原始数据
        }
        
        structured_records.append(structured)
    
    print(f"✅ 结构化完成: {len(structured_records)} 条")
    return structured_records


def save_to_excel(records, output_path):
    """保存到Excel"""
    if not records:
        print("⚠️ 没有数据需要保存")
        return
    
    df = pd.DataFrame(records)
    
    # 选择主要字段
    main_columns = [
        'sku_code', 'name', 'category_name', 'brand', 'specification',
        'material', 'cost_price', 'sale_price', 'unit', 'description', 'source'
    ]
    
    # 只保留存在的列
    columns = [c for c in main_columns if c in df.columns]
    df = df[columns]
    
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"✅ Excel已保存: {output_path}")
    print(f"   共 {len(df)} 行, {len(df.columns)} 列")


def main():
    """主函数"""
    print("🚀 PDF家具数据提取工具")
    print("="*60)
    
    # PDF文件列表
    pdf_files = [
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟eclectic批发报价.pdf', '高晟eclectic'),
        (r'D:\desktop\报价标准数据库\帝标供应链\25年9月高晟大师系列批发价.pdf', '高晟大师系列'),
    ]
    
    all_records = []
    
    for pdf_path, brand_name in pdf_files:
        records = extract_furniture_from_pdf(pdf_path, brand_name)
        all_records.extend(records)
    
    print(f"\n{'='*60}")
    print(f"总计提取: {len(all_records)} 条原始记录")
    print('='*60)
    
    # 数据结构化
    structured = analyze_and_structure(all_records)
    
    # 保存原始数据
    raw_json = os.path.join(os.path.dirname(__file__), 'furniture_raw.json')
    with open(raw_json, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 原始数据已保存: {raw_json}")
    
    # 保存结构化数据
    structured_json = os.path.join(os.path.dirname(__file__), 'furniture_structured.json')
    with open(structured_json, 'w', encoding='utf-8') as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    print(f"✅ 结构化数据已保存: {structured_json}")
    
    # 保存Excel
    excel_path = os.path.join(os.path.dirname(__file__), 'furniture_import.xlsx')
    save_to_excel(structured, excel_path)
    
    print("\n" + "="*60)
    print("🎉 处理完成!")
    print("="*60)
    print("\n输出文件:")
    print(f"  1. furniture_raw.json - 原始提取数据")
    print(f"  2. furniture_structured.json - 结构化数据")
    print(f"  3. furniture_import.xlsx - Excel导入文件")
    print("\n下一步:")
    print("  请检查Excel文件，确认数据正确后导入数据库")


if __name__ == '__main__':
    main()
