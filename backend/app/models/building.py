"""
楼盘管理模块 - 数据模型
V3.0 全新设计
"""
from datetime import datetime
from app import db


class Building(db.Model):
    """楼盘/小区表"""
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='楼盘名称')
    alias = db.Column(db.String(100), comment='别名')

    # 位置信息
    province = db.Column(db.String(50), comment='省')
    city = db.Column(db.String(50), comment='市')
    district = db.Column(db.String(50), comment='区/县')
    address = db.Column(db.String(255), comment='详细地址')

    # 坐标
    longitude = db.Column(db.Numeric(10, 7), comment='经度')
    latitude = db.Column(db.Numeric(10, 7), comment='纬度')

    # 楼盘信息
    developer = db.Column(db.String(100), comment='开发商')
    property_company = db.Column(db.String(100), comment='物业公司')
    build_year = db.Column(db.Integer, comment='建成年份')
    total_houses = db.Column(db.Integer, comment='总户数')
    property_type = db.Column(db.String(50), comment='物业类型')
    # 住宅/别墅/公寓/商业

    # 合作信息
    cooperation_status = db.Column(db.String(20), default='none', comment='合作状态')
    # none(未合作)/contacting(接洽中)/cooperating(合作中)/ended(已结束)

    cooperation_type = db.Column(db.String(50), comment='合作类型')
    # 异业合作/物业合作/开发商合作

    contact_name = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    contact_position = db.Column(db.String(50), comment='职位')

    # 合作详情
    cooperation_start_date = db.Column(db.Date, comment='合作开始日期')
    cooperation_end_date = db.Column(db.Date, comment='合作结束日期')
    cooperation_terms = db.Column(db.Text, comment='合作条款')

    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    remark = db.Column(db.Text, comment='备注')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'alias': self.alias,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address': self.address,
            'longitude': float(self.longitude) if self.longitude else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'developer': self.developer,
            'property_company': self.property_company,
            'build_year': self.build_year,
            'total_houses': self.total_houses,
            'property_type': self.property_type,
            'cooperation_status': self.cooperation_status,
            'cooperation_type': self.cooperation_type,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_position': self.contact_position,
            'cooperation_start_date': self.cooperation_start_date.isoformat() if self.cooperation_start_date else None,
            'cooperation_end_date': self.cooperation_end_date.isoformat() if self.cooperation_end_date else None,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BuildingFollow(db.Model):
    """楼盘跟进记录"""
    __tablename__ = 'building_follow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)

    # 跟进信息
    follow_type = db.Column(db.String(50), comment='跟进类型')
    # visit(拜访)/phone(电话)/meeting(会议)/other(其他)

    content = db.Column(db.Text, comment='跟进内容')

    # 联系人
    contact_name = db.Column(db.String(50), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')

    # 结果
    result = db.Column(db.String(50), comment='跟进结果')
    # interested(有意向)/considering(考虑中)/rejected(拒绝)/cooperated(已合作)

    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    next_follow_content = db.Column(db.Text, comment='下次跟进内容')

    # 操作人
    operator_id = db.Column(db.Integer, comment='跟进人ID')
    operator_name = db.Column(db.String(50), comment='跟进人姓名')

    attachments = db.Column(db.JSON, default=list, comment='附件')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'building_id': self.building_id,
            'follow_type': self.follow_type,
            'content': self.content,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'result': self.result,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'next_follow_content': self.next_follow_content,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'attachments': self.attachments or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BuildingCustomer(db.Model):
    """楼盘客户关联（业主信息）"""
    __tablename__ = 'building_customer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    # 房屋信息
    building_no = db.Column(db.String(20), comment='楼栋号')
    unit_no = db.Column(db.String(20), comment='单元号')
    room_no = db.Column(db.String(20), comment='房号')
    floor = db.Column(db.Integer, comment='楼层')

    # 户型面积
    house_type = db.Column(db.String(50), comment='户型')
    house_area = db.Column(db.Numeric(8, 2), comment='面积')

    # 装修状态
    decoration_status = db.Column(db.String(20), comment='装修状态')
    # not_started(未装修)/decorating(装修中)/completed(已完工)

    # 业主类型
    owner_type = db.Column(db.String(20), comment='业主类型')
    # owner(业主)/tenant(租户)/investor(投资客)

    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'building_id': self.building_id,
            'customer_id': self.customer_id,
            'building_no': self.building_no,
            'unit_no': self.unit_no,
            'room_no': self.room_no,
            'floor': self.floor,
            'house_type': self.house_type,
            'house_area': float(self.house_area) if self.house_area else None,
            'decoration_status': self.decoration_status,
            'owner_type': self.owner_type,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 合作状态选项
COOPERATION_STATUS = [
    ('none', '未合作'),
    ('contacting', '接洽中'),
    ('cooperating', '合作中'),
    ('ended', '已结束'),
]

# 合作类型
COOPERATION_TYPES = [
    ('cross_industry', '异业合作'),
    ('property', '物业合作'),
    ('developer', '开发商合作'),
    ('community', '社区合作'),
]

# 物业类型
PROPERTY_TYPES = [
    ('residential', '住宅'),
    ('villa', '别墅'),
    ('apartment', '公寓'),
    ('commercial', '商业'),
    ('mixed', '商住混合'),
]

# 跟进类型
FOLLOW_TYPES = [
    ('visit', '上门拜访'),
    ('phone', '电话联系'),
    ('meeting', '会议洽谈'),
    ('event', '活动推广'),
    ('other', '其他'),
]

# 跟进结果
FOLLOW_RESULTS = [
    ('interested', '有意向'),
    ('considering', '考虑中'),
    ('rejected', '拒绝'),
    ('cooperated', '已合作'),
    ('follow_up', '需跟进'),
]
