# -*- coding: utf-8 -*-
"""
PDF Generation Service for Quote Management (v3.0 - 按规范文档四页结构)
Generates two versions: customer (full) and visitor (desensitized)
"""
import os
import math
from datetime import datetime
from decimal import Decimal

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black, Color, red as colors_red
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ─── Font registration ────────────────────────────────────────────────────────
import platform
_system = platform.system()
if _system == 'Windows':
    FONT_DIR = r'C:\Windows\Fonts'
    _simhei = os.path.join(FONT_DIR, 'simhei.ttf')
    _simsun = os.path.join(FONT_DIR, 'simsun.ttc')
elif _system == 'Darwin':  # macOS
    _simhei = '/System/Library/Fonts/STHeiti Medium.ttc'
    _simsun = '/System/Library/Fonts/Supplemental/Songti.ttc'
else:
    _simhei = ''
    _simsun = ''

try:
    pdfmetrics.registerFont(TTFont('SimHei', _simhei))
    pdfmetrics.registerFont(TTFont('SimSun', _simsun))
    CN_FONT = 'SimHei'
    CN_FONT_BODY = 'SimSun'
except Exception as e:
    print(f'[PDF] Font registration failed: {e}')
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

# ─── Background image ─────────────────────────────────────────────────────
BG_IMAGE_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'static', 'quote_bg', 'inner_bg.png'
))

