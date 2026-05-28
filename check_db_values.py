import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.cursor()

# Check actual custom_measure values
cur.execute("""
SELECT id, material_name, width, depth, height, unit, custom_measure, quantity, unit_price, total_price
FROM case_space_materials 
WHERE case_id=37 
ORDER BY id
""")
rows = cur.fetchall()
print("=== 案例37 物料数据（含计算验证）===")
print("id | name | w | d | h | unit | custom_measure | qty | price | amount")
for r in rows:
    id, name, w, d, h, unit, cm, qty, price, amount = r
    # Calculate what it should be
    w = w or 0; d = d or 0; h = h or 0
    calc = (w * d * h) / 1000000000 if w and d and h else 0
    print(f"{id} | {name} | {w} | {d} | {h} | {unit} | {cm} | {qty} | {price} | {amount}")
    print(f"   -> 计算值: {calc:.3f} m³, 实际显示: {cm}")
    print()

conn.close()
