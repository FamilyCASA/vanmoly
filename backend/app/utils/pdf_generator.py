# -*- coding: utf-8 -*-
"""
PDF Generation Service for Quote Management (v3.0 - 按规范文档四页结构)
Generates two versions: customer (full) and visitor (desensitized)
"""
import os
import math
from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ─── Font registration ────────────────────────────────────────────────────────
FONT_DIR = r'C:\Windows\Fonts'
try:
    pdfmetrics.registerFont(TTFont('SimHei', os.path.join(FONT_DIR, 'simhei.ttf')))
    pdfmetrics.registerFont(TTFont('SimSun', os.path.join(FONT_DIR, 'simsun.ttc')))
    CN_FONT = 'SimHei'
    CN_FONT_BODY = 'SimSun'
except Exception:
    CN_FONT = 'Helvetica-Bold'
    CN_FONT_BODY = 'Helvetica'

# ─── Brand colours ────────────────────────────────────────────────────────────
BRAND_BROWN   = HexColor('#8B5A2B')
BRAND_GOLD    = HexColor('#C8A96E')
LIGHT_GRAY    = HexColor('#F5F5F5')
MID_GRAY      = HexColor('#999999')
DARK_TEXT     = HexColor('#333333')
GREEN_HEADER  = HexColor('#E8F5E9')
WATERMARK_CLR = HexColor('#D4C5B0')

# ─── Path ────────────────────────────────────────────────────────────────────
UPLOAD_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'upload'
))

# ─── Category key → Chinese display name ────────────────────────────────────
CAT_MAP = {
    # new DB 7-category keys
    'hard_material':  '硬装主材',
    'construction':   '硬装施工服务',
    'custom':         '固装家具',
    'furniture':      '成品家具',
    'soft':           '软装饰品',
    'design':         '全案服务',
    'installation':   '硬装施工服务',
    'delivery':       '其他辅助物料及服务',
    'other':          '其他辅助物料及服务',
    'moving':         '其他辅助物料及服务',
    'equipment':      '电气设备',
    'smart_home':     '智能家居',
    # old English values in quotes.db
    'Custom Furniture':   '固装家具',
    'Finished Furniture':  '成品家具',
    'Soft Furnishing':     '软装饰品',
    'Customized Furniture': '固装家具',
    'Standard Furniture':   '成品家具',
}

# ─── Room ordering (by user-specified sequence) ──────────────────────────────
ROOM_ORDER = [
    '客厅', 'Living Room',
    '餐厅', 'Dining Room',
    '主卧', 'Master Bedroom',
    '次卧', 'Guest Bedroom', 'Secondary Bedroom',
    '儿童房', "Kids' Room", "Children's Bedroom",
    '老人房', 'Senior Bedroom', 'Elderly Room',
    '书房', '工作间', 'Study', 'Home Office',
    '中厨', 'Chinese Kitchen',
    '西厨', 'Western Kitchen',
    '开放式厨房', 'Open Kitchen',
    '主卫', 'Master Bathroom',
    '客卫', 'Guest Bathroom',
    '公卫（公寓）', 'Common Bathroom', '公卫（住宅内）',
    '干湿分离卫生间', 'Wet-Dry Separate Bathroom',
    '玄关', 'Foyer', 'Entryway',
    '入户花园', 'Entry Garden', 'Porch Garden',
    '生活阳台', 'Service Balcony',
    '休闲阳台', 'Leisure Balcony',
    '观景阳台', 'View Balcony', 'Scenic Balcony',
    '过道', '走廊', 'Passageway', 'Corridor',
    '步入式衣帽间', 'Walk-in Closet',
    '嵌入式衣帽间', 'Built-in Closet',
    '储藏室', '杂物间', 'Storage Room', 'Utility Room',
    '阁楼', 'Attic', 'Loft',
    '地下室', 'Basement',
    '影音室', '家庭影院', 'Home Theater', 'Media Room',
    '健身室', '瑜伽室', 'Home Gym', 'Yoga Room',
    '茶室', '棋牌室', 'Tea Room', 'Chess & Card Room',
    '琴房', '画室', 'Music Room', 'Art Studio',
    '保姆房', "Maid's Room", "Nanny's Room",
    '儿童活动区', "Kids' Play Area", "Children's Activity Zone",
    '老人护理间', 'Elderly Care Room',
    '宠物房', 'Pet Room',
    '阳光房', 'Sunroom', 'Solarium',
    '入户花厅', 'Entry Hall with Garden', 'Foyer Garden',
    '空中花园', 'Sky Garden', 'Rooftop Garden',
    '酒窖', 'Wine Cellar',
    '雪茄房', 'Cigar Room',
    '冥想室', 'Meditation Room',
    '私人会所', 'Private Clubhouse',
    '设备间', 'Equipment Room',
    # fallback groups
    '全屋', '全屋服务',
    '厨房', 'Kitchen',
    '阳台', 'Balcony',
]


