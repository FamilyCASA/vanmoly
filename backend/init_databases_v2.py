"""
初始化多数据库架构 V2.0
创建8个业务数据库并初始化表结构
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_v2 import DevelopmentConfig
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    return app

def init_databases():
    """初始化所有数据库"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("D&B 帝标|设记家系统 V3.0 - 多数据库架构初始化")
        print("=" * 70)
        
        # 确保instance目录存在
        os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)
        
        # 导入所有模型
        print("\n[1/8] 导入HR系统模型 (hr.db)...")
        from app.models.hr_v2 import (
            Department, Position, Employee, EmployeeSalary,
            PerformanceReview, EmployeePoints, PointsTransaction,
            CareerPath, TrainingRecord, EmployeeWelfare
        )
        
        print("[2/8] 导入线索系统模型 (lead.db)...")
        from app.models.lead_v3 import (
            Lead, LeadFollow, PublicSeaLead,
            LeadDistributionLog, LeadChannelStats
        )
        
        print("[3/8] 导入CRM系统模型 (crm.db)...")
        from app.models.crm_v2 import (
            Customer, CustomerFollow, CustomerServiceHistory
        )
        
        # 创建所有表
        print("\n[4/8] 创建数据库表...")
        db.create_all()
        
        # 初始化基础数据
        print("\n[5/8] 初始化基础数据...")
        init_hr_data()
        
        print("\n[6/8] 验证数据库...")
        verify_databases()
        
        print("\n" + "=" * 70)
        print("数据库初始化完成!")
        print("=" * 70)
        print("\n数据库文件列表:")
        for bind_key, uri in app.config['SQLALCHEMY_BINDS'].items():
            db_path = uri.replace('sqlite:///', '')
            size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            print(f"  {bind_key:12} -> {db_path} ({size} bytes)")

def init_hr_data():
    """初始化HR基础数据"""
    from app.models.hr_v2 import Department, Position
    
    # 检查是否已有数据
    if Department.query.first():
        print("  HR基础数据已存在，跳过初始化")
        return
    
    # 创建默认部门
    departments = [
        Department(code='MGMT', name='管理层', sort_order=1),
        Department(code='SALES', name='销售部', sort_order=2),
        Department(code='DESIGN', name='设计部', sort_order=3),
        Department(code='PROJECT', name='项目部', sort_order=4),
        Department(code='SERVICE', name='客服部', sort_order=5),
        Department(code='HR', name='人力资源部', sort_order=6),
        Department(code='FINANCE', name='财务部', sort_order=7),
        Department(code='MARKET', name='市场部', sort_order=8),
    ]
    
    for dept in departments:
        db.session.add(dept)
    
    db.session.flush()
    
    # 创建默认岗位
    positions = [
        Position(code='CEO', name='总经理', department_id=1, level=10, job_type='管理'),
        Position(code='SALES_MGR', name='销售经理', department_id=2, level=7, job_type='管理'),
        Position(code='SALES', name='销售顾问', department_id=2, level=4, job_type='销售'),
        Position(code='DESIGN_MGR', name='设计总监', department_id=3, level=8, job_type='管理'),
        Position(code='DESIGNER', name='设计师', department_id=3, level=5, job_type='技术'),
        Position(code='PM', name='项目经理', department_id=4, level=6, job_type='管理'),
        Position(code='CS', name='客服专员', department_id=5, level=3, job_type='职能'),
    ]
    
    for pos in positions:
        db.session.add(pos)
    
    db.session.commit()
    print(f"  已创建 {len(departments)} 个部门，{len(positions)} 个岗位")

def verify_databases():
    """验证数据库连接"""
    from sqlalchemy import text
    
    for bind_key in ['auth', 'hr', 'lead', 'crm', 'material', 'project', 'case', 'finance']:
        try:
            engine = db.engines.get(bind_key)
            if engine:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in result]
                    print(f"  [{bind_key:8}] 连接成功，共 {len(tables)} 个表")
        except Exception as e:
            print(f"  [{bind_key:8}] 连接失败: {e}")

if __name__ == '__main__':
    init_databases()
