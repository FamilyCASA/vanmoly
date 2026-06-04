"""生成剩余模块的测试数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print('Generating test data for remaining modules...')
    
    # 1. 合同数据
    from app.models.contract import Contract
    if Contract.query.count() == 0:
        print('\n[1] Creating contracts...')
        contracts = [
            Contract(
                contract_no='HT20260427001',
                customer_id=1,
                title='万科城全案设计',
                total_amount=285000,
                status='signed',
                signed_date=(datetime.now() - timedelta(days=10)).date(),
                contract_type='all_in'
            ),
            Contract(
                contract_no='HT20260427002',
                customer_id=2,
                title='天府新区软装设计',
                total_amount=156000,
                status='executing',
                signed_date=(datetime.now() - timedelta(days=5)).date(),
                contract_type='soft'
            ),
            Contract(
                contract_no='HT20260427003',
                customer_id=3,
                title='高新区全屋定制',
                total_amount=98000,
                status='draft',
                contract_type='all_in'
            )
        ]
        for c in contracts:
            db.session.add(c)
        db.session.commit()
        print(f'   Created {len(contracts)} contracts')
    
    # 2. 楼盘数据
    from app.models.building import Building
    if Building.query.count() == 0:
        print('\n[2] Creating buildings...')
        buildings = [
            Building(
                name='万科城',
                address='成都市高新区天府大道100号',
                city='成都市',
                district='高新区',
                property_type='住宅',
                developer='万科地产',
                total_houses=1200
            ),
            Building(
                name='保利天悦',
                address='成都市锦江区东大街200号',
                city='成都市',
                district='锦江区',
                property_type='住宅',
                developer='保利地产',
                total_houses=800
            ),
            Building(
                name='中海国际中心',
                address='成都市武侯区人民南路300号',
                city='成都市',
                district='武侯区',
                property_type='商业',
                developer='中海地产',
                total_houses=500
            ),
            Building(
                name='龙湖西宸原著',
                address='成都市金牛区茶店子路400号',
                city='成都市',
                district='金牛区',
                property_type='别墅',
                developer='龙湖地产',
                total_houses=200
            ),
            Building(
                name='华润二十四城',
                address='成都市成华区双庆路500号',
                city='成都市',
                district='成华区',
                property_type='住宅',
                developer='华润置地',
                total_houses=3000
            )
        ]
        for b in buildings:
            db.session.add(b)
        db.session.commit()
        print(f'   Created {len(buildings)} buildings')
    
    # 3. 报价数据
    from app.models.quote import Quote, QuoteItem
    if Quote.query.count() == 0:
        print('\n[3] Creating quotes...')
        quotes = [
            Quote(
                quote_no='BJ20260427001',
                customer_id=1,
                total_amount=285000,
                status='confirmed',
                creator_id=1,
                creator_name='管理员'
            ),
            Quote(
                quote_no='BJ20260427002',
                customer_id=2,
                total_amount=156000,
                status='sent',
                creator_id=2,
                creator_name='设计师A'
            ),
            Quote(
                quote_no='BJ20260427003',
                customer_id=3,
                total_amount=98000,
                status='draft',
                creator_id=1,
                creator_name='管理员'
            )
        ]
        for q in quotes:
            db.session.add(q)
        db.session.commit()
        print(f'   Created {len(quotes)} quotes')
    
    # 4. 案例数据
    from app.models.case import CaseStudy
    if CaseStudy.query.count() == 0:
        print('\n[4] Creating case studies...')
        cases = [
            CaseStudy(
                title='现代简约·万科城120㎡',
                description='原木与白色的温暖对话',
                style='modern',
                house_type='三室两厅',
                area=120,
                budget_range='20-30万',
                location='成都·高新区',
                is_featured=True,
                status='已发布',
                view_count=1256,
                like_count=89,
                created_by=1
            ),
            CaseStudy(
                title='北欧风·保利天悦89㎡',
                description='小户型的精致生活',
                style='nordic',
                house_type='两室两厅',
                area=89,
                budget_range='15-20万',
                location='成都·锦江区',
                is_featured=True,
                status='已发布',
                view_count=892,
                like_count=56,
                created_by=1
            ),
            CaseStudy(
                title='新中式·西宸原著200㎡',
                description='东方美学的现代表达',
                style='chinese',
                house_type='四室三厅',
                area=200,
                budget_range='50-80万',
                location='成都·金牛区',
                is_featured=True,
                status='已发布',
                view_count=2341,
                like_count=167,
                created_by=2
            )
        ]
        for c in cases:
            db.session.add(c)
        db.session.commit()
        print(f'   Created {len(cases)} case studies')
    
    # 5. 线索数据 (V2)
    from app.models.lead_v2 import Lead
    if Lead.query.count() == 0:
        print('\n[5] Creating leads (V2)...')
        leads = [
            Lead(
                name='王先生',
                phone='13800138001',
                source='官网咨询',
                building_name='万科城',
                house_type='三室两厅',
                area=120,
                budget='20-30万',
                intention_level='high',
                status='new',
                owner_id=1
            ),
            Lead(
                name='李女士',
                phone='13800138002',
                source='案例留资',
                building_name='保利天悦',
                house_type='两室两厅',
                area=89,
                budget='15-20万',
                intention_level='medium',
                status='following',
                owner_id=2
            ),
            Lead(
                name='张先生',
                phone='13800138003',
                source='电话咨询',
                building_name='西宸原著',
                house_type='四室三厅',
                area=200,
                budget='50-80万',
                intention_level='high',
                status='quoted',
                owner_id=1
            ),
            Lead(
                name='陈女士',
                phone='13800138004',
                source='微信咨询',
                building_name='华润二十四城',
                house_type='三室两厅',
                area=110,
                budget='25-35万',
                intention_level='medium',
                status='deposit',
                owner_id=3
            ),
            Lead(
                name='刘先生',
                phone='13800138005',
                source='转介绍',
                building_name='中海国际',
                house_type='两室一厅',
                area=75,
                budget='10-15万',
                intention_level='low',
                status='sea',
                owner_id=None
            )
        ]
        for l in leads:
            db.session.add(l)
        db.session.commit()
        print(f'   Created {len(leads)} leads')
    
    # 6. 供应商数据
    from app.models.material_sku import MaterialSupplier
    if MaterialSupplier.query.count() == 0:
        print('\n[6] Creating suppliers...')
        suppliers = [
            MaterialSupplier(
                name='帝标家居',
                contact_person='张经理',
                phone='13800138100',
                email='zhang@dibiao.com',
                address='成都市武侯区家具产业园',
                status='active'
            ),
            MaterialSupplier(
                name='高晟家具',
                contact_person='李经理',
                phone='13800138101',
                email='li@gaosheng.com',
                address='成都市新都区家具城',
                status='active'
            ),
            MaterialSupplier(
                name='D&B 帝标|设记家定制',
                contact_person='王经理',
                phone='13800138102',
                email='wang@fanmoli.com',
                address='成都市高新区设计中心',
                status='active'
            )
        ]
        for s in suppliers:
            db.session.add(s)
        db.session.commit()
        print(f'   Created {len(suppliers)} suppliers')
    
    print('\n' + '='*50)
    print('Test data generation complete!')
    print('='*50)