def _room_sort_key(name):
    """Return (priority, display_name) for a room name."""
    n = name or ''
    for i, alias in enumerate(ROOM_ORDER):
        if alias.lower() == n.strip().lower():
            return (i, name)
    return (999, name)


def _cat_display(key):
    """Return Chinese display name for a category key."""
    return CAT_MAP.get(key, key)


def _ymoney(v):
    """Format as ¥X,XXX.XX"""
    return '¥{:.2f}'.format(float(v or 0))


def _build_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('WMTxt',    fontName=CN_FONT, fontSize=50, leading=60,
                          textColor=WATERMARK_CLR, alignment=TA_CENTER))
    s.add(ParagraphStyle('CNTitle',  fontName=CN_FONT, fontSize=22, leading=30,
                          textColor=BRAND_BROWN, alignment=TA_CENTER, spaceAfter=4*mm))
    s.add(ParagraphStyle('CNSubT',    fontName=CN_FONT, fontSize=13, leading=18,
                          textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=6*mm))
    s.add(ParagraphStyle('CNSmall',  fontName=CN_FONT_BODY, fontSize=8, leading=12,
                          textColor=MID_GRAY))
    s.add(ParagraphStyle('CNSec',     fontName=CN_FONT, fontSize=12, leading=18,
                          textColor=BRAND_BROWN, spaceBefore=6*mm, spaceAfter=2*mm))
    s.add(ParagraphStyle('CNBody',    fontName=CN_FONT_BODY, fontSize=9, leading=14,
                          textColor=DARK_TEXT))
    s.add(ParagraphStyle('CNTotal',   fontName=CN_FONT, fontSize=14, leading=20,
                          textColor=BRAND_BROWN, alignment=TA_RIGHT, spaceBefore=4*mm))
    s.add(ParagraphStyle('CNGrand',   fontName=CN_FONT, fontSize=16, leading=24,
                          textColor=BRAND_BROWN, alignment=TA_CENTER,
                          spaceBefore=6*mm, spaceAfter=6*mm))
    s.add(ParagraphStyle('CNPrinci',  fontName=CN_FONT, fontSize=14, leading=24,
                          textColor=BRAND_BROWN, alignment=TA_CENTER))
    s.add(ParagraphStyle('CNPrinciB', fontName=CN_FONT, fontSize=18, leading=28,
                          textColor=BRAND_BROWN, alignment=TA_CENTER,
                          spaceBefore=10*mm, spaceAfter=10*mm))
    return s


# ─── Cover page ──────────────────────────────────────────────────────────────

