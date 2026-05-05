"""
合同管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models.contract import (
    Contract, ContractTemplate, ContractPayment, ContractChange,
    CONTRACT_TYPES, CONTRACT_STATUS, PAYMENT_PHASES
)
from app.models.customer import Customer
from app.models import Employee as Emp
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date
import io

# 使用weasyprint生成PDF
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

contract_bp = Blueprint('contract', __name__, url_prefix='/api/v3/contracts')


# ========== 合同模板 ==========

@contract_bp.route('/templates', methods=['GET'])
@jwt_required_v2
def get_templates(current_user):
    """获取合同模板列表"""
    contract_type = request.args.get('contract_type')

    query = ContractTemplate.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    )

    if contract_type:
        query = query.filter_by(contract_type=contract_type)

    templates = query.order_by(ContractTemplate.sort_order).all()

    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in templates]
    })


@contract_bp.route('/templates', methods=['POST'])
@jwt_required_v2
def create_template(current_user):
    """创建合同模板"""
    data = request.get_json()

    template = ContractTemplate(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        code=data.get('code'),
        contract_type=data['contract_type'],
        content=data.get('content', ''),
        variables=data.get('variables', []),
        is_default=data.get('is_default', False),
        sort_order=data.get('sort_order', 0)
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': template.to_dict()
    })


@contract_bp.route('/templates/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_template(current_user, id):
    """更新合同模板"""
    template = ContractTemplate.query.get_or_404(id)
    data = request.get_json()

    fields = ['name', 'code', 'contract_type', 'content', 'variables', 'is_default', 'is_enabled']
    for field in fields:
        if field in data:
            setattr(template, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': template.to_dict()
    })


# ========== 合同管理 ==========

@contract_bp.route('', methods=['GET'])
@jwt_required_v2
def get_contracts(current_user):
    """获取合同列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    contract_type = request.args.get('contract_type')

    query = Contract.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False
    )

    if keyword:
        query = query.filter(
            db.or_(
                Contract.contract_no.contains(keyword),
                Contract.title.contains(keyword)
            )
        )

    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)
    if contract_type:
        query = query.filter_by(contract_type=contract_type)

    query = query.order_by(Contract.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 加载客户信息
    items = []
    for contract in pagination.items:
        data = contract.to_dict()
        customer = Customer.query.get(contract.customer_id)
        data['customer_name'] = customer.name if customer else None
        items.append(data)

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@contract_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_contract(current_user, id):
    """获取合同详情"""
    contract = Contract.query.get_or_404(id)

    # 加载付款记录
    payments = ContractPayment.query.filter_by(contract_id=id).order_by(ContractPayment.planned_date).all()

    # 加载变更记录
    changes = ContractChange.query.filter_by(contract_id=id).order_by(ContractChange.created_at.desc()).all()

    data = contract.to_dict(include_content=True)
    data['payments'] = [p.to_dict() for p in payments]
    data['changes'] = [c.to_dict() for c in changes]

    # 客户信息
    customer = Customer.query.get(contract.customer_id)
    data['customer'] = customer.to_dict() if customer else None

    return jsonify({
        'code': 200,
        'data': data
    })


def _generate_contract_html(contract, customer, payments, v):
    """生成完整合同HTML（参考设记家标准合同范本）"""
    # 合同金额中文大写
    def to_rmb(val):
        if not val: return '零'
        s = '%.2f' % float(val)
        integer, decimal = s.split('.')
        units = ['', '万', '仟', '佰', '拾', '', '仟', '佰', '拾', '']
        nums = '零壹贰叁肆伍陆柒捌玖'
        result = []
        if len(integer) > 10: integer = integer[-10:]
        for i, c in enumerate(integer[::-1]):
            idx = len(integer) - i - 1
            if c != '0':
                result.append(nums[int(c)] + units[min(idx, len(units)-1)])
            else:
                if result and result[-1] != '零': result.append('零')
        res = ''.join(reversed(result)).strip('零') or '零'
        return res + '元整'

    total = float(contract.total_amount or 0)
    total_rmb = to_rmb(total)

    # 甲方信息
    party_a_name = v.get('party_a_name', customer.name if customer else '')
    party_a_phone = v.get('party_a_phone', customer.phone if customer else '')
    party_a_id_card = v.get('party_a_id_card', '________________________')
    party_a_area = v.get('party_a_area', '')
    party_a_address = v.get('party_a_address', '')
    # 乙方信息
    party_b_company = v.get('party_b_company', '成都术木家居设计有限公司')
    party_b_credit_code = v.get('party_b_credit_code', '91510107MA69NG2R92')
    party_b_legal = v.get('party_b_legal_person', '')
    party_b_phone = v.get('party_b_phone', '________________________')
    party_b_address = v.get('party_b_address', '________________________')
    party_b_bank = v.get('party_b_bank', '________________________')
    party_b_account = v.get('party_b_account', '________________________')
    # 项目负责人
    planner = v.get('planner', '')
    designer = v.get('designer', '')
    pm = v.get('project_manager', '')
    supervisor = v.get('supervisor', '')
    # 服务信息
    service_type = v.get('service_type', '纯设计服务')
    start_date = str(contract.start_date or '')[:10] if contract.start_date else ''
    end_date = str(contract.end_date or '')[:10] if contract.end_date else ''
    project_address = v.get('project_address', '________________________')
    # 合同类型
    contract_type_map = {'design': '室内全案设计服务', 'construction': '装修施工服务', 'all_in': '全案落地服务', 'soft': '软装搭配服务'}
    contract_type_text = contract_type_map.get(contract.contract_type, contract.contract_type or '室内全案设计服务')

    # 付款计划HTML
    payment_rows = ''
    for i, p in enumerate(payments, 1):
        pct = float(p.percentage or 0)
        amt = float(p.amount or 0)
        planned = str(p.planned_date or '')[:10] if p.planned_date else ''
        payment_rows += f'<li>{p.phase}（{pct}%）：{planned} 支付 {amt:,.0f} 元；</li>'
    payment_list = payment_rows if payment_rows else '<li>首期款（50%）：合同签订当日支付；</li><li>中期款（30%）：效果图确认后支付；</li><li>尾款（20%）：施工图交付后支付。</li>'

    # 特殊约定
    special_terms = []
    for i in range(1, 4):
        term = v.get(f'special_term_{i}', '').strip()
        if term: special_terms.append(f'<li>{term}</li>')
    special_terms_html = ''.join(special_terms) if special_terms else '<li>无</li>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>设记家 - {contract_type_text}合同</title>
<style>
  body {{ font-family: SimSun, Songti SC, "宋体", serif; font-size: 14px; color: #000; margin: 0; padding: 30px 50px; line-height: 1.8; }}
  .contract-wrap {{ max-width: 750px; margin: 0 auto; }}
  .brand {{ text-align: center; font-size: 16px; font-weight: bold; letter-spacing: 8px; margin-bottom: 4px; }}
  h1 {{ text-align: center; font-size: 18px; font-weight: bold; margin: 0 0 10px; letter-spacing: 2px; }}
  .contract-no {{ text-align: right; font-size: 12px; color: #333; margin-bottom: 24px; }}
  .party-section {{ margin: 16px 0; }}
  .party-title {{ font-weight: bold; margin-bottom: 6px; }}
  .party-info p {{ margin: 2px 0; font-size: 13px; }}
  .legal-basis {{ margin: 20px 0; font-size: 13px; text-indent: 2em; line-height: 1.9; }}
  .article {{ margin: 18px 0; }}
  .article-title {{ font-weight: bold; margin-bottom: 8px; }}
  .article-content {{ font-size: 13px; line-height: 1.9; }}
  .article-content p {{ margin: 4px 0; text-indent: 2em; }}
  .article-content ul {{ margin: 4px 0 4px 2em; padding: 0; list-style: none; }}
  .article-content li {{ margin: 2px 0; }}
  .sign-area {{ margin-top: 50px; display: flex; justify-content: space-between; }}
  .sign-block {{ width: 46%; }}
  .sign-block p {{ margin: 6px 0; font-size: 13px; }}
  .sign-block .company {{ font-weight: bold; margin-top: 10px; }}
  @media print {{
    body {{ padding: 20px 40px; }}
    @page {{ margin: 15mm; size: A4; }}
  }}
</style>
</head>
<body>
<div class="contract-wrap">
  <div class="brand">设记家</div>
  <h1>{contract_type_text}合同</h1>
  <p class="contract-no">合同编号：{contract.contract_no}</p>

  <div class="party-section">
    <div class="party-title">甲方（委托方）</div>
    <div class="party-info">
      <p>姓名：{party_a_name}</p>
      <p>身份证号：{party_a_id_card}</p>
      <p>联系电话：{party_a_phone}</p>
      <p>项目地址：{project_address}</p>
      <p>建筑面积：{party_a_area} ㎡</p>
    </div>
  </div>

  <div class="party-section">
    <div class="party-title">乙方（受托方）</div>
    <div class="party-info">
      <p>单位名称：{party_b_company}</p>
      <p>设计师：{designer if designer else '________________________'}</p>
      <p>联系电话：{party_b_phone}</p>
      <p>地址：{party_b_address}</p>
    </div>
  </div>

  <div class="legal-basis">
    依据《中华人民共和国民法典》《住宅室内装饰装修管理办法》等相关法律法规，甲乙双方本着平等自愿、公平诚信原则，就甲方委托乙方提供{contract_type_text}达成如下协议，共同遵守。
  </div>

  <div class="article">
    <div class="article-title">一、服务内容与成果标准</div>
    <div class="article-content">
      <p><b>1.1 服务性质</b></p>
      <p>本合同为{contract_type_text}合同，服务范围以合同约定为准；后期相关服务可另行签订专项协议对接。</p>
      <p><b>1.2 设计成果交付标准</b></p>
      <ul>
        <li>1. 效果图：室内每个空间静态效果图2张/空间；客厅、主卧各提供720°VR全景效果图1套；</li>
        <li>2. 施工图（全套CAD+PDF）：平面规划图、土建改造图、水电改造图、地面铺装图、天花布局图、立面设计图、家具布局图等；</li>
        <li>3. 交付形式：电子版（PDF+CAD源文件）+ 纸质版2份，甲乙双方各执1份。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">二、设计费用与支付方式</div>
    <div class="article-content">
      <p><b>2.1 设计费总额</b></p>
      <p>人民币：<b>{total:,.0f} 元</b>（大写：<b>{total_rmb}</b>），固定包干价，不含税、不含后期落地服务费用。</p>
      <p><b>2.2 支付节点</b></p>
      <ul>
        {payment_list}
      </ul>
      <p><b>2.3 收款账户</b></p>
      <p>户名：{party_b_bank}</p>
      <p>账号：{party_b_account}</p>
      <p>开户行：________________________</p>
      <p>甲方转账即视为完成付款义务。</p>
    </div>
  </div>

  <div class="article">
    <div class="article-title">三、设计周期</div>
    <div class="article-content">
      <ul>
        <li>1. 自乙方收到首期款之日起计算周期；</li>
        <li>2. 效果图交付：________个工作日；</li>
        <li>3. 施工图交付：效果图确认后________个工作日；</li>
        <li>4. 甲方逾期确认，交付周期相应顺延。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">四、现场技术服务</div>
    <div class="article-content">
      <ul>
        <li>1. 硬装施工期间，设计师{designer if designer else '________'}到现场提供：施工技术交底、图纸核对与落地指导、施工质量监督与检验；</li>
        <li>2. 现场服务次数：不低于5次；</li>
        <li>3. 重大节点可双方协商增加到场次数。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">五、后期服务预留接口</div>
    <div class="article-content">
      <p>本合同为设计合同，甲方后续如需以下服务，另行签订专项协议：</p>
      <ul>
        <li>1. 《全屋定制设计与落地服务协议》</li>
        <li>2. 《成品家具选型与采购服务协议》</li>
        <li>3. 《软装饰品搭配与陈设服务协议》</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">六、双方权利与义务</div>
    <div class="article-content">
      <p><b>6.1 甲方义务</b></p>
      <ul>
        <li>1. 按时支付设计费，逾期则工期顺延；</li>
        <li>2. 及时提供房屋资料、物业要求、清晰对接设计需求；</li>
        <li>3. 设计成果确认时限不超过3个工作日，逾期视为确认。</li>
      </ul>
      <p><b>6.2 乙方义务</b></p>
      <ul>
        <li>1. 按约定标准交付完整、可落地的设计成果；</li>
        <li>2. 按约定到场完成技术交底与质量监督；</li>
        <li>3. 对甲方信息及设计图纸保密。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">七、设计变更</div>
    <div class="article-content">
      <ul>
        <li>1. 小范围优化调整免费；</li>
        <li>2. 重大方案变更，双方另行协商周期与增补费用；</li>
        <li>3. 所有变更以书面/微信确认为准，口头无效。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">八、知识产权</div>
    <div class="article-content">
      <ul>
        <li>1. 设计成果知识产权归乙方所有；</li>
        <li>2. 甲方付清全款后获得本项目唯一使用权，不得用于其他项目或转售。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">九、违约责任</div>
    <div class="article-content">
      <ul>
        <li>1. 甲方逾期付款：每日按未付金额0.05%支付违约金；逾期超15日，乙方有权暂停服务；</li>
        <li>2. 乙方逾期交付：每日按设计费总额0.05%支付违约金；</li>
        <li>3. 单方无故解约：违约方支付设计费总额20%作为违约金。</li>
      </ul>
    </div>
  </div>

  <div class="article">
    <div class="article-title">十、争议解决</div>
    <div class="article-content">
      <p>协商不成，向项目所在地人民法院提起诉讼。</p>
    </div>
  </div>

  <div class="article">
    <div class="article-title">十一、附则</div>
    <div class="article-content">
      <ul>
        <li>1. 本合同一式两份，甲乙双方各执一份，签字生效；</li>
        <li>2. 沟通记录、确认单、交付凭证均为本合同有效附件；</li>
        <li>3. 后期落地服务以补充协议为准。</li>
      </ul>
    </div>
  </div>

  <div class="sign-area">
    <div class="sign-block">
      <p><b>甲方（签字）：</b>________________________</p>
      <p>日期：______年____月____日</p>
    </div>
    <div class="sign-block">
      <p><b>乙方（签字/盖章）：</b>________________________</p>
      <p class="company">{party_b_company}</p>
      <p>全案设计师：</p>
      <p>日期：______年____月____日</p>
    </div>
  </div>
</div>
</body>
</html>"""
    return html

@contract_bp.route('/<int:id>/preview-full', methods=['GET'])
@jwt_required_v2
def preview_full_contract(current_user, id):
    """生成完整合同正文HTML（用于打印预览）- 基于全功能成交合同范本"""
    contract = Contract.query.get_or_404(id)
    customer = Customer.query.get(contract.customer_id)
    payments = ContractPayment.query.filter_by(contract_id=id).order_by(ContractPayment.planned_date).all()
    v = contract.variables or {}
    html = _generate_contract_html(contract, customer, payments, v)
    return jsonify({'code': 200, 'data': {'html': html}})


@contract_bp.route('/<int:id>/export-pdf', methods=['GET'])
@jwt_required_v2
def export_contract_pdf(current_user, id):
    """导出合同PDF（使用weasyprint生成真正的PDF文件）"""
    if not WEASYPRINT_AVAILABLE:
        return jsonify({'code': 500, 'message': 'weasyprint未安装，无法生成PDF', 'data': None}), 500
    
    contract = Contract.query.get_or_404(id)
    customer = Customer.query.get(contract.customer_id)
    payments = ContractPayment.query.filter_by(contract_id=id).order_by(ContractPayment.planned_date).all()
    v = contract.variables or {}
    
    # 生成HTML
    html_content = _generate_contract_html(contract, customer, payments, v)
    
    try:
        # 使用weasyprint将HTML转换为PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        # 创建BytesIO对象
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_file.seek(0)
        
        # 生成文件名
        filename = f"合同_{contract.contract_no}_{customer.name if customer else '未知'}.pdf"
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'code': 500, 'message': f'PDF生成失败: {str(e)}', 'data': None}), 500


@contract_bp.route('/export-pdf', methods=['POST'])
@jwt_required_v2
def export_contract_pdf_full(current_user):
    """旧版PDF导出接口（保持兼容）- 仍返回HTML"""

    # 甲方信息
    party_a_name = v.get('party_a_name', customer.name if customer else '')
    party_a_phone = v.get('party_a_phone', customer.phone if customer else '')
    party_a_id_card = v.get('party_a_id_card', '')
    party_a_area = v.get('party_a_area', '')
    party_a_address = v.get('party_a_address', '')
    # 乙方信息
    party_b_company = v.get('party_b_company', '成都术木家居设计有限公司')
    party_b_credit_code = v.get('party_b_credit_code', '91510107MA69NG2R92')
    party_b_legal = v.get('party_b_legal_person', '')
    party_b_phone = v.get('party_b_phone', '')
    party_b_bank = v.get('party_b_bank', '')
    party_b_account = v.get('party_b_account', '')
    # 项目负责人
    planner = v.get('planner', '')
    designer = v.get('designer', '')
    pm = v.get('project_manager', '')
    supervisor = v.get('supervisor', '')
    # 服务信息
    service_type = v.get('service_type', '')
    start_date = str(contract.start_date or '')[:10] if contract.start_date else ''
    end_date = str(contract.end_date or '')[:10] if contract.end_date else ''
    project_address = v.get('project_address', '')
    # 合同类型
    contract_type_map = {'design': '室内设计服务', 'construction': '装修施工服务', 'all_in': '全案落地服务', 'soft': '软装搭配服务'}
    contract_type_text = contract_type_map.get(contract.contract_type, contract.contract_type or '')

    # 付款计划HTML
    payment_rows = ''
    total_pct = 0
    for i, p in enumerate(payments, 1):
        pct = float(p.percentage or 0)
        amt = float(p.amount or 0)
        planned = str(p.planned_date or '')[:10] if p.planned_date else ''
        status_map = {'paid': '已完成', 'pending': '待付', 'overdue': '已逾期'}
        payment_rows += f'<tr><td>{i}</td><td>{p.phase}</td><td>{pct}%</td><td>¥{amt:,.2f}</td><td>{planned}</td><td>{status_map.get(p.status, p.status)}</td></tr>'
        total_pct += pct
    if payment_rows:
        payment_table = f'<table class="payment-table"><thead><tr><th>序号</th><th>阶段</th><th>比例</th><th>金额</th><th>计划日期</th><th>状态</th></tr></thead><tbody>{payment_rows}</tbody></table>'
    else:
        payment_table = '<p>暂无付款计划</p>'

    # 特殊约定
    special_terms = []
    for i in range(1, 4):
        term = v.get(f'special_term_{i}', '').strip()
        if term: special_terms.append(f'<p>第{i}条：{term}</p>')
    special_terms_html = ''.join(special_terms) if special_terms else '<p>无</p>'

    # 额外条款
    extra_clause = v.get('extra_clause', '').strip()

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: SimSun, Songti SC, serif; font-size: 14px; color: #000; margin: 0; padding: 20px 40px; line-height: 1.8; }}
  .contract-wrap {{ max-width: 800px; margin: 0 auto; }}
  h1 {{ text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 6px; letter-spacing: 4px; }}
  .contract-no {{ text-align: right; font-size: 12px; color: #666; margin-bottom: 20px; }}
  .section-title {{ font-size: 15px; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 4px; margin: 14px 0 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0; }}
  table, th, td {{ border: 1px solid #000; }}
  th, td {{ padding: 5px 8px; font-size: 13px; }}
  th {{ background: #f5f5f5; font-weight: normal; text-align: left; }}
  .info-table td:first-child {{ font-weight: normal; width: 90px; background: #f9f9f9; }}
  .info-table td:nth-child(2) {{ width: 35%; }}
  .sign-area {{ margin-top: 40px; display: flex; justify-content: space-between; }}
  .sign-block {{ width: 45%; }}
  .sign-block p {{ margin: 4px 0; }}
  @media print {{ body {{ padding: 0; }} @page {{ margin: 20px; }} }}
</style>
</head>
<body>
<div class="contract-wrap">
  <h1>设 计 合 同</h1>
  <p class="contract-no">合同编号：{contract.contract_no}</p>

  <!-- 基本信息 -->
  <div class="section-title">一、基本信息</div>
  <table class="info-table">
    <tr><td>委托方（甲方）</td><td>{party_a_name}</td><td>联系方式</td><td>{party_a_phone}</td></tr>
    <tr><td>受托方（乙方）</td><td>{party_b_company}</td><td>联系方式</td><td>{party_b_phone}</td></tr>
    <tr><td>服务类型</td><td>{contract_type_text}</td><td>合同总金额</td><td><b>人民币 {total:,.2f} 元（{total_rmb}）</b></td></tr>
    <tr><td>项目地址</td><td colspan="3">{project_address}</td></tr>
    <tr><td>服务周期</td><td colspan="3">{start_date} 至 {end_date}</td></tr>
  </table>

  <!-- 甲方信息 -->
  <div class="section-title">二、甲方信息</div>
  <table class="info-table">
    <tr><td>甲方姓名</td><td>{party_a_name}</td><td>身份证号</td><td>{party_a_id_card}</td></tr>
    <tr><td>联系电话</td><td>{party_a_phone}</td><td>房屋面积</td><td>{party_a_area} ㎡</td></tr>
    <tr><td>通讯地址</td><td colspan="3">{party_a_address}</td></tr>
  </table>

  <!-- 乙方信息 -->
  <div class="section-title">三、乙方信息</div>
  <table class="info-table">
    <tr><td>公司名称</td><td>{party_b_company}</td><td>统一社会信用代码</td><td>{party_b_credit_code}</td></tr>
    <tr><td>法定代表人</td><td>{party_b_legal}</td><td>联系电话</td><td>{party_b_phone}</td></tr>
    <tr><td>收款账户</td><td>{party_b_bank}</td><td>账号</td><td>{party_b_account}</td></tr>
  </table>

  <!-- 项目负责人 -->
  <div class="section-title">四、项目负责人</div>
  <table class="info-table">
    <tr><td>规划师</td><td>{planner}</td><td>设计师</td><td>{designer}</td></tr>
    <tr><td>项目经理</td><td>{pm}</td><td>工程监理</td><td>{supervisor}</td></tr>
  </table>

  <!-- 付款计划 -->
  <div class="section-title">五、付款计划</div>
  {payment_table}

  <!-- 特殊约定 -->
  <div class="section-title">六、特殊约定</div>
  {special_terms_html}

  <!-- 附加条款 -->

  <!-- 签署区 -->
  <div class="sign-area">
    <div class="sign-block">
      <p><b>甲方（签章）：</b></p>
      <p>甲方签字：________________</p>
      <p>签署日期：________________</p>
    </div>
    <div class="sign-block">
      <p><b>乙方（签章）：</b></p>
      <p>{party_b_company}</p>
      <p>签署日期：________________</p>
    </div>
  </div>

  <!-- 附件 -->
  <div class="section-title">附件</div>
  <div class="attachment-list">
    <p>附件清单以实际签约文件为准</p>
  </div>
</div>
</body>
</html>'''

    return jsonify({'code': 200, 'data': {'html': html}})


@contract_bp.route('', methods=['POST'])
@jwt_required_v2
def create_contract(current_user):
    """创建合同"""
    data = request.get_json()

    # 生成合同编号
    today = date.today().strftime('%Y%m%d')
    count = Contract.query.filter(
        Contract.contract_no.like(f'HT{today}%')
    ).count()
    contract_no = f"HT{today}{count+1:04d}"

    # 处理付款计划
    payment_schedule = data.get('payment_schedule', [])
    for item in payment_schedule:
        item['status'] = 'pending'

    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'code': 400, 'message': '请选择客户', 'data': None})

    # 支持自定义状态（草稿/待审核）
    contract_status = data.get('status', 'draft')

    contract = Contract(
        tenant_id=current_user.get('tenant_id', '0'),
        contract_no=contract_no,
        customer_id=customer_id,
        template_id=data.get('template_id'),
        contract_type=data.get('contract_type'),
        title=data.get('title', f'Contract-{contract_no}'),
        variables=data.get('variables', {}),
        total_amount=data.get('total_amount', 0),
        design_fee=data.get('design_fee', 0),
        construction_fee=data.get('construction_fee', 0),
        material_fee=data.get('material_fee', 0),
        soft_fee=data.get('soft_fee', 0),
        payment_schedule=payment_schedule,
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        status=contract_status,
        creator_id=current_user.get('id'),
        manager_id=data.get('manager_id'),
        remark=data.get('remark')
    )

    db.session.add(contract)
    db.session.flush()

    # 创建付款记录
    for item in payment_schedule:
        planned_date_str = item.get('planned_date')
        planned_date = None
        if planned_date_str:
            from datetime import datetime
            if isinstance(planned_date_str, str):
                planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
            else:
                planned_date = planned_date_str
        
        payment = ContractPayment(
            contract_id=contract.id,
            phase=item.get('phase'),
            percentage=item.get('percentage', 0),
            amount=item.get('amount', 0),
            planned_date=planned_date,
            status='pending'
        )
        db.session.add(payment)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/preview', methods=['POST'])
@jwt_required_v2
def preview_contract(current_user):
    """预览合同（不保存）"""
    data = request.get_json()
    
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'code': 400, 'message': '请选择客户', 'data': None})
    
    from app.models.customer import Customer
    customer = Customer.query.get(customer_id)
    
    # 构建预览数据
    variables = data.get('variables', {})
    preview_data = {
        'contract_no': '预览-' + date.today().strftime('%Y%m%d%H%M%S'),
        'customer': {'name': customer.name, 'phone': customer.phone} if customer else None,
        'title': data.get('title', ''),
        'contract_type': data.get('contract_type'),
        'total_amount': data.get('total_amount', 0),
        'design_fee': data.get('design_fee', 0),
        'construction_fee': data.get('construction_fee', 0),
        'material_fee': data.get('material_fee', 0),
        'soft_fee': data.get('soft_fee', 0),
        'payment_schedule': data.get('payment_schedule', []),
        'payments': data.get('payment_schedule', []),  # 兼容前端detailDrawer显示
        'start_date': data.get('start_date'),
        'end_date': data.get('end_date'),
        'variables': variables,  # 包含所有扩展字段
        'status': 'draft'
    }
    return jsonify({'code': 200, 'message': 'ok', 'data': preview_data})


@contract_bp.route('/export-pdf', methods=['POST'])
@jwt_required_v2
def export_contract_pdf_simple(current_user):
    """导出合同PDF"""
    data = request.get_json()
    
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'code': 400, 'message': '请先选择客户', 'data': None})
    
    from app.models.customer import Customer
    customer = Customer.query.get(customer_id)
    
    # 生成合同内容
    title = data.get('title', '装修合同')
    total = data.get('total_amount', 0)
    design_fee = data.get('design_fee', 0)
    construction_fee = data.get('construction_fee', 0)
    material_fee = data.get('material_fee', 0)
    soft_fee = data.get('soft_fee', 0)
    remark = data.get('remark', '')
    
    # 构建HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{ font-family: SimSun; font-size: 14px; line-height: 1.8; }}
            .title {{ text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; }}
            .section {{ margin: 15px 0; }}
            .label {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
            .amount {{ text-align: right; }}
            .total-row {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="title">{title}</div>
        
        <div class="section">
            <span class="label">客户：</span>{customer.name if customer else ''}<br>
            <span class="label">电话：</span>{customer.phone if customer else ''}
        </div>
        
        <div class="section">
            <span class="label">合同金额：</span>¥{total:,.2f} 元
        </div>
        
        <div class="section">
            <span class="label">费用明细：</span>
            <table>
                <tr><td>设计费</td><td class="amount">¥{design_fee:,.2f}</td></tr>
                <tr><td>施工费</td><td class="amount">¥{construction_fee:,.2f}</td></tr>
                <tr><td>材料费</td><td class="amount">¥{material_fee:,.2f}</td></tr>
                <tr><td>软装费</td><td class="amount">¥{soft_fee:,.2f}</td></tr>
                <tr class="total-row"><td>合计</td><td class="amount">¥{total:,.2f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <span class="label">备注：</span>{remark}
        </div>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333;">
            <div style="display: flex; justify-content: space-between;">
                <span>甲方（签字）：___________</span>
                <span>乙方（签字）：___________</span>
            </div>
            <div style="margin-top: 20px;">
                <span>日期：___________</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 使用weasyprint或其他方式生成PDF
    # 这里返回HTML，前端可iframe预览或使用浏览器打印
    import io
    import base64
    
    # 简单起见，返回HTML的base64编码供前端下载
    html_b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    return jsonify({
        'code': 200,
        'message': 'PDF内容生成成功',
        'data': {
            'html': html_content,
            'filename': f"合同_{title}.html"
        }
    })


@contract_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_contract(current_user, id):
    """更新合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    # 只有草稿状态可以修改基本信息
    if contract.status == 'draft':
        fields = ['title', 'content', 'variables', 'total_amount', 'design_fee',
                  'construction_fee', 'material_fee', 'soft_fee', 'start_date',
                  'end_date', 'manager_id', 'remark']
        for field in fields:
            if field in data:
                setattr(contract, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required_v2
def submit_contract(current_user, id):
    """提交合同（草稿->待签署）"""
    contract = Contract.query.get_or_404(id)

    if contract.status != 'draft':
        return jsonify({'code': 400, 'message': '只有草稿状态可以提交'}), 400

    contract.status = 'pending'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '提交成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/sign', methods=['POST'])
@jwt_required_v2
def sign_contract(current_user, id):
    """签署合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    signer = data.get('signer')  # customer/company

    if signer == 'customer':
        contract.signed_by_customer = True
        contract.customer_sign_date = datetime.utcnow()
    elif signer == 'company':
        contract.signed_by_company = True
        contract.company_sign_date = datetime.utcnow()

    # 双方都签署后，状态变为已签署
    if contract.signed_by_customer and contract.signed_by_company:
        contract.status = 'signed'
        contract.signed_date = date.today()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '签署成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/execute', methods=['POST'])
@jwt_required_v2
def execute_contract(current_user, id):
    """开始执行合同"""
    contract = Contract.query.get_or_404(id)

    if contract.status != 'signed':
        return jsonify({'code': 400, 'message': '合同未签署'}), 400

    contract.status = 'executing'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '已开始执行',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/complete', methods=['POST'])
@jwt_required_v2
def complete_contract(current_user, id):
    """完成合同"""
    contract = Contract.query.get_or_404(id)

    contract.status = 'completed'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '合同已完成',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required_v2
def cancel_contract(current_user, id):
    """取消合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    contract.status = 'cancelled'

    # 记录变更
    change = ContractChange(
        contract_id=id,
        change_type='cancel',
        old_value={'status': contract.status},
        new_value={'status': 'cancelled'},
        reason=data.get('reason'),
        operator_id=current_user.get('id')
    )
    db.session.add(change)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '合同已取消',
        'data': contract.to_dict()
    })


# ========== 付款管理 ==========

@contract_bp.route('/<int:contract_id>/payments/<int:payment_id>/pay', methods=['POST'])
@jwt_required_v2
def record_payment(current_user, contract_id, payment_id):
    """记录付款"""
    payment = ContractPayment.query.get_or_404(payment_id)
    data = request.get_json()

    payment.status = 'paid'
    payment.actual_date = data.get('actual_date') or date.today()
    payment.payment_method = data.get('payment_method')
    payment.transaction_no = data.get('transaction_no')
    payment.receipt_url = data.get('receipt_url')
    payment.remark = data.get('remark')

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '付款记录成功',
        'data': payment.to_dict()
    })


# ========== 统计报表 ==========

@contract_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取合同统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 状态统计
    status_stats = db.session.query(
        Contract.status,
        db.func.count(Contract.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Contract.status).all()

    # 类型统计
    type_stats = db.session.query(
        Contract.contract_type,
        db.func.count(Contract.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Contract.contract_type).all()

    # 金额统计
    amount_stats = db.session.query(
        db.func.sum(Contract.total_amount)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).first()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Contract.query.filter(
        Contract.tenant_id == tenant_id,
        Contract.is_deleted == False,
        Contract.created_at >= current_month
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'by_status': {s: c for s, c in status_stats},
            'by_type': {t: c for (t, c) in type_stats if t is not None},
            'total_amount': float(amount_stats[0]) if amount_stats[0] else 0,
            'new_this_month': new_this_month
        }
    })


# ========== 选项数据 ==========

@contract_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取合同相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'contract_types': [{'value': v, 'label': l} for v, l in CONTRACT_TYPES],
            'status_list': [{'value': v, 'label': l} for v, l in CONTRACT_STATUS],
            'payment_phases': [{'value': v, 'label': l} for v, l in PAYMENT_PHASES],
        }
    })


# ========== 员工选择（项目负责人） ==========

@contract_bp.route('/employees-for-team', methods=['GET'])
@jwt_required_v2
def get_employees_for_team(current_user):
    """获取可用于项目负责人的员工列表（按岗位分组）"""
    employees = Emp.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False,
        status='active'
    ).order_by(Emp.department_id, Emp.position_id, Emp.name).all()
    
    result = []
    for e in employees:
        result.append({
            'id': e.id,
            'name': e.name,
            'phone': e.phone or '',
            'title': e.title or '',
            'position_id': e.position_id,
            'department_id': e.department_id,
        })
    
    return jsonify({'code': 200, 'data': result})


# ========== 模板应用 ==========

@contract_bp.route('/templates/<int:id>/apply', methods=['GET'])
@jwt_required_v2
def apply_template(current_user, id):
    """获取模板的变量数据，用于前端一键填充表单"""
    template = ContractTemplate.query.get_or_404(id)
    
    import json
    variables = template.variables
    if isinstance(variables, str):
        try:
            variables = json.loads(variables)
        except:
            variables = {}
    
    return jsonify({
        'code': 200,
        'data': {
            'id': template.id,
            'name': template.name,
            'contract_type': template.contract_type,
            'variables': variables or {},
        }
    })
