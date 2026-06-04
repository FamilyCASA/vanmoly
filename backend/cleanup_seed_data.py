"""
清理测试种子数据，保留一套有效的
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.customer import Customer
from app.models.employee import Employee, Department
from app.models.lead_v2 import Lead, LeadFollow, LeadPoint
from app.models.contract import Contract
from app.models.building import Building
from app.models.quote import Quote
from app.models.case import CaseStudy
from app.models.material_sku import MaterialSKU, MaterialCategory, MaterialSupplier
from sqlalchemy import func

app = create_app()

def main():
    with app.app_context():
        print("="*60)
        print("Cleaning up seed data - keeping one valid set")
        print("="*60)
        
        # 1. 清理线索数据 - 保留最新的10条，删除旧的
        print("\n[1] Cleaning leads...")
        old_leads = Lead.query.order_by(Lead.id.desc()).offset(10).all()
        for lead in old_leads:
            # 先删除关联的跟进和积分
            LeadFollow.query.filter_by(lead_id=lead.id).delete()
            LeadPoint.query.filter_by(lead_id=lead.id).delete()
            db.session.delete(lead)
        db.session.commit()
        remaining_leads = Lead.query.count()
        print(f"    Kept {remaining_leads} leads, deleted {len(old_leads)}")
        
        # 2. 清理客户数据 - 保留最新的200条（刚生成的），删除旧的10条
        print("\n[2] Cleaning customers...")
        # 保留ID最大的200条（刚生成的）
        subquery = db.session.query(Customer.id).order_by(Customer.id.desc()).limit(200).subquery()
        old_customers = Customer.query.filter(~Customer.id.in_(subquery)).all()
        for c in old_customers:
            db.session.delete(c)
        db.session.commit()
        remaining_customers = Customer.query.count()
        print(f"    Kept {remaining_customers} customers")
        
        # 3. 清理合同数据 - 保留3条有效数据
        print("\n[3] Cleaning contracts...")
        contracts = Contract.query.all()
        if len(contracts) > 3:
            for c in contracts[3:]:
                db.session.delete(c)
            db.session.commit()
        remaining = Contract.query.count()
        print(f"    Kept {remaining} contracts")
        
        # 4. 清理楼盘数据 - 保留5条有效数据
        print("\n[4] Cleaning buildings...")
        buildings = Building.query.all()
        if len(buildings) > 5:
            for b in buildings[5:]:
                db.session.delete(b)
            db.session.commit()
        remaining = Building.query.count()
        print(f"    Kept {remaining} buildings")
        
        # 5. 清理报价数据 - 保留3条有效数据
        print("\n[5] Cleaning quotes...")
        quotes = Quote.query.all()
        if len(quotes) > 3:
            for q in quotes[3:]:
                db.session.delete(q)
            db.session.commit()
        remaining = Quote.query.count()
        print(f"    Kept {remaining} quotes")
        
        # 6. 清理案例数据 - 保留3条有效数据
        print("\n[6] Cleaning case studies...")
        cases = CaseStudy.query.all()
        if len(cases) > 3:
            for c in cases[3:]:
                db.session.delete(c)
            db.session.commit()
        remaining = CaseStudy.query.count()
        print(f"    Kept {remaining} cases")
        
        # 7. 清理供应商数据 - 保留3条有效数据
        print("\n[7] Cleaning suppliers...")
        suppliers = MaterialSupplier.query.all()
        if len(suppliers) > 3:
            for s in suppliers[3:]:
                db.session.delete(s)
            db.session.commit()
        remaining = MaterialSupplier.query.count()
        print(f"    Kept {remaining} suppliers")
        
        # 8. 检查并显示最终统计
        print("\n" + "="*60)
        print("Final Data Summary")
        print("="*60)
        
        stats = [
            ("Departments", Department.query.count()),
            ("Employees", Employee.query.count()),
            ("Customers", Customer.query.count()),
            ("Leads", Lead.query.count()),
            ("Lead Follows", LeadFollow.query.count()),
            ("Lead Points", LeadPoint.query.count()),
            ("Contracts", Contract.query.count()),
            ("Buildings", Building.query.count()),
            ("Quotes", Quote.query.count()),
            ("Case Studies", CaseStudy.query.count()),
            ("Material Categories", MaterialCategory.query.count()),
            ("Material SKUs", MaterialSKU.query.count()),
            ("Suppliers", MaterialSupplier.query.count()),
        ]
        
        for name, count in stats:
            print(f"  {name:<25} {count:>5}")
        
        print("\n" + "="*60)
        print("Cleanup complete!")
        print("="*60)

if __name__ == '__main__':
    main()
