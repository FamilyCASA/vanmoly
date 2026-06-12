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
        # 补全员工信息（兼容旧数据只有 employee_id 的情况）
        _role_map = {
            'quoter': '报价员', 'designer': '审核', 'planner': '全案规划师',
            'designer_3d': '效果图设计师', 'project_manager': '全案设计师'
        }
        _emp_cache = {}
        for m in quote.service_team:
            role_name = m.get('role_name') or _role_map.get(m.get('role',''), '')
            name = m.get('name', '')
            phone = m.get('phone', '')
            # 如果缺少姓名，尝试从数据库查询
            if not name and m.get('employee_id'):
                eid = m['employee_id']
                if eid not in _emp_cache:
                    try:
                        from app.models.employee import Employee
                        emp = Employee.query.get(eid)
                        _emp_cache[eid] = {'name': emp.name, 'phone': getattr(emp,'phone','') or ''} if emp else {}
                    except Exception:
                        _emp_cache[eid] = {}
                name = _emp_cache[eid].get('name', '')
                phone = _emp_cache[eid].get('phone', '')
            team_data.append([role_name, name, phone])
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

def _item_row(it, is_visitor, show_ref=True):
    """Return one data row for an item. show_ref=False hides empty ref columns."""
    # Custom dimensions — only show if user entered values
    dims = []
    has_dim = False
    for f, lbl in [('width','W'), ('depth','D'), ('height','H')]:
        v = getattr(it, f, None)
        if v and float(v or 0) > 0:
            dims.append('{}{}'.format(lbl, float(v)))
            has_dim = True

    # Only show dimension string if there are actual values, or if show_ref=True
    if dims:
        dim_str = '×'.join(dims)
    elif show_ref:
        dim_str = it.spec or ''
    else:
        dim_str = ''

    # Craft annotation
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

    # Build row based on show_ref
    if show_ref:
        # Full row: 名称 | 定制尺寸/规格 | 品牌 | 单位 | 数量 | [单价] | 合计 | 工艺/备注
        brand_val = it.brand or ''
        if not brand_val:
            brand_val = ''
        row = [
            it.name or '',
            dim_str,
            brand_val,
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
    else:
        # Compact row: 名称 | 规格/尺寸 | 单位 | 数量 | [单价] | 合计 | 工艺/备注
        row = [
            it.name or '',
            dim_str,
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

def _cat_headers(is_visitor, show_ref=True):
    if show_ref:
        if is_visitor:
            return ['名称', '定制尺寸/规格', '品牌', '单位', '数量', '合计', '工艺/备注']
        return ['名称', '定制尺寸/规格', '品牌', '单位', '数量', '单价', '合计', '工艺/备注']
    else:
        if is_visitor:
            return ['名称', '规格/尺寸', '单位', '数量', '合计', '工艺/备注']
        return ['名称', '规格/尺寸', '单位', '数量', '单价', '合计', '工艺/备注']


def _cat_col_widths(is_visitor, show_ref=True):
    if show_ref:
        if is_visitor:
            return [36*mm, 26*mm, 20*mm, 14*mm, 14*mm, 22*mm, 28*mm]
        return [34*mm, 24*mm, 18*mm, 12*mm, 12*mm, 18*mm, 22*mm, 18*mm]
    else:
        if is_visitor:
            return [40*mm, 32*mm, 16*mm, 14*mm, 22*mm, 36*mm]
        return [38*mm, 28*mm, 14*mm, 14*mm, 18*mm, 22*mm, 24*mm]


def _cat_table(items, is_visitor, styles, show_ref=True):
    """Build one category section (header + item rows + subtotal)."""
    data = [_cat_headers(is_visitor)]
    total = Decimal('0')
    for it in items:
        data.append(_item_row(it, is_visitor, show_ref))
        total += Decimal(str(it.total_price or 0))

    # Subtotal row — span all but last 2 columns
    n_cols = len(_cat_col_widths(is_visitor, show_ref))
    if is_visitor:
        subtotal_row = ['-- 小计 --'] + [''] * (n_cols - 3) + [_ymoney(total), '']
    else:
        subtotal_row = ['-- 小计 --'] + [''] * (n_cols - 3) + [_ymoney(total), '']
    data.append(subtotal_row)

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
        ('SPAN',(0,-1),(-3, -1)),
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


def _category_summary_page(story, items, is_visitor, styles, show_ref=True):
    """
    分类汇总页 — 重构版：
      费用汇总区：一级分类合计 + 缩进显示各二级分类明细（仅物料金额）
      其他费用区：仅含工艺费用、管理费、税额、优惠（纯费用项目）
      最后总价大写。
    """
    from app.models.material_sku import MaterialCategory as MC
    from sqlalchemy import or_ as sql_or
    from collections import OrderedDict

    grouped = _group_by_category(items)

    # 构建有序一级分类列表
    cats = MC.query.filter(
        MC.parent_id.is_(None),
        sql_or(MC.is_deleted == False, MC.is_deleted.is_(None)),
        MC.is_enabled == True
    ).order_by(MC.sort_order).all()

    # 构建有序二级分类列表（全部启用）
    all_l2 = MC.query.filter(
        MC.parent_id.isnot(None),
        sql_or(MC.is_deleted == False, MC.is_deleted.is_(None)),
        MC.is_enabled == True
    ).order_by(MC.sort_order).all()
    l2_order = [c.name for c in all_l2]

    grand_total = Decimal('0')
    cat_rows = []       # [(一级分类名, 金额, [(二级名, 金额), ...])]

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

        # 二级分类明细（按系统顺序排列）
        l2_grouped = OrderedDict()
        for it in cat_items:
            l2 = it.category_level2 or '其他'
            l2_grouped.setdefault(l2, []).append(it)
        l2_detail = []
        for l2_name in l2_order:
            if l2_name in l2_grouped:
                l2_amt = sum(Decimal(str(it.total_price or 0)) for it in l2_grouped[l2_name])
                l2_detail.append((l2_name, l2_amt))
        # 未在系统中的二级分类
        for l2_name, l2_items in l2_grouped.items():
            if l2_name not in l2_order:
                l2_amt = sum(Decimal(str(it.total_price or 0)) for it in l2_items)
                l2_detail.append((l2_name, l2_amt))

        cat_rows.append((cat_key, ct, l2_detail))

    # 未归类的一级分类
    for gk, gitems in grouped.items():
        if not any(gk == cr[0] or CAT_MAP.get(gk) == cr[0] for cr in cat_rows):
            ct = sum(Decimal(str(it.total_price or 0)) for it in gitems)
            grand_total += ct
            display_name = CAT_MAP.get(gk, gk)
            cat_rows.append((display_name, ct, []))

    # ════════════════════════════════════════════
    #  第一部分：费用汇总（一级分类 + 二级缩进）
    # ════════════════════════════════════════════
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('<b>费用汇总</b>', styles['CNSec']))
    story.append(Spacer(1, 2*mm))

    summary_data = []
    s_style_L = ParagraphStyle('SumL', fontName=CN_FONT_BODY, fontSize=10, leading=14)
    s_style_R = ParagraphStyle('SumR', fontName=CN_FONT_BODY, fontSize=10, leading=14, alignment=TA_RIGHT)
    s_style_L2 = ParagraphStyle('SumL2', fontName=CN_FONT_BODY, fontSize=9, leading=12,
                                leftIndent=8, textColor=MID_GRAY)
    s_style_R2 = ParagraphStyle('SumR2', fontName=CN_FONT_BODY, fontSize=9, leading=12,
                                alignment=TA_RIGHT, textColor=MID_GRAY)

    for cname, amt, l2_detail in cat_rows:
        summary_data.append([Paragraph(cname, s_style_L), Paragraph(_ymoney(amt), s_style_R)])
        # 二级分类缩进显示
        for l2_name, l2_amt in l2_detail:
            summary_data.append([Paragraph(f'  ├ {l2_name}', s_style_L2), Paragraph(_ymoney(l2_amt), s_style_R2)])

    if summary_data:
        stbl = Table(summary_data, colWidths=[80*mm, 50*mm])
        stbl.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1), CN_FONT_BODY),
            ('FONTSIZE',(0,0),(-1,-1), 10),
            ('ALIGN',(0,0),(0,-1),'LEFT'),
            ('ALIGN',(1,0),(1,-1),'RIGHT'),
            ('BOTTOMPADDING',(0,0),(-1,-1), 3),
            ('TOPPADDING',(0,0),(-1,-1), 3),
            ('LINEBELOW',(0,0),(-1,-1), 0.3, LIGHT_GRAY),
        ]))
        story.append(stbl)

    # ════════════════════════════════════════════
    #  第二部分：其他费用（纯费用项，不含物料分类）
    # ════════════════════════════════════════════
    if not is_visitor:
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph('<b>其他费用</b>', styles['CNSec']))
        story.append(Spacer(1, 2*mm))

        quote = globals().get('quote_obj')

        # 计算工艺费用
        craft_total = Decimal('0')
        for it in items:
            if getattr(it, 'item_type', '') in ('craft', 'process'):
                craft_total += Decimal(str(it.total_price or 0))
                continue
            p_coef = float(getattr(it, 'process_coefficient', None) or 1)
            p_qty = float(getattr(it, 'process_quantity', None) or 0)
            p_uprice = float(getattr(it, 'process_unit_price', None) or 0)
            tp = Decimal(str(it.total_price or 0))
            if p_coef > 1 or p_qty > 0:
                base_amt = tp / Decimal(str(p_coef)) if p_coef > 1 else tp
                craft_total += (tp - base_amt) + Decimal(str(p_qty * p_uprice))

        extra_data = []
        e_style_L = ParagraphStyle('ExtL', fontName=CN_FONT_BODY, fontSize=9, leading=13)
        e_style_R = ParagraphStyle('ExtR', fontName=CN_FONT_BODY, fontSize=9, leading=13, alignment=TA_RIGHT)

        # 工艺费用
        if craft_total > 0:
            extra_data.append([
                Paragraph('工艺费用', e_style_L),
                Paragraph(_ymoney(craft_total), e_style_R),
            ])

        # 管理费
        mgmt_rate = float(getattr(quote, 'manage_rate', 0) or getattr(quote, 'management_fee_rate', 0) or 0) if quote else 0
        mgmt_fee = Decimal(str(getattr(quote, 'manage_amount', 0) or getattr(quote, 'management_fee', 0) or 0)) if quote else Decimal('0')
        if mgmt_rate and not mgmt_fee:
            mgmt_fee = (grand_total * Decimal(str(mgmt_rate))) / Decimal('100')
        if mgmt_fee > 0:
            extra_data.append([
                Paragraph(f'管理费 ({mgmt_rate}%)', e_style_L),
                Paragraph(_ymoney(mgmt_fee), e_style_R),
            ])

        # 税额
        tax_val = Decimal(str(getattr(quote, 'tax_amount', 0) or getattr(quote, 'tax', 0) or 0)) if quote else Decimal('0')
        tax_rate = float(getattr(quote, 'tax_rate', 0) or 0) if quote else 0
        if tax_rate and not tax_val:
            tax_val = ((grand_total + mgmt_fee) * Decimal(str(tax_rate))) / Decimal('100')
        if tax_val > 0:
            extra_data.append([
                Paragraph(f'税额 ({tax_rate}%)', e_style_L),
                Paragraph(_ymoney(tax_val), e_style_R),
            ])

        # 优惠
        discount_rate = float(getattr(quote, 'discount_rate', 0) or 0) if quote else 0
        discount = Decimal('0')
        if quote and discount_rate > 0:
            discount = round((grand_total + mgmt_fee) * Decimal(str(discount_rate)) / Decimal('100'), 2)
        if discount > 0:
            extra_data.append([
                Paragraph(f'优惠 ({discount_rate}%)', e_style_L),
                Paragraph('-' + _ymoney(discount), ParagraphStyle('ExtRd', fontName=CN_FONT_BODY, fontSize=9, leading=13, alignment=TA_RIGHT, textColor=colors_red)),
            ])

        if extra_data:
            etbl = Table(extra_data, colWidths=[80*mm, 50*mm])
            etbl.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1), CN_FONT_BODY),
                ('FONTSIZE',(0,0),(-1,-1), 9),
                ('ALIGN',(0,0),(0,-1),'LEFT'),
                ('ALIGN',(1,0),(1,-1),'RIGHT'),
                ('BOTTOMPADDING',(0,0),(-1,-1), 4),
                ('TOPPADDING',(0,0),(-1,-1), 4),
                ('LINEBELOW',(0,0),(-1,-1), 0.2, LIGHT_GRAY),
            ]))
            story.append(etbl)

    # ════════════════════════════════════════════
    #  第三部分：总价
    # ════════════════════════════════════════════
    final_total = grand_total
    if not is_visitor:
        final_total = round(final_total + mgmt_fee + tax_val - discount)

    story.append(Spacer(1, 8*mm))
    # 总价框
    total_label = '参考总价' if is_visitor else '本报价表合计'
    total_box_data = [[
    Paragraph(
        f'<b>{total_label}：<font color="red">{_ymoney(final_total)}</font></b>',
        ParagraphStyle('GrandTotal', fontName=CN_FONT, fontSize=16, leading=24, alignment=TA_CENTER)
    )]]
    tbox = Table(total_box_data, colWidths=[140*mm])
    tbox.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1), 1.5, BRAND_BROWN),
        ('BACKGROUND',(0,0),(-1,-1), HexColor('#FFF8F0')),
        ('TOPPADDING',(0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
    ]))
    story.append(tbox)

    # 大写
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        f'合计人民币大写：<b>{_money_to_chinese(final_total)}</b>',
        styles['CNBody']
    ))

    return final_total


