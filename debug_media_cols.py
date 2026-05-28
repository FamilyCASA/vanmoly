import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    from app.models.case import CaseMedia
    cols = [c.name for c in CaseMedia.__table__.columns]
    print("CaseMedia model columns:", cols)
