import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Fix addMatRow - add custom_name and custom_measure
old_add = "matRows.value.push({ name:'',cat1Id:'',cat2Id:'',material_name:'',material_id:null,spec:'',width:null,depth:null,height:null,quantity:1,price:null,amount:0,unit:'',calcVal:null,sku_code:'',brand:'',material:'',main_image:'',env_level:'合格',supply_chain:'直供',color_name:'' })"
new_add = "matRows.value.push({ name:'',cat1Id:'',cat2Id:'',material_name:'',material_id:null,spec:'',width:null,depth:null,height:null,quantity:1,price:null,amount:0,unit:'',calcVal:null,sku_code:'',brand:'',material:'',main_image:'',env_level:'合格',supply_chain:'直供',color_name:'',custom_name:'',custom_measure:'' })"
c = c.replace(old_add, new_add, 1)
print("✅ addMatRow 添加 custom_name/custom_measure")

# 2. Fix onMatSelect - remove duplicate row.material assignment
old_select = """    row.color_name = mat.color_name || ''
            row.material = mat.material || ''
            row.custom_name = mat.custom_name || ''
            row.custom_measure = mat.custom_measure || ''"""
new_select = """    row.color_name = mat.color_name || ''
    row.custom_name = ''
    row.custom_measure = ''"""
c = c.replace(old_select, new_select, 1)
print("✅ onMatSelect 清理重复 material，custom_name/custom_measure 默认空")

# 3. Fix saveMaterialConfig - remove duplicate material:r.material
old_save = "env_level:r.env_level,supply_chain:r.supply_chain,color_name:r.color_name,custom_name:r.custom_name,material:r.material,custom_measure:r.custom_measure"
new_save = "env_level:r.env_level,supply_chain:r.supply_chain,color_name:r.color_name,custom_name:r.custom_name,custom_measure:r.custom_measure"
c = c.replace(old_save, new_save, 1)
print("✅ saveMaterialConfig 移除重复 material（已在前面定义）")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
