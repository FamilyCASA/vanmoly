# -*- coding: utf-8 -*-
"""
填充 case_space_config_item 表物料明细数据
"""
import sqlite3
import os

# 数据库路径
DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'

# 物料模板：按空间类型分类
SPACE_MATERIALS = {
    '客厅': {
        'comfort': [  # 舒适版
            {'category': '柜体', 'name': '实木颗粒板-柜体-浅灰橡木', 'brand': '帝标', 'spec': '18mm', 'quantity': 8, 'unit': '㎡', 'price': 260},
            {'category': '门板', 'name': '吸塑门板-暖白', 'brand': '帝标', 'spec': '肤感膜', 'quantity': 6, 'unit': '㎡', 'price': 439},
            {'category': '五金', 'name': '基础铰链', 'brand': 'DTC', 'spec': '阻尼', 'quantity': 12, 'unit': '个', 'price': 28},
            {'category': '五金', 'name': '挂衣杆', 'brand': '帝标', 'spec': '铝合金', 'quantity': 2, 'unit': '根', 'price': 85},
        ],
        'luxury': [  # 豪华版
            {'category': '柜体', 'name': '实木颗粒板-柜体-浅灰橡木', 'brand': '帝标', 'spec': '18mm', 'quantity': 10, 'unit': '㎡', 'price': 260},
            {'category': '门板', 'name': 'PET门板-高光灰', 'brand': '帝标', 'spec': '进口PET', 'quantity': 8, 'unit': '㎡', 'price': 580},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼', 'quantity': 16, 'unit': '个', 'price': 68},
            {'category': '五金', 'name': '挂衣杆', 'brand': '帝标', 'spec': '实木', 'quantity': 2, 'unit': '根', 'price': 180},
            {'category': '灯光', 'name': '层板灯带', 'brand': '欧普', 'spec': 'LED 12V', 'quantity': 3, 'unit': '米', 'price': 120},
        ],
        'top': [  # 顶配版
            {'category': '柜体', 'name': '多层实木板-柜体-北美黑胡桃', 'brand': '帝标', 'spec': '18mm', 'quantity': 12, 'unit': '㎡', 'price': 480},
            {'category': '门板', 'name': '实木贴皮-黑胡桃', 'brand': '帝标', 'spec': '天然木皮', 'quantity': 10, 'unit': '㎡', 'price': 1200},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼+电动', 'quantity': 20, 'unit': '个', 'price': 128},
            {'category': '五金', 'name': '智能挂衣杆', 'brand': '帝标', 'spec': '电动升降', 'quantity': 1, 'unit': '根', 'price': 2800},
            {'category': '灯光', 'name': '智能灯带', 'brand': '欧普', 'spec': 'LED RGBW', 'quantity': 5, 'unit': '米', 'price': 280},
        ],
    },
    '卧室': {
        'comfort': [
            {'category': '柜体', 'name': '实木颗粒板-柜体-暖白', 'brand': '帝标', 'spec': '18mm', 'quantity': 12, 'unit': '㎡', 'price': 260},
            {'category': '门板', 'name': '吸塑门板-暖白', 'brand': '帝标', 'spec': '肤感膜', 'quantity': 10, 'unit': '㎡', 'price': 439},
            {'category': '五金', 'name': '基础铰链', 'brand': 'DTC', 'spec': '阻尼', 'quantity': 20, 'unit': '个', 'price': 28},
            {'category': '五金', 'name': '挂衣杆', 'brand': '帝标', 'spec': '铝合金', 'quantity': 3, 'unit': '根', 'price': 85},
        ],
        'luxury': [
            {'category': '柜体', 'name': '实木颗粒板-柜体-北美樱桃', 'brand': '帝标', 'spec': '18mm', 'quantity': 14, 'unit': '㎡', 'price': 320},
            {'category': '门板', 'name': 'PET门板-哑光灰', 'brand': '帝标', 'spec': '进口PET', 'quantity': 12, 'unit': '㎡', 'price': 580},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼', 'quantity': 24, 'unit': '个', 'price': 68},
            {'category': '五金', 'name': '穿衣镜', 'brand': '帝标', 'spec': '全身镜', 'quantity': 1, 'unit': '个', 'price': 680},
            {'category': '灯光', 'name': '感应灯带', 'brand': '欧普', 'spec': 'LED人体感应', 'quantity': 2, 'unit': '米', 'price': 180},
        ],
        'top': [
            {'category': '柜体', 'name': '多层实木板-柜体-北美黑胡桃', 'brand': '帝标', 'spec': '18mm', 'quantity': 16, 'unit': '㎡', 'price': 480},
            {'category': '门板', 'name': '实木贴皮-黑胡桃', 'brand': '帝标', 'spec': '天然木皮', 'quantity': 14, 'unit': '㎡', 'price': 1200},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼+电动', 'quantity': 28, 'unit': '个', 'price': 128},
            {'category': '五金', 'name': '智能穿衣镜', 'brand': '帝标', 'spec': 'LED+除雾', 'quantity': 1, 'unit': '个', 'price': 2800},
            {'category': '灯光', 'name': '智能灯带', 'brand': '欧普', 'spec': 'LED RGBW', 'quantity': 4, 'unit': '米', 'price': 280},
        ],
    },
    '书房': {
        'comfort': [
            {'category': '柜体', 'name': '实木颗粒板-柜体-暖白', 'brand': '帝标', 'spec': '18mm', 'quantity': 6, 'unit': '㎡', 'price': 260},
            {'category': '门板', 'name': '吸塑门板-暖白', 'brand': '帝标', 'spec': '肤感膜', 'quantity': 4, 'unit': '㎡', 'price': 439},
            {'category': '五金', 'name': '基础铰链', 'brand': 'DTC', 'spec': '阻尼', 'quantity': 8, 'unit': '个', 'price': 28},
            {'category': '台面', 'name': '书桌台面', 'brand': '帝标', 'spec': '1.4m', 'quantity': 1, 'unit': '张', 'price': 680},
        ],
        'luxury': [
            {'category': '柜体', 'name': '实木颗粒板-柜体-北美樱桃', 'brand': '帝标', 'spec': '18mm', 'quantity': 8, 'unit': '㎡', 'price': 320},
            {'category': '门板', 'name': '玻璃门板', 'brand': '帝标', 'spec': '铝合金边框', 'quantity': 4, 'unit': '㎡', 'price': 720},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼', 'quantity': 12, 'unit': '个', 'price': 68},
            {'category': '台面', 'name': '实木书桌台面', 'brand': '帝标', 'spec': '黑胡桃1.6m', 'quantity': 1, 'unit': '张', 'price': 1680},
            {'category': '灯光', 'name': '书柜灯带', 'brand': '欧普', 'spec': 'LED 12V', 'quantity': 2, 'unit': '米', 'price': 120},
        ],
        'top': [
            {'category': '柜体', 'name': '多层实木板-柜体-北美黑胡桃', 'brand': '帝标', 'spec': '18mm', 'quantity': 10, 'unit': '㎡', 'price': 480},
            {'category': '门板', 'name': '实木贴皮-黑胡桃+玻璃', 'brand': '帝标', 'spec': '天然木皮', 'quantity': 6, 'unit': '㎡', 'price': 1400},
            {'category': '五金', 'name': '进口铰链', 'brand': 'Blum', 'spec': '全阻尼+电动', 'quantity': 16, 'unit': '个', 'price': 128},
            {'category': '台面', 'name': '实木书桌台面', 'brand': '帝标', 'spec': '黑胡桃1.8m', 'quantity': 1, 'unit': '张', 'price': 3200},
            {'category': '灯光', 'name': '智能灯带', 'brand': '欧普', 'spec': 'LED RGBW', 'quantity': 3, 'unit': '米', 'price': 280},
        ],
    },
}