# ─── Page size: 16:9 landscape ───────────────────────────────────────────────
# 16:9 at 297mm wide → height = 297 * 9/16 = 167.06mm
PAGE_W = 297*mm
PAGE_H = 297*mm * 9 / 16
PAGE_SIZE = (PAGE_W, PAGE_H)

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
    """
    v4.0 — 封面页：品牌 + DESIGNARY大标题 + 副标题(客户+楼盘) + 双卡片 + 背景图
    布局：
      ① 背景图（从SlideTemplate内页背景图获取，16:9适配横版A4）
      ② 顶部：D&B·帝标｜设记家（品牌名）+ DESIGNARY（大标题）
      ③ 副标题行：客户名称 + 楼盘名 + 门牌号 + 报价表
      ④ 双卡片（左：报价编号/有效期/生成时间/户型，右：服务团队）
    """
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import KeepTogether
    from app.models.case import SlideTemplate

    # ══════════════════════════════════════
    # 背景图（全页覆盖，16:9）— 由 _page_header_footer 在 canvas 层绘制
    # ══════════════════════════════════════
    # Background is drawn via canvas.drawImage in _page_header_footer
    # No need to add Image to story (it would overlap with canvas layer)

    # ══════════════════════════════════════
    # 颜色常量
    # ══════════════════════════════════════
    CARD_BG       = HexColor('#F8F5F0')
    CARD_HEADER_BG = HexColor('#8B5A2B')
    CARD_BORDER   = HexColor('#D4C4A8')

    # ══════════════════════════════════════
    # ① 品牌名 + 大标题 DESIGNARY
    # ══════════════════════════════════════
    story.append(Spacer(1, 6*mm))

    brand_style = ParagraphStyle(
        'CoverBrand', fontName=CN_FONT_BODY, fontSize=11, leading=15,
        textColor=HexColor('#8B7355'), alignment=TA_CENTER,
    )
    story.append(Paragraph('D&B·帝标｜设记家', brand_style))

    story.append(Spacer(1, 2*mm))

    # 大标题 DESIGNARY
    title_style = ParagraphStyle(
        'DesignaryTitle', fontName='Helvetica-Bold', fontSize=36, leading=44,
        textColor=BRAND_BROWN, alignment=TA_CENTER,
        spaceAfter=1*mm,
    )
    story.append(Paragraph('<b>DESIGNARY</b>', title_style))

    # ══════════════════════════════════════
    # ② 副标题（客户名称 + 楼盘名 + 门牌号 + 报价表）
    # ══════════════════════════════════════
    cn = getattr(quote, 'customer_name', '') or ''
    building = getattr(quote, 'building_name', '') or ''
    pa = getattr(quote, 'project_address', '') or ''
    qno = quote.quote_no or ''

    subtitle_parts = []
    if cn:
        subtitle_parts.append(cn)
    if building:
        subtitle_parts.append(building)
    if pa and pa != building:
        # 取门牌号部分
        subtitle_parts.append(pa)

    subtitle_text = ' · '.join(subtitle_parts) + (' · 报价表' if qno else '')
    if not subtitle_text.strip():
        subtitle_text = '全案落地报价单'

    subtitle_style = ParagraphStyle(
        'CoverSub', fontName=CN_FONT_BODY, fontSize=12, leading=18,
        textColor=MID_GRAY, alignment=TA_CENTER, spaceBefore=2*mm, spaceAfter=3*mm,
    )
    story.append(Paragraph(subtitle_text, subtitle_style))

    # 金色分隔线
    sep_line = Table([['']], colWidths=[140*mm], rowHeights=[2*mm])
    sep_line.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#C4A35A')),
        ('LINEABOVE', (0,0), (-1,-1), 0, white),
    ]))
    story.append(sep_line)
    story.append(Spacer(1, 6*mm))

    # ══════════════════════════════════════
    # ③ 双卡片区域
    # ══════════════════════════════════════

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    # ── 左卡：报价信息 ──
    cust_rows = [[_ch('报价信息'), _ch('')]]

    if qno:
        cust_rows.append([_fl('报价编号'), _fv(qno)])
    cust_rows.append([_fl('生成时间'), _fv(now_str)])

    exp = getattr(quote, 'expire_date', '') or ''
    if exp:
        cust_rows.append([_fl('有效期至'), _fv(exp)])

    ht = getattr(quote, 'house_type', '') or ''
    if ht:
        cust_rows.append([_fl('户型信息'), _fv(ht)])

    cust_table = Table(cust_rows, colWidths=[32*mm, 68*mm])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0),(-1,0), CARD_HEADER_BG),
        ('TEXTCOLOR',   (0,0),(0,0), white),
        ('FONTNAME',    (0,0),(0,0), CN_FONT),
        ('FONTSIZE',   (0,0),(0,0), 11),
        ('ALIGN',       (0,0),(0,0), 'CENTER'),
        ('SPAN',        (0,0),(1,0)),
        ('BACKGROUND',  (0,1),(-1,-1), CARD_BG),
        ('FONTNAME',    (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE',    (0,1),(-1,-1), 9),
        ('TEXTCOLOR',   (0,1),(0,1), BRAND_BROWN),
        ('TEXTCOLOR',   (1,1),(1,-1), DARK_TEXT),
        ('GRID',        (0,1),(-1,-1), 0.5, CARD_BORDER),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('TOPPADDING',  (0,0),(-1,-1), 5),
        ('LEFTPADDING', (0,0),(-1,-1), 6),
        ('RIGHTPADDING',(0,0),(-1,-1), 6),
        ('VALIGN',      (0,0),(-1,-1), 'MIDDLE'),
    ]))

    # ── 右卡：服务团队 ──
    team_rows = [[_ch('服务团队'), _ch('')]]

    if not is_visitor and getattr(quote, 'service_team', None):
        _role_map = {
            'quoter': '报价员',
            'auditor': '审核员',
            'designer': '全案设计师',
            'planner': '全案规划师',
            'project_manager': '项目经理',
        }
        _emp_cache = {}
        for m in quote.service_team:
            role_name = m.get('role_name') or _role_map.get(m.get('role',''), '')
            name = m.get('name', '')
            phone = m.get('phone', '')
            if not name and m.get('employee_id'):
                eid = m['employee_id']
                if eid not in _emp_cache:
                    try:
                        from app.models.hr import Employee
                        emp = Employee.query.get(eid)
                        _emp_cache[eid] = {'name': emp.name, 'phone': getattr(emp,'phone','') or ''} if emp else {}
                    except Exception:
                        _emp_cache[eid] = {}
                name = _emp_cache[eid].get('name', '')
                phone = _emp_cache[eid].get('phone', '')
            team_rows.append([_fl(role_name), _fv(name + ('  ' + phone if phone else ''))])

    if len(team_rows) == 1:
        team_rows.append([_fl('暂无'), _fv('')])

    team_table = Table(team_rows, colWidths=[32*mm, 68*mm])
    team_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0),(-1,0), CARD_HEADER_BG),
        ('TEXTCOLOR',   (0,0),(0,0), white),
        ('FONTNAME',    (0,0),(0,0), CN_FONT),
        ('FONTSIZE',   (0,0),(0,0), 11),
        ('ALIGN',       (0,0),(0,0), 'CENTER'),
        ('SPAN',        (0,0),(1,0)),
        ('BACKGROUND',  (0,1),(-1,-1), CARD_BG),
        ('FONTNAME',    (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE',    (0,1),(-1,-1), 9),
        ('TEXTCOLOR',   (0,1),(0,1), BRAND_BROWN),
        ('TEXTCOLOR',   (1,1),(1,-1), DARK_TEXT),
        ('GRID',        (0,1),(-1,-1), 0.5, CARD_BORDER),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('TOPPADDING',  (0,0),(-1,-1), 5),
        ('LEFTPADDING', (0,0),(-1,-1), 6),
        ('RIGHTPADDING',(0,0),(-1,-1), 6),
        ('VALIGN',      (0,0),(-1,-1), 'MIDDLE'),
    ]))

    # ── 卡片容器 ──
    card_container = Table([[cust_table, team_table]], colWidths=[110*mm, 110*mm])
    card_container.setStyle(TableStyle([
        ('BACKGROUND',  (0,0),(0,0), white),
        ('BACKGROUND',  (1,0),(1,0), white),
        ('LEFTPADDING', (0,0),(0,0), 10),
        ('RIGHTPADDING',(0,0),(0,0), 10),
        ('TOPPADDING',  (0,0),(0,0), 5),
        ('BOTTOMPADDING',(0,0),(0,0), 5),
        ('VALIGN',      (0,0),(-1,-1), 'TOP'),
    ]))

    story.append(KeepTogether([card_container]))
    story.append(PageBreak())




# ─── Cover page helper functions ─────────────────────────────────────────────

def _ch(text):
    """Card header cell (spanned title)."""
    from reportlab.platypus import Paragraph as RP
    s = ParagraphStyle('CHdr', fontName=CN_FONT, fontSize=11, leading=16,
                       textColor=white, alignment=TA_CENTER)
    return RP(text, s)


