import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    from app.models.case import CaseSpaceMaterial
    from app.models.material_sku import MaterialSKU
    
    mats = CaseSpaceMaterial.query.filter_by(case_id=37).all()
    print(f"case_space_materials for case 37: {len(mats)}")
    
    skus = MaterialSKU.query.filter_by(is_deleted=False).count()
    print(f"Active MaterialSKU count: {skus}")
