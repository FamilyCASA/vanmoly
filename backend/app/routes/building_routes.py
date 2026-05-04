"""
楼盘管理模块 - API路由
V3.0 全新设计 + V3.1 Excel导入 + AI智能总结
"""
import os
import json
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models.building import (
    Building, BuildingFollow, BuildingCustomer,
    COOPERATION_STATUS, COOPERATION_TYPES, PROPERTY_TYPES, FOLLOW_TYPES, FOLLOW_RESULTS
)
from app.models.customer import Customer
from app.routes.auth_routes_v2 import jwt_required_v2
from app.utils.ai_utils import ai_summarize_building, ai_extract_customers, ai_analyze_excel_row
from datetime import datetime, date

logger = logging.getLogger(__name__)

building_bp = Blueprint('building', __name__, url_prefix='/api/v3/buildings')


# ========== 楼盘管理 ==========

@building_bp.route('', methods=['GET'])
@jwt_required_v2
def get_buildings(current_user):
    """获取楼盘列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    city = request.args.get('city', '').strip()
    cooperation_status = request.args.get('cooperation_status')
    property_type = request.args.get('property_type')

    query = Building.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    )

    if keyword:
        query = query.filter(
            db.or_(
                Building.name.contains(keyword),
                Building.alias.contains(keyword),
                Building.address.contains(keyword)
            )
        )

    if city:
        query = query.filter(Building.city.contains(city))
    if cooperation_status:
        query = query.filter_by(cooperation_status=cooperation_status)
    if property_type:
        query = query.filter_by(property_type=property_type)

    query = query.order_by(Building.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [b.to_dict() for b in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@building_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_building(current_user, id):
    """获取楼盘详情"""
    building = Building.query.get_or_404(id)

    # 加载跟进记录
    follows = BuildingFollow.query.filter_by(
        building_id=id
    ).order_by(BuildingFollow.created_at.desc()).all()

    # 加载业主信息
    customers = db.session.query(
        BuildingCustomer, Customer
    ).join(
        Customer, BuildingCustomer.customer_id == Customer.id
    ).filter(
        BuildingCustomer.building_id == id
    ).all()

    data = building.to_dict()
    data['follows'] = [f.to_dict() for f in follows]
    data['customers'] = [
        {
            **bc.to_dict(),
            'customer_name': c.name,
            'customer_phone': c.phone
        }
        for bc, c in customers
    ]

    return jsonify({
        'code': 200,
        'data': data
    })


@building_bp.route('', methods=['POST'])
@jwt_required_v2
def create_building(current_user):
    """创建楼盘"""
    data = request.get_json()

    building = Building(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        alias=data.get('alias'),
        province=data.get('province'),
        city=data.get('city'),
        district=data.get('district'),
        address=data.get('address'),
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        developer=data.get('developer'),
        property_company=data.get('property_company'),
        build_year=data.get('build_year'),
        total_houses=data.get('total_houses'),
        property_type=data.get('property_type'),
        cooperation_status=data.get('cooperation_status', 'none'),
        cooperation_type=data.get('cooperation_type'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
        contact_position=data.get('contact_position'),
        cooperation_start_date=data.get('cooperation_start_date'),
        cooperation_end_date=data.get('cooperation_end_date'),
        cooperation_terms=data.get('cooperation_terms'),
        remark=data.get('remark')
    )

    db.session.add(building)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': building.to_dict()
    })


@building_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_building(current_user, id):
    """更新楼盘"""
    building = Building.query.get_or_404(id)
    data = request.get_json()

    fields = [
        'name', 'alias', 'province', 'city', 'district', 'address',
        'longitude', 'latitude', 'developer', 'property_company',
        'build_year', 'total_houses', 'property_type',
        'cooperation_status', 'cooperation_type',
        'contact_name', 'contact_phone', 'contact_position',
        'cooperation_start_date', 'cooperation_end_date',
        'cooperation_terms', 'remark', 'is_enabled'
    ]

    for field in fields:
        if field in data:
            setattr(building, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': building.to_dict()
    })


@building_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_building(current_user, id):
    """删除楼盘"""
    building = Building.query.get_or_404(id)
    building.is_enabled = False
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 跟进记录 ==========

@building_bp.route('/<int:building_id>/follows', methods=['GET'])
@jwt_required_v2
def get_follows(current_user, building_id):
    """获取楼盘跟进记录"""
    follows = BuildingFollow.query.filter_by(
        building_id=building_id
    ).order_by(BuildingFollow.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'data': [f.to_dict() for f in follows]
    })


@building_bp.route('/<int:building_id>/follows', methods=['POST'])
@jwt_required_v2
def add_follow(current_user, building_id):
    """添加跟进记录"""
    data = request.get_json()

    follow = BuildingFollow(
        building_id=building_id,
        follow_type=data.get('follow_type'),
        content=data.get('content'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
        result=data.get('result'),
        next_follow_at=data.get('next_follow_at'),
        next_follow_content=data.get('next_follow_content'),
        operator_id=current_user.get('id'),
        operator_name=current_user.get('name'),
        attachments=data.get('attachments', [])
    )

    db.session.add(follow)

    # 更新楼盘合作状态
    if data.get('result') == 'cooperated':
        building = Building.query.get(building_id)
        if building:
            building.cooperation_status = 'cooperating'
            building.cooperation_start_date = date.today()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': follow.to_dict()
    })


# ========== 业主管理 ==========

@building_bp.route('/<int:building_id>/customers', methods=['GET'])
@jwt_required_v2
def get_building_customers(current_user, building_id):
    """获取楼盘业主列表"""
    records = db.session.query(
        BuildingCustomer, Customer
    ).join(
        Customer, BuildingCustomer.customer_id == Customer.id
    ).filter(
        BuildingCustomer.building_id == building_id
    ).all()

    return jsonify({
        'code': 200,
        'data': [
            {
                **bc.to_dict(),
                'customer_name': c.name,
                'customer_phone': c.phone
            }
            for bc, c in records
        ]
    })


@building_bp.route('/<int:building_id>/customers', methods=['POST'])
@jwt_required_v2
def add_building_customer(current_user, building_id):
    """添加业主"""
    data = request.get_json()

    # 检查是否已存在
    existing = BuildingCustomer.query.filter_by(
        building_id=building_id,
        customer_id=data['customer_id']
    ).first()

    if existing:
        return jsonify({'code': 400, 'message': '该客户已是该楼盘业主'}), 400

    record = BuildingCustomer(
        building_id=building_id,
        customer_id=data['customer_id'],
        building_no=data.get('building_no'),
        unit_no=data.get('unit_no'),
        room_no=data.get('room_no'),
        floor=data.get('floor'),
        house_type=data.get('house_type'),
        house_area=data.get('house_area'),
        decoration_status=data.get('decoration_status', 'not_started'),
        owner_type=data.get('owner_type', 'owner'),
        remark=data.get('remark')
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': record.to_dict()
    })


# ========== 统计报表 ==========

@building_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取楼盘统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 总数
    total = Building.query.filter_by(
        tenant_id=tenant_id,
        is_enabled=True
    ).count()

    # 合作状态统计
    status_stats = db.session.query(
        Building.cooperation_status,
        db.func.count(Building.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_enabled=True
    ).group_by(Building.cooperation_status).all()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Building.query.filter(
        Building.tenant_id == tenant_id,
        Building.is_enabled == True,
        Building.created_at >= current_month
    ).count()

    # 合作中数量
    cooperating = Building.query.filter_by(
        tenant_id=tenant_id,
        is_enabled=True,
        cooperation_status='cooperating'
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'by_status': {s: c for s, c in status_stats},
            'new_this_month': new_this_month,
            'cooperating': cooperating
        }
    })


# ========== 选项数据 ==========

@building_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取楼盘相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'cooperation_status': [{'value': v, 'label': l} for v, l in COOPERATION_STATUS],
            'cooperation_types': [{'value': v, 'label': l} for v, l in COOPERATION_TYPES],
            'property_types': [{'value': v, 'label': l} for v, l in PROPERTY_TYPES],
            'follow_types': [{'value': v, 'label': l} for v, l in FOLLOW_TYPES],
            'follow_results': [{'value': v, 'label': l} for v, l in FOLLOW_RESULTS],
        }
    })


# ========== AI 智能总结 ==========

@building_bp.route('/ai-summarize', methods=['POST'])
@jwt_required_v2
def ai_summarize(current_user):
    """AI 总结楼盘信息，自动填表"""
    data = request.get_json()
    raw_text = data.get('text', '').strip()

    if not raw_text:
        return jsonify({'code': 400, 'message': '请输入楼盘原始信息'}), 400

    result = ai_summarize_building(raw_text)

    if not result:
        return jsonify({
            'code': 503,
            'message': 'AI 服务暂不可用（可能账户欠费或网络问题），请稍后重试或手动填写'
        }), 503

    return jsonify({
        'code': 200,
        'message': 'AI 分析完成',
        'data': result
    })


# ========== Excel 批量导入 ==========

@building_bp.route('/import-excel', methods=['POST'])
@jwt_required_v2
def import_excel(current_user):
    """Excel 批量导入楼盘调查数据
    
    Excel 列头支持（自动识别）：
    楼盘名称/楼盘/名称, 地址, 开发商, 物业/物业公司, 
    楼栋/栋号, 单元, 房号/房号, 
    户型, 面积, 业主/姓名, 电话/手机, 
    装修状态, 备注
    """
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请上传 Excel 文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'code': 400, 'message': '文件名为空'}), 400

    # 检查文件扩展名
    allowed_ext = {'.xlsx', '.xls', '.csv'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_ext:
        return jsonify({'code': 400, 'message': f'不支持的文件格式 {ext}，请上传 xlsx/xls/csv'}), 400

    # 保存临时文件
    filename = secure_filename(file.filename)
    if not filename:
        filename = 'import' + ext
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'temp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f'building_import_{datetime.now().strftime("%Y%m%d%H%M%S")}_{filename}')
    file.save(tmp_path)

    try:
        import pandas as pd

        # 读取 Excel
        if ext == '.csv':
            df = pd.read_csv(tmp_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(tmp_path)

        if df.empty:
            return jsonify({'code': 400, 'message': 'Excel 文件为空'}), 400

        # 列名映射（支持多种表头写法）
        COLUMN_MAP = {
            '楼盘名称': 'building_name', '楼盘': 'building_name', '名称': 'building_name',
            '地址': 'address', '详细地址': 'address',
            '开发商': 'developer',
            '物业': 'property_company', '物业公司': 'property_company',
            '城市': 'city', '市': 'city',
            '区': 'district', '区县': 'district', '区域': 'district',
            '省': 'province',
            '楼栋': 'building_no', '栋号': 'building_no', '楼栋号': 'building_no',
            '单元': 'unit_no', '单元号': 'unit_no',
            '房号': 'room_no', '房间号': 'room_no',
            '户型': 'house_type',
            '面积': 'house_area', '建筑面积': 'house_area',
            '业主': 'customer_name', '姓名': 'customer_name', '客户': 'customer_name', '业主姓名': 'customer_name',
            '电话': 'customer_phone', '手机': 'customer_phone', '手机号': 'customer_phone', '联系电话': 'customer_phone',
            '装修状态': 'decoration_status',
            '备注': 'remark', '说明': 'remark',
        }

        # 标准化列名
        df.columns = [str(c).strip() for c in df.columns]
        renamed = {}
        for col in df.columns:
            if col in COLUMN_MAP:
                renamed[col] = COLUMN_MAP[col]
        df = df.rename(columns=renamed)

        # 填充 NaN
        df = df.fillna('')

        # 按 building_name 分组处理
        building_groups = df.groupby('building_name') if 'building_name' in df.columns else None

        tenant_id = current_user.get('tenant_id', '0')
        created_buildings = 0
        updated_buildings = 0
        created_customers = 0
        errors = []

        if building_groups is not None:
            for bname, group in building_groups:
                if not bname:
                    continue

                # 取第一行的楼盘信息
                first = group.iloc[0]

                # 查找或创建楼盘
                building = Building.query.filter_by(
                    name=str(bname),
                    tenant_id=tenant_id,
                    is_enabled=True
                ).first()

                if building:
                    # 更新楼盘信息（只更新非空字段）
                    updated = False
                    for field, col in [
                        ('address', 'address'), ('developer', 'developer'),
                        ('property_company', 'property_company'),
                        ('city', 'city'), ('district', 'district'),
                        ('province', 'province'),
                    ]:
                        val = str(first.get(col, ''))
                        if val and val != 'nan':
                            setattr(building, field, val)
                            updated = True
                    if updated:
                        updated_buildings += 1
                else:
                    # 创建新楼盘
                    building = Building(
                        tenant_id=tenant_id,
                        name=str(bname),
                        address=str(first.get('address', '')) if first.get('address', '') else None,
                        developer=str(first.get('developer', '')) if first.get('developer', '') else None,
                        property_company=str(first.get('property_company', '')) if first.get('property_company', '') else None,
                        city=str(first.get('city', '')) if first.get('city', '') else None,
                        district=str(first.get('district', '')) if first.get('district', '') else None,
                        province=str(first.get('province', '')) if first.get('province', '') else None,
                        cooperation_status='none',
                    )
                    db.session.add(building)
                    db.session.flush()  # 获取 building.id
                    created_buildings += 1

                # 导入客户/业主数据
                for _, row in group.iterrows():
                    customer_name = str(row.get('customer_name', '')).strip()
                    customer_phone = str(row.get('customer_phone', '')).strip()

                    if not customer_name and not customer_phone:
                        continue

                    # 查找或创建客户
                    customer = None
                    if customer_phone:
                        customer = Customer.query.filter_by(phone=customer_phone).first()
                    if not customer and customer_name:
                        customer = Customer.query.filter_by(name=customer_name).first()
                    if not customer:
                        customer = Customer(
                            name=customer_name or 'unknown',
                            phone=customer_phone or '',
                            source='building_import',
                            status='new'
                        )
                        db.session.add(customer)
                        db.session.flush()

                    # 检查是否已关联
                    existing = BuildingCustomer.query.filter_by(
                        building_id=building.id,
                        customer_id=customer.id
                    ).first()

                    if existing:
                        continue

                    # 创建关联
                    bc = BuildingCustomer(
                        building_id=building.id,
                        customer_id=customer.id,
                        building_no=str(row.get('building_no', '')) or None,
                        unit_no=str(row.get('unit_no', '')) or None,
                        room_no=str(row.get('room_no', '')) or None,
                        house_type=str(row.get('house_type', '')) or None,
                        house_area=float(row['house_area']) if row.get('house_area') and str(row.get('house_area', '')) not in ('', 'nan') else None,
                        decoration_status=str(row.get('decoration_status', 'not_started')) or 'not_started',
                        owner_type='owner',
                        remark=str(row.get('remark', '')) or None,
                    )
                    db.session.add(bc)
                    created_customers += 1

        db.session.commit()

        # 清理临时文件
        try:
            os.remove(tmp_path)
        except:
            pass

        return jsonify({
            'code': 200,
            'message': f'导入完成：新建楼盘 {created_buildings} 个，更新楼盘 {updated_buildings} 个，导入业主 {created_customers} 条',
            'data': {
                'created_buildings': created_buildings,
                'updated_buildings': updated_buildings,
                'created_customers': created_customers,
                'errors': errors,
                'total_rows': len(df)
            }
        })

    except Exception as e:
        logger.error(f'Excel import error: {str(e)}', exc_info=True)
        # 清理临时文件
        try:
            os.remove(tmp_path)
        except:
            pass
        return jsonify({'code': 500, 'message': f'导入失败: {str(e)}'}), 500


# ========== Excel 模板下载 ==========

@building_bp.route('/import-template', methods=['GET'])
@jwt_required_v2
def download_import_template(current_user):
    """下载楼盘调查 Excel 导入模板"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    columns = [
        '楼盘名称', '省', '城市', '区', '地址', '开发商', '物业公司',
        '楼栋', '单元', '房号', '户型', '面积',
        '业主姓名', '联系电话', '装修状态', '备注'
    ]

    # 示例数据
    sample_data = [
        ['天府匠芯', '四川', '成都', '青羊', '蔡桥街道天府匠芯北区', 'XX开发', 'XX物业',
         'A栋', '1单元', '601', '3室2厅', 125,
         '张三', '13800001111', '未装修', '重点客户'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='楼盘调查数据')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='楼盘调查导入模板.xlsx'
    )


