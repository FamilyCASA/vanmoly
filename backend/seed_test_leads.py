"""
生成10条随机测试线索数据
用于测试客户列表、编辑、跟进、公海、积分功能
"""

import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.lead_v2 import Lead, LeadFollow, LeadPoint


def generate_phone():
    """生成唯一手机号"""
    prefix = random.choice(['138', '139', '136', '137', '150', '151', '152', '157', '158', '159', '182', '183', '187', '188'])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return prefix + suffix


def random_date(days_back=30):
    """生成随机日期"""
    return datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))


def create_test_leads():
    """创建10条测试线索"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("生成10条随机测试线索")
        print("=" * 50)
        
        # 测试数据池
        names = ['张伟', '李娜', '王芳', '刘洋', '陈静', '杨帆', '赵敏', '黄磊', '周杰', '吴倩', 
                 '徐鹏', '孙丽', '马超', '朱婷', '胡军', '郭明', '林华', '何平', '高飞', '梁雨']
        sources = ['案例留资', '抖音广告', '百度搜索', '朋友圈广告', '老客户推荐', '楼盘合作', '线下活动', '官网咨询']
        buildings = ['万科城', '保利花园', '华润置地', '龙湖天街', '中海国际', '绿地中心', '万达华府', '碧桂园', '恒大绿洲', '融创壹号院']
        house_types = ['一室一厅', '两室一厅', '两室两厅', '三室一厅', '三室两厅', '四室两厅', '别墅']
        budgets = ['10万以下', '10-20万', '20-30万', '30-50万', '50-100万', '100万以上']
        decoration_types = ['新房装修', '旧房翻新', '局部改造', '软装搭配']
        styles = ['现代简约', '北欧', '新中式', '轻奢', '美式', '日式']
        statuses = ['待分配', '已分配', '跟进中', '已到店', '已量房', '已出方案', '已交定金', '已签约']
        intention_levels = ['高', '中', '低']
        
        generated_phones = set()
        leads_created = []
        
        for i in range(10):
            # 确保手机号唯一
            phone = generate_phone()
            while phone in generated_phones:
                phone = generate_phone()
            generated_phones.add(phone)
            
            # 随机选择数据
            name = random.choice(names)
            source = random.choice(sources)
            building = random.choice(buildings)
            house_type = random.choice(house_types)
            budget = random.choice(budgets)
            decoration_type = random.choice(decoration_types)
            style = random.choice(styles)
            status = random.choice(statuses)
            intention = random.choice(intention_levels)
            
            # 生成创建时间（过去30天内）
            created_at = random_date(30)
            
            # 创建线索
            lead = Lead(
                name=name,
                phone=phone,
                wechat=f"wx_{phone[-6:]}",
                gender=random.choice(['男', '女']),
                source=source,
                source_detail=f"{source}-详情页",
                building_name=building,
                building_address=f"成都市高新区{building}{random.randint(1,20)}栋",
                house_type=house_type,
                area=random.choice([60, 80, 90, 100, 120, 140, 160, 180, 200]),
                floor=f"{random.randint(1,30)}/{random.randint(10,33)}层",
                delivery_date=(datetime.now() + timedelta(days=random.randint(30, 365))).date(),
                decoration_status=random.choice(['未开工', '水电阶段', '泥木阶段', '油漆阶段', '安装阶段']),
                decoration_type=decoration_type,
                style_preference=style,
                budget=budget,
                timeline=random.choice(['1个月内', '1-3个月', '3-6个月', '6个月以上']),
                detailed_needs=f"客户需要{decoration_type}，喜欢{style}风格，预算{budget}，{random.choice(['注重收纳', '需要儿童房', '要求环保', '追求品质'])}。",
                family_structure=random.choice(['夫妻两人', '夫妻+1孩', '夫妻+2孩', '三代同堂', '单身']),
                living_habits=random.choice(['经常做饭', '喜欢阅读', '居家办公', '热爱运动', '养宠物']),
                hobbies=random.choice(['摄影', '烹饪', '阅读', '健身', '旅行', '音乐']),
                special_requirements=random.choice(['需要智能家居', '要求无障碍设计', '需要大量收纳', '要求隔音好']),
                focus_points=random.choice(['价格', '设计', '材料', '工期', '售后']),
                tags=random.sample(['高意向', '急单', '老客户介绍', '价格敏感', '品质要求高'], random.randint(1, 3)),
                status=status,
                intention_level=intention,
                conversion_level=random.choice(['线索', '客户', 'VIP']),
                assigned_to=random.choice([None, 1, 2, 3]) if status != '待分配' else None,
                assigned_at=created_at + timedelta(hours=random.randint(1, 24)) if status != '待分配' else None,
                follow_count=random.randint(0, 8),
                first_contact_at=created_at + timedelta(hours=random.randint(1, 48)) if status != '待分配' else None,
                last_follow_at=created_at + timedelta(days=random.randint(1, 10)) if status != '待分配' else None,
                next_follow_at=datetime.now() + timedelta(days=random.randint(1, 7)) if random.random() > 0.3 else None,
                is_overdue=random.choice([True, False]),
                overdue_days=random.randint(1, 5) if random.random() > 0.7 else 0,
                is_visited=status in ['已到店', '已量房', '已出方案', '已交定金', '已签约'],
                visited_at=random_date(10) if status in ['已到店', '已量房', '已出方案', '已交定金', '已签约'] else None,
                is_measured=status in ['已量房', '已出方案', '已交定金', '已签约'],
                measured_at=random_date(8) if status in ['已量房', '已出方案', '已交定金', '已签约'] else None,
                has_scheme=status in ['已出方案', '已交定金', '已签约'],
                scheme_at=random_date(5) if status in ['已出方案', '已交定金', '已签约'] else None,
                deposit_amount=random.choice([5000, 10000, 20000, 30000]) if status in ['已交定金', '已签约'] else None,
                deposit_at=random_date(3) if status in ['已交定金', '已签约'] else None,
                contract_type=random.choice(['签约全案', '签约定制', '签约软装']) if status == '已签约' else None,
                contract_amount=random.randint(150000, 800000) if status == '已签约' else None,
                contract_at=random_date(1) if status == '已签约' else None,
                is_in_sea=random.random() > 0.8,
                sea_at=random_date(5) if random.random() > 0.8 else None,
                sea_reason=random.choice(['48小时未跟进', '主动放弃', '客户要求']) if random.random() > 0.8 else None,
                total_points=random.randint(0, 50),
                remark=f"测试数据-{i+1}",
                ip_address=f"192.168.1.{random.randint(10, 200)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(1, 5))
            )
            
            db.session.add(lead)
            db.session.flush()  # 获取lead.id
            leads_created.append(lead)
            
            print(f"  [{i+1}/10] {name} {phone} | {building} | {status} | 积分:{lead.total_points}")
            
            # 添加跟进记录
            if lead.follow_count > 0:
                for j in range(min(lead.follow_count, 3)):  # 最多3条记录
                    follow = LeadFollow(
                        lead_id=lead.id,
                        follow_type=random.choice(['电话', '微信', '到店']),
                        content=random.choice([
                            '客户意向强烈，约明天到店详谈',
                            '客户对设计方案满意，准备签约',
                            '客户需要再考虑一下，下周再联系',
                            '客户预算有限，需要调整方案',
                            '客户对材料有疑问，已解答'
                        ]),
                        result=random.choice(['意向强烈', '意向一般', '需要再联系', '暂不考虑']),
                        next_follow_at=lead.next_follow_at,
                        is_visited=j == lead.follow_count - 1 and lead.is_visited,
                        visited_at=lead.visited_at if j == lead.follow_count - 1 else None,
                        operator_id=lead.assigned_to or 1,
                        created_at=lead.created_at + timedelta(days=j+1)
                    )
                    db.session.add(follow)
            
            # 添加积分记录
            if lead.total_points > 0:
                point_types = [
                    ('录入线索', 1),
                    ('有效跟进', 1),
                    ('预约到店', 0.5),
                    ('实际到店', 2),
                    ('获取需求', 1),
                    ('交定金', 10)
                ]
                
                remaining_points = lead.total_points
                for point_type, point_value in point_types:
                    if remaining_points >= point_value and random.random() > 0.3:
                        point = LeadPoint(
                            lead_id=lead.id,
                            employee_id=lead.assigned_to or 1,
                            point_type=point_type,
                            points=point_value,
                            description=f'{point_type}: {name}',
                            created_at=lead.created_at + timedelta(days=random.randint(1, 5))
                        )
                        db.session.add(point)
                        remaining_points -= point_value
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        print(f"\n生成了 {len(leads_created)} 条线索:")
        print(f"  - 待分配: {sum(1 for l in leads_created if l.status == '待分配')}")
        print(f"  - 跟进中: {sum(1 for l in leads_created if l.status == '跟进中')}")
        print(f"  - 已到店: {sum(1 for l in leads_created if l.is_visited)}")
        print(f"  - 已交定金: {sum(1 for l in leads_created if l.deposit_at)}")
        print(f"  - 已签约: {sum(1 for l in leads_created if l.contract_at)}")
        print(f"  - 公海: {sum(1 for l in leads_created if l.is_in_sea)}")
        print(f"\n总积分: {sum(l.total_points for l in leads_created)}")
        
        return leads_created
        

def clear_test_data():
    """清除测试数据"""
    app = create_app()
    
    with app.app_context():
        print("清除测试数据...")
        
        # 删除积分记录
        LeadPoint.query.filter(LeadPoint.description.contains('测试')).delete(synchronize_session=False)
        
        # 删除跟进记录
        LeadFollow.query.filter(LeadFollow.content.contains('测试')).delete(synchronize_session=False)
        
        # 删除线索
        Lead.query.filter(Lead.remark.contains('测试')).delete(synchronize_session=False)
        
        db.session.commit()
        print("测试数据已清除")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生成测试线索数据')
    parser.add_argument('--clear', action='store_true', help='清除测试数据')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_test_data()
    else:
        create_test_leads()