def _fl(text):
    """Field label cell for cover page cards."""
    from reportlab.platypus import Paragraph as RP
    s = ParagraphStyle('FLbl', fontName=CN_FONT, fontSize=9, leading=14,
                       textColor=BRAND_BROWN)
    return RP(text, s)


def _fv(text):
    """Field value cell for cover page cards."""
    from reportlab.platypus import Paragraph as RP
    s = ParagraphStyle('FVal', fontName=CN_FONT_BODY, fontSize=9, leading=14,
                       textColor=DARK_TEXT)
    return RP(str(text) if text else '', s)




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

def _item_row(it, is_visitor, show_ref=True):
    """
    v3.5 — 物料详单行（自动换行）
    客户版11列：名称 | 物料 | 定制参数 | 计量值×数量 | 单位 | 工艺与系数 | 工艺数量 | 工艺金额 | 金额 | 备注
    参考版12列：+ 单价（单位后）
    """
    from reportlab.platypus import Paragraph as RP
    from reportlab.lib.styles import ParagraphStyle as RPS
    from reportlab.lib.enums import TA_LEFT

    def _cell(text, fontsize=7, align=TA_LEFT):
        style = RPS('cell', fontName=CN_FONT_BODY, fontSize=fontsize,
                    leading=fontsize + 2, alignment=align)
        return RP(str(text) if text else '', style)

    # ── 名称（custom_name 优先）──
    custom_nm = getattr(it, 'custom_name', None) or ''
    name_cell = _cell(custom_nm) if custom_nm else _cell(it.name or '')

    # ── 物料（material_name → fallback name）──
    mat_nm = getattr(it, 'material_name', None)
    mat_cell = _cell(mat_nm) if mat_nm else _cell(it.name or '')

    # ── 定制参数（宽×深×高）──
    cw = getattr(it, 'custom_width', None)
    cd = getattr(it, 'custom_depth', None)
    ch = getattr(it, 'custom_height', None)
    w = getattr(it, 'width', None)
    d = getattr(it, 'depth', None)
    h = getattr(it, 'height', None)
    size_parts = []
    for val, label in [(cw,w),(cd,d),(ch,h)]:
        fv = float(val or 0)
        if fv > 0:
            size_parts.append(str(int(fv)))
    custom_size_str = '\u00d7'.join(size_parts) if size_parts else (it.spec or '')

    # ── 计量值\u00d7数量 ──
    mval = getattr(it, 'measurement_value', None)
    qty = it.quantity or 0
    if mval and float(mval or 0) > 0 and float(mval or 0) != 1:
        qty_str = '{}\u00d7{}'.format(float(mval), qty)
    else:
        qty_str = str(qty)

    # ── 单位 ──
    unit_val = str(getattr(it, 'unit', None) or '').strip()

    # ── 工艺与系数（默认显示1.0）──
    pname = getattr(it, 'process_name', None) or ''
    pcoef = getattr(it, 'process_coefficient', None)
    cc = getattr(it, 'craft_coefficient', None)
    craft_parts = []
    if pname:
        craft_parts.append(pname)
    if pcoef and float(pcoef or 0) != 1.0:
        craft_parts.append('\u00d7{}'.format(float(pcoef)))
    if cc and float(cc or 0) != 1.0:
        craft_parts.append('\u00d7{}'.format(float(cc)))
    craft_info_str = ' '.join(craft_parts) if craft_parts else '1.0'

    # ── 工艺数量（默认0）──
    pqty = getattr(it, 'process_quantity', None)
    cq = getattr(it, 'craft_quantity', None)
    craft_qty_val = '0'
    if pqty and float(pqty or 0) > 0:
        craft_qty_val = str(float(pqty))
    elif cq and float(cq or 0) > 0:
        craft_qty_val = str(float(cq))

    # ── 工艺金额 ──
    pamount = getattr(it, 'process_amount', None)
    craft_amt = Decimal('0')
    if pamount and float(pamount or 0) > 0:
        craft_amt = Decimal(str(pamount))
    elif cc and float(cc or 0) > 1:
        base = Decimal(str(qty)) * Decimal(str(mval or 1)) * Decimal(str(it.unit_price or 0))
        craft_amt = base * (Decimal(str(cc)) - 1)

    # ── Build row ──
    row = [
        name_cell,
        mat_cell,
        _cell(custom_size_str),
        _cell(qty_str),
        _cell(unit_val),
    ]
    if not is_visitor:
        row.append(_cell(_ymoney(it.unit_price)))
    row += [
        _cell(craft_info_str),
        _cell(craft_qty_val),
        _cell(_ymoney(craft_amt)),
        _cell(_ymoney(it.total_price)),
        _cell(it.remark or '', 6.5),
    ]
    return row


def _cat_headers(is_visitor, show_ref=True):
    """v3.2 — same as _room_headers for consistency"""
    return _room_headers(is_visitor, show_ref)


def _cat_col_widths(is_visitor, show_ref=True):
    """v3.2 — same as ROOM_CW for consistency"""
    if is_visitor:
        return ROOM_CW_V
    else:
        return ROOM_CW_C


