# -*- coding: utf-8 -*-
"""
物料管理升级 - 6大类分类体系迁移脚本
执行: python migrations/upgrade_material_categories_6level.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text
from datetime import datetime

# 6大类分类定义
NEW_CATEGORIES = [
    # 1. 固装家具
    {'name': '固装家具', 'code': 'guzhuang', 'level': 1, 'color': '#8B5A2B', 'children': [
        {'name': '柜类', 'code': 'guzhuang-cabinet'},
        {'name': '门类', 'code': 'guzhuang-door'},
        {'name': '窗套', 'code': 'guzhuang-window'},
        {'name': '楼梯', 'code': 'guzhuang-stairs'},
    ]},
    # 2. 基装施工
    {'name': '基装施工', 'code': 'jizhuang', 'level': 1, 'color': '#E8A87C', 'children': [
        {'name': '打拆', 'code': 'jizhuang-demo'},
        {'name': '水电', 'code': 'jizhuang-plumbing'},
        {'name': '泥工', 'code': 'jizhuang-masonry'},
        {'name': '木工', 'code': 'jizhuang-carpentry'},
        {'name': '漆工', 'code': 'jizhuang-painting'},
    ]},
    # 3. 主材
    {'name': '主材', 'code': 'zhucai', 'level': 1, 'color': '#41B3A7', 'children': [
        {'name': '瓷砖', 'code': 'zhucai-tile'},
        {'name': '地板', 'code': 'zhucai-floor'},
        {'name': '涂料', 'code': 'zhucai-paint'},
        {'name': '石材', 'code': 'zhucai-stone'},
        {'name': '灯具', 'code': 'zhucai-lamp'},
        {'name': '开关', 'code': 'zhucai-switch'},
    ]},
    # 4. 服务费
    {'name': '服务费', 'code': 'fuwu', 'level': 1, 'color': '#F9ED69', 'children': [
        {'name': '搬运费', 'code': 'fuwu-carry'},
        {'name': '上楼费', 'code': 'fuwu-upstairs'},
        {'name': '垃圾清运', 'code': 'fuwu-garbage'},
    ]},
    # 5. 成品家具
    {'name': '成品家具', 'code': 'chengpin', 'level': 1, 'color': '#567A8B', 'children': [
        {'name': '餐桌椅', 'code': 'chengpin-dining'},
        {'name': '沙发茶几', 'code': 'chengpin-sofa'},
        {'name': '床', 'code': 'chengpin-bed'},
        {'name': '床垫', 'code': 'chengpin-mattress'},
    ]},
    # 6. 软装饰品
    {'name': '软装饰品', 'code': 'ruanzhuang', 'level': 1, 'color': '#D4A5A5', 'children': [
        {'name': '窗帘', 'code': 'ruanzhuang-curtain'},
        {'name': '墙纸', 'code': 'ruanzhuang-wallpaper'},
        {'name': '挂画', 'code': 'ruanzhuang-painting'},
        {'name': '抱枕', 'code': 'ruanzhuang-pillow'},
    ]},
]

def migrate_material_categories():
    """执行物料分类6级体系迁移"""
    app = create_app()
    
    with app.app_context():
        conn = db.engine.connect()
        
        print("=" * 60)
        print("物料管理升级 - 6大类分类体系迁移")
        print("=" * 60)
        
        # 1. 备份现有数据
        print("\n[1/6] 备份现有数据...")
        backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 备份分类表
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS material_category_backup_{backup_time} 
            AS SELECT * FROM material_category
        """))
        print(f"  [OK] 已备份 material_category -> material_category_backup_{backup_time}")
        
        # 备份SKU表
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS material_sku_backup_{backup_time} 
            AS SELECT * FROM material_sku
        """))
        print(f"  [OK] 已备份 material_sku -> material_sku_backup_{backup_time}")
        
        # 2. 清空现有分类（保留备份）
        print("\n[2/6] 清空现有分类数据...")
        conn.execute(text("DELETE FROM material_category"))
        print("  [OK] 已清空 material_category 表")
        
        # 3. 创建6大类 + 二级分类
        print("\n[3/6] 创建6大类分类体系...")
        category_id_map = {}  # 新name -> new_id 映射
        
        for cat in NEW_CATEGORIES:
            # 插入一级分类
            result = conn.execute(text("""
                INSERT INTO material_category (name, code, level, color, is_enabled, created_at, updated_at)
                VALUES (:name, :code, :level, :color, 1, :now, :now)
            """), {
                'name': cat['name'],
                'code': cat['code'],
                'level': cat['level'],
                'color': cat['color'],
                'now': datetime.utcnow()
            })
            parent_id = result.lastrowid
            category_id_map[cat['name']] = parent_id
            print(f"  [OK] L1: {cat['name']} (ID={parent_id})")
            
            # 插入二级分类
            for child in cat['children']:
                child_result = conn.execute(text("""
                    INSERT INTO material_category (name, code, parent_id, level, color, is_enabled, created_at, updated_at)
                    VALUES (:name, :code, :parent_id, 2, :color, 1, :now, :now)
                """), {
                    'name': child['name'],
                    'code': child['code'],
                    'parent_id': parent_id,
                    'color': cat['color'],
                    'now': datetime.utcnow()
                })
                child_id = child_result.lastrowid
                print(f"        [OK] L2: {child['name']} (ID={child_id})")
        
        total_l2 = sum(len(c['children']) for c in NEW_CATEGORIES)
        print(f"\n  [完成] 共创建 {len(NEW_CATEGORIES)} 个一级分类 + {total_l2} 个二级分类")
        
        # 4. 迁移SKU数据（简单映射 - 需要手动调整）
        print("\n[4/6] 迁移SKU数据到新分类...")
        # 查询所有SKU
        skus = conn.execute(text("SELECT id, name, category_id FROM material_sku WHERE is_deleted=0")).fetchall()
        print(f"  共 {len(skus)} 条SKU待迁移")
        
        # TODO: 这里需要更精确的映射逻辑
        # 暂时将所有SKU映射到第一个一级分类（固装家具）
        default_cat_id = category_id_map.get('固装家具')
        if default_cat_id:
            conn.execute(text(f"UPDATE material_sku SET category_id = :cat_id WHERE category_id IS NOT NULL"), {
                'cat_id': default_cat_id
            })
            print(f"  [警告] 已将 {len(skus)} 条SKU临时映射到 '固装家具' (ID={default_cat_id})")
            print("         需要手动调整SKU分类映射！")
        
        # 5. 创建 material_color 表（花色管理）
        print("\n[5/6] 创建 material_color 花色表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS material_color (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) DEFAULT '0',
                sku_id INTEGER NOT NULL,
                color_name VARCHAR(50) NOT NULL,
                color_code VARCHAR(20),
                image VARCHAR(500),
                stock_quantity INTEGER DEFAULT 0,
                price_adjustment NUMERIC(10,2) DEFAULT 0,
                is_enabled BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sku_id) REFERENCES material_sku(id) ON DELETE CASCADE
            )
        """))
        print("  [OK] material_color 表创建成功")
        
        # 6. 添加索引
        print("\n[6/6] 添加索引...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_material_color_sku_id ON material_color(sku_id)"))
            print("  [OK] idx_material_color_sku_id")
        except Exception as e:
            print(f"  [跳过] {e}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("[完成] 迁移完成！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 手动调整SKU的分类映射（material_sku.category_id）")
        print("2. 完善后端API (material_routes.py)")
        print("3. 改造前端 (MaterialManageV2.vue)")


if __name__ == '__main__':
    migrate_material_categories()
