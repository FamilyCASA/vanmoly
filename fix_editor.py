import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Add custom_name, material, custom_measure to addMatRow defaults
old_add = "env_level:'合格', supply_chain:'直供', color_name:''"
if old_add in c:
    new_add = "env_level:'合格', supply_chain:'直供', color_name:'', custom_name:'', material:'', custom_measure:''"
    c = c.replace(old_add, new_add, 1)
    print("✅ addMatRow 默认值添加 custom_name/material/custom_measure")

# 2. Add material field to onMatSelect auto-fill
# Find where sku.brand etc. are set
old_select = "color_name: sku.color_name || ''"
if old_select in c:
    new_select = "color_name: sku.color_name || '', material: sku.material || '', custom_name: '', custom_measure: ''"
    c = c.replace(old_select, new_select, 1)
    print("✅ onMatSelect 添加 material 字段自动填充")

# 3. Add custom_name, material, custom_measure to openMaterialConfig load
# Find where fields are loaded from API response
old_load = "color_name: m.color_name"
if old_load in c:
    new_load = "color_name: m.color_name, material: m.material, custom_name: m.custom_name, custom_measure: m.custom_measure"
    c = c.replace(old_load, new_load, 1)
    print("✅ openMaterialConfig 加载添加 custom_name/material/custom_measure")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
