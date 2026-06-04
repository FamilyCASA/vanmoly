"""
案例数据种子
创建测试案例数据
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import CaseStudy, CaseMedia
from datetime import datetime

app = create_app()

def seed_cases():
    with app.app_context():
        print("开始创建测试案例数据...")
        
        # 检查是否已有数据
        existing = CaseStudy.query.count()
        if existing > 0:
            print(f"已有 {existing} 条案例数据，跳过")
            return
        
        # 测试案例数据
        cases_data = [
            {
                'title': '现代简约三居室，打造温馨舒适的家',
                'case_no': 'CS202604260001',
                'type': '实景',
                'style': '现代简约',
                'space_type': '住宅',
                'location': '成都市高新区',
                'address': '天府大道北段',
                'house_type': '三室两厅',
                'area': 120,
                'budget_range': '25-35万',
                'construction_phase': '竣工验收',
                'description': '本案位于成都市高新区，业主是一对年轻夫妇，希望打造一个简约而不简单的居住空间。设计师通过合理的空间布局和精致的细节处理，营造出一个温馨舒适的家。',
                'design_concept': '以"少即是多"为设计理念，通过简洁的线条和纯粹的色彩，打造出一个宁静舒适的居住空间。在材质选择上，我们大量使用了原木、棉麻等天然材料，让空间充满温度。',
                'whole_house_plan': '客厅与餐厅采用开放式设计，增加了空间的通透感。主卧配备独立衣帽间和卫生间，提升居住品质。儿童房采用榻榻米设计，既节省空间又增加了储物功能。',
                'customer_requirements': '业主希望空间简洁明亮，有足够的储物空间，同时希望保留一些原木元素，让家更有温度。',
                'design_highlights': '1. 客厅电视背景墙采用悬浮式设计，搭配隐藏灯带，营造出轻盈的视觉效果。\n2. 餐厅卡座设计，既节省空间又增加了储物功能。\n3. 主卧床头背景墙采用软包设计，提升舒适度。',
                'customer_value': '通过合理的空间规划和精致的细节处理，我们为业主打造了一个既美观又实用的家，让每一寸空间都得到了充分利用。',
                'total_price': 320000,
                'package_type': '全案A套餐',
                'price_detail': '[{"item":"基础装修","desc":"水电、泥木、油漆等基础工程","amount":120000},{"item":"定制家具","desc":"橱柜、衣柜、鞋柜等定制产品","amount":80000},{"item":"活动家具","desc":"沙发、床、餐桌等活动家具","amount":70000},{"item":"软装配饰","desc":"窗帘、灯具、装饰品等","amount":50000}]',
                'owner_authorized': True,
                'is_public': True,
                'is_featured': True,
                'status': '已发布',
                'view_count': 1234,
                'like_count': 89,
                'subscription_count': 56,
                'cover_image': 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1200',
                'responsible_id': 1,
                'created_by': 1,
                'publish_time': datetime.now()
            },
            {
                'title': '新中式别墅，传统与现代的完美融合',
                'case_no': 'CS202604260002',
                'type': '实景',
                'style': '新中式',
                'space_type': '别墅',
                'location': '成都市天府新区',
                'address': '麓湖生态城',
                'house_type': '别墅',
                'area': 300,
                'budget_range': '> 50万',
                'construction_phase': '软装进场',
                'description': '本案是一套300㎡的别墅，业主喜欢中式风格，但又不希望过于传统。设计师巧妙地将中式元素与现代设计手法相结合，打造出一个既有东方韵味又不失现代感的居住空间。',
                'design_concept': '以"东方雅韵"为设计理念，将传统中式元素与现代简约风格相融合。在空间布局上，我们借鉴了传统园林的造景手法，营造出移步换景的空间体验。',
                'whole_house_plan': '一层为公共区域，包括客厅、餐厅、厨房和茶室。二层为私密空间，包括主卧套房和两间次卧。地下一层为娱乐休闲区，包括影音室、健身房和酒窖。',
                'customer_requirements': '业主是一位企业家，喜欢中式文化，希望家中能够体现东方美学，同时要有现代生活的便利性。',
                'design_highlights': '1. 客厅挑高设计，搭配中式格栅屏风，气势恢宏。\n2. 茶室采用榻榻米设计，营造禅意空间。\n3. 庭院景观与室内空间相互借景，形成独特的空间体验。',
                'customer_value': '这个案例成功地将传统文化与现代生活相结合，为业主打造了一个既有文化底蕴又符合现代生活方式的居住空间。',
                'total_price': 850000,
                'package_type': '全案S套餐',
                'price_detail': '[{"item":"基础装修","desc":"水电、泥木、油漆等基础工程","amount":300000},{"item":"定制家具","desc":"橱柜、衣柜、书柜等定制产品","amount":200000},{"item":"活动家具","desc":"沙发、床、餐桌等活动家具","amount":180000},{"item":"软装配饰","desc":"窗帘、灯具、装饰品等","amount":120000},{"item":"庭院景观","desc":"庭院设计与施工","amount":50000}]',
                'owner_authorized': True,
                'is_public': True,
                'is_featured': True,
                'status': '已发布',
                'view_count': 892,
                'like_count': 67,
                'subscription_count': 34,
                'cover_image': 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200',
                'responsible_id': 1,
                'created_by': 1,
                'publish_time': datetime.now()
            },
            {
                'title': '北欧风小户型，温馨治愈的二人世界',
                'case_no': 'CS202604260003',
                'type': '实景',
                'style': '北欧',
                'space_type': '公寓',
                'location': '成都市锦江区',
                'address': '春熙路附近',
                'house_type': '两室一厅',
                'area': 65,
                'budget_range': '15-25万',
                'construction_phase': '竣工验收',
                'description': '本案是一套65㎡的小户型，业主是一对刚结婚的年轻夫妻。设计师通过巧妙的空间规划和温馨的色调搭配，打造出一个舒适治愈的二人世界。',
                'design_concept': '以"温馨治愈"为设计理念，采用北欧风格的简洁线条和温暖色调，营造出一个舒适放松的居住空间。在材质选择上，我们大量使用了原木和棉麻等天然材料。',
                'whole_house_plan': '客厅与卧室之间采用玻璃隔断，增加了空间的通透感。厨房采用开放式设计，与餐厅相连。卫生间采用干湿分离设计，提升使用体验。',
                'customer_requirements': '业主希望空间温馨舒适，有足够的储物空间，同时希望保留一些个性化的设计元素。',
                'design_highlights': '1. 客厅采用投影仪代替电视，节省空间又增加趣味性。\n2. 卧室地台床设计，下方可做储物空间。\n3. 阳台改造为阅读角，增加生活情趣。',
                'customer_value': '通过巧妙的设计，我们将65㎡的小空间打造得功能齐全、温馨舒适，满足了业主对美好生活的向往。',
                'total_price': 180000,
                'package_type': '全案A套餐',
                'price_detail': '[{"item":"基础装修","desc":"水电、泥木、油漆等基础工程","amount":70000},{"item":"定制家具","desc":"橱柜、衣柜等定制产品","amount":50000},{"item":"活动家具","desc":"沙发、床、餐桌等活动家具","amount":40000},{"item":"软装配饰","desc":"窗帘、灯具、装饰品等","amount":20000}]',
                'owner_authorized': True,
                'is_public': True,
                'is_featured': False,
                'status': '已发布',
                'view_count': 2156,
                'like_count': 156,
                'subscription_count': 89,
                'cover_image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200',
                'responsible_id': 1,
                'created_by': 1,
                'publish_time': datetime.now()
            },
            {
                'title': '轻奢风格四居室，品质生活的完美诠释',
                'case_no': 'CS202604260004',
                'type': '实景',
                'style': '轻奢',
                'space_type': '住宅',
                'location': '成都市武侯区',
                'address': '桐梓林片区',
                'house_type': '四室两厅',
                'area': 158,
                'budget_range': '35-50万',
                'construction_phase': '安装阶段',
                'description': '本案是一套158㎡的四居室，业主是一对事业有成的中年夫妇。设计师采用轻奢风格，通过精致的材质和考究的细节，打造出一个品质感十足的居住空间。',
                'design_concept': '以"精致生活"为设计理念，采用轻奢风格的设计语言，通过大理石、金属、皮革等高端材质的运用，营造出一个优雅精致的居住空间。',
                'whole_house_plan': '客厅采用横厅设计，空间开阔大气。主卧配备独立衣帽间和豪华卫生间。另外三间卧室分别作为儿童房、书房和客房使用。',
                'customer_requirements': '业主希望空间有品质感，材质要高端，细节要精致，同时要有足够的储物空间。',
                'design_highlights': '1. 客厅采用大理石背景墙，搭配金属线条，奢华大气。\n2. 餐厅水晶吊灯，营造用餐氛围。\n3. 主卧采用套房设计，配备独立衣帽间和豪华卫生间。',
                'customer_value': '我们通过高端材质和精致细节，为业主打造了一个品质感十足的居住空间，完美诠释了轻奢生活的内涵。',
                'total_price': 450000,
                'package_type': '全案B套餐',
                'price_detail': '[{"item":"基础装修","desc":"水电、泥木、油漆等基础工程","amount":150000},{"item":"定制家具","desc":"橱柜、衣柜等定制产品","amount":120000},{"item":"活动家具","desc":"沙发、床、餐桌等活动家具","amount":100000},{"item":"软装配饰","desc":"窗帘、灯具、装饰品等","amount":80000}]',
                'owner_authorized': True,
                'is_public': True,
                'is_featured': True,
                'status': '已发布',
                'view_count': 1567,
                'like_count': 123,
                'subscription_count': 78,
                'cover_image': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200',
                'responsible_id': 1,
                'created_by': 1,
                'publish_time': datetime.now()
            },
            {
                'title': '日式风格loft，都市青年的理想居所',
                'case_no': 'CS202604260005',
                'type': '实景',
                'style': '日式',
                'space_type': 'loft',
                'location': '成都市成华区',
                'address': '东郊记忆附近',
                'house_type': 'loft',
                'area': 45,
                'budget_range': '< 15万',
                'construction_phase': '竣工验收',
                'description': '本案是一套45㎡的loft公寓，业主是一位单身设计师。设计师采用日式风格，通过原木元素和简约设计，打造出一个温馨舒适的都市居所。',
                'design_concept': '以"极简生活"为设计理念，采用日式风格的设计语言，通过原木元素和简约线条，营造出一个宁静舒适的居住空间。',
                'whole_house_plan': '一层为公共区域，包括客厅、厨房和卫生间。二层为私密空间，包括卧室和书房。楼梯下方设计为储物空间。',
                'customer_requirements': '业主希望空间简洁实用，有足够的储物空间，同时希望保留一些个性化的设计元素。',
                'design_highlights': '1. 楼梯采用悬浮式设计，轻盈通透。\n2. 二层卧室采用地台床设计，节省空间。\n3. 大量储物空间设计，满足收纳需求。',
                'customer_value': '我们通过巧妙的设计，将45㎡的小空间打造得功能齐全、温馨舒适，满足了业主对理想居所的向往。',
                'total_price': 120000,
                'package_type': '全案A套餐',
                'price_detail': '[{"item":"基础装修","desc":"水电、泥木、油漆等基础工程","amount":50000},{"item":"定制家具","desc":"橱柜、衣柜等定制产品","amount":30000},{"item":"活动家具","desc":"沙发、床、餐桌等活动家具","amount":25000},{"item":"软装配饰","desc":"窗帘、灯具、装饰品等","amount":15000}]',
                'owner_authorized': True,
                'is_public': True,
                'is_featured': False,
                'status': '已发布',
                'view_count': 3421,
                'like_count': 234,
                'subscription_count': 156,
                'cover_image': 'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=1200',
                'responsible_id': 1,
                'created_by': 1,
                'publish_time': datetime.now()
            }
        ]
        
        # 创建案例
        for case_data in cases_data:
            case = CaseStudy(**case_data)
            db.session.add(case)
        
        db.session.commit()
        
        # 为每个案例添加媒体图片
        cases = CaseStudy.query.all()
        for case in cases:
            for i in range(3):
                media = CaseMedia(
                    case_id=case.id,
                    media_type='image',
                    url=case.cover_image,
                    sort_order=i
                )
                db.session.add(media)
        
        db.session.commit()
        
        print(f"成功创建 {len(cases_data)} 条测试案例数据！")

if __name__ == '__main__':
    seed_cases()
