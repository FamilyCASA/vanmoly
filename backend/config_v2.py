"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 配置文件 - 多数据库架构
8个业务域独立数据库
"""
import os
from datetime import timedelta


class Config:
    """基础配置类 - 多数据库架构"""
    
    # 应用密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vanmoly-v3.0-secret-key-dev'
    
    # 基础目录
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # 主数据库（认证、配置、系统级）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(INSTANCE_DIR, 'auth.db')
    
    # 多数据库绑定配置 - 8个业务域
    SQLALCHEMY_BINDS = {
        # 1. 认证中心 - 用户、权限、租户、系统配置
        'auth': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'auth.db'),
        
        # 2. 人力资源 - 员工、部门、岗位、薪酬、绩效、成长
        'hr': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'hr.db'),
        
        # 3. 客户关系 - 客户、跟进记录、服务历史
        'crm': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'crm.db'),
        
        # 4. 线索管理 - 线索、线索分配、公海、积分
        'lead': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'lead.db'),
        
        # 5. 物料库存 - SKU、分类、供应商、库存
        'material': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'material.db'),
        
        # 6. 项目管理 - 合同、报价、方案、楼盘
        'project': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'project.db'),
        
        # 7. 案例展示 - 案例、订阅、客资、模板
        'case': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'case.db'),
        
        # 8. 财务中心 - 收款、付款、发票、对账
        'finance': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'finance.db'),
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'vanmoly-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # 租户配置
    DEFAULT_TENANT_ID = 'default'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    
    # HR积分规则配置
    HR_POINTS_RULES = {
        'lead_entry': 1,           # 录入线索
        'lead_follow': 1,          # 跟进线索
        'appointment_booked': 0.5, # 预约到店
        'appointment_actual': 2,   # 实际到店
        'demand_confirmed': 1,     # 需求确认
        'deposit_paid': 10,        # 交定金
        'contract_signed_small': 10,   # 签约小单
        'contract_signed_medium': 30,  # 签约中单
        'contract_signed_large': 60,   # 签约大单
    }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        if not os.environ.get('SECRET_KEY'):
            raise ValueError('生产环境必须设置 SECRET_KEY 环境变量')
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError('生产环境必须设置 JWT_SECRET_KEY 环境变量')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
