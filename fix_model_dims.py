import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Add width/depth/height columns to model (after custom_measure)
old_fields = """    # 自定义字段
    custom_name = db.Column(db.String(200), comment='自定义商品名称')
    material = db.Column(db.String(100), comment='材质')
    custom_measure = db.Column(db.String(100), comment='定制计量值')

    # 用量/价格"""

new_fields = """    # 自定义字段
    custom_name = db.Column(db.String(200), comment='自定义商品名称')
    material = db.Column(db.String(100), comment='材质')
    custom_measure = db.Column(db.String(100), comment='定制计量值')

    # 尺寸
    width = db.Column(db.Numeric(10, 2), comment='宽度(mm)')
    depth = db.Column(db.Numeric(10, 2), comment='深度(mm)')
    height = db.Column(db.Numeric(10, 2), comment='高度(mm)')

    # 用量/价格"""

c = c.replace(old_fields, new_fields, 1)

# 2. Add to to_dict output
old_dict = """            'custom_measure': self.custom_measure or '',
            'quantity': float(self.quantity) if self.quantity else 0,"""

new_dict = """            'custom_measure': self.custom_measure or '',
            'width': float(self.width) if self.width else None,
            'depth': float(self.depth) if self.depth else None,
            'height': float(self.height) if self.height else None,
            'quantity': float(self.quantity) if self.quantity else 0,"""

c = c.replace(old_dict, new_dict, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ Model: width/depth/height added + to_dict updated")