def _cat_table(items, is_visitor, styles, show_ref=True):
    """Build one category section (header + item rows + subtotal)."""
    data = [_cat_headers(is_visitor)]
    total = Decimal('0')
    craft_subtotal = Decimal('0')
    for it in items:
        data.append(_item_row(it, is_visitor, show_ref))
        total += Decimal(str(it.total_price or 0))
        # Accumulate craft amount from last column
        pa = getattr(it, 'process_amount', None)
        if pa and float(pa or 0) > 0:
            craft_subtotal += Decimal(str(pa))
        else:
            cc = getattr(it, 'craft_coefficient', None) or 1
            if float(cc) > 1:
                base = Decimal(str(it.quantity or 0)) * Decimal(str(getattr(it, 'measurement_value', 1) or 1)) * Decimal(str(it.unit_price or 0))
                craft_subtotal += base * (Decimal(str(cc)) - 1)

    # Subtotal row — span col 0 to -5, last 5 cols: [工艺数量|工艺金额|金额|备注] (visitor) or [单价|...]
    n_cols = len(_cat_col_widths(is_visitor, show_ref))
    if is_visitor:
        # visitor 11 cols: span 0~(-6), leave [工艺数量, 工艺金额, 金额, 备注]
        subtotal_row = ['-- 小计 --'] + [''] * (n_cols - 4) + ['', _ymoney(craft_subtotal), _ymoney(total), '']
    else:
        # customer 12 cols: span 0~(-6), leave [单价, 工艺数量, 工艺金额, 金额, 备注]
        subtotal_row = ['-- 小计 --'] + [''] * (n_cols - 5) + ['', '', _ymoney(craft_subtotal), _ymoney(total), '']
    data.append(subtotal_row)

    cw = _cat_col_widths(is_visitor)
    n_cols = len(cw)

    cmds = [
        ('FONTNAME', (0,0),(-1,0), CN_FONT),
        ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE', (0,0),(-1,-1), 7),
        ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
        ('TEXTCOLOR',(0,0),(-1,0), white),
        ('GRID',(0,0),(-1,-1), 0.5, MID_GRAY),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ('TOPPADDING',(0,0),(-1,-1), 3),
        # Subtotal row
        ('FONTNAME',(0,-1),(-1,-1), CN_FONT),
        ('BACKGROUND',(0,-1),(-1,-1), LIGHT_GRAY),
        ('SPAN',(0,-1),(-5, -1)),
        ('ALIGN',(-2,-1),(-1,-1),'RIGHT'),
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


def _money_to_chinese(n):
    """金额转中文大写（PDF端）"""
    if not n or n == 0:
        return '零元整'
    digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = '{:.2f}'.format(abs(float(n)))
    int_part, dec_part = s.split('.')
    r = ''
    for i, ch in enumerate(int_part):
        d = int(ch)
        ui = len(int_part) - 1 - i
        r += digits[d] + units[ui]
    import re
    r = re.sub(r'零+$', '', r)
    r = re.sub(r'零{2,}', '零', r)
    if dec_part and dec_part != '00':
        for i, ch in enumerate(dec_part[:2]):
            d = int(ch)
            if d != 0:
                r += digits[d] + ('角' if i == 0 else '分')
    r += '元整'
    return r


def _category_summary_page(story, quote, items, is_visitor, styles, show_ref=True):
    """
    v4.0 — 分类汇总页：与HTML模板一致的左右卡片布局
    布局：标题 → 左右双栏(左:分类卡片带二级子项,右:费用明细) → 底部总栏(整数+大写)
    """
    from app.models.material_sku import MaterialCategory as MC
    from sqlalchemy import or_ as sql_or
    from collections import OrderedDict
    from reportlab.lib.colors import Color

    grouped = _group_by_category(items)

    # ── 一级/二级分类（系统顺序）──
    cats = MC.query.filter(
        MC.parent_id.is_(None),
        sql_or(MC.is_deleted == False, MC.is_deleted.is_(None)),
        MC.is_enabled == True
    ).order_by(MC.sort_order).all()
    all_l2 = MC.query.filter(
        MC.parent_id.isnot(None),
        sql_or(MC.is_deleted == False, MC.is_deleted.is_(None)),
        MC.is_enabled == True
    ).order_by(MC.sort_order).all()
    l2_order = [c.name for c in all_l2]

    grand_total = Decimal('0')
    cat_rows = []

    for cat in cats:
        cat_key = cat.name
        cat_items = grouped.get(cat_key, [])
        if not cat_items:
            for k, v in CAT_MAP.items():
                if v == cat_key and grouped.get(k):
                    cat_items = grouped.get(k, [])
                    break
        if not cat_items:
            continue
        ct = sum(Decimal(str(it.total_price or 0)) for it in cat_items)
        grand_total += ct

        l2_grouped = OrderedDict()
        for it in cat_items:
            l2 = it.category_level2 or '其他'
            l2_grouped.setdefault(l2, []).append(it)
        l2_detail = []
        for l2_name in l2_order:
            if l2_name in l2_grouped:
                l2_amt = sum(Decimal(str(it.total_price or 0)) for it in l2_grouped[l2_name])
                l2_detail.append((l2_name, l2_amt))
        for l2_name, l2_items in l2_grouped.items():
            if l2_name not in l2_order:
                l2_amt = sum(Decimal(str(it.total_price or 0)) for it in l2_items)
                l2_detail.append((l2_name, l2_amt))

        cat_rows.append((cat_key, ct, l2_detail))

    # 未归类
    for gk, gitems in grouped.items():
        if not any(gk == cr[0] or CAT_MAP.get(gk) == cr[0] for cr in cat_rows):
            ct = sum(Decimal(str(it.total_price or 0)) for it in gitems)
            grand_total += ct
            display_name = CAT_MAP.get(gk, gk)
            cat_rows.append((display_name, ct, []))

    # ══════════════════════════════════════
    #  页面标题
    # ══════════════════════════════════════
    story.append(Spacer(1, 4*mm))

    title_style = ParagraphStyle('SumTitle', fontName=CN_FONT, fontSize=16, leading=24,
                                 textColor=BRAND_BROWN, alignment=TA_CENTER,
                                 spaceAfter=1*mm)
    story.append(Paragraph('报 价 汇 总', title_style))

    subtitle_style = ParagraphStyle('SumSub', fontName=CN_FONT_BODY, fontSize=9, leading=13,
                                    textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=6*mm)
    story.append(Paragraph('分类费用明细与总计', subtitle_style))

    # ══════════════════════════════════════
    #  读取费用字段
    # ══════════════════════════════════════
    material_amt = Decimal(str(getattr(quote, 'material_amount', 0) or 0))
    craft_amt = Decimal(str(getattr(quote, 'craft_amount', 0) or 0))
    design_amt = Decimal(str(getattr(quote, 'design_amount', 0) or 0))
    install_amt = Decimal(str(getattr(quote, 'install_amount', 0) or 0))
    mgmt_rate = float(getattr(quote, 'manage_rate', 0) or getattr(quote, 'management_fee_rate', 0) or 0)
    mgmt_fee = Decimal(str(getattr(quote, 'manage_amount', 0) or getattr(quote, 'management_fee', 0) or 0))
    tax_rate_val = float(getattr(quote, 'tax_rate', 0) or 0)
    tax_amt = Decimal(str(getattr(quote, 'tax_amount', 0) or getattr(quote, 'tax', 0) or 0))
    disc_rate = float(getattr(quote, 'discount_rate', 0) or 0)
    disc_amt = Decimal(str(getattr(quote, 'discount_amount', 0) or 0))
    if mgmt_fee > 0 and mgmt_rate == 0 and grand_total > 0:
        mgmt_rate = round(float(mgmt_fee / grand_total * 100), 1)
    subtotal_val = material_amt + craft_amt + design_amt + install_amt
    final_total = subtotal_val + mgmt_fee + tax_amt - disc_amt

    # ══════════════════════════════════════
    #  左侧：分类卡片（带二级子项）
    # ══════════════════════════════════════
    CAT_COLORS_PY = [
        HexColor('#8B5A2B'), HexColor('#C4A35A'), HexColor('#6B7F5E'),
        HexColor('#5B7A9D'), HexColor('#9B6B8D'), HexColor('#B8865A'),
        HexColor('#5A8B8B'), HexColor('#8B6B5A'),
    ]

    cat_hdr = ParagraphStyle('CatHdr', fontName=CN_FONT, fontSize=11, leading=16,
                              textColor=BRAND_BROWN, spaceAfter=6)
    cat_name_p = ParagraphStyle('CatNm', fontName=CN_FONT, fontSize=10, leading=14)
    cat_sub_p = ParagraphStyle('CatSub', fontName=CN_FONT_BODY, fontSize=8, leading=12,
                               textColor=HexColor('#777'))

    left_content = [[Paragraph('\u25aa 分类汇总', cat_hdr)]]
    for ci, (cname, amt, l2_detail) in enumerate(cat_rows):
        color = CAT_COLORS_PY[ci % len(CAT_COLORS_PY)]
        pct = round(float(amt / grand_total * 100), 1) if grand_total > 0 else 0

        # 一级名称 + 金额
        name_cell = Paragraph(f'<b>{cname}</b>', cat_name_p)
        amt_cell = Paragraph(f'<b>¥{amt:,.2f}</b>  <font color="#999" size="8">{pct}%</font>',
                            ParagraphStyle('CAtR', fontName=CN_FONT, fontSize=10, leading=14,
                                          alignment=TA_RIGHT))
        header_row = Table([[name_cell, amt_cell]], colWidths=[65*mm, 35*mm])
        header_row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (0,0), 8),
            ('RIGHTPADDING', (1,0), (1,0), 6),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        card_rows = [[header_row]]
        if l2_detail:
            for ln, la in l2_detail:
                lp = Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;· {ln}', cat_sub_p)
                rp = Paragraph(f'{la:,.2f}', cat_sub_p)
                lr = Table([[lp, rp]], colWidths=[65*mm, 35*mm])
                lr.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (0,0), 10),
                    ('RIGHTPADDING', (1,0), (1,0), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ]))
                card_rows.append([lr])

        card_tbl = Table(card_rows, colWidths=[102*mm])
        card_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), HexColor('#FAF8F5')),
            ('BACKGROUND', (0,1), (0,-1), HexColor('#FAF8F5')),
            ('LINEBELOW', (0,0), (0,0), 2.5, color),
            ('BOX', (0,0), (-1,-1), 0.5, HexColor('#E8E0D4')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        left_content.append([card_tbl])

    left_tbl = Table(left_content, colWidths=[106*mm])
    left_tbl.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    # ══════════════════════════════════════
    #  右侧：费用明细表
    # ══════════════════════════════════════
    fee_label = ParagraphStyle('FeeL', fontName=CN_FONT_BODY, fontSize=9.5, leading=15)
    fee_val_s = ParagraphStyle('FeeVS', fontName=CN_FONT_BODY, fontSize=9.5, leading=15, alignment=TA_RIGHT)
    fee_bold_L = ParagraphStyle('FeeBL2', fontName=CN_FONT, fontSize=10, leading=16)
    fee_bold_R = ParagraphStyle('FeeBR2', fontName=CN_FONT, fontSize=10, leading=16, alignment=TA_RIGHT)
    fee_red = ParagraphStyle('FeeRed2', fontName=CN_FONT_BODY, fontSize=9.5, leading=15, alignment=TA_RIGHT,
                             textColor=HexColor('#CC0000'))

    fee_rows = []
    fee_rows.append([Paragraph('<b>物料总额</b>', fee_label),
                     Paragraph(f'¥{material_amt:,.2f}', fee_val_s)])
    if craft_amt > 0:
        fee_rows.append([Paragraph('工艺费用', fee_label),
                         Paragraph(f'¥{craft_amt:,.2f}', fee_val_s)])
    if design_amt > 0:
        fee_rows.append([Paragraph('设计费', fee_label),
                         Paragraph(f'¥{design_amt:,.2f}', fee_val_s)])
    if install_amt > 0:
        fee_rows.append([Paragraph('安装费', fee_label),
                         Paragraph(f'¥{install_amt:,.2f}', fee_val_s)])
    fee_rows.append([Spacer(1, 2), Spacer(1, 2)])
    fee_rows.append([Paragraph('<b>小计（材料+工艺）</b>', fee_bold_L),
                     Paragraph(f'<b>¥{subtotal_val:,.2f}</b>', fee_bold_R)])
    if mgmt_fee > 0:
        rate_str = f'{mgmt_rate}%' if mgmt_rate > 0 else ''
        fee_rows.append([Paragraph(f'管理费{rate_str}', fee_label),
                         Paragraph(f'¥{mgmt_fee:,.2f}', fee_val_s)])
    if tax_amt > 0:
        tr_str = f'{tax_rate_val}%' if tax_rate_val > 0 else ''
        fee_rows.append([Paragraph(f'税费{tr_str}', fee_label),
                         Paragraph(f'¥{tax_amt:,.2f}', fee_val_s)])
    if disc_amt > 0:
        dr_str = f'{disc_rate}%' if disc_rate > 0 else ''
        fee_rows.append([Paragraph(f'优惠折扣{dr_str}', fee_label),
                         Paragraph(f'-¥{disc_amt:,.2f}', fee_red)])

    fee_tbl = Table(fee_rows, colWidths=[72*mm, 32*mm])
    fee_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), CN_FONT_BODY),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (0,-1), 12),
        ('RIGHTPADDING', (1,0), (1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-3), 0.3, HexColor('#EEE8DD')),
        ('BACKGROUND', (0,0), (-1,-1), white),
    ]))

    right_hdr = ParagraphStyle('FeeHdr2', fontName=CN_FONT, fontSize=11, leading=16,
                                textColor=BRAND_BROWN, spaceAfter=6)
    right_content = [[Paragraph('\u25aa 费用明细', right_hdr)], [fee_tbl]]
    right_tbl = Table(right_content, colWidths=[106*mm])
    right_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), HexColor('#F8F5F0')),
        ('BOX', (0,0), (-1,-1), 0.5, HexColor('#D4C4A8')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    # ══════════════════════════════════════
    #  左右双栏容器
    # ══════════════════════════════════════
    cols_tbl = Table([[left_tbl, right_tbl]], colWidths=[110*mm, 110*mm])
    cols_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (0,0), 8),
        ('LEFTPADDING', (1,0), (1,0), 8),
        ('RIGHTPADDING', (1,0), (1,0), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(cols_tbl)

    # ══════════════════════════════════════
    #  底部总栏（与HTML一致，单金额整数+大写）
    # ══════════════════════════════════════
    story.append(Spacer(1, 8*mm))

    total_bar_inner = [[
        Paragraph('<b>总计：</b>', ParagraphStyle('TLbl', fontName=CN_FONT, fontSize=16, leading=22,
                                                  textColor=BRAND_BROWN)),
        Paragraph(f'<font color="#CC0000"><b>¥{int(final_total)}</b></font>',
                 ParagraphStyle('TAmt', fontName=CN_FONT, fontSize=26, leading=30, alignment=TA_RIGHT)),
    ]]
    total_bar = Table(total_bar_inner, colWidths=[90*mm, 60*mm])
    total_bar.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, BRAND_BROWN),
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#FFFDF8')),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,-1), 24),
        ('RIGHTPADDING', (1,0), (1,-1), 24),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(total_bar)

    # 大写金额行
    chinese = _money_to_chinese(final_total)
    cap_row = Table([[
        Paragraph('合计人民币（大写）：', ParagraphStyle('CapL', fontName=CN_FONT_BODY, fontSize=10,
                                                         leading=14, textColor=HexColor('#666'))),
        Paragraph(f'<b>{chinese}</b>', ParagraphStyle('CapR', fontName=CN_FONT, fontSize=11,
                                                       leading=16, textColor=BRAND_BROWN, alignment=TA_RIGHT)),
    ]], colWidths=[90*mm, 60*mm])
    cap_row.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#FFFDF8')),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, HexColor('#E8DCC8')),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,-1), 24),
        ('RIGHTPADDING', (1,0), (1,-1), 24),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(cap_row)

    return final_total




