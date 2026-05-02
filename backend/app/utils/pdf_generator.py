"""
PDF Generation Service for Quote Management
Generates two versions: customer (full) and visitor (desensitized)
"""
import os
import json
from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Register Chinese fonts
FONT_DIR = r'C:\Windows\Fonts'
try:
    pdfmetrics.registerFont(TTFont('SimHei', os.path.join(FONT_DIR, 'simhei.ttf')))
    pdfmetrics.registerFont(TTFont('SimSun', os.path.join(FONT_DIR, 'simsun.ttc')))
    CN_FONT = 'SimHei'
    CN_FONT_BODY = 'SimSun'
except:
    CN_FONT = 'Helvetica-Bold'
    CN_FONT_BODY = 'Helvetica'

# Brand colors
BRAND_BROWN = HexColor('#8B5A2B')
BRAND_GOLD = HexColor('#C8A96E')
LIGHT_GRAY = HexColor('#F5F5F5')
MID_GRAY = HexColor('#999999')
DARK_TEXT = HexColor('#333333')

UPLOAD_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'upload'
))

# Category key to Chinese name mapping
CATEGORY_MAP = {
    'hard_material': '硬装主材',
    'construction': '施工服务',
    'installation': '安装服务',
    'delivery': '配送服务',
    'moving': '搬运服务',
    'design': '设计服务',
    'custom': '全屋定制',
    'furniture': '成品家具',
    'soft': '软装饰品',
    'equipment': '电气设备',
    'smart_home': '智能家居',
    'other': '其他',
}


def _build_styles():
    """Build paragraph styles for PDF"""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CNTitle', fontName=CN_FONT, fontSize=20, leading=28,
        textColor=BRAND_BROWN, alignment=TA_CENTER, spaceAfter=6*mm
    ))
    styles.add(ParagraphStyle(
        'CNSubTitle', fontName=CN_FONT, fontSize=12, leading=18,
        textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=10*mm
    ))
    styles.add(ParagraphStyle(
        'CNSection', fontName=CN_FONT, fontSize=13, leading=20,
        textColor=BRAND_BROWN, spaceBefore=8*mm, spaceAfter=4*mm
    ))
    styles.add(ParagraphStyle(
        'CNBody', fontName=CN_FONT_BODY, fontSize=9, leading=14,
        textColor=DARK_TEXT
    ))
    styles.add(ParagraphStyle(
        'CNSmall', fontName=CN_FONT_BODY, fontSize=8, leading=12,
        textColor=MID_GRAY
    ))
    styles.add(ParagraphStyle(
        'CNTotal', fontName=CN_FONT, fontSize=14, leading=20,
        textColor=BRAND_BROWN, alignment=TA_RIGHT, spaceBefore=4*mm
    ))
    return styles


def _get_quote_items_by_category(items):
    """Group items by category_level1"""
    grouped = {}
    for item in items:
        cat = item.category_level1 or '其他'
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)
    return grouped


def _build_cover_page(story, quote, styles, is_visitor=False):
    """Build cover page"""
    story.append(Spacer(1, 40*mm))

    brand = '帝标·设记家'
    story.append(Paragraph(brand, styles['CNTitle']))

    doc_type = '报价单' if not is_visitor else '价格参考'
    story.append(Paragraph(doc_type, styles['CNSubTitle']))

    story.append(Spacer(1, 20*mm))

    info_data = [
        ['报价编号', quote.quote_no or ''],
    ]

    if not is_visitor:
        cust_name = getattr(quote, 'customer_name', '') or ''
        if hasattr(quote, 'customer') and quote.customer:
            cust_name = quote.customer.name or ''
        if cust_name:
            info_data.append(['客户', cust_name])

    info_data.append(['日期', datetime.now().strftime('%Y-%m-%d')])

    if quote.expire_date:
        info_data.append(['有效期至', quote.expire_date.strftime('%Y-%m-%d')])

    info_table = Table(info_data, colWidths=[40*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), CN_FONT),
        ('FONTNAME', (1, 0), (1, -1), CN_FONT_BODY),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), BRAND_BROWN),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_TEXT),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)

    if not is_visitor and quote.service_team:
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph('服务团队', styles['CNSection']))
        team_data = [['角色', '姓名', '联系电话']]
        for member in (quote.service_team or []):
            team_data.append([
                member.get('role_name', ''),
                member.get('name', ''),
                member.get('phone', ''),
            ])
        team_table = Table(team_data, colWidths=[40*mm, 40*mm, 50*mm])
        team_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_BROWN),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(team_table)

    story.append(PageBreak())


