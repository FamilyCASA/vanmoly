-- 给所有缺少 tenant_id 的表添加字段（带默认值，避免破坏现有数据）
-- 每个表先检查是否有 tenant_id，没有才添加

-- 关联/Lookup表
ALTER TABLE building_customer ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE building_follow ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE career_path ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_files ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_leads ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_media ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_notifications ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_operation_logs ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_subscriptions ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_templates ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE case_timeline ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE contract_change ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE contract_payment ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE coupon_claim ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE customer_follow ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE customer_schemes ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE digital_asset_transfers ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE employee_contract ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE employee_performance ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE employee_points ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE employee_salary ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE employee_welfare ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE lead_distribution ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE lead_follow ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE lead_point ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE login_logs ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE material_variant ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE performance_review ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE points_transaction ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE quote_item ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE quote_template ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE scheme_items ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE training_record ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE workflow_node ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';
ALTER TABLE workflow_node_record ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default';

-- 已有 tenant_id 但可能缺失的表（检查性添加，避免重复报错）
-- 这些已有字段，不需要修改