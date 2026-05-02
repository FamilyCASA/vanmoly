"""
D&B 帝标|设记家系统 V3.0 - 测试数据生成脚本
生成10个客户 + 20个不同岗位员工
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.customer import Customer
from app.models.employee import Employee, Department

app = create_app()

# 姓氏库
surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']

# 名字库
names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞', '平', '刚', '桂英', '文', '辉', '鑫', '宇', '博', '浩', '然', '轩', '怡', '欣', '雨', '晨', '一诺', '子涵', '诗涵', '梓涵', '子轩']

# 岗位配置 (name, department, job_level)
positions = [
    # 管理层
    {'name': '总经理', 'department': '管理层', 'job_level': 'L5'},
    {'name': '设计总监', 'department': '设计部', 'job_level': 'L5'},
    {'name': '工程总监', 'department': '工程部', 'job_level': 'L5'},
    {'name': '市场总监', 'department': '市场部', 'job_level': 'L5'},
    
    # 设计部
    {'name': '首席设计师', 'department': '设计部', 'job_level': 'L4'},
    {'name': '高级设计师', 'department': '设计部', 'job_level': 'L3'},
    {'name': '高级设计师', 'department': '设计部', 'job_level': 'L3'},
    {'name': '设计师', 'department': '设计部', 'job_level': 'L2'},
    {'name': '设计师', 'department': '设计部', 'job_level': 'L2'},
    {'name': '助理设计师', 'department': '设计部', 'job_level': 'L1'},
    
    # 工程部
    {'name': '项目经理', 'department': '工程部', 'job_level': 'L4'},
    {'name': '项目经理', 'department': '工程部', 'job_level': 'L4'},
    {'name': '施工监理', 'department': '工程部', 'job_level': 'L3'},
    {'name': '施工监理', 'department': '工程部', 'job_level': 'L3'},
    {'name': '质检专员', 'department': '工程部', 'job_level': 'L2'},
    
    # 市场部
    {'name': '销售经理', 'department': '市场部', 'job_level': 'L4'},
    {'name': '销售顾问', 'department': '市场部', 'job_level': 'L2'},
    {'name': '销售顾问', 'department': '市场部', 'job_level': 'L2'},
    {'name': '销售顾问', 'department': '市场部', 'job_level': 'L2'},
    {'name': '客服专员', 'department': '市场部', 'job_level': 'L1'},
    
    # 行政财务
    {'name': '行政主管', 'department': '行政部', 'job_level': 'L3'},
    {'name': '财务专员', 'department': '财务部', 'job_level': 'L2'},
]

def random_phone():
    """生成随机手机号"""
    prefix = random.choice(['138', '139', '137', '136', '135', '134', '159', '158', '157', '150', '151', '152', '188', '187', '182', '183', '184', '178', '177', '166', '199', '198'])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return prefix + suffix

def random_name():
    """生成随机姓名"""
    surname = random.choice(surnames)
    name = random.choice(names)
    # 30%概率生成双字名
    if random.random() < 0.3:
        name += random.choice(names)
    return surname + name

def random_date(start_year=2020, end_year=2025):
    """生成随机日期"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))

def create_departments():
    """创建部门"""
    departments = ['管理层', '设计部', '工程部', '市场部', '行政部', '财务部']
    dept_objs = {}
    for dept_name in departments:
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            dept = Department(
                name=dept_name,
                code=dept_name.lower().replace('部', '').replace('层', '')
            )
            db.session.add(dept)
            db.session.flush()
        dept_objs[dept_name] = dept
    db.session.commit()
    return dept_objs

def create_positions(departments):
    """创建岗位"""
    print("Creating positions...")
    from app.models.employee import Position
    
    position_objs = {}
    for pos in positions[:20]:
        dept = departments.get(pos['department'])
        position = Position(
            name=pos['name'],
            department_id=dept.id if dept else None,
            level=int(pos['job_level'][1:]),
            is_enabled=True
        )
        db.session.add(position)
        db.session.flush()
        position_objs[pos['name']] = position
    
    db.session.commit()
    print(f"[OK] Created {len(position_objs)} positions")
    return position_objs

