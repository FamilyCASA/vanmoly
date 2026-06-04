"""
D&B 帝标|设记家全案落地服务系统 DEMO V3.0.1 配置文件
"""
import os
from datetime import timedelta


class Config:
    """基础配置类"""
    
    # 应用密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vanmoly-v3.0-secret-key-dev'
    
    # 数据库配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # 主数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(INSTANCE_DIR, 'vanmoly_v3.db')
    
    # 多数据库绑定（已废弃，V3.0 统一使用主数据库 vanmoly_v3.db）
    # 保留 material 是因为 material.db 有部分 SKU 数据暂未迁移
    SQLALCHEMY_BINDS = {
        'material': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'material.db'),
        'quote': 'sqlite:///' + os.path.join(INSTANCE_DIR, 'quotes.db'),
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


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境必须使用环境变量设置密钥
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
