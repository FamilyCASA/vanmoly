"""
导出 Case ID=37 的数据为 JSON
"""
import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.case import CaseStudy, CaseMedia, CasePhase, CaseSpaceRendering

app = create_app()

with app.app_context():
    # 读取 Case ID=37
    case = CaseStudy.query.get(37)
    
    if not case:
        print(json.dumps({'error': 'Case ID=37 not found'}))
        sys.exit(1)
    
    # 转换为字典
    case_data = case.to_dict(include_relations=True)
    
    # 读取关联的媒体文件
    media_files = CaseMedia.query.filter_by(case_id=37).all()
    case_data['media_files'] = [m.to_dict() for m in media_files]
    
    # 读取阶段数据
    phases = CasePhase.query.filter_by(case_id=37).order_by(CasePhase.phase_number).all()
    case_data['phases'] = [p.to_dict() for p in phases]
    
    # 读取空间效果图
    from app.models.case import CaseSpaceRendering, CaseRenderingItem
    spaces = CaseSpaceRendering.query.filter_by(case_id=37).order_by(CaseSpaceRendering.sort_order).all()
    case_data['spaces'] = [s.to_dict(include_items=True) for s in spaces]
    
    # 输出 JSON
    print(json.dumps(case_data, ensure_ascii=False, indent=2))