def _build_item_table_customer(items, cat_name, styles):
    """Build item table for customer version (full details with unit price)"""
    headers = ['名称', '规格', '品牌', '单位', '数量', '单价', '合计']
    data = [headers]

    cat_total = Decimal('0')
    for item in items:
        total = item.total_price or Decimal('0')
        cat_total += total
        data.append([
            item.name or '',
            item.spec or '',
            item.brand or '',
            item.unit or '',
            str(item.quantity or 0),
            '{:.2f}'.format(float(item.unit_price or 0)),
            '{:.2f}'.format(float(total)),
        ])

    data.append(['小计', '', '', '', '', '', '{:.2f}'.format(float(cat_total))])

    col_widths = [45*mm, 30*mm, 22*mm, 14*mm, 14*mm, 18*mm, 22*mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ('FONTNAME', (0, 0), (-1, 0), CN_FONT),
        ('FONTNAME', (0, 1), (-1, -1), CN_FONT_BODY),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BROWN),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('FONTNAME', (0, -1), (-1, -1), CN_FONT),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GRAY),
        ('SPAN', (0, -1), (5, -1)),
        ('ALIGN', (5, -1), (-1, -1), 'RIGHT'),
    ]

    table.setStyle(TableStyle(style_cmds))
    return table, cat_total


def _build_item_table_visitor(items, cat_name, styles):
    """Build item table for visitor version (no unit price, only subtotals)"""
    headers = ['名称', '规格', '材质', '数量']
    data = [headers]

    cat_total = Decimal('0')
    for item in items:
        total = item.total_price or Decimal('0')
        cat_total += total
        data.append([
            item.name or '',
            item.spec or '',
            item.brand or '',
            str(item.quantity or 0),
        ])

    data.append(['分类小计: ¥{:.2f}'.format(float(cat_total)), '', '', ''])

    col_widths = [55*mm, 40*mm, 30*mm, 20*mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ('FONTNAME', (0, 0), (-1, 0), CN_FONT),
        ('FONTNAME', (0, 1), (-1, -1), CN_FONT_BODY),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BROWN),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('SPAN', (0, -1), (-1, -1)),
        ('FONTNAME', (0, -1), (-1, -1), CN_FONT),
        ('TEXTCOLOR', (0, -1), (-1, -1), BRAND_BROWN),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GRAY),
    ]

    table.setStyle(TableStyle(style_cmds))
    return table, cat_total


