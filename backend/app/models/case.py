"""
案例展示模块数据模型 V3.1
支持全链路案例运营：创建→编辑→发布→同步→数据分析
"""
import json

from datetime import datetime
from app import db


def _fix_garbled(text):
    """修复数据库存储时的编码损坏（UTF-8/GBK混用导致）"""
    if not isinstance(text, str) or not text:
        return text
    try:
        text.encode('gbk')
        return text
    except UnicodeEncodeError:
        pass
    try:
        return text.encode('latin1').decode('gbk')
    except (UnicodeDecodeError, AttributeError):
        try:
            return text.encode('latin1').decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            return text


class CaseStudy(db.Model):
    """案例主表"""
    __tablename__ = 'case_study'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_no = db.Column(db.String(50), unique=True, comment='案例编号')
    
    # 基础信息
    title = db.Column(db.String(200), nullable=False, comment='案例标题')
    type = db.Column(db.String(20), default='实景', comment='案例类型')
    style = db.Column(db.String(50), comment='风格标签')
    atmosphere = db.Column(db.String(20), comment='氛围分类')  # 温馨/清新/简约/浪漫/雅致/沉稳
    scene_tags = db.Column(db.Text, comment='场景标签JSON数组')  # 美食烹饪/游戏聚会/音乐乐器/办公学习/亲子陪伴
    space_type = db.Column(db.String(50), comment='空间类型')
    budget_range = db.Column(db.String(50), comment='预算区间')
    area = db.Column(db.Numeric(10, 2), comment='面积(㎡)')
    house_type = db.Column(db.String(50), comment='户型')
    
    # 位置信息
    location = db.Column(db.String(200), comment='小区/楼盘名称')
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), comment='关联楼盘ID')
    address = db.Column(db.String(500), comment='详细地址')
    
    # 客户信息
    customer_name = db.Column(db.String(100), comment='客户称呼(脱敏)')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), comment='关联客户ID')
    
    # 视觉素材
    cover_image = db.Column(db.String(500), comment='封面图URL')
    vr_link = db.Column(db.String(500), comment='360VR链接')
    
   
    
    # 配色方案
    main_colors = db.Column(db.Text, comment='方案主色JSON数组(最多5个)')
    auxiliary_colors = db.Column(db.Text, comment='方案辅助色JSON数组(最多5个)')
    accent_colors = db.Column(db.Text, comment='方案点缀色JSON数组(最多5个)')
    background_colors = db.Column(db.Text, comment='方案背景色JSON数组(最多6个)')
    
    # 报价配置
    total_price = db.Column(db.Numeric(12, 2), comment='全案总价')
    deal_budget = db.Column(db.Numeric(12, 2), comment='成交型预算')
    package_type = db.Column(db.String(50), comment='套餐配置')
    price_detail = db.Column(db.Text, comment='造价明细JSON')
    material_list = db.Column(db.Text, comment='材料清单JSON')
    
    # 施工信息
    construction_phase = db.Column(db.String(50), comment='施工阶段')
    owner_authorized = db.Column(db.Boolean, default=False, comment='业主授权状态')
    
    # 状态管理
    status = db.Column(db.String(20), default='草稿', comment='状态:草稿/已发布/已下架')
    is_public = db.Column(db.Boolean, default=True, comment='是否公开')
    is_featured = db.Column(db.Boolean, default=False, comment='是否精选')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    top_position = db.Column(db.Integer, comment='置顶位置(1-3)')
    publish_time = db.Column(db.DateTime, comment='发布时间')
    scheduled_time = db.Column(db.DateTime, comment='定时发布时间')
    
    # 同步状态
    sync_xiaohongshu = db.Column(db.Boolean, default=False, comment='同步小红书')
    sync_mp = db.Column(db.Boolean, default=False, comment='同步公众号')
    
    # 订阅通知
    enable_subscription = db.Column(db.Boolean, default=True, comment='开启订阅')
    enable_notify = db.Column(db.Boolean, default=True, comment='微信通知开关')
    
    # 数据统计
    view_count = db.Column(db.Integer, default=0, comment='浏览次数')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    subscription_count = db.Column(db.Integer, default=0, comment='订阅数')
    lead_count = db.Column(db.Integer, default=0, comment='留资数')
    consult_count = db.Column(db.Integer, default=0, comment='咨询数')
    download_count = db.Column(db.Integer, default=0, comment='下载数')
    share_count = db.Column(db.Integer, default=0, comment='分享数')
    
    # 负责人
    responsible_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='负责人ID')
    
    # 服务团队
    planner_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='全案规划师ID')
    designer_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='全案设计师ID')
    vr_qrcode = db.Column(db.String(500), comment='VR二维码图片URL')
    storage_plan = db.Column(db.Text, comment='收纳规划方案')
    execution_detail = db.Column(db.Text, comment='全案落地执行细节')

    # 多图轮播和图集
    hero_images = db.Column(db.Text, comment='英雄图JSON数组(最多5张)')
    gallery = db.Column(db.Text, comment='瀑布流图集JSON数组')

    # 幻灯片模板引用
    slide_template_id = db.Column(db.Integer, db.ForeignKey('slide_templates.id'), comment='幻灯片模板ID')

    # 系统字段
    tenant_id = db.Column(db.String(20), comment='租户ID')
    is_real_case = db.Column(db.Boolean, default=False, comment='是否真实案例(自动)')
    enable_public_workflow = db.Column(db.Boolean, default=False, comment='是否公开服务流程')
    workflow_id = db.Column(db.Integer, db.ForeignKey('customer_workflow.id'), comment='关联服务流程ID')
    quote_id = db.Column(db.Integer, comment='关联报价表ID')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, comment='软删除时间')

    # 关联关系
    media = db.relationship('CaseMedia', backref='case', lazy='dynamic',
                           cascade='all, delete-orphan')
    timeline = db.relationship('CaseTimeline', backref='case', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='CaseTimeline.node_time')
    files = db.relationship('CaseFile', backref='case', lazy='dynamic',
                           cascade='all, delete-orphan')
    subscriptions = db.relationship('CaseSubscription', backref='case', lazy='dynamic',
                                   cascade='all, delete-orphan')
    leads = db.relationship('CaseLead', backref='case', lazy='dynamic',
                           cascade='all, delete-orphan')
    planner = db.relationship('Employee', foreign_keys=[planner_id], backref='planned_cases')
    designer = db.relationship('Employee', foreign_keys=[designer_id], backref='designed_cases')
    responsible = db.relationship('Employee', foreign_keys=[responsible_id], backref='responsible_cases')
    building = db.relationship('Building', backref='cases')

    def to_dict(self, include_relations=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'case_no': _fix_garbled(self.case_no),
            'title': _fix_garbled(self.title),
            'type': _fix_garbled(self.type),
            'style': _fix_garbled(self.style),
            'atmosphere': _fix_garbled(self.atmosphere),
            'scene_tags': json.loads(self.scene_tags) if self.scene_tags else [],
            'space_type': _fix_garbled(self.space_type),
            'budget_range': _fix_garbled(self.budget_range),
            'area': float(self.area) if self.area else None,
            'house_type': _fix_garbled(self.house_type),
            'location': _fix_garbled(self.location),
            'building_id': self.building_id,
            'address': _fix_garbled(self.address),
            'customer_name': _fix_garbled(self.customer_name),
            'customer_id': self.customer_id,
            'cover_image': self.cover_image,
            'vr_link': self.vr_link,
            'main_colors': json.loads(self.main_colors) if self.main_colors else [],
            'auxiliary_colors': json.loads(self.auxiliary_colors) if self.auxiliary_colors else [],
            'accent_colors': json.loads(self.accent_colors) if self.accent_colors else [],
            'background_colors': json.loads(self.background_colors) if self.background_colors else [],
            'total_price': float(self.total_price) if self.total_price else None,
            'deal_budget': float(self.deal_budget) if self.deal_budget else None,
            'package_type': _fix_garbled(self.package_type),
            'price_detail': self.price_detail,
            'material_list': self.material_list,
            'construction_phase': _fix_garbled(self.construction_phase),
            'owner_authorized': self.owner_authorized,
            'status': _fix_garbled(self.status),
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'is_top': self.is_top,
            'top_position': self.top_position,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'sync_xiaohongshu': self.sync_xiaohongshu,
            'sync_mp': self.sync_mp,
            'enable_subscription': self.enable_subscription,
            'enable_notify': self.enable_notify,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'subscription_count': self.subscription_count,
            'lead_count': self.lead_count,
            'consult_count': self.consult_count,
            'download_count': self.download_count,
            'share_count': self.share_count,
            'responsible_id': self.responsible_id,
            'workflow_id': self.workflow_id,
            'quote_id': self.quote_id,
            'is_real_case': self.is_real_case,
            'enable_public_workflow': self.enable_public_workflow,
            'planner_id': self.planner_id,
            'designer_id': self.designer_id,
            'vr_qrcode': self.vr_qrcode,
            'storage_plan': _fix_garbled(self.storage_plan),
            'execution_detail': _fix_garbled(self.execution_detail),
            'planner': {'id': self.planner.id, 'name': _fix_garbled(self.planner.name), 'title': _fix_garbled(self.planner.title), 'bio': _fix_garbled(self.planner.bio), 'avatar': self.planner.avatar, 'showcase_photo': self.planner.showcase_photo} if self.planner else None,
            'designer': {'id': self.designer.id, 'name': _fix_garbled(self.designer.name), 'title': _fix_garbled(self.designer.title), 'bio': _fix_garbled(self.designer.bio), 'avatar': self.designer.avatar, 'showcase_photo': self.designer.showcase_photo} if self.designer else None,
            'responsible': {'id': self.responsible.id, 'name': _fix_garbled(self.responsible.name), 'title': _fix_garbled(self.responsible.title), 'bio': _fix_garbled(self.responsible.bio), 'avatar': self.responsible.avatar, 'showcase_photo': self.responsible.showcase_photo} if self.responsible else None,
            'building_name': _fix_garbled(self.building.name) if self.building_id and self.building else None,
            'hero_images': json.loads(self.hero_images) if self.hero_images else [],
            'gallery': json.loads(self.gallery) if self.gallery else [],
            'slide_template_id': self.slide_template_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relations:
            data['media'] = [m.to_dict() for m in self.media.order_by(CaseMedia.sort_order)]
            data['timeline'] = [t.to_dict() for t in self.timeline]
            data['files'] = [f.to_dict() for f in self.files]

            # workflow progress summary
            if self.is_real_case and self.enable_public_workflow:
                tl_nodes = CaseWorkflowTimeline.query.filter_by(
                    case_id=self.id
                ).order_by(CaseWorkflowTimeline.phase_order).all()
                if tl_nodes:
                    total = len(tl_nodes)
                    completed = sum(1 for n in tl_nodes if n.status == 'completed')
                    ongoing = sum(1 for n in tl_nodes if n.status == 'ongoing')
                    progress_pct = round(completed / total * 100) if total > 0 else 0
                    # find current phase
                    current_phase = ''
                    phase_order = 0
                    for n in tl_nodes:
                        if n.status == 'ongoing':
                            current_phase = n.phase
                            phase_order = n.phase_order
                            break
                    if not current_phase and completed > 0:
                        last_done = [n for n in tl_nodes if n.status == 'completed'][-1]
                        current_phase = last_done.phase
                        phase_order = last_done.phase_order
                    # group by phase
                    phases = []
                    seen = set()
                    for n in tl_nodes:
                        if n.phase not in seen:
                            seen.add(n.phase)
                            phase_nodes = [x for x in tl_nodes if x.phase == n.phase]
                            p_completed = sum(1 for x in phase_nodes if x.status == 'completed')
                            phases.append({
                                'name': n.phase,
                                'phase_order': n.phase_order,
                                'total_nodes': len(phase_nodes),
                                'completed_nodes': p_completed,
                                'status': 'completed' if p_completed == len(phase_nodes) else ('ongoing' if any(x.status == 'ongoing' for x in phase_nodes) else 'pending')
                            })
                    data['workflow_progress'] = {
                        'total_nodes': total,
                        'completed_nodes': completed,
                        'ongoing_nodes': ongoing,
                        'progress_pct': progress_pct,
                        'current_phase': current_phase,
                        'phase_order': phase_order,
                        'phases': phases
                    }
                    data['workflow_timeline'] = [n.to_dict() for n in tl_nodes if n.is_public]

        return data

    def increment_view(self):
        """增加浏览量"""
        self.view_count += 1
        db.session.commit()

    def increment_likes(self):
        """增加点赞数"""
        self.like_count += 1
        db.session.commit()

    def soft_delete(self):
        """软删除"""
        self.deleted_at = datetime.utcnow()
        self.status = '已删除'
        db.session.commit()


class CaseMedia(db.Model):
    """案例媒体表"""
    __tablename__ = 'case_media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    media_type = db.Column(db.String(20), comment='媒体类型: image/video')
    url = db.Column(db.String(500), nullable=False, comment='文件URL')
    thumbnail = db.Column(db.String(500), comment='缩略图')
    # 自定义/材质
    custom_name = db.Column(db.String(200), comment='自定义商品名称')
    material = db.Column(db.String(100), comment='材质')
    custom_measure = db.Column(db.String(100), comment='定制计量值')

    sort_order = db.Column(db.Integer, default=0, comment='排序')
    description = db.Column(db.String(500), comment='说明')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'media_type': self.media_type,
            'url': self.url,
            'thumbnail': self.thumbnail,
            'sort_order': self.sort_order,
            'description': self.description,
        }


