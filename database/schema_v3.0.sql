-- ============================================
-- 梵木里全案服务系统 V3.0 数据库脚本
-- 创建日期: 2026-04-25
-- 版本: v3.0.0
-- ============================================

-- 开启外键约束
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. 案例展示模块
-- ============================================

-- 案例主表
CREATE TABLE IF NOT EXISTS case_study (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) DEFAULT '实景',
    style VARCHAR(50),
    space_type VARCHAR(50),
    budget_range VARCHAR(50),
    area DECIMAL(10,2),
    cover_image VARCHAR(500),
    location VARCHAR(200),
    customer_name VARCHAR(100),
    description TEXT,
    tags TEXT,
    is_featured BOOLEAN DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT '草稿',
    tenant_id VARCHAR(20),
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 案例媒体表
CREATE TABLE IF NOT EXISTS case_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    media_type VARCHAR(20),
    url VARCHAR(500) NOT NULL,
    thumbnail VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    description VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
);

-- 案例索引
CREATE INDEX IF NOT EXISTS idx_case_type ON case_study(type);
CREATE INDEX IF NOT EXISTS idx_case_style ON case_study(style);
CREATE INDEX IF NOT EXISTS idx_case_status ON case_study(status);
CREATE INDEX IF NOT EXISTS idx_case_featured ON case_study(is_featured);
CREATE INDEX IF NOT EXISTS idx_case_tenant ON case_study(tenant_id);
CREATE INDEX IF NOT EXISTS idx_media_case ON case_media(case_id);

-- ============================================
-- 2. 留资引导模块
-- ============================================

-- 留资线索表
CREATE TABLE IF NOT EXISTS lead (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    phone VARCHAR(20) UNIQUE NOT NULL,
    source VARCHAR(50),
    source_id INTEGER,
    source_page VARCHAR(200),
    intention TEXT,
    budget VARCHAR(50),
    house_type VARCHAR(50),
    area VARCHAR(50),
    status VARCHAR(20) DEFAULT '新线索',
    assigned_to INTEGER,
    follow_count INTEGER DEFAULT 0,
    first_contact_at DATETIME,
    last_follow_at DATETIME,
    remark TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    tenant_id VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 线索跟进记录表
CREATE TABLE IF NOT EXISTS lead_follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    follow_type VARCHAR(20),
    content TEXT,
    next_follow_at DATETIME,
    operator_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES lead(id) ON DELETE CASCADE
);

-- 线索索引
CREATE INDEX IF NOT EXISTS idx_lead_phone ON lead(phone);
CREATE INDEX IF NOT EXISTS idx_lead_status ON lead(status);
CREATE INDEX IF NOT EXISTS idx_lead_source ON lead(source);
CREATE INDEX IF NOT EXISTS idx_lead_assigned ON lead(assigned_to);
CREATE INDEX IF NOT EXISTS idx_lead_tenant ON lead(tenant_id);
CREATE INDEX IF NOT EXISTS idx_lead_created ON lead(created_at);
CREATE INDEX IF NOT EXISTS idx_follow_lead ON lead_follow(lead_id);

-- ============================================
-- 3. 预约量尺模块
-- ============================================

-- 预约表
CREATE TABLE IF NOT EXISTS appointment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    house_address VARCHAR(200),
    house_type VARCHAR(50),
    area VARCHAR(50),
    budget VARCHAR(50),
    appointment_date DATE,
    appointment_time TIME,
    status VARCHAR(20) DEFAULT '待确认',
    assigned_to INTEGER,
    remark TEXT,
    cancel_reason TEXT,
    ip_address VARCHAR(50),
    tenant_id VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 预约索引
CREATE INDEX IF NOT EXISTS idx_appointment_phone ON appointment(phone);
CREATE INDEX IF NOT EXISTS idx_appointment_status ON appointment(status);
CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointment(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointment_assigned ON appointment(assigned_to);
CREATE INDEX IF NOT EXISTS idx_appointment_tenant ON appointment(tenant_id);

-- ============================================
-- 4. 销售物料模块
-- ============================================

-- 优惠券表
CREATE TABLE IF NOT EXISTS coupon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20),
    value DECIMAL(10,2),
    discount_percent INTEGER,
    min_amount DECIMAL(10,2),
    valid_from DATE,
    valid_to DATE,
    quantity INTEGER,
    used_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT '未发布',
    image_url VARCHAR(500),
    description TEXT,
    tenant_id VARCHAR(20),
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 优惠券领取记录表
CREATE TABLE IF NOT EXISTS coupon_claim (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id INTEGER NOT NULL,
    phone VARCHAR(20) NOT NULL,
    claim_code VARCHAR(50) UNIQUE,
    claimed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    used_at DATETIME,
    used_by INTEGER,
    status VARCHAR(20) DEFAULT '未使用',
    FOREIGN KEY (coupon_id) REFERENCES coupon(id),
    FOREIGN KEY (used_by) REFERENCES employee(id)
);

