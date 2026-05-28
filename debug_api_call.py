import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
with app.app_context():
    # Simulate the slide data route
    from app.models.case import CaseStudy, CaseSpaceMaterial, CaseSlideConfig, SlideTemplate
    from app.models.material_sku import MaterialSKU, MaterialCategory
    
    case = CaseStudy.query.get(37)
    print(f"Case: {case}")
    if case:
        print(f"  brand_name: {case.brand_name}")
    
    # Check slide config
    configs = CaseSlideConfig.query.filter_by(case_id=37).all()
    print(f"Slide configs: {len(configs)}")
    
    # Check spaces
    phases = case.phases if case else []
    print(f"Phases: {len(phases)}")
    for p in phases:
        print(f"  Phase {p.id}: {p.name}, spaces: {len(p.spaces) if hasattr(p, 'spaces') else 'N/A'}")
    
    # Try the actual API call
    try:
        with app.test_client() as client:
            resp = client.get('/api/v3/cases/37/slide-data')
            print(f"\nAPI status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Response: {resp.data[:500].decode('utf-8', errors='replace')}")
    except Exception as e:
        print(f"API error: {type(e).__name__}: {e}")