class CaseTimeline(db.Model):
    """案例时间轴表"""
    __tablename__ = 'case_timeline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    node_time = db.Column(db.DateTime, nullable=False, comment='时间节点')
    title = db.Column(db.String(100), comment='节点标题')
    content = db.Column(db.Text, comment='内容')
    media_urls = db.Column(db.Text, comment='图片/视频JSON数组')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'node_time': self.node_time.isoformat() if self.node_time else None,
            'title': self.title,
            'content': self.content,
            'media_urls': self.media_urls,
            'sort_order': self.sort_order,
        }


class CaseFile(db.Model):
    """案例文件表"""
    __tablename__ = 'case_files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    file_type = db.Column(db.String(20), comment='文件类型: pdf/image/video')
    file_name = db.Column(db.String(200), comment='文件名')
    file_url = db.Column(db.String(500), comment='文件URL')
    has_watermark = db.Column(db.Boolean, default=False, comment='是否有水印')
    download_count = db.Column(db.Integer, default=0, comment='下载次数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'has_watermark': self.has_watermark,
            'download_count': self.download_count,
        }


class CaseSubscription(db.Model):
    """案例订阅表"""
    __tablename__ = 'case_subscriptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    user_id = db.Column(db.Integer, comment='注册用户ID')
    openid = db.Column(db.String(100), comment='微信openid')
    phone = db.Column(db.String(20), comment='订阅手机号')
    email = db.Column(db.String(100), comment='订阅邮箱')
    subscribe_time = db.Column(db.DateTime, default=datetime.utcnow, comment='订阅时间')
    notify_enabled = db.Column(db.Boolean, default=True, comment='是否接收通知')
    last_notify_time = db.Column(db.DateTime, comment='最后通知时间')

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'user_id': self.user_id,
            'openid': self.openid,
            'phone': self.phone,
            'email': self.email,
            'subscribe_time': self.subscribe_time.isoformat() if self.subscribe_time else None,
            'notify_enabled': self.notify_enabled,
            'tenant_id': self.tenant_id,
        }