# ========== AI 批量分析 Excel 数据 ==========

@building_bp.route('/ai-analyze-excel', methods=['POST'])
@jwt_required_v2
def ai_analyze_excel(current_user):
    """上传 Excel 后先用 AI 分析数据质量，返回预览结果（不写入数据库）"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请上传 Excel 文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'code': 400, 'message': '文件名为空'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {'.xlsx', '.xls', '.csv'}:
        return jsonify({'code': 400, 'message': f'不支持的文件格式 {ext}'}), 400

    # 保存临时文件
    filename = secure_filename(file.filename)
    if not filename:
        filename = 'analyze' + ext
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'temp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f'building_analyze_{datetime.now().strftime("%Y%m%d%H%M%S")}_{filename}')
    file.save(tmp_path)

    try:
        import pandas as pd

        if ext == '.csv':
            df = pd.read_csv(tmp_path, encoding='utf-8-sig')
        else:
            df = pd.read_excel(tmp_path)

        if df.empty:
            return jsonify({'code': 400, 'message': 'Excel 文件为空'}), 400

        # 返回预览数据（前20行 + 列信息 + 统计）
        df = df.fillna('')
        preview = df.head(20).to_dict('records')
        columns = list(df.columns)
        stats = {
            'total_rows': len(df),
            'columns': columns,
            'column_count': len(columns),
        }

        # 检测可能的列映射
        COLUMN_MAP = {
            '楼盘名称': 'building_name', '楼盘': 'building_name', '名称': 'building_name',
            '地址': 'address', '详细地址': 'address',
            '开发商': 'developer',
            '物业': 'property_company', '物业公司': 'property_company',
            '城市': 'city', '市': 'city',
            '区': 'district', '区县': 'district',
            '省': 'province',
            '楼栋': 'building_no', '栋号': 'building_no',
            '单元': 'unit_no', '单元号': 'unit_no',
            '房号': 'room_no', '房间号': 'room_no',
            '户型': 'house_type',
            '面积': 'house_area', '建筑面积': 'house_area',
            '业主': 'customer_name', '姓名': 'customer_name', '客户': 'customer_name', '业主姓名': 'customer_name',
            '电话': 'customer_phone', '手机': 'customer_phone', '手机号': 'customer_phone', '联系电话': 'customer_phone',
            '装修状态': 'decoration_status',
            '备注': 'remark', '说明': 'remark',
        }

        mapping = {}
        unmapped = []
        for col in columns:
            col_stripped = str(col).strip()
            if col_stripped in COLUMN_MAP:
                mapping[col_stripped] = COLUMN_MAP[col_stripped]
            else:
                unmapped.append(col_stripped)

        stats['mapping'] = mapping
        stats['unmapped'] = unmapped
        stats['mapped_count'] = len(mapping)

        # 清理临时文件
        try:
            os.remove(tmp_path)
        except:
            pass

        return jsonify({
            'code': 200,
            'message': '分析完成',
            'data': {
                'preview': preview,
                'stats': stats
            }
        })

    except Exception as e:
        logger.error(f'Excel analyze error: {str(e)}', exc_info=True)
        try:
            os.remove(tmp_path)
        except:
            pass
        return jsonify({'code': 500, 'message': f'分析失败: {str(e)}'}), 500