def _cover_page(story, quote, styles, is_visitor):
    # Watermark text
    story.append(Spacer(1, 25*mm))
    story.append(Paragraph('帝标 · 设记家', styles['WMTxt']))
    story.append(Spacer(1, 5*mm))

    # Title
    title = '报价单' if not is_visitor else '价格参考单'
    story.append(Paragraph(title, styles['CNTitle']))
    story.append(Paragraph('帝标·设记家  全案落地报价单', styles['CNSubT']))
    story.append(Paragraph('★ 保密文件，严禁外泄 ★', styles['CNSmall']))

    story.append(Spacer(1, 8*mm))

    # Info table
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    rows = [
        ['报价编号', quote.quote_no or ''],
        ['生成时间', now_str],
    ]
    if not is_visitor:
        cn = getattr(quote, 'customer_name', '') or ''
        if cn:
            rows.append(['客户名称', cn])
        cp = getattr(quote, 'customer_phone', '') or ''
        if cp:
            rows.append(['联系电话', cp])
    pn = getattr(quote, 'project_name', '') or ''
    if pn:
        rows.append(['项目名称', pn])
    pa = getattr(quote, 'project_address', '') or ''
    if pa:
        rows.append(['项目地址', pa])
    ht = getattr(quote, 'house_type', '') or ''
    if ht:
        rows.append(['户型信息', ht])
    cno = getattr(quote, 'contract_no', '') or ''
    if cno:
        rows.append(['合同编号', cno])

    t = Table(rows, colWidths=[38*mm, 102*mm])
    t.setStyle(TableStyle([
        ('FONTNAME',  (0,0),(0,-1), CN_FONT),
        ('FONTNAME',  (1,0),(1,-1), CN_FONT_BODY),
        ('FONTSIZE',  (0,0),(-1,-1), 10),
        ('TEXTCOLOR', (0,0),(0,-1), BRAND_BROWN),
        ('TEXTCOLOR', (1,0),(1,-1), DARK_TEXT),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('TOPPADDING',   (0,0),(-1,-1), 5),
    ]))
    story.append(t)

    # Service team
    if not is_visitor and getattr(quote, 'service_team', None):
        story.append(Spacer(1, 8*mm))
        story.append(Paragraph('服务团队', styles['CNSec']))
        team_data = [['角色', '姓名', '联系电话']]
        for m in quote.service_team:
            team_data.append([
                m.get('role_name', ''),
                m.get('name', ''),
                m.get('phone', ''),
            ])
        tt = Table(team_data, colWidths=[38*mm, 50*mm, 52*mm])
        tt.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1), CN_FONT_BODY),
            ('FONTSIZE',(0,0),(-1,0), 9),
            ('FONTSIZE',(0,1),(-1,-1), 9),
            ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
            ('TEXTCOLOR',(0,0),(-1,0), white),
            ('GRID',(0,0),(-1,-1), 0.5, MID_GRAY),
            ('BOTTOMPADDING',(0,0),(-1,-1), 4),
            ('TOPPADDING',(0,0),(-1,-1), 4),
        ]))
        story.append(tt)

    story.append(PageBreak())


# ─── Category grouping helpers ───────────────────────────────────────────────

def _group_by_category(items):
    """Return {cat_key: [items]} grouped by category_level1."""
    g = {}
    for it in items:
        k = it.category_level1 or 'other'
        g.setdefault(k, []).append(it)
    return g


def _group_by_room(items):
    """Return {room_name: [items]} grouped by room_name."""
    g = {}
    for it in items:
        k = it.room_name or '其他'
        g.setdefault(k, []).append(it)
    return g


# ─── Customer item row ───────────────────────────────────────────────────────

def _item_row(it, is_visitor):
    """Return one data row for an item (customer or visitor version)."""
    # Custom dimensions
    dims = []
    for f, lbl in [('width','W'), ('depth','D'), ('height','H')]:
        v = getattr(it, f, None)
        if v and float(v or 0) > 0:
            dims.append('{}{}'.format(lbl, float(v)))
    dim_str = '×'.join(dims) if dims else it.spec or ''

    craft = ''
    cq = getattr(it, 'craft_quantity', None)
    cc = getattr(it, 'craft_coefficient', None)
    if cq or cc:
        parts = []
        if cq and float(cq or 0) > 0:
            parts.append('数量{}'.format(float(cq)))
        if cc and float(cc or 0) != 1.0:
            parts.append('系数{}'.format(float(cc)))
        craft = '×'.join(parts)

    row = [
        it.name or '',
        dim_str,
        it.brand or '',
        it.unit or '',
        str(it.quantity or 0),
    ]
    if is_visitor:
        row += [_ymoney(it.total_price)]
    else:
        row += [_ymoney(it.unit_price), _ymoney(it.total_price)]
    if craft:
        row.append(craft)
    else:
        row.append(it.remark or '')
    return row


# ─── Category summary section ────────────────────────────────────────────────

def _cat_headers(is_visitor):
    if is_visitor:
        return ['名称', '规格', '品牌', '单位', '数量', '合计', '备注']
    return ['名称', '定制尺寸', '品牌', '单位', '数量', '单价', '合计', '工艺/备注']


