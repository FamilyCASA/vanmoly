import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Add to both mat row defaults (2 occurrences of this exact string)
old1 = "env_level: c.env_level || '合格', supply_chain: c.supply_chain || '直供', color_name: c.color_name || ''"
new1 = "env_level: c.env_level || '合格', supply_chain: c.supply_chain || '直供', color_name: c.color_name || '', custom_name: c.custom_name || '', material: c.material || '', custom_measure: c.custom_measure || ''"
c = c.replace(old1, new1)
print(f"✅ 替换了 {c.count(new1)} 处 mat row defaults")

# 2. Add to row.field = mat.field assignments
old2 = "row.color_name = mat.color_name || ''"
new2 = "row.color_name = mat.color_name || ''\n            row.material = mat.material || ''\n            row.custom_name = mat.custom_name || ''\n            row.custom_measure = mat.custom_measure || ''"
c = c.replace(old2, new2)
print(f"✅ 替换了 {c.count('row.custom_name = mat.custom_name')} 处 row assignments")

# 3. Add to save payload
old3 = "env_level:r.env_level,supply_chain:r.supply_chain,color_name:r.color_name"
new3 = "env_level:r.env_level,supply_chain:r.supply_chain,color_name:r.color_name,custom_name:r.custom_name,material:r.material,custom_measure:r.custom_measure"
c = c.replace(old3, new3)
print(f"✅ 替换了 {c.count(new3)} 处 save payload")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ PhaseSpaceRenderingsEditor.vue 全部更新完成")
