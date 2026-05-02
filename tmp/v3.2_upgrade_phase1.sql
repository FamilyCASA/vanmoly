-- ============================================
-- VANMOLY-SYS V3.2 数据库升级脚本
-- Phase 1: 空间配置模板
-- 执行时间: 2026-04-29
-- ============================================

-- 备份提示：执行前请先备份数据库！
-- sqlite3 instance/vanmoly_v3.db ".backup instance/vanmoly_v3_backup_20260429.db"

-- ============================================
-- 1. 创建空间配置模板表（核心新增）
-- ============================================
CREATE TABLE IF NOT EXISTS case_space_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id VARCHAR(32) DEFAULT '0',
    
    -- 关联
    case_id INTEGER NOT NULL,
    quote_id INTEGER,
    
    -- 空间信息
    space_type VARCHAR(50) NOT NULL,
    space_name VARCHAR(100),
    space_area DECIMAL(10,2),
    
    -- 版本档位
    version_level VARCHAR(20) NOT NULL,
    version_code VARCHAR(20),
    
    -- 配置信息
    config_name VARCHAR(200),
    config_desc TEXT,
    
    -- 物料清单（JSON格式）
    materials TEXT,
    material_count INTEGER DEFAULT 0,
    
    -- 价格汇总
    material_cost DECIMAL(12,2) DEFAULT 0,
    labor_cost DECIMAL(12,2) DEFAULT 0,
    design_cost DECIMAL(12,2) DEFAULT 0,
    manage_cost DECIMAL(12,2) DEFAULT 0,
    total_price DECIMAL(12,2) DEFAULT 0,
    
    -- 模板属性
    is_template INTEGER DEFAULT 1,
    template_tags TEXT,
    
    -- 互斥配置
    exclusive_rules TEXT,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',
    
    -- 创建人
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES case_study(id),
    FOREIGN KEY (quote_id) REFERENCES quote(id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_case_space_config_case ON case_space_config(case_id);
CREATE INDEX IF NOT EXISTS idx_case_space_config_space ON case_space_config(space_type);
CREATE INDEX IF NOT EXISTS idx_case_space_config_version ON case_space_config(version_level);
CREATE INDEX IF NOT EXISTS idx_case_space_config_template ON case_space_config(is_template, status);

-- ============================================
-- 2. 创建空间配置物料明细表
-- ============================================
CREATE TABLE IF NOT EXISTS case_space_config_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    
    -- 物料信息
    sku_id INTEGER NOT NULL,
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    brand VARCHAR(100),
    specification VARCHAR(200),
    category VARCHAR(50),
    
    -- 用量与价格
    quantity DECIMAL(10,2) DEFAULT 1,
    unit VARCHAR(20),
    unit_price DECIMAL(12,2),
    total_price DECIMAL(12,2),
    
    -- 互斥标记
    is_exclusive INTEGER DEFAULT 0,
    exclusive_group VARCHAR(50),
    
    -- 选装标记
    is_optional INTEGER DEFAULT 0,
    is_default INTEGER DEFAULT 1,
    
    sort_order INTEGER DEFAULT 0,
    
    FOREIGN KEY (config_id) REFERENCES case_space_config(id),
    FOREIGN KEY (sku_id) REFERENCES material_sku(id)
);

CREATE INDEX IF NOT EXISTS idx_config_item_config ON case_space_config_item(config_id);
CREATE INDEX IF NOT EXISTS idx_config_item_sku ON case_space_config_item(sku_id);

-- ============================================
-- 3. 创建报价单-空间配置实例表
-- ============================================
CREATE TABLE IF NOT EXISTS quote_space_instance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id VARCHAR(32) DEFAULT '0',
    quote_id INTEGER NOT NULL,
    template_config_id INTEGER,
    
    -- 空间信息（复制自模板）
    space_type VARCHAR(50),
    space_name VARCHAR(100),
    space_area DECIMAL(10,2),
    version_level VARCHAR(20),
    
    -- 调整后价格
    original_price DECIMAL(12,2),
    adjusted_price DECIMAL(12,2),
    adjustment_reason TEXT,
    
    -- 调整明细
    adjustments TEXT,
    
    -- 状态
    is_selected INTEGER DEFAULT 1,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (quote_id) REFERENCES quote(id),
    FOREIGN KEY (template_config_id) REFERENCES case_space_config(id)
);

CREATE INDEX IF NOT EXISTS idx_quote_space_quote ON quote_space_instance(quote_id);

-- ============================================
-- 4. 创建物料互斥规则表
-- ============================================
CREATE TABLE IF NOT EXISTS material_exclusive_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id VARCHAR(32) DEFAULT '0',
    rule_name VARCHAR(100),
    rule_group VARCHAR(50),
    sku_id INTEGER,
    exclusive_sku_ids TEXT,
    description TEXT,
    is_enabled INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. 改造现有表（增加字段）
-- ============================================

-- 案例表增加配置标记
-- ALTER TABLE case_study ADD COLUMN has_space_config INTEGER DEFAULT 0;
-- ALTER TABLE case_study ADD COLUMN config_version_count INTEGER DEFAULT 0;

-- 报价项表增加空间关联（如果不存在）
-- ALTER TABLE quote_item ADD COLUMN space_config_id INTEGER;
-- ALTER TABLE quote_item ADD COLUMN space_type VARCHAR(50);
-- ALTER TABLE quote_item ADD COLUMN is_from_template INTEGER DEFAULT 0;

-- 物料表增加互斥标记（如果不存在）
-- ALTER TABLE material_sku ADD COLUMN exclusive_group VARCHAR(50);
-- ALTER TABLE material_sku ADD COLUMN is_exclusive_item INTEGER DEFAULT 0;

-- ============================================
-- 6. 插入测试数据
-- ============================================

-- 空间类型字典
INSERT INTO case_space_config (case_id, space_type, space_name, version_level, total_price, is_template, status)
SELECT 
    id as case_id,
    '客厅' as space_type,
    '客厅' as space_name,
    '舒适' as version_level,
    COALESCE(total_price * 0.15, 50000) as total_price,
    1 as is_template,
    'active' as status
FROM case_study 
WHERE id NOT IN (SELECT case_id FROM case_space_config)
LIMIT 3;

-- ============================================
-- 7. 验证创建结果
-- ============================================
SELECT 
    'case_space_config' as table_name,
    COUNT(*) as count
FROM case_space_config
UNION ALL
SELECT 
    'case_space_config_item' as table_name,
    COUNT(*) as count
FROM case_space_config_item
UNION ALL
SELECT 
    'quote_space_instance' as table_name,
    COUNT(*) as count
FROM quote_space_instance
UNION ALL
SELECT 
    'material_exclusive_rule' as table_name,
    COUNT(*) as count
FROM material_exclusive_rule;

-- 升级完成
SELECT 'Phase 1 数据库升级完成！' as message;
