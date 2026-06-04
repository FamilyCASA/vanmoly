"""
楼盘调查表 - 数据模型
V3.2 新增模块
"""
from datetime import datetime
from app import db


class BuildingSurvey(db.Model):
    """楼盘调查表"""
    __tablename__ = 'building_survey'
    __bind_key__ = None  # 使用主库

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'),
                            nullable=False, unique=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 项目概况
    delivery_date = db.Column(db.Date, comment='交付时间 YYYY-MM-DD')
    delivery_count = db.Column(db.Integer, comment='交付数量（套）')
    base_task = db.Column(db.String(50), comment='保底任务（金额或说明）')
    property_category = db.Column(db.String(20), comment='项目类别：residential/commercial/mixed/villa')

    # 户型分析
    unit_area = db.Column(db.String(30), comment='户型面积，如"95.5平米"')
    unit_count = db.Column(db.Integer, comment='户型数量')
    main_unit_type = db.Column(db.String(50), comment='主力户型，如"三室两厅"')

    # 购房人群占比（存储整数，%可省略）
    age_0_18 = db.Column(db.Integer, comment='0-18岁占比')
    age_19_30 = db.Column(db.Integer, comment='19-30岁占比')
    age_31_45 = db.Column(db.Integer, comment='31-45岁占比')
    age_46_60 = db.Column(db.Integer, comment='46-60岁占比')
    age_60_plus = db.Column(db.Integer, comment='60岁以上占比')

    # 配套设施
    matching_shops = db.Column(db.Text, comment='匹配商家，多个逗号分隔')
    metro_info = db.Column(db.String(50), comment='地铁配套，如"有（300米）"或"无"')
    park_info = db.Column(db.String(50), comment='公园配套，如"有"或"无"')

    # 录入信息
    entry_date = db.Column(db.Date, comment='录入日期')
    entry_by = db.Column(db.String(50), comment='录入人')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    PROPERTY_CATEGORIES = ['residential', 'commercial', 'mixed', 'villa']

    def to_dict(self):
        return {
            'id': self.id,
            'building_id': self.building_id,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_count': self.delivery_count,
            'base_task': self.base_task,
            'property_category': self.property_category,
            'unit_area': self.unit_area,
            'unit_count': self.unit_count,
            'main_unit_type': self.main_unit_type,
            'age_0_18': self.age_0_18,
            'age_19_30': self.age_19_30,
            'age_31_45': self.age_31_45,
            'age_46_60': self.age_46_60,
            'age_60_plus': self.age_60_plus,
            'matching_shops': self.matching_shops,
            'metro_info': self.metro_info,
            'park_info': self.park_info,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'entry_by': self.entry_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_age_groups(self):
        return [
            {'label': '0-18岁', 'value': self.age_0_18, 'key': 'age_0_18'},
            {'label': '19-30岁', 'value': self.age_19_30, 'key': 'age_19_30'},
            {'label': '31-45岁', 'value': self.age_31_45, 'key': 'age_31_45'},
            {'label': '46-60岁', 'value': self.age_46_60, 'key': 'age_46_60'},
            {'label': '60岁以上', 'value': self.age_60_plus, 'key': 'age_60_plus'},
        ]