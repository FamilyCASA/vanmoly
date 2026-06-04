"""
初始化前端配置数据
创建默认页面配置、主题和导航菜单
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.frontend_config import (
    PageConfig, ComponentConfig, ResourceConfig,
    NavigationConfig, ThemeConfig, FrontendVersion
)
from datetime import datetime


def init_themes():
    """初始化主题配置"""
    theme_data = {
        'theme_name': 'D&B 帝标|设记家品牌主题',
        'theme_key': 'designary_default',
        'colors': {
            'primary': '#8B5A2B',
            'primary_light': '#D4A574',
            'accent': '#2C5F2D',
            'text_primary': '#333333',
            'text_secondary': '#666666',
            'text_muted': '#999999',
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F5F5',
            'border': '#E5E5E5',
            'success': '#67C23A',
            'warning': '#E6A23C',
            'danger': '#F56C6C',
            'info': '#909399'
        },
        'fonts': {
            'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'size_base': '14px',
            'size_sm': '12px',
            'size_lg': '16px',
            'size_xl': '18px',
            'size_title': '20px'
        },
        'spacing': {
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
            'lg': '24px',
            'xl': '32px'
        },
        'border_radius': {
            'sm': '4px',
            'md': '8px',
            'lg': '12px',
            'round': '50%'
        },
        'shadows': {
            'sm': '0 2px 4px rgba(0,0,0,0.1)',
            'md': '0 4px 8px rgba(0,0,0,0.12)',
            'lg': '0 8px 16px rgba(0,0,0,0.15)'
        },
        'is_active': True,
        'is_default': True
    }

    existing = ThemeConfig.query.filter_by(theme_key='designary_default').first()
    if not existing:
        theme = ThemeConfig(**theme_data)
        db.session.add(theme)
        db.session.commit()
        print(f"创建主题: {theme_data['theme_name']}")
    else:
        print("主题已存在，跳过创建")

    print("主题配置初始化完成")


def init_pages():
    """初始化页面配置"""
    pages = [
        {
            'page_key': 'home',
            'page_name': '首页',
            'page_title': 'D&B 帝标|设记家 - 全案定制家居',
            'meta_description': 'D&B 帝标|设记家提供一站式全屋定制服务，包括设计、施工、软装等全案解决方案。',
            'meta_keywords': '全屋定制,家装设计,软装搭配,D&B 帝标|设记家',
            'sections': [
                {
                    'type': 'banner',
                    'name': '轮播图',
                    'config': {
                        'height': '400rpx',
                        'indicator_type': 'dot',
                        'autoplay': True,
                        'interval': 5000,
                        'items': [
                            {
                                'image': '/images/banner/banner1.jpg',
                                'title': '一站式全案定制',
                                'subtitle': '设计·施工·软装·售后 全程无忧',
                                'link': '/pages/lead/index'
                            },
                            {
                                'image': '/images/banner/banner2.jpg',
                                'title': '专业设计师团队',
                                'subtitle': '10年以上经验 1对1专属服务',
                                'link': '/pages/cases/index'
                            },
                            {
                                'image': '/images/banner/banner3.jpg',
                                'title': '品质施工保障',
                                'subtitle': '德系工艺 终身质保',
                                'link': '/pages/appointment/index'
                            }
                        ]
                    }
                },
                {
                    'type': 'quick_nav',
                    'name': '快捷入口',
                    'config': {
                        'columns': 4,
                        'items': [
                            {'icon': 'edit', 'title': '免费设计', 'color': '#8B5A2B', 'link': '/pages/lead/index'},
                            {'icon': 'calendar', 'title': '预约量尺', 'color': '#2C5F2D', 'link': '/pages/appointment/index'},
                            {'icon': 'picture', 'title': '案例展示', 'color': '#D4A574', 'link': '/pages/cases/index'},
                            {'icon': 'ticket', 'title': '优惠券', 'color': '#E6A23C', 'link': '/pages/coupons/index'}
                        ]
                    }
                },
                {
                    'type': 'section_title',
                    'name': '精选案例标题',
                    'config': {
                        'title': '精选案例',
                        'subtitle': '真实家装案例，见证品质服务',
                        'more_link': '/pages/cases/index',
                        'show_more': True
                    }
                },
                {
                    'type': 'case_list',
                    'name': '精选案例列表',
                    'config': {
                        'layout': 'grid',
                        'columns': 2,
                        'limit': 4,
                        'show_load_more': True
                    }
                },
                {
                    'type': 'section_title',
                    'name': '服务流程标题',
                    'config': {
                        'title': '服务流程',
                        'subtitle': '标准化服务流程，让您省心省力',
                        'show_more': False
                    }
                },
                {
                    'type': 'service_steps',
                    'name': '服务流程步骤',
                    'config': {
                        'steps': [
                            {'icon': 'chat', 'title': '在线咨询', 'desc': '了解需求'},
                            {'icon': 'home', 'title': '上门量尺', 'desc': '精准测量'},
                            {'icon': 'edit', 'title': '方案设计', 'desc': '专属定制'},
                            {'icon': 'tools', 'title': '签约施工', 'desc': '品质保障'},
                            {'icon': 'sofa', 'title': '软装搭配', 'desc': '拎包入住'}
                        ]
                    }
                },
                {
                    'type': 'section_title',
                    'name': '品牌数据标题',
                    'config': {
                        'title': 'D&B 帝标|设记家实力',
                        'subtitle': '用数据说话，值得信赖',
                        'show_more': False
                    }
                },
                {
                    'type': 'stats_grid',
                    'name': '品牌数据统计',
                    'config': {
                        'items': [
                            {'value': '10+', 'label': '年行业经验', 'suffix': '年'},
                            {'value': '5000+', 'label': '服务家庭', 'suffix': '户'},
                            {'value': '100+', 'label': '专业设计师', 'suffix': '人'},
                            {'value': '98%', 'label': '客户满意度', 'suffix': ''}
                        ]
                    }
                },
                {
                    'type': 'contact_bar',
                    'name': '底部联系栏',
                    'config': {
                        'phone': '400-888-8888',
                        'work_hours': '周一至周日 9:00-21:00',
                        'buttons': [
                            {'type': 'phone', 'text': '电话咨询', 'icon': 'phone'},
                            {'type': 'form', 'text': '免费设计', 'icon': 'edit', 'link': '/pages/lead/index'}
                        ]
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'cases',
            'page_name': '案例展示',
            'page_title': '装修案例 - D&B 帝标|设记家',
            'meta_description': '浏览D&B 帝标|设记家精选家装案例，获取装修灵感。',
            'meta_keywords': '装修案例,家装效果图,设计案例',
            'sections': [
                {
                    'type': 'filter_bar',
                    'name': '筛选栏',
                    'config': {
                        'filters': [
                            {'key': 'style', 'title': '风格', 'options': ['现代简约', '北欧', '中式', '轻奢', '美式']},
                            {'key': 'area', 'title': '面积', 'options': ['80㎡以下', '80-120㎡', '120-150㎡', '150㎡以上']},
                            {'key': 'type', 'title': '户型', 'options': ['一居', '两居', '三居', '四居及以上']}
                        ]
                    }
                },
                {
                    'type': 'case_list',
                    'name': '案例列表',
                    'config': {
                        'layout': 'grid',
                        'columns': 2,
                        'limit': 10,
                        'show_load_more': True
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'case_detail',
            'page_name': '案例详情',
            'page_title': '案例详情 - D&B 帝标|设记家',
            'meta_description': '查看案例详细信息',
            'meta_keywords': '',
            'sections': [
                {
                    'type': 'case_gallery',
                    'name': '案例图集',
                    'config': {}
                },
                {
                    'type': 'case_info',
                    'name': '案例信息',
                    'config': {}
                },
                {
                    'type': 'designer_card',
                    'name': '设计师卡片',
                    'config': {}
                },
                {
                    'type': 'related_cases',
                    'name': '相关案例',
                    'config': {'limit': 4}
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'lead',
            'page_name': '免费设计',
            'page_title': '免费获取设计方案 - D&B 帝标|设记家',
            'meta_description': '填写表单，免费获取专业设计师的装修方案。',
            'meta_keywords': '免费设计,装修咨询,设计方案',
            'sections': [
                {
                    'type': 'form_header',
                    'name': '表单头部',
                    'config': {
                        'title': '免费获取设计方案',
                        'subtitle': '专业设计师1对1服务，0元定制您的家',
                        'benefits': ['免费上门量房', '3套设计方案', '详细报价清单']
                    }
                },
                {
                    'type': 'lead_form',
                    'name': '留资表单',
                    'config': {
                        'fields': [
                            {'key': 'name', 'label': '您的姓名', 'type': 'text', 'required': True},
                            {'key': 'phone', 'label': '联系电话', 'type': 'phone', 'required': True},
                            {'key': 'building_name', 'label': '楼盘名称', 'type': 'text', 'required': False},
                            {'key': 'house_area', 'label': '房屋面积', 'type': 'number', 'required': False, 'suffix': '㎡'},
                            {'key': 'budget', 'label': '装修预算', 'type': 'select', 'options': ['10万以下', '10-20万', '20-30万', '30-50万', '50万以上']},
                            {'key': 'requirements', 'label': '装修需求', 'type': 'textarea', 'placeholder': '请描述您的装修需求...'}
                        ]
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'appointment',
            'page_name': '预约量尺',
            'page_title': '预约上门量尺 - D&B 帝标|设记家',
            'meta_description': '预约专业设计师上门量房，获取精准报价。',
            'meta_keywords': '预约量房,上门量尺,装修报价',
            'sections': [
                {
                    'type': 'form_header',
                    'name': '表单头部',
                    'config': {
                        'title': '预约上门量尺',
                        'subtitle': '免费上门量房，专业设计师一对一服务',
                        'steps': ['提交预约', '客服确认', '上门量尺', '方案设计']
                    }
                },
                {
                    'type': 'appointment_form',
                    'name': '预约表单',
                    'config': {
                        'fields': [
                            {'key': 'name', 'label': '您的姓名', 'type': 'text', 'required': True},
                            {'key': 'phone', 'label': '联系电话', 'type': 'phone', 'required': True},
                            {'key': 'address', 'label': '房屋地址', 'type': 'text', 'required': True},
                            {'key': 'appointment_date', 'label': '预约日期', 'type': 'date', 'required': True},
                            {'key': 'appointment_time', 'label': '预约时段', 'type': 'select', 'options': ['上午 9:00-12:00', '下午 14:00-18:00', '晚上 18:00-21:00']},
                            {'key': 'remark', 'label': '备注', 'type': 'textarea', 'placeholder': '其他需求或问题...'}
                        ]
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'coupons',
            'page_name': '优惠活动',
            'page_title': '优惠活动 - D&B 帝标|设记家',
            'meta_description': '查看最新优惠活动，领取装修优惠券。',
            'meta_keywords': '装修优惠,优惠券,活动',
            'sections': [
                {
                    'type': 'coupon_list',
                    'name': '优惠券列表',
                    'config': {
                        'show_claimed': True
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'articles',
            'page_name': '装修攻略',
            'page_title': '装修攻略 - D&B 帝标|设记家',
            'meta_description': '获取专业装修知识和避坑指南。',
            'meta_keywords': '装修知识,装修攻略,避坑指南',
            'sections': [
                {
                    'type': 'category_tabs',
                    'name': '分类标签',
                    'config': {
                        'categories': ['全部', '装修知识', '风格搭配', '选材指南', '避坑攻略']
                    }
                },
                {
                    'type': 'article_list',
                    'name': '文章列表',
                    'config': {
                        'layout': 'list',
                        'show_cover': True
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        },
        {
            'page_key': 'profile',
            'page_name': '我的',
            'page_title': '个人中心 - D&B 帝标|设记家',
            'meta_description': '查看我的预约、优惠券和装修进度。',
            'meta_keywords': '',
            'sections': [
                {
                    'type': 'user_card',
                    'name': '用户信息卡片',
                    'config': {}
                },
                {
                    'type': 'menu_grid',
                    'name': '功能菜单',
                    'config': {
                        'items': [
                            {'icon': 'calendar', 'title': '我的预约', 'link': '/pages/profile/appointments'},
                            {'icon': 'ticket', 'title': '我的优惠券', 'link': '/pages/profile/coupons'},
                            {'icon': 'home', 'title': '我的家', 'link': '/pages/profile/project'},
                            {'icon': 'file-text', 'title': '合同协议', 'link': '/pages/profile/contracts'},
                            {'icon': 'customer-service', 'title': '客服中心', 'link': '/pages/profile/service'},
                            {'icon': 'setting', 'title': '设置', 'link': '/pages/profile/settings'}
                        ]
                    }
                }
            ],
            'is_enabled': True,
            'is_default': True
        }
    ]

    for page_data in pages:
        existing = PageConfig.query.filter_by(page_key=page_data['page_key']).first()
        if not existing:
            page = PageConfig(**page_data)
            db.session.add(page)
            print(f"创建页面: {page_data['page_name']}")

    db.session.commit()
    print("页面配置初始化完成")


def init_navigation():
    """初始化导航配置"""
    nav_configs = [
        {
            'nav_position': 'header',
            'nav_items': [
                {'title': '首页', 'icon': 'home', 'link': '/', 'sort': 1},
                {'title': '案例', 'icon': 'picture', 'link': '/cases', 'sort': 2},
                {'title': '免费设计', 'icon': 'edit', 'link': '/leads', 'sort': 3},
                {'title': '预约量尺', 'icon': 'calendar', 'link': '/book', 'sort': 4}
            ],
            'style_config': {
                'position': 'fixed',
                'background': '#FFFFFF',
                'text_color': '#333333',
                'active_color': '#8B5A2B'
            },
            'is_enabled': True,
            'is_default': True
        },
        {
            'nav_position': 'footer',
            'nav_items': [
                {'title': '首页', 'icon': 'home', 'link': '/pages/index/index', 'sort': 1},
                {'title': '案例', 'icon': 'picture', 'link': '/pages/cases/index', 'sort': 2},
                {'title': '优惠', 'icon': 'ticket', 'link': '/pages/coupons/index', 'sort': 3},
                {'title': '我的', 'icon': 'user', 'link': '/pages/profile/index', 'sort': 4}
            ],
            'style_config': {
                'position': 'fixed',
                'background': '#FFFFFF',
                'border_top': True,
                'text_color': '#999999',
                'active_color': '#8B5A2B'
            },
            'is_enabled': True,
            'is_default': True
        },
        {
            'nav_position': 'mobile',
            'nav_items': [
                {'title': '首页', 'icon': 'home', 'link': '/pages/index/index', 'sort': 1},
                {'title': '案例', 'icon': 'picture', 'link': '/pages/cases/index', 'sort': 2},
                {'title': '免费设计', 'icon': 'edit', 'link': '/pages/lead/index', 'sort': 3, 'is_center': True},
                {'title': '优惠', 'icon': 'ticket', 'link': '/pages/coupons/index', 'sort': 4},
                {'title': '我的', 'icon': 'user', 'link': '/pages/profile/index', 'sort': 5}
            ],
            'style_config': {
                'position': 'fixed',
                'background': '#FFFFFF',
                'border_top': True,
                'center_button': True,
                'center_button_color': '#8B5A2B',
                'text_color': '#999999',
                'active_color': '#8B5A2B'
            },
            'is_enabled': True,
            'is_default': True
        }
    ]

    for nav_data in nav_configs:
        existing = NavigationConfig.query.filter_by(
            nav_position=nav_data['nav_position'],
            is_default=True
        ).first()
        if not existing:
            nav = NavigationConfig(**nav_data)
            db.session.add(nav)
            print(f"创建导航: {nav_data['nav_position']}")

    db.session.commit()
    print("导航配置初始化完成")


def init_components():
    """初始化组件配置库"""
    components = [
        {
            'component_key': 'banner',
            'component_name': '轮播图',
            'component_type': 'media',
            'config_schema': {
                'height': {'type': 'string', 'default': '400rpx', 'label': '高度'},
                'indicator_type': {'type': 'select', 'options': ['dot', 'number', 'none'], 'default': 'dot', 'label': '指示器类型'},
                'autoplay': {'type': 'boolean', 'default': True, 'label': '自动播放'},
                'interval': {'type': 'number', 'default': 5000, 'label': '切换间隔(ms)'},
                'items': {'type': 'array', 'label': '轮播项列表', 'item_schema': {
                    'image': {'type': 'image', 'label': '图片'},
                    'title': {'type': 'string', 'label': '标题'},
                    'subtitle': {'type': 'string', 'label': '副标题'},
                    'link': {'type': 'string', 'label': '链接'}
                }}
            },
            'default_config': {
                'height': '400rpx',
                'indicator_type': 'dot',
                'autoplay': True,
                'interval': 5000,
                'items': []
            },
            'category': 'media',
            'is_enabled': True
        },
        {
            'component_key': 'quick_nav',
            'component_name': '快捷入口',
            'component_type': 'nav',
            'config_schema': {
                'columns': {'type': 'number', 'default': 4, 'label': '列数'},
                'items': {'type': 'array', 'label': '入口项', 'item_schema': {
                    'icon': {'type': 'icon', 'label': '图标'},
                    'title': {'type': 'string', 'label': '标题'},
                    'color': {'type': 'color', 'label': '颜色'},
                    'link': {'type': 'string', 'label': '链接'}
                }}
            },
            'default_config': {
                'columns': 4,
                'items': []
            },
            'category': 'nav',
            'is_enabled': True
        },
        {
            'component_key': 'section_title',
            'component_name': '区块标题',
            'component_type': 'content',
            'config_schema': {
                'title': {'type': 'string', 'label': '标题'},
                'subtitle': {'type': 'string', 'label': '副标题'},
                'show_more': {'type': 'boolean', 'default': False, 'label': '显示更多'},
                'more_link': {'type': 'string', 'label': '更多链接'}
            },
            'default_config': {
                'title': '',
                'subtitle': '',
                'show_more': False
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'case_list',
            'component_name': '案例列表',
            'component_type': 'content',
            'config_schema': {
                'layout': {'type': 'select', 'options': ['grid', 'list'], 'default': 'grid', 'label': '布局'},
                'columns': {'type': 'number', 'default': 2, 'label': '列数'},
                'limit': {'type': 'number', 'default': 10, 'label': '显示数量'},
                'show_load_more': {'type': 'boolean', 'default': True, 'label': '显示加载更多'}
            },
            'default_config': {
                'layout': 'grid',
                'columns': 2,
                'limit': 10,
                'show_load_more': True
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'service_steps',
            'component_name': '服务流程',
            'component_type': 'content',
            'config_schema': {
                'steps': {'type': 'array', 'label': '流程步骤', 'item_schema': {
                    'icon': {'type': 'icon', 'label': '图标'},
                    'title': {'type': 'string', 'label': '标题'},
                    'desc': {'type': 'string', 'label': '描述'}
                }}
            },
            'default_config': {
                'steps': []
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'stats_grid',
            'component_name': '数据统计',
            'component_type': 'content',
            'config_schema': {
                'items': {'type': 'array', 'label': '统计项', 'item_schema': {
                    'value': {'type': 'string', 'label': '数值'},
                    'label': {'type': 'string', 'label': '标签'},
                    'suffix': {'type': 'string', 'label': '后缀'}
                }}
            },
            'default_config': {
                'items': []
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'contact_bar',
            'component_name': '联系栏',
            'component_type': 'content',
            'config_schema': {
                'phone': {'type': 'string', 'label': '电话号码'},
                'work_hours': {'type': 'string', 'label': '工作时间'},
                'buttons': {'type': 'array', 'label': '按钮', 'item_schema': {
                    'type': {'type': 'select', 'options': ['phone', 'form', 'link'], 'label': '类型'},
                    'text': {'type': 'string', 'label': '文字'},
                    'icon': {'type': 'icon', 'label': '图标'},
                    'link': {'type': 'string', 'label': '链接'}
                }}
            },
            'default_config': {
                'phone': '',
                'work_hours': '',
                'buttons': []
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'lead_form',
            'component_name': '留资表单',
            'component_type': 'form',
            'config_schema': {
                'fields': {'type': 'array', 'label': '表单字段', 'item_schema': {
                    'key': {'type': 'string', 'label': '字段名'},
                    'label': {'type': 'string', 'label': '标签'},
                    'type': {'type': 'select', 'options': ['text', 'phone', 'number', 'select', 'textarea', 'date'], 'label': '类型'},
                    'required': {'type': 'boolean', 'label': '必填'},
                    'options': {'type': 'array', 'label': '选项（select类型）'},
                    'placeholder': {'type': 'string', 'label': '占位符'},
                    'suffix': {'type': 'string', 'label': '后缀'}
                }}
            },
            'default_config': {
                'fields': []
            },
            'category': 'form',
            'is_enabled': True
        },
        {
            'component_key': 'coupon_list',
            'component_name': '优惠券列表',
            'component_type': 'content',
            'config_schema': {
                'show_claimed': {'type': 'boolean', 'default': True, 'label': '显示已领取'}
            },
            'default_config': {
                'show_claimed': True
            },
            'category': 'content',
            'is_enabled': True
        },
        {
            'component_key': 'article_list',
            'component_name': '文章列表',
            'component_type': 'content',
            'config_schema': {
                'layout': {'type': 'select', 'options': ['list', 'card'], 'default': 'list', 'label': '布局'},
                'show_cover': {'type': 'boolean', 'default': True, 'label': '显示封面'}
            },
            'default_config': {
                'layout': 'list',
                'show_cover': True
            },
            'category': 'content',
            'is_enabled': True
        }
    ]

    for comp_data in components:
        existing = ComponentConfig.query.filter_by(
            component_key=comp_data['component_key']
        ).first()
        if not existing:
            comp = ComponentConfig(**comp_data)
            db.session.add(comp)
            print(f"创建组件: {comp_data['component_name']}")

    db.session.commit()
    print("组件配置初始化完成")


def init_resources():
    """初始化资源配置"""
    resources = [
        {
            'resource_key': 'logo',
            'resource_name': '品牌Logo',
            'resource_type': 'image',
            'file_url': '/images/logo.png',
            'usage_scenes': ['header', 'share'],
            'is_enabled': True
        },
        {
            'resource_key': 'logo_white',
            'resource_name': '白色Logo',
            'resource_type': 'image',
            'file_url': '/images/logo-white.png',
            'usage_scenes': ['footer', 'dark_bg'],
            'is_enabled': True
        },
        {
            'resource_key': 'default_avatar',
            'resource_name': '默认头像',
            'resource_type': 'image',
            'file_url': '/images/avatar-default.png',
            'usage_scenes': ['user', 'profile'],
            'is_enabled': True
        },
        {
            'resource_key': 'default_case',
            'resource_name': '默认案例图',
            'resource_type': 'image',
            'file_url': '/images/case-default.jpg',
            'usage_scenes': ['case', 'list'],
            'is_enabled': True
        },
        {
            'resource_key': 'banner_1',
            'resource_name': '首页轮播图1',
            'resource_type': 'image',
            'file_url': '/images/banner/banner1.jpg',
            'usage_scenes': ['banner', 'home'],
            'is_enabled': True
        },
        {
            'resource_key': 'banner_2',
            'resource_name': '首页轮播图2',
            'resource_type': 'image',
            'file_url': '/images/banner/banner2.jpg',
            'usage_scenes': ['banner', 'home'],
            'is_enabled': True
        },
        {
            'resource_key': 'banner_3',
            'resource_name': '首页轮播图3',
            'resource_type': 'image',
            'file_url': '/images/banner/banner3.jpg',
            'usage_scenes': ['banner', 'home'],
            'is_enabled': True
        }
    ]

    for res_data in resources:
        existing = ResourceConfig.query.filter_by(
            resource_key=res_data['resource_key']
        ).first()
        if not existing:
            res = ResourceConfig(**res_data)
            db.session.add(res)
            print(f"创建资源: {res_data['resource_name']}")

    db.session.commit()
    print("资源配置初始化完成")


def init_version():
    """初始化版本信息"""
    version = FrontendVersion.query.filter_by(status='published').first()
    if not version:
        version = FrontendVersion(
            version='1.0.0',
            version_name='初始版本',
            changes='系统初始化，创建默认配置',
            change_list=['创建品牌主题', '初始化页面配置', '设置导航菜单', '配置组件库'],
            status='published',
            published_at=datetime.utcnow()
        )
        db.session.add(version)
        db.session.commit()
        print("版本信息初始化完成")
    else:
        print("版本信息已存在")


def main():
    """主函数"""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("开始初始化前端配置数据")
        print("=" * 60)

        init_themes()
        init_pages()
        init_navigation()
        init_components()
        init_resources()
        init_version()

        print("=" * 60)
        print("前端配置初始化完成！")
        print("=" * 60)
        print("\n已创建配置：")
        print(f"- 主题: {ThemeConfig.query.count()} 个")
        print(f"- 页面: {PageConfig.query.count()} 个")
        print(f"- 导航: {NavigationConfig.query.count()} 个")
        print(f"- 组件: {ComponentConfig.query.count()} 个")
        print(f"- 资源: {ResourceConfig.query.count()} 个")
        print(f"- 版本: {FrontendVersion.query.count()} 个")


if __name__ == '__main__':
    main()
