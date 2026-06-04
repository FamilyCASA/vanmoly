# -*- coding: utf-8 -*-
"""
种子脚本：为 ThemeConfig 表添加"暗黑"模板和"简约科技"模板
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.frontend_config import ThemeConfig

app = create_app()

with app.app_context():
    # === Plan A: 暗黑暖光奢华模板 ===
    dark_warm = ThemeConfig(
        theme_key='plan_a_warm_dark',
        theme_name='暗黑 · 暖光奢华',
        description='方案A：暖色深灰背景+原木棕点缀，底部暖光渐变，玻璃态卡片，温暖奢华感',
        colors={
            'primary': '#8B5A2B',        # 品牌原木棕（主色）
            'secondary': '#C9956A',     # 浅驼色
            'accent': '#D4A574',        # 暖强调色
            'background': '#0f0f14',    # 微暖深灰背景
            'surface': '#1e1c1a',       # 暖灰卡片背景
            'elevated': '#2a2018',      # 暖灰悬浮层
            'text': '#F5E6D3',          # 米白主文字
            'text_secondary': '#C9956A', # 暖灰次要文字
            'border': 'rgba(139,90,43,0.20)',  # 原木边框
            'hero_overlay_start': 'rgba(30,28,26,0.88)',
            'hero_overlay_end': 'rgba(30,28,26,0.40)',
            'warm_glow': 'rgba(139,90,43,0.25)',
            'glass_bg': 'rgba(139,90,43,0.06)',
            'glass_border': 'rgba(139,90,43,0.20)',
            'glass_hover_bg': 'rgba(139,90,43,0.10)',
            'glass_hover_border': 'rgba(139,90,43,0.40)',
            'btn_primary_bg': 'linear-gradient(135deg, #8B5A2B, #A0692F)',
            'btn_primary_shadow': 'rgba(139,90,43,0.30)',
            'btn_outline_color': '#C9956A',
            'btn_outline_border': 'rgba(139,90,43,0.60)',
            'title_gradient_start': '#F5E6D3',
            'title_gradient_end': '#C9956A',
        },
        fonts={
            'heading': 'system-ui, -apple-system, sans-serif',
            'body': 'system-ui, -apple-system, sans-serif',
        },
        spacing={
            'xs': '4px', 'sm': '8px', 'md': '16px',
            'lg': '24px', 'xl': '40px', 'xxl': '64px',
        },
        border_radius={
            'sm': '4px', 'md': '8px', 'lg': '16px', 'xl': '24px',
        },
        shadows={
            'sm': '0 2px 8px rgba(0,0,0,0.15)',
            'md': '0 4px 20px rgba(0,0,0,0.20)',
            'lg': '0 10px 40px rgba(0,0,0,0.25)',
            'warm': '0 8px 32px rgba(139,90,43,0.15)',
        },
        section_configs={
            'hero': {
                'overlay_gradient': 'linear-gradient(135deg, rgba(30,28,26,0.88) 0%, rgba(30,28,26,0.65) 50%, rgba(30,28,26,0.40) 100%)',
                'bottom_warm_glow': 'linear-gradient(to top, rgba(139,90,43,0.18) 0%, transparent 100%)',
                'bottom_glow_height': '300px',
                'text_gradient': 'linear-gradient(135deg, #F5E6D3 0%, #C9956A 100%)',
            },
            'cta': {
                'background': '#0f0f14',
                'warm_glow': 'radial-gradient(ellipse at center, rgba(139,90,43,0.20) 0%, transparent 65%)',
                'title_color': '#fff',
                'desc_color': 'rgba(255,255,255,0.80)',
            },
            'service_card': {
                'background': 'rgba(30,28,26,0.60)',
                'border': '1px solid rgba(139,90,43,0.15)',
                'border_radius': '16px',
                'hover_bg': 'rgba(139,90,43,0.12)',
                'hover_border': 'rgba(139,90,43,0.40)',
                'backdrop_blur': '16px',
                'icon_bg': 'linear-gradient(135deg, rgba(139,90,43,0.30), rgba(139,90,43,0.10))',
                'icon_border': '1px solid rgba(139,90,43,0.30)',
                'icon_color': '#C9956A',
            },
            'about': {
                'background': '#0f0f14',
                'stat_value_gradient': 'linear-gradient(135deg, #C9956A 0%, #8B5A2B 100%)',
            },
            'brand_item': {
                'background': 'rgba(30,28,26,0.60)',
                'border': '1px solid rgba(139,90,43,0.15)',
                'hover_bg': 'rgba(139,90,43,0.10)',
                'hover_border': 'rgba(139,90,43,0.40)',
            },
            'footer': {
                'background': '#0a0a0f',
                'brand_color': '#C9956A',
            },
        },
        is_active=False,
        is_default=False,
    )

    # === 简约科技风模板（明亮主题）===
    light_minimal = ThemeConfig(
        theme_key='light_minimal',
        theme_name='简约 · 科技风',
        description='明亮米白背景，原木棕品牌色，简约清爽，适合对外展示',
        colors={
            'primary': '#8B7355',
            'secondary': '#C4A77D',
            'accent': '#D4A574',
            'background': '#FAF8F5',
            'surface': '#FFFFFF',
            'elevated': '#F5F3F0',
            'text': '#2C2420',
            'text_secondary': '#6B6560',
            'border': '#E8E4E0',
        },
        fonts={
            'heading': 'system-ui, -apple-system, sans-serif',
            'body': 'system-ui, -apple-system, sans-serif',
        },
        spacing={
            'xs': '4px', 'sm': '8px', 'md': '16px',
            'lg': '24px', 'xl': '40px', 'xxl': '64px',
        },
        border_radius={
            'sm': '4px', 'md': '8px', 'lg': '16px', 'xl': '24px',
        },
        shadows={
            'sm': '0 2px 8px rgba(44,36,32,0.06)',
            'md': '0 4px 20px rgba(44,36,32,0.08)',
            'lg': '0 10px 40px rgba(44,36,32,0.12)',
        },
        section_configs={},
        is_active=True,   # 默认激活简约科技风
        is_default=True,
    )

    # Upsert themes (check existence first)
    for theme in [dark_warm, light_minimal]:
        existing = ThemeConfig.query.filter_by(theme_key=theme.theme_key).first()
        if existing:
            print(f'Theme "{theme.theme_name}" already exists, skipping.')
        else:
            db.session.add(theme)
            print(f'Added theme: {theme.theme_name} ({theme.theme_key})')

    db.session.commit()
    print('\nDone! Themes:')
    for t in ThemeConfig.query.all():
        print(f'  [{t.theme_key}] {t.theme_name} - active={t.is_active}')