def create_employees(departments, position_objs):
    """创建20个员工"""
    print("Creating 20 employees...")
    
    employees = []
    for i, pos in enumerate(positions[:20], 1):
        dept = departments.get(pos['department'])
        position = position_objs.get(pos['name'])
        
        # 根据级别生成薪资
        level_num = int(pos['job_level'][1:])
        base_salary = {
            1: random.randint(4000, 6000),
            2: random.randint(6000, 10000),
            3: random.randint(10000, 15000),
            4: random.randint(15000, 25000),
            5: random.randint(25000, 50000)
        }.get(level_num, 5000)
        
        employee = Employee(
            employee_no=f'VM{2024}{i:03d}',
            name=random_name(),
            phone=random_phone(),
            email=f'employee{i}@vanmoly.com',
            department_id=dept.id if dept else None,
            position_id=position.id if position else None,
            job_level=pos['job_level'],
            base_salary=base_salary,
            status='active',
            entry_date=random_date(2020, 2024),
            id_card=f'{random.randint(100000, 999999)}19900101{random.randint(1000, 9999)}',
            address=f'Chengdu {random.choice(["Jinjiang", "Qingyang", "Jinniu", "Wuhou", "Chenghua", "Gaoxin", "Tianfu"])} Street {i}',
            emergency_contact=random_name(),
            emergency_phone=random_phone(),
            created_at=datetime.now()
        )
        employees.append(employee)
        db.session.add(employee)
    
    db.session.commit()
    print(f"[OK] Created {len(employees)} employees")
    return employees

def create_customers():
    """创建10个客户"""
    print("Creating 10 customers...")
    
    house_types = ['1R1L', '2R1L', '3R1L', '3R2L', '4R+']
    areas = ['<80', '80-100', '100-120', '120-150', '150+']
    budgets = ['<15w', '15-20w', '20-30w', '30-50w', '50w+']
    styles = ['Modern', 'Nordic', 'Chinese', 'Luxury', 'Industrial', 'Japanese']
    statuses = ['pending', 'following', 'signed', 'construction', 'completed']
    sources = ['Website', 'MiniApp', 'Douyin', 'Xiaohongshu', 'Referral', 'Building', 'Offline']
    districts = ['Jinjiang', 'Qingyang', 'Jinniu', 'Wuhou', 'Chenghua', 'Gaoxin', 'Tianfu']
    buildings = ['Vanke', 'Longfor', 'Poly', 'CR', 'Zhonghai', 'Greenland', 'Merchants']
    
    customers = []
    for i in range(1, 11):
        district = random.choice(districts)
        building = random.choice(buildings)
        customer = Customer(
            name=random_name(),
            phone=random_phone(),
            wechat=f'wx_{random.randint(10000, 99999)}',
            email=f'customer{i}@example.com',
            address=f'Chengdu {district} {building} Garden Bldg {random.randint(1, 20)} Unit {random.randint(1, 30)} No.{random.randint(101, 3001)}',
            city='Chengdu',
            district=district,
            building_name=f'{building} Garden',
            house_type=random.choice(house_types),
            house_area=random.choice([65, 85, 95, 110, 125, 140, 160, 180]),
            budget=random.choice(budgets),
            style_preference=random.choice(styles),
            status=random.choice(statuses),
            source=random.choice(sources),
            remark=f'Customer remark {i}',
            created_at=random_date(2024, 2025)
        )
        customers.append(customer)
        db.session.add(customer)
    
    db.session.commit()
    print(f"[OK] Created {len(customers)} customers")
    return customers

def main():
    with app.app_context():
        print("=" * 50)
        print("Vanmoly V3.0 - Test Data Generator")
        print("=" * 50)
        print()
        
        # 清空现有数据（可选）
        # Customer.query.delete()
        # Employee.query.delete()
        # Department.query.delete()
        # db.session.commit()
        
        # 创建部门
        departments = create_departments()
        print(f"[OK] 部门创建完成: {list(departments.keys())}")
        print()
        
        # 创建岗位
        position_objs = create_positions(departments)
        print()
        
        # 创建员工
        employees = create_employees(departments, position_objs)
        print()
        
        # 创建客户
        customers = create_customers()
        print()
        
        print("=" * 50)
        print("Test Data Generation Complete!")
        print("=" * 50)
        print(f"客户总数: {Customer.query.count()}")
        print(f"员工总数: {Employee.query.count()}")
        print(f"部门总数: {Department.query.count()}")
        print()
        print("Employee Position Distribution:")
        for pos in positions[:20]:
            print(f"  - {pos['department']} / {pos['name']} ({pos['job_level']})")

if __name__ == '__main__':
    main()
