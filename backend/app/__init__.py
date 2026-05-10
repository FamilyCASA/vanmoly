"""
D&B 帝标|设记家全安落地服务系统 V3.2.0
Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from pathlib import Path

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    # 全局 CORS 配置 - 支持所有来源和方法
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }
    })

    # 注册蓝图
    from app.routes.case_routes import case_bp
    from app.routes.lead_routes import lead_bp
    from app.routes.lead_routes_v2 import lead_v2_bp
    from app.routes.appointment_routes import appointment_bp
    from app.routes.coupon_routes import coupon_bp
    from app.routes.article_routes import article_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.frontend_config_routes import frontend_config_bp
    from app.routes.customer_routes import customer_bp
    from app.routes.material_sku_routes import material_sku_bp
    from app.routes.service_workflow_routes import service_workflow_bp
    from app.routes.employee_routes import employee_bp
    from app.routes.contract_routes import contract_bp
    from app.routes.building_routes import building_bp
    from app.routes.quote_routes import quote_bp
    from app.routes.scheme_routes import scheme_bp
    from app.routes.hr_routes_v2 import hr_v2_bp
    from app.routes.auth_routes_v2 import auth_v2_bp
    from app.routes.customer_routes_v2 import customer_v2_bp
    # V3.2 新增
    from app.routes.space_config_routes import space_config_bp
    from app.routes.store_routes import store_bp
    from app.routes.knowledge_routes import knowledge_bp
    from app.routes.building_survey_routes import survey_bp

    app.register_blueprint(case_bp, url_prefix='/api/v3')
    app.register_blueprint(lead_bp, url_prefix='/api/v3')
    app.register_blueprint(lead_v2_bp)  # 蓝图内部已定义路由路径
    app.register_blueprint(appointment_bp, url_prefix='/api/v3')
    app.register_blueprint(coupon_bp, url_prefix='/api/v3')
    app.register_blueprint(article_bp, url_prefix='/api/v3')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v3')
    # app.register_blueprint(auth_bp, url_prefix='/api/v3')  # 旧版认证已禁用，使用 auth_v2_bp
    app.register_blueprint(upload_bp, url_prefix='/api/v3')
    app.register_blueprint(frontend_config_bp)  # 蓝图内部已定义url_prefix='/api/v3/frontend'
    app.register_blueprint(customer_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(material_sku_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(service_workflow_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(employee_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(contract_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(building_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(quote_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(scheme_bp)  # 蓝图已定义url_prefix
    app.register_blueprint(hr_v2_bp)  # HR V2 路由
    app.register_blueprint(auth_v2_bp, url_prefix='/api/v3/auth')  # 认证 V2 路由
    app.register_blueprint(customer_v2_bp, url_prefix='/api/v3')  # 客户 V2 路由
    app.register_blueprint(space_config_bp, url_prefix='/api/v3/space-configs')  # V3.2 空间配置路由
    app.register_blueprint(store_bp, url_prefix='/api/v3')  # 分店管理路由
    app.register_blueprint(knowledge_bp)  # 知识库路由
    app.register_blueprint(survey_bp)  # 楼盘调查路由

    # 上传文件静态服务 - 必须在蓝图外注册，确保 /upload/ 路径可访问
    @app.route('/upload/<path:filename>')
    def serve_upload(filename):
        """Serve uploaded files directly at /upload/ path"""
        from flask import send_from_directory
        upload_dir = str(Path(__file__).parent.parent / 'upload')
        return send_from_directory(upload_dir, filename)

    # 旧数据兼容：/static/uploads/ 路径
    @app.route('/static/uploads/<path:filename>')
    def serve_static_uploads(filename):
        """Serve old-style static upload files"""
        from flask import send_from_directory
        static_dir = str(Path(__file__).parent.parent / 'static' / 'uploads')
        return send_from_directory(static_dir, filename)

    # 根路由 - 健康检查
    @app.route('/')
    def index():
        return {'code': 200, 'message': 'D&B 帝标|设记家 V3.0 API服务运行中', 'data': {'version': '3.0.4', 'status': 'running'}}

    @app.route('/api/v3/')
    def api_index():
        return {'code': 200, 'message': 'D&B 帝标|设记家 V3.0 API', 'data': {'version': '3.0.4', 'prefix': '/api/v3'}}

    # 注册错误处理
    register_error_handlers(app)

    # 创建数据库表和上传目录
    with app.app_context():
        db.create_all()
        
        # 创建上传目录
        from app.utils.upload import ensure_upload_dirs
        ensure_upload_dirs()

    return app


def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(400)
    def bad_request(error):
        return {'code': 400, 'message': '请求参数错误', 'data': None}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'code': 401, 'message': '未授权', 'data': None}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'code': 403, 'message': '权限不足', 'data': None}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'message': '资源不存在', 'data': None}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'code': 500, 'message': '服务器内部错误', 'data': None}, 500