def _cat_col_widths(is_visitor):
    if is_visitor:
        return [40*mm, 30*mm, 22*mm, 14*mm, 14*mm, 22*mm, 18*mm]
    return [38*mm, 22*mm, 20*mm, 12*mm, 12*mm, 18*mm, 22*mm, 16*mm]


def _cat_table(items, is_visitor, styles):
    """Build one category section (header + item rows + subtotal)."""
    data = [_cat_headers(is_visitor)]
    total = Decimal('0')
    for it in items:
        data.append(_item_row(it, is_visitor))
        total += Decimal(str(it.total_price or 0))

    # Subtotal row
    if is_visitor:
        data.append(['-- 小计 --', '', '', '', '', _ymoney(total), ''])
    else:
        data.append(['-- 小计 --', '', '', '', '', '', _ymoney(total), ''])

    cw = _cat_col_widths(is_visitor)
    n_cols = len(cw)

    cmds = [
        ('FONTNAME', (0,0),(-1,0), CN_FONT),
        ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE', (0,0),(-1,-1), 7.5),
        ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
        ('TEXTCOLOR',(0,0),(-1,0), white),
        ('GRID',(0,0),(-1,-1), 0.5, MID_GRAY),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ('TOPPADDING',(0,0),(-1,-1), 3),
        # Subtotal row
        ('FONTNAME',(0,-1),(-1,-1), CN_FONT),
        ('BACKGROUND',(0,-1),(-1,-1), LIGHT_GRAY),
        ('SPAN',(0,-1),(n_cols-2 if is_visitor else n_cols-3, -1)),
        ('ALIGN',(n_cols-1 if is_visitor else n_cols-2,-1),(n_cols-1,-1),'RIGHT'),
        ('TEXTCOLOR',(0,-1),(-1,-1), BRAND_BROWN),
    ]

    # Highlight merged cells for custom furniture (custom/furniture categories)
    prev_name = None
    span_start = 1
    merged = []
    for i, it in enumerate(items, 1):
        nm = (it.name or '').strip()
        if nm == prev_name and i > span_start:
            merged.append(i)
        else:
            if i > span_start:
                merged.append((span_start, i - 1))
            span_start = i
            prev_name = nm
    if span_start < len(items):
        merged.append((span_start, len(items)))

    tbl = Table(data, colWidths=cw, repeatRows=1)
    tbl.setStyle(TableStyle(cmds))
    return tbl, total


def _category_summary_page(story, items, is_visitor, styles):
    """Build the category summary section (one continuous flow, page-breaks auto)."""
    grouped = _group_by_category(items)

    # Build ordered cat list from DB sort_order
    from app.models.material_sku import MaterialCategory
    from sqlalchemy import or_ as sql_or
    cats = MaterialCategory.query.filter(
        MaterialCategory.parent_id.is_(None),
        sql_or(MaterialCategory.is_deleted == False,
               MaterialCategory.is_deleted.is_(None)),
        MaterialCategory.is_enabled == True
    ).order_by(MaterialCategory.sort_order).all()

    # Map L1 id → display name
    cat_id_to_key = {}
    for c in cats:
        cat_id_to_key[c.id] = c.name  # e.g. 1→'全案服务'

    grand_total = Decimal('0')
    cat_totals = []

    for cat in cats:
        cat_key = cat.name  # e.g. '全案服务'
        cat_items = grouped.get(cat_key, [])
        # Also check via CAT_MAP for legacy keys
        if not cat_items:
            for k, v in CAT_MAP.items():
                if v == cat_key:
                    cat_items = grouped.get(k, [])
                    if cat_items:
                        break

        if not cat_items:
            continue

        story.append(Paragraph(cat_key, styles['CNSec']))
        tbl, ct = _cat_table(cat_items, is_visitor, styles)
        grand_total += ct
        cat_totals.append((cat_key, ct))
        story.append(tbl)
        story.append(Spacer(1, 3*mm))

    # Grand total line
    story.append(Spacer(1, 6*mm))
    label = '参考总价' if is_visitor else '报价总计'
    story.append(Paragraph(
        '{}：{}'.format(label, _ymoney(grand_total)),
        styles['CNGrand']
    ))

    # Management fee & tax (customer only)
    if not is_visitor:
        extras = []
        mf = getattr(quote_obj, 'management_fee', None) if 'quote_obj' in dir() else None
        # use closure quote via outer scope
        pass

    return grand_total


