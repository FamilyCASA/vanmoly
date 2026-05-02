"""
生成200个种子客户，随机分配给销售类员工
用于测试员工积分系统
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.customer import Customer
from app.models.employee import Employee, Department
from app.models.lead_v2 import Lead, LeadFollow, LeadPoint
from datetime import datetime, timedelta
import random

app = create_app()

# 姓氏和名字库
surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '吴', '周', '徐', '孙', '马', '朱', '胡', '郭', '林', '何', '高', '罗']
first_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞', '平', '刚', '桂英', '文', '辉', '鑫', '宇', '博', '浩', '然']

# 楼盘名称库
building_names = [
    '万科城', '保利天悦', '西宸原著', '中海九号公馆', '华润二十四城', '龙湖三千集',
    '绿地468', '融创玖棠府', '招商大魔方', '仁恒滨河湾', '建发央玺', '新希望D10',
    '德商迎晖天玺', '麓湖生态城', '蔚蓝卡地亚', '伊泰天骄', '嘉佰道', '锦江大院',
    '武侯金茂府', '青羊樾府', '金牛国投', '成华奥园', '高新誉峰', '天府锦绣',
    '锦城湖岸', '兴隆湖畔', '秦皇寺CBD', '东安新城', '北部新城', '南部商务区'
]

# 区域
areas = ['高新区', '锦江区', '青羊区', '金牛区', '武侯区', '成华区', '天府新区', '龙泉驿区', '双流区', '温江区']

# 客户来源
sources = ['小程序', '官网', '抖音', '小红书', '转介绍', '电话营销', '线下活动', '合作渠道']

# 装修需求
requirements = ['全屋整装', '局部改造', '软装搭配', '定制家具', '设计咨询', '预算规划']

# 预算范围
budget_ranges = ['10万以下', '10-15万', '15-20万', '20-30万', '30-50万', '50-80万', '80万以上']

# 状态分布（加权随机）
status_weights = [
    ('potential', 30),      # 潜在客户 30%
    ('contacted', 25),      # 已联系 25%
    ('following', 20),      # 跟进中 20%
    ('quoted', 10),         # 已报价 10%
    ('negotiating', 8),     # 洽谈中 8%
    ('signed', 5),          # 已签约 5%
    ('lost', 2),            # 已流失 2%
]

def get_random_name():
    return random.choice(surnames) + random.choice(first_names)

def get_random_phone():
    prefixes = ['138', '139', '135', '136', '137', '150', '151', '152', '157', '158', '159', '182', '183', '187', '188']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

def get_weighted_status():
    total = sum(w for _, w in status_weights)
    r = random.randint(1, total)
    cumulative = 0
    for status, weight in status_weights:
        cumulative += weight
        if r <= cumulative:
            return status
    return 'potential'

def generate_customer_data(index, sales_employees):
    """生成单个客户数据"""
    status = get_weighted_status()
    assigned_sales = random.choice(sales_employees) if sales_employees else None
    
    # 根据状态设置时间线
    created_at = datetime.now() - timedelta(days=random.randint(1, 90))
    
    customer = Customer(
        name=get_random_name(),
        phone=get_random_phone(),
        source=random.choice(sources),
        status=status,
        budget=random.choice(budget_ranges),
        address=f"成都市{random.choice(areas)}{random.choice(building_names)}",
        building_name=random.choice(building_names),
        remark=f"客户意向：{random.choice(requirements)}，预计{random.randint(1, 6)}个月内装修",
        created_at=created_at,
        updated_at=created_at + timedelta(days=random.randint(0, 30))
    )
    
    return customer, assigned_sales, status, created_at

def main():
    with app.app_context():
        print("="*60)
        print("Generating 200 Seed Customers for Sales Testing")
        print("="*60)
        
        # 1. 获取所有销售类员工
        sales_depts = Department.query.filter(
            Department.name.in_(['销售部', '市场部', '客服部'])
        ).all()
        sales_dept_ids = [d.id for d in sales_depts]
        
        sales_employees = Employee.query.filter(
            Employee.department_id.in_(sales_dept_ids),
            Employee.status == 'active'
        ).all()
        
        if not sales_employees:
            # 如果没有找到销售部门员工，获取所有员工
            sales_employees = Employee.query.filter_by(status='active').all()
        
        print(f"[INFO] Found {len(sales_employees)} sales employees")
        for emp in sales_employees[:5]:  # 显示前5个
            print(f"       - {emp.name} ({emp.department.name if emp.department else 'N/A'})")
        
        # 2. 生成200个客户
        customers_data = []
        assignment_data = []  # (customer, employee, status, created_at)
        
        for i in range(200):
            customer, assigned_sales, status, created_at = generate_customer_data(i, sales_employees)
            customers_data.append(customer)
            if assigned_sales:
                assignment_data.append((customer, assigned_sales, status, created_at))
        
        # 3. 批量插入客户
        print(f"\n[1] Inserting 200 customers...")
        for customer in customers_data:
            db.session.add(customer)
        db.session.commit()
        print(f"      Created 200 customers")
        
        # 4. 为每个客户创建线索记录和分配
        print(f"\n[2] Creating lead records and assignments...")
        score_logs = []
        
        for customer, employee, status, created_at in assignment_data:
            # 创建线索
            lead = Lead(
                customer_id=customer.id,
                name=customer.name,
                phone=customer.phone,
                source=customer.source,
                source_detail=customer.building_name,
                status=status,
                budget_range=customer.budget,
                # area字段不存在，使用address代替
                address=customer.address,
                employee_id=employee.id,
                employee_name=employee.name,
                created_at=created_at,
                updated_at=created_at
            )
            db.session.add(lead)
            db.session.flush()  # 获取lead.id
            
            # 根据状态添加跟进记录和积分
            if status in ['contacted', 'following', 'quoted', 'negotiating', 'signed']:
                # 添加跟进记录
                follow = LeadFollow(
                    lead_id=lead.id,
                    employee_id=employee.id,
                    follow_type='phone' if random.random() > 0.5 else 'wechat',
                    content=f"初次联系，客户意向{random.choice(['强', '中等', '一般'])}",
                    next_follow_time=created_at + timedelta(days=random.randint(1, 7)),
                    created_at=created_at + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(follow)
                
                # 添加积分记录（录入+1，跟进+1）
                score_logs.append(LeadPoint(
                    employee_id=employee.id,
                    lead_id=lead.id,
                    point_type=LeadPoint.TYPE_CREATE,
                    points=1,
                    description=f'录入线索: {customer.name}',
                    created_at=created_at
                ))
                score_logs.append(LeadPoint(
                    employee_id=employee.id,
                    lead_id=lead.id,
                    point_type=LeadPoint.TYPE_FOLLOW,
                    points=1,
                    description=f'跟进线索: {customer.name}',
                    created_at=created_at + timedelta(hours=2)
                ))
                
                # 如果已签约，添加更多积分
                if status == 'signed':
                    score_logs.append(LeadPoint(
                        employee_id=employee.id,
                        lead_id=lead.id,
                        point_type=LeadPoint.TYPE_CONTRACT_FULL,
                        points=random.randint(10, 30),
                        description=f'签约成功: {customer.name}',
                        created_at=created_at + timedelta(days=random.randint(30, 60))
                    ))
        
        # 批量插入积分记录
        print(f"\n[3] Inserting {len(score_logs)} score logs...")
        for log in score_logs:
            db.session.add(log)
        
        db.session.commit()
        
        # 5. 统计结果
        print(f"\n" + "="*60)
        print("Summary")
        print("="*60)
        
        # 按员工统计
        from sqlalchemy import func
        employee_stats = db.session.query(
            Lead.employee_id,
            Employee.name,
            func.count(Lead.id).label('lead_count'),
            func.sum(LeadScoreLog.score).label('total_score')
        ).join(Employee, Lead.employee_id == Employee.id
        ).outerjoin(LeadScoreLog, LeadScoreLog.employee_id == Employee.id
        ).group_by(Lead.employee_id, Employee.name).all()
        
        print(f"\nEmployee Performance:")
        print(f"{'Employee':<15} {'Leads':<10} {'Score':<10}")
        print("-" * 40)
        for emp_id, name, lead_count, total_score in sorted(employee_stats, key=lambda x: x[3] or 0, reverse=True)[:10]:
            print(f"{name:<15} {lead_count:<10} {total_score or 0:<10}")
        
        # 状态分布
        print(f"\nStatus Distribution:")
        status_counts = db.session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
        for status, count in sorted(status_counts, key=lambda x: x[1], reverse=True):
            print(f"  {status:<15} {count:>3} ({count/200*100:>5.1f}%)")
        
        print(f"\nTotal: 200 customers created successfully!")
        print("="*60)

if __name__ == '__main__':
    main()