class CaseLead(db.Model):
    """客资留资表"""
    __tablename__ = 'case_leads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    name = db.Column(db.String(100), comment='姓名')
    phone = db.Column(db.String(20), comment='手机号')
    email = db.Column(db.String(100), comment='邮箱')
    wechat = db.Column(db.String(100), comment='微信号')
    source = db.Column(db.String(50), comment='来源: pdf_download/view_detail/consult/subscribe')
    message = db.Column(db.Text, comment='留言内容')
    status = db.Column(db.String(20), default='new', comment='状态: new/contacted/converted/invalid')
    contacted_at = db.Column(db.DateTime, comment='联系时间')
    converted_at = db.Column(db.DateTime, comment='转化时间')
    remark = db.Column(db.Text, comment='跟进备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'wechat': self.wechat,
            'source': self.source,
            'message': self.message,
            'status': self.status,
            'contacted_at': self.contacted_at.isoformat() if self.contacted_at else None,
            'converted_at': self.converted_at.isoformat() if self.converted_at else None,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CaseTemplate(db.Model):
    """案例模板表"""
    __tablename__ = 'case_templates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template_name = db.Column(db.String(200), comment='模板名称')
    package_type = db.Column(db.String(50), comment='套餐类型')
    price_min = db.Column(db.Numeric(12, 2), comment='价格区间-最小')
    price_max = db.Column(db.Numeric(12, 2), comment='价格区间-最大')
    suitable_house_types = db.Column(db.Text, comment='适用户型JSON数组')
    base_content = db.Column(db.Text, comment='基础文案内容JSON')
    sample_images = db.Column(db.Text, comment='示例图片JSON数组')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'template_name': self.template_name,
            'package_type': self.package_type,
            'price_min': float(self.price_min) if self.price_min else None,
            'price_max': float(self.price_max) if self.price_max else None,
            'suitable_house_types': self.suitable_house_types,
            'base_content': self.base_content,
            'sample_images': self.sample_images,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CaseNotification(db.Model):
    """推送记录表"""
    __tablename__ = 'case_notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    notify_type = db.Column(db.String(20), comment='类型: auto/manual')
    content = db.Column(db.Text, comment='通知内容')
    send_time = db.Column(db.DateTime, comment='发送时间')
    send_status = db.Column(db.String(20), default='pending', comment='状态: pending/sent/failed')
    receiver_count = db.Column(db.Integer, default=0, comment='接收人数')
    success_count = db.Column(db.Integer, default=0, comment='成功数')
    fail_count = db.Column(db.Integer, default=0, comment='失败数')
    error_msg = db.Column(db.Text, comment='错误信息')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'notify_type': self.notify_type,
            'content': self.content,
            'send_time': self.send_time.isoformat() if self.send_time else None,
            'send_status': self.send_status,
            'receiver_count': self.receiver_count,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
        }


