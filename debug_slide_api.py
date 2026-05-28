import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')
from app import create_app
app = create_app()
with app.app_context():
    from app.models.case import Case
    case = Case.query.get(37)
    if case:
        print(f"Case found: {case.brand_name}")
    else:
        print("Case 37 not found!")
    
    # Try to call the slide data route directly
    try:
        from app.routes.case_routes import get_slide_data, get_public_slide_data
        print("Routes imported OK")
    except Exception as e:
        print(f"Import error: {e}")
