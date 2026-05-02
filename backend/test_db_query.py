"""直接在Flask应用上下文中查询数据库"""
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.material_sku import MaterialSKU, MaterialCategory
from app.models.customer import Customer
from app.models.employee import Employee

app = create_app()

with app.app_context():
    print('Database URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    print()
    
    # 查询物料
    print('MaterialSKU count:', MaterialSKU.query.count())
    print('MaterialCategory count:', MaterialCategory.query.count())
    
    # 查询客户
    print('Customer count:', Customer.query.count())
    
    # 查询员工
    print('Employee count:', Employee.query.count())
    
    # 显示前3个物料
    print('\nFirst 3 SKUs:')
    for sku in MaterialSKU.query.limit(3).all():
        print(f'  - {sku.name} ({sku.sku_code})')