class CaseWorkflowTimeline(db.Model):
    """案例服务流程时间轴"""
    __tablename__ = 'case_workflow_timeline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    workflow_id = db.Column(db.Integer, db.ForeignKey('customer_workflow.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), nullable=False)
    node_code = db.Column(db.String(20))
    node_name = db.Column(db.String(100))
    phase = db.Column(db.String(50))
    phase_order = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')
    # pending/ongoing/completed
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    photos = db.Column(db.Text, default='[]')
    renderings = db.Column(db.Text, default='[]')
    notes = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json as _json
        return {
            'id': self.id,
            'case_id': self.case_id,
            'workflow_id': self.workflow_id,
            'node_id': self.node_id,
            'node_code': self.node_code,
            'node_name': self.node_name,
            'phase': self.phase,
            'phase_order': self.phase_order,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'photos': json.loads(self.photos) if self.photos else [],
            'renderings': json.loads(self.renderings) if self.renderings else [],
            'notes': self.notes,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CaseOperationLog(db.Model):
    """操作日志表"""
    __tablename__ = 'case_operation_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'))
    operator_id = db.Column(db.Integer, comment='操作人ID')
    operator_name = db.Column(db.String(100), comment='操作人姓名')
    operation = db.Column(db.String(50), comment='操作类型')
    content = db.Column(db.Text, comment='操作内容')
    ip_address = db.Column(db.String(50), comment='IP地址')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'operation': self.operation,
            'content': self.content,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class MorandiPalette(db.Model):
    """莫兰迪色卡表"""
    __tablename__ = 'morandi_palette'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_key = db.Column(db.String(30), nullable=False, comment='色系英文key')
    group_name = db.Column(db.String(30), nullable=False, comment='色系中文名')
    name_cn = db.Column(db.String(30), nullable=False, comment='颜色中文名')
    hex_value = db.Column(db.String(7), nullable=False, comment='HEX色值')
    pantone_code = db.Column(db.String(30), comment='潘通色号')
    sort_order = db.Column(db.Integer, default=0, comment='排序')

    def to_dict(self):
        return {
            'id': self.id,
            'group_key': self.group_key,
            'group_name': self.group_name,
            'name_cn': self.name_cn,
            'hex_value': self.hex_value,
            'pantone_code': self.pantone_code,
            'sort_order': self.sort_order,
        }


