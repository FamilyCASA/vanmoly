# -*- coding: utf-8 -*-
"""
空间配置模块 - 数据模型
V3.2 新增：案例空间配置模板
"""
from datetime import datetime
from app import db
import json


class CaseSpaceConfig(db.Model):
    """空间配置模板表"""
    __tablename__ = 'case_space_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)
    
    # 关联
    case_id = db.Column(db.Integer, nullable=False, comment='关联案例')
    quote_id = db.Column(db.Integer, comment='关联报价单')
    
    # 空间信息
    space_type = db.Column(db.String(50), nullable=False, comment='空间类型：客厅/主卧/餐厅等')
    space_name = db.Column(db.String(100), comment='空间名称（自定义）')
    space_area = db.Column(db.Numeric(10, 2), comment='空间面积')
    
    # 版本档位
    version_level = db.Column(db.String(20), nullable=False, comment='档位：舒适/豪华/顶配')
    version_code = db.Column(db.String(20), comment='版本编码：C/H/T')
    
    # 配置信息
    config_name = db.Column(db.String(200), comment='配置名称')
    config_desc = db.Column(db.Text, comment='配置描述')
    
    # 物料清单（JSON格式）
    materials = db.Column(db.Text, comment='物料清单JSON')
    material_count = db.Column(db.Integer, default=0, comment='物料数量')
    
    # 价格汇总
    material_cost = db.Column(db.Numeric(12, 2), default=0, comment='物料成本')
    labor_cost = db.Column(db.Numeric(12, 2), default=0, comment='人工成本')
    design_cost = db.Column(db.Numeric(12, 2), default=0, comment='设计费')
    manage_cost = db.Column(db.Numeric(12, 2), default=0, comment='管理费')
    total_price = db.Column(db.Numeric(12, 2), default=0, comment='空间总价')
    
    # 模板属性
    is_template = db.Column(db.Boolean, default=True, comment='是否为模板')
    template_tags = db.Column(db.Text, comment='模板标签JSON')
    
    # 互斥配置
    exclusive_rules = db.Column(db.Text, comment='互斥规则JSON')
    
    # 状态
    status = db.Column(db.String(20), default='active', comment='状态：active/disabled')
    
    # 创建人
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    items = db.relationship('CaseSpaceConfigItem', backref='config', lazy='dynamic',
                            cascade='all, delete-orphan',
                            primaryjoin='CaseSpaceConfig.id == CaseSpaceConfigItem.config_id',
                            foreign_keys='CaseSpaceConfigItem.config_id')
    
    # 空间类型常量
    SPACE_TYPES = ['客厅', '主卧', '次卧', '餐厅', '厨房', '卫生间', '书房', '阳台', '玄关', '储物间']
    
    # 版本常量
    VERSION_LEVELS = ['舒适', '豪华', '顶配']
    VERSION_CODES = {'舒适': 'C', '豪华': 'H', '顶配': 'T'}
    
    def to_dict(self, include_items=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'case_id': self.case_id,
            'quote_id': self.quote_id,
            'space_type': self.space_type,
            'space_name': self.space_name or self.space_type,
            'space_area': float(self.space_area) if self.space_area else None,
            'version_level': self.version_level,
            'version_code': self.version_code,
            'config_name': self.config_name,
            'config_desc': self.config_desc,
            'materials': json.loads(self.materials) if self.materials else [],
            'material_count': self.material_count,
            'material_cost': float(self.material_cost) if self.material_cost else 0,
            'labor_cost': float(self.labor_cost) if self.labor_cost else 0,
            'design_cost': float(self.design_cost) if self.design_cost else 0,
            'manage_cost': float(self.manage_cost) if self.manage_cost else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'is_template': self.is_template,
            'template_tags': json.loads(self.template_tags) if self.template_tags else [],
            'exclusive_rules': json.loads(self.exclusive_rules) if self.exclusive_rules else {},
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
    
    def calculate_total(self):
        """计算总价"""
        total = 0
        for item in self.items:
            if item.total_price:
                total += float(item.total_price)
        self.material_cost = total
        self.total_price = total + float(self.labor_cost or 0) + float(self.design_cost or 0) + float(self.manage_cost or 0)
        self.material_count = self.items.count()
        return self.total_price
    
    @classmethod
    def get_version_code(cls, level):
        """获取版本编码"""
        return cls.VERSION_CODES.get(level, 'C')


class CaseSpaceConfigItem(db.Model):
    """空间配置物料明细表"""
    __tablename__ = 'case_space_config_item'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_id = db.Column(db.Integer, nullable=False)
    
    # 物料信息
    sku_id = db.Column(db.Integer, nullable=False)
    sku_code = db.Column(db.String(50), comment='物料编码')
    sku_name = db.Column(db.String(200), comment='物料名称')
    brand = db.Column(db.String(100), comment='品牌')
    specification = db.Column(db.String(200), comment='规格')
    category = db.Column(db.String(50), comment='分类')
    
    # 用量与价格
    quantity = db.Column(db.Numeric(10, 2), default=1, comment='数量')
    unit = db.Column(db.String(20), comment='单位')
    unit_price = db.Column(db.Numeric(12, 2), comment='单价')
    total_price = db.Column(db.Numeric(12, 2), comment='小计')
    
    # 互斥标记
    is_exclusive = db.Column(db.Boolean, default=False, comment='是否互斥项')
    exclusive_group = db.Column(db.String(50), comment='互斥组')
    
    # 选装标记
    is_optional = db.Column(db.Boolean, default=False, comment='是否选装项')
    is_default = db.Column(db.Boolean, default=True, comment='是否默认包含')
    
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_id': self.config_id,
            'sku_id': self.sku_id,
            'sku_code': self.sku_code,
            'sku_name': self.sku_name,
            'brand': self.brand,
            'specification': self.specification,
            'category': self.category,
            'quantity': float(self.quantity) if self.quantity else 1,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'is_exclusive': self.is_exclusive,
            'exclusive_group': self.exclusive_group,
            'is_optional': self.is_optional,
            'is_default': self.is_default,
            'sort_order': self.sort_order,
        }