def _quote_grand_total(quote, items):
    """Calculate grand total from items."""
    return sum(Decimal(str(it.total_price or 0)) for it in items)


# ─── Room detail section ─────────────────────────────────────────────────────

def _room_headers(is_visitor, show_ref=True):
    """
    v3.4 — 名称 | 物料 | 定制参数 | 计量值×数量 | 单位 | [单价] | 工艺与系数 | 工艺数量 | 工艺金额 | 金额 | 备注
    参考版额外插入单价列（单位后）。
    """
    base = ['名称', '物料', '定制参数', '计量值×数量', '单位']
    if is_visitor:
        return base + ['工艺与系数', '工艺数量', '工艺金额', '金额', '备注']
    else:
        return base + ['单价', '工艺与系数', '工艺数量', '工艺金额', '金额', '备注']


# v3.4 — 横版A4 273mm，表格占260mm（95%）
# 客户版 11列: 22+30+38+20+12+28+16+22+26+24+22 = 260mm
# 参考版 12列: 22+30+38+20+12+18+28+16+22+26+24+22 = 278mm → 紧凑到 258mm
ROOM_CW_V = [22*mm, 30*mm, 38*mm, 20*mm, 12*mm, 28*mm, 16*mm, 22*mm, 26*mm, 24*mm, 22*mm]   # visitor 11 cols (260mm)
ROOM_CW_C = [20*mm, 28*mm, 36*mm, 18*mm, 12*mm, 16*mm, 26*mm, 14*mm, 20*mm, 24*mm, 22*mm, 22*mm]   # customer 12 cols (258mm)


