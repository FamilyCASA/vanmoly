"""
前端配置管理模型
支持动态配置 Web 端页面、样式、组件、资源
"""
from datetime import datetime
from app import db

class PageConfig(db.Model):
    """页面配置"""
    __tablename__ = 'page_config'
    
    id = db.Column(db.Integer, primary_key=True)
    page_key = db.Column(db.String(50), unique=True, nullable=False, comment='页面标识，如 home, cases, about')
    page_name = db.Column(db.String(100), nullable=False, comment='页面名称')
    page_title = db.Column(db.String(200), comment='页面标题')
    meta_description = db.Column(db.Text, comment='SEO描述')
    meta_keywords = db.Column(db.String(500), comment='SEO关键词')
    
    # 页面结构配置（JSON格式）
    sections = db.Column(db.JSON, default=list, comment='页面区块配置数组')
    
    # 样式配置
    custom_css = db.Column(db.Text, comment='自定义CSS')
    theme_config = db.Column(db.JSON, default=dict, comment='主题色配置')
    
    # 状态
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认配置')
    
    # 版本控制
    version = db.Column(db.Integer, default=1, comment='配置版本')
    parent_id = db.Column(db.Integer, db.ForeignKey('page_config.id'), nullable=True, comment='父配置ID，用于版本继承')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='创建人')
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_key': self.page_key,
            'page_name': self.page_name,
            'page_title': self.page_title,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'sections': self.sections,
            'custom_css': self.custom_css,
            'theme_config': self.theme_config,
            'is_enabled': self.is_enabled,
            'is_default': self.is_default,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ComponentConfig(db.Model):
    """组件配置库"""
    __tablename__ = 'component_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 组件标识
    component_key = db.Column(db.String(50), unique=True, nullable=False, comment='组件标识')
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    component_type = db.Column(db.String(50), nullable=False, comment='组件类型：hero/banner/card/list/form等')
    
    # 组件配置Schema（定义可配置字段）
    config_schema = db.Column(db.JSON, nullable=False, comment='配置字段定义')
    
    # 默认配置
    default_config = db.Column(db.JSON, default=dict, comment='默认配置值')
    
    # 组件模板（Vue组件代码或配置模板）
    template_code = db.Column(db.Text, comment='组件模板代码')
    
    # 预览图
    preview_image = db.Column(db.String(500), comment='预览图URL')
    
    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50), default='general', comment='分类：general/hero/content/form/media')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'component_key': self.component_key,
            'component_name': self.component_name,
            'component_type': self.component_type,
            'config_schema': self.config_schema,
            'default_config': self.default_config,
            'preview_image': self.preview_image,
            'is_enabled': self.is_enabled,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ResourceConfig(db.Model):
    """资源管理（图片、视频、文件等）"""
    __tablename__ = 'resource_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 资源标识
    resource_key = db.Column(db.String(100), unique=True, nullable=False, comment='资源标识')
    resource_name = db.Column(db.String(200), nullable=False, comment='资源名称')
    resource_type = db.Column(db.String(50), nullable=False, comment='类型：image/video/file/font')
    
    # 资源地址
    file_url = db.Column(db.String(500), comment='文件URL')
    file_path = db.Column(db.String(500), comment='本地文件路径')
    file_size = db.Column(db.Integer, comment='文件大小（字节）')
    mime_type = db.Column(db.String(100), comment='MIME类型')
    
    # 图片特有
    width = db.Column(db.Integer, comment='图片宽度')
    height = db.Column(db.Integer, comment='图片高度')
    
    # 使用场景
    usage_scenes = db.Column(db.JSON, default=list, comment='使用场景标签')
    
    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('employee.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'resource_key': self.resource_key,
            'resource_name': self.resource_name,
            'resource_type': self.resource_type,
            'file_url': self.file_url,
            'width': self.width,
            'height': self.height,
            'usage_scenes': self.usage_scenes,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NavigationConfig(db.Model):
    """导航配置"""
    __tablename__ = 'navigation_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 导航位置
    nav_position = db.Column(db.String(50), nullable=False, comment='位置：header/footer/mobile')
    
    # 导航项
    nav_items = db.Column(db.JSON, default=list, comment='导航项数组')
    
    # 样式
    style_config = db.Column(db.JSON, default=dict, comment='样式配置')
    
    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nav_position': self.nav_position,
            'nav_items': self.nav_items,
            'style_config': self.style_config,
            'is_enabled': self.is_enabled,
            'is_default': self.is_default
        }


class ThemeConfig(db.Model):
    """主题配置"""
    __tablename__ = 'theme_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    theme_name = db.Column(db.String(100), nullable=False, comment='主题名称')
    theme_key = db.Column(db.String(50), unique=True, nullable=False, comment='主题标识')
    
    # 颜色配置
    colors = db.Column(db.JSON, default=dict, comment='颜色配置JSON')
    
    # 字体配置
    fonts = db.Column(db.JSON, default=dict, comment='字体配置JSON')
    
    # 间距/圆角等
    spacing = db.Column(db.JSON, default=dict, comment='间距配置')
    border_radius = db.Column(db.JSON, default=dict, comment='圆角配置')
    shadows = db.Column(db.JSON, default=dict, comment='阴影配置')
    
    # 状态
    is_active = db.Column(db.Boolean, default=False, comment='是否当前激活主题')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认主题')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'theme_name': self.theme_name,
            'theme_key': self.theme_key,
            'colors': self.colors,
            'fonts': self.fonts,
            'spacing': self.spacing,
            'border_radius': self.border_radius,
            'shadows': self.shadows,
            'is_active': self.is_active,
            'is_default': self.is_default
        }


class FrontendVersion(db.Model):
    """前端版本发布记录"""
    __tablename__ = 'frontend_version'
    
    id = db.Column(db.Integer, primary_key=True)
    
    version = db.Column(db.String(20), nullable=False, comment='版本号，如 3.0.1')
    version_name = db.Column(db.String(100), comment='版本名称')
    
    # 变更内容
    changes = db.Column(db.Text, comment='变更说明')
    change_list = db.Column(db.JSON, default=list, comment='变更列表')
    
    # 配置快照
    page_configs = db.Column(db.JSON, comment='页面配置快照')
    theme_config = db.Column(db.JSON, comment='主题配置快照')
    
    # 发布状态
    status = db.Column(db.String(20), default='draft', comment='状态：draft/published/rollback')
    published_at = db.Column(db.DateTime, comment='发布时间')
    published_by = db.Column(db.Integer, db.ForeignKey('employee.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'version_name': self.version_name,
            'changes': self.changes,
            'change_list': self.change_list,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