def _quote_grand_total(quote, items):
    """Calculate grand total from items."""
    return sum(Decimal(str(it.total_price or 0)) for it in items)


# ─── Room detail section ─────────────────────────────────────────────────────

def _room_headers(is_visitor):
    if is_visitor:
        return ['名称', '定制尺寸', '品牌', '单位', '数量', '合计', '备注']
    return ['名称', '定制尺寸', '品牌', '单位', '数量', '单价', '合计', '工艺/备注']


ROOM_CW_V = [38*mm, 24*mm, 22*mm, 14*mm, 14*mm, 22*mm, 20*mm]
ROOM_CW_C = [36*mm, 22*mm, 20*mm, 12*mm, 12*mm, 18*mm, 22*mm, 18*mm]


def _room_section(story, room_name, items, is_visitor, styles):
    """Build one room section with green header."""
    if not items:
        return Decimal('0')

    total = sum(Decimal(str(it.total_price or 0)) for it in items)

    # Header row
    header_text = '{}  —  {}件  小计：{}'.format(
        room_name, len(items), _ymoney(total)
    )
    hdr_data = [[header_text, '', '', '', '', '']]
    if not is_visitor:
        hdr_data[0].append('')
    hdr_cw = ROOM_CW_V if is_visitor else ROOM_CW_C

    hdr_tbl = Table(hdr_data, colWidths=hdr_cw)
    hdr_tbl.setStyle(TableStyle([
        ('SPAN', (0,0), (-1,0)),
        ('BACKGROUND', (0,0), (-1,0), GREEN_HEADER),
        ('FONTNAME', (0,0), (-1,0), CN_FONT),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('TEXTCOLOR', (0,0), (-1,0), BRAND_BROWN),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('TOPPADDING', (0,0), (-1,0), 4),
        ('LEFTPADDING', (0,0), (-1,0), 4),
    ]))
    story.append(hdr_tbl)

    # Item rows
    rows = [_room_headers(is_visitor)]
    for it in items:
        rows.append(_item_row(it, is_visitor))

    tbl = Table(rows, colWidths=hdr_cw, repeatRows=1)
    cmds = [
        ('FONTNAME', (0,0),(-1,0), CN_FONT),
        ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE', (0,0),(-1,-1), 7.5),
        ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
        ('TEXTCOLOR',(0,0),(-1,0), white),
        ('GRID',(0,0),(-1,-1), 0.5, MID_GRAY),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ('TOPPADDING',(0,0),(-1,-1), 3),
    ]
    tbl.setStyle(TableStyle(cmds))
    story.append(tbl)
    story.append(Spacer(1, 4*mm))
    return total


def _room_details_page(story, items, is_visitor, styles):
    """Build all room sections in user-specified order."""
    grouped = _group_by_room(items)
    rooms_sorted = sorted(grouped.keys(), key=_room_sort_key)
    grand = Decimal('0')
    for rn in rooms_sorted:
        t = _room_section(story, rn, grouped[rn], is_visitor, styles)
        grand += t
    return grand


# ─── Principles footer page ──────────────────────────────────────────────────

def _principles_page(story, styles, is_visitor):
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph('★  报价原则  ★', styles['CNTitle']))
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph('本报价单严格遵循', styles['CNPrinci']))
    story.append(Paragraph('"预算即决算，零增项"', styles['CNPrinciB']))
    story.append(Paragraph('核心承诺', styles['CNPrinci']))

    story.append(Spacer(1, 12*mm))

    principles = [
        ('1', '报价即决算', '本报价单所列价格均为最终价格，不含任何隐性收费项目。'),
        ('2', '零增项保障', '合同签订后，如非业主主动变更需求，不产生任何额外费用。'),
        ('3', '透明报价', '所有材料、人工、管理费用均清晰列明，绝无低价导入高价结算。'),
        ('4', '品质承诺', '所有产品均按合同约定品牌、规格、材质供货，假一赔十。'),
        ('5', '工期保障', '严格按合同约定工期执行，延误按约定承担违约责任。'),
    ]
    for num, title, body in principles:
        story.append(Paragraph(
            '{}、{}：{}'.format(num, title, body),
            styles['CNBody']
        ))
        story.append(Spacer(1, 3*mm))

    story.append(Spacer(1, 12*mm))
    if is_visitor:
        story.append(Paragraph('以上价格仅供参考，实际报价以到店咨询为准。', styles['CNSmall']))
    else:
        days = getattr(quote_obj, 'valid_days', 30) if 'quote_obj' in dir() else 30
        story.append(Paragraph('本报价单有效期 {} 天，过期作废。'.format(days), styles['CNSmall']))
    story.append(PageBreak())


