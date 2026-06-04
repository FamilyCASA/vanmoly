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
    ('待跟进', 30),
    ('跟进中', 35),
    ('已报价', 15),
    ('洽谈中', 10),
    ('已成交', 8),
    ('已流失', 2),
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
    return '待跟进'

def main():
    with app.app_context():
        print("="*60)
        print("Generating 200 Seed Customers")
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
            sales_employees = Employee.query.filter_by(status='active').all()
        
        print(f"[INFO] Found {len(sales_employees)} sales employees")
        
        # 2. 删除旧客户数据（保留前10个）
        old_customers = Customer.query.offset(10).all()
        for c in old_customers:
            db.session.delete(c)
        db.session.commit()
        print(f"[INFO] Cleared old customers (kept first 10)")
        
        # 3. 生成200个客户
        customers = []
        for i in range(200):
            status = get_weighted_status()
            assigned_sales = random.choice(sales_employees) if sales_employees else None
            created_at = datetime.now() - timedelta(days=random.randint(1, 90))
            
            customer = Customer(
                name=get_random_name(),
                phone=get_random_phone(),
                source=random.choice(sources),
                status=status,
                budget=random.choice(budget_ranges),
                address=f"成都市{random.choice(areas)}{random.choice(building_names)}",
                building_name=random.choice(building_names),
                house_type=random.choice(['一室一厅', '两室一厅', '两室两厅', '三室两厅', '四室两厅']),
                house_area=random.choice([60, 80, 90, 100, 120, 140, 160, 180, 200]),
                requirements=random.choice(requirements),
                owner_id=assigned_sales.id if assigned_sales else None,
                remark=f"预计{random.randint(1, 6)}个月内装修",
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(0, 30))
            )
            customers.append(customer)
        
        # 4. 批量插入
        print(f"\n[1] Inserting 200 customers...")
        for customer in customers:
            db.session.add(customer)
        db.session.commit()
        print(f"      Created 200 customers successfully!")
        
        # 5. 统计结果
        print(f"\n" + "="*60)
        print("Summary")
        print("="*60)
        
        # 按员工统计
        from sqlalchemy import func
        employee_stats = db.session.query(
            Customer.owner_id,
            Employee.name,
            func.count(Customer.id).label('customer_count')
        ).join(Employee, Customer.owner_id == Employee.id
        ).group_by(Customer.owner_id, Employee.name).all()
        
        print(f"\nTop 10 Sales by Customer Count:")
        print(f"{'Employee':<15} {'Customers':<10}")
        print("-" * 30)
        for emp_id, name, count in sorted(employee_stats, key=lambda x: x[2], reverse=True)[:10]:
            print(f"{name:<15} {count:<10}")
        
        # 状态分布
        print(f"\nStatus Distribution:")
        status_counts = db.session.query(Customer.status, func.count(Customer.id)).group_by(Customer.status).all()
        for status, count in sorted(status_counts, key=lambda x: x[1], reverse=True):
            print(f"  {status:<12} {count:>3} ({count/200*100:>5.1f}%)")
        
        # 来源分布
        print(f"\nSource Distribution:")
        source_counts = db.session.query(Customer.source, func.count(Customer.id)).group_by(Customer.source).all()
        for source, count in sorted(source_counts, key=lambda x: x[1], reverse=True):
            print(f"  {source:<12} {count:>3} ({count/200*100:>5.1f}%)")
        
        print(f"\nTotal: 200 customers created successfully!")
        print("="*60)

if __name__ == '__main__':
    main()
