# -*- coding: utf-8 -*-
"""
V3.2 视觉素材6阶段 API - 追加到case_routes.py
"""

NEW_API_CODE = '''

# ============================================================
# V3.2 视觉素材6阶段 API
# ============================================================

@case_bp.route('/<int:id>/phases', methods=['GET'])
@jwt_required()
def get_case_phases(current_user, id):
    """获取案例所有阶段内容"""
    try:
        from app.models.case import CasePhase
        phases = CasePhase.query.filter_by(case_id=id).order_by(CasePhase.phase_number).all()
        # 确保返回6个阶段（即使为空）
        result = {i: None for i in range(1, 7)}
        for p in phases:
            result[p.phase_number] = p.to_dict()
        return api_response(data=result)
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/<int:id>/phases/<int:phase_num>', methods=['PUT'])
@jwt_required()
def update_case_phase(current_user, id, phase_num):
    """更新指定阶段内容"""
    try:
        from app.models.case import CasePhase
        data = request.get_json()
        
        phase = CasePhase.query.filter_by(case_id=id, phase_number=phase_num).first()
        if not phase:
            phase = CasePhase(case_id=id, phase_number=phase_num)
            db.session.add(phase)
        
        # 阶段名称
        phase_names = {
            1: '户型分析',
            2: '设计意境',
            3: '平面规划',
            4: '鸟瞰展示',
            5: '效果图首页',
            6: '空间效果图'
        }
        phase.phase_name = phase_names.get(phase_num, '')
        
        # 根据阶段号更新对应字段
        if phase_num == 1:
            if 'layout_images' in data:
                phase.layout_images = json.dumps(data['layout_images'])
            if 'layout_analysis' in data:
                phase.layout_analysis = data['layout_analysis']
        elif phase_num == 2:
            if 'mood_images' in data:
                phase.mood_images = json.dumps(data['mood_images'])
            if 'mood_text' in data:
                phase.mood_text = data['mood_text']
        elif phase_num == 3:
            if 'plan_image' in data:
                phase.plan_image = data['plan_image']
            if 'plan_text' in data:
                phase.plan_text = data['plan_text']
        elif phase_num == 4:
            if 'birdview_images' in data:
                phase.birdview_images = json.dumps(data['birdview_images'])
        elif phase_num == 5:
            if 'showcase_images' in data:
                phase.showcase_images = json.dumps(data['showcase_images'])
            if 'showcase_title1' in data:
                phase.showcase_title1 = data['showcase_title1']
            if 'showcase_title2' in data:
                phase.showcase_title2 = data['showcase_title2']
            if 'showcase_text_cn' in data:
                phase.showcase_text_cn = data['showcase_text_cn']
            if 'showcase_text_en' in data:
                phase.showcase_text_en = data['showcase_text_en']
        
        db.session.commit()
        return api_response(data=phase.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ============================================================
# 空间效果图 API (阶段6)
# ============================================================

@case_bp.route('/<int:id>/spaces', methods=['GET'])
@jwt_required()
def get_case_spaces(current_user, id):
    """获取案例空间列表"""
    try:
        from app.models.case import CaseSpaceRendering
        spaces = CaseSpaceRendering.query.filter_by(case_id=id).order_by(CaseSpaceRendering.sort_order).all()
        return api_response(data=[s.to_dict() for s in spaces])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/<int:id>/spaces', methods=['POST'])
@jwt_required()
def add_case_space(current_user, id):
    """添加空间"""
    try:
        from app.models.case import CaseSpaceRendering
        data = request.get_json()
        
        # 获取当前最大排序号
        max_order = db.session.query(db.func.max(CaseSpaceRendering.sort_order)).filter_by(case_id=id).scalar() or 0
        
        space = CaseSpaceRendering(
            case_id=id,
            space_name=data.get('space_name', '未命名空间'),
            sort_order=max_order + 1
        )
        db.session.add(space)
        db.session.commit()
        return api_response(data=space.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>', methods=['PUT'])
@jwt_required()
def update_case_space(current_user, space_id):
    """更新空间"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')
        
        data = request.get_json()
        if 'space_name' in data:
            space.space_name = data['space_name']
        if 'sort_order' in data:
            space.sort_order = data['sort_order']
        
        db.session.commit()
        return api_response(data=space.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>', methods=['DELETE'])
@jwt_required()
def delete_case_space(current_user, space_id):
    """删除空间（级联删除效果图）"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')
        
        db.session.delete(space)
        db.session.commit()
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ============================================================
# 效果图 API
# ============================================================

@case_bp.route('/spaces/<int:space_id>/renderings', methods=['GET'])
@jwt_required()
def get_space_renderings(current_user, space_id):
    """获取空间下的效果图列表"""
    try:
        from app.models.case import CaseRenderingItem
        items = CaseRenderingItem.query.filter_by(space_id=space_id).order_by(CaseRenderingItem.sort_order).all()
        return api_response(data=[i.to_dict() for i in items])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>/renderings', methods=['POST'])
@jwt_required()
def add_space_rendering(current_user, space_id):
    """添加效果图"""
    try:
        from app.models.case import CaseRenderingItem
        data = request.get_json()
        
        # 获取当前最大排序号
        max_order = db.session.query(db.func.max(CaseRenderingItem.sort_order)).filter_by(space_id=space_id).scalar() or 0
        
        item = CaseRenderingItem(
            space_id=space_id,
            image_url=data.get('image_url', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            sort_order=max_order + 1
        )
        db.session.add(item)
        db.session.commit()
        return api_response(data=item.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/renderings/<int:rendering_id>', methods=['PUT'])
@jwt_required()
def update_rendering(current_user, rendering_id):
    """更新效果图"""
    try:
        from app.models.case import CaseRenderingItem
        item = CaseRenderingItem.query.get(rendering_id)
        if not item:
            return api_response(code=404, message='效果图不存在')
        
        data = request.get_json()
        if 'image_url' in data:
            item.image_url = data['image_url']
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'sort_order' in data:
            item.sort_order = data['sort_order']
        
        db.session.commit()
        return api_response(data=item.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/renderings/<int:rendering_id>', methods=['DELETE'])
@jwt_required()
def delete_rendering(current_user, rendering_id):
    """删除效果图"""
    try:
        from app.models.case import CaseRenderingItem
        item = CaseRenderingItem.query.get(rendering_id)
        if not item:
            return api_response(code=404, message='效果图不存在')
        
        db.session.delete(item)
        db.session.commit()
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/reorder', methods=['POST'])
@jwt_required()
def reorder_spaces(current_user):
    """批量重排空间顺序"""
    try:
        from app.models.case import CaseSpaceRendering
        data = request.get_json()
        orders = data.get('orders', [])  # [{id: 1, sort_order: 1}, ...]
        
        for item in orders:
            space = CaseSpaceRendering.query.get(item['id'])
            if space:
                space.sort_order = item['sort_order']
        
        db.session.commit()
        return api_response(message='排序成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))
'''

if __name__ == '__main__':
    import codecs
    with codecs.open(r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py', 'a', 'utf-8') as f:
        f.write(NEW_API_CODE)
    print('API endpoints appended successfully')
