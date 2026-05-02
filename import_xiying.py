"""
西映品牌供应链数据导入脚本
将三个Excel文件的数据导入到物料数据库
"""
import json
import sqlite3
import re
from datetime import datetime

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'

def parse_price(price_val):
    """解析价格，返回数字"""
    if price_val is None:
        return None
    if isinstance(price_val, (int, float)):
        return float(price_val)
    if isinstance(price_val, str):
        # 提取数字
        nums = re.findall(r'\d+', price_val)
        if nums:
            return float(nums[0])
    return None

def clean_text(text):
    """清理文本"""
    if text is None:
        return None
    if isinstance(text, str):
        return text.strip().replace('\n', ' ').replace('  ', ' ')
    return str(text)

def import_chair_data():
    """导入餐椅数据"""
    with open('xiying_chair.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for row in data:
        # 跳过表头和空行
        if not row.get('Unnamed: 0') or row.get('Unnamed: 0') in ['须知', '产品信息', '序号', None]:
            continue
        
        model = clean_text(row.get('=DISPIMG("ID_01157989C4DA4EB0ADCBBCC5BADD81A7",1)'))
        if not model or model.startswith('=DISPIMG'):
            continue
            
        price = parse_price(row.get('Unnamed: 6'))
        if not price:
            continue
        
        spec = clean_text(row.get('Unnamed: 5'))
        desc = clean_text(row.get('24年度产品报价表-餐椅'))
        
        items.append({
            'sku_code': f'XY-CY-{model.replace(" ", "-").replace("\n", "")}',
            'name': f'西映 {model} 餐椅',
            'category': '餐椅',
            'category_code': 'furniture-dining-chair',
            'brand': '西映',
            'specification': spec,
            'description': desc,
            'cost_price': price,
            'sale_price': round(price * 1.5, 2),  # 成本价*1.5作为销售价
            'unit': '把',
            'status': 'active',
            'supplier': '西映',
            'created_at': datetime.now().isoformat()
        })
    
    return items

def import_table_data():
    """导入餐桌数据"""
    with open('xiying_table.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for row in data:
        if not row.get('Unnamed: 0') or row.get('Unnamed: 0') in ['产品信息', '序号', None]:
            continue
        
        model = clean_text(row.get('Unnamed: 1'))
        if not model:
            continue
        
        price = parse_price(row.get('Unnamed: 6'))
        if not price:
            continue
        
        spec = clean_text(row.get('Unnamed: 5'))
        desc = clean_text(row.get('24年度产品报价表-餐桌'))
        
        items.append({
            'sku_code': f'XY-CZ-{model.replace(" ", "-").replace("\n", "")}',
            'name': f'西映 {model} 餐桌',
            'category': '餐桌',
            'category_code': 'furniture-dining-table',
            'brand': '西映',
            'specification': spec,
            'description': desc,
            'cost_price': price,
            'sale_price': round(price * 1.5, 2),
            'unit': '张',
            'status': 'active',
            'supplier': '西映',
            'created_at': datetime.now().isoformat()
        })
    
    return items

def import_furniture_data():
    """导入家居配套数据（妆台、书桌、边几）"""
    with open('xiying_furniture.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = []
    for row in data:
        if not row.get('Unnamed: 0') or row.get('Unnamed: 0') in ['产品信息', '序号', None]:
            continue
        
        model = clean_text(row.get('Unnamed: 1'))
        if not model:
            continue
        
        price = parse_price(row.get('Unnamed: 6'))
        if not price:
            continue
        
        spec = clean_text(row.get('Unnamed: 5'))
        desc = clean_text(row.get('24年度产品报价表-妆台&书桌&边几'))
        
        # 根据型号判断分类
        category = '家居配套'
        category_code = 'furniture-accessory'
        prefix = 'XY-PJ'
        
        model_upper = model.upper()
        if '妆台' in model or 'ZT' in model_upper or 'SZT' in model_upper:
            category = '妆台'
            category_code = 'furniture-dressing-table'
            prefix = 'XY-ZT'
        elif '书桌' in model or 'DZ' in model_upper or 'SZ' in model_upper:
            category = '书桌'
            category_code = 'furniture-desk'
            prefix = 'XY-SZ'
        elif '边几' in model or 'BJ' in model_upper:
            category = '边几'
            category_code = 'furniture-side-table'
            prefix = 'XY-BJ'
        elif '柜' in model:
            category = '柜类'
            category_code = 'furniture-cabinet'
            prefix = 'XY-G'
        elif '凳' in model or '椅' in model:
            category = '椅凳'
            category_code = 'furniture-stool'
            prefix = 'XY-YD'
        
        items.append({
            'sku_code': f'{prefix}-{model.replace(" ", "-").replace("\n", "").replace("/", "-")}',
            'name': f'西映 {model}',
            'category': category,
            'category_code': category_code,
            'brand': '西映',
            'specification': spec,
            'description': desc,
            'cost_price': price,
            'sale_price': round(price * 1.5, 2),
            'unit': '件',
            'status': 'active',
            'supplier': '西映',
            'created_at': datetime.now().isoformat()
        })
    
    return items

def ensure_category(conn, name, code):
    """确保分类存在，不存在则创建"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM material_category WHERE code = ?", (code,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # 创建分类
    cursor.execute("""
        INSERT INTO material_category (name, code, parent_id, sort_order, is_deleted)
        VALUES (?, ?, NULL, 0, 0)
    """, (name, code))
    conn.commit()
    return cursor.lastrowid

def import_to_database(items):
    """导入数据到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    success_count = 0
    skip_count = 0
    
    for item in items:
        # 确保分类存在
        category_id = ensure_category(conn, item['category'], item['category_code'])
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM material_sku WHERE sku_code = ?", (item['sku_code'],))
        if cursor.fetchone():
            print(f"跳过已存在: {item['sku_code']}")
            skip_count += 1
            continue
        
        # 插入数据
        try:
            cursor.execute("""
                INSERT INTO material_sku (
                    sku_code, name, category_id, brand, specification,
                    description, cost_price, sale_price, unit, status,
                    is_deleted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                item['sku_code'], item['name'], category_id, item['brand'],
                item['specification'], item['description'], item['cost_price'],
                item['sale_price'], item['unit'], item['status'],
                item['created_at']
            ))
            success_count += 1
            print(f"导入成功: {item['sku_code']} - {item['name']}")
        except Exception as e:
            print(f"导入失败 {item['sku_code']}: {e}")
    
    conn.commit()
    conn.close()
    
    return success_count, skip_count

def main():
    print("=" * 60)
    print("西映品牌供应链数据导入")
    print("=" * 60)
    
    # 导入餐椅
    print("\n[1/3] 导入餐椅数据...")
    chair_items = import_chair_data()
    print(f"解析到 {len(chair_items)} 条餐椅数据")
    
    # 导入餐桌
    print("\n[2/3] 导入餐桌数据...")
    table_items = import_table_data()
    print(f"解析到 {len(table_items)} 条餐桌数据")
    
    # 导入家居配套
    print("\n[3/3] 导入家居配套数据...")
    furniture_items = import_furniture_data()
    print(f"解析到 {len(furniture_items)} 条家居配套数据")
    
    # 合并所有数据
    all_items = chair_items + table_items + furniture_items
    print(f"\n总计: {len(all_items)} 条物料数据")
    
    # 导入数据库
    print("\n开始导入数据库...")
    success, skip = import_to_database(all_items)
    
    print("\n" + "=" * 60)
    print("导入完成!")
    print(f"成功: {success} 条")
    print(f"跳过(已存在): {skip} 条")
    print("=" * 60)

if __name__ == '__main__':
    main()
