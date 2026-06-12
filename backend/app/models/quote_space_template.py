# -*- coding: utf-8 -*-
"""
报价空间模板模型
"""
from app import db
from datetime import datetime
import json


class QuoteSpaceTemplate(db.Model):
    """按空间粒度的报价模板"""
    __tablename__ = 'quote_space_template'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(32), default='0')
    name = db.Column(db.String(100), nullable=False)
    source_quote_id = db.Column(db.Integer)
    space_type = db.Column(db.String(50))
    space_name = db.Column(db.String(100))
    version_level = db.Column(db.String(20))
    house_type = db.Column(db.String(100))
    style = db.Column(db.String(50))
    area_range = db.Column(db.String(50))
    items_json = db.Column(db.Text)
    material_count = db.Column(db.Integer, default=0)
    material_cost = db.Column(db.Numeric(12, 2), default=0)
    labor_cost = db.Column(db.Numeric(12, 2), default=0)
    design_cost = db.Column(db.Numeric(12, 2), default=0)
    manage_cost = db.Column(db.Numeric(12, 2), default=0)
    total_price = db.Column(db.Numeric(12, 2), default=0)
    is_enabled = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        """序列化为字典"""
        items = []
        if self.items_json:
            try:
                items = json.loads(self.items_json)
            except Exception:
                items = []

        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'source_quote_id': self.source_quote_id,
            'space_type': self.space_type,
            'space_name': self.space_name,
            'version_level': self.version_level,
            'house_type': self.house_type,
            'style': self.style,
            'area_range': self.area_range,
            'items': items,
            'material_count': self.material_count,
            'material_cost': float(self.material_cost or 0),
            'labor_cost': float(self.labor_cost or 0),
            'design_cost': float(self.design_cost or 0),
            'manage_cost': float(self.manage_cost or 0),
            'total_price': float(self.total_price or 0),
            'is_enabled': bool(self.is_enabled),
            'sort_order': self.sort_order,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,
        }
