"""检查SKU数量"""
import sys
sys.path.insert(0, 'D:\\desktop\\DESIGNARY-SYS-V3.0\\backend')

from app import create_app
from config import config

app = create_app(config['development'])
with app.app_context():
    from app.models.material_sku import MaterialSKU
    print(f'SKU count: {MaterialSKU.query.count()}')
    print(f'Database: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
