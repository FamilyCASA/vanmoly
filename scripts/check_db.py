"""检查数据库配置"""
import sys
sys.path.insert(0, 'D:\\desktop\\DESIGNARY-SYS-V3.0\\backend')

from app import create_app
from config import config

app = create_app(config['development'])

with app.app_context():
    print(f'Database URI: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
    
    from app.models.material_sku import MaterialSKU, MaterialCategory
    from app import db
    
    print(f'SKU count: {MaterialSKU.query.count()}')
    print(f'Category count: {MaterialCategory.query.count()}')
