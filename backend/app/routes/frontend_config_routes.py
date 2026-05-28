"""
前端配置管理 API
支持动态配置 Web 端页面、样式、组件
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.frontend_config import (
    PageConfig, ComponentConfig, ResourceConfig,
    NavigationConfig, ThemeConfig, FrontendVersion
)
from app.routes.auth_routes_v2 import jwt_required_v2

frontend_config_bp = Blueprint('frontend_config', __name__, url_prefix='/api/v3/frontend')


# ==================== 页面配置管理 ====================

@frontend_config_bp.route('/pages', methods=['GET'])
def get_pages():
    """获取所有页面配置列表"""
    pages = PageConfig.query.filter_by(is_enabled=True).all()
    return jsonify({
        'code': 200,
        'data': [p.to_dict() for p in pages],
        'message': 'success'
    })


@frontend_config_bp.route('/pages/<page_key>', methods=['GET'])
def get_page(page_key):
    """获取单个页面配置"""
    page = PageConfig.query.filter_by(
        page_key=page_key,
        is_enabled=True
    ).order_by(PageConfig.version.desc()).first()
    
    if not page:
        return jsonify({'code': 404, 'message': '页面配置不存在'}), 404
    
    return jsonify({
        'code': 200,
        'data': page.to_dict(),
        'message': 'success'
    })


@frontend_config_bp.route('/pages', methods=['POST'])
@jwt_required_v2
def create_page(current_user):
    """创建页面配置"""
    data = request.get_json()
    
    # 检查页面标识是否已存在
    existing = PageConfig.query.filter_by(page_key=data.get('page_key')).first()
    if existing:
        return jsonify({'code': 400, 'message': '页面标识已存在'}), 400
    
    page = PageConfig(
        page_key=data.get('page_key'),
        page_name=data.get('page_name'),
        page_title=data.get('page_title'),
        meta_description=data.get('meta_description'),
        meta_keywords=data.get('meta_keywords'),
        sections=data.get('sections', []),
        custom_css=data.get('custom_css'),
        theme_config=data.get('theme_config', {}),
        is_enabled=data.get('is_enabled', True),
        created_by=current_user.get('id')
    )
    
    db.session.add(page)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': page.to_dict(),
        'message': '页面配置创建成功'
    })


@frontend_config_bp.route('/pages/<int:page_id>', methods=['PUT'])
@jwt_required_v2
def update_page(current_user, page_id):
    """更新页面配置"""
    page = PageConfig.query.get_or_404(page_id)
    data = request.get_json()
    
    # 更新字段
    for field in ['page_name', 'page_title', 'meta_description', 'meta_keywords',
                  'sections', 'custom_css', 'theme_config', 'is_enabled']:
        if field in data:
            setattr(page, field, data[field])
    
    page.version += 1
    page.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': page.to_dict(),
        'message': '页面配置更新成功'
    })


@frontend_config_bp.route('/pages/<int:page_id>', methods=['DELETE'])
@jwt_required_v2
def delete_page(current_user, page_id):
    """删除页面配置（软删除）"""
    page = PageConfig.query.get_or_404(page_id)
    page.is_enabled = False
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '页面配置已删除'
    })


@frontend_config_bp.route('/pages/<int:page_id>/clone', methods=['POST'])
@jwt_required_v2
def clone_page(current_user, page_id):
    """克隆页面配置"""
    source = PageConfig.query.get_or_404(page_id)
    data = request.get_json()
    
    new_page = PageConfig(
        page_key=data.get('page_key'),
        page_name=data.get('page_name', f"{source.page_name} 副本"),
        page_title=source.page_title,
        meta_description=source.meta_description,
        meta_keywords=source.meta_keywords,
        sections=source.sections,
        custom_css=source.custom_css,
        theme_config=source.theme_config,
        parent_id=source.id,
        created_by=current_user.get('id')
    )
    
    db.session.add(new_page)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': new_page.to_dict(),
        'message': '页面配置克隆成功'
    })


# ==================== 组件库管理 ====================

@frontend_config_bp.route('/components', methods=['GET'])
def get_components():
    """获取组件库列表"""
    category = request.args.get('category')
    query = ComponentConfig.query.filter_by(is_enabled=True)
    
    if category:
        query = query.filter_by(category=category)
    
    components = query.all()
    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in components],
        'message': 'success'
    })


@frontend_config_bp.route('/components/<component_key>', methods=['GET'])
def get_component(component_key):
    """获取单个组件配置"""
    component = ComponentConfig.query.filter_by(
        component_key=component_key,
        is_enabled=True
    ).first()
    
    if not component:
        return jsonify({'code': 404, 'message': '组件不存在'}), 404
    
    return jsonify({
        'code': 200,
        'data': component.to_dict(),
        'message': 'success'
    })


@frontend_config_bp.route('/components', methods=['POST'])
@jwt_required_v2
def create_component(current_user):
    """创建组件"""
    data = request.get_json()
    
    component = ComponentConfig(
        component_key=data.get('component_key'),
        component_name=data.get('component_name'),
        component_type=data.get('component_type'),
        config_schema=data.get('config_schema', {}),
        default_config=data.get('default_config', {}),
        template_code=data.get('template_code'),
        preview_image=data.get('preview_image'),
        category=data.get('category', 'general')
    )
    
    db.session.add(component)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': component.to_dict(),
        'message': '组件创建成功'
    })


# ==================== 资源管理 ====================

@frontend_config_bp.route('/about-section', methods=['GET'])
def get_about_section():
    """获取关于我们区块配置（公开）"""
    component = ComponentConfig.query.filter_by(
        component_key='home_about',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': None, 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/about-section', methods=['PUT'])
@jwt_required_v2
def update_about_section(current_user):
    """更新关于我们区块配置"""
    data = request.get_json()
    component = ComponentConfig.query.filter_by(component_key='home_about').first()
    if not component:
        component = ComponentConfig(
            component_key='home_about',
            component_name='首页关于我们',
            component_type='section',
            config_schema={},
            default_config=data,
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = data
    db.session.commit()
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/brand-logos', methods=['GET'])
def get_brand_logos():
    """获取品牌背书 logo 列表（公开）"""
    component = ComponentConfig.query.filter_by(
        component_key='home_brands',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': [], 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config.get('logos', []), 'message': 'success'})


@frontend_config_bp.route('/brand-logos', methods=['PUT'])
@jwt_required_v2
def update_brand_logos(current_user):
    """更新品牌背书 logo 列表"""
    data = request.get_json()
    logos = data.get('logos', [])
    component = ComponentConfig.query.filter_by(component_key='home_brands').first()
    if not component:
        component = ComponentConfig(
            component_key='home_brands',
            component_name='品牌背书',
            component_type='brands',
            config_schema={},
            default_config={'logos': logos},
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = {'logos': logos}
    db.session.commit()
    return jsonify({'code': 200, 'data': logos, 'message': 'success'})


@frontend_config_bp.route('/services-section', methods=['GET'])
def get_services_section():
    """获取服务优势配置（公开）"""
    component = ComponentConfig.query.filter_by(
        component_key='home_services',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': None, 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/services-section', methods=['PUT'])
@jwt_required_v2
def update_services_section(current_user):
    """更新服务优势配置"""
    data = request.get_json()
    component = ComponentConfig.query.filter_by(component_key='home_services').first()
    if not component:
        component = ComponentConfig(
            component_key='home_services',
            component_name='首页服务优势',
            component_type='section',
            config_schema={},
            default_config=data,
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = data
    db.session.commit()
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/cases-section', methods=['GET'])
def get_cases_section():
    """获取精选案例配置（公开）"""
    component = ComponentConfig.query.filter_by(
        component_key='home_cases',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': None, 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/cases-section', methods=['PUT'])
@jwt_required_v2
def update_cases_section(current_user):
    """更新精选案例配置"""
    data = request.get_json()
    component = ComponentConfig.query.filter_by(component_key='home_cases').first()
    if not component:
        component = ComponentConfig(
            component_key='home_cases',
            component_name='首页精选案例',
            component_type='section',
            config_schema={},
            default_config=data,
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = data
    db.session.commit()
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/cta-section', methods=['GET'])
def get_cta_section():
    component = ComponentConfig.query.filter_by(
        component_key='home_cta',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': {
            'title': '准备好打造您的理想之家了吗？',
            'subtitle': '立即预约免费量尺，获取专属设计方案与报价',
            'primaryBtn': '预约免费量尺',
            'secondaryBtn': '400-888-8888'
        }, 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/cta-section', methods=['PUT'])
@jwt_required_v2
def update_cta_section(current_user):
    data = request.get_json()
    component = ComponentConfig.query.filter_by(component_key='home_cta').first()
    if not component:
        component = ComponentConfig(
            component_key='home_cta',
            component_name='首页CTA',
            component_type='section',
            config_schema={},
            default_config=data,
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = data
    db.session.commit()
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/contact-section', methods=['GET'])
def get_contact_section():
    component = ComponentConfig.query.filter_by(
        component_key='home_contact',
        is_enabled=True
    ).first()
    if not component:
        return jsonify({'code': 200, 'data': {
            'address': '成都市青羊区蔡桥街道天府匠芯北区A座6-10',
            'phone': '139 0817 9177',
            'hours': '周一至周日 9:00-18:00'
        }, 'message': 'success'})
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/contact-section', methods=['PUT'])
@jwt_required_v2
def update_contact_section(current_user):
    data = request.get_json()
    component = ComponentConfig.query.filter_by(component_key='home_contact').first()
    if not component:
        component = ComponentConfig(
            component_key='home_contact',
            component_name='首页联系信息',
            component_type='section',
            config_schema={},
            default_config=data,
            category='homepage',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = data
    db.session.commit()
    return jsonify({'code': 200, 'data': component.default_config, 'message': 'success'})


@frontend_config_bp.route('/hero-slides', methods=['GET'])
def get_hero_slides():
    """获取首页轮播图列表"""
    component = ComponentConfig.query.filter_by(
        component_key='home_hero',
        is_enabled=True
    ).first()
    
    if not component:
        # 返回默认轮播图
        return jsonify({
            'code': 200,
            'data': [
                {'id': 1, 'url': 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1920&q=80', 'order': 0},
                {'id': 2, 'url': 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1920&q=80', 'order': 1},
                {'id': 3, 'url': 'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1920&q=80', 'order': 2}
            ],
            'message': 'success'
        })
    
    slides = component.default_config.get('slides', [])
    return jsonify({
        'code': 200,
        'data': slides,
        'message': 'success'
    })


@frontend_config_bp.route('/hero-slides', methods=['PUT'])
@jwt_required_v2
def update_hero_slides(current_user):
    """更新首页轮播图列表"""
    data = request.get_json()
    slides = data.get('slides', [])
    
    component = ComponentConfig.query.filter_by(
        component_key='home_hero'
    ).first()
    
    if not component:
        component = ComponentConfig(
            component_key='home_hero',
            component_name='首页轮播图',
            component_type='hero',
            config_schema={
                'slides': {'type': 'array', 'label': '轮播图片列表'}
            },
            default_config={'slides': slides},
            category='hero',
            is_enabled=True
        )
        db.session.add(component)
    else:
        component.default_config = {'slides': slides}
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': slides,
        'message': '轮播图更新成功'
    })


@frontend_config_bp.route('/resources', methods=['GET'])
def get_resources():
    """获取资源列表"""
    resource_type = request.args.get('type')
    scene = request.args.get('scene')
    
    query = ResourceConfig.query.filter_by(is_enabled=True)
    
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    if scene:
        # JSON 字段查询
        query = query.filter(ResourceConfig.usage_scenes.contains([scene]))
    
    resources = query.order_by(ResourceConfig.created_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in resources],
        'message': 'success'
    })


@frontend_config_bp.route('/resources', methods=['POST'])
@jwt_required_v2
def create_resource(current_user):
    """创建资源记录"""
    data = request.get_json()
    
    resource = ResourceConfig(
        resource_key=data.get('resource_key'),
        resource_name=data.get('resource_name'),
        resource_type=data.get('resource_type'),
        file_url=data.get('file_url'),
        file_path=data.get('file_path'),
        file_size=data.get('file_size'),
        mime_type=data.get('mime_type'),
        width=data.get('width'),
        height=data.get('height'),
        usage_scenes=data.get('usage_scenes', []),
        created_by=current_user.get('id')
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': resource.to_dict(),
        'message': '资源创建成功'
    })


# ==================== 导航配置 ====================

@frontend_config_bp.route('/navigation/<position>', methods=['GET'])
def get_navigation(position):
    """获取导航配置"""
    nav = NavigationConfig.query.filter_by(
        nav_position=position,
        is_enabled=True,
        is_default=True
    ).first()
    
    if not nav:
        # 返回默认导航
        return jsonify({
            'code': 200,
            'data': get_default_navigation(position),
            'message': 'success'
        })
    
    return jsonify({
        'code': 200,
        'data': nav.to_dict(),
        'message': 'success'
    })


def get_default_navigation(position):
    """获取默认导航配置"""
    if position == 'header':
        return {
            'nav_position': 'header',
            'nav_items': [
                {'label': '首页', 'link': '/', 'type': 'link'},
                {'label': '案例', 'link': '/cases', 'type': 'link'},
                {'label': '关于', 'link': '/about', 'type': 'link'},
                {'label': '联系', 'link': '/contact', 'type': 'link'},
                {'label': '预约量尺', 'link': '/book', 'type': 'button'}
            ],
            'style_config': {
                'bg_color': 'transparent',
                'text_color': '#FFFFFF',
                'active_color': '#C4A77D'
            }
        }
    elif position == 'footer':
        return {
            'nav_position': 'footer',
            'nav_items': [
                {
                    'title': '服务',
                    'items': [
                        {'label': '全案设计', 'link': '/services/design'},
                        {'label': '定制家具', 'link': '/services/furniture'},
                        {'label': '施工监理', 'link': '/services/construction'},
                        {'label': '软装搭配', 'link': '/services/decoration'}
                    ]
                },
                {
                    'title': '案例',
                    'items': [
                        {'label': '实景案例', 'link': '/cases'},
                        {'label': '在建工地', 'link': '/cases?type=ongoing'},
                        {'label': '设计方案', 'link': '/cases?type=design'}
                    ]
                },
                {
                    'title': '关于',
                    'items': [
                        {'label': '品牌故事', 'link': '/about'},
                        {'label': '设计团队', 'link': '/team'},
                        {'label': '合作伙伴', 'link': '/partners'}
                    ]
                },
                {
                    'title': '联系',
                    'items': [
                        {'label': '预约量尺', 'link': '/book'},
                        {'label': '展厅地址', 'link': '/contact'},
                        {'label': '400-888-8888', 'link': 'tel:4008888888'}
                    ]
                }
            ]
        }
    return {}


@frontend_config_bp.route('/navigation', methods=['POST'])
@jwt_required_v2
def save_navigation(current_user):
    """保存导航配置"""
    data = request.get_json()
    position = data.get('nav_position')
    
    # 取消之前的默认配置
    NavigationConfig.query.filter_by(
        nav_position=position,
        is_default=True
    ).update({'is_default': False})
    
    nav = NavigationConfig(
        nav_position=position,
        nav_items=data.get('nav_items', []),
        style_config=data.get('style_config', {}),
        is_default=True
    )
    
    db.session.add(nav)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': nav.to_dict(),
        'message': '导航配置保存成功'
    })


# ==================== 主题配置 ====================

@frontend_config_bp.route('/themes', methods=['GET'])
def get_themes():
    """获取所有主题"""
    themes = ThemeConfig.query.all()
    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in themes],
        'message': 'success'
    })


@frontend_config_bp.route('/themes/active', methods=['GET'])
def get_active_theme():
    """获取当前激活主题"""
    theme = ThemeConfig.query.filter_by(is_active=True).first()
    
    if not theme:
        # 返回默认主题
        return jsonify({
            'code': 200,
            'data': {
                'theme_name': 'D&B 帝标|设记家默认主题',
                'theme_key': 'designary_default',
                'colors': {
                    'primary': '#8B7355',
                    'secondary': '#C4A77D',
                    'accent': '#D4A574',
                    'background': '#FAF8F5',
                    'surface': '#FFFFFF',
                    'text': '#2C2420',
                    'text_secondary': '#6B6560',
                    'border': '#E8E4E0'
                },
                'fonts': {
                    'heading': 'system-ui, -apple-system, sans-serif',
                    'body': 'system-ui, -apple-system, sans-serif'
                },
                'spacing': {
                    'xs': '4px',
                    'sm': '8px',
                    'md': '16px',
                    'lg': '24px',
                    'xl': '40px',
                    'xxl': '64px'
                },
                'border_radius': {
                    'sm': '4px',
                    'md': '8px',
                    'lg': '16px',
                    'xl': '24px'
                },
                'shadows': {
                    'sm': '0 2px 8px rgba(44, 36, 32, 0.06)',
                    'md': '0 4px 20px rgba(44, 36, 32, 0.08)',
                    'lg': '0 10px 40px rgba(44, 36, 32, 0.12)'
                }
            },
            'message': 'success'
        })
    
    return jsonify({
        'code': 200,
        'data': theme.to_dict(),
        'message': 'success'
    })


@frontend_config_bp.route('/themes', methods=['POST'])
@jwt_required_v2
def create_theme(current_user):
    """创建主题"""
    data = request.get_json()
    
    theme = ThemeConfig(
        theme_name=data.get('theme_name'),
        theme_key=data.get('theme_key'),
        colors=data.get('colors', {}),
        fonts=data.get('fonts', {}),
        spacing=data.get('spacing', {}),
        border_radius=data.get('border_radius', {}),
        shadows=data.get('shadows', {})
    )
    
    db.session.add(theme)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': theme.to_dict(),
        'message': '主题创建成功'
    })


@frontend_config_bp.route('/themes/<int:theme_id>', methods=['PUT'])
@jwt_required_v2
def update_theme(current_user, theme_id):
    """更新主题"""
    theme = ThemeConfig.query.get_or_404(theme_id)
    data = request.get_json()
    
    for field in ['theme_name', 'theme_key', 'description', 'colors', 'fonts',
                   'spacing', 'border_radius', 'shadows', 'section_configs']:
        if field in data:
            setattr(theme, field, data[field])
    
    theme.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': theme.to_dict(),
        'message': '主题更新成功'
    })


@frontend_config_bp.route('/themes/<int:theme_id>', methods=['DELETE'])
@jwt_required_v2
def delete_theme(current_user, theme_id):
    """删除主题"""
    theme = ThemeConfig.query.get_or_404(theme_id)
    if theme.is_active:
        return jsonify({'code': 400, 'message': '不能删除当前激活的主题'}), 400
    db.session.delete(theme)
    db.session.commit()
    return jsonify({'code': 200, 'message': '主题已删除'})


@frontend_config_bp.route('/themes/<int:theme_id>/activate', methods=['POST'])
@jwt_required_v2
def activate_theme(current_user, theme_id):
    """激活主题"""
    # 取消其他激活主题
    ThemeConfig.query.filter_by(is_active=True).update({'is_active': False})
    
    theme = ThemeConfig.query.get_or_404(theme_id)
    theme.is_active = True
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '主题已激活'
    })


# ==================== 版本管理 ====================

@frontend_config_bp.route('/versions', methods=['GET'])
@jwt_required_v2
def get_versions(current_user):
    """获取版本列表"""
    versions = FrontendVersion.query.order_by(FrontendVersion.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'data': [v.to_dict() for v in versions],
        'message': 'success'
    })


@frontend_config_bp.route('/versions', methods=['POST'])
@jwt_required_v2
def create_version(current_user):
    """创建新版本"""
    data = request.get_json()
    
    # 获取当前所有配置的快照
    pages = PageConfig.query.filter_by(is_enabled=True).all()
    active_theme = ThemeConfig.query.filter_by(is_active=True).first()
    
    version = FrontendVersion(
        version=data.get('version'),
        version_name=data.get('version_name'),
        changes=data.get('changes'),
        change_list=data.get('change_list', []),
        page_configs=[p.to_dict() for p in pages],
        theme_config=active_theme.to_dict() if active_theme else None,
        status='draft',
        published_by=current_user.get('id')
    )
    
    db.session.add(version)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': version.to_dict(),
        'message': '版本创建成功'
    })


@frontend_config_bp.route('/versions/<int:version_id>/publish', methods=['POST'])
@jwt_required_v2
def publish_version(current_user, version_id):
    """发布版本"""
    version = FrontendVersion.query.get_or_404(version_id)
    version.status = 'published'
    version.published_at = datetime.now()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '版本已发布'
    })


# ==================== 前端渲染接口（公开） ====================

@frontend_config_bp.route('/render/<page_key>', methods=['GET'])
def render_page(page_key):
    """获取页面渲染数据（前端调用）"""
    # 获取页面配置
    page = PageConfig.query.filter_by(
        page_key=page_key,
        is_enabled=True
    ).order_by(PageConfig.version.desc()).first()
    
    if not page:
        return jsonify({'code': 404, 'message': '页面不存在'}), 404
    
    # 获取当前主题
    theme = ThemeConfig.query.filter_by(is_active=True).first()
    
    # 获取导航
    header_nav = NavigationConfig.query.filter_by(
        nav_position='header',
        is_enabled=True,
        is_default=True
    ).first()
    
    footer_nav = NavigationConfig.query.filter_by(
        nav_position='footer',
        is_enabled=True,
        is_default=True
    ).first()
    
    return jsonify({
        'code': 200,
        'data': {
            'page': page.to_dict(),
            'theme': theme.to_dict() if theme else None,
            'navigation': {
                'header': header_nav.to_dict() if header_nav else get_default_navigation('header'),
                'footer': footer_nav.to_dict() if footer_nav else get_default_navigation('footer')
            }
        },
        'message': 'success'
    })


@frontend_config_bp.route('/render-config', methods=['GET'])
def get_render_config():
    """获取全局渲染配置（前端初始化调用）"""
    # 获取当前激活主题
    theme = ThemeConfig.query.filter_by(is_active=True).first()
    
    # 获取启用的页面列表
    pages = PageConfig.query.filter_by(is_enabled=True).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'theme': theme.to_dict() if theme else get_default_theme(),
            'pages': [{'key': p.page_key, 'name': p.page_name} for p in pages],
            'api_base': '/api/v3'
        },
        'message': 'success'
    })


def get_default_theme():
    """获取默认主题配置"""
    return {
        'theme_name': 'D&B 帝标|设记家默认主题',
        'theme_key': 'designary_default',
        'colors': {
            'primary': '#8B7355',
            'secondary': '#C4A77D',
            'accent': '#D4A574',
            'background': '#FAF8F5',
            'surface': '#FFFFFF',
            'text': '#2C2420',
            'text_secondary': '#6B6560',
            'border': '#E8E4E0'
        },
        'fonts': {
            'heading': 'system-ui, -apple-system, sans-serif',
            'body': 'system-ui, -apple-system, sans-serif'
        }
    }
    return theme_config

# Frontend config public endpoint

@frontend_config_bp.route('/public', methods=['GET'])
def get_public_frontend_config():
    """Get frontend config (public, no auth required)"""
    from app.models.frontend_config import ComponentConfig

    config = ComponentConfig.query.first()
    if not config:
        return jsonify({'code': 200, 'data': {}})

    return jsonify({'code': 200, 'data': config.to_dict()})