class QuoteSpaceInstance(db.Model):
    """报价单-空间配置实例表"""
    __tablename__ = 'quote_space_instance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)
    
    quote_id = db.Column(db.Integer, nullable=False)
    template_config_id = db.Column(db.Integer)
    
    # 空间信息（复制自模板，可修改）
    space_type = db.Column(db.String(50))
    space_name = db.Column(db.String(100))
    space_area = db.Column(db.Numeric(10, 2))
    version_level = db.Column(db.String(20))
    
    # 调整后价格
    original_price = db.Column(db.Numeric(12, 2), comment='模板原价')
    adjusted_price = db.Column(db.Numeric(12, 2), comment='调整后价格')
    adjustment_reason = db.Column(db.Text, comment='调整原因')
    
    # 调整明细（JSON）
    adjustments = db.Column(db.Text, comment='调整明细JSON')
    
    # 状态
    is_selected = db.Column(db.Boolean, default=True, comment='是否选中')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'quote_id': self.quote_id,
            'template_config_id': self.template_config_id,
            'space_type': self.space_type,
            'space_name': self.space_name,
            'space_area': float(self.space_area) if self.space_area else None,
            'version_level': self.version_level,
            'original_price': float(self.original_price) if self.original_price else 0,
            'adjusted_price': float(self.adjusted_price) if self.adjusted_price else 0,
            'adjustment_reason': self.adjustment_reason,
            'adjustments': json.loads(self.adjustments) if self.adjustments else {},
            'is_selected': self.is_selected,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class MaterialExclusiveRule(db.Model):
    """物料互斥规则表"""
    __tablename__ = 'material_exclusive_rule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)
    
    rule_name = db.Column(db.String(100), comment='规则名称')
    rule_group = db.Column(db.String(50), comment='互斥组')
    
    sku_id = db.Column(db.Integer)
    exclusive_sku_ids = db.Column(db.Text, comment='互斥物料ID列表JSON')
    
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'rule_name': self.rule_name,
            'rule_group': self.rule_group,
            'sku_id': self.sku_id,
            'exclusive_sku_ids': json.loads(self.exclusive_sku_ids) if self.exclusive_sku_ids else [],
            'description': self.description,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def check_conflict(self, selected_sku_ids):
        """检查是否有冲突"""
        exclusive_ids = set(json.loads(self.exclusive_sku_ids) if self.exclusive_sku_ids else [])
        selected = set(selected_sku_ids)
        conflicts = selected & exclusive_ids
        return len(conflicts) > 0, list(conflicts)
