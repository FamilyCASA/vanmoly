import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    from app.models.case import CaseSpaceMaterial, CaseSpaceRendering, db
    # Remove test data, keep original 3 records
    db.session.query(CaseSpaceMaterial).filter(CaseSpaceMaterial.material_name == '测试电视柜').delete()
    db.session.commit()
    
    remaining = CaseSpaceMaterial.query.filter_by(case_id=37).count()
    print(f"Remaining materials for case 37: {remaining}")