def generate_quote_pdf(quote, items, is_visitor=False):
    """
    Generate a PDF for the given quote.

    Args:
        quote: Quote model instance
        items: list of QuoteItem instances
        is_visitor: if True, generate visitor version (no unit prices)

    Returns:
        str: relative path to the generated PDF file (from upload root)
    """
    styles = _build_styles()

    pdf_dir = os.path.join(UPLOAD_ROOT, 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    version = 'visitor' if is_visitor else 'customer'
    filename = 'quote_{}_{}_{}.pdf'.format(quote.quote_no or quote.id, version, timestamp)
    filepath = os.path.join(pdf_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm,
    )

    story = []

    _build_cover_page(story, quote, styles, is_visitor=is_visitor)

    grouped = _get_quote_items_by_category(items)

    grand_total = Decimal('0')

    cat_order = []
    if quote.category_summary:
        cat_order = list(quote.category_summary.keys())

    for cat in grouped:
        if cat not in cat_order:
            cat_order.append(cat)

    for cat_key in cat_order:
        cat_name = CATEGORY_MAP.get(cat_key, cat_key)

        if cat_key in grouped:
            cat_items = grouped[cat_key]
        else:
            continue

        story.append(Paragraph(cat_name, styles['CNSection']))

        if is_visitor:
            table, cat_total = _build_item_table_visitor(cat_items, cat_name, styles)
        else:
            table, cat_total = _build_item_table_customer(cat_items, cat_name, styles)

        grand_total += cat_total
        story.append(table)
        story.append(Spacer(1, 4*mm))

    story.append(Spacer(1, 10*mm))

    if is_visitor:
        total_label = '参考总价: ¥{:.2f}'.format(float(grand_total))
    else:
        total_label = '报价总计: ¥{:.2f}'.format(float(grand_total))

    story.append(Paragraph(total_label, styles['CNTotal']))

    if not is_visitor:
        fees_data = []
        if quote.management_fee and float(quote.management_fee) > 0:
            fees_data.append(['管理费', '{:.2f}'.format(float(quote.management_fee))])
        if quote.tax and float(quote.tax) > 0:
            fees_data.append(['税费', '{:.2f}'.format(float(quote.tax))])

        if fees_data:
            story.append(Spacer(1, 4*mm))
            fees_table = Table(fees_data, colWidths=[40*mm, 40*mm])
            fees_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), CN_FONT_BODY),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ]))
            story.append(fees_table)

        if quote.total_amount and float(quote.total_amount) > 0:
            final = '最终报价: ¥{:.2f}'.format(float(quote.total_amount))
            story.append(Spacer(1, 4*mm))
            story.append(Paragraph(final, styles['CNTotal']))

    story.append(Spacer(1, 15*mm))

    if is_visitor:
        footer = '以上价格仅供参考，实际报价以到店咨询为准。'
    else:
        footer = '本报价单有效期 {} 天，过期作废。'.format(quote.valid_days or 30)

    story.append(Paragraph(footer, styles['CNSmall']))

    doc.build(story)

    return 'pdf/{}'.format(filename)


def generate_both_pdfs(quote_id):
    """
    Generate both customer and visitor PDFs for a quote.
    Called when quote status changes to confirmed/signed.

    Returns:
        dict with customer_path and visitor_path (relative paths)
    """
    from app.models.quote import Quote, QuoteItem
    from app.models.case import CaseFile, CaseStudy
    from app import db

    quote = Quote.query.get(quote_id)
    if not quote:
        return None

    items = QuoteItem.query.filter_by(quote_id=quote_id).order_by(
        QuoteItem.category_level1, QuoteItem.sort_order
    ).all()

    if not items:
        return None

    customer_rel = generate_quote_pdf(quote, items, is_visitor=False)
    visitor_rel = generate_quote_pdf(quote, items, is_visitor=True)

    case = CaseStudy.query.filter_by(customer_id=quote.customer_id).first()

    result = {'customer_path': customer_rel, 'visitor_path': visitor_rel}

    if case:
        cf1 = CaseFile(
            case_id=case.id,
            file_type='pdf',
            file_name='报价单_{}_客户版.pdf'.format(quote.quote_no),
            file_url='/upload/{}'.format(customer_rel),
            has_watermark=False,
        )
        db.session.add(cf1)

        cf2 = CaseFile(
            case_id=case.id,
            file_type='pdf',
            file_name='报价单_{}_访客版.pdf'.format(quote.quote_no),
            file_url='/upload/{}'.format(visitor_rel),
            has_watermark=True,
        )
        db.session.add(cf2)

        db.session.commit()
        result['case_id'] = case.id

    return result


def auto_authorize_on_quote_confirm(quote_id):
    """
    Auto-authorize case when quote is confirmed.
    Sets owner_authorized=True and enable_public_workflow=True
    on the related CaseStudy.

    Returns:
        dict with authorization status or None if quote not found
    """
    from app.models.quote import Quote
    from app.models.case import CaseStudy
    from app import db

    quote = Quote.query.get(quote_id)
    if not quote:
        return None

    case = CaseStudy.query.filter_by(customer_id=quote.customer_id).first()
    if not case:
        return {'authorized': False, 'case_id': None, 'message': 'No case found for this customer'}

    if case.owner_authorized and case.enable_public_workflow:
        return {'authorized': True, 'case_id': case.id, 'message': 'Already authorized'}

    case.owner_authorized = True
    case.enable_public_workflow = True

    if case.building_id or case.workflow_id:
        case.is_real_case = True

    db.session.commit()

    return {
        'authorized': True,
        'case_id': case.id,
        'message': 'Case auto-authorized from quote confirmation',
        'is_real_case': case.is_real_case,
    }