class PantoneColorMap(db.Model):
    """潘通色号与RGB映射表"""
    __tablename__ = 'pantone_color_map'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pantone_code = db.Column(db.String(30), nullable=False, unique=True, comment='潘通色号')
    hex_value = db.Column(db.String(7), nullable=False, comment='HEX色值')
    name_cn = db.Column(db.String(50), comment='颜色中文名')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pantone_code': self.pantone_code,
            'hex_value': self.hex_value,
            'name_cn': self.name_cn,
        }


class CasePhase(db.Model):
    """案例阶段内容表 - V3.2 视觉素材6阶段"""
    __tablename__ = 'case_phases'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    phase_number = db.Column(db.Integer, nullable=False, comment='阶段编号1-6')
    phase_name = db.Column(db.String(50), comment='阶段名称')

    # 阶段1：户型分析
    layout_images = db.Column(db.Text, comment='户型图JSON数组')
    layout_analysis = db.Column(db.Text, comment='户型分析文案(富文本)')

    # 阶段2：设计意境
    mood_images = db.Column(db.Text, comment='意境图JSON数组(≤10张)')
    mood_text = db.Column(db.Text, comment='客户需求文案(富文本)')

    # 阶段3：平面规划
    plan_image = db.Column(db.String(500), comment='平面规划图URL')
    plan_text = db.Column(db.Text, comment='规划文案(富文本)')

    # 阶段4：鸟瞰展示
    birdview_images = db.Column(db.Text, comment='鸟瞰图JSON数组(≤4张)')

    # 阶段5：效果图首页
    showcase_images = db.Column(db.Text, comment='设计意向图JSON数组(≤10张)')
    showcase_title1 = db.Column(db.String(200), comment='一级标题')
    showcase_title2 = db.Column(db.String(200), comment='二级标题')
    showcase_text_cn = db.Column(db.Text, comment='中文文案')
    showcase_text_en = db.Column(db.Text, comment='英文文案')

    # 阶段7：材质展示
    material_gallery = db.Column(db.Text, comment='材质图JSON数组')
    material_specs = db.Column(db.Text, comment='材质规格说明(富文本)')

    # 阶段8：物料展示
    product_gallery = db.Column(db.Text, comment='物料图JSON数组')
    product_list = db.Column(db.Text, comment='物料清单JSON(引用物料库)')

    # 阶段9：工法展示
    process_gallery = db.Column(db.Text, comment='工法图JSON数组')
    process_desc = db.Column(db.Text, comment='工艺说明(富文本)')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'phase_number': self.phase_number,
            'phase_name': self.phase_name,
            'layout_images': json.loads(self.layout_images) if self.layout_images else [],
            'layout_analysis': self.layout_analysis,
            'mood_images': json.loads(self.mood_images) if self.mood_images else [],
            'mood_text': self.mood_text,
            'plan_image': self.plan_image,
            'plan_text': self.plan_text,
            'birdview_images': json.loads(self.birdview_images) if self.birdview_images else [],
            'showcase_images': json.loads(self.showcase_images) if self.showcase_images else [],
            'showcase_title1': self.showcase_title1,
            'showcase_title2': self.showcase_title2,
            'showcase_text_cn': self.showcase_text_cn,
            'showcase_text_en': self.showcase_text_en,
            # 阶段7：材质展示
            'material_gallery': json.loads(self.material_gallery) if self.material_gallery else [],
            'material_specs': self.material_specs,
            # 阶段8：物料展示
            'product_gallery': json.loads(self.product_gallery) if self.product_gallery else [],
            'product_list': json.loads(self.product_list) if self.product_list else [],
            # 阶段9：工法展示
            'process_gallery': json.loads(self.process_gallery) if self.process_gallery else [],
            'process_desc': self.process_desc,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CaseSpaceRendering(db.Model):
    """空间效果图分组表 - V3.2 阶段6"""
    __tablename__ = 'case_space_renderings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False)
    space_name = db.Column(db.String(100), nullable=False, comment='空间名称')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联效果图列表
    items = db.relationship('CaseRenderingItem', backref='space', lazy='dynamic',
                          cascade='all, delete-orphan', order_by='CaseRenderingItem.sort_order')

    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'case_id': self.case_id,
            'space_name': self.space_name,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_items:
            data['renderings'] = [item.to_dict() for item in self.items]
        return data


