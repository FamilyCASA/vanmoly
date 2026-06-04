"""
前端配置种子数据初始化脚本
为前端配置管理系统创建预设的页面、主题、导航等配置
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.frontend_config import PageConfig, ThemeConfig, NavigationConfig, ComponentConfig, ResourceConfig

def init_frontend_config():
    """初始化前端配置数据"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有数据
        if PageConfig.query.first():
            print('前端配置数据已存在，跳过初始化')
            return
        
        # ========== 主题配置 ==========
        default_theme = ThemeConfig(
            theme_key='default',
            theme_name='默认主题',
            colors={
                'primary': '#8B7355',
                'secondary': '#C4A77D', 
                'accent': '#D4A574',
                'background': '#FAF8F5',
                'surface': '#FFFFFF',
                'text': '#2C2420',
                'text_secondary': '#6B6560',
                'border': '#E8E4E0'
            },
            fonts={
                'primary': 'PingFang SC, Microsoft YaHei, sans-serif',
                'heading': 'PingFang SC, Microsoft YaHei, sans-serif'
            },
            spacing={
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px'
            },
            border_radius='8px',
            shadows='0 2px 8px rgba(0,0,0,0.08)',
            is_active=True
        )
        db.session.add(default_theme)
        
        # 暖色主题
        warm_theme = ThemeConfig(
            theme_key='warm',
            theme_name='暖色主题',
            colors={
                'primary': '#C17F59',
                'secondary': '#E8C4A8',
                'accent': '#F5D6BA',
                'background': '#FDF9F3',
                'surface': '#FFFFFF',
                'text': '#3D2F2F',
                'text_secondary': '#7A6565',
                'border': '#E8DDD5'
            },
            fonts={
                'primary': 'PingFang SC, Microsoft YaHei, sans-serif',
                'heading': 'PingFang SC, Microsoft YaHei, sans-serif'
            },
            spacing={
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px'
            },
            border_radius='12px',
            shadows='0 4px 12px rgba(0,0,0,0.1)',
            is_active=False
        )
        db.session.add(warm_theme)
        
        # ========== 页面配置 ==========
        pages = [
            {
                'page_key': 'home',
                'page_name': '首页',
                'page_title': '帝标|设记家 - 成都高端全屋定制',
                'meta_description': '20年专注高端全屋定制，提供专业设计、全案落地服务。成都别墅、大平层全屋定制首选品牌。',
                'sections': [
                    {
                        'name': 'Hero轮播',
                        'component': 'HeroCarousel',
                        'config': {
                            'height': '85vh',
                            'autoplay': True,
                            'interval': 5000,
                            'slides': [
                                {
                                    'image': '/images/hero-1.jpg',
                                    'title': '全屋定制 品质生活',
                                    'subtitle': '20年品牌沉淀，专业设计团队',
                                    'cta': {'text': '立即预约', 'link': '/book'}
                                },
                                {
                                    'image': '/images/hero-2.jpg',
                                    'title': '全案落地 省心之选',
                                    'subtitle': '从设计到施工，一站式服务',
                                    'cta': {'text': '了解更多', 'link': '/cases'}
                                }
                            ]
                        }
                    },
                    {
                        'name': '品牌数据',
                        'component': 'BrandStats',
                        'config': {
                            'stats': [
                                {'value': '20', 'label': '年品牌沉淀'},
                                {'value': '5000+', 'label': '成功案例'},
                                {'value': '100+', 'label': '设计团队'},
                                {'value': '98%', 'label': '客户满意度'}
                            ]
                        }
                    },
                    {
                        'name': '服务优势',
                        'component': 'ServiceFeatures',
                        'config': {
                            'title': '为什么选择我们',
                            'features': [
                                {'icon': 'design', 'title': '专业设计', 'desc': '资深设计师1对1服务'},
                                {'icon': 'quality', 'title': '品质保障', 'desc': '精选环保材料'},
                                {'icon': 'construction', 'title': '精湛工艺', 'desc': '自有产业工人'},
                                {'icon': 'service', 'title': '全程服务', 'desc': '从设计到入住'}
                            ]
                        }
                    },
                    {
                        'name': '精选案例',
                        'component': 'FeaturedCases',
                        'config': {
                            'title': '精选案例',
                            'subtitle': '看看他们的新家',
                            'limit': 6
                        }
                    },
                    {
                        'name': '服务流程',
                        'component': 'ProcessSteps',
                        'config': {
                            'title': '服务流程',
                            'steps': [
                                {'step': '01', 'title': '预约量尺', 'desc': '免费上门测量'},
                                {'step': '02', 'title': '设计方案', 'desc': '3套方案对比'},
                                {'step': '03', 'title': '签订合同', 'desc': '透明报价无增项'},
                                {'step': '04', 'title': '生产交付', 'desc': '工厂直配到户'},
                                {'step': '05', 'title': '安装验收', 'desc': '专业团队施工'}
                            ]
                        }
                    },
                    {
                        'name': '关于我们',
                        'component': 'AboutSection',
                        'config': {
                            'title': '关于帝标|设记家',
                            'content': '创立于2003年，20年专注高端全屋定制。集设计、研发、生产、销售于一体，为追求品质生活的家庭提供专业的全屋定制解决方案。',
                            'highlights': [
                                '成都国际家具设计奖金奖',
                                '金物奖最佳设计奖',
                                '四川省级企业技术中心',
                                '省级工业设计中心'
                            ]
                        }
                    },
                    {
                        'name': 'CTA行动号召',
                        'component': 'CallToAction',
                        'config': {
                            'title': '预约免费量尺',
                            'subtitle': '专业设计师上门服务',
                            'button_text': '立即预约',
                            'button_link': '/book'
                        }
                    },
                    {
                        'name': '联系表单',
                        'component': 'ContactForm',
                        'config': {
                            'title': '联系我们',
                            'subtitle': '获取专属设计方案',
                            'fields': ['name', 'phone', 'city', 'house_type', 'budget']
                        }
                    }
                ],
                'is_enabled': True
            },
            {
                'page_key': 'about',
                'page_name': '关于我们',
                'page_title': '关于我们 - 帝标|设记家',
                'meta_description': '帝标|设记家，2003年创立，20年专注高端全屋定制。成都高端家具定制品牌。',
                'sections': [
                    {
                        'name': '品牌故事',
                        'component': 'BrandStory',
                        'config': {
                            'title': '品牌故事',
                            'content': '帝标|设记家创立于2003年，源自对美好家居生活的追求。20年来，我们始终坚持以用户需求为中心，以设计创新为驱动，以品质服务为根本，为万千家庭打造理想居所。'
                        }
                    },
                    {
                        'name': '品牌荣誉',
                        'component': 'Awards',
                        'config': {
                            'title': '品牌荣誉',
                            'awards': [
                                {'name': '成都国际家具设计奖', 'org': 'iF设计奖', 'year': '2024'},
                                {'name': '金物奖最佳设计奖', 'org': '金物奖组委会', 'year': '2023'},
                                {'name': '四川省级企业技术中心', 'org': '四川省经信厅', 'year': '2022'},
                                {'name': '省级工业设计中心', 'org': '四川省经信厅', 'year': '2021'}
                            ]
                        }
                    },
                    {
                        'name': '品牌文化',
                        'component': 'Culture',
                        'config': {
                            'title': '品牌文化',
                            'values': [
                                {'title': '设计为本', 'desc': '以设计创新引领行业发展'},
                                {'title': '品质至上', 'desc': '精选材料，精湛工艺'},
                                {'title': '服务第一', 'desc': '全程无忧，省心交付'}
                            ]
                        }
                    }
                ],
                'is_enabled': True
            },
            {
                'page_key': 'contact',
                'page_name': '联系我们',
                'page_title': '联系我们 - 帝标|设记家',
                'meta_description': '帝标|设记家门店信息及联系方式。预约量尺请致电：400-6118-315',
                'sections': [
                    {
                        'name': '联系方式',
                        'component': 'ContactInfo',
                        'config': {
                            'title': '联系我们',
                            'phones': [
                                {'label': '总部热线', 'number': '400-6118-315'},
                                {'label': '设记家先锋店', 'number': '13881828767（贺女士）'},
                                {'label': '设记家先锋店', 'number': '13219762086（曾女士）'}
                            ],
                            'addresses': [
                                {
                                    'name': '帝标总部',
                                    'address': '四川省成都市新都区列维士路258号'
                                },
                                {
                                    'name': '设记家先锋店',
                                    'address': '四川省成都市青羊区蔡桥街道天府匠芯北区A座6-10'
                                }
                            ],
                            'hours': '周一至周日 9:00-20:00'
                        }
                    },
                    {
                        'name': '联系表单',
                        'component': 'ContactForm',
                        'config': {
                            'title': '在线预约',
                            'subtitle': '留下您的信息，我们会尽快联系您',
                            'fields': ['name', 'phone', 'city', 'house_type', 'budget']
                        }
                    }
                ],
                'is_enabled': True
            },
            {
                'page_key': 'cases',
                'page_name': '案例中心',
                'page_title': '案例中心 - 帝标|设记家',
                'meta_description': '精选全屋定制案例，现代简约、中式、美式等多种风格可选。',
                'sections': [
                    {
                        'name': '案例筛选',
                        'component': 'CaseFilter',
                        'config': {
                            'filters': ['style', 'space', 'budget'],
                            'sort_options': ['最新', '最热', '价格']
                        }
                    }
                ],
                'is_enabled': True
            },
            {
                'page_key': 'products',
                'page_name': '产品中心',
                'page_title': '产品中心 - 帝标|设记家',
                'meta_description': '全屋定制产品展示，橱柜、衣柜、书柜、木门等全屋定制产品。',
                'sections': [
                    {
                        'name': '产品分类',
                        'component': 'CategoryNav',
                        'config': {
                            'categories': ['橱柜', '衣柜', '书柜', '木门', '护墙板', '楼梯']
                        }
                    }
                ],
                'is_enabled': True
            },
            {
                'page_key': 'book',
                'page_name': '预约量尺',
                'page_title': '预约量尺 - 帝标|设记家',
                'meta_description': '免费预约上门量尺，专业设计师为您服务。',
                'sections': [
                    {
                        'name': '预约表单',
                        'component': 'BookingForm',
                        'config': {
                            'title': '免费预约量尺',
                            'subtitle': '专业设计师上门服务，量身定制专属方案',
                            'fields': ['name', 'phone', 'city', 'district', 'address', 'house_type', 'budget', 'preferred_date', 'remark']
                        }
                    },
                    {
                        'name': '预约须知',
                        'component': 'BookingNotes',
                        'config': {
                            'notes': [
                                '预约成功后，客服将在24小时内与您联系确认',
                                '量尺服务完全免费，不收取任何费用',
                                '设计团队将根据您的需求提供多套方案供参考',
                                '您可以随时取消或更改预约时间'
                            ]
                        }
                    }
                ],
                'is_enabled': True
            }
        ]
        
        for page_data in pages:
            page = PageConfig(**page_data)
            db.session.add(page)
        
        # ========== 导航配置 ==========
        header_nav = NavigationConfig(
            nav_position='header',
            nav_items=[
                {'label': '首页', 'link': '/', 'type': 'link'},
                {'label': '案例', 'link': '/cases', 'type': 'link'},
                {'label': '产品', 'link': '/products', 'type': 'link'},
                {'label': '预约量尺', 'link': '/book', 'type': 'link'},
                {'label': '关于我们', 'link': '/about', 'type': 'link'}
            ],
            style_config={
                'logo': '/images/logo.png',
                'brand_name': '帝标|设记家',
                'cta_text': '预约量尺',
                'cta_link': '/book'
            }
        )
        db.session.add(header_nav)
        
        footer_nav = NavigationConfig(
            nav_position='footer',
            nav_items=[
                {
                    'title': '关于设记家',
                    'links': [
                        {'label': '关于我们', 'link': '/about'},
                        {'label': '品牌荣誉', 'link': '/about#awards'},
                        {'label': '设计团队', 'link': '/about#team'}
                    ]
                },
                {
                    'title': '服务项目',
                    'links': [
                        {'label': '全屋定制', 'link': '/products'},
                        {'label': '案例展示', 'link': '/cases'},
                        {'label': '预约量尺', 'link': '/book'}
                    ]
                },
                {
                    'title': '联系我们',
                    'links': [
                        {'label': '400-6118-315', 'link': 'tel:4006118315'},
                        {'label': '门店地址', 'link': '/contact'}
                    ]
                }
            ],
            style_config={
                'copyright': '© 2024 帝标|设记家 版权所有',
                'icp': '蜀ICP备15030401号-3',
                'address': '四川省成都市青羊区蔡桥街道天府匠芯北区A座6-10'
            }
        )
        db.session.add(footer_nav)
        
        # ========== 组件库配置 ==========
        components = [
            {
                'component_key': 'HeroCarousel',
                'component_name': 'Hero轮播组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'height': {'type': 'string'},
                        'autoplay': {'type': 'boolean'},
                        'interval': {'type': 'number'},
                        'slides': {'type': 'array'}
                    }
                },
                'default_config': {
                    'height': '85vh',
                    'autoplay': True,
                    'interval': 5000
                }
            },
            {
                'component_key': 'BrandStats',
                'component_name': '品牌数据组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'stats': {'type': 'array'}
                    }
                }
            },
            {
                'component_key': 'ServiceFeatures',
                'component_name': '服务优势组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'features': {'type': 'array'}
                    }
                }
            },
            {
                'component_key': 'FeaturedCases',
                'component_name': '精选案例组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'limit': {'type': 'number'}
                    }
                }
            },
            {
                'component_key': 'ProcessSteps',
                'component_name': '服务流程组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'steps': {'type': 'array'}
                    }
                }
            },
            {
                'component_key': 'AboutSection',
                'component_name': '关于我们组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'content': {'type': 'string'}
                    }
                }
            },
            {
                'component_key': 'CallToAction',
                'component_name': '行动号召组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'subtitle': {'type': 'string'},
                        'button_text': {'type': 'string'},
                        'button_link': {'type': 'string'}
                    }
                }
            },
            {
                'component_key': 'ContactForm',
                'component_name': '联系表单组件',
                'config_schema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'fields': {'type': 'array'}
                    }
                }
            }
        ]
        
        for comp_data in components:
            comp_data['component_type'] = comp_data.get('component_type', 'general')
            comp = ComponentConfig(**comp_data)
            db.session.add(comp)
        
        db.session.commit()
        print('前端配置数据初始化完成！')
        print(f'- 主题配置: {ThemeConfig.query.count()} 个')
        print(f'- 页面配置: {PageConfig.query.count()} 个')
        print(f'- 导航配置: {NavigationConfig.query.count()} 个')
        print(f'- 组件库: {ComponentConfig.query.count()} 个')


if __name__ == '__main__':
    init_frontend_config()
