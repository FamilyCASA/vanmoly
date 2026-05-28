import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# The fallback dicts have slightly different indentation. Let me find the exact text.
old1 = "ply_chain': sku.supply_chain or '\u76f4\u4f9b',\n                    'color_name': sku.color_name or '',\n                })"
old2 = "pply_chain': sku.supply_chain or '\u76f4\u4f9b',\n                    'color_name': sku.color_name or '',\n                })"

new_text = """ply_chain': sku.supply_chain or '\u76f4\u4f9b',
                    'color_name': sku.color_name or '',
                    'width': float(sku.width) if sku.width else None,
                    'depth': float(sku.depth) if sku.depth else None,
                    'height': float(sku.height) if sku.height else None,
                })"""

count = c.count(old1)
print(f"Pattern 1 found: {count}")
c = c.replace(old1, new_text)

count2 = c.count(old2)
print(f"Pattern 2 found: {count2}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
