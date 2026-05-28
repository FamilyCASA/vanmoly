import sys; sys.stdout.reconfigure(encoding='utf-8')

# Check CaseSpaceMaterial to_dict
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

idx = c.find("class CaseSpaceMaterial")
end = c.find("\nclass ", idx + 10)
if end < 0: end = len(c)
block = c[idx:end]
# Find to_dict
td = block.find("def to_dict")
if td > 0:
    print("=== CaseSpaceMaterial.to_dict ===")
    print(block[td:td+500])

# Check MaterialSKU material field
path2 = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\material_sku.py'
with open(path2, encoding='utf-8') as f:
    c2 = f.read()

# Find MaterialSKU class
idx2 = c2.find('class MaterialSKU')
if idx2 > 0:
    end2 = c2.find('\nclass ', idx2 + 10)
    if end2 < 0: end2 = len(c2)
    block2 = c2[idx2:end2]
    # Find 'material' column
    for line in block2.split('\n'):
        if 'material' in line.lower() and 'db.Column' in line:
            print(f"\n  MaterialSKU: {line.strip()[:120]}")