def _quote_grand_total(quote, items):
    """Calculate grand total from items."""
    return sum(Decimal(str(it.total_price or 0)) for it in items)


# ─── Room detail section ─────────────────────────────────────────────────────

def _room_headers(is_visitor, show_ref=True):
    if show_ref:
        if is_visitor:
            return ['名称', '定制尺寸/规格', '品牌', '单位', '数量', '合计', '工艺/备注']
        return ['名称', '定制尺寸/规格', '品牌', '单位', '数量', '单价', '合计', '工艺/备注']
    else:
        if is_visitor:
            return ['名称', '规格/尺寸', '单位', '数量', '合计', '工艺/备注']
        return ['名称', '规格/尺寸', '单位', '数量', '单价', '合计', '工艺/备注']


ROOM_CW_V = [38*mm, 24*mm, 22*mm, 14*mm, 14*mm, 22*mm, 20*mm]   # visitor, show_ref=True (7 cols)
ROOM_CW_C = [36*mm, 22*mm, 20*mm, 12*mm, 12*mm, 18*mm, 22*mm, 18*mm]   # customer, show_ref=True (8 cols)
# Non-ref (compact) versions
ROOM_CW_V_COMPACT = [42*mm, 28*mm, 16*mm, 14*mm, 22*mm, 38*mm]   # visitor, show_ref=False (6 cols)
ROOM_CW_C_COMPACT = [40*mm, 26*mm, 14*mm, 14*mm, 18*mm, 22*mm, 24*mm]   # customer, show_ref=False (7 cols)


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
    hdr_cw = (ROOM_CW_V if is_visitor else ROOM_CW_C) if show_ref else (ROOM_CW_V_COMPACT if is_visitor else ROOM_CW_C_COMPACT)

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
        hdr_cw = (ROOM_CW_V if is_visitor else ROOM_CW_C) if show_ref else (ROOM_CW_V_COMPACT if is_visitor else ROOM_CW_C_COMPACT)
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

            # ── 分类子标题（棕色小标签）──
            cat_hdr_text = '{}  —  {}件  ¥{}'.format(cat_name, len(cat_items), _ymoney(cat_total))
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
            cmds = [
                ('FONTNAME', (0,0),(-1,0), CN_FONT),
                ('FONTNAME', (0,1),(-1,-1), CN_FONT_BODY),
                ('FONTSIZE', (0,0),(-1,-1), 7.5),
                ('BACKGROUND',(0,0),(-1,0), BRAND_BROWN),
                ('TEXTCOLOR',(0,0),(-1,0), white),
                ('GRID',(0,0),(-1,-1), 0.3, MID_GRAY),
                ('BOTTOMPADDING',(0,0),(-1,-1), 3),
                ('TOPPADDING',(0,0),(-1,-1), 3),
            ]
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
        fpath, pagesize=landscape(A4),
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
        canvas.drawString(12*mm, landscape(A4)[1] - 8*mm,
                          '\u5c1a\u6807\u00b7\u8bbe\u8bb0\u5bb6  \u62a5\u4ef7\u5355')
        canvas.drawRightString(landscape(A4)[0] - 12*mm, landscape(A4)[1] - 8*mm,
                               (quote.quote_no or '') + '  ' + ('\u5ba2\u6237\u7248' if not is_visitor else '\u53c2\u8003\u7248'))
        # Footer line
        canvas.setFillColor(MID_GRAY)
        canvas.setFont(CN_FONT_BODY, 7)
        canvas.drawString(12*mm, 8*mm, '\u2014\u2014  \u4fdd\u5bc6\u6587\u4ef6  \u2014\u2014')
        canvas.drawRightString(landscape(A4)[0] - 12*mm, 8*mm, 'p{}\u9875'.format(doc.page))
        canvas.restoreState()

    # Page 1 = cover (already built), Pages 2+ = category summary
    # Add page header to subsequent pages
    def _cat_page_header(canvas, doc):
        if doc.page == 1:
            return
        _page_header_footer(canvas, doc)

    # ── Page 2+: Category summary (简洁汇总) ──────
    final_total = _category_summary_page(story, items, is_visitor, styles, show_ref)

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
