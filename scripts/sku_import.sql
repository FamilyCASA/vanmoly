-- SKU物料数据导入脚本
-- 生成时间: 2026-04-26 11:02:54
-- 注意: 先确保material_category表中有对应分类

BEGIN TRANSACTION;

-- 插入分类
INSERT OR IGNORE INTO material_category (name, code, level) VALUES ('固装家具', '固装家具', 1);

-- 插入SKU数据
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00001',
    '净醛系列-实木颗粒板-门板-梨花白-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00002',
    '净醛系列-实木颗粒板-柜体-梨花白',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-梨花白',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00003',
    '净醛系列-实木颗粒板-门板-羊绒可可-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00004',
    '净醛系列-实木颗粒板-柜体-羊绒可可',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-羊绒可可',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00005',
    '净醛系列-实木颗粒板-门板-星空灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00006',
    '净醛系列-实木颗粒板-柜体-星空灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-星空灰',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00007',
    '净醛系列-实木颗粒板-门板-迪诺胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00008',
    '净醛系列-实木颗粒板-柜体-迪诺胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-迪诺胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00009',
    '净醛系列-实木颗粒板-门板-唯美胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00010',
    '净醛系列-实木颗粒板-柜体-唯美胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-唯美胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00011',
    '净醛系列-实木颗粒板-门板-安娜胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00012',
    '净醛系列-实木颗粒板-柜体-安娜胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-安娜胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00013',
    '净醛系列-实木颗粒板-门板-清雅胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00014',
    '净醛系列-实木颗粒板-柜体-清雅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-清雅胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00015',
    '净醛系列-实木颗粒板-门板-香贵胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00016',
    '净醛系列-实木颗粒板-柜体-香贵胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-香贵胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00017',
    '净醛系列-实木颗粒板-门板-直纹浅胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00018',
    '净醛系列-实木颗粒板-柜体-直纹浅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-直纹浅胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00019',
    '净醛系列-实木颗粒板-门板-象直纹深胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00020',
    '净醛系列-实木颗粒板-柜体-直纹深胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-直纹深胡桃',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00021',
    '净醛系列-实木颗粒板-门板-臻品浅橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00022',
    '净醛系列-实木颗粒板-柜体-臻品浅橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-臻品浅橡',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00023',
    '净醛系列-实木颗粒板-门板-安邸红橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00024',
    '净醛系列-实木颗粒板-柜体-安邸红橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-安邸红橡',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00025',
    '净醛系列-实木颗粒板-门板-托斯卡棕橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00026',
    '净醛系列-实木颗粒板-柜体-托斯卡棕橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-托斯卡棕橡',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00027',
    '净醛系列-实木颗粒板-门板-半山灰橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00028',
    '净醛系列-实木颗粒板-柜体-半山灰橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-半山灰橡',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00029',
    '净醛系列-实木颗粒板-门板-挪威黑橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00030',
    '净醛系列-实木颗粒板-柜体-挪威黑橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-挪威黑橡',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00031',
    '净醛系列-实木颗粒板-门板-象牙白-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00032',
    '净醛系列-实木颗粒板-柜体-象牙白',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-象牙白',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00033',
    '净醛系列-实木颗粒板-门板-雪山灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00034',
    '净醛系列-实木颗粒板-柜体-雪山灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-雪山灰',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00035',
    '净醛系列-实木颗粒板-门板-月光灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    156.0,
    260.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00036',
    '净醛系列-实木颗粒板-柜体-月光灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体-月光灰',
    '净醛颗粒板',
    263.4,
    439.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00037',
    '净醛系列-实木颗粒板-展开板-9mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:9; 厚度:9mm',
    '净醛颗粒板',
    60.0,
    100.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00038',
    '净醛系列-实木颗粒板-展开板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    101.4,
    169.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00039',
    '净醛系列-实木颗粒板-展开板-28mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:28; 厚度:28mm',
    '净醛颗粒板',
    192.0,
    320.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00040',
    '净醛系列-实木颗粒板-展开板-37mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:37; 厚度:37mm',
    '净醛颗粒板',
    330.0,
    550.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00041',
    '净醛系列-实木颗粒板-墙板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '净醛颗粒板',
    198.0,
    330.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00042',
    '净醛系列-实木颗粒板-柜体/柜门',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-实木颗粒板-柜体/柜门',
    '净醛颗粒板',
    419.4,
    699.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00043',
    '净醛系列-欧松板-展开板-9mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:9; 厚度:9mm',
    '欧松板',
    84.0,
    140.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00044',
    '净醛系列-欧松板-展开板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    119.4,
    199.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00045',
    '净醛系列-欧松板-展开板-28mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:28; 厚度:28mm',
    '欧松板',
    216.0,
    360.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00046',
    '净醛系列-欧松板-展开板-37mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:37; 厚度:37mm',
    '欧松板',
    360.0,
    600.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00047',
    '净醛系列-欧松板-墙板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    216.0,
    360.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00048',
    '净醛系列-欧松板-柜体/柜门',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体/柜门',
    '欧松板',
    539.4,
    899.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00049',
    '净醛系列-欧松板-门板-梨花白-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00050',
    '净醛系列-欧松板-柜体-梨花白',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-梨花白',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00051',
    '净醛系列-欧松板-门板-羊绒可可-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00052',
    '净醛系列-欧松板-柜体-羊绒可可',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-羊绒可可',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00053',
    '净醛系列-欧松板-门板-星空灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00054',
    '净醛系列-欧松板-柜体-星空灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-星空灰',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00055',
    '净醛系列-欧松板-门板-迪诺胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00056',
    '净醛系列-欧松板-柜体-迪诺胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-迪诺胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00057',
    '净醛系列-欧松板-门板-唯美胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00058',
    '净醛系列-欧松板-柜体-唯美胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-唯美胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00059',
    '净醛系列-欧松板-门板-安娜胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00060',
    '净醛系列-欧松板-柜体-安娜胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-安娜胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00061',
    '净醛系列-欧松板-门板-清雅胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00062',
    '净醛系列-欧松板-柜体-清雅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-清雅胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00063',
    '净醛系列-欧松板-门板-香贵胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00064',
    '净醛系列-欧松板-柜体-香贵胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-香贵胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00065',
    '净醛系列-欧松板-门板-直纹浅胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00066',
    '净醛系列-欧松板-柜体-直纹浅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-直纹浅胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00067',
    '净醛系列-欧松板-门板-象直纹深胡桃-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00068',
    '净醛系列欧松板-柜体-直纹深胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列欧松板-柜体-直纹深胡桃',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00069',
    '净醛系列-欧松板-门板-臻品浅橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00070',
    '净醛系列-欧松板-柜体-臻品浅橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-臻品浅橡',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00071',
    '净醛系列-欧松板-门板-安邸红橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00072',
    '净醛系列-欧松板-柜体-安邸红橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-安邸红橡',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00073',
    '净醛系列-欧松板-门板-托斯卡棕橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00074',
    '净醛系列-欧松板-柜体-托斯卡棕橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-托斯卡棕橡',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00075',
    '净醛系列-欧松板-门板-半山灰橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00076',
    '净醛系列-欧松板-柜体-半山灰橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-半山灰橡',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00077',
    '净醛系列-欧松板-门板-挪威黑橡-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00078',
    '净醛系列-欧松板-柜体-挪威黑橡',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-挪威黑橡',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00079',
    '净醛系列-欧松板-门板-象牙白-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00080',
    '净醛系列-欧松板-柜体-象牙白',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-象牙白',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00081',
    '净醛系列-欧松板-门板-雪山灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00082',
    '净醛系列-欧松板-柜体-雪山灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-雪山灰',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00083',
    '净醛系列-欧松板-门板-月光灰-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '欧松板',
    180.0,
    300.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00084',
    '净醛系列-欧松板-柜体-月光灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-欧松板-柜体-月光灰',
    '欧松板',
    359.4,
    599.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00085',
    '净醛系列-多层板-展开板-9mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:9; 厚度:9mm',
    '多层板',
    90.0,
    150.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00086',
    '净醛系列-多层板-展开板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '多层板',
    143.4,
    239.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00087',
    '净醛系列-多层板-展开板-28mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:28; 厚度:28mm',
    '多层板',
    228.0,
    380.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00088',
    '净醛系列-多层板-展开板-37mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:37; 厚度:37mm',
    '多层板',
    384.0,
    640.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00089',
    '净醛系列-多层板-墙板-18mm',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '尺寸:18; 厚度:18mm',
    '多层板',
    228.0,
    380.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00090',
    '净醛系列-多层板-柜体/柜门',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体/柜门',
    '多层板',
    539.4,
    899.0,
    '㎡',
    'quantity',
    '柜体：净醛多层板+柜门：净醛颗粒板',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00091',
    '净醛系列-多层板-柜体-梨花白',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-梨花白',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00092',
    '净醛系列-多层板-柜体-羊绒可可',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-羊绒可可',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00093',
    '净醛系列-多层板-柜体-星空灰',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-星空灰',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00094',
    '净醛系列-多层板-柜体-迪诺胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-迪诺胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00095',
    '净醛系列-多层板-柜体-唯美胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-唯美胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00096',
    '净醛系列-多层板-柜体-安娜胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-安娜胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00097',
    '净醛系列-多层板-柜体-清雅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-清雅胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00098',
    '净醛系列-多层板-柜体-香贵胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-香贵胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00099',
    '净醛系列-多层板-柜体-直纹浅胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-直纹浅胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);
INSERT INTO material_sku (
    sku_code, name, category_id, brand, model, specification, material,
    cost_price, sale_price, unit, calc_type, description, status, created_at
) VALUES (
    'D&B-00100',
    '净醛系列-多层板-柜体-直纹深胡桃',
    (SELECT id FROM material_category WHERE name = '固装家具'),
    '',
    '',
    '净醛系列-多层板-柜体-直纹深胡桃',
    '多层板',
    383.4,
    639.0,
    '㎡',
    'quantity',
    '门板单个展开面积不足0.25㎡按0.25㎡计算；见光板及封板按门板价格计价，封板宽度不足100mm按100mm计价',
    'active',
    datetime('now')
);

COMMIT;