class CaseRenderingItem(db.Model):
    """效果图详情表 - V3.2 阶段6"""
    __tablename__ = 'case_rendering_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    space_id = db.Column(db.Integer, db.ForeignKey('case_space_renderings.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False, comment='图片URL')
    title = db.Column(db.String(200), comment='标题')
    description = db.Column(db.Text, comment='简介(富文本)')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'space_id': self.space_id,
            'image_url': self.image_url,
            'title': self.title,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CaseSpaceMaterial(db.Model):
    """空间物料配置表 - V3.3 阶段6增强"""
    __tablename__ = 'case_space_materials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    space_id = db.Column(db.Integer, db.ForeignKey('case_space_renderings.id'), nullable=False, comment='空间ID')
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False, comment='案例ID')

    # 空间信息
    space_name = db.Column(db.String(100), comment='空间名称(冗余)')
    room_name = db.Column(db.String(50), comment='房间类型')

    # 引用物料库
    sku_id = db.Column(db.Integer, comment='关联物料SKU ID')
    sku_code = db.Column(db.String(50), comment='物料编号')
    material_name = db.Column(db.String(200), comment='物料名称')
    material_image = db.Column(db.String(500), comment='物料图片URL')

    # 分类
    category_level1 = db.Column(db.String(50), comment='大类')
    category_level2 = db.Column(db.String(50), comment='中类')
    category_level3 = db.Column(db.String(50), comment='小类')

    # 规格信息
    brand = db.Column(db.String(100), comment='品牌')
    spec = db.Column(db.String(200), comment='规格')
    unit = db.Column(db.String(20), comment='单位')

    # 环保/供应链
    env_level = db.Column(db.String(50), comment='环保等级')
    supply_chain = db.Column(db.String(100), comment='供应链/采购渠道')
    color_name = db.Column(db.String(100), comment='花色')

    # 自定义字段
    custom_name = db.Column(db.String(200), comment='自定义商品名称')
    material = db.Column(db.String(100), comment='材质')
    custom_measure = db.Column(db.String(100), comment='定制计量值')

    # 尺寸
    width = db.Column(db.Numeric(10, 2), comment='宽度(mm)')
    depth = db.Column(db.Numeric(10, 2), comment='深度(mm)')
    height = db.Column(db.Numeric(10, 2), comment='高度(mm)')

    # 用量/价格
    quantity = db.Column(db.Numeric(10, 2), default=1, comment='数量')
    unit_price = db.Column(db.Numeric(10, 2), default=0, comment='单价')
    total_price = db.Column(db.Numeric(12, 2), default=0, comment='总价')

    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # 查询原始SKU名称（db 已在模块顶部 from app import db 导入）
        sku_name = ''
        try:
            from sqlalchemy import text as sa_text
            sku_row = db.session.execute(
                sa_text('SELECT name FROM material_sku WHERE id = :sid'),
                {'sid': self.sku_id}
            ).fetchone()
            if sku_row and sku_row[0]:
                sku_name = sku_row[0]
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f'[CaseSpaceMaterial.to_dict] sku_name query failed: sku_id={self.sku_id}, error={e}')
        return {
            'id': self.id,
            'space_id': self.space_id,
            'case_id': self.case_id,
            'space_name': self.space_name,
            'room_name': self.room_name,
            'sku_id': self.sku_id,
            'sku_code': self.sku_code,
            'sku_name': sku_name,
            'material_name': self.material_name,
            'material_image': self.material_image,
            'category_level1': self.category_level1,
            'category_level2': self.category_level2,
            'category_level3': self.category_level3,
            'brand': self.brand,
            'spec': self.spec,
            'unit': self.unit,
            'env_level': self.env_level,
            'supply_chain': self.supply_chain,
            'color_name': self.color_name,
            'custom_name': self.custom_name or '',
            'material': self.material or '',
            'custom_measure': self.custom_measure or '',
            'width': float(self.width) if self.width else None,
            'depth': float(self.depth) if self.depth else None,
            'height': float(self.height) if self.height else None,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CaseSlideConfig(db.Model):
    """案例幻灯片配置表 - V3.4"""
    __tablename__ = 'case_slide_configs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), nullable=False, unique=True, comment='案例ID')
    template_id = db.Column(db.Integer, db.ForeignKey('slide_templates.id'), comment='关联幻灯片模板')

    # 幻灯片模板/风格配置
    template_style = db.Column(db.String(50), default='dark', comment='模板风格')
    primary_color = db.Column(db.String(7), default='#8B4513', comment='主色调')

    # 幻灯片画幅比例
    aspect_ratio = db.Column(db.String(10), default='16:9', comment='画幅比例: 16:9/21:9/4:3')

    # 封面配置
    cover_title = db.Column(db.String(200), comment='封面标题(可覆盖)')
    cover_subtitle = db.Column(db.String(200), comment='封面副标题')
    cover_bg_image = db.Column(db.String(500), comment='封面背景图URL')
    brand_name = db.Column(db.String(100), default='DESIGNARY', comment='品牌名称')

    # 内页背景图（默认）
    inner_bg_image = db.Column(db.String(500), comment='内页默认背景图URL')

    # 封底配置
    back_bg_image = db.Column(db.String(500), comment='封底背景图URL')

    # 关于我们模板配置
    about_title = db.Column(db.String(200), default='关于我们', comment='关于我们标题')
    about_subtitle = db.Column(db.String(200), comment='关于我们副标题')
    about_content = db.Column(db.Text, comment='关于我们内容(富文本)')
    about_image = db.Column(db.String(500), comment='关于我们图片URL')

    # 页面开关
    show_about = db.Column(db.Boolean, default=True, comment='显示关于我们')
    show_team = db.Column(db.Boolean, default=True, comment='显示团队展示')
    show_toc = db.Column(db.Boolean, default=True, comment='显示目录')
    show_material = db.Column(db.Boolean, default=True, comment='显示材质展示')
    show_product = db.Column(db.Boolean, default=True, comment='显示物料展示')
    show_process = db.Column(db.Boolean, default=True, comment='显示工法展示')
    show_summary = db.Column(db.Boolean, default=True, comment='显示物料汇总')

    # 材质展示配置
    showcase_material_ids = db.Column(db.JSON, default=list, comment='材质展示选中的SKU ID列表')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'template_id': self.template_id,
            'template_style': self.template_style,
            'primary_color': self.primary_color,
            'aspect_ratio': self.aspect_ratio,
            'cover_title': self.cover_title,
            'cover_subtitle': self.cover_subtitle,
            'cover_bg_image': self.cover_bg_image,
            'brand_name': self.brand_name,
            'inner_bg_image': self.inner_bg_image,
            'back_bg_image': self.back_bg_image,
            'about_title': self.about_title,
            'about_subtitle': self.about_subtitle,
            'about_content': self.about_content,
            'about_image': self.about_image,
            'show_about': self.show_about,
            'show_team': self.show_team,
            'show_toc': self.show_toc,
            'show_material': self.show_material,
            'show_product': self.show_product,
            'show_process': self.show_process,
            'show_summary': self.show_summary,
            'showcase_material_ids': self.showcase_material_ids or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SlideTemplate(db.Model):
    """幻灯片模板表 - V3.4 公共模板系统"""
    __tablename__ = 'slide_templates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='模板名称')
    description = db.Column(db.Text, comment='模板描述')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认模板')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')

    # 幻灯片风格配置
    template_style = db.Column(db.String(50), default='dark', comment='模板风格: dark/light/minimal')
    primary_color = db.Column(db.String(7), default='#8B4513', comment='主色调')

    # 幻灯片画幅比例
    aspect_ratio = db.Column(db.String(10), default='16:9', comment='画幅比例: 16:9/21:9/4:3')

    # 封面配置
    cover_title = db.Column(db.String(200), comment='封面标题(可覆盖)')
    cover_subtitle = db.Column(db.String(200), comment='封面副标题')
    cover_bg_image = db.Column(db.String(500), comment='封面背景图URL')
    brand_name = db.Column(db.String(100), default='DESIGNARY', comment='品牌名称')

    # 内页背景图（默认）
    inner_bg_image = db.Column(db.String(500), comment='内页默认背景图URL')

    # 封底配置
    back_bg_image = db.Column(db.String(500), comment='封底背景图URL')

    # 关于我们模板配置
    about_title = db.Column(db.String(200), default='关于我们', comment='关于我们标题')
    about_subtitle = db.Column(db.String(200), comment='关于我们副标题')
    about_content = db.Column(db.Text, comment='关于我们内容(富文本)')
    about_image = db.Column(db.String(500), comment='关于我们图片URL')

    # 页面开关
    show_about = db.Column(db.Boolean, default=True, comment='显示关于我们')
    show_team = db.Column(db.Boolean, default=True, comment='显示团队展示')
    show_toc = db.Column(db.Boolean, default=True, comment='显示目录')
    show_material = db.Column(db.Boolean, default=True, comment='显示材质展示')
    show_product = db.Column(db.Boolean, default=True, comment='显示物料展示')
    show_process = db.Column(db.Boolean, default=True, comment='显示工法展示')
    show_summary = db.Column(db.Boolean, default=True, comment='显示物料汇总')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'template_style': self.template_style,
            'primary_color': self.primary_color,
            'aspect_ratio': self.aspect_ratio,
            'cover_title': self.cover_title,
            'cover_subtitle': self.cover_subtitle,
            'cover_bg_image': self.cover_bg_image,
            'brand_name': self.brand_name,
            'inner_bg_image': self.inner_bg_image,
            'back_bg_image': self.back_bg_image,
            'about_title': self.about_title,
            'about_subtitle': self.about_subtitle,
            'about_content': self.about_content,
            'about_image': self.about_image,
            'show_about': self.show_about,
            'show_team': self.show_team,
            'show_toc': self.show_toc,
            'show_material': self.show_material,
            'show_product': self.show_product,
            'show_process': self.show_process,
            'show_summary': self.show_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