# ─── Main generator ──────────────────────────────────────────────────────────

def generate_quote_pdf(quote, items, is_visitor=False):
    """
    Generate a PDF for the given quote.
    quote  : Quote model instance
    items  : list of QuoteItem instances
    is_visitor : True → visitor version (no unit prices)
    Returns: relative path string e.g. 'pdf/quote_xxx_customer_20260505.pdf'
    """
    global quote_obj
    quote_obj = quote  # make available to inner functions above

    styles = _build_styles()

    pdf_dir = os.path.join(UPLOAD_ROOT, 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    ver = 'visitor' if is_visitor else 'customer'
    fname = 'quote_{}_{}_{}.pdf'.format(quote.quote_no or quote.id, ver, ts)
    fpath = os.path.join(pdf_dir, fname)

    doc = SimpleDocTemplate(
        fpath, pagesize=A4,
        topMargin=12*mm, bottomMargin=12*mm,
        leftMargin=12*mm, rightMargin=12*mm,
    )

    story = []

    # ── Page 1: Cover ────────────────────────────────────────────────────
    _cover_page(story, quote, styles, is_visitor)

    # ── Page 2+: Category summary (continuous flow, auto page-break) ──────
    # Inject page header on each new page after cover
    def _page_header_footer(canvas, doc):
        canvas.saveState()
        # Header line
        canvas.setFillColor(BRAND_BROWN)
        canvas.setFont(CN_FONT, 8)
        canvas.drawString(12*mm, A4[1] - 8*mm,
                          '\u5c1a\u6807\u00b7\u8bbe\u8bb0\u5bb6  \u62a5\u4ef7\u5355')
        canvas.drawRightString(A4[0] - 12*mm, A4[1] - 8*mm,
                               (quote.quote_no or '') + '  ' + ('\u5ba2\u6237\u7248' if not is_visitor else '\u53c2\u8003\u7248'))
        # Footer line
        canvas.setFillColor(MID_GRAY)
        canvas.setFont(CN_FONT_BODY, 7)
        canvas.drawString(12*mm, 8*mm, '\u2014\u2014  \u4fdd\u5bc6\u6587\u4ef6  \u2014\u2014')
        canvas.drawRightString(A4[0] - 12*mm, 8*mm, 'p{}\u9875'.format(doc.page))
        canvas.restoreState()

    # Page 1 = cover (already built), Pages 2+ = category summary
    # Add page header to subsequent pages
    def _cat_page_header(canvas, doc):
        if doc.page == 1:
            return
        _page_header_footer(canvas, doc)

    grouped = _group_by_category(items)
    from app.models.material_sku import MaterialCategory
    from sqlalchemy import or_ as sql_or
    cats = MaterialCategory.query.filter(
        MaterialCategory.parent_id.is_(None),
        sql_or(MaterialCategory.is_deleted == False,
               MaterialCategory.is_deleted.is_(None)),
        MaterialCategory.is_enabled == True
    ).order_by(MaterialCategory.sort_order).all()

    grand_total = Decimal('0')
    cat_totals_list = []

    for cat in cats:
        cat_key = cat.name
        cat_items = grouped.get(cat_key, [])
        if not cat_items:
            for k, v in CAT_MAP.items():
                if v == cat_key:
                    cat_items = grouped.get(k, [])
                    if cat_items:
                        break
        if not cat_items:
            continue

        story.append(Paragraph(cat_key, styles['CNSec']))
        tbl, ct = _cat_table(cat_items, is_visitor, styles)
        grand_total += ct
        cat_totals_list.append((cat_key, ct))
        story.append(tbl)
        story.append(Spacer(1, 3*mm))

    # Grand total banner
    story.append(Spacer(1, 6*mm))
    lbl = '\u53c2\u8003\u603b\u4ef7' if is_visitor else '\u62a5\u4ef7\u603b\u8ba1'
    story.append(Paragraph('{}：{}'.format(lbl, _ymoney(grand_total)), styles['CNGrand']))

    # Management fee + tax
    if not is_visitor:
        extras = []
        for lbl, val in [('\u7ba1\u7406\u8d39', 'management_fee'),
                          ('\u7a0e\u8d39', 'tax')]:
            v = getattr(quote, val, None)
            if v and float(v or 0) > 0:
                extras.append([lbl, _ymoney(v)])
        if extras:
            story.append(Spacer(1, 4*mm))
            et = Table(extras, colWidths=[38*mm, 50*mm])
            et.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1), CN_FONT_BODY),
                ('FONTSIZE',(0,0),(-1,-1), 9),
                ('ALIGN',(1,0),(1,-1),'RIGHT'),
            ]))
            story.append(et)
        if getattr(quote, 'total_amount', None) and float(quote.total_amount or 0) > 0:
            story.append(Paragraph('\u6700\u7ec8\u62a5\u4ef7\uff1a{}'.format(
                _ymoney(quote.total_amount)), styles['CNTotal']))

    story.append(PageBreak())

    # ── Room details pages ─────────────────────────────────────────────────
    def _room_page_header(canvas, doc):
        _page_header_footer(canvas, doc)

    _room_details_page(story, items, is_visitor, styles)

    # ── Final page: Principles ─────────────────────────────────────────────
    def _principles_page_header(canvas, doc):
        _page_header_footer(canvas, doc)

    story.append(PageBreak())
    _principles_page(story, styles, is_visitor)

    doc.build(story, onFirstPage=_cat_page_header,
              onLaterPages=_cat_page_header)

    return 'pdf/{}'.format(fname)


