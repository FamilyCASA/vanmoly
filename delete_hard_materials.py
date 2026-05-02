import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("删除硬装施工类物料")
print("=" * 60)

# 先查看有多少硬装施工类物料
cursor.execute("""
    SELECT COUNT(*) as cnt 
    FROM material_sku 
    WHERE category_id IN (
        SELECT id FROM material_category 
        WHERE name LIKE '%硬装%' OR name LIKE '%施工%' OR code LIKE 'HZ%'
    )
    OR sku_code LIKE 'HZ-%'
""")
count = cursor.fetchone()['cnt']
print(f"\n找到硬装施工类物料: {count} 条")

if count > 0:
    # 显示即将删除的物料示例
    cursor.execute("""
        SELECT sku_code, name, category_id 
        FROM material_sku 
        WHERE category_id IN (
            SELECT id FROM material_category 
            WHERE name LIKE '%硬装%' OR name LIKE '%施工%' OR code LIKE 'HZ%'
        )
        OR sku_code LIKE 'HZ-%'
        LIMIT 10
    """)
    rows = cursor.fetchall()
    print("\n物料示例:")
    for row in rows:
        print(f"  {row['sku_code']} - {row['name']}")
    
    # 删除硬装施工类物料
    cursor.execute("""
        DELETE FROM material_sku 
        WHERE category_id IN (
            SELECT id FROM material_category 
            WHERE name LIKE '%硬装%' OR name LIKE '%施工%' OR code LIKE 'HZ%'
        )
        OR sku_code LIKE 'HZ-%'
    """)
    deleted = cursor.rowcount
    conn.commit()
    print(f"\n已删除: {deleted} 条硬装施工类物料")
else:
    print("\n没有找到硬装施工类物料")

# 查看当前物料总数
cursor.execute("SELECT COUNT(*) as cnt FROM material_sku")
total = cursor.fetchone()['cnt']
print(f"当前物料总数: {total} 条")

conn.close()

print("\n" + "=" * 60)
print("删除完成，准备导入新的硬装施工单价明细表")
print("=" * 60)