-- 销售物料表
CREATE TABLE IF NOT EXISTS sales_material (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20),
    category VARCHAR(50),
    image_url VARCHAR(500),
    file_url VARCHAR(500),
    qr_code_url VARCHAR(500),
    share_title VARCHAR(200),
    share_desc TEXT,
    status VARCHAR(20) DEFAULT '启用',
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    tenant_id VARCHAR(20),
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 优惠券索引
CREATE INDEX IF NOT EXISTS idx_coupon_status ON coupon(status);
CREATE INDEX IF NOT EXISTS idx_coupon_type ON coupon(type);
CREATE INDEX IF NOT EXISTS idx_coupon_tenant ON coupon(tenant_id);
CREATE INDEX IF NOT EXISTS idx_claim_coupon ON coupon_claim(coupon_id);
CREATE INDEX IF NOT EXISTS idx_claim_phone ON coupon_claim(phone);
CREATE INDEX IF NOT EXISTS idx_claim_code ON coupon_claim(claim_code);
CREATE INDEX IF NOT EXISTS idx_material_type ON sales_material(type);
CREATE INDEX IF NOT EXISTS idx_material_status ON sales_material(status);

-- ============================================
-- 5. 品牌内容模块
-- ============================================

-- 文章/动态表
CREATE TABLE IF NOT EXISTS article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    cover_image VARCHAR(500),
    summary TEXT,
    content TEXT,
    tags TEXT,
    type VARCHAR(20) DEFAULT '动态',
    author_id INTEGER,
    view_count INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT '草稿',
    is_top BOOLEAN DEFAULT 0,
    publish_at DATETIME,
    tenant_id VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 文章索引
CREATE INDEX IF NOT EXISTS idx_article_type ON article(type);
CREATE INDEX IF NOT EXISTS idx_article_status ON article(status);
CREATE INDEX IF NOT EXISTS idx_article_top ON article(is_top);
CREATE INDEX IF NOT EXISTS idx_article_tenant ON article(tenant_id);
CREATE INDEX IF NOT EXISTS idx_article_publish ON article(publish_at);

-- ============================================
-- 6. 触发器：自动更新 updated_at
-- ============================================

CREATE TRIGGER IF NOT EXISTS trg_case_study_updated
AFTER UPDATE ON case_study
BEGIN
    UPDATE case_study SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_lead_updated
AFTER UPDATE ON lead
BEGIN
    UPDATE lead SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_appointment_updated
AFTER UPDATE ON appointment
BEGIN
    UPDATE appointment SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_coupon_updated
AFTER UPDATE ON coupon
BEGIN
    UPDATE coupon SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_sales_material_updated
AFTER UPDATE ON sales_material
BEGIN
    UPDATE sales_material SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_article_updated
AFTER UPDATE ON article
BEGIN
    UPDATE article SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- 7. 初始数据
-- ============================================

-- 插入示例案例
INSERT OR IGNORE INTO case_study (id, title, type, style, space_type, budget_range, area, location, description, status, is_featured, tenant_id) VALUES
(1, '龙湖天街·现代轻奢', '实景', '现代', '全屋', '25-35万', 128.5, '龙湖天街', '本案采用现代轻奢风格，以灰白为主色调，搭配金属线条点缀，营造高级感。全屋定制柜体，收纳功能强大。', '已发布', 1, 'default'),
(2, '万科城·北欧简约', '实景', '北欧', '三室两厅', '18-25万', 105.0, '万科城', '北欧风格，原木色与白色搭配，温馨舒适。开放式厨房设计，空间通透。', '已发布', 1, 'default'),
(3, '保利中心·新中式', '设计', '新中式', '四室两厅', '35-50万', 156.0, '保利中心', '新中式风格，融入现代元素，传统与时尚完美结合。', '已发布', 0, 'default');

-- 插入示例优惠券
INSERT OR IGNORE INTO coupon (id, name, type, value, min_amount, valid_from, valid_to, quantity, status, tenant_id) VALUES
(1, '到店礼·精美礼品', '到店礼', 0, 0, '2026-04-01', '2026-12-31', 1000, '进行中', 'default'),
(2, '定金抵扣·立减5000', '定金抵扣', 5000, 50000, '2026-04-01', '2026-06-30', 500, '进行中', 'default'),
(3, '竣工礼·家电礼包', '竣工礼', 3000, 100000, '2026-04-01', '2026-12-31', 200, '进行中', 'default');

-- ============================================
-- 完成
-- ============================================

SELECT '数据库初始化完成' as message;
