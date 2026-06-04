#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端配置种子数据脚本
为 frontend_config、page_config、theme_config 等表插入初始数据
"""
import sys
import os

# 添加后端目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.frontend_config import (
    PageConfig, ComponentConfig, ResourceConfig,
    NavigationConfig, ThemeConfig, FrontendVersion
)
from datetime import datetime
import json

def seed_theme():
    """种子主题配置"""
    from app import db
    # 检查是否已存在默认主题
    if ThemeConfig.query.filter_by(theme_key='designary_default').first():
        print("默认主题已存在，跳过")
        return

    theme = ThemeConfig(
        theme_name='帝标·设记家默认主题',
        theme_key='designary_default',
        colors={
            'primary': '#409EFF',
            'brand': '#8B5A2B',  # 品牌棕
            'success': '#67C23A',
            'warning': '#E6A23C',
            'danger': '#F56C6C',
            'info': '#909399',
            'text_primary': '#303133',
            'text_regular': '#606266',
            'text_secondary': '#909399',
            'border': '#DCDFE6',
            'background': '#F5F7FA'
        },
        fonts={
            'primary': "'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif"
        },
        spacing={
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
            'lg': '24px',
            'xl': '32px'
        },
        border_radius={
            'sm': '4px',
            'md': '8px',
            'lg': '16px'
        },
        shadows={
            'sm': '0 2px 4px rgba(0,0,0,0.1)',
            'md': '0 4px 12px rgba(0,0,0,0.1)',
            'lg': '0 8px 24px rgba(0,0,0,0.15)'
        },
        is_active=True,
        is_default=True
    )
    db.session.add(theme)
    db.session.commit()
    print("主题配置种子数据插入完成")


def seed_pages():
    """种子页面配置"""
    from app import db
    # 首页配置
    if PageConfig.query.filter_by(page_key='home').first():
        print("首页配置已存在，跳过")
        return

    home_page = PageConfig(
        page_key='home',
        page_name='首页',
        page_title='帝标·设记家 - 全案落地装修服务',
        meta_description='帝标·设记家提供全屋定制、全案落地装修服务，20年品牌经验，iF金奖设计团队',
        meta_keywords='全屋定制,全案落地,装修设计,帝标设记家',
        sections=[
            {'type': 'hero', 'component_key': 'home_hero', 'order': 1, 'is_enabled': True},
            {'type': 'section', 'component_key': 'featured_cases', 'order': 2, 'is_enabled': True},
            {'type': 'section', 'component_key': 'service_advantages', 'order': 3, 'is_enabled': True}
        ],
        theme_config={
            'hero_background': '/uploads/frontend/hero_bg.jpg',
            'section_spacing': '64px 0'
        },
        is_enabled=True,
        is_default=True,
        version=1
    )

    # 案例页配置
    cases_page = PageConfig(
        page_key='cases',
        page_name='案例展示',
        page_title='装修案例 - 帝标·设记家',
        meta_description='浏览帝标·设记家最新装修案例，包含多种风格实景参考',
        meta_keywords='装修案例,实景案例,全屋定制案例',
        sections=[
            {'type': 'filter_bar', 'component_key': 'case_filter', 'order': 1, 'is_enabled': True},
            {'type': 'grid', 'component_key': 'case_grid', 'order': 2, 'is_enabled': True}
        ],
        is_enabled=True,
        version=1
    )

    db.session.add_all([home_page, cases_page])
    db.session.commit()
    print("页面配置种子数据插入完成")


def seed_navigation():
    """种子导航配置"""
    from app import db
    # 页头导航
    if NavigationConfig.query.filter_by(nav_position='header').first():
        print("页头导航已存在，跳过")
        return

    header_nav = NavigationConfig(
        nav_position='header',
        nav_items=[
            {'label': '首页', 'path': '/', 'order': 1, 'is_enabled': True},
            {'label': '案例', 'path': '/cases', 'order': 2, 'is_enabled': True},
            {'label': '产品', 'path': '/products', 'order': 3, 'is_enabled': True},
            {'label': '关于我们', 'path': '/about', 'order': 4, 'is_enabled': True}
        ],
        style_config={
            'background': '#fff',
            'text_color': '#303133',
            'active_color': '#8B5A2B',
            'height': '60px'
        },
        is_enabled=True,
        is_default=True
    )

    db.session.add(header_nav)
    db.session.commit()
    print("导航配置种子数据插入完成")


def seed_components():
    """种子组件配置"""
    from app import db
    if ComponentConfig.query.filter_by(component_key='home_hero').first():
        print("组件配置已存在，跳过")
        return

    components = [
        ComponentConfig(
            component_key='home_hero',
            component_name='首页英雄区',
            component_type='hero',
            config_schema={
                'title': {'type': 'string', 'label': '标题', 'default': '帝标·设记家'},
                'subtitle': {'type': 'string', 'label': '副标题', 'default': '全案落地装修服务，20年品牌保障'},
                'background_image': {'type': 'image', 'label': '背景图', 'default': '/uploads/frontend/hero_bg.jpg'},
                'cta_text': {'type': 'string', 'label': '按钮文字', 'default': '免费预约量尺'}
            },
            default_config={
                'title': '帝标·设记家',
                'subtitle': '全案落地装修服务，20年品牌保障',
                'background_image': '/uploads/frontend/hero_bg.jpg',
                'cta_text': '免费预约量尺'
            },
            category='hero',
            is_enabled=True
        )
    ]

    db.session.add_all(components)
    db.session.commit()
    print("组件配置种子数据插入完成")


def seed_resources():
    """种子资源配置"""
    from app import db
    if ResourceConfig.query.filter_by(resource_key='logo').first():
        print("资源配置已存在，跳过")
        return

    resources = [
        ResourceConfig(
            resource_key='logo',
            resource_name='网站Logo',
            resource_type='image',
            file_url='/logo.png',
            usage_scenes=['header', 'footer'],
            is_enabled=True
        )
    ]

    db.session.add_all(resources)
    db.session.commit()
    print("资源配置种子数据插入完成")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from app import db
        print("开始插入前端配置种子数据...")
        seed_theme()
        seed_pages()
        seed_navigation()
        seed_components()
        seed_resources()
        print("前端配置种子数据插入完成！")