def get_version_level_en(level_cn):
    """中文版本转英文"""
    mapping = {
        '舒适': 'comfort',
        '豪华': 'luxury',
        '顶配': 'top',
    }
    return mapping.get(level_cn, 'comfort')

def get_space_type_en(type_cn):
    """中文空间类型转英文"""
    mapping = {
        '客厅': 'living_room',
        '卧室': 'bedroom',
        '书房': 'study',
    }
    return mapping.get(type_cn, 'living_room')

def populate_items():
    """填充物料明细"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取所有空间配置
    c.execute('''
        SELECT id, case_id, space_type, version_level, total_price
        FROM case_space_config
        ORDER BY id
    ''')
    configs = c.fetchall()
    
    # 备份当前数据
    c.execute('SELECT COUNT(*) FROM case_space_config_item')
    existing_count = c.fetchone()[0]
    if existing_count > 0:
        print(f"警告: case_space_config_item 表已有 {existing_count} 条记录")
        print("将清空并重新填充...")
        c.execute('DELETE FROM case_space_config_item')
    
    # 按配置填充物料
    inserted = 0
    for config in configs:
        config_id, case_id, space_type, version_level, total_price = config
        
        # 获取对应物料列表
        space_materials = SPACE_MATERIALS.get(space_type, {})
        version_key = get_version_level_en(version_level)
        materials = space_materials.get(version_key, [])
        
        if not materials:
            print(f"配置 {config_id}: 无物料模板 ({space_type}/{version_level})")
            continue
        
        # 插入物料明细
        for idx, mat in enumerate(materials):
            total = mat['quantity'] * mat['price']
            c.execute('''
                INSERT INTO case_space_config_item
                (config_id, sku_id, sku_code, sku_name, brand, specification,
                 category, quantity, unit, unit_price, total_price,
                 is_exclusive, exclusive_group, is_optional, is_default, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config_id,
                0,  # sku_id 暂时为0，后续可关联
                f"D&B-{config_id:04d}-{idx+1:02d}",
                mat['name'],
                mat['brand'],
                mat['spec'],
                mat['category'],
                mat['quantity'],
                mat['unit'],
                mat['price'],
                total,
                0,  # is_exclusive
                None,  # exclusive_group
                0,  # is_optional
                1,  # is_default
                idx,  # sort_order
            ))
            inserted += 1
        
        print(f"配置 {config_id}: {space_type}/{version_level} - 插入 {len(materials)} 条物料")
    
    # 提交事务
    conn.commit()
    
    # 验证
    c.execute('SELECT COUNT(*) FROM case_space_config_item')
    final_count = c.fetchone()[0]
    
    print(f"\n完成！共插入 {inserted} 条物料明细")
    print(f"当前表记录数: {final_count}")
    
    conn.close()
    
    return final_count

if __name__ == '__main__':
    print("开始填充 case_space_config_item 表...")
    print(f"数据库: {DB_PATH}\n")
    
    count = populate_items()
    
    print(f"\n✅ 物料数据填充完成，共 {count} 条记录")