def _room_section(story, room_name, items, is_visitor, styles, show_ref=True):
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
    hdr_cw = (ROOM_CW_V if is_visitor else ROOM_CW_C) if show_ref else (ROOM_CW_V if is_visitor else ROOM_CW_C)

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
    rows = [_room_headers(is_visitor, show_ref)]
    for it in items:
        rows.append(_item_row(it, is_visitor, show_ref))

    tbl = Table(rows, colWidths=hdr_cw, repeatRows=1)
    cmds = [
        ('FONTNAME', (0,0),(-1,0), CN_FONT),
        ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
        ('FONTSIZE', (0,0),(-1,-1), 7),
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


def _room_details_page(story, items, is_visitor, styles, show_ref=True):
    """Build all room sections grouped by space name, then by category_level1 inside each space."""
    from collections import OrderedDict

    # 1. Group by space_name
    space_groups = OrderedDict()
    for it in items:
        sn = it.space_name or it.room_name or '其他'
        space_groups.setdefault(sn, []).append(it)

    # 2. Sort rooms
    rooms_sorted = sorted(space_groups.keys(), key=_room_sort_key)

    grand = Decimal('0')
    for rn in rooms_sorted:
        room_items = space_groups[rn]
        room_total = sum(Decimal(str(it.total_price or 0)) for it in room_items)

        # ── 空间标题行（绿色表头）──
        header_text = '{}  —  {}件  小计：{}'.format(rn, len(room_items), _ymoney(room_total))
        hdr_cw = (ROOM_CW_V if is_visitor else ROOM_CW_C) if show_ref else (ROOM_CW_V if is_visitor else ROOM_CW_C)
        cols = len(hdr_cw)
        hdr_data = [[header_text] + [''] * (cols - 1)]
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

        # 3. Within room, group by category_level1
        cat_groups = OrderedDict()
        for it in room_items:
            ck = it.category_level1 or '其他'
            cat_groups.setdefault(ck, []).append(it)

        # Sort categories by predefined order
        cat_order = list(CAT_MAP.values()) + ['其他']
        cats_sorted = sorted(cat_groups.keys(), key=lambda c: (cat_order.index(c) if c in cat_order else 999))

        for cat_name in cats_sorted:
            cat_items = cat_groups[cat_name]
            cat_total = sum(Decimal(str(it.total_price or 0)) for it in cat_items)

            # ── 分类子标题（棕色小标签）+ 工艺金额汇总 ──
            cat_craft_total = sum(
                Decimal(str(getattr(it, 'process_amount', 0) or 0)) + (
                    (Decimal(str(it.quantity or 0)) * Decimal(str(getattr(it, 'measurement_value', 1) or 1)) * Decimal(str(it.unit_price or 0)) * (Decimal(str(getattr(it, 'craft_coefficient', 1) or 1)) - 1))
                    if float(getattr(it, 'craft_coefficient', 1) or 1) > 1 else Decimal('0')
                )
                for it in cat_items
            )
            craft_label = ''
            if cat_craft_total > 0:
                craft_label = '  工艺¥{}'.format(_ymoney(cat_craft_total))
            cat_hdr_text = '{}  —  {}件  ¥{}{}'.format(cat_name, len(cat_items), _ymoney(cat_total), craft_label)
            cat_hdr_data = [[cat_hdr_text] + [''] * (cols - 1)]
            cat_hdr_tbl = Table(cat_hdr_data, colWidths=hdr_cw)
            cat_hdr_tbl.setStyle(TableStyle([
                ('SPAN', (0,0), (-1,0)),
                ('BACKGROUND', (0,0), (-1,0), HexColor('#FFF8F0')),
                ('FONTNAME', (0,0), (-1,0), CN_FONT_BODY),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('TEXTCOLOR', (0,0), (-1,0), BRAND_BROWN),
                ('BOTTOMPADDING', (0,0), (-1,0), 3),
                ('TOPPADDING', (0,0), (-1,0), 3),
                ('LEFTPADDING', (0,0), (-1,0), 6),
                ('LINEBELOW', (0,0), (-1,0), 0.3, BRAND_BROWN),
            ]))
            story.append(cat_hdr_tbl)

            # ── 物料明细表格 ──
            rows = [_room_headers(is_visitor, show_ref)]
            for it in cat_items:
                rows.append(_item_row(it, is_visitor, show_ref))

            tbl = Table(rows, colWidths=hdr_cw, repeatRows=1)
            # visitor cols: 0=名称 1=物料名 2=qty 3=单位 4=工艺 5=工艺额 6=金额 7=备注
            # customer cols: 0=名称 1=物料名 2=qty 3=单位 4=单价 5=工艺 6=工艺额 7=金额 8=备注
            n = len(hdr_cw)
            cmds = [
                ('FONTNAME', (0,0),(-1,0), CN_FONT),
                ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
                ('FONTSIZE', (0,0),(-1,-1), 7),
                ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
                ('TEXTCOLOR',(0,0),(-1,0), white),
                ('GRID',(0,0),(-1,-1), 0.3, MID_GRAY),
                ('BOTTOMPADDING',(0,0),(-1,-1), 3),
                ('TOPPADDING',(0,0),(-1,-1), 3),
                # Right-align numeric columns (工艺金额=工艺额后第1列, 金额=最后第2列)
                ('ALIGN', (-3,-1), (-3,-1), 'RIGHT'),
                ('ALIGN', (-2,-1), (-2,-1), 'RIGHT'),
            ]
            if not is_visitor:
                cmds.append(('ALIGN', (-4,-1), (-4,-1), 'RIGHT'))  # 单价
            tbl.setStyle(TableStyle(cmds))
            story.append(tbl)
            story.append(Spacer(1, 2*mm))

        grand += room_total
        story.append(Spacer(1, 4*mm))

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

def generate_quote_pdf(quote, items, is_visitor=False, show_ref=True):
    """
    Generate a PDF for the given quote.
    quote  : Quote model instance
    items  : list of QuoteItem instances
    is_visitor : True → visitor version (no unit prices)
    show_ref   : True → show all ref columns (material/brand/color/spec etc.); False → compact view
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
        fpath, pagesize=PAGE_SIZE,
        topMargin=8*mm, bottomMargin=8*mm,
        leftMargin=12*mm, rightMargin=12*mm,
    )

    story = []

    # ── Page 1: Cover ────────────────────────────────────────────────────
    _cover_page(story, quote, styles, is_visitor)

    # ── Page 2+: Category summary (continuous flow, auto page-break) ──────
    # Inject page header on each new page after cover
    def _page_header_footer(canvas, doc):
        canvas.saveState()
        # Draw background image on every page
        if os.path.exists(BG_IMAGE_PATH):
            try:
                canvas.drawImage(BG_IMAGE_PATH, 0, 0, width=PAGE_W, height=PAGE_H,
                                 preserveAspectRatio=False, mask='auto')
            except Exception:
                pass
        canvas.restoreState()

    # Page 1 = cover (already built), Pages 2+ = category summary
    def _cat_page_header(canvas, doc):
        if doc.page == 1:
            # Cover page also gets background
            _page_header_footer(canvas, doc)
            return
        _page_header_footer(canvas, doc)

    # ── Page 2+: Category summary (简洁汇总) ──────
    final_total = _category_summary_page(story, quote_obj, items, is_visitor, styles, show_ref)

    # ── Room details pages (按空间→分类分组物料详单) ─────────────────────
    story.append(PageBreak())
    _room_details_page(story, items, is_visitor, styles, show_ref)

    # ── Final page: Principles ─────────────────────────────────────────────
    def _principles_page_header(canvas, doc):
        _page_header_footer(canvas, doc)

    story.append(PageBreak())
    _principles_page(story, styles, is_visitor)

    doc.build(story, onFirstPage=_cat_page_header,
              onLaterPages=_cat_page_header)

    return 'pdf/{}'.format(fname)


def generate_both_pdfs(quote_id, show_ref=True):
    """Generate customer + visitor PDFs; optionally attach to case.
    show_ref: True=full ref columns, False=compact view."""
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

    c_rel = generate_quote_pdf(quote, items, is_visitor=False, show_ref=show_ref)
    v_rel = generate_quote_pdf(quote, items, is_visitor=True, show_ref=show_ref)

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
