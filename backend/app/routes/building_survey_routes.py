"""
楼盘调查表 - API路由
V3.2 新增模块
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.building_survey import BuildingSurvey
from app.models.building import Building
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

survey_bp = Blueprint('building_survey', __name__, url_prefix='/api/v3/building-surveys')


@survey_bp.route('/<int:building_id>', methods=['GET'])
@jwt_required_v2
def get_survey(current_user, building_id):
    """获取指定楼盘的调查表"""
    survey = BuildingSurvey.query.filter_by(building_id=building_id).first()
    if not survey:
        return jsonify({'code': 404, 'msg': '该楼盘尚未录入调查表'}), 404
    return jsonify({'code': 200, 'data': survey.to_dict()})


@survey_bp.route('', methods=['POST'])
@jwt_required_v2
def create_survey(current_user):
    """新建楼盘调查表"""
    data = request.get_json()

    building_id = data.get('building_id')
    if not building_id:
        return jsonify({'code': 400, 'msg': 'building_id 不能为空'}), 400

    # 检查楼盘是否存在
    building = Building.query.get(building_id)
    if not building:
        return jsonify({'code': 404, 'msg': '楼盘不存在'}), 404

    # 检查是否已有调查表
    existing = BuildingSurvey.query.filter_by(building_id=building_id).first()
    if existing:
        return jsonify({'code': 400, 'msg': '该楼盘已存在调查表，请使用更新接口'}), 400

    # 校验购房人群占比
    age_fields = ['age_0_18', 'age_19_30', 'age_31_45', 'age_46_60', 'age_60_plus']
    total = sum(int(data.get(f, 0) or 0) for f in age_fields)
    if total > 0 and abs(total - 100) > 5:
        return jsonify({'code': 400, 'msg': f'购房人群占比总和为 {total}%，应接近100%'}), 400

    survey = BuildingSurvey(building_id=building_id)
    _apply_data(survey, data)
    db.session.add(survey)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '创建成功', 'data': survey.to_dict()})


@survey_bp.route('/<int:building_id>', methods=['PUT'])
@jwt_required_v2
def update_survey(current_user, building_id):
    """更新楼盘调查表"""
    survey = BuildingSurvey.query.filter_by(building_id=building_id).first()
    if not survey:
        return jsonify({'code': 404, 'msg': '调查表不存在'}), 404

    data = request.get_json()

    # 校验购房人群占比
    age_fields = ['age_0_18', 'age_19_30', 'age_31_45', 'age_46_60', 'age_60_plus']
    total = sum(int(data.get(f, 0) or 0) for f in age_fields)
    if total > 0 and abs(total - 100) > 5:
        return jsonify({'code': 400, 'msg': f'购房人群占比总和为 {total}%，应接近100%'}), 400

    _apply_data(survey, data)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': survey.to_dict()})


@survey_bp.route('/<int:building_id>', methods=['DELETE'])
@jwt_required_v2
def delete_survey(current_user, building_id):
    """删除楼盘调查表"""
    survey = BuildingSurvey.query.filter_by(building_id=building_id).first()
    if not survey:
        return jsonify({'code': 404, 'msg': '调查表不存在'}), 404
    db.session.delete(survey)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})


def _apply_data(survey, data):
    """将请求数据写入模型字段"""
    date_fields = ['delivery_date', 'entry_date']
    int_fields = ['delivery_count', 'unit_count',
                  'age_0_18', 'age_19_30', 'age_31_45', 'age_46_60', 'age_60_plus']
    str_fields = ['base_task', 'property_category',
                 'unit_area', 'main_unit_type',
                 'matching_shops', 'metro_info', 'park_info', 'entry_by']

    for f in date_fields:
        val = data.get(f)
        if val:
            try:
                if len(str(val)) == 7:
                    survey.__setattr__(f, datetime.strptime(val, '%Y-%m').date())
                else:
                    survey.__setattr__(f, datetime.strptime(val, '%Y-%m-%d').date())
            except ValueError:
                pass

    for f in int_fields:
        val = data.get(f)
        if val is not None:
            try:
                survey.__setattr__(f, int(val))
            except (ValueError, TypeError):
                pass

    for f in str_fields:
        survey.__setattr__(f, data.get(f))