def generate_both_pdfs(quote_id):
    """Generate customer + visitor PDFs; optionally attach to case."""
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

    c_rel = generate_quote_pdf(quote, items, is_visitor=False)
    v_rel = generate_quote_pdf(quote, items, is_visitor=True)

    result = {'customer_path': c_rel, 'visitor_path': v_rel}

    case = CaseStudy.query.filter_by(customer_id=quote.customer_id).first()
    if case:
        for fname, url, wm in [
            ('\u62a5\u4ef7\u5355_{}_\u5ba2\u6237\u7248.pdf'.format(quote.quote_no),
             '/upload/{}'.format(c_rel), False),
            ('\u62a5\u4ef7\u5355_{}_\u53c2\u8003\u7248.pdf'.format(quote.quote_no),
             '/upload/{}'.format(v_rel), True),
        ]:
            cf = CaseFile(case_id=case.id, file_type='pdf',
                          file_name=fname, file_url=url, has_watermark=wm)
            db.session.add(cf)
        db.session.commit()
        result['case_id'] = case.id

    return result


def auto_authorize_on_quote_confirm(quote_id):
    """Auto-authorize related case when quote is confirmed."""
    from app.models.quote import Quote
    from app.models.case import CaseStudy
    from app import db

    quote = Quote.query.get(quote_id)
    if not quote:
        return None
    case = CaseStudy.query.filter_by(customer_id=quote.customer_id).first()
    if not case:
        return {'authorized': False, 'case_id': None,
                'message': 'No case found for this customer'}
    if case.owner_authorized and case.enable_public_workflow:
        return {'authorized': True, 'case_id': case.id,
                'message': 'Already authorized'}

    case.owner_authorized = True
    case.enable_public_workflow = True
    if case.building_id or case.workflow_id:
        case.is_real_case = True
    db.session.commit()

    return {'authorized': True, 'case_id': case.id,
            'message': 'Case auto-authorized from quote confirmation',
            'is_real_case': case.is_real_case}


# Placeholder so inner functions can reference quote_obj
quote_obj = None